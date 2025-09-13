from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
import requests
import pytz
from ..models import Sport, MultiSourcePlayers, DataSource, PlayerDataSourceInfo, PlayerDataConflict


def initialize_data_sources():
    """Initialize default data sources if they don't exist"""
    sources = [
        {
            'name': 'Sportmonks',
            'slug': 'sportmonks',
            'priority': 90,
            'api_base_url': getattr(settings, 'SPORT_MONKS_URL', ''),
            'description': 'Sportmonks API - Primary source for official sports data'
        },
        {
            'name': 'Transfer Market',
            'slug': 'transfermarkt',
            'priority': 80,
            'api_base_url': 'https://www.transfermarkt.com',
            'description': 'Transfer Market scraping - Best for market values and transfers'
        },
        {
            'name': 'Manual Entry',
            'slug': 'manual',
            'priority': 70,
            'description': 'Manually entered data by administrators'
        }
    ]
    
    created_sources = []
    for source_data in sources:
        source, created = DataSource.objects.get_or_create(
            slug=source_data['slug'],
            defaults=source_data
        )
        if created:
            created_sources.append(source.name)
    
    return created_sources


@csrf_exempt
def AdminMultiSourcePlayersGetData(request):
    """
    Enhanced function to fetch players from Sportmonks API using multi-source model
    Compatible with existing HTML admin interface
    """
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        # Initialize data sources if they don't exist
        initialize_data_sources()
        
        sport = request.POST.get('sport', 'football')
        processed, added, updated, conflicts = 0, 0, 0, 0

        try:
            sport_obj = Sport.objects.get(name=sport)
            sportmonks_source = DataSource.objects.get(slug='sportmonks')
        except (Sport.DoesNotExist, DataSource.DoesNotExist) as e:
            return JsonResponse({'type': 'Error', 'message': f"Required object not found: {str(e)}"})

        try:
            api_key = settings.SPORT_MONKS_TOKEN
            base_url = settings.SPORT_MONKS_URL
        except AttributeError:
            return JsonResponse({'type': 'Error', 'message': 'Sportmonks API configuration missing in settings'})

        if not api_key or not base_url:
            return JsonResponse({'type': 'Error', 'message': 'Sportmonks API configuration missing'})

        next_page_url = base_url.rstrip('/') + f'/{sport}/players?api_token={api_key}'

        while next_page_url:
            try:
                response = requests.get(next_page_url)
                if response.status_code == 200:
                    data = response.json()
                    data_to_db = data.get('data', [])

                    for player_data in data_to_db:
                        result = process_sportmonks_player_data(player_data, sport_obj, sportmonks_source, request.user)
                        
                        if result['action'] == 'created':
                            added += 1
                        elif result['action'] == 'updated':
                            updated += 1
                        elif result['action'] == 'conflict':
                            conflicts += 1
                        
                        processed += 1

                    pagination = data.get('pagination', {})
                    if pagination.get('has_more') and pagination.get('next_page'):
                        next_page_url = f"{pagination.get('next_page')}&api_token={api_key}"
                    else:
                        next_page_url = None
                else:
                    return JsonResponse({'type': 'Error', 'message': f'API request failed: {response.status_code}'})
            except Exception as e:
                return JsonResponse({'type': 'Error', 'message': f'An error occurred: {str(e)}'})

        success_message = f'Multi-source data fetched successfully. Processed: {processed}, Added: {added}, Updated: {updated}'
        if conflicts > 0:
            success_message += f', Conflicts detected: {conflicts} (check admin panel to resolve)'
        
        return JsonResponse({'type': 'Success', 'message': success_message})

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})


