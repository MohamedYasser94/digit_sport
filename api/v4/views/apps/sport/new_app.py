import threading
from collections import defaultdict
from datetime import timedelta, time
from django.db import DatabaseError
from django.http import JsonResponse
from django.utils import timezone as django_timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from django.shortcuts import get_object_or_404
from api.v4.serializers.blog import BlogArticleSerializer, BlogVideoSerializer
from api.v4.serializers.sport.sport import *
from api.v4.serializers.sport.favorite import FavoriteToggleSerializer
from apps.sport.models.models import *
from apps.sport.models.operations import MatchPlayerReport, MatchPlayerReportSerializer
from apps.sport.views.fetch_monks import _fetch_and_store_fixtures_from_source
from core.models.blog import BlogArticle, BlogVideo
from digit_sport import settings
from datetime import datetime, time, timezone

api_key = settings.SPORT_MONKS_TOKEN
base_url = settings.SPORT_MONKS_URL

############# Home Fixtures api urls #############

def _get_serialized_fixtures_for_date(fetch_date, sport_obj, request=None):
    """
    Modified to return data from both Fixtures and Match models
    """
    start_of_day_utc = datetime.combine(fetch_date, time.min, tzinfo=timezone.utc)
    end_of_day_utc = datetime.combine(fetch_date, time.max, tzinfo=timezone.utc)

    fixtures_for_day = Fixtures.objects.filter(
        starting_at__range=(start_of_day_utc, end_of_day_utc),
        sport=sport_obj
    ).select_related('league', 'season').prefetch_related('participants__team').order_by('league__name', 'starting_at')

    matches_for_day = Match.objects.filter(
        start_time__range=(start_of_day_utc, end_of_day_utc),
        sport=sport_obj,
        status='Active'
    ).select_related('league', 'home_team', 'away_team').order_by('league__name', 'start_time')

    leagues_data = []
    
    fixtures_by_league = defaultdict(list)
    for fixture in fixtures_for_day:
        if fixture.league:
            fixtures_by_league[fixture.league].append(fixture)
    
    matches_by_league = defaultdict(list)
    for match in matches_for_day:
        if match.league:
            matches_by_league[match.league].append(match)

    all_leagues = set(list(fixtures_by_league.keys()) + list(matches_by_league.keys()))
    
    for league in sorted(all_leagues, key=lambda x: x.name if x else ""):
        league_serializer = SimpleLeagueSerializer(league,context={'request': request})
        league_fixtures = fixtures_by_league.get(league, [])
        fixture_serializer = FixtureSerializer(league_fixtures, many=True)
        league_matches = matches_by_league.get(league, [])
        match_serializer = MatchSerializer(league_matches, many=True,context={'request': request})
        
        leagues_data.append({
            'league': league_serializer.data,
            'fixtures': fixture_serializer.data,
            'matches': match_serializer.data
        })

    live_statuses_from_docs = [
        'INPLAY_1ST_HALF', 'HT', 'INPLAY_2ND_HALF', 'BREAK',
        'INPLAY_ET', 'EXTRA_TIME_BREAK', 'INPLAY_PENALTIES', 'PEN_BREAK',
        'SUSPENDED', 'INTERRUPTED'
    ]

    live_fixtures_count = fixtures_for_day.filter(
        state__in=live_statuses_from_docs
    ).count()
    
    live_matches_count = matches_for_day.filter(
        is_live='Yes'
    ).count()

    return {
        'live_count': live_fixtures_count + live_matches_count,
        'leagues': leagues_data
    }



@api_view(['GET'])
def FixturesByDateApiList(request, sport, date, lang):
    """
    High-performance API endpoint for Flutter.
    1. Always serves from cache instantly if data exists.
    2. For today's date, it serves stale cache first, then triggers a non-blocking background refresh.
    """
    if date.lower() == 'today':
        fetch_date = django_timezone.now().date()
    else:
        try:
            fetch_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD or 'today'."},
                            status=status.HTTP_400_BAD_REQUEST)

    try:
        sport_obj = Sport.objects.get(name__iexact=sport)
        fetched_record = FetchedDate.objects.filter(date=fetch_date, sport=sport_obj).first()
        has_fixtures = Fixtures.objects.filter(starting_at__date=fetch_date,sport=sport_obj).exists() if fetched_record else False

        if fetched_record and has_fixtures:
            today = django_timezone.now().date()
            if fetch_date == today:
                time_since_last_fetch = django_timezone.now() - fetched_record.fetched_at
                if time_since_last_fetch > timedelta(minutes=2):
                    thread = threading.Thread(
                        target=_fetch_and_store_fixtures_from_source,
                        args=(sport, fetch_date.strftime('%Y-%m-%d'))
                    )
                    thread.start()

            response_data = _get_serialized_fixtures_for_date(fetch_date, sport_obj, request)
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            success = _fetch_and_store_fixtures_from_source(sport, fetch_date.strftime('%Y-%m-%d'))
            if not success:
                return Response({"error": "Failed to fetch data from the source API."},
                                status=status.HTTP_503_SERVICE_UNAVAILABLE)
            FetchedDate.objects.update_or_create(
                date=fetch_date, sport=sport_obj, defaults={'fetched_at': django_timezone.now()}
            )
            response_data = _get_serialized_fixtures_for_date(fetch_date, sport_obj, request)
            return Response(response_data, status=status.HTTP_200_OK)

    except Sport.DoesNotExist:
        return Response({"error": f"Sport '{sport}' not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred.{e}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def MatchDetailsApi(request, match_id):
    try:
        match = Match.objects.select_related(
            'home_team', 'away_team', 'league', 'season', 'round', 'venues'
        ).get(id=match_id)
        
        goals = MatchGoals.objects.filter(match=match_id)
        best_player_report = MatchPlayerReport.objects.select_related(
            'player', 'team'
        ).filter(
            match=match_id, 
            is_best_player=True
        ).first()

        match_serializer = MatchDetailsSerializer(match, many=False, context={'request': request})
        goals_serializer = MatchGoalsSerializer(goals, many=True, context={'request': request})
        best_player_data = None
        if best_player_report:
            best_player_data = MatchPlayerReportSerializer(
                best_player_report, 
                many=False, 
                context={'request': request}
            ).data

        sport_data = {
            'match': match_serializer.data,
            'goals': goals_serializer.data,
            'best_player': best_player_data
        }
        
        success = True
        message = f"Match details retrieved successfully"
        
        data = {
            'success': success, 
            'data': sport_data, 
            'message': message,
        }
        return JsonResponse(data, safe=False)

    except Match.DoesNotExist:
        success = False
        message = f"Match not found"
        sport_data = {'match': None, 'goals': [], 'best_player': None}
        data = {'success': success, 'data': sport_data, 'message': message}
        return JsonResponse(data, safe=False, status=404)
        
    except Exception as e:
        print(f"Error in MatchDetailsApi: {e}")
        success = False
        message = f"Error retrieving match details"
        sport_data = {'match': None, 'goals': [], 'best_player': None}
        data = {'success': success, 'data': sport_data, 'message': message}
        return JsonResponse(data, safe=False, status=500)

@api_view(['GET'])
def LeagueStandingsApi(request, league_id, season_id):
    """
    Get league standings for a specific league and season
    """
    try:
        print(f"Looking for standings - League: {league_id}, Season: {season_id}")
        
        league_season_table = get_object_or_404(
            LeagueSeasonTable.objects.select_related('league', 'season'),
            league_id=league_id,
            season_id=season_id
        )
        
        standings = TeamSeasonTable.objects.filter(
            table_id=league_season_table.id
        ).select_related('team', 'league').order_by('position')
        
        standings_serializer = TeamSeasonTableSerializer(
            standings, 
            many=True, 
            context={'request': request}
        )
        
        league_data = {
            'league_id': league_season_table.league.id,
            'league_name': league_season_table.league.name,
            'season_id': league_season_table.season.id,
            'season_name': league_season_table.season.name if hasattr(league_season_table.season, 'name') else None,
            'league_season_table_id': league_season_table.id
        }
        
        return Response({
            'success': True,
            'data': {
                'league_info': league_data,
                'standings': standings_serializer.data
            },
            'message': "League standings retrieved successfully"
        })
        
    except LeagueSeasonTable.DoesNotExist:
        return Response({
            'success': False,
            'data': {'standings': []},
            'message': f"League standings not found for league_id {league_id} and season_id {season_id}"
        }, status=404)
        
    except Exception as e:
        print(f"Error retrieving standings: {str(e)}")
        return Response({
            'success': False,
            'data': {'standings': []},
            'message': f"Error retrieving league standings: {str(e)}"
        }, status=500)

@api_view(['GET'])
def LeagueMatchesApi(request, league_id):
    try:
        matches_query = Match.objects.filter(
            league_id=league_id,
            status='Active'
        ).select_related(
            'home_team', 'away_team', 'venues', 'round'
        )
        previous_matches = matches_query.filter(played='Yes').order_by('-start_time')
        
        upcoming_matches = matches_query.filter(played='No').order_by('start_time')
        previous_serializer = MatchDetailsSerializer(previous_matches, many=True, context={'request': request})
        upcoming_serializer = MatchDetailsSerializer(upcoming_matches, many=True, context={'request': request})

        sport_data = {
            'previous_matches': previous_serializer.data,
            'upcoming_matches': upcoming_serializer.data,
        }

        success = True
        message = "League matches retrieved successfully"

        data = {
            'success': success,
            'data': sport_data,
            'message': message,
        }
        
        return JsonResponse(data, safe=False)

    except Exception as e:
        print(f"Error in LeagueMatchesApi: {e}")
        
        success = False
        message = "Error retrieving league matches"
        sport_data = {'previous_matches': [], 'upcoming_matches': []}
        
        data = {
            'success': success,
            'data': sport_data,
            'message': message
        }
        return JsonResponse(data, safe=False, status=500)

@api_view(['GET'])
def TeamMatchesApi(request, team_id):
    try:
        matches_query = Match.objects.filter(
            Q(home_team_id=team_id) | Q(away_team_id=team_id),
            status='Active'
        ).select_related(
            'home_team', 'away_team', 'league', 'round', 'venues'
        )

        previous_matches = matches_query.filter(played='Yes').order_by('-start_time')
        upcoming_matches = matches_query.filter(played='No').order_by('start_time')
        previous_serializer = MatchDetailsSerializer(previous_matches, many=True, context={'request': request})
        upcoming_serializer = MatchDetailsSerializer(upcoming_matches, many=True, context={'request': request})

        sport_data = {
            'previous_matches': previous_serializer.data,
            'upcoming_matches': upcoming_serializer.data,
        }

        success = True
        message = "Team matches retrieved successfully"

        data = {
            'success': success,
            'data': sport_data,
            'message': message,
        }
        
        return JsonResponse(data, safe=False)

    except Exception as e:
        print(f"Error in TeamMatchesApi: {e}")
        
        success = False
        message = "Error retrieving team matches"
        sport_data = {'previous_matches': [], 'upcoming_matches': []}
        
        data = {
            'success': success,
            'data': sport_data,
            'message': message
        }
        return JsonResponse(data, safe=False, status=500)

@api_view(['GET'])
def HeadToHeadApi(request, team1_id, team2_id):
    try:
        matches_query = Match.objects.filter(
            (Q(home_team_id=team1_id) & Q(away_team_id=team2_id)) |
            (Q(home_team_id=team2_id) & Q(away_team_id=team1_id)),
            played='Yes'
        ).select_related('home_team', 'away_team', 'league', 'round', 'venues'
        ).prefetch_related('match_goal').order_by('-start_time')

        team1_wins = 0
        team2_wins = 0
        draws = 0
        team1_total_score = 0 
        team2_total_score = 0 
        team1_total_sets_won = 0
        team2_total_sets_won = 0

        for match in matches_query:
            h_score = match.home_score if match.home_score is not None else 0
            a_score = match.away_score if match.away_score is not None else 0
            if match.home_team_id == team1_id:
                team1_total_score += h_score
                team2_total_score += a_score
                if h_score > a_score: team1_wins += 1
                elif h_score < a_score: team2_wins += 1
                else: draws += 1
            else:
                team1_total_score += a_score
                team2_total_score += h_score
                if a_score > h_score: team1_wins += 1
                elif a_score < h_score: team2_wins += 1
                else: draws += 1
            goals_records = match.match_goal.all()

            for goal_record in goals_records:
                gs_home = goal_record.home_score if goal_record.home_score is not None else 0
                gs_away = goal_record.away_score if goal_record.away_score is not None else 0
                if gs_home == 0 and gs_away == 0:
                    continue
                set_winner = None
                if gs_home > gs_away:
                    set_winner = 'home'
                elif gs_away > gs_home:
                    set_winner = 'away'
                if set_winner == 'home':
                    if match.home_team_id == team1_id:
                        team1_total_sets_won += 1
                    else:
                        team2_total_sets_won += 1
                elif set_winner == 'away':
                    if match.away_team_id == team1_id:
                        team1_total_sets_won += 1
                    else: 
                        team2_total_sets_won += 1
        matches_serializer = MatchDetailsSerializer(matches_query, many=True, context={'request': request})
        stats_data = {
            'total_matches': matches_query.count(),
            'team1_id': team1_id,
            'team1_wins': team1_wins,
            'team1_total_score': team1_total_score,
            'team1_total_sets': team1_total_sets_won,
            'team2_id': team2_id,
            'team2_wins': team2_wins,
            'team2_total_score': team2_total_score,
            'team2_total_sets': team2_total_sets_won,
            'draws': draws,
        }

        sport_data = {
            'stats': stats_data,
            'history_matches': matches_serializer.data,
        }

        return JsonResponse({
            'success': True,
            'data': sport_data,
            'message': "Head-to-head statistics retrieved successfully"
        }, safe=False)

    except Exception as e:
        import traceback
        print(f"Error in HeadToHeadApi: {e}")
        print(traceback.format_exc())
        
        return JsonResponse({
            'success': False, 
            'message': f"Error retrieving data: {str(e)}"
        }, safe=False, status=500)

@api_view(['GET'])
def favorite_team(request, team_id):
    try:
        try:
            team_obj = Teams.objects.get(id=team_id)
        except Teams.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': "Team not found",
                'data': None
            }, status=404)
        team_serializer = SimpleTeamSerializer(team_obj, context={'request': request})
        matches_query = Match.objects.filter(
            Q(home_team_id=team_id) | Q(away_team_id=team_id),
            status='Active'
        ).select_related(
            'home_team', 'away_team', 'league', 'round', 'venues'
        )

        previous_matches = matches_query.filter(played='Yes').order_by('-start_time')[:1]
        upcoming_matches = matches_query.filter(played='No').order_by('start_time')[:1]
        previous_serializer = MatchDetailsSerializer(previous_matches, many=True, context={'request': request})
        upcoming_serializer = MatchDetailsSerializer(upcoming_matches, many=True, context={'request': request})

        sport_data = {
            'team_details': team_serializer.data,
            'previous_matches': previous_serializer.data,
            'upcoming_matches': upcoming_serializer.data,
        }

        success = True
        message = "Favorite team matches retrieved successfully"

        data = {
            'success': success,
            'data': sport_data,
            'message': message,
        }
        
        return JsonResponse(data, safe=False)

    except Exception as e:
        print(f"Error in favorite_team: {e}")
        
        success = False
        message = "Error retrieving favorite team matches"
        sport_data = {'previous_matches': [], 'upcoming_matches': []}
        
        data = {
            'success': success,
            'data': sport_data,
            'message': message
        }
        return JsonResponse(data, safe=False, status=500)

