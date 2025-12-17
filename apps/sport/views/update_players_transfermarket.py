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
                'errors': []
            }

            # Process each player
            for player in players:
                try:
                    # Get TransferMarket data for this player
                    tm_data = get_transfermarket_data_for_player(player)

                    if tm_data:
                        # Update player with TransferMarket data
                        update_player_with_transfermarket_data(player, tm_data)
                        stats['updated'] += 1
                        stats['matched'] += 1
                    else:
                        stats['failed'] += 1

                except Exception as e:
                    stats['failed'] += 1
                    stats['errors'].append(f"Error updating {player.name}: {str(e)}")

            success_message = (
                f"TransferMarket update completed. "
                f"Total: {stats['total']}, "
                f"Updated: {stats['updated']}, "
                f"Matched: {stats['matched']}, "
                f"Failed: {stats['failed']}"
            )

            if stats['errors']:
                success_message += f". Errors: {len(stats['errors'])}"

            return JsonResponse({
                'type': 'Success',
                'message': success_message,
                'stats': stats
            })

        except Exception as e:
            return JsonResponse({
                'type': 'Error',
                'message': f'Error processing TransferMarket data: {str(e)}'
            })

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})


def fetch_transfermarkt_search_results(player_name):
    """
    NEW: Fetches a list of potential player matches from the Transfermarkt API
    using the player's name.
    Returns: List of player dictionaries from the API search result.
    """
    search_url = f"{TM_API_BASE_URL}/players/search/{player_name}"
    try:
        response = requests.get(search_url, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        return data.get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Transfermarkt search results for '{player_name}': {e}", flush=True)
        return []


def fetch_transfermarkt_player_profile(player_id):
    """
    NEW: Fetches the full player profile from the Transfermarkt API using the player ID.
    Returns: Player profile dictionary or None.
    """
    profile_url = f"{TM_API_BASE_URL}/players/{player_id}/profile"
    try:
        response = requests.get(profile_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Transfermarkt profile for ID '{player_id}': {e}", flush=True)
        return None


def get_transfermarket_data_for_player(player):
    """
    Get TransferMarket data for a specific player.
    PRIORITY 1: Match by existing transfermarkt_id (using live API if possible)
    PRIORITY 2: Live search by name and fuzzy match with team
    PRIORITY 3: Fallback to cached data (original logic)

    Returns TransferMarket data dict or None if not found
    """
    tm_data = None

    # --- PRIORITY 1: Match by existing transfermarkt_id (Live API) ---
    if player.transfermarkt_id:
        # Use the ID to fetch the full, up-to-date profile
        tm_data = fetch_transfermarkt_player_profile(player.transfermarkt_id)
        if tm_data:
            return tm_data

    # --- PRIORITY 2: Live search by name and fuzzy match with team ---
    if player.name and player.team:
        search_results = fetch_transfermarkt_search_results(player.name)
        if search_results:
            # Use fuzzy matching on the live search results
            tm_data = fuzzy_match_live_results(player.name, player.team.name, search_results)

            if tm_data:
                # IMPORTANT: Save the newly found Transfermarkt ID for future runs
                player.transfermarkt_id = tm_data.get('id')
                player.save(update_fields=['transfermarkt_id'])
                # Now fetch the full profile using the ID
                full_profile = fetch_transfermarkt_player_profile(player.transfermarkt_id)
                return full_profile if full_profile else tm_data # Return full profile if successful, otherwise the search result

    # --- PRIORITY 3: Fallback to cached data (Original logic) ---
    # The original logic using cached data is kept as a fallback.

    # Try to match by existing transfermarkt_id (using cache as a fallback)
    if player.transfermarkt_id:
        tm_data = find_tm_data_by_id(player.transfermarkt_id)
        if tm_data:
            return tm_data

    # Try to match by player name and team (using cache)
    if player.name and player.team:
        tm_data = find_tm_data_by_name_and_team(player.name, player.team.name)
        if tm_data:
            return tm_data

    # Try to match by player name only (using cache)
    if player.name:
        tm_data = find_tm_data_by_name(player.name)
        if tm_data:
            return tm_data

    return None


def fuzzy_match_live_results(player_name, team_name, search_results):
    """
    Applies fuzzy matching logic to the live API search results.
    This is similar to the original find_tm_data_by_name_and_team but adapted
    for the structure of the search results.
    """
    best_match = None
    best_score = 0.0

    for tm_player in search_results:
        # Calculate name similarity
        name_similarity = SequenceMatcher(
            None,
            player_name.lower().strip(),
            tm_player.get('name', '').lower().strip()
        ).ratio()

        # Calculate team similarity if available
        team_similarity = 0.0
        # The search result structure has 'club' with 'name'
        tm_club_name = tm_player.get('club', {}).get('name', '')
        if tm_club_name:
            team_similarity = SequenceMatcher(
                None,
                team_name.lower().strip(),
                tm_club_name.lower().strip()
            ).ratio()

        # Combined score (70% name, 30% team)
        combined_score = (name_similarity * 0.7) + (team_similarity * 0.3)

        # Require minimum 80% match
        if combined_score > best_score and combined_score >= 0.80:
            best_score = combined_score
            best_match = tm_player

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
    """
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
    market_value = tm_data.get('current_market_value') or tm_data.get('marketValue', {}).get('value')
    if market_value:
        if isinstance(market_value, str):
            market_value = _parse_market_value(market_value)
        if market_value:
            player.current_market_value = market_value

    # Update highest market value
    if tm_data.get('highest_market_value'):
        player.highest_market_value = tm_data['highest_market_value']

    # Update physical attributes
    if tm_data.get('height'):
        player.height = tm_data['height']

    if tm_data.get('weight'):
        player.weight = tm_data['weight']

    if tm_data.get('age'):
        player.age = tm_data['age']

    if tm_data.get('position'):
        player.position = tm_data['position']

    if tm_data.get('foot'):
        player.foot = tm_data['foot']

    if tm_data.get('citizenship'):
        player.citizenship = tm_data['citizenship']

    # Update contract info
    if tm_data.get('joined'):
        player.joined = tm_data['joined']

    if tm_data.get('contract_expires'):
        player.contract_expires = tm_data['contract_expires']

    # Update agent info
    if tm_data.get('player_agent'):
        player.player_agent_name = tm_data['player_agent'].get('name')

    if tm_data.get('outfitter'):
        player.outfitter = tm_data['outfitter']

    # Update birth location
    if tm_data.get('place_of_birth'):
        place = tm_data['place_of_birth']
        if place.get('city'):
            player.place_of_birth_city = place['city']
        if place.get('country'):
            player.place_of_birth_country = place['country']

    # Update timestamp
    player.market_value_last_updated = timezone.now()

    # Save player
    player.save()