def process_sportmonks_player_data(player_data, sport_obj, source, user):
    """
    Process individual player data from Sportmonks API
    """
    try:
        # Parse birthdate
        birthdate_obj = None
        if player_data.get('date_of_birth'):
            try:
                birthdate_obj = datetime.strptime(player_data['date_of_birth'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass

        # Try to find existing player by Sportmonks ID first
        player = MultiSourcePlayers.objects.filter(
            sportmonks_api_id=player_data['id']
        ).first()

        if not player:
            # Try to find by name and sport (fuzzy matching)
            display_name = player_data.get('display_name', '').strip()
            if display_name:
                player = MultiSourcePlayers.objects.filter(
                    name__iexact=display_name,
                    sport=sport_obj
                ).first()

        # Prepare the data dictionary for updating
        update_data = {
            'id': player_data['id'],
            'common_name': player_data.get('common_name'),
            'firstname': player_data.get('firstname'),
            'lastname': player_data.get('lastname'),
            'display_name': player_data.get('display_name'),
            'height': player_data.get('height'),
            'weight': player_data.get('weight'),
            'date_of_birth': player_data.get('date_of_birth'),
            'gender': player_data.get('gender'),
            'country_id': player_data.get('country_id'),
            'nationality_id': player_data.get('nationality_id'),
            'city_id': player_data.get('city_id'),
            'position_id': player_data.get('position_id'),
            'detailed_position_id': player_data.get('detailed_position_id'),
            'type_id': player_data.get('type_id'),
            'image_path': player_data.get('image_path'),
        }

        if player:
            # Update existing player
            player.update_from_source(source, update_data, user)
            action = 'updated'
        else:
            # Create new player
            player = MultiSourcePlayers(
                sportmonks_api_id=player_data['id'],
                sport=sport_obj,
                name=player_data.get('display_name'),
                primary_data_source=source
            )
            player.save()
            player.update_from_source(source, update_data, user)
            action = 'created'

        return {'action': action, 'player': player}

    except Exception as e:
        return {'action': 'error', 'error': str(e)}


@csrf_exempt
@login_required
def AdminTransfermarktPlayersGetData(request):
    """
    Function to process Transfer Market scraped data for players
    """
    if request.method == "POST":
        # Initialize data sources if they don't exist
        initialize_data_sources()
        
        try:
            transfermarkt_source = DataSource.objects.get(slug='transfermarkt')
        except DataSource.DoesNotExist:
            return JsonResponse({'type': 'Error', 'message': 'Transfer Market data source not found'})

        method = request.POST.get('method', 'json')
        processed, added, updated, conflicts = 0, 0, 0, 0

        if method == 'url':
            # Scrape data from Transfer Market URL
            url = request.POST.get('url', '')
            options_str = request.POST.get('options', '{}')
            
            if not url:
                return JsonResponse({'type': 'Error', 'message': 'Transfer Market URL is required'})
            
            try:
                import json
                from ..utils.transfermarkt_scraper import scrape_transfermarkt_player
                
                options = json.loads(options_str)
                
                # Check if it's a single player URL or team URL
                if '/spieler/' in url:
                    # Single player
                    scraped_data = scrape_transfermarkt_player(url, options)
                    if scraped_data:
                        result = process_transfermarkt_player_data(scraped_data, transfermarkt_source, request.user)
                        processed = 1
                        if result['action'] == 'created':
                            added = 1
                        elif result['action'] == 'updated':
                            updated = 1
                        elif result['action'] == 'conflict':
                            conflicts = 1
                    else:
                        return JsonResponse({'type': 'Error', 'message': 'Failed to scrape player data from URL'})
                
                elif '/verein/' in url or '/startseite/verein/' in url:
                    # Team URL - scrape multiple players
                    from ..utils.transfermarkt_scraper import scrape_transfermarkt_team
                    
                    players_data = scrape_transfermarkt_team(url, limit=50)  # Limit to 50 players
                    
                    for player_data in players_data:
                        result = process_transfermarkt_player_data(player_data, transfermarkt_source, request.user)
                        
                        if result['action'] == 'created':
                            added += 1
                        elif result['action'] == 'updated':
                            updated += 1
                        elif result['action'] == 'conflict':
                            conflicts += 1
                        
                        processed += 1
                
                else:
                    return JsonResponse({'type': 'Error', 'message': 'Invalid Transfer Market URL. Please provide a player or team URL.'})
                
            except Exception as e:
                return JsonResponse({'type': 'Error', 'message': f'Error scraping Transfer Market: {str(e)}'})

        else:
            # Process JSON data
            try:
                import json
                scraped_data = json.loads(request.POST.get('scraped_data', '[]'))
            except json.JSONDecodeError:
                return JsonResponse({'type': 'Error', 'message': 'Invalid JSON data provided'})

            for player_data in scraped_data:
                result = process_transfermarkt_player_data(player_data, transfermarkt_source, request.user)
                
                if result['action'] == 'created':
                    added += 1
                elif result['action'] == 'updated':
                    updated += 1
                elif result['action'] == 'conflict':
                    conflicts += 1
                
                processed += 1

        success_message = f'Transfer Market data processed. Processed: {processed}, Added: {added}, Updated: {updated}'
        if conflicts > 0:
            success_message += f', Conflicts: {conflicts}'
        
        return JsonResponse({'type': 'Success', 'message': success_message})

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})