@api_view(['GET'])
def LeagueSeasonsApi(request, league_id):
    try:
        seasons_query = Season.objects.filter(
            league_id=league_id,
            status='Active'
        ).order_by('-starting_at')
        seasons_serializer = SeasonDetailsSerializer(seasons_query, many=True)
        sport_data = {
            'seasons': seasons_serializer.data,
        }
        success = True
        message = "League seasons retrieved successfully"
        data = {
            'success': success,
            'data': sport_data,
            'message': message,
        }
        
        return JsonResponse(data, safe=False)

    except Exception as e:
        print(f"Error in LeagueSeasonsApi: {e}")
        
        success = False
        message = "Error retrieving league seasons"
        sport_data = {'seasons': []}
        
        data = {
            'success': success,
            'data': sport_data,
            'message': message
        }
        return JsonResponse(data, safe=False, status=500)

class FavoriteLeagueToggle(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        league_id = request.data.get('league_id')
        if not league_id:
            return Response({'error': 'League ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            league = Leagues.objects.get(api_id=league_id)
        except Leagues.DoesNotExist:
            return Response({'error': 'League not found.'}, status=status.HTTP_404_NOT_FOUND)
        favorite, created = FavoriteLeague.objects.get_or_create(user=request.user, league=league)
        if not created:
            favorite.delete()
            return Response({'status': 'removed'}, status=status.HTTP_200_OK)
        return Response({'status': 'added'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def SearchGeneralApi(request, name, sport):
    try:
        search_query = name.strip()
        sport_name_filter = sport.strip()
        players_qs = Players.objects.filter(
            name__icontains=search_query,
            sport__name__icontains=sport_name_filter 
        ).select_related('team', 'sport')

        player_data = PlayerSearchSerializer(
            players_qs, 
            many=True, 
            context={'request': request} 
        ).data
        teams_qs = Teams.objects.filter(
            name__icontains=search_query,
            sport__name__icontains=sport_name_filter
        ).select_related('sport')

        team_data = TeamSearchSerializer(
            teams_qs, 
            many=True, 
            context={'request': request}
        ).data
        leagues_qs = Leagues.objects.filter(
            name__icontains=search_query,
            sport__name__icontains=sport_name_filter
        ).select_related('sport')

        league_data = LeagueSearchSerializer(
            leagues_qs, 
            many=True, 
            context={'request': request}
        ).data
        total_results = len(player_data) + len(team_data) + len(league_data)
        success = True
        
        if total_results > 0:
            message = f"Found {total_results} results for '{search_query}' in '{sport_name_filter}'"
        else:
            message = f"No results found for '{search_query}' in '{sport_name_filter}'"

        data = {
            'success': success,
            'message': message,
            'data': {
                'leagues': league_data,
                'teams': team_data,
                'players': player_data,
            }
        }

        return JsonResponse(data, safe=False)

    except Exception as e:
        print(f"Search API Error: {str(e)}")
        
        return JsonResponse({
            'success': False,
            'message': "An error occurred during the search process.",
            'error_details': str(e),
            'data': {}
        }, status=500)

# ... (other code)

@api_view(['GET'])
def FixtureDetailApiView(request, fixture_id, lang):
    """
    Acts as a proxy to fetch live fixture details from SportMonks.
    This ensures the app always gets the most up-to-date information.
    round;group;scores;sport;stage;aggregate;league;season;referees;coaches;venue;state;lineups;events;timeline;trends;statistics;periods;participants;metadata;sidelined;formations;sidelined.sideline.player
    """
    # This is the full include string needed to get all the data for the screen
    include_string = "scores;sport;round;stage;group;league;season;state;coaches;formations;statistics;statistics.type;participants;periods;events.player;events.relatedplayer;lineups.player;lineups.details;metadata;venue;sidelined.sideline.player"

    url = f"{base_url}football/fixtures/{fixture_id}?api_token={api_key}&include={include_string}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        # Initialize variables to find the best player
        best_player = None
        highest_rating = 0.0

        for player in data['data']['lineups']:
            player_details = player.get('details', [])
                
            # Loop through the details to find the player rating 
            for detail in player_details:
                if detail.get('type_id') == 118:
                    try:
                        rating = float(detail['data']['value'])
                        if rating > highest_rating:
                            highest_rating = rating
                            best_player = {
                            "player_id": player.get('player_id'),
                            "team_id": player.get('team_id'),
                            "country_id": player.get('player', {}).get('country_id'),
                            "nationality_id": player.get('player', {}).get('nationality_id'),
                            "position_id": player.get('position_id'),
                            "player_name": player.get('player_name'),
                            "jersey_number": player.get('jersey_number'),
                            "image_path": player.get('player', {}).get('image_path'),
                            "rating": rating
                        }
                    except (ValueError, KeyError):
                        continue
            
        if data.get('data'):
            data['data']['man_of_the_match'] = best_player
            _enrich_fixture_detail_with_name_tr(data['data'])
            if 'starting_at' in data['data'] and isinstance(data['data']['starting_at'], str):
                try:
                    utc_time = datetime.strptime(data['data']['starting_at'], '%Y-%m-%d %H:%M:%S')
                    utc_plus_3_time = utc_time + timedelta(hours=3)
                    data['data']['starting_at'] = utc_plus_3_time.strftime('%Y-%m-%d %H:%M:%S')
                    data['data']['timezone'] = 'UTC+3'
                except ValueError:
                    pass
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch fixture details from source: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _enrich_fixture_detail_with_name_tr(fixture_data):
    """
    Enrich fixture detail data with name_tr and image_path from local database
    Inserts name_tr immediately after name field for better readability
    Overrides image_path with local database value if available
    """
    if fixture_data.get('league'):
        league_api_id = fixture_data['league'].get('id')
        name_tr_value = None
        image_path_value = None
        if league_api_id:
            try:
                league = Leagues.objects.filter(api_id=league_api_id).values('name_tr', 'image_path').first()
                if league:
                    name_tr_value = league['name_tr']
                    image_path_value = league['image_path']
            except Exception:
                pass
        _insert_after_key(fixture_data['league'], 'name', 'name_tr', name_tr_value)
        if image_path_value:
            fixture_data['league']['image_path'] = image_path_value

    if fixture_data.get('participants'):
        team_ids = [p.get('id') for p in fixture_data['participants'] if p.get('id')]
        teams_dict = {}
        if team_ids:
            teams = Teams.objects.filter(api_id__in=team_ids).values('api_id', 'name_tr', 'image_path')
            teams_dict = {t['api_id']: {'name_tr': t['name_tr'], 'image_path': t['image_path']} for t in teams}

        for participant in fixture_data['participants']:
            participant_id = participant.get('id')
            team_data = teams_dict.get(participant_id) if participant_id else None
            name_tr_value = team_data['name_tr'] if team_data else None
            image_path_value = team_data['image_path'] if team_data else None
            _insert_after_key(participant, 'name', 'name_tr', name_tr_value)
            if image_path_value:
                participant['image_path'] = image_path_value

    if fixture_data.get('events'):
        player_ids = set()
        for event in fixture_data['events']:
            if event.get('player_id'):
                player_ids.add(event['player_id'])
            if event.get('related_player_id'):
                player_ids.add(event['related_player_id'])

        players_dict = {}
        if player_ids:
            players = Players.objects.filter(api_id__in=player_ids).values('api_id', 'name_tr', 'image_path')
            players_dict = {p['api_id']: {'name_tr': p['name_tr'], 'image_path': p['image_path']} for p in players}

        for event in fixture_data['events']:
            if event.get('player'):
                player_id = event['player'].get('id')
                player_data = players_dict.get(player_id) if player_id else None
                name_tr_value = player_data['name_tr'] if player_data else None
                image_path_value = player_data['image_path'] if player_data else None
                if 'display_name' in event['player']:
                    _insert_after_key(event['player'], 'display_name', 'name_tr', name_tr_value)
                elif 'name' in event['player']:
                    _insert_after_key(event['player'], 'name', 'name_tr', name_tr_value)
                if image_path_value:
                    event['player']['image_path'] = image_path_value

            if event.get('relatedplayer'):
                related_player_id = event['relatedplayer'].get('id')
                player_data = players_dict.get(related_player_id) if related_player_id else None
                name_tr_value = player_data['name_tr'] if player_data else None
                image_path_value = player_data['image_path'] if player_data else None
                if 'display_name' in event['relatedplayer']:
                    _insert_after_key(event['relatedplayer'], 'display_name', 'name_tr', name_tr_value)
                elif 'name' in event['relatedplayer']:
                    _insert_after_key(event['relatedplayer'], 'name', 'name_tr', name_tr_value)
                if image_path_value:
                    event['relatedplayer']['image_path'] = image_path_value

    if fixture_data.get('lineups'):
        lineup_player_ids = [l.get('player_id') for l in fixture_data['lineups'] if l.get('player_id')]
        lineup_players_dict = {}
        if lineup_player_ids:
            players = Players.objects.filter(api_id__in=lineup_player_ids).values('api_id', 'name_tr', 'image_path')
            lineup_players_dict = {p['api_id']: {'name_tr': p['name_tr'], 'image_path': p['image_path']} for p in players}

        for lineup in fixture_data['lineups']:
            if lineup.get('player'):
                player_id = lineup['player'].get('id')
                player_data = lineup_players_dict.get(player_id) if player_id else None
                name_tr_value = player_data['name_tr'] if player_data else None
                image_path_value = player_data['image_path'] if player_data else None
                if 'display_name' in lineup['player']:
                    _insert_after_key(lineup['player'], 'display_name', 'name_tr', name_tr_value)
                elif 'name' in lineup['player']:
                    _insert_after_key(lineup['player'], 'name', 'name_tr', name_tr_value)
                if image_path_value:
                    lineup['player']['image_path'] = image_path_value

    if fixture_data.get('man_of_the_match'):
        motm_player_id = fixture_data['man_of_the_match'].get('player_id')
        name_tr_value = None
        image_path_value = None
        if motm_player_id:
            try:
                player = Players.objects.filter(api_id=motm_player_id).values('name_tr', 'image_path').first()
                if player:
                    name_tr_value = player['name_tr']
                    image_path_value = player['image_path']
            except Exception:
                pass
        _insert_after_key(fixture_data['man_of_the_match'], 'player_name', 'player_name_tr', name_tr_value)
        if image_path_value:
            fixture_data['man_of_the_match']['image_path'] = image_path_value

def _insert_after_key(data_dict, after_key, new_key, new_value):
    """
    Insert a new key-value pair immediately after a specified key in a dictionary.
    Preserves the order of other keys.
    """
    if after_key not in data_dict:
        data_dict[new_key] = new_value
        return

    items = list(data_dict.items())
    new_items = []
    
    for key, value in items:
        new_items.append((key, value))
        if key == after_key:
            new_items.append((new_key, new_value))
    data_dict.clear()
    data_dict.update(new_items)

def _enrich_standings_data(standings_data):
    """
    Enrich standings data with name_tr and image_path from local database.
    Works with LiveStandingsByLeagueApiView and standingsByseasonsApiView responses.
    """
    if not standings_data or 'data' not in standings_data:
        return
    
    data_list = standings_data['data']
    if not isinstance(data_list, list):
        return
    
    # Collect all team and league IDs
    team_ids = set()
    league_ids = set()
    
    for item in data_list:
        if item.get('participant') and item['participant'].get('id'):
            team_ids.add(item['participant']['id'])
        if item.get('league') and item['league'].get('id'):
            league_ids.add(item['league']['id'])
    
    # Fetch teams from local database
    teams_dict = {}
    if team_ids:
        teams = Teams.objects.filter(api_id__in=team_ids).values('api_id', 'name_tr', 'image_path')
        teams_dict = {t['api_id']: {'name_tr': t['name_tr'], 'image_path': t['image_path']} for t in teams}
    
    # Fetch leagues from local database
    leagues_dict = {}
    if league_ids:
        leagues = Leagues.objects.filter(api_id__in=league_ids).values('api_id', 'name_tr', 'image_path')
        leagues_dict = {l['api_id']: {'name_tr': l['name_tr'], 'image_path': l['image_path']} for l in leagues}
    
    # Enrich each standing
    for item in data_list:
        if item.get('participant'):
            team_id = item['participant'].get('id')
            team_data = teams_dict.get(team_id) if team_id else None
            if team_data:
                _insert_after_key(item['participant'], 'name', 'name_tr', team_data['name_tr'])
                if team_data['image_path']:
                    item['participant']['image_path'] = team_data['image_path']
        
        if item.get('league'):
            league_id = item['league'].get('id')
            league_data = leagues_dict.get(league_id) if league_id else None
            if league_data:
                _insert_after_key(item['league'], 'name', 'name_tr', league_data['name_tr'])
                if league_data['image_path']:
                    item['league']['image_path'] = league_data['image_path']

def _enrich_topscorers_data(topscorers_data):
    """
    Enrich top scorers/assists data with name_tr and image_path from local database.
    """
    if not topscorers_data or 'data' not in topscorers_data:
        return
    
    data_list = topscorers_data['data']
    if not isinstance(data_list, list):
        return
    
    # Collect all player and team IDs
    player_ids = set()
    team_ids = set()
    
    for item in data_list:
        if item.get('player') and item['player'].get('id'):
            player_ids.add(item['player']['id'])
        if item.get('participant') and item['participant'].get('id'):
            team_ids.add(item['participant']['id'])
    
    # Fetch players from local database
    players_dict = {}
    if player_ids:
        players = Players.objects.filter(api_id__in=player_ids).values('api_id', 'name_tr', 'image_path')
        players_dict = {p['api_id']: {'name_tr': p['name_tr'], 'image_path': p['image_path']} for p in players}
    
    # Fetch teams from local database
    teams_dict = {}
    if team_ids:
        teams = Teams.objects.filter(api_id__in=team_ids).values('api_id', 'name_tr', 'image_path')
        teams_dict = {t['api_id']: {'name_tr': t['name_tr'], 'image_path': t['image_path']} for t in teams}
    
    # Enrich each top scorer
    for item in data_list:
        if item.get('player'):
            player_id = item['player'].get('id')
            player_data = players_dict.get(player_id) if player_id else None
            if player_data:
                if 'display_name' in item['player']:
                    _insert_after_key(item['player'], 'display_name', 'name_tr', player_data['name_tr'])
                elif 'name' in item['player']:
                    _insert_after_key(item['player'], 'name', 'name_tr', player_data['name_tr'])
                if player_data['image_path']:
                    item['player']['image_path'] = player_data['image_path']
        
        if item.get('participant'):
            team_id = item['participant'].get('id')
            team_data = teams_dict.get(team_id) if team_id else None
            if team_data:
                _insert_after_key(item['participant'], 'name', 'name_tr', team_data['name_tr'])
                if team_data['image_path']:
                    item['participant']['image_path'] = team_data['image_path']

def _enrich_fixtures_list_data(fixtures_list):
    """
    Enrich a list of fixtures with name_tr and image_path from local database.
    Used by PreviousMatchesApiView and similar endpoints.
    """
    if not fixtures_list or not isinstance(fixtures_list, list):
        return
    
    # Collect all league IDs
    league_ids = set()
    for fixture in fixtures_list:
        if fixture.get('league') and fixture['league'].get('id'):
            league_ids.add(fixture['league']['id'])
    
    # Fetch leagues from local database
    leagues_dict = {}
    if league_ids:
        leagues = Leagues.objects.filter(api_id__in=league_ids).values('api_id', 'name_tr', 'image_path')
        leagues_dict = {l['api_id']: {'name_tr': l['name_tr'], 'image_path': l['image_path']} for l in leagues}
    
    # Enrich each fixture
    for fixture in fixtures_list:
        if fixture.get('league'):
            league_id = fixture['league'].get('id')
            league_data = leagues_dict.get(league_id) if league_id else None
            if league_data:
                _insert_after_key(fixture['league'], 'name', 'name_tr', league_data['name_tr'])
                if league_data['image_path']:
                    fixture['league']['image_path'] = league_data['image_path']

def _enrich_search_results(search_data, entity_type='team'):
    """
    Enrich search results with name_tr and image_path from local database.
    entity_type can be 'team', 'league', or 'player'
    """
    if not search_data or 'data' not in search_data:
        return
    
    data_list = search_data['data']
    if not isinstance(data_list, list):
        return
    
    # Collect all IDs
    entity_ids = set()
    for item in data_list:
        if item.get('id'):
            entity_ids.add(item['id'])
    
    if not entity_ids:
        return
    
    # Fetch from local database based on entity type
    entities_dict = {}
    if entity_type == 'team':
        entities = Teams.objects.filter(api_id__in=entity_ids).values('api_id', 'name_tr', 'image_path')
        entities_dict = {e['api_id']: {'name_tr': e['name_tr'], 'image_path': e['image_path']} for e in entities}
    elif entity_type == 'league':
        entities = Leagues.objects.filter(api_id__in=entity_ids).values('api_id', 'name_tr', 'image_path')
        entities_dict = {e['api_id']: {'name_tr': e['name_tr'], 'image_path': e['image_path']} for e in entities}
    elif entity_type == 'player':
        entities = Players.objects.filter(api_id__in=entity_ids).values('api_id', 'name_tr', 'image_path')
        entities_dict = {e['api_id']: {'name_tr': e['name_tr'], 'image_path': e['image_path']} for e in entities}
    
    # Enrich each result
    for item in data_list:
        entity_id = item.get('id')
        entity_data = entities_dict.get(entity_id) if entity_id else None
        if entity_data:
            if 'display_name' in item:
                _insert_after_key(item, 'display_name', 'name_tr', entity_data['name_tr'])
            elif 'name' in item:
                _insert_after_key(item, 'name', 'name_tr', entity_data['name_tr'])
            if entity_data['image_path']:
                item['image_path'] = entity_data['image_path']

def _enrich_league_data(league_data):
    """
    Enrich league data with name_tr and image_path from local database.
    """
    if not league_data or 'data' not in league_data:
        return
    
    data = league_data['data']
    if not isinstance(data, dict):
        return
    
    league_id = data.get('id')
    if league_id:
        try:
            league = Leagues.objects.filter(api_id=league_id).values('name_tr', 'image_path').first()
            if league:
                _insert_after_key(data, 'name', 'name_tr', league['name_tr'])
                if league['image_path']:
                    data['image_path'] = league['image_path']
        except Exception:
            pass
    
    # Enrich seasons if present
    if data.get('seasons') and isinstance(data['seasons'], list):
        for season in data['seasons']:
            if season.get('league') and season['league'].get('id'):
                league_id = season['league']['id']
                try:
                    league = Leagues.objects.filter(api_id=league_id).values('name_tr', 'image_path').first()
                    if league:
                        _insert_after_key(season['league'], 'name', 'name_tr', league['name_tr'])
                        if league['image_path']:
                            season['league']['image_path'] = league['image_path']
                except Exception:
                    pass

def _enrich_squads_data(squads_data):
    """
    Enrich squads data with name_tr and image_path from local database.
    """
    if not squads_data or 'data' not in squads_data:
        return
    
    data_list = squads_data['data']
    if not isinstance(data_list, list):
        return
    
    # Collect all player IDs
    player_ids = set()
    for item in data_list:
        if item.get('player') and item['player'].get('id'):
            player_ids.add(item['player']['id'])
    
    # Fetch players from local database
    players_dict = {}
    if player_ids:
        players = Players.objects.filter(api_id__in=player_ids).values('api_id', 'name_tr', 'image_path')
        players_dict = {p['api_id']: {'name_tr': p['name_tr'], 'image_path': p['image_path']} for p in players}
    
    # Enrich each squad member
    for item in data_list:
        if item.get('player'):
            player_id = item['player'].get('id')
            player_data = players_dict.get(player_id) if player_id else None
            if player_data:
                if 'display_name' in item['player']:
                    _insert_after_key(item['player'], 'display_name', 'name_tr', player_data['name_tr'])
                elif 'name' in item['player']:
                    _insert_after_key(item['player'], 'name', 'name_tr', player_data['name_tr'])
                if player_data['image_path']:
                    item['player']['image_path'] = player_data['image_path']

def _enrich_season_data(season_data):
    """
    Enrich season data with name_tr and image_path from local database.
    """
    if not season_data or 'data' not in season_data:
        return
    
    data = season_data['data']
    if not isinstance(data, dict):
        return
    
    # Enrich league if present
    if data.get('league') and data['league'].get('id'):
        league_id = data['league']['id']
        try:
            league = Leagues.objects.filter(api_id=league_id).values('name_tr', 'image_path').first()
            if league:
                _insert_after_key(data['league'], 'name', 'name_tr', league['name_tr'])
                if league['image_path']:
                    data['league']['image_path'] = league['image_path']
        except Exception:
            pass

######################### team Screen api urls #########################
@api_view(['GET'])
def TeamScreenApiView(request, sport, lang):
    try:
        now = django_timezone.now()
        active_window_start = now - timedelta(days=30)
        active_window_end = now + timedelta(days=30)
        target_team_ids = set(FixtureParticipant.objects.filter(
            fixture__starting_at__range=(active_window_start, active_window_end)
        ).values_list('team__api_id', flat=True))

        if not target_team_ids:
            teams = Teams.objects.all().order_by('name')[:20]
            target_team_ids = set(teams.values_list('api_id', flat=True))
        else:
            teams = Teams.objects.filter(api_id__in=target_team_ids).order_by('name')

        upcoming_fixtures_map = defaultdict(list)
        previous_fixtures_map = defaultdict(list)

        previous_fixtures_qs = Fixtures.objects.filter(
            participants__team__api_id__in=target_team_ids,
            starting_at__lt=now
        ).order_by('-starting_at').prefetch_related('participants__team')

        upcoming_fixtures_qs = Fixtures.objects.filter(
            participants__team__api_id__in=target_team_ids,
            starting_at__gte=now
        ).order_by('starting_at').prefetch_related('participants__team')

        temp_previous_map = {}
        for fixture in previous_fixtures_qs:
            for participant in fixture.participants.all():
                team_id = participant.team.api_id
                if team_id in target_team_ids and team_id not in temp_previous_map:
                    previous_fixtures_map[team_id] = [fixture]
                    temp_previous_map[team_id] = True
            if len(temp_previous_map) == len(target_team_ids):
                break

        temp_upcoming_map = {}
        for fixture in upcoming_fixtures_qs:
            for participant in fixture.participants.all():
                team_id = participant.team.api_id
                if team_id in target_team_ids and team_id not in temp_upcoming_map:
                    upcoming_fixtures_map[team_id] = [fixture]
                    temp_upcoming_map[team_id] = True
            if len(temp_upcoming_map) == len(target_team_ids):
                break

        serializer_context = {
            'upcoming_fixtures': upcoming_fixtures_map,
            'previous_fixtures': previous_fixtures_map,
        }
        serializer = TeamWithMatchesSerializer(teams, many=True, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def TeamDetailApiView(request, team_id, lang):
    include_string = "coaches;coaches.coach;players;players.player;players.player.nationality;latest;latest.league;latest.scores;latest.participants;upcoming;upcoming.league;upcoming.participants;activeSeasons;activeseasons.league;country;venue;"

    url = f"{base_url}football/teams/{team_id}?api_token={api_key}&include={include_string}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('data'):
            _enrich_team_detail_with_name_tr(data['data'])
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch team details from source: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _enrich_team_detail_with_name_tr(team_data):
    """
    Enrich team detail data with name_tr and image_path from local database
    Inserts name_tr immediately after name field for better readability
    Overrides image_path with local database value if available
    """
    team_api_id = team_data.get('id')
    team_name_tr = None
    team_image_path = None
    if team_api_id:
        try:
            team = Teams.objects.filter(api_id=team_api_id).values('name_tr', 'image_path').first()
            if team:
                team_name_tr = team['name_tr']
                team_image_path = team['image_path']
        except Exception:
            pass
    _insert_after_key(team_data, 'name', 'name_tr', team_name_tr)
    if team_image_path:
        team_data['image_path'] = team_image_path
    
    if team_data.get('players'):
        player_ids = [p['player'].get('id') for p in team_data['players'] if p.get('player') and p['player'].get('id')]
        players_dict = {}
        if player_ids:
            players = Players.objects.filter(api_id__in=player_ids).values('api_id', 'name_tr', 'image_path')
            players_dict = {p['api_id']: {'name_tr': p['name_tr'], 'image_path': p['image_path']} for p in players}

        for squad_player in team_data['players']:
            if squad_player.get('player'):
                player_id = squad_player['player'].get('id')
                player_data = players_dict.get(player_id) if player_id else None
                name_tr_value = player_data['name_tr'] if player_data else None
                image_path_value = player_data['image_path'] if player_data else None
                if 'display_name' in squad_player['player']:
                    _insert_after_key(squad_player['player'], 'display_name', 'name_tr', name_tr_value)
                elif 'name' in squad_player['player']:
                    _insert_after_key(squad_player['player'], 'name', 'name_tr', name_tr_value)
                if image_path_value:
                    squad_player['player']['image_path'] = image_path_value
    
    if team_data.get('latest'):
        for match in team_data['latest']:
            if match.get('league'):
                league_api_id = match['league'].get('id')
                league_name_tr = None
                league_image_path = None
                if league_api_id:
                    try:
                        league = Leagues.objects.filter(api_id=league_api_id).values('name_tr', 'image_path').first()
                        if league:
                            league_name_tr = league['name_tr']
                            league_image_path = league['image_path']
                    except Exception:
                        pass
                _insert_after_key(match['league'], 'name', 'name_tr', league_name_tr)
                if league_image_path:
                    match['league']['image_path'] = league_image_path

            if match.get('participants'):
                participant_ids = [p.get('id') for p in match['participants'] if p.get('id')]
                teams_dict = {}
                if participant_ids:
                    teams = Teams.objects.filter(api_id__in=participant_ids).values('api_id', 'name_tr', 'image_path')
                    teams_dict = {t['api_id']: {'name_tr': t['name_tr'], 'image_path': t['image_path']} for t in teams}

                for participant in match['participants']:
                    participant_id = participant.get('id')
                    team_data_local = teams_dict.get(participant_id) if participant_id else None
                    name_tr_value = team_data_local['name_tr'] if team_data_local else None
                    image_path_value = team_data_local['image_path'] if team_data_local else None
                    _insert_after_key(participant, 'name', 'name_tr', name_tr_value)
                    if image_path_value:
                        participant['image_path'] = image_path_value

    if team_data.get('upcoming'):
        for match in team_data['upcoming']:
            if match.get('league'):
                league_api_id = match['league'].get('id')
                league_name_tr = None
                league_image_path = None
                if league_api_id:
                    try:
                        league = Leagues.objects.filter(api_id=league_api_id).values('name_tr', 'image_path').first()
                        if league:
                            league_name_tr = league['name_tr']
                            league_image_path = league['image_path']
                    except Exception:
                        pass
                _insert_after_key(match['league'], 'name', 'name_tr', league_name_tr)
                if league_image_path:
                    match['league']['image_path'] = league_image_path

            if match.get('participants'):
                participant_ids = [p.get('id') for p in match['participants'] if p.get('id')]
                teams_dict = {}
                if participant_ids:
                    teams = Teams.objects.filter(api_id__in=participant_ids).values('api_id', 'name_tr', 'image_path')
                    teams_dict = {t['api_id']: {'name_tr': t['name_tr'], 'image_path': t['image_path']} for t in teams}

                for participant in match['participants']:
                    participant_id = participant.get('id')
                    team_data_local = teams_dict.get(participant_id) if participant_id else None
                    name_tr_value = team_data_local['name_tr'] if team_data_local else None
                    image_path_value = team_data_local['image_path'] if team_data_local else None
                    _insert_after_key(participant, 'name', 'name_tr', name_tr_value)
                    if image_path_value:
                        participant['image_path'] = image_path_value
    
    if team_data.get('activeseasons'):
        league_ids = [s['league'].get('id') for s in team_data['activeseasons'] if s.get('league') and s['league'].get('id')]
        leagues_dict = {}
        if league_ids:
            leagues = Leagues.objects.filter(api_id__in=league_ids).values('api_id', 'name_tr', 'image_path')
            leagues_dict = {l['api_id']: {'name_tr': l['name_tr'], 'image_path': l['image_path']} for l in leagues}

        for season in team_data['activeseasons']:
            if season.get('league'):
                league_id = season['league'].get('id')
                league_data = leagues_dict.get(league_id) if league_id else None
                name_tr_value = league_data['name_tr'] if league_data else None
                image_path_value = league_data['image_path'] if league_data else None
                _insert_after_key(season['league'], 'name', 'name_tr', name_tr_value)
                if image_path_value:
                    season['league']['image_path'] = image_path_value


@api_view(['GET'])
def TopTeamsApiView(request):
    """
    Fetch details for top teams (specified by IDs)
    """
    TOP_TEAM_IDS = [8, 9 , 6, 14, 19 ,18 , 3468, 83, 134474, 503, 68, 591, 44, 597, 37, 113 ,2930 , 625, 2506, 476, 7011]  
    top_teams_data = []
    
    try:
        for team_id in TOP_TEAM_IDS:
            url = f"{base_url}football/teams/{team_id}?api_token={api_key}"
            
            response = requests.get(url)
            response.raise_for_status()

            team_response = response.json()
            
            if 'data' in team_response and isinstance(team_response['data'], dict):
                # Enrich team data with name_tr and image_path from local database
                _enrich_team_detail_with_name_tr(team_response['data'])
                team_data = {
                    "data": team_response['data']
                }
                top_teams_data.append(team_data)
        
        return Response({
            "data": top_teams_data
        }, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch team details from source: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################ Leagues API Endpoints ################

@api_view(['GET'])
def LeaguesApiView(request, sport, lang):
    try:
        sport_obj = Sport.objects.get(name__iexact=sport)
        leagues = Leagues.objects.filter(sport=sport_obj).order_by('name')
        serializer = LeagueSerializer(leagues, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Sport.DoesNotExist:
        return Response({"error": f"Sport '{sport}' not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def LeagueDetailApiView(request, league_id, lang):
    try:
        league = Leagues.objects.get(api_id=league_id)
        fixturess = Fixtures.objects.filter(league=league).order_by('-starting_at')
        current_season = league.currentseason
        fixtures_serializer = FixtureSerializer(fixturess, many=True)
        response_data = {
            'api_id': league.api_id,
            'name': league.name,
            'image_path': league.image_path,
            'country': league.country,
            'current_season_id': current_season if current_season else None,
            'fixtures': fixtures_serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except Leagues.DoesNotExist:
        return Response({"error": "League not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- NEW VIEW FOR LIVE STANDINGS ---
@api_view(['GET'])
def LiveStandingsByLeagueApiView(request, league_id, lang='en'):
    """
    Acts as a proxy to fetch live standings for a league from SportMonks.
    """
    include_params = request.query_params.get('include', 'participant;rule.type;details.type;form;stage;league;group',)
    url = f"{base_url}football/standings/live/leagues/{league_id}?api_token={api_key}&include={include_params}&locale={lang}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        _enrich_standings_data(data)
        return Response(data, status=status.HTTP_200_OK)
    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch standings from source: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- CORRECTED VIEW FOR TOP SCORERS ---
@api_view(['GET'])
def TopScorersBySeasonApiView(request, season_id, lang='en'):
    """
    Acts as a proxy to fetch top scorers for a season from SportMonks.
    This version correctly constructs the URL with multiple separate 'filters' parameters.
    """
    try:
        # Start with the base URL and API token
        url = f"{base_url}football/topscorers/seasons/{season_id}?api_token={api_key}&locale={lang}"

        # Append the 'include' parameter
        include_param = request.query_params.get('include', 'player;player.nationality;player.position;participant;type;&filters=seasonTopscorerTypes:208')
        url += f"&include={include_param.replace(',', ';')}"

        # Manually append each filter as a separate parameter
        for key, value in request.query_params.items():
            if key.startswith('filters['):
                # Example key: 'filters[fixtureLeagues]'
                filter_key = key.split('[')[1].split(']')[0]
                url += f"&filters={filter_key}:{value}"
        toppscorer = []
        for key, value in request.query_params.items():
            if key == 'topscorer':
                toppscorer.append(value)
        if toppscorer:
            url += f"&topscorer={','.join(toppscorer)}"
            palyer = Players.objects.filter(api_id__in=toppscorer).values_list('api_id', flat=True)
            if len(palyer) != len(toppscorer):
                return Response({"error": "One or more player IDs are invalid."}, status=status.HTTP_400_BAD_REQUEST)
            player_serializer = PlyerSerializer(Players.objects.filter(api_id__in=toppscorer), many=True)
            # You can include player_serializer.data in the final response if needed
        # Make the request with the fully constructed URL
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        _enrich_topscorers_data(data)
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch top scorers from source: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# --- NEW VIEW FOR TOP ASSISTS ---
@api_view(['GET'])
def TopAssistsBySeasonApiView(request, season_id, lang='en'):
    """
    Acts as a proxy to fetch top scorers for a season from SportMonks.
    This version correctly constructs the URL with multiple separate 'filters' parameters.
    """
    try:
        # Start with the base URL and API token
        url = f"{base_url}football/topscorers/seasons/{season_id}?api_token={api_key}&locale={lang}"

        # Append the 'include' parameter
        include_param = request.query_params.get('include', 'player;player.nationality;player.position;participant;type;&filters=seasonTopscorerTypes:209')
        url += f"&include={include_param.replace(',', ';')}"

        # Manually append each filter as a separate parameter
        for key, value in request.query_params.items():
            if key.startswith('filters['):
                # Example key: 'filters[fixtureLeagues]'
                filter_key = key.split('[')[1].split(']')[0]
                url += f"&filters={filter_key}:{value}"

        # Make the request with the fully constructed URL
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        _enrich_topscorers_data(data)
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch top scorers from source: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# --- NEW VIEW FOR HEAD-TO-HEAD PREVIOUS MATCHES (CURRENT SCORES ONLY) ---
@api_view(['GET'])
def PreviousMatchesApiView(request, team1_id, team2_id, lang='en'):
    """
    Fetch previous matches between two teams (head-to-head) from SportMonks,
    including only scores with description = 'CURRENT' and league details.
    """
    try:
        url = f"{base_url}football/fixtures/head-to-head/{team1_id}/{team2_id}?api_token={api_key}&include=scores;league&locale={lang}"

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        fixtures = data.get("data", [])

        filtered_fixtures = []
        for fixture in fixtures:
            # Filter only scores with description == "CURRENT"
            scores = fixture.get("scores", [])
            current_scores = [s for s in scores if s.get("description") == "CURRENT"]

            league = fixture.get("league")

            # Rebuild fixture with filtered scores and league
            filtered_fixture = {
                "id": fixture.get("id"),
                "sport_id": fixture.get("sport_id"),
                "league_id": fixture.get("league_id"),
                "season_id": fixture.get("season_id"),
                "stage_id": fixture.get("stage_id"),
                "group_id": fixture.get("group_id"),
                "aggregate_id": fixture.get("aggregate_id"),
                "round_id": fixture.get("round_id"),
                "state_id": fixture.get("state_id"),
                "venue_id": fixture.get("venue_id"),
                "name": fixture.get("name"),
                "starting_at": fixture.get("starting_at"),
                "result_info": fixture.get("result_info"),
                "leg": fixture.get("leg"),
                "details": fixture.get("details"),
                "length": fixture.get("length"),
                "placeholder": fixture.get("placeholder"),
                "has_odds": fixture.get("has_odds"),
                "has_premium_odds": fixture.get("has_premium_odds"),
                "starting_at_timestamp": fixture.get("starting_at_timestamp"),
                "league": league,
                "scores": current_scores,
            }
            filtered_fixtures.append(filtered_fixture)

        _enrich_fixtures_list_data(filtered_fixtures)
        return Response(filtered_fixtures, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch previous matches: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response(
            {"error": f"Unexpected error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def TeamLatestUpcomingApiView(request, team_id, lang='en'):
    """
    Fetch a single team's latest match (with only CURRENT scores) and first upcoming match.
    """
    try:
        url = f"{base_url}football/teams/{team_id}?api_token={api_key}&include=latest;latest.participants;latest.league;latest.scores;upcoming;upcoming.league;upcoming.participants&locale={lang}"

        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("data", {})

        # --- Filter latest: take only the most recent one ---
        latest_matches = data.get("latest", [])
        latest_match = latest_matches[0] if latest_matches else None

        if latest_match:
            # keep only scores with description == CURRENT
            scores = latest_match.get("scores", [])
            current_scores = [s for s in scores if s.get("description") == "CURRENT"]
            latest_match["scores"] = current_scores
            data["latest"] = [latest_match]
        else:
            data["latest"] = []

        # --- Filter upcoming: take only the nearest one ---
        upcoming_matches = data.get("upcoming", [])
        upcoming_match = upcoming_matches[0] if upcoming_matches else None
        data["upcoming"] = [upcoming_match] if upcoming_match else []

        # Enrich with local database data
        _enrich_team_detail_with_name_tr(data)
        return Response({"data": data}, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch team data: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response(
            {"error": f"Unexpected error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def standingsByseasonsApiView(request, season_id, lang='en'):
    """
    Acts as a proxy to fetch season details from SportMonks.
    Includes fixtures, teams, sport, league, stages, groups, statistics, etc.
    """
    try:
        # Start with the base URL and API token
        url = f"{base_url}football/standings/seasons/{season_id}?api_token={api_key}&locale={lang}"

        # Handle include parameters
        include_param = request.query_params.get('include', 'participant;rule.type;details.type;form;stage;league;group')
        url += f"&include={include_param.replace(',', ';')}"

        # Handle additional query parameters
        query_params = request.query_params.copy()
        
        # Remove 'include' since we already handled it
        query_params.pop('include', None)
        
        # Add other query parameters to the URL
        for key, value in query_params.items():
            if 'filters[' in key:
                # Handle filter parameters (e.g., filters[league_id]=123)
                filter_key = key.split('[')[1].split(']')[0]
                url += f"&filters={filter_key}:{value}"
            else:
                # Handle regular parameters
                url += f"&{key}={value}"

        # Make the request with the fully constructed URL
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        _enrich_standings_data(data)
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        error_msg = f"Failed to fetch season data from source: {err.response.status_code} {err.response.reason}"
        if err.response.status_code == 404:
            error_msg = f"Season with ID {season_id} not found"
        return Response({"error": error_msg}, status=err.response.status_code)
    
    except requests.exceptions.RequestException as err:
        return Response({"error": f"Network error occurred: {str(err)}"}, 
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def LeagueInformationApiView(request, league_id, lang='en'):
    """
    Acts as a proxy to fetch league details (seasons, latest, upcoming, currentSeason, stages)
    from SportMonks API for the given league_id.
    """
    try:
        url = f"{base_url}football/leagues/{league_id}?api_token={api_key}&locale={lang}"

        include_param = request.query_params.get("include","seasons;currentSeason;stages;")
        url += f"&include={include_param.replace(',', ';')}"

        for key, value in request.query_params.items():
            if key.startswith("filters["):
                filter_key = key.split("[")[1].split("]")[0]
                url += f"&filters={filter_key}:{value}"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        _enrich_league_data(data)
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch league details: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code)
    except Exception as e:
        return Response(
            {"error": f"Unexpected error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def SeasonSchedulesApiView(request, season_id, lang='en'):
    """
    Proxy to fetch schedules for a given season from SportMonks API.
    Supports dynamic 'include' and 'filters'.
    """
    try:
        url = f"{base_url}football/schedules/seasons/{season_id}?api_token={api_key}&locale={lang}"

        include_param = request.query_params.get("include", "")
        if include_param:
            url += f"&include={include_param.replace(',', ';')}"

        for key, value in request.query_params.items():
            if key.startswith("filters["):
                filter_key = key.split("[")[1].split("]")[0]
                url += f"&filters={filter_key}:{value}"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        _enrich_season_data(data)
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch schedules: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response(
            {"error": f"Unexpected error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@api_view(['GET'])
def LeagueSearchApiView(request, name,lang='en'):
    """
    Proxy endpoint to search leagues by name using SportMonks API.
    Example: /v4/football/leagues/search/Premier/
    """
    try:
        # Base URL for searching leagues
        url = f"{base_url}football/leagues/search/{name}?api_token={api_key}&locale={lang}"

        # Append the include param (default currentseason)
        include_param = request.query_params.get('include', 'currentSeason')
        url += f"&include={include_param.replace(',', ';')}"

        # Forward extra query parameters (filters, pagination, etc.)
        for key, value in request.query_params.items():
            if key not in ["include"]:
                url += f"&{key}={value}"

        # Make request
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        _enrich_search_results(data, entity_type='league')
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch leagues: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def TeamSearchApiView(request, name,lang='en'):
    """
    Proxy endpoint to search teams by name using SportMonks API.
    Example: /v4/football/teams/search/man/
    """
    try:
        # Base URL for searching teams
        url = f"{base_url}football/teams/search/{name}?api_token={api_key}&locale={lang}"

        # Append the include param (default none, but user can pass their own)
        include_param = request.query_params.get('include', '')
        if include_param:
            url += f"&include={include_param.replace(',', ';')}"

        # Forward extra query parameters (pagination, filters, etc.)
        for key, value in request.query_params.items():
            if key not in ["include"]:
                url += f"&{key}={value}"

        # Make request to SportMonks
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        _enrich_search_results(data, entity_type='team')
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch teams: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response(
            {"error": f"Unexpected error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def PlayerSearchApiView(request, name,lang='en'):
    """
    Proxy endpoint to search teams by name using SportMonks API.
    Example: /v4/football/teams/search/man/
    """
    try:
        # Base URL for searching teams
        url = f"{base_url}football/teams/search/{name}?api_token={api_key}&locale={lang}"

        # Append the include param (default none, but user can pass their own)
        include_param = request.query_params.get('include', '')
        if include_param:
            url += f"&include={include_param.replace(',', ';')}"

        # Forward extra query parameters (pagination, filters, etc.)
        for key, value in request.query_params.items():
            if key not in ["include"]:
                url += f"&{key}={value}"

        # Make request to SportMonks
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        _enrich_search_results(data, entity_type='player')
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch teams: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response(
            {"error": f"Unexpected error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

################## Player Detail API Endpoint ##################
@api_view(['GET'])
def PlayerDetailApiView(request, player_id, lang):
    """
    Acts as a proxy to fetch player details from SportMonks.
    include
    country;nationality;city;position;detailedPosition;teams;transfers;pendingTransfers;sport;
    """
    include_string = "country;nationality;position;detailedPosition;teams;teams.team;transfers;transfers.type;transfers.FromTeam;transfers.ToTeam;pendingTransfers;sport;"
    url = f"{base_url}football/players/{player_id}?api_token={api_key}&include={include_string}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        
        if 'data' in data and 'transfers' in data['data']:
            clubs_timeline = process_transfers_to_clubs_timeline(data['data']['transfers'])
            data['data']['clubs_played_for'] = clubs_timeline

        if data.get('data'):
            _enrich_player_detail_with_name_tr(data['data'])
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch player details from source: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def _enrich_player_detail_with_name_tr(player_data):
    """
    Enrich player detail data with name_tr and image_path from local database
    Inserts name_tr immediately after name/display_name field for better readability
    Overrides image_path with local database value if available
    """
    player_api_id = player_data.get('id')
    player_name_tr = None
    player_image_path = None
    if player_api_id:
        try:
            player = Players.objects.filter(api_id=player_api_id).values('name_tr', 'image_path').first()
            if player:
                player_name_tr = player['name_tr']
                player_image_path = player['image_path']
        except Exception:
            pass

    if 'display_name' in player_data:
        _insert_after_key(player_data, 'display_name', 'name_tr', player_name_tr)
    elif 'name' in player_data:
        _insert_after_key(player_data, 'name', 'name_tr', player_name_tr)
    if player_image_path:
        player_data['image_path'] = player_image_path

    if player_data.get('teams'):
        team_ids = [t['team'].get('id') for t in player_data['teams'] if t.get('team') and t['team'].get('id')]
        teams_dict = {}
        if team_ids:
            teams = Teams.objects.filter(api_id__in=team_ids).values('api_id', 'name_tr', 'image_path')
            teams_dict = {t['api_id']: {'name_tr': t['name_tr'], 'image_path': t['image_path']} for t in teams}

        for player_team in player_data['teams']:
            if player_team.get('team'):
                team_id = player_team['team'].get('id')
                team_data = teams_dict.get(team_id) if team_id else None
                name_tr_value = team_data['name_tr'] if team_data else None
                image_path_value = team_data['image_path'] if team_data else None
                _insert_after_key(player_team['team'], 'name', 'name_tr', name_tr_value)
                if image_path_value:
                    player_team['team']['image_path'] = image_path_value

    if player_data.get('transfers'):
        transfer_team_ids = set()
        for transfer in player_data['transfers']:
            if transfer.get('fromteam') and transfer['fromteam'].get('id'):
                transfer_team_ids.add(transfer['fromteam']['id'])
            if transfer.get('toteam') and transfer['toteam'].get('id'):
                transfer_team_ids.add(transfer['toteam']['id'])

        transfer_teams_dict = {}
        if transfer_team_ids:
            teams = Teams.objects.filter(api_id__in=transfer_team_ids).values('api_id', 'name_tr', 'image_path')
            transfer_teams_dict = {t['api_id']: {'name_tr': t['name_tr'], 'image_path': t['image_path']} for t in teams}

        for transfer in player_data['transfers']:
            if transfer.get('fromteam'):
                from_team_id = transfer['fromteam'].get('id')
                team_data = transfer_teams_dict.get(from_team_id) if from_team_id else None
                name_tr_value = team_data['name_tr'] if team_data else None
                image_path_value = team_data['image_path'] if team_data else None
                _insert_after_key(transfer['fromteam'], 'name', 'name_tr', name_tr_value)
                if image_path_value:
                    transfer['fromteam']['image_path'] = image_path_value

            if transfer.get('toteam'):
                to_team_id = transfer['toteam'].get('id')
                team_data = transfer_teams_dict.get(to_team_id) if to_team_id else None
                name_tr_value = team_data['name_tr'] if team_data else None
                image_path_value = team_data['image_path'] if team_data else None
                _insert_after_key(transfer['toteam'], 'name', 'name_tr', name_tr_value)
                if image_path_value:
                    transfer['toteam']['image_path'] = image_path_value

    if player_data.get('clubs_played_for'):
        club_ids = [c.get('id') for c in player_data['clubs_played_for'] if c.get('id')]
        clubs_dict = {}
        if club_ids:
            clubs = Teams.objects.filter(api_id__in=club_ids).values('api_id', 'name_tr', 'image_path')
            clubs_dict = {c['api_id']: {'name_tr': c['name_tr'], 'image_path': c['image_path']} for c in clubs}

        for club in player_data['clubs_played_for']:
            club_id = club.get('id')
            club_data = clubs_dict.get(club_id) if club_id else None
            name_tr_value = club_data['name_tr'] if club_data else None
            image_path_value = club_data['image_path'] if club_data else None
            _insert_after_key(club, 'name', 'name_tr', name_tr_value)
            if image_path_value:
                club['image_path'] = image_path_value

def process_transfers_to_clubs_timeline(transfers):
    """
    Process transfers data to create a chronological timeline of clubs played for.
    Handles special cases like loan returns.
    """
    if not transfers:
        return []

    relevant_transfers = [
        transfer for transfer in transfers 
        if transfer['type']['name'].lower() != 'end of loan'
    ]
    sorted_transfers = sorted(relevant_transfers, key=lambda x: x['date'])
    
    clubs_timeline = []
    club_periods = {}
    
    for i, transfer in enumerate(sorted_transfers):
        transfer_type = transfer['type']['name']
        transfer_date = transfer['date']
        transfer_id = transfer['id']
        to_team = transfer['toteam']
        
        club_entry = {
            "id": to_team['id'],
            "name": to_team['name'],
            "image_path": to_team['image_path'],
            "short_code": to_team.get('short_code'),
            "start_date": transfer_date,
            "end_date": None,  
            "transfer_type": transfer_type,
            "transfer_id": transfer_id
        }
        
        club_key = to_team['id']
        if club_key in club_periods:
            for period in clubs_timeline:
                if period['id'] == club_key and period['end_date'] is None:
                    period['end_date'] = transfer_date
                    break
        
        club_periods[club_key] = club_entry
        clubs_timeline.append(club_entry)
    
    if sorted_transfers:
        first_transfer = sorted_transfers[0]
        first_club = first_transfer['fromteam']
        first_club_entry = {
            "id": first_club['id'],
            "name": first_club['name'],
            "image_path": first_club['image_path'],
            "short_code": first_club.get('short_code'),
            "start_date": None,
            "end_date": first_transfer['date'],
            "transfer_type": first_transfer['type']['name'],
            "transfer_id": first_transfer['id']
        }
        clubs_timeline.insert(0, first_club_entry)
    
    return clubs_timeline

######################### News api urls #########################
@api_view(['GET'])
def NewsApiView(request, lang):
    try:
        news_articles = BlogArticle.objects.all().order_by('-id')
        # FIX: Fetch all video objects, not just the first one.
        news_videos = BlogVideo.objects.all().order_by('-id')

        news_serializer = BlogArticleSerializer(news_articles, many=True,context={'request': request})
        # FIX: Serialize the entire list of videos. This will correctly return [] if empty.
        video_serializer = BlogVideoSerializer(news_videos, many=True,context={'request': request})

        response_data = {
            'articles': news_serializer.data,
            'videos': video_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def TransfersApiView(request):
    """
    Acts as a proxy to fetch the latest football transfers from SportMonks.
    Fetches transfers from the last 3 months and combines them into a single response.
    """
    try:
        today = datetime.now().date()
        all_transfers = []
        date_ranges = []
        month1_end = today
        month1_start = today - timedelta(days=30)
        date_ranges.append((month1_start, month1_end))
        month2_end = today - timedelta(days=31)
        month2_start = today - timedelta(days=61)
        date_ranges.append((month2_start, month2_end))
        month3_end = today - timedelta(days=62)
        month3_start = today - timedelta(days=92)
        date_ranges.append((month3_start, month3_end))

        for start_date, end_date in date_ranges:
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')

            url = f"{base_url}football/transfers/between/{start_date_str}/{end_date_str}?api_token={api_key}&include=player;fromTeam;toTeam;type;"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if 'data' in data and isinstance(data['data'], list):
                all_transfers.extend(data['data'])

        combined_response = {
            'data': all_transfers,
            'total_transfers': len(all_transfers),
            'date_range': {
                'from': month3_start.strftime('%Y-%m-%d'),
                'to': today.strftime('%Y-%m-%d')
            }
        }

        return Response(combined_response, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch transfers from source: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def NewsDetailApiView(request, news_id, lang):
    try:
        news_article = BlogArticle.objects.get(id=news_id)
        serializer = BlogArticleSerializer(news_article)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except BlogArticle.DoesNotExist:
        return Response({"error": "News article not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def TeamNewsApiView(request, team_id, lang):
    """
    Fetch news articles for a specific team.
    """
    try:
        team = Teams.objects.get(api_id=team_id)

        team_news = BlogArticle.objects.filter(
            team=team,   
        ).order_by('-created_at')

        
        serializer = BlogArticleSerializer(team_news, many=True, context={'request': request})
        
        response_data = {
            'team': {
                'id': team.id,  
                'name': team.name,
                'image_path': team.image_path
            },
            'articles': serializer.data,
            'count': team_news.count()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Teams.DoesNotExist:
        return Response(
            {"error": f"Team with ID {team_id} not found."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected server error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




@api_view(['POST'])
def favorite_toggle(request):
    """
    A high-performance and robust endpoint for users to add or remove a favorite item.
    - Uses transaction.atomic to ensure data integrity.
    - Includes comprehensive try-except blocks to handle potential database errors gracefully.
    """
    serializer = FavoriteToggleSerializer(data=request.data)
    # The is_valid call will handle validation errors and return a 400 Bad Request automatically
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data
    content_type = validated_data['content_type']
    object_id = validated_data['object_id']
    instance_name = validated_data['instance_name']
    user = request.user

    try:
        # The core logic is wrapped in a try block to catch unexpected database errors
        favorite, created = Favorite.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=object_id
        )

        if created:
            message = f"'{instance_name}' has been added to your favorites."
            response_status = status.HTTP_201_CREATED
        else:
            # If the favorite already existed, delete it
            favorite.delete()
            message = f"'{instance_name}' has been removed from your favorites."
            response_status = status.HTTP_200_OK

        return Response({"detail": message}, status=response_status)

    except DatabaseError:
        # This catches errors during the .get_or_create() or .delete() calls,
        # such as a temporary database connection issue.
        return Response(
            {"detail": "A database error occurred. Please try again."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception:
        # A general catch-all for any other unexpected errors.
        # It's good practice to log these errors for debugging purposes.
        return Response(
            {"detail": "An unexpected server error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_user_favorites(request):
    """
    A high-performance endpoint to list a user's favorites.
    - Efficiently fetches all favorite types (teams, players, leagues) in minimal queries.
    - Supports optional filtering by type (e.g., ?type=team).
    - Returns counts and serialized data for each category.
    """
    try:
        user = request.user
        filter_type = request.query_params.get('type', None)  # e.g., 'team', 'player', 'league'

        # 1. Fetch all favorite records for the user in a single query
        favorites_qs = Favorite.objects.filter(user=user).select_related('content_type')

        # 2. Group the favorite IDs by their model type (e.g., 'teams', 'players')
        # This is very efficient as it avoids hitting the database in a loop.
        favorite_ids = defaultdict(list)
        for fav in favorites_qs:
            model_name = fav.content_type.model_class().__name__.lower()
            favorite_ids[model_name].append(fav.object_id)

        # 3. Prepare the final response structure
        response_data = {
            'total_favorites': len(favorites_qs),
            'teams_favorites': [],
            'players_favorites': [],
            'leagues_favorites': []
        }

        # 4. Define a map to process each model type professionally
        model_map = {
            'teams': {'model': Teams, 'serializer': TeamSerializer, 'key': 'teams_favorites'},
            'players': {'model': Players, 'serializer': PlyerSerializer, 'key': 'players_favorites'},
            'leagues': {'model': Leagues, 'serializer': SimpleLeagueSerializer, 'key': 'leagues_favorites'}
        }

        # 5. Fetch and serialize the actual objects based on the collected IDs
        for model_name, details in model_map.items():
            # Check if we should process this type based on the filter
            type_name = model_name.rstrip('s')  # 'teams' -> 'team'
            if not filter_type or filter_type == type_name:
                ids = favorite_ids.get(model_name)
                if ids:
                    queryset = details['model'].objects.filter(pk__in=ids)
                    # Use the appropriate serializer for each model type
                    serializer = details['serializer'](queryset, many=True, context={'request': request})
                    response_data[details['key']] = serializer.data

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        # A general catch-all for any unexpected errors.
        return Response(
            {"detail": "An unexpected server error occurred while fetching favorites."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def PlayersReportdetailsApi(request, sport_name, team_id, match_id):
    try:
        try:
            sport = Sport.objects.get(name=sport_name)
        except Sport.DoesNotExist:
            sport = Sport.objects.create(name=sport_name)
        
        team = Teams.objects.get(id=team_id)
        match = Match.objects.get(id=match_id)
        players_list = Players.objects.filter(
            sport=sport.id,
            team=team.id
        ).select_related('team').order_by('name')
        player_count= players_list.count()
        success = True
        message = f"Players statistics for match {match.slug}//{player_count}"
        
        players_serializer = PlayerSerializer(
            players_list,
            many=True,
            context={
                'request': request,
                'match_id': match_id
            }
        )
        
        sport_data = {'sport': sport_name,'team_id': team_id,'team_name': team.name,
            'match_id': match_id,'match_name': match.name,'players': players_serializer.data,}
        
        data = {
            'success': success,
            'data': sport_data,
            'message': message,
        }
        
        return JsonResponse(data, safe=False)
    
    except Teams.DoesNotExist:
        success = False
        message = f"Team with id {team_id} does not exist"
        data = {
            'success': success,
            'data': {
                'sport': sport_name,
                'team_id': team_id,
                'match_id': match_id
            },
            'message': message,
        }
        return JsonResponse(data, status=404)
    
    except Match.DoesNotExist:
        success = False
        message = f"Match with id {match_id} does not exist"
        data = {
            'success': success,
            'data': {
                'sport': sport_name,
                'team_id': team_id,
                'match_id': match_id
            },
            'message': message,
        }
        return JsonResponse(data, status=404)
    
    except Exception as e:
        success = False
        message = f"Error in get data: {str(e)}"
        data = {
            'success': success,
            'data': {
                'sport': sport_name,
                'team_id': team_id,
                'match_id': match_id
            },
            'message': message,
        }
        return JsonResponse(data, status=500)

@api_view(['GET'])
def PlayerBasicDetailsApi(request, player_id):
    """
    Get basic player details by player ID.

    This API automatically fetches TransferMarket data in the background if:
    - market_value_last_updated is None (never fetched)
    - OR market_value_last_updated is older than 30 days

    The response is returned immediately with current data, and the update happens asynchronously.
    """
    try:
        player = Players.objects.select_related('team', 'sport').get(id=player_id)
        
        # Check if we need to fetch TransferMarket data
        should_fetch_tm_data = False

        if player.market_value_last_updated is None:
            # Never fetched before
            should_fetch_tm_data = True
        else:
            # Check if last update was more than 30 days ago
            days_since_update = (django_timezone.now() - player.market_value_last_updated).days
            if days_since_update >= 30:
                should_fetch_tm_data = True

        # Fetch TransferMarket data in background thread if needed
        if should_fetch_tm_data:
            def fetch_tm_data_async(player_pk):
                """Background task to fetch TransferMarket data"""
                try:
                    from apps.sport.views.update_players_transfermarket import (
                        get_transfermarket_data_for_player,
                        update_player_with_transfermarket_data
                    )

                    # Re-fetch the player in this thread to avoid cross-thread issues
                    player_obj = Players.objects.select_related('team').get(pk=player_pk)

                    # Get TransferMarket data
                    tm_data = get_transfermarket_data_for_player(player_obj)

                    if tm_data:
                        # Update player with TransferMarket data
                        update_player_with_transfermarket_data(player_obj, tm_data)
                        print(f"[TM API] Successfully updated player {player_obj.name} (ID: {player_pk})")
                    else:
                        print(f"[TM API] No TransferMarket data found for player {player_obj.name} (ID: {player_pk})")

                except Exception as e:
                    print(f"[TM API] Error fetching TransferMarket data for player ID {player_pk}: {e}")

            # Start background thread for TransferMarket data fetch
            thread = threading.Thread(
                target=fetch_tm_data_async,
                args=(player.pk,),
                daemon=True  # Thread will be killed when main program exits
            )
            thread.start()

        success = True
        message = f"Basic details for player {player.name}"
        
        # Add info about whether TM data is being fetched
        if should_fetch_tm_data:
            message += " (TransferMarket data update in progress)"

        player_serializer = PlayerBasicInfoSerializer(
            player,
            context={'request': request}
        )
        
        data = {
            'success': success,
            'data': player_serializer.data,
            'message': message,
            'tm_data_updating': should_fetch_tm_data,  # Let the app know if update is in progress
        }
        
        return JsonResponse(data, safe=False)
    
    except Players.DoesNotExist:
        success = False
        message = f"Player with id {player_id} does not exist"
        data = {
            'success': success,
            'data': {
                'player_id': player_id
            },
            'message': message,
        }
        return JsonResponse(data, status=404)
    
    except Exception as e:
        success = False
        message = f"Error retrieving player data: {str(e)}"
        data = {
            'success': success,
            'data': {
                'player_id': player_id
            },
            'message': message,
        }
        return JsonResponse(data, status=500)


@api_view(['POST'])
def PlayerRefreshTransfermarketApi(request, player_id):
    """
    Force refresh TransferMarket data for a player.

    This endpoint fetches the latest TransferMarket data regardless of when it was last updated.
    Useful when the user explicitly wants to update the player data.

    POST /api/v4/players/{player_id}/refresh-transfermarket/
    """
    try:
        player = Players.objects.select_related('team', 'sport').get(id=player_id)

        # Import the TransferMarket functions
        from apps.sport.views.update_players_transfermarket import (
            get_transfermarket_data_for_player,
            update_player_with_transfermarket_data
        )

        # Fetch TransferMarket data
        tm_data = get_transfermarket_data_for_player(player)

        if tm_data:
            # Update player with TransferMarket data
            update_player_with_transfermarket_data(player, tm_data)

            # Refresh from database to get updated data
            player.refresh_from_db()

            success = True
            message = f"TransferMarket data updated successfully for {player.name}"

            player_serializer = PlayerBasicInfoSerializer(
                player,
                context={'request': request}
            )

            data = {
                'success': success,
                'data': player_serializer.data,
                'message': message,
            }

            return JsonResponse(data, safe=False)
        else:
            success = False
            message = f"No TransferMarket data found for {player.name}"

            player_serializer = PlayerBasicInfoSerializer(
                player,
                context={'request': request}
            )

            data = {
                'success': success,
                'data': player_serializer.data,
                'message': message,
            }

            return JsonResponse(data, safe=False)

    except Players.DoesNotExist:
        success = False
        message = f"Player with id {player_id} does not exist"
        data = {
            'success': success,
            'data': {
                'player_id': player_id
            },
            'message': message,
        }
        return JsonResponse(data, status=404)

    except Exception as e:
        success = False
        message = f"Error refreshing TransferMarket data: {str(e)}"
        data = {
            'success': success,
            'data': {
                'player_id': player_id
            },
            'message': message,
        }
        return JsonResponse(data, status=500)


@api_view(['GET'])
def PlayerTransfersApi(request, player_id):
    """
    Get player transfer history.

    GET /api/v4/players/{player_id}/transfers/

    Returns a list of all transfers for the specified player,
    ordered by date (most recent first).
    """
    try:
        player = Players.objects.get(id=player_id)

        # Get all transfers for this player
        transfers = Transfers.objects.filter(player=player).select_related(
            'from_team', 'to_team'
        ).order_by('-date')

        from api.v4.serializers.sport.sport import PlayerTransferSerializer

        transfers_serializer = PlayerTransferSerializer(
            transfers,
            many=True,
            context={'request': request}
        )

        success = True
        message = f"Transfer history for {player.name}"

        data = {
            'success': success,
            'data': {
                'player_id': player_id,
                'player_name': player.name,
                'transfer_count': transfers.count(),
                'transfers': transfers_serializer.data
            },
            'message': message,
        }

        return JsonResponse(data, safe=False)

    except Players.DoesNotExist:
        success = False
        message = f"Player with id {player_id} does not exist"
        data = {
            'success': success,
            'data': {
                'player_id': player_id
            },
            'message': message,
        }
        return JsonResponse(data, status=404)

    except Exception as e:
        success = False
        message = f"Error retrieving transfer history: {str(e)}"
        data = {
            'success': success,
            'data': {
                'player_id': player_id
            },
            'message': message,
        }
        return JsonResponse(data, status=500)


@api_view(['GET'])
def PlayerFullDetailsApi(request, player_id):
    """
    Get full player details including transfer history.

    GET /api/v4/players/{player_id}/full/

    This endpoint returns complete player information including:
    - Basic info (name, position, nationality, etc.)
    - TransferMarket data (market value, contract, agent, etc.)
    - Transfer history

    Also triggers TransferMarket data refresh if data is stale (>30 days old).
    """
    try:
        player = Players.objects.select_related('team', 'sport').get(id=player_id)

        # Check if we need to fetch TransferMarket data
        should_fetch_tm_data = False

        if player.market_value_last_updated is None:
            should_fetch_tm_data = True
        else:
            days_since_update = (django_timezone.now() - player.market_value_last_updated).days
            if days_since_update >= 30:
                should_fetch_tm_data = True

        # Fetch TransferMarket data in background thread if needed
        if should_fetch_tm_data:
            def fetch_tm_data_async(player_pk):
                try:
                    from apps.sport.views.update_players_transfermarket import (
                        get_transfermarket_data_for_player,
                        update_player_with_transfermarket_data,
                        fetch_player_transfers,
                        save_player_transfers
                    )

                    player_obj = Players.objects.select_related('team').get(pk=player_pk)
                    tm_data = get_transfermarket_data_for_player(player_obj)

                    if tm_data:
                        update_player_with_transfermarket_data(player_obj, tm_data)

                        # Also fetch and save transfers
                        if player_obj.transfermarkt_id:
                            transfers = fetch_player_transfers(player_obj.transfermarkt_id)
                            if transfers:
                                save_player_transfers(player_obj, transfers)

                        print(f"[TM API Full] Successfully updated player {player_obj.name} (ID: {player_pk})")
                except Exception as e:
                    print(f"[TM API Full] Error fetching data for player ID {player_pk}: {e}")

            thread = threading.Thread(
                target=fetch_tm_data_async,
                args=(player.pk,),
                daemon=True
            )
            thread.start()

        from api.v4.serializers.sport.sport import PlayerWithTransfersSerializer

        success = True
        message = f"Full details for player {player.name}"

        if should_fetch_tm_data:
            message += " (TransferMarket data update in progress)"

        player_serializer = PlayerWithTransfersSerializer(
            player,
            context={'request': request}
        )

        data = {
            'success': success,
            'data': player_serializer.data,
            'message': message,
            'tm_data_updating': should_fetch_tm_data,
        }

        return JsonResponse(data, safe=False)

    except Players.DoesNotExist:
        success = False
        message = f"Player with id {player_id} does not exist"
        data = {
            'success': success,
            'data': {
                'player_id': player_id
            },
            'message': message,
        }
        return JsonResponse(data, status=404)

    except Exception as e:
        success = False
        message = f"Error retrieving player data: {str(e)}"
        data = {
            'success': success,
            'data': {
                'player_id': player_id
            },
            'message': message,
        }
        return JsonResponse(data, status=500)


@api_view(['POST', 'GET'])
def PlayerRefreshTransfermarketApi(request, player_id):
    """
    Force refresh TransferMarket data for a specific player.

    POST /api/v4/players/{player_id}/refresh-transfermarket/
    GET /api/v4/players/{player_id}/refresh-transfermarket/

    This endpoint forces a full refresh of TransferMarket data including:
    - Player profile (market value, position, contract, etc.)
    - Transfer history
    - Market value history
    - Season statistics
    - Achievements

    Returns the updated player data.
    """
    try:
        player = Players.objects.select_related('team', 'sport').get(id=player_id)

        from apps.sport.views.update_players_transfermarket import (
            get_transfermarket_data_for_player,
            update_player_with_transfermarket_data,
            fetch_player_transfers,
            save_player_transfers,
            fetch_player_market_value_history,
            save_player_market_value_history,
            fetch_player_stats,
            save_player_season_stats,
            update_player_career_totals,
            fetch_player_achievements,
            save_player_achievements,
        )

        results = {
            'profile': {'success': False, 'message': ''},
            'transfers': {'success': False, 'count': 0, 'message': ''},
            'market_value_history': {'success': False, 'count': 0, 'message': ''},
            'season_stats': {'success': False, 'count': 0, 'message': ''},
            'achievements': {'success': False, 'count': 0, 'message': ''},
        }

        # Step 1: Fetch and update player profile
        tm_data = get_transfermarket_data_for_player(player)
        if tm_data:
            update_player_with_transfermarket_data(player, tm_data)
            results['profile']['success'] = True
            results['profile']['message'] = 'Profile updated successfully'
            player.refresh_from_db()
        else:
            results['profile']['message'] = 'Could not fetch TransferMarket data'

        # Step 2: Fetch transfers if we have TM ID
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
                mv_added, mv_updated = save_player_market_value_history(player, mv_history)
                results['market_value_history']['success'] = True
                results['market_value_history']['count'] = mv_added + mv_updated
                results['market_value_history']['message'] = f'Added: {mv_added}, Updated: {mv_updated}'
            else:
                results['market_value_history']['message'] = 'No market value history found'

            # Step 4: Fetch season stats
            stats = fetch_player_stats(player.transfermarkt_id)
            if stats:
                stats_added, stats_updated = save_player_season_stats(player, stats)
                results['season_stats']['success'] = True
                results['season_stats']['count'] = stats_added + stats_updated
                results['season_stats']['message'] = f'Added: {stats_added}, Updated: {stats_updated}'
                update_player_career_totals(player)
            else:
                results['season_stats']['message'] = 'No season stats found'

            # Step 5: Fetch achievements
            try:
                achievements = fetch_player_achievements(player.transfermarkt_id)
                if achievements:
                    ach_added, ach_updated = save_player_achievements(player, achievements)
                    results['achievements']['success'] = True
                    results['achievements']['count'] = ach_added + ach_updated
                    results['achievements']['message'] = f'Added: {ach_added}, Updated: {ach_updated}'
                else:
                    results['achievements']['message'] = 'No achievements found'
            except Exception as e:
                results['achievements']['message'] = f'Error: {str(e)}'

        # Refresh player from DB to get updated data
        player.refresh_from_db()

        # Return updated player data
        from api.v4.serializers.sport.sport import PlayerWithTransfersSerializer
        player_serializer = PlayerWithTransfersSerializer(player, context={'request': request})

        overall_success = results['profile']['success']
        message = "TransferMarket data refresh completed"

        data = {
            'success': overall_success,
            'data': player_serializer.data,
            'message': message,
            'refresh_results': results,
        }

        return JsonResponse(data, safe=False)

    except Players.DoesNotExist:
        return JsonResponse({
            'success': False,
            'data': {'player_id': player_id},
            'message': f"Player with id {player_id} does not exist",
        }, status=404)

    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'data': {'player_id': player_id},
            'message': f"Error refreshing TransferMarket data: {str(e)}",
            'traceback': traceback.format_exc()[:500]
        }, status=500)


@api_view(['GET'])
def TeamDetailsApi(request, team_id):
    try:
        team = Teams.objects.select_related(
            'sport'
        ).get(id=team_id)
        
        success = True
        message = f"Team details for {team.name}"
        
        team_serializer = TeamBasicInfoSerializer(
            team,
            context={'request': request}
        )
        
        data = {
            'success': success,
            'data': team_serializer.data,
            'message': message,
        }
        
        return JsonResponse(data, safe=False)
    
    except Teams.DoesNotExist:
        success = False
        message = f"Team with id {team_id} does not exist"
        data = {
            'success': success,
            'data': {
                'team_id': team_id
            },
            'message': message,
        }
        return JsonResponse(data, status=404)
    
    except Exception as e:
        success = False
        message = f"Error retrieving team data: {str(e)}"
        data = {
            'success': success,
            'data': {
                'team_id': team_id
            },
            'message': message,
        }
        return JsonResponse(data, status=500)

@api_view(['GET'])
def SquadsBySeasonAndTeamApiView(request, season_id, team_id, lang='en'):
    """
    Acts as a proxy to fetch Squads for a specific Team in a specific Season from SportMonks.
    Target URL: /v3/football/squads/seasons/{season_id}/teams/{team_id}
    Default Include: player;details.type
    """
    try:
        url = f"{base_url}football/squads/seasons/{season_id}/teams/{team_id}?api_token={api_key}&locale={lang}"

        include_param = request.query_params.get('include', 'player;details.type')
        url += f"&include={include_param.replace(',', ';')}"

        for key, value in request.query_params.items():
            if key.startswith('filters['):
                filter_key = key.split('[')[1].split(']')[0]
                url += f"&filters={filter_key}:{value}"

        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        _enrich_squads_data(data)
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch squads from source: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def PlayerStatisticsBySeasonApiView(request, player_id, lang='en'):
    try:
        url = f"{base_url}football/players/{player_id}?api_token={api_key}&locale={lang}"
        # include_param = request.query_params.get('include', 'statistics.details.type&filters=playerstatisticdetailTypes:79,52,85,83')
        include_param = request.query_params.get('include','statistics.details.type')
        url += f"&include={include_param.replace(',', ';')}"

        # for key, value in request.query_params.items():
        #     if key.startswith('filters['):
        #         filter_key = key.split('[')[1].split(']')[0]
        #         url += f"&filters={filter_key}:{value}"

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and 'statistics' in data['data']:
            stats_list = data['data']['statistics']

            if isinstance(stats_list, list) and len(stats_list) > 0:
                stats_list.sort(key=lambda x: x.get('season_id', 0), reverse=True)

                # data['data']['statistics'] = stats_list[:4]

        _enrich_player_detail_with_name_tr(data.get('data', {}))
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch player stats: {err.response.status_code}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def SeasonDetailsApiView(request, season_id, lang='en'):
    try:
        url = f"{base_url}football/seasons/{season_id}?api_token={api_key}&locale={lang}"
        include_param = request.query_params.get('include', 'league')
        url += f"&include={include_param.replace(',', ';')}"

        for key, value in request.query_params.items():
            if key.startswith('filters['):
                filter_key = key.split('[')[1].split(']')[0]
                url += f"&filters={filter_key}:{value}"

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        _enrich_season_data(data)
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch season details: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )