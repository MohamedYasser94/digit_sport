"""
Celery tasks for TransferMarket data fetching.
These tasks run in the background to prevent server timeouts during bulk operations.

Usage:
    from apps.sport.tasks.transfermarket_tasks import fetch_all_players_transfermarket_data

    # Queue the task (returns immediately)
    result = fetch_all_players_transfermarket_data.delay(sport_type='football')

    # Or call with arguments
    result = fetch_single_player_transfermarket_data.delay(player_id=123)

Configuration:
    Add to your Django settings.py:

    CELERY_BROKER_URL = 'redis://localhost:6379/0'  # or your broker
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    And ensure Celery is configured in your project.

    To install Celery:
    pip install celery[redis]
"""
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

# Try to import Celery, but make it optional
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

    # Mock self object for bound tasks
    class MockTask:
        def update_state(self, state=None, meta=None):
            logger.debug(f"Task state: {state}, meta: {meta}")

        def retry(self, exc=None):
            raise exc if exc else Exception("Task retry requested")

    # Create a dummy decorator when Celery is not available
    def shared_task(*args, **kwargs):
        def decorator(func):
            def wrapper(*f_args, **f_kwargs):
                logger.warning(f"Celery is not installed. Running {func.__name__} synchronously.")
                # Add mock self if bind=True was specified
                if kwargs.get('bind', False):
                    return func(MockTask(), *f_args, **f_kwargs)
                return func(*f_args, **f_kwargs)
            wrapper.delay = lambda *a, **kw: wrapper(*a, **kw)
            wrapper.apply_async = lambda *a, **kw: wrapper(*kw.get('args', ()), **kw.get('kwargs', {}))
            return wrapper
        if len(args) == 1 and callable(args[0]):
            return decorator(args[0])
        return decorator


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_all_players_transfermarket_data(self, sport_type='football', batch_size=50):
    """
    Background task to fetch TransferMarket data for all players.
    Processes players in batches to avoid memory issues.

    Args:
        sport_type: Type of sport (default: 'football')
        batch_size: Number of players to process per batch (default: 50)

    Returns:
        Dictionary with statistics about the operation
    """
    try:
        from apps.sport.models.models import Players, Sport
        from apps.sport.views.update_players_transfermarket import (
            get_transfermarket_data_for_player,
            update_player_with_transfermarket_data
        )

        # Get sport
        sport = Sport.objects.filter(name__iexact=sport_type).first()
        if not sport:
            return {'error': f'Sport "{sport_type}" not found'}

        # Get all players
        players = Players.objects.filter(sport=sport).select_related('team')
        total = players.count()

        if total == 0:
            return {'error': f'No players found for {sport_type}'}

        # Statistics
        stats = {
            'total': total,
            'processed': 0,
            'updated': 0,
            'skipped': 0,
            'failed': 0,
            'errors': []
        }

        # Process in batches
        for i in range(0, total, batch_size):
            batch = players[i:i + batch_size]

            for player in batch:
                try:
                    # Update task progress
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': stats['processed'],
                            'total': total,
                            'player_name': player.name
                        }
                    )

                    # Fetch TransferMarket data
                    tm_data = get_transfermarket_data_for_player(player)

                    if tm_data:
                        update_player_with_transfermarket_data(player, tm_data)
                        stats['updated'] += 1
                    else:
                        stats['skipped'] += 1

                    stats['processed'] += 1

                except Exception as e:
                    stats['failed'] += 1
                    stats['errors'].append(f"Error for {player.name}: {str(e)}")
                    logger.error(f"Error processing player {player.id}: {e}")
                    continue

            # Log batch progress
            logger.info(f"Batch progress: {stats['processed']}/{total}")

        stats['completed_at'] = timezone.now().isoformat()
        return stats

    except Exception as e:
        logger.error(f"Task failed: {e}")
        # Retry on failure
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def fetch_single_player_transfermarket_data(self, player_id, include_transfers=False, include_market_value_history=False):
    """
    Background task to fetch TransferMarket data for a single player.
    Useful for fetching data on-demand without blocking the request.

    Args:
        player_id: ID of the player to fetch data for
        include_transfers: Whether to also fetch transfer history
        include_market_value_history: Whether to fetch market value history

    Returns:
        Dictionary with results
    """
    try:
        from apps.sport.models.models import Players
        from apps.sport.views.update_players_transfermarket import (
            get_transfermarket_data_for_player,
            update_player_with_transfermarket_data,
            fetch_player_transfers,
            save_player_transfers,
            fetch_player_market_value_history
        )

        player = Players.objects.get(id=player_id)

        results = {
            'player_id': player_id,
            'player_name': player.name,
            'profile': {'success': False, 'message': ''},
            'transfers': {'success': False, 'count': 0, 'message': ''},
            'market_value_history': {'success': False, 'count': 0, 'message': ''}
        }

        # Fetch profile
        tm_data = get_transfermarket_data_for_player(player)

        if tm_data:
            update_player_with_transfermarket_data(player, tm_data)
            results['profile']['success'] = True
            results['profile']['message'] = 'Profile updated successfully'

            # Refresh player from DB
            player.refresh_from_db()

            # Fetch transfers if requested
            if include_transfers and player.transfermarkt_id:
                transfers = fetch_player_transfers(player.transfermarkt_id)
                if transfers:
                    added, updated, failed = save_player_transfers(player, transfers)
                    results['transfers']['success'] = True
                    results['transfers']['count'] = added + updated
                    results['transfers']['message'] = f'Added: {added}, Updated: {updated}, Failed: {failed}'
                else:
                    results['transfers']['message'] = 'No transfers found'

            # Fetch market value history if requested
            if include_market_value_history and player.transfermarkt_id:
                mv_history = fetch_player_market_value_history(player.transfermarkt_id)
                if mv_history:
                    results['market_value_history']['success'] = True
                    results['market_value_history']['count'] = len(mv_history)
                    results['market_value_history']['message'] = f'Found {len(mv_history)} entries'

                    # Store in player's keyword field
                    import json
                    try:
                        existing_keyword = json.loads(player.keyword) if player.keyword else {}
                    except:
                        existing_keyword = {}

                    existing_keyword['market_value_history'] = mv_history
                    player.keyword = json.dumps(existing_keyword, default=str)
                    player.save(update_fields=['keyword'])
                else:
                    results['market_value_history']['message'] = 'No market value history found'
        else:
            results['profile']['message'] = 'No TransferMarket data found'

        results['completed_at'] = timezone.now().isoformat()
        return results

    except Players.DoesNotExist:
        return {'error': f'Player with ID {player_id} not found'}
    except Exception as e:
        logger.error(f"Task failed for player {player_id}: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_sportmonks_players_data(self, sport_type='football', batch_size=50):
    """
    Background task to fetch Sportmonks data for all players.

    Args:
        sport_type: Type of sport (default: 'football')
        batch_size: Number of API pages to process per batch

    Returns:
        Dictionary with statistics about the operation
    """
    try:
        from django.conf import settings
        from core.utils.api_client import get_api_client
        from apps.sport.models.models import Players, Sport, Teams

        api_key = settings.SPORT_MONKS_TOKEN
        base_url = settings.SPORT_MONKS_URL

        # Get sport
        try:
            sport = Sport.objects.get(name__iexact=sport_type)
        except Sport.DoesNotExist:
            return {'error': f'Sport "{sport_type}" not found'}

        api_client = get_api_client()

        stats = {
            'total_pages': 0,
            'processed': 0,
            'added': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }

        next_page_url = f"{base_url}{sport_type}/players?api_token={api_key}&include=teams;country;position;detailedPosition"
        max_pages = 100

        while next_page_url and stats['total_pages'] < max_pages:
            stats['total_pages'] += 1

            try:
                # Update progress
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'page': stats['total_pages'],
                        'processed': stats['processed']
                    }
                )

                data = api_client.get(next_page_url, timeout=30)

                if data is None:
                    stats['errors'].append(f'Failed to fetch page {stats["total_pages"]}')
                    break

                players_data = data.get('data', [])

                for player_data in players_data:
                    try:
                        from datetime import datetime

                        # Parse birthdate
                        birthdate_obj = None
                        if player_data.get('date_of_birth'):
                            try:
                                birthdate_obj = datetime.strptime(player_data['date_of_birth'], '%Y-%m-%d').date()
                            except (ValueError, TypeError):
                                birthdate_obj = None

                        # Get current team
                        team_obj = None
                        teams_list = player_data.get('teams') or []
                        current_team = None
                        for t in teams_list:
                            if t.get('end') in (None, '', False):
                                current_team = t
                                break
                        if not current_team and teams_list:
                            current_team = teams_list[0]
                        if current_team and current_team.get('team_id'):
                            team_obj = Teams.objects.filter(api_id=current_team.get('team_id')).first()

                        defaults = {
                            'sport': sport,
                            'api_country': player_data.get('country_id'),
                            'api_nationality': player_data.get('nationality_id'),
                            'api_city': player_data.get('city_id'),
                            'api_position': player_data.get('position_id'),
                            'api_detailed_position': player_data.get('detailed_position_id'),
                            'type': player_data.get('type_id'),
                            'common_name': player_data.get('common_name'),
                            'first_name': player_data.get('firstname'),
                            'last_name': player_data.get('lastname'),
                            'name': player_data.get('display_name'),
                            'image_path': player_data.get('image_path'),
                            'height': player_data.get('height'),
                            'weight': player_data.get('weight'),
                            'birthdate': birthdate_obj,
                            'gender': player_data.get('gender'),
                            'team': team_obj,
                        }

                        obj, created = Players.objects.update_or_create(
                            api_id=player_data['id'],
                            defaults=defaults
                        )
                        stats['processed'] += 1
                        if created:
                            stats['added'] += 1
                        else:
                            stats['updated'] += 1

                    except Exception as e:
                        stats['failed'] += 1
                        stats['errors'].append(f"Error processing player {player_data.get('id')}: {str(e)}")
                        continue

                # Handle pagination
                pagination = data.get('pagination', {})
                if pagination.get('has_more') and pagination.get('next_page'):
                    next_page_url = f"{pagination.get('next_page')}&api_token={api_key}"
                else:
                    next_page_url = None

            except Exception as e:
                stats['failed'] += 1
                stats['errors'].append(f'Error on page {stats["total_pages"]}: {str(e)}')
                break

        stats['completed_at'] = timezone.now().isoformat()
        return stats

    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise self.retry(exc=e)