def process_transfermarkt_player_data(player_data, source, user):
    """
    Process individual player data from Transfer Market scraping
    """
    try:
        # Extract Transfer Market ID from href or use provided ID
        transfermarkt_id = player_data.get('id') or extract_transfermarkt_id(player_data.get('href', ''))
        
        if not transfermarkt_id:
            return {'action': 'error', 'error': 'No Transfer Market ID found'}

        # Try to find existing player by Transfer Market ID
        player = MultiSourcePlayers.objects.filter(
            transfermarkt_id=transfermarkt_id
        ).first()

        if not player:
            # Try to find by name (fuzzy matching)
            player_name = player_data.get('name', '').strip()
            if player_name:
                player = MultiSourcePlayers.objects.filter(
                    name__iexact=player_name
                ).first()

        if player:
            # Update existing player with Transfer Market data
            player.update_from_source(source, player_data, user)
            action = 'updated'
        else:
            # Create new player from Transfer Market data
            player = create_player_from_transfermarkt(player_data, source)
            if player:
                player.update_from_source(source, player_data, user)
                action = 'created'
            else:
                return {'action': 'error', 'error': 'Failed to create player'}

        return {'action': action, 'player': player}

    except Exception as e:
        return {'action': 'error', 'error': str(e)}


def create_player_from_transfermarkt(player_data, source):
    """
    Create a new player from Transfer Market data
    """
    try:
        player = MultiSourcePlayers(
            transfermarkt_id=player_data.get('id') or extract_transfermarkt_id(player_data.get('href', '')),
            transfermarkt_code=player_data.get('code'),
            name=player_data.get('name'),
            primary_data_source=source
        )
        
        # Parse birthdate if available
        if player_data.get('date_of_birth'):
            try:
                # Transfer Market format might be "Jan 1, 1990 (30)"
                birthdate_str = player_data['date_of_birth'].split(' (')[0]
                birthdate_obj = datetime.strptime(birthdate_str, '%b %d, %Y').date()
                player.birthdate = birthdate_obj
            except (ValueError, TypeError):
                pass
        
        player.save()
        return player
    except Exception as e:
        print(f"Error creating player from Transfer Market: {e}")
        return None


def extract_transfermarkt_id(href):
    """
    Extract Transfer Market player ID from URL
    """
    import re
    if not href:
        return None
    
    # Transfer Market URLs typically have format: /player-name/profil/spieler/12345
    match = re.search(r'/spieler/(\d+)', href)
    return match.group(1) if match else None


@csrf_exempt
@login_required
def AdminManualPlayerEntry(request):
    """
    Function to handle manual player data entry
    """
    if request.method == "POST":
        # Initialize data sources if they don't exist
        initialize_data_sources()
        
        try:
            manual_source = DataSource.objects.get(slug='manual')
        except DataSource.DoesNotExist:
            return JsonResponse({'type': 'Error', 'message': 'Manual data source not found'})

        # Extract form data
        player_data = {
            'name': request.POST.get('name'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'position': request.POST.get('position'),
            'height': request.POST.get('height'),
            'weight': request.POST.get('weight'),
            'birthdate': request.POST.get('birthdate'),
            'nationality': request.POST.get('nationality'),
            'current_market_value': request.POST.get('market_value'),
            'sport_id': request.POST.get('sport_id'),
            'team_id': request.POST.get('team_id'),
        }

        try:
            # Get sport
            sport_obj = None
            if player_data['sport_id']:
                sport_obj = Sport.objects.get(id=player_data['sport_id'])

            # Create or update player
            player_id = request.POST.get('player_id')
            if player_id:
                # Update existing player
                player = MultiSourcePlayers.objects.get(id=player_id)
                player.update_from_source(manual_source, player_data, request.user)
                message = f'Player {player.name} updated successfully.'
            else:
                # Create new player
                player = MultiSourcePlayers(
                    name=player_data['name'],
                    sport=sport_obj,
                    primary_data_source=manual_source,
                    manual_entry_id=f"manual_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
                player.save()
                player.update_from_source(manual_source, player_data, request.user)
                message = f'Player {player.name} created successfully.'

            return JsonResponse({'type': 'Success', 'message': message, 'player_id': player.id})

        except Exception as e:
            return JsonResponse({'type': 'Error', 'message': f'An error occurred: {str(e)}'})

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})


