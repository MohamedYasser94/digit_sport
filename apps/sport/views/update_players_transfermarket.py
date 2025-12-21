"""
TransferMarket Player Data Update View
Updates existing Players with TransferMarket data while preserving Sportmonks data
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import Players, Sport
import re
from decimal import Decimal
import requests # <-- NEW: Import requests for API calls
from difflib import SequenceMatcher # <-- NEW: Import SequenceMatcher for fuzzy matching on live results

# --- Configuration ---
TM_API_BASE_URL = "https://transfermarkt-api.fly.dev"
# ---------------------


@csrf_exempt
@login_required
def AdminTransferMarketPlayersGetData(request):
    """
    Update Players model with TransferMarket data
    - Primary source: Sportmonks (for match/league integration)
    - Update source: TransferMarket (for detailed player info, market value, images)
    - Protected field: name_tr (manually added)
    - Now includes timeout, retries, and graceful error handling
    """
    if request.method == "POST":
        sport_type = request.POST.get('sport', 'football')

        try:
            # Get sport
            sport = Sport.objects.filter(name__iexact=sport_type).first()
            if not sport:
                return JsonResponse({
                    'type': 'Error',
                    'message': f'Sport "{sport_type}" not found'
                })

            # Get players from the main Players model (not MultiSourcePlayers)
            # Use prefetch_related for team to avoid N+1 queries in the loop
            players = Players.objects.filter(sport=sport).select_related('team')

            if not players.exists():
                return JsonResponse({
                    'type': 'Error',
                    'message': f'No players found for {sport_type}'
                })

            # Statistics
            stats = {
                'total': players.count(),
                'updated': 0,
                'matched': 0,
                'failed': 0,
                'skipped': 0,
                'errors': []
            }

            # Process each player with error handling
            for idx, player in enumerate(players):
                try:
                    # Get TransferMarket data for this player with timeout
                    tm_data = get_transfermarket_data_for_player(player)

                    if tm_data:
                        try:
                            # Update player with TransferMarket data
                            update_player_with_transfermarket_data(player, tm_data)
                            stats['updated'] += 1
                            stats['matched'] += 1
                        except Exception as e:
                            stats['failed'] += 1
                            stats['errors'].append(f"Error updating {player.name}: {str(e)}")
                    else:
                        stats['skipped'] += 1

                except Exception as e:
                    stats['failed'] += 1
                    error_msg = f"Error getting data for {player.name}: {str(e)}"
                    stats['errors'].append(error_msg)
                    continue  # Continue with next player instead of failing entire batch

            success_message = (
                f"TransferMarket update completed. "
                f"Total: {stats['total']}, "
                f"Updated: {stats['updated']}, "
                f"Matched: {stats['matched']}, "
                f"Skipped: {stats['skipped']}, "
                f"Failed: {stats['failed']}"
            )

            if stats['errors']:
                success_message += f". Errors: {len(stats['errors'])}"

            response_status = 'Success' if stats['updated'] > 0 else 'Warning' if stats['skipped'] > 0 else 'Error'

            return JsonResponse({
                'type': response_status,
                'message': success_message,
                'stats': stats
            })

        except Exception as e:
            import traceback
            return JsonResponse({
                'type': 'Error',
                'message': f'Error processing TransferMarket data: {str(e)}',
                'error_detail': str(traceback.format_exc())[:500]
            })

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})


def fetch_transfermarkt_search_results(player_name):
    """
    Fetches a list of potential player matches from the Transfermarkt API
    using the player's name.
    Now uses robust API client with timeout and retries.
    Enhanced with URL encoding and multiple search strategies.
    Returns: List of player dictionaries from the API search result.
    """
    import urllib.parse
    from core.utils.api_client import get_api_client
    api_client = get_api_client()

    if not player_name:
        return []

    # Ensure player_name is a string
    if not isinstance(player_name, str):
        player_name = str(player_name) if player_name else ""

    player_name = player_name.strip()
    if not player_name:
        return []

    print(f'[TM Search] Searching for player: {player_name}')

    # URL encode the player name for safe API call
    encoded_name = urllib.parse.quote(player_name)
    search_url = f"{TM_API_BASE_URL}/players/search/{encoded_name}"

    try:
        data = api_client.get(search_url, timeout=15)
        if data is None:
            print(f'[TM Search] No data returned for: {player_name}')
            return []

        results = data.get('results', [])
        print(f'[TM Search] Found {len(results)} results for: {player_name}')
        return results
    except Exception as e:
        print(f"Error fetching Transfermarkt search results for '{player_name}': {e}", flush=True)
        return []


def fetch_transfermarkt_player_profile(player_id):
    """
    Fetches the full player profile from the Transfermarkt API using the player ID.
    Now uses robust API client with timeout and retries.
    Returns: Player profile dictionary or None.
    """
    from core.utils.api_client import get_api_client
    api_client = get_api_client()

    profile_url = f"{TM_API_BASE_URL}/players/{player_id}/profile"
    try:
        return api_client.get(profile_url, timeout=10)
    except Exception as e:
        print(f"Error fetching Transfermarkt profile for ID '{player_id}': {e}", flush=True)
        return None


def get_transfermarket_data_for_player(player):
    """
    Get TransferMarket data for a specific player.
    PRIORITY 1: Match by existing transfermarkt_id (using live API if possible)
    PRIORITY 2: Live search by full name and fuzzy match with team
    PRIORITY 3: Live search by name only (if team doesn't help)
    PRIORITY 4: Try alternative names (first_name, display_name, common_name)
    PRIORITY 5: Fallback to cached data (original logic)

    Returns TransferMarket data dict or None if not found
    """
    import logging
    logger = logging.getLogger(__name__)

    tm_data = None

    # --- PRIORITY 1: Match by existing transfermarkt_id (Live API) ---
    if player.transfermarkt_id:
        logger.info(f"Fetching by existing ID: {player.transfermarkt_id}")
        # Use the ID to fetch the full, up-to-date profile
        tm_data = fetch_transfermarkt_player_profile(player.transfermarkt_id)
        if tm_data:
            return tm_data

    # --- Prepare search names (prioritize full name, then alternatives) ---
    search_names = []

    # Primary: Use full name
    if player.name and isinstance(player.name, str) and player.name.strip():
        search_names.append(player.name.strip())

    # Alternative: display_name
    if player.display_name and isinstance(player.display_name, str) and player.display_name.strip():
        if player.display_name.strip() not in search_names:
            search_names.append(player.display_name.strip())

    # Alternative: common_name
    if player.common_name and isinstance(player.common_name, str) and player.common_name.strip():
        if player.common_name.strip() not in search_names:
            search_names.append(player.common_name.strip())

    # Alternative: first_name + last_name
    if player.first_name and player.last_name:
        full_name = f"{player.first_name} {player.last_name}".strip()
        if full_name and full_name not in search_names:
            search_names.append(full_name)

    # Alternative: just first_name (last resort)
    if player.first_name and isinstance(player.first_name, str) and player.first_name.strip():
        if player.first_name.strip() not in search_names:
            search_names.append(player.first_name.strip())

    # --- PRIORITY 2-4: Try each search name ---
    for search_name in search_names:
        logger.info(f"Searching TransferMarket for: {search_name}")
        search_results = fetch_transfermarkt_search_results(search_name)
        print(f'[TM] Search results for "{search_name}": {len(search_results)} found')

        if search_results:
            logger.info(f"Found {len(search_results)} results for '{search_name}'")

            # Try with team matching first (if team exists)
            if player.team and hasattr(player.team, 'name') and player.team.name:
                team_name = player.team.name if isinstance(player.team.name, str) else str(player.team.name)
                tm_data = fuzzy_match_live_results(search_name, team_name, search_results, player_obj=player)

                if tm_data:
                    logger.info(f"Matched with team: {tm_data.get('id')}")
                    # Save the newly found Transfermarkt ID
                    player.transfermarkt_id = tm_data.get('id')
                    player.save(update_fields=['transfermarkt_id'])
                    # Fetch full profile
                    full_profile = fetch_transfermarkt_player_profile(player.transfermarkt_id)
                    return full_profile if full_profile else tm_data

            # --- Try name-only matching (lower threshold) ---
            if not tm_data:
                logger.info(f"Trying name-only match for: {search_name}")
                tm_data = fuzzy_match_by_name_only(search_name, search_results, player_obj=player)

                if tm_data:
                    logger.info(f"Matched by name only: {tm_data.get('id')}")
                    # Save the newly found Transfermarkt ID
                    player.transfermarkt_id = tm_data.get('id')
                    player.save(update_fields=['transfermarkt_id'])
                    # Fetch full profile
                    full_profile = fetch_transfermarkt_player_profile(player.transfermarkt_id)
                    return full_profile if full_profile else tm_data

        # If we found a match, break the loop
        if tm_data:
            break

    # --- PRIORITY 5: Fallback to cached data (Original logic) ---
    logger.info(f"Trying cached data for: {player.name}")

    # Try to match by existing transfermarkt_id (using cache as a fallback)
    if player.transfermarkt_id:
        tm_data = find_tm_data_by_id(player.transfermarkt_id)
        if tm_data:
            return tm_data

    # Try to match by player name and team (using cache)
    if player.name and player.team and hasattr(player.team, 'name'):
        team_name = player.team.name if isinstance(player.team.name, str) else str(player.team.name)
        tm_data = find_tm_data_by_name_and_team(player.name, team_name)
        if tm_data:
            return tm_data

    # Try to match by player name only (using cache)
    if player.name:
        tm_data = find_tm_data_by_name(player.name)
        if tm_data:
            return tm_data

    logger.warning(f"No TransferMarket data found for: {player.name}")
    return None


def fuzzy_match_live_results(player_name, team_name, search_results, player_obj=None):
    """
    Applies fuzzy matching logic to the live API search results.
    Uses combined name (70%) and team (30%) similarity.
    Enhanced with additional validation criteria:
    - Market value (prioritize higher value/famous players)
    - Nationality matching (bonus if available)
    - Age range validation (if birthdate available)
    - Position matching (bonus if available)
    """
    import logging
    logger = logging.getLogger(__name__)

    best_match = None
    best_score = 0.0
    candidates = []

    # Ensure player_name and team_name are strings
    if not isinstance(player_name, str):
        player_name = str(player_name) if player_name else ""
    if not isinstance(team_name, str):
        team_name = str(team_name) if team_name else ""

    for tm_player in search_results:
        # Get the player name from TransferMarket result
        tm_name = tm_player.get('name', '')
        if isinstance(tm_name, dict):
            tm_name = tm_name.get('name', '') or tm_name.get('fullName', '') or str(tm_name)
        if not isinstance(tm_name, str):
            tm_name = str(tm_name) if tm_name else ''

        # Calculate name similarity
        name_similarity = SequenceMatcher(
            None,
            player_name.lower().strip(),
            tm_name.lower().strip()
        ).ratio()

        # Calculate team similarity if available
        team_similarity = 0.0
        tm_club = tm_player.get('club', {})
        tm_club_name = ''
        if isinstance(tm_club, dict):
            tm_club_name = tm_club.get('name', '') or ''
        elif isinstance(tm_club, str):
            tm_club_name = tm_club

        if not isinstance(tm_club_name, str):
            tm_club_name = str(tm_club_name) if tm_club_name else ''

        if tm_club_name and team_name:
            team_similarity = SequenceMatcher(
                None,
                team_name.lower().strip(),
                tm_club_name.lower().strip()
            ).ratio()

        # Combined score (70% name, 30% team)
        combined_score = (name_similarity * 0.7) + (team_similarity * 0.3)

        # Additional validation bonuses
        bonus_score = 0.0
        validation_details = []

        # Bonus 1: Nationality match (if player_obj has nationality)
        if player_obj and hasattr(player_obj, 'nationality') and player_obj.nationality:
            tm_nationality = tm_player.get('nationality', '') or tm_player.get('citizenship', '')
            if isinstance(tm_nationality, dict):
                tm_nationality = tm_nationality.get('name', '') or ''
            if not isinstance(tm_nationality, str):
                tm_nationality = str(tm_nationality) if tm_nationality else ''

            if tm_nationality and isinstance(player_obj.nationality, str):
                nationality_match = SequenceMatcher(
                    None,
                    player_obj.nationality.lower().strip(),
                    tm_nationality.lower().strip()
                ).ratio()
                if nationality_match >= 0.8:
                    bonus_score += 0.05  # 5% bonus for nationality match
                    validation_details.append(f"nationality:{nationality_match:.2f}")

        # Bonus 2: Age validation (if player_obj has age or birthdate)
        if player_obj and hasattr(player_obj, 'age') and player_obj.age:
            tm_age = tm_player.get('age')
            if tm_age:
                try:
                    age_diff = abs(int(player_obj.age) - int(tm_age))
                    if age_diff <= 2:  # Within 2 years
                        bonus_score += 0.03  # 3% bonus for age match
                        validation_details.append(f"age:{tm_age}")
                    elif age_diff > 5:  # More than 5 years difference - penalty
                        bonus_score -= 0.05
                        validation_details.append(f"age_mismatch:{age_diff}y")
                except (ValueError, TypeError):
                    pass  # Ignore if age conversion fails

        # Bonus 3: Position match (if player_obj has position)
        if player_obj and hasattr(player_obj, 'position') and player_obj.position:
            tm_position = tm_player.get('position', {})
            if isinstance(tm_position, dict):
                tm_position = tm_position.get('name', '')
            if tm_position:
                position_match = SequenceMatcher(
                    None,
                    player_obj.position.lower().strip(),
                    str(tm_position).lower().strip()
                ).ratio()
                if position_match >= 0.6:
                    bonus_score += 0.02  # 2% bonus for position match
                    validation_details.append(f"position:{position_match:.2f}")

        # Bonus 4: Market value indicator (prefer more famous/valuable players)
        tm_market_value = tm_player.get('marketValue', {})
        if isinstance(tm_market_value, dict):
            tm_market_value = tm_market_value.get('value', 0)

        # If market value is high (famous player), add small bonus
        if tm_market_value and isinstance(tm_market_value, (int, float)):
            if tm_market_value > 20000000:  # Over 20M euros - likely famous player
                bonus_score += 0.03
                validation_details.append(f"high_value:{tm_market_value}")

        # Final score with bonus
        final_score = combined_score + bonus_score

        logger.debug(f"Matching '{player_name}' vs '{tm_player.get('name')}': "
                    f"name={name_similarity:.2f}, team={team_similarity:.2f}, "
                    f"combined={combined_score:.2f}, bonus={bonus_score:.2f}, "
                    f"final={final_score:.2f} {validation_details}")

        # Store candidate for analysis
        candidates.append({
            'player': tm_player,
            'score': final_score,
            'name_sim': name_similarity,
            'team_sim': team_similarity,
            'bonus': bonus_score
        })

        # Track best match (threshold 0.70)
        if final_score > best_score and combined_score >= 0.70:
            best_score = final_score
            best_match = tm_player

    # Log all candidates for debugging
    if candidates:
        logger.info(f"Found {len(candidates)} candidates for '{player_name}':")
        for i, candidate in enumerate(sorted(candidates, key=lambda x: x['score'], reverse=True)[:3]):
            logger.info(f"  {i+1}. {candidate['player'].get('name')} at {candidate['player'].get('club', {}).get('name', 'N/A')} "
                       f"(ID: {candidate['player'].get('id')}) - Score: {candidate['score']:.3f}")

    if best_match:
        logger.info(f"Best match: {best_match.get('name')} at {best_match.get('club', {}).get('name', 'N/A')} "
                   f"(ID: {best_match.get('id')}) (final score: {best_score:.2f})")

    return best_match


def fuzzy_match_by_name_only(player_name, search_results, player_obj=None):
    """
    Matches player by name only (no team matching).
    Used when team matching fails or no team is available.
    Enhanced with validation and prioritization:
    - Uses 65% threshold for name similarity (lowered for famous players)
    - Prioritizes higher market value (famous players)
    - Validates nationality and age if available
    - Returns most likely candidate (usually the famous one)
    """
    import logging
    logger = logging.getLogger(__name__)

    best_match = None
    best_score = 0.0
    candidates = []

    # Ensure player_name is a string
    if not isinstance(player_name, str):
        player_name = str(player_name) if player_name else ""

    for tm_player in search_results:
        # Get the player name from TransferMarket result
        tm_name = tm_player.get('name', '')
        if isinstance(tm_name, dict):
            tm_name = tm_name.get('name', '') or tm_name.get('fullName', '') or str(tm_name)
        if not isinstance(tm_name, str):
            tm_name = str(tm_name) if tm_name else ''

        # Calculate name similarity
        name_similarity = SequenceMatcher(
            None,
            player_name.lower().strip(),
            tm_name.lower().strip()
        ).ratio()

        # Additional validation and prioritization
        bonus_score = 0.0
        validation_details = []

        # Validation 1: Nationality match
        if player_obj and hasattr(player_obj, 'nationality') and player_obj.nationality:
            tm_nationality = tm_player.get('nationality', '') or tm_player.get('citizenship', '')
            if isinstance(tm_nationality, dict):
                tm_nationality = tm_nationality.get('name', '') or ''
            if not isinstance(tm_nationality, str):
                tm_nationality = str(tm_nationality) if tm_nationality else ''

            if tm_nationality and isinstance(player_obj.nationality, str):
                nationality_match = SequenceMatcher(
                    None,
                    player_obj.nationality.lower().strip(),
                    tm_nationality.lower().strip()
                ).ratio()
                if nationality_match >= 0.8:
                    bonus_score += 0.1  # 10% bonus for nationality match in name-only
                    validation_details.append(f"nationality_match")

        # Validation 2: Age validation
        if player_obj and hasattr(player_obj, 'age') and player_obj.age:
            tm_age = tm_player.get('age')
            if tm_age:
                try:
                    age_diff = abs(int(player_obj.age) - int(tm_age))
                    if age_diff <= 2:
                        bonus_score += 0.05
                        validation_details.append(f"age_ok")
                    elif age_diff > 5:
                        bonus_score -= 0.1  # Penalty for age mismatch
                        validation_details.append(f"age_bad:{age_diff}y")
                except (ValueError, TypeError):
                    pass  # Ignore if age conversion fails

        # Prioritization: Market value (prefer famous players)
        tm_market_value = tm_player.get('marketValue', {})
        if isinstance(tm_market_value, dict):
            tm_market_value = tm_market_value.get('value', 0)
        if not isinstance(tm_market_value, (int, float)):
            tm_market_value = 0

        if tm_market_value and isinstance(tm_market_value, (int, float)):
            # Scale bonus based on market value
            if tm_market_value > 50000000:  # Over 50M - superstar
                bonus_score += 0.15
                validation_details.append(f"superstar:{tm_market_value/1000000:.0f}M")
            elif tm_market_value > 20000000:  # Over 20M - star player
                bonus_score += 0.10
                validation_details.append(f"star:{tm_market_value/1000000:.0f}M")
            elif tm_market_value > 5000000:  # Over 5M - established player
                bonus_score += 0.05
                validation_details.append(f"value:{tm_market_value/1000000:.0f}M")

        final_score = name_similarity + bonus_score

        logger.debug(f"Name-only matching '{player_name}' vs '{tm_name}': "
                    f"name={name_similarity:.2f}, bonus={bonus_score:.2f}, "
                    f"final={final_score:.2f} {validation_details}")

        # Store candidate
        candidates.append({
            'player': tm_player,
            'score': final_score,
            'name_sim': name_similarity,
            'bonus': bonus_score,
            'market_value': tm_market_value if isinstance(tm_market_value, (int, float)) else 0
        })

        # Use 65% threshold for name similarity (lowered for famous players with high market value)
        threshold = 0.65 if tm_market_value > 20000000 else 0.75
        if final_score > best_score and name_similarity >= threshold:
            best_score = final_score
            best_match = tm_player

    # Log all candidates for debugging
    if candidates:
        logger.info(f"Found {len(candidates)} name-only candidates for '{player_name}':")
        for i, candidate in enumerate(sorted(candidates, key=lambda x: x['score'], reverse=True)[:3]):
            tm_club = candidate['player'].get('club', {})
            club_name = tm_club.get('name', 'N/A') if isinstance(tm_club, dict) else str(tm_club) if tm_club else 'N/A'
            logger.info(f"  {i+1}. {candidate['player'].get('name')} at {club_name} "
                       f"(ID: {candidate['player'].get('id')}) - Score: {candidate['score']:.3f} (MV: €{candidate['market_value']/1000000:.1f}M)")

    if best_match:
        tm_club = best_match.get('club', {})
        club_name = tm_club.get('name', 'Unknown') if isinstance(tm_club, dict) else str(tm_club) if tm_club else 'Unknown'
        logger.info(f"Best name-only match: {best_match.get('name')} at {club_name} "
                   f"(ID: {best_match.get('id')}) (final score: {best_score:.2f})")

    return best_match


# --- Original functions (kept for compatibility with cached data fallback) ---

def find_tm_data_by_id(tm_id):
    """
    Find TransferMarket data by player ID (from cache)
    """
    if not tm_id:
        return None

    tm_players = _get_cached_tm_data()

    for player in tm_players:
        if str(player.get('id', '')).strip() == str(tm_id).strip():
            return player

    return None


# Global cache for TransferMarket data
_tm_data_cache = None


def _get_cached_tm_data():
    """Get or load TransferMarket data with caching"""
    global _tm_data_cache
    if _tm_data_cache is None:
        _tm_data_cache = load_transfermarket_data()
    return _tm_data_cache


def find_tm_data_by_name_and_team(player_name, team_name):
    """
    Find TransferMarket data by player name and team (from cache)
    More accurate matching using cached data
    """
    tm_players = _get_cached_tm_data()

    best_match = None
    best_score = 0.0

    for tm_player in tm_players:
        # Calculate name similarity
        name_similarity = SequenceMatcher(
            None,
            player_name.lower().strip(),
            tm_player.get('name', '').lower().strip()
        ).ratio()

        # Calculate team similarity if available
        team_similarity = 0.0
        if 'current_club' in tm_player and tm_player['current_club']:
            team_similarity = SequenceMatcher(
                None,
                team_name.lower().strip(),
                tm_player['current_club'].get('name', '').lower().strip()
            ).ratio()

        # Combined score (70% name, 30% team)
        combined_score = (name_similarity * 0.7) + (team_similarity * 0.3)

        # Require minimum 80% match
        if combined_score > best_score and combined_score >= 0.80:
            best_score = combined_score
            best_match = tm_player

    return best_match


def find_tm_data_by_name(player_name):
    """
    Find TransferMarket data by player name only (from cache)
    Less accurate - use as fallback, uses cached data
    """
    tm_players = _get_cached_tm_data()

    best_match = None
    best_score = 0.0

    for tm_player in tm_players:
        similarity = SequenceMatcher(
            None,
            player_name.lower().strip(),
            tm_player.get('name', '').lower().strip()
        ).ratio()

        # Require minimum 85% match for name-only
        if similarity > best_score and similarity >= 0.85:
            best_score = similarity
            best_match = tm_player

    return best_match


def load_transfermarket_data():
    """
    Load TransferMarket data from your existing system

    Priority:
    1. Use existing MultiSourcePlayers with TransferMarket data
    2. Check for cached JSON file
    3. Fall back to empty list

    Returns: List of TransferMarket player dictionaries
    """
    import os
    import json
    from django.conf import settings

    try:
        # Method 1: Get from existing MultiSourcePlayers with TransferMarket data
        from ..models.multi_source_players import MultiSourcePlayers

        multi_source_players = MultiSourcePlayers.objects.filter(
            transfermarkt_id__isnull=False
        ).exclude(transfermarkt_id='').values(
            'transfermarkt_id',
            'name',
            'image_url',
            'current_market_value',
            'highest_market_value',
            'height',
            'weight',
            'age',
            'position',
            'foot',
            'citizenship',
            'joined',
            'contract_expires',
            'player_agent_name',
            'outfitter',
            'current_club_name',
            'place_of_birth_city',
            'place_of_birth_country'
        )

        if multi_source_players.exists():
            data = []
            for player in multi_source_players:
                tm_player = {
                    'id': player.get('transfermarkt_id'),
                    'name': player.get('name'),
                    'image_url': player.get('image_url'),
                    'current_market_value': player.get('current_market_value'),
                    'highest_market_value': player.get('highest_market_value'),
                    'height': player.get('height'),
                    'weight': player.get('weight'),
                    'age': player.get('age'),
                    'position': player.get('position'),
                    'foot': player.get('foot'),
                    'citizenship': player.get('citizenship'),
                    'joined': player.get('joined'),
                    'contract_expires': player.get('contract_expires'),
                    'player_agent': {'name': player.get('player_agent_name')} if player.get('player_agent_name') else None,
                    'outfitter': player.get('outfitter'),
                    'current_club': {'name': player.get('current_club_name')} if player.get('current_club_name') else None,
                    'place_of_birth': {
                        'city': player.get('place_of_birth_city'),
                        'country': player.get('place_of_birth_country')
                    }
                }
                data.append(tm_player)

            if data:
                print(f"[TM] Loaded {len(data)} players from MultiSourcePlayers")
                return data
    except Exception as e:
        print(f"[TM] Error loading from MultiSourcePlayers: {e}")

    # Method 2: Check for cached JSON file
    try:
        json_cache_path = os.path.join(settings.BASE_DIR, 'scraped_data', 'transfermarket_players_cache.json')
        if os.path.exists(json_cache_path):
            with open(json_cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"[TM] Loaded {len(data)} players from JSON cache")
                return data
    except Exception as e:
        print(f"[TM] Error loading from JSON cache: {e}")

    # Method 3: Fall back to empty list
    print("[TM] No TransferMarket data loaded. Falling back to empty list.")
    return []


def _parse_market_value(value_str):
    """
    Helper function to parse market value string (e.g., '€50.00m', '£45.00k') into a Decimal.
    """
    if not isinstance(value_str, str):
        return value_str

    value_str = value_str.strip().lower().replace(',', '.')
    multiplier = 1

    if 'm' in value_str:
        multiplier = 1_000_000
        value_str = value_str.replace('m', '')
    elif 'k' in value_str:
        multiplier = 1_000
        value_str = value_str.replace('k', '')

    # Remove currency symbols (€, £, $, etc.)
    value_str = re.sub(r'[^\d\.]', '', value_str)

    try:
        return Decimal(value_str) * multiplier
    except:
        return None


def update_player_with_transfermarket_data(player, tm_data):
    """
    Update Player instance with TransferMarket data
    Handles both API response and cached data formats
    Includes comprehensive error handling for each field
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Ensure ID is saved
        if tm_data.get('id') and not player.transfermarkt_id:
            player.transfermarkt_id = tm_data['id']

        # Update name if empty (prefer existing)
        if not player.name and tm_data.get('name'):
            player.name = tm_data['name']

        # Update image
        if tm_data.get('image_url') and not player.image_path:
            player.image_path = tm_data['image_url']

        # Update market value
        try:
            market_value = tm_data.get('current_market_value') or tm_data.get('marketValue', {}).get('value')
            if market_value:
                if isinstance(market_value, str):
                    market_value = _parse_market_value(market_value)
                if market_value:
                    player.current_market_value = market_value
        except Exception as e:
            logger.warning(f"Error updating market value for {player.name}: {e}")

        # Update highest market value
        try:
            if tm_data.get('highest_market_value'):
                player.highest_market_value = tm_data['highest_market_value']
        except Exception as e:
            logger.warning(f"Error updating highest market value for {player.name}: {e}")

        # Update physical attributes
        try:
            if tm_data.get('height'):
                player.height = tm_data['height']
        except Exception as e:
            logger.warning(f"Error updating height for {player.name}: {e}")

        try:
            if tm_data.get('weight'):
                player.weight = tm_data['weight']
        except Exception as e:
            logger.warning(f"Error updating weight for {player.name}: {e}")

        try:
            if tm_data.get('age'):
                player.age = tm_data['age']
        except Exception as e:
            logger.warning(f"Error updating age for {player.name}: {e}")

        # Update position with validation
        try:
            if tm_data.get('position'):
                new_position = tm_data['position']

                # Handle position data - it might be a dict or a string
                if isinstance(new_position, dict):
                    # If it's a dict, try to get the 'name' or 'label' field
                    new_position = new_position.get('name') or new_position.get('label') or new_position.get('shortLabel') or str(new_position)

                # Only update if we have a valid string
                if new_position and isinstance(new_position, str):
                    # Log the change if position is different
                    if player.position:
                        if player.position.lower().strip() != new_position.lower().strip():
                            logger.info(f"Position change for {player.name}: {player.position} -> {new_position}")
                    player.position = new_position
        except Exception as e:
            logger.warning(f"Error updating position for {player.name}: {e}")

        try:
            if tm_data.get('foot'):
                player.foot = tm_data['foot']
        except Exception as e:
            logger.warning(f"Error updating foot for {player.name}: {e}")

        try:
            if tm_data.get('citizenship'):
                player.citizenship = tm_data['citizenship']
        except Exception as e:
            logger.warning(f"Error updating citizenship for {player.name}: {e}")

        # Update contract info
        try:
            if tm_data.get('joined'):
                player.joined = tm_data['joined']
        except Exception as e:
            logger.warning(f"Error updating joined date for {player.name}: {e}")

        try:
            if tm_data.get('contract_expires'):
                player.contract_expires = tm_data['contract_expires']
        except Exception as e:
            logger.warning(f"Error updating contract expiry for {player.name}: {e}")

        # Update agent info
        try:
            if tm_data.get('player_agent'):
                agent_name = tm_data['player_agent']
                if isinstance(agent_name, dict):
                    agent_name = agent_name.get('name')
                if agent_name:
                    player.player_agent_name = agent_name
        except Exception as e:
            logger.warning(f"Error updating player agent for {player.name}: {e}")

        try:
            if tm_data.get('outfitter'):
                player.outfitter = tm_data['outfitter']
        except Exception as e:
            logger.warning(f"Error updating outfitter for {player.name}: {e}")

        # Update birth location
        try:
            if tm_data.get('place_of_birth'):
                place = tm_data['place_of_birth']
                if isinstance(place, dict):
                    if place.get('city'):
                        player.place_of_birth_city = place['city']
                    if place.get('country'):
                        player.place_of_birth_country = place['country']
        except Exception as e:
            logger.warning(f"Error updating birth location for {player.name}: {e}")

        # Update timestamp
        player.market_value_last_updated = timezone.now()

        # Save player
        player.save()
        logger.info(f"Successfully updated {player.name} with TransferMarket data")

    except Exception as e:
        logger.error(f"Error updating player {player.name} with TransferMarket data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


def fetch_player_transfers(player_id):
    """
    Fetch player transfer history from TransferMarket API.

    Args:
        player_id: TransferMarket player ID

    Returns:
        List of transfer dictionaries or empty list on failure
    """
    from core.utils.api_client import get_api_client
    import logging
    logger = logging.getLogger(__name__)

    if not player_id:
        return []

    api_client = get_api_client()
    transfers_url = f"{TM_API_BASE_URL}/players/{player_id}/transfers"

    try:
        data = api_client.get(transfers_url, timeout=15)
        if data is None:
            logger.warning(f"No transfer data returned for player ID: {player_id}")
            return []

        transfers = data.get('transfers', [])
        logger.info(f"Found {len(transfers)} transfers for player ID: {player_id}")
        return transfers
    except Exception as e:
        logger.error(f"Error fetching transfers for player ID {player_id}: {e}")
        return []


def fetch_player_market_value_history(player_id):
    """
    Fetch player market value history from TransferMarket API.

    Args:
        player_id: TransferMarket player ID

    Returns:
        List of market value history dictionaries or empty list on failure
    """
    from core.utils.api_client import get_api_client
    import logging
    logger = logging.getLogger(__name__)

    if not player_id:
        return []

    api_client = get_api_client()
    market_value_url = f"{TM_API_BASE_URL}/players/{player_id}/market_value"

    try:
        data = api_client.get(market_value_url, timeout=15)
        if data is None:
            logger.warning(f"No market value history returned for player ID: {player_id}")
            return []

        history = data.get('marketValueHistory', [])
        logger.info(f"Found {len(history)} market value entries for player ID: {player_id}")
        return history
    except Exception as e:
        logger.error(f"Error fetching market value history for player ID {player_id}: {e}")
        return []


def save_player_transfers(player, transfers_data):
    """
    Save player transfer history to the Transfers model.

    Args:
        player: Players model instance
        transfers_data: List of transfer dictionaries from TransferMarket API

    Returns:
        Tuple of (added, updated, failed) counts
    """
    from ..models import Transfers, Teams
    from difflib import SequenceMatcher
    import logging
    logger = logging.getLogger(__name__)

    added, updated, failed = 0, 0, 0

    for transfer in transfers_data:
        try:
            # Extract transfer data
            transfer_date = transfer.get('date')
            from_team_name = None
            to_team_name = None
            fee = transfer.get('fee', {})

            # Get from team info
            from_team_data = transfer.get('from', {}) or transfer.get('oldClub', {})
            if from_team_data:
                from_team_name = from_team_data.get('clubName') or from_team_data.get('name')

            # Get to team info
            to_team_data = transfer.get('to', {}) or transfer.get('newClub', {})
            if to_team_data:
                to_team_name = to_team_data.get('clubName') or to_team_data.get('name')

            # Try to match teams with existing teams in database using fuzzy matching
            from_team_obj = None
            to_team_obj = None

            if from_team_name:
                from_team_obj = fuzzy_match_team(from_team_name)

            if to_team_name:
                to_team_obj = fuzzy_match_team(to_team_name)

            # Parse fee
            fee_value = None
            fee_currency = None
            if isinstance(fee, dict):
                fee_value = fee.get('value') or fee.get('fee')
                fee_currency = fee.get('currency', 'EUR')
            elif isinstance(fee, str):
                fee_value = fee

            # Parse market value at transfer time
            market_value = transfer.get('marketValue')
            if isinstance(market_value, dict):
                market_value = market_value.get('value')

            # Determine transfer type
            is_free = fee_value in [None, 0, 'free', 'Free', '-', 'loan', 'Loan']

            # Create or update transfer record
            defaults = {
                'player': player,
                'from_team': from_team_obj,
                'to_team': to_team_obj,
                'fee': str(fee_value) if fee_value else None,
                'market_value': str(market_value) if market_value else None,
                'market_value_currency': fee_currency or 'EUR',
                'free_transfer': 'Yes' if is_free else 'No',
                'status': 'Active',
            }

            # Parse date
            if transfer_date:
                from datetime import datetime
                try:
                    if isinstance(transfer_date, str):
                        # Try different date formats
                        for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%b %d, %Y']:
                            try:
                                defaults['date'] = datetime.strptime(transfer_date, fmt).date()
                                break
                            except ValueError:
                                continue
                except Exception as e:
                    logger.warning(f"Could not parse transfer date: {transfer_date}")

            # Look for existing transfer with same player, date, from_team, to_team
            existing = Transfers.objects.filter(
                player=player,
                date=defaults.get('date'),
                from_team=from_team_obj,
                to_team=to_team_obj
            ).first()

            if existing:
                # Update existing transfer
                for key, value in defaults.items():
                    if value is not None:
                        setattr(existing, key, value)
                existing.save()
                updated += 1
            else:
                # Create new transfer
                transfer_obj = Transfers(**defaults)
                transfer_obj.save()
                added += 1

        except Exception as e:
            logger.error(f"Error saving transfer for {player.name}: {e}")
            failed += 1

    logger.info(f"Transfer save results for {player.name}: Added={added}, Updated={updated}, Failed={failed}")
    return added, updated, failed


def fuzzy_match_team(team_name):
    """
    Try to match team name with existing teams in database using fuzzy matching.

    Args:
        team_name: Team name to match

    Returns:
        Teams model instance or None if no match found
    """
    from ..models import Teams
    from difflib import SequenceMatcher

    if not team_name or not isinstance(team_name, str):
        return None

    team_name = team_name.strip()

    # Try exact match first
    team = Teams.objects.filter(name__iexact=team_name).first()
    if team:
        return team

    # Try contains match
    team = Teams.objects.filter(name__icontains=team_name).first()
    if team:
        return team

    # Fuzzy match with threshold
    best_match = None
    best_score = 0.0

    for team in Teams.objects.all()[:500]:  # Limit to 500 teams for performance
        if team.name:
            similarity = SequenceMatcher(
                None,
                team_name.lower().strip(),
                team.name.lower().strip()
            ).ratio()

            if similarity > best_score and similarity >= 0.8:
                best_score = similarity
                best_match = team

    return best_match


def update_player_transfermarket_url(player, transfermarkt_url=None, transfermarkt_id=None):
    """
    Update player's TransferMarket URL and ID.
    This allows manually correcting the TransferMarket link.

    Args:
        player: Players model instance
        transfermarkt_url: Full TransferMarket URL (e.g., https://www.transfermarkt.com/player/profil/spieler/12345)
        transfermarkt_id: TransferMarket player ID (extracted from URL or provided directly)

    Returns:
        Tuple of (success, message)
    """
    import re
    import logging
    logger = logging.getLogger(__name__)

    try:
        # If URL is provided, extract the ID from it
        if transfermarkt_url:
            # Pattern to extract player ID from TransferMarket URL
            # Example: https://www.transfermarkt.com/mohamed-salah/profil/spieler/148455
            patterns = [
                r'/spieler/(\d+)',  # German format
                r'/player/(\d+)',   # English format
                r'/profil/spieler/(\d+)',  # Profile format
            ]

            extracted_id = None
            for pattern in patterns:
                match = re.search(pattern, transfermarkt_url)
                if match:
                    extracted_id = match.group(1)
                    break

            if extracted_id:
                transfermarkt_id = extracted_id
                player.transfermarkt_url = transfermarkt_url
                logger.info(f"Extracted TransferMarket ID {transfermarkt_id} from URL: {transfermarkt_url}")
            else:
                logger.warning(f"Could not extract ID from TransferMarket URL: {transfermarkt_url}")

        # Update the player with the new ID
        if transfermarkt_id:
            old_id = player.transfermarkt_id
            player.transfermarkt_id = str(transfermarkt_id)
            player.save(update_fields=['transfermarkt_id', 'transfermarkt_url'] if transfermarkt_url else ['transfermarkt_id'])

            message = f"Updated TransferMarket ID from {old_id} to {transfermarkt_id}"
            if transfermarkt_url:
                message += f" (URL: {transfermarkt_url})"

            logger.info(message)
            return True, message
        else:
            return False, "No valid TransferMarket ID provided"

    except Exception as e:
        logger.error(f"Error updating TransferMarket URL for {player.name}: {e}")
        return False, f"Error: {str(e)}"


def fetch_player_by_transfermarkt_id(transfermarkt_id):
    """
    Fetch player data directly by TransferMarket ID.
    Useful when you know the correct ID.

    Args:
        transfermarkt_id: TransferMarket player ID

    Returns:
        Player profile dictionary or None
    """
    from core.utils.api_client import get_api_client
    import logging
    logger = logging.getLogger(__name__)

    if not transfermarkt_id:
        return None

    api_client = get_api_client()
    profile_url = f"{TM_API_BASE_URL}/players/{transfermarkt_id}/profile"

    try:
        data = api_client.get(profile_url, timeout=15)
        if data:
            logger.info(f"Successfully fetched profile for TransferMarket ID: {transfermarkt_id}")
            return data
        else:
            logger.warning(f"No data returned for TransferMarket ID: {transfermarkt_id}")
            return None
    except Exception as e:
        logger.error(f"Error fetching profile for TransferMarket ID {transfermarkt_id}: {e}")
        return None


def get_transfermarket_url_for_player(player):
    """
    Generate the TransferMarket URL for a player based on their ID and name.

    Args:
        player: Players model instance

    Returns:
        TransferMarket URL string or None
    """
    if not player.transfermarkt_id:
        return None

    # Generate URL-friendly name
    name_slug = ""
    if player.name:
        import re
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        name_slug = player.name.lower().strip()
        name_slug = re.sub(r'[^\w\s-]', '', name_slug)
        name_slug = re.sub(r'[\s]+', '-', name_slug)
    else:
        name_slug = "player"

    return f"https://www.transfermarkt.com/{name_slug}/profil/spieler/{player.transfermarkt_id}"


def fetch_and_update_player_complete_data(player, force_refresh=False):
    """
    Fetch complete player data including profile, transfers, and market value history.

    Args:
        player: Players model instance
        force_refresh: If True, fetch new data even if player has TransferMarket ID

    Returns:
        Dictionary with results for each data type
    """
    import logging
    logger = logging.getLogger(__name__)

    results = {
        'profile': {'success': False, 'message': ''},
        'transfers': {'success': False, 'count': 0, 'message': ''},
        'market_value_history': {'success': False, 'count': 0, 'message': ''},
    }

    try:
        # Step 1: Get or fetch TransferMarket data
        if player.transfermarkt_id and not force_refresh:
            tm_data = fetch_transfermarkt_player_profile(player.transfermarkt_id)
        else:
            tm_data = get_transfermarket_data_for_player(player)

        if tm_data:
            # Update player profile
            update_player_with_transfermarket_data(player, tm_data)
            results['profile']['success'] = True
            results['profile']['message'] = 'Profile updated successfully'

            # Refresh player from DB
            player.refresh_from_db()

            # Step 2: Fetch and save transfers
            if player.transfermarkt_id:
                transfers = fetch_player_transfers(player.transfermarkt_id)
                if transfers:
                    added, updated, failed = save_player_transfers(player, transfers)
                    results['transfers']['success'] = True
                    results['transfers']['count'] = added + updated
                    results['transfers']['message'] = f'Added: {added}, Updated: {updated}, Failed: {failed}'
                else:
                    results['transfers']['message'] = 'No transfers found'

                # Step 3: Fetch market value history
                mv_history = fetch_player_market_value_history(player.transfermarkt_id)
                if mv_history:
                    results['market_value_history']['success'] = True
                    results['market_value_history']['count'] = len(mv_history)
                    results['market_value_history']['message'] = f'Found {len(mv_history)} entries'
                    # Store in player's keyword field as JSON for now (or create separate model)
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

    except Exception as e:
        logger.error(f"Error in complete data fetch for {player.name}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        results['profile']['message'] = f'Error: {str(e)}'

    return results

