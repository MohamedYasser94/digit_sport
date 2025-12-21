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


def format_market_value(value):
    """
    Format a numeric market value into a readable string (e.g., €12.00m).

    Args:
        value: Numeric value in EUR

    Returns:
        Formatted string like '€12.00m' or '€500k'
    """
    if not value:
        return None

    try:
        value = float(value)
        if value >= 1_000_000:
            return f"€{value / 1_000_000:.2f}m"
        elif value >= 1_000:
            return f"€{value / 1_000:.0f}k"
        else:
            return f"€{value:.0f}"
    except (ValueError, TypeError):
        return str(value) if value else None


def parse_date_string(date_str):
    """
    Parse various date string formats into a date object.

    Args:
        date_str: Date string in various formats

    Returns:
        datetime.date object or None
    """
    from datetime import datetime

    if not date_str:
        return None

    # Common date formats
    formats = [
        '%Y-%m-%d',      # 2023-01-01
        '%d/%m/%Y',      # 01/01/2023
        '%d.%m.%Y',      # 01.01.2023
        '%d-%m-%Y',      # 01-01-2023
        '%b %d, %Y',     # Jan 01, 2023
        '%B %d, %Y',     # January 01, 2023
        '%Y',            # 2023 (just year)
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue

    return None


def update_player_with_transfermarket_data(player, tm_data):
    """
    Update Player instance with TransferMarket data
    Handles both API response and cached data formats
    Includes comprehensive error handling for each field
    """
    import logging
    from datetime import datetime
    logger = logging.getLogger(__name__)

    try:
        # Ensure ID is saved
        if tm_data.get('id') and not player.transfermarkt_id:
            player.transfermarkt_id = tm_data['id']

        # Update URL
        if tm_data.get('url'):
            player.transfermarkt_url = tm_data['url']

        # Update name if empty (prefer existing)
        if not player.name and tm_data.get('name'):
            player.name = tm_data['name']

        # Update full name
        try:
            if tm_data.get('fullName'):
                player.full_name = tm_data['fullName']
        except Exception as e:
            logger.warning(f"Error updating full name for {player.name}: {e}")

        # Update description
        try:
            if tm_data.get('description'):
                player.description = tm_data['description']
        except Exception as e:
            logger.warning(f"Error updating description for {player.name}: {e}")

        # Update image
        if tm_data.get('imageUrl') or tm_data.get('image_url'):
            image_url = tm_data.get('imageUrl') or tm_data.get('image_url')
            if not player.image_path:
                player.image_path = image_url
            player.image_url = image_url

        # Update market value - handle both numeric and string formats
        try:
            market_value = tm_data.get('marketValue')
            if market_value:
                if isinstance(market_value, (int, float)):
                    player.current_market_value_numeric = int(market_value)
                    player.current_market_value = format_market_value(market_value)
                elif isinstance(market_value, dict):
                    val = market_value.get('value')
                    if val:
                        player.current_market_value_numeric = int(val) if isinstance(val, (int, float)) else None
                        player.current_market_value = format_market_value(val)
                elif isinstance(market_value, str):
                    parsed = _parse_market_value(market_value)
                    if parsed:
                        player.current_market_value = str(parsed)
                        player.current_market_value_numeric = int(parsed)
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
            height = tm_data.get('height')
            if height:
                if isinstance(height, int):
                    player.height_cm = height
                    player.height = f"{height} cm"
                else:
                    player.height = str(height)
        except Exception as e:
            logger.warning(f"Error updating height for {player.name}: {e}")

        try:
            if tm_data.get('weight'):
                player.weight = tm_data['weight']
        except Exception as e:
            logger.warning(f"Error updating weight for {player.name}: {e}")

        try:
            if tm_data.get('age'):
                player.age = str(tm_data['age'])
        except Exception as e:
            logger.warning(f"Error updating age for {player.name}: {e}")

        # Update is_retired
        try:
            if 'isRetired' in tm_data:
                player.is_retired = bool(tm_data['isRetired'])
        except Exception as e:
            logger.warning(f"Error updating is_retired for {player.name}: {e}")

        # Update position with validation
        try:
            position_data = tm_data.get('position')
            if position_data:
                if isinstance(position_data, dict):
                    # Handle structured position data
                    main_pos = position_data.get('main')
                    other_pos = position_data.get('other', [])

                    if main_pos:
                        player.main_position = main_pos
                        player.position = main_pos

                    if other_pos:
                        player.other_positions = other_pos
                elif isinstance(position_data, str):
                    player.position = position_data
                    player.main_position = position_data
        except Exception as e:
            logger.warning(f"Error updating position for {player.name}: {e}")

        # Update foot
        try:
            if tm_data.get('foot'):
                player.foot = tm_data['foot']
        except Exception as e:
            logger.warning(f"Error updating foot for {player.name}: {e}")

        # Update citizenship - handle both string and list formats
        try:
            citizenship = tm_data.get('citizenship')
            if citizenship:
                if isinstance(citizenship, list):
                    player.citizenships = citizenship
                    player.citizenship = citizenship[0] if citizenship else None
                elif isinstance(citizenship, str):
                    player.citizenship = citizenship
        except Exception as e:
            logger.warning(f"Error updating citizenship for {player.name}: {e}")

        # Update shirt number
        try:
            if tm_data.get('shirtNumber'):
                player.shirt_number = tm_data['shirtNumber']
                # Also extract just the number
                number_str = tm_data['shirtNumber'].replace('#', '').strip()
                if number_str.isdigit():
                    player.number = number_str
        except Exception as e:
            logger.warning(f"Error updating shirt number for {player.name}: {e}")

        # Update contract info from club data
        try:
            club_data = tm_data.get('club')
            if isinstance(club_data, dict):
                if club_data.get('joined'):
                    player.joined = club_data['joined']
                    player.joined_date = parse_date_string(club_data['joined'])

                if club_data.get('contractExpires'):
                    player.contract_expires = club_data['contractExpires']
                    player.contract_expires_date = parse_date_string(club_data['contractExpires'])
        except Exception as e:
            logger.warning(f"Error updating contract info for {player.name}: {e}")

        # Update agent info
        try:
            agent_data = tm_data.get('agent')
            if agent_data:
                if isinstance(agent_data, dict):
                    player.player_agent_name = agent_data.get('name')
                    if agent_data.get('url'):
                        player.player_agent_url = f"https://www.transfermarkt.com{agent_data['url']}"
                elif isinstance(agent_data, str):
                    player.player_agent_name = agent_data
        except Exception as e:
            logger.warning(f"Error updating player agent for {player.name}: {e}")

        try:
            if tm_data.get('outfitter'):
                player.outfitter = tm_data['outfitter']
        except Exception as e:
            logger.warning(f"Error updating outfitter for {player.name}: {e}")

        # Update social media
        try:
            if tm_data.get('socialMedia'):
                player.social_media = tm_data['socialMedia']
        except Exception as e:
            logger.warning(f"Error updating social media for {player.name}: {e}")

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

        # Update current club from TransferMarket
        try:
            current_club = tm_data.get('club') or tm_data.get('current_club') or tm_data.get('currentClub')
            if current_club:
                club_name = None
                if isinstance(current_club, dict):
                    club_name = current_club.get('name') or current_club.get('clubName')
                elif isinstance(current_club, str):
                    club_name = current_club

                if club_name:
                    # Save club name as team_text (for display without FK relationship)
                    player.team_text = club_name

                    # Try to match with existing team using fuzzy matching
                    matched_team = fuzzy_match_team(club_name)
                    if matched_team:
                        player.team = matched_team
                        player.in_team = 'Yes'
                        logger.info(f"Matched current club '{club_name}' to team: {matched_team.name}")
                    else:
                        logger.info(f"Could not match club '{club_name}' to existing team, saved as team_text")
        except Exception as e:
            logger.warning(f"Error updating current club for {player.name}: {e}")

        # Update country/nationality from TransferMarket
        try:
            # Try different field names for nationality
            tm_nationality = (
                tm_data.get('nationality') or
                tm_data.get('nationalities') or
                tm_data.get('country') or
                tm_data.get('citizenship')
            )

            if tm_nationality:
                nationality_name = None

                # Handle list of nationalities (take first one)
                if isinstance(tm_nationality, list) and len(tm_nationality) > 0:
                    first_nat = tm_nationality[0]
                    if isinstance(first_nat, dict):
                        nationality_name = first_nat.get('name') or first_nat.get('nationality')
                    else:
                        nationality_name = str(first_nat)
                elif isinstance(tm_nationality, dict):
                    nationality_name = tm_nationality.get('name') or tm_nationality.get('nationality')
                elif isinstance(tm_nationality, str):
                    nationality_name = tm_nationality

                if nationality_name and isinstance(nationality_name, str):
                    # Update api_nationality (raw from API)
                    player.api_nationality = nationality_name

                    # Try to match with Country_List choices
                    from helper.modelHelper import Country_List
                    country_choices = [choice[0] for choice in Country_List]

                    # Find best match in country choices
                    best_match = None
                    best_score = 0.0
                    for country in country_choices:
                        similarity = SequenceMatcher(
                            None,
                            nationality_name.lower().strip(),
                            country.lower().strip()
                        ).ratio()
                        if similarity > best_score and similarity >= 0.8:
                            best_score = similarity
                            best_match = country

                    if best_match:
                        player.nationality = best_match
                        player.country = best_match
                        logger.info(f"Matched nationality '{nationality_name}' to: {best_match}")
                    else:
                        # Just save as-is if no match
                        logger.info(f"Could not match nationality '{nationality_name}' to choices, keeping original")
        except Exception as e:
            logger.warning(f"Error updating nationality for {player.name}: {e}")

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
            from_team_tm_id = None
            to_team_tm_id = None
            fee = transfer.get('fee', {})

            # Get from team info - try multiple field names
            from_team_data = transfer.get('from', {}) or transfer.get('oldClub', {}) or transfer.get('clubFrom', {})
            if from_team_data:
                if isinstance(from_team_data, dict):
                    from_team_name = from_team_data.get('clubName') or from_team_data.get('name')
                    from_team_tm_id = from_team_data.get('id') or from_team_data.get('clubId')
                elif isinstance(from_team_data, str):
                    from_team_name = from_team_data

            # Get to team info - try multiple field names
            to_team_data = transfer.get('to', {}) or transfer.get('newClub', {}) or transfer.get('clubTo', {})
            if to_team_data:
                if isinstance(to_team_data, dict):
                    to_team_name = to_team_data.get('clubName') or to_team_data.get('name')
                    to_team_tm_id = to_team_data.get('id') or to_team_data.get('clubId')
                elif isinstance(to_team_data, str):
                    to_team_name = to_team_data

            # Try to match teams with existing teams in database using fuzzy matching
            from_team_obj = None
            to_team_obj = None

            if from_team_name:
                from_team_obj = fuzzy_match_team(from_team_name)
                logger.info(f"From team '{from_team_name}' matched: {from_team_obj.name if from_team_obj else 'NOT FOUND - saved as text'}")

            if to_team_name:
                to_team_obj = fuzzy_match_team(to_team_name)
                logger.info(f"To team '{to_team_name}' matched: {to_team_obj.name if to_team_obj else 'NOT FOUND - saved as text'}")

            # Parse fee - handle multiple formats
            fee_value = None
            fee_numeric = None
            fee_currency = 'EUR'

            if isinstance(fee, dict):
                fee_value = fee.get('value') or fee.get('fee')
                fee_currency = fee.get('currency', 'EUR')
            elif isinstance(fee, (int, float)):
                fee_numeric = int(fee)
                fee_value = format_market_value(fee)
            elif isinstance(fee, str):
                fee_value = fee

            # Also check for direct fee field
            if not fee_value and transfer.get('fee'):
                raw_fee = transfer.get('fee')
                if isinstance(raw_fee, (int, float)):
                    fee_numeric = int(raw_fee)
                    fee_value = format_market_value(raw_fee)
                else:
                    fee_value = str(raw_fee)

            # Parse market value at transfer time
            market_value = transfer.get('marketValue')
            market_value_numeric = None
            if isinstance(market_value, dict):
                market_value = market_value.get('value')
            if isinstance(market_value, (int, float)):
                market_value_numeric = int(market_value)
                market_value = format_market_value(market_value)
            elif market_value:
                market_value = str(market_value)

            # Get season
            season = transfer.get('season')

            # Determine transfer type
            is_free = fee_value in [None, 0, 'free', 'Free', '-', 'loan', 'Loan', '0', 'ablösefrei']
            is_loan = 'loan' in str(fee_value).lower() if fee_value else False
            is_upcoming = transfer.get('upcoming', False)

            # Get TransferMarket transfer ID
            tm_transfer_id = transfer.get('id') or transfer.get('transferId')

            # Create or update transfer record - ALWAYS save team names as text
            defaults = {
                'player': player,
                'from_team': from_team_obj,
                'to_team': to_team_obj,
                'from_team_name': from_team_name,  # Always save text name
                'to_team_name': to_team_name,      # Always save text name
                'from_team_tm_id': str(from_team_tm_id) if from_team_tm_id else None,
                'to_team_tm_id': str(to_team_tm_id) if to_team_tm_id else None,
                'fee': fee_value,
                'fee_numeric': fee_numeric,
                'fee_currency': fee_currency,
                'market_value': market_value,
                'market_value_numeric': market_value_numeric,
                'market_value_currency': 'EUR',
                'season': season,
                'free_transfer': 'Yes' if is_free else 'No',
                'is_loan': is_loan,
                'is_upcoming': is_upcoming,
                'transfermarkt_transfer_id': str(tm_transfer_id) if tm_transfer_id else None,
                'status': 'Active',
            }

            # Parse date
            if transfer_date:
                from datetime import datetime
                try:
                    if isinstance(transfer_date, str):
                        # Try different date formats
                        for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%b %d, %Y', '%Y-%m-%dT%H:%M:%S']:
                            try:
                                defaults['date'] = datetime.strptime(transfer_date.split('T')[0], fmt.split('T')[0]).date()
                                break
                            except ValueError:
                                continue
                except Exception as e:
                    logger.warning(f"Could not parse transfer date: {transfer_date}")

            # Look for existing transfer - by TM ID first, then by player/date/teams
            existing = None
            if tm_transfer_id:
                existing = Transfers.objects.filter(
                    transfermarkt_transfer_id=str(tm_transfer_id)
                ).first()

            if not existing:
                existing = Transfers.objects.filter(
                    player=player,
                    date=defaults.get('date'),
                    from_team_name=from_team_name,
                    to_team_name=to_team_name
                ).first()

            if not existing and from_team_obj and to_team_obj:
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
                    # Save to PlayerMarketValueHistory model
                    mv_added, mv_updated = save_player_market_value_history(player, mv_history)
                    results['market_value_history']['success'] = True
                    results['market_value_history']['count'] = mv_added + mv_updated
                    results['market_value_history']['message'] = f'Added: {mv_added}, Updated: {mv_updated}'

                    # Also update highest market value if we have history
                    if mv_history:
                        max_value = max(mv_history, key=lambda x: x.get('marketValue', 0) if isinstance(x.get('marketValue'), (int, float)) else 0, default=None)
                        if max_value:
                            player.highest_market_value_numeric = max_value.get('marketValue')
                            player.highest_market_value = format_market_value(max_value.get('marketValue'))
                            if max_value.get('date'):
                                player.highest_market_value_date = parse_date_string(max_value.get('date'))
                            player.save(update_fields=['highest_market_value', 'highest_market_value_numeric', 'highest_market_value_date'])
                else:
                    results['market_value_history']['message'] = 'No market value history found'

                # Step 4: Fetch and save detailed stats
                stats = fetch_player_stats(player.transfermarkt_id)
                if stats:
                    stats_added, stats_updated = save_player_season_stats(player, stats)

                    # Calculate career totals
                    update_player_career_totals(player)
        else:
            results['profile']['message'] = 'No TransferMarket data found'

    except Exception as e:
        logger.error(f"Error in complete data fetch for {player.name}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        results['profile']['message'] = f'Error: {str(e)}'

    return results


def save_player_market_value_history(player, mv_history):
    """
    Save player market value history to the PlayerMarketValueHistory model.

    Args:
        player: Players model instance
        mv_history: List of market value history dictionaries

    Returns:
        Tuple of (added, updated) counts
    """
    from ..models import PlayerMarketValueHistory, Teams
    import logging
    logger = logging.getLogger(__name__)

    added, updated = 0, 0

    for entry in mv_history:
        try:
            date = parse_date_string(entry.get('date'))
            market_value = entry.get('marketValue')

            if not date or not market_value:
                continue

            # Try to match club
            club_name = entry.get('clubName')
            club_tm_id = entry.get('clubId')
            club = None

            if club_name:
                club = fuzzy_match_team(club_name)

            defaults = {
                'age': entry.get('age'),
                'market_value': int(market_value) if isinstance(market_value, (int, float)) else None,
                'market_value_formatted': format_market_value(market_value),
                'club_name': club_name,
                'club_tm_id': str(club_tm_id) if club_tm_id else None,
                'club': club,
            }

            obj, created = PlayerMarketValueHistory.objects.update_or_create(
                player=player,
                date=date,
                market_value=defaults['market_value'],
                defaults=defaults
            )

            if created:
                added += 1
            else:
                updated += 1

        except Exception as e:
            logger.warning(f"Error saving market value history entry for {player.name}: {e}")
            continue

    logger.info(f"Market value history save results for {player.name}: Added={added}, Updated={updated}")
    return added, updated


def fetch_player_stats(player_id):
    """
    Fetch player detailed statistics from TransferMarket API.

    Args:
        player_id: TransferMarket player ID

    Returns:
        List of stats dictionaries or empty list on failure
    """
    from core.utils.api_client import get_api_client
    import logging
    logger = logging.getLogger(__name__)

    if not player_id:
        return []

    api_client = get_api_client()
    stats_url = f"{TM_API_BASE_URL}/players/{player_id}/stats"

    try:
        data = api_client.get(stats_url, timeout=15)
        if data is None:
            logger.warning(f"No stats returned for player ID: {player_id}")
            return []

        stats = data.get('stats', [])
        logger.info(f"Found {len(stats)} stat entries for player ID: {player_id}")
        return stats
    except Exception as e:
        logger.error(f"Error fetching stats for player ID {player_id}: {e}")
        return []


def save_player_season_stats(player, stats_data):
    """
    Save player season statistics to the PlayerSeasonStats model.

    Args:
        player: Players model instance
        stats_data: List of stats dictionaries from TransferMarket API

    Returns:
        Tuple of (added, updated) counts
    """
    from ..models import PlayerSeasonStats, Teams, Leagues
    import logging
    logger = logging.getLogger(__name__)

    added, updated = 0, 0

    for stat in stats_data:
        try:
            season = stat.get('seasonId') or stat.get('season')
            competition_tm_id = stat.get('competitionId')
            club_tm_id = stat.get('clubId')

            if not season:
                continue

            # Try to match club
            club_name = stat.get('clubName')
            club = None
            if club_name:
                club = fuzzy_match_team(club_name)

            # Try to match competition
            competition_name = stat.get('competitionName')
            competition = None
            if competition_name:
                competition = Leagues.objects.filter(name__icontains=competition_name).first()

            defaults = {
                'competition_tm_id': competition_tm_id,
                'competition_name': competition_name,
                'competition': competition,
                'club_name': club_name,
                'club': club,
                'appearances': stat.get('appearances', 0) or 0,
                'goals': stat.get('goals', 0) or 0,
                'assists': stat.get('assists', 0) or 0,
                'yellow_cards': stat.get('yellowCards', 0) or 0,
                'red_cards': stat.get('redCards', 0) or 0,
                'minutes_played': stat.get('minutesPlayed', 0) or 0,
            }

            obj, created = PlayerSeasonStats.objects.update_or_create(
                player=player,
                season=season,
                competition_tm_id=competition_tm_id,
                club_tm_id=str(club_tm_id) if club_tm_id else None,
                defaults=defaults
            )

            if created:
                added += 1
            else:
                updated += 1

        except Exception as e:
            logger.warning(f"Error saving season stats entry for {player.name}: {e}")
            continue

    logger.info(f"Season stats save results for {player.name}: Added={added}, Updated={updated}")
    return added, updated


def update_player_career_totals(player):
    """
    Calculate and update player career totals from season stats.

    Args:
        player: Players model instance
    """
    from django.db.models import Sum
    from ..models import PlayerSeasonStats
    import logging
    logger = logging.getLogger(__name__)

    try:
        totals = PlayerSeasonStats.objects.filter(player=player).aggregate(
            total_appearances=Sum('appearances'),
            total_goals=Sum('goals'),
            total_assists=Sum('assists'),
            total_yellow_cards=Sum('yellow_cards'),
            total_red_cards=Sum('red_cards'),
            total_minutes_played=Sum('minutes_played'),
        )

        player.total_appearances = totals['total_appearances'] or 0
        player.total_goals = totals['total_goals'] or 0
        player.total_assists = totals['total_assists'] or 0
        player.total_yellow_cards = totals['total_yellow_cards'] or 0
        player.total_red_cards = totals['total_red_cards'] or 0
        player.total_minutes_played = totals['total_minutes_played'] or 0

        player.save(update_fields=[
            'total_appearances', 'total_goals', 'total_assists',
            'total_yellow_cards', 'total_red_cards', 'total_minutes_played'
        ])

        logger.info(f"Updated career totals for {player.name}: Apps={player.total_appearances}, Goals={player.total_goals}, Assists={player.total_assists}")

    except Exception as e:
        logger.error(f"Error updating career totals for {player.name}: {e}")


def save_player_relatives(player, relatives_data):
    """
    Save player relatives to the PlayerRelative model.

    Args:
        player: Players model instance
        relatives_data: List of relative dictionaries from TransferMarket API

    Returns:
        Number of relatives saved
    """
    from ..models import PlayerRelative, Players
    import logging
    logger = logging.getLogger(__name__)

    saved = 0

    for relative in relatives_data:
        try:
            relative_tm_id = relative.get('id')
            relative_name = relative.get('name')

            if not relative_name:
                continue

            # Try to find relative in our players database
            relative_player = None
            if relative_tm_id:
                relative_player = Players.objects.filter(transfermarkt_id=str(relative_tm_id)).first()

            defaults = {
                'relative_name': relative_name,
                'relative_url': relative.get('url'),
                'profile_type': relative.get('profileType'),
                'relative_player': relative_player,
            }

            obj, created = PlayerRelative.objects.update_or_create(
                player=player,
                relative_tm_id=str(relative_tm_id) if relative_tm_id else None,
                defaults=defaults
            )

            if created:
                saved += 1

        except Exception as e:
            logger.warning(f"Error saving relative for {player.name}: {e}")
            continue

    logger.info(f"Saved {saved} relatives for {player.name}")
    return saved


def fetch_player_achievements(player_id):
    """
    Fetch player achievements/trophies from TransferMarket API.

    Args:
        player_id: TransferMarket player ID

    Returns:
        List of achievement dictionaries or empty list on failure
    """
    from core.utils.api_client import get_api_client
    import logging
    logger = logging.getLogger(__name__)

    if not player_id:
        return []

    api_client = get_api_client()
    achievements_url = f"{TM_API_BASE_URL}/players/{player_id}/achievements"

    try:
        data = api_client.get(achievements_url, timeout=15)
        if data is None:
            logger.warning(f"No achievements returned for player ID: {player_id}")
            return []

        achievements = data.get('achievements', []) or data.get('titles', []) or data.get('trophies', [])
        logger.info(f"Found {len(achievements)} achievements for player ID: {player_id}")
        return achievements
    except Exception as e:
        logger.error(f"Error fetching achievements for player ID {player_id}: {e}")
        return []


def save_player_achievements(player, achievements_data):
    """
    Save player achievements/trophies to the PlayerAchievement model.

    Args:
        player: Players model instance
        achievements_data: List of achievement dictionaries from TransferMarket API

    Returns:
        Tuple of (added, updated) counts
    """
    from ..models import PlayerAchievement, Teams, Leagues
    import logging
    logger = logging.getLogger(__name__)

    added, updated = 0, 0

    for achievement in achievements_data:
        try:
            name = achievement.get('title') or achievement.get('name') or achievement.get('competition')
            if not name:
                continue

            # Determine achievement type
            achievement_type = 'trophy'
            name_lower = name.lower()
            if any(x in name_lower for x in ['ballon', 'fifa best', 'golden boot', 'golden ball', 'player of']):
                achievement_type = 'individual_award'
            elif any(x in name_lower for x in ['world cup', 'euro', 'copa america', 'nations league']):
                achievement_type = 'international'
            elif any(x in name_lower for x in ['league', 'liga', 'serie', 'bundesliga', 'ligue', 'premier']):
                achievement_type = 'league'
            elif any(x in name_lower for x in ['cup', 'copa', 'pokal', 'coupe']):
                achievement_type = 'cup'
            elif any(x in name_lower for x in ['champions', 'europa league', 'conference']):
                achievement_type = 'club'

            # Extract year/season
            season = achievement.get('season')
            year = achievement.get('year')
            if not year and season:
                # Try to extract year from season like "2023/24"
                try:
                    year = int(season.split('/')[0]) if '/' in str(season) else int(season)
                except (ValueError, AttributeError):
                    pass

            # Try to match club
            club_name = achievement.get('club') or achievement.get('clubName')
            club_tm_id = achievement.get('clubId')
            club = None
            if club_name:
                club = fuzzy_match_team(club_name)

            # Try to match competition
            competition_name = achievement.get('competition') or achievement.get('competitionName')
            competition_tm_id = achievement.get('competitionId')
            competition = None
            if competition_name:
                competition = Leagues.objects.filter(name__icontains=competition_name).first()

            # Check if international
            is_international = achievement.get('isInternational', False)
            if not is_international:
                is_international = any(x in name_lower for x in ['world cup', 'euro', 'copa america', 'nations league', 'national team'])

            defaults = {
                'achievement_type': achievement_type,
                'competition': competition,
                'competition_name': competition_name,
                'competition_tm_id': str(competition_tm_id) if competition_tm_id else None,
                'club': club,
                'club_name': club_name,
                'club_tm_id': str(club_tm_id) if club_tm_id else None,
                'season': season,
                'year': year,
                'count': achievement.get('count', 1) or 1,
                'description': achievement.get('description'),
                'image_url': achievement.get('imageUrl') or achievement.get('image'),
                'is_international': is_international,
                'national_team': achievement.get('nationalTeam'),
            }

            # Try to find existing by name, player, and year/season
            obj, created = PlayerAchievement.objects.update_or_create(
                player=player,
                name=name,
                year=year,
                season=season,
                defaults=defaults
            )

            if created:
                added += 1
            else:
                updated += 1

        except Exception as e:
            logger.warning(f"Error saving achievement for {player.name}: {e}")
            continue

    logger.info(f"Achievement save results for {player.name}: Added={added}, Updated={updated}")
    return added, updated


def save_player_awards(player, awards_data):
    """
    Save player individual awards to the PlayerAward model.

    Args:
        player: Players model instance
        awards_data: List of award dictionaries from TransferMarket API

    Returns:
        Tuple of (added, updated) counts
    """
    from ..models import PlayerAward, Leagues
    import logging
    logger = logging.getLogger(__name__)

    added, updated = 0, 0

    for award in awards_data:
        try:
            name = award.get('title') or award.get('name') or award.get('award')
            if not name:
                continue

            # Determine award category
            category = 'other'
            name_lower = name.lower()
            if 'ballon' in name_lower:
                category = 'ballon_dor'
            elif 'fifa best' in name_lower or 'fifa player' in name_lower:
                category = 'fifa_best'
            elif 'golden boot' in name_lower or 'top scorer' in name_lower:
                category = 'golden_boot'
            elif 'golden ball' in name_lower:
                category = 'golden_ball'
            elif 'player of the month' in name_lower:
                category = 'player_of_month'
            elif 'player of the year' in name_lower or 'player of year' in name_lower:
                category = 'player_of_year'
            elif 'mvp' in name_lower or 'most valuable' in name_lower:
                category = 'mvp'
            elif 'best player' in name_lower:
                category = 'best_player'

            # Extract year/season
            season = award.get('season')
            year = award.get('year')
            if not year and season:
                try:
                    year = int(season.split('/')[0]) if '/' in str(season) else int(season)
                except (ValueError, AttributeError):
                    pass

            # Try to match competition
            competition_name = award.get('competition') or award.get('competitionName')
            competition = None
            if competition_name:
                competition = Leagues.objects.filter(name__icontains=competition_name).first()

            defaults = {
                'category': category,
                'competition': competition,
                'competition_name': competition_name,
                'season': season,
                'ranking': award.get('ranking', 1) or 1,
                'goals': award.get('goals'),
                'assists': award.get('assists'),
                'appearances': award.get('appearances'),
                'description': award.get('description'),
                'image_url': award.get('imageUrl') or award.get('image'),
            }

            obj, created = PlayerAward.objects.update_or_create(
                player=player,
                name=name,
                year=year,
                season=season,
                defaults=defaults
            )

            if created:
                added += 1
            else:
                updated += 1

        except Exception as e:
            logger.warning(f"Error saving award for {player.name}: {e}")
            continue

    logger.info(f"Award save results for {player.name}: Added={added}, Updated={updated}")
    return added, updated