@csrf_exempt
@login_required
def AdminResolvePlayerConflicts(request):
    """
    Function to resolve data conflicts between different sources
    """
    if request.method == "POST":
        conflict_id = request.POST.get('conflict_id')
        resolution = request.POST.get('resolution')  # 'source_1', 'source_2', 'manual', 'ignore'
        manual_value = request.POST.get('manual_value', '')

        try:
            conflict = PlayerDataConflict.objects.get(id=conflict_id)
            
            if resolution in ['source_1', 'source_2', 'manual', 'ignore']:
                conflict.resolution_choice = resolution
                conflict.manual_value = manual_value if resolution == 'manual' else None
                conflict.resolved = True
                conflict.resolved_by = request.user
                conflict.resolved_at = timezone.now()
                conflict.save()

                # Apply the resolution to the player
                if resolution == 'source_1':
                    setattr(conflict.player, conflict.field_name, conflict.value_1)
                elif resolution == 'source_2':
                    setattr(conflict.player, conflict.field_name, conflict.value_2)
                elif resolution == 'manual':
                    setattr(conflict.player, conflict.field_name, manual_value)
                
                if resolution != 'ignore':
                    conflict.player.save()

                return JsonResponse({'type': 'Success', 'message': 'Conflict resolved successfully.'})
            else:
                return JsonResponse({'type': 'Error', 'message': 'Invalid resolution choice.'})

        except PlayerDataConflict.DoesNotExist:
            return JsonResponse({'type': 'Error', 'message': 'Conflict not found.'})
        except Exception as e:
            return JsonResponse({'type': 'Error', 'message': f'An error occurred: {str(e)}'})

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})


def AdminGetPlayerConflicts(request):
    """
    Get unresolved player data conflicts
    """
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        conflicts = PlayerDataConflict.objects.filter(resolved=False).select_related(
            'player', 'source_1', 'source_2'
        )

        conflicts_data = []
        for conflict in conflicts:
            conflicts_data.append({
                'id': conflict.id,
                'player_name': conflict.player.name,
                'field_name': conflict.field_name,
                'source_1': {
                    'name': conflict.source_1.name,
                    'value': conflict.value_1
                },
                'source_2': {
                    'name': conflict.source_2.name,
                    'value': conflict.value_2
                },
                'created_at': conflict.created_at.isoformat()
            })

        return JsonResponse({
            'type': 'Success', 
            'conflicts': conflicts_data,
            'count': len(conflicts_data)
        })

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})


def AdminGetDataSourceStats(request):
    """
    Get statistics about data sources and player coverage
    """
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        stats = {}
        
        for source in DataSource.objects.all():
            player_count = MultiSourcePlayers.objects.filter(
                data_sources=source
            ).count()
            
            primary_count = MultiSourcePlayers.objects.filter(
                primary_data_source=source
            ).count()
            
            stats[source.name] = {
                'total_players': player_count,
                'primary_source_for': primary_count,
                'priority': source.priority,
                'is_active': source.is_active
            }

        total_players = MultiSourcePlayers.objects.count()
        total_conflicts = PlayerDataConflict.objects.filter(resolved=False).count()

        return JsonResponse({
            'type': 'Success',
            'source_stats': stats,
            'total_players': total_players,
            'unresolved_conflicts': total_conflicts
        })

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})
