
"""
Player Search API - Search for players by name and get filtered results
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from ..models import Players, Sport
from django.db.models import Q


@csrf_exempt
@login_required
def search_players_api(request):
    """
    Search for players by name

    Parameters:
    - q: search query (player name)
    - sport: filter by sport (optional)
    - limit: number of results (default: 20)

    Returns: JSON list of players
    """
    if request.method == "POST":
        search_query = request.POST.get('q', '').strip()
        sport_filter = request.POST.get('sport', '').strip()
        limit = int(request.POST.get('limit', 20))

        if not search_query or len(search_query) < 2:
            return JsonResponse({
                'type': 'Error',
                'message': 'Search query must be at least 2 characters',
                'results': []
            })

        try:
            # Build query
            players_query = Players.objects.filter(
                Q(name__icontains=search_query) |
                Q(common_name__icontains=search_query) |
                Q(display_name__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            ).select_related('team', 'sport')

            # Filter by sport if provided
            if sport_filter:
                sport = Sport.objects.filter(name__iexact=sport_filter).first()
                if sport:
                    players_query = players_query.filter(sport=sport)

            # Apply limit
            players = players_query[:limit]

            # Build results
            results = []
            for player in players:
                results.append({
                    'id': player.id,
                    'name': player.name or player.common_name or player.display_name or 'Unknown',
                    'team': player.team.name if player.team else 'No Team',
                    'position': player.position or 'Unknown',
                    'slug': player.slug,
                    'image': player.get_image() or player.image_path or '',
                    'market_value': player.current_market_value or 'N/A'
                })

            return JsonResponse({
                'type': 'Success',
                'message': f'Found {len(results)} players',
                'results': results,
                'total_count': players_query.count()
            })

        except Exception as e:
            return JsonResponse({
                'type': 'Error',
                'message': f'Search error: {str(e)}',
                'results': []
            })

    return JsonResponse({
        'type': 'Error',
        'message': 'Invalid request method. Use POST',
        'results': []
    })


@csrf_exempt
@login_required
def get_player_by_name(request):
    """
    Get a specific player by exact name match

    Parameters:
    - name: player name (exact or partial)

    Returns: JSON player object
    """
    if request.method == "POST":
        player_name = request.POST.get('name', '').strip()

        if not player_name:
            return JsonResponse({
                'type': 'Error',
                'message': 'Player name required'
            })

        try:
            # Try exact match first
            player = Players.objects.filter(
                Q(name__iexact=player_name) |
                Q(common_name__iexact=player_name) |
                Q(display_name__iexact=player_name)
            ).first()

            if not player:
                return JsonResponse({
                    'type': 'Error',
                    'message': f'Player "{player_name}" not found'
                })

            return JsonResponse({
                'type': 'Success',
                'player': {
                    'id': player.id,
                    'name': player.name,
                    'common_name': player.common_name,
                    'display_name': player.display_name,
                    'team': player.team.name if player.team else None,
                    'position': player.position,
                    'number': player.number,
                    'age': player.age,
                    'height': player.height,
                    'weight': player.weight,
                    'market_value': player.current_market_value,
                    'image': player.get_image() or player.image_path,
                    'slug': player.slug
                }
            })

        except Exception as e:
            return JsonResponse({
                'type': 'Error',
                'message': f'Error: {str(e)}'
            })

    return JsonResponse({
        'type': 'Error',
        'message': 'Invalid request method. Use POST'
    })

