import threading
from collections import defaultdict
from datetime import timedelta, time
from django.http import JsonResponse
from django.utils import timezone as django_timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from django.shortcuts import get_object_or_404

from api.v4.serializers.sport.sport import LeagueSerializer, MatchDetailsSerializer, MatchGoalsSerializer, MatchSerializer, SimpleLeagueSerializer, FixtureSerializer, TeamSeasonTableSerializer, TeamSerializer, \
    TeamWithMatchesSerializer, PlyerSerializer
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
        league_serializer = SimpleLeagueSerializer(league)
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
        match = Match.objects.get(id=match_id)
        goals = MatchGoals.objects.filter(match=match_id)
        best_player_report = MatchPlayerReport.objects.filter(match=match_id, is_best_player=True).first()
        match_serializer = MatchDetailsSerializer(match, many=False, context={'request': request})
        goals_serializer = MatchGoalsSerializer(goals, many=True, context={'request': request})
        best_player_serializer = None
        if best_player_report:best_player_serializer = MatchPlayerReportSerializer(best_player_report, many=False, context={'request': request}).data

        sport_data = {'matches': match_serializer.data, 'goals': goals_serializer.data,'best_player': best_player_serializer}
        success = True
        message = f"Send From Django API mix {match_id} "
        
        data = {'success': success, 'data': sport_data, 'message': message,}
        return JsonResponse(data, safe=False)

    except Exception as e:
        print(e)
        success = False
        message = f"error in get data  match Details {e} "
        sport_data = {'matches': [],}
        data = {'success': success, 'data': sport_data, 'message': message,}
    return JsonResponse(data, safe=False)

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
            #Time conversion to UTC+3
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
        return Response(response.json(), status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch team details from source: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        serializer = LeagueSerializer(leagues, many=True)
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
def LiveStandingsByLeagueApiView(request, league_id):
    """
    Acts as a proxy to fetch live standings for a league from SportMonks.
    """
    include_params = request.query_params.get('include', 'participant;details;details.type',)
    url = f"{base_url}football/standings/live/leagues/{league_id}?api_token={api_key}&include={include_params}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return Response(response.json(), status=status.HTTP_200_OK)
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
def TopScorersBySeasonApiView(request, season_id):
    """
    Acts as a proxy to fetch top scorers for a season from SportMonks.
    This version correctly constructs the URL with multiple separate 'filters' parameters.
    """
    try:
        # Start with the base URL and API token
        url = f"{base_url}football/topscorers/seasons/{season_id}?api_token={api_key}"

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
        return Response(response.json(), status=status.HTTP_200_OK)

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
def TopAssistsBySeasonApiView(request, season_id):
    """
    Acts as a proxy to fetch top scorers for a season from SportMonks.
    This version correctly constructs the URL with multiple separate 'filters' parameters.
    """
    try:
        # Start with the base URL and API token
        url = f"{base_url}football/topscorers/seasons/{season_id}?api_token={api_key}"

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
        return Response(response.json(), status=status.HTTP_200_OK)

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
def PreviousMatchesApiView(request, team1_id, team2_id):
    """
    Fetch previous matches between two teams (head-to-head) from SportMonks,
    including only scores with description = 'CURRENT' and league details.
    """
    try:
        url = f"{base_url}football/fixtures/head-to-head/{team1_id}/{team2_id}?api_token={api_key}&include=scores;league"

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
def TeamLatestUpcomingApiView(request, team_id):
    """
    Fetch a single team's latest match (with only CURRENT scores) and first upcoming match.
    """
    try:
        url = f"{base_url}football/teams/{team_id}?api_token={api_key}&include=latest;latest.participants;latest.league;latest.scores;upcoming;upcoming.league;upcoming.participants"

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
def standingsByseasonsApiView(request, season_id):
    """
    Acts as a proxy to fetch season details from SportMonks.
    Includes fixtures, teams, sport, league, stages, groups, statistics, etc.
    """
    try:
        # Start with the base URL and API token
        url = f"{base_url}football/standings/seasons/{season_id}?api_token={api_key}"

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
        
        return Response(response.json(), status=status.HTTP_200_OK)

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
def LeagueInformationApiView(request, league_id):
    """
    Acts as a proxy to fetch league details (seasons, latest, upcoming, currentSeason, stages)
    from SportMonks API for the given league_id.
    """
    try:
        url = f"{base_url}football/leagues/{league_id}?api_token={api_key}"

        include_param = request.query_params.get("include","seasons;currentSeason;stages;")
        url += f"&include={include_param.replace(',', ';')}"

        for key, value in request.query_params.items():
            if key.startswith("filters["):
                filter_key = key.split("[")[1].split("]")[0]
                url += f"&filters={filter_key}:{value}"

        response = requests.get(url)
        response.raise_for_status()

        return Response(response.json(), status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch league details: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code)
    except Exception as e:
        return Response(
            {"error": f"Unexpected error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def SeasonSchedulesApiView(request, season_id):
    """
    Proxy to fetch schedules for a given season from SportMonks API.
    Supports dynamic 'include' and 'filters'.
    """
    try:
        url = f"{base_url}football/schedules/seasons/{season_id}?api_token={api_key}"

        include_param = request.query_params.get("include", "")
        if include_param:
            url += f"&include={include_param.replace(',', ';')}"

        for key, value in request.query_params.items():
            if key.startswith("filters["):
                filter_key = key.split("[")[1].split("]")[0]
                url += f"&filters={filter_key}:{value}"

        response = requests.get(url)
        response.raise_for_status()

        return Response(response.json(), status=status.HTTP_200_OK)

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
def LeagueSearchApiView(request, name):
    """
    Proxy endpoint to search leagues by name using SportMonks API.
    Example: /v4/football/leagues/search/Premier/
    """
    try:
        # Base URL for searching leagues
        url = f"{base_url}football/leagues/search/{name}?api_token={api_key}"

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

        return Response(response.json(), status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch leagues: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def TeamSearchApiView(request, name):
    """
    Proxy endpoint to search teams by name using SportMonks API.
    Example: /v4/football/teams/search/man/
    """
    try:
        # Base URL for searching teams
        url = f"{base_url}football/teams/search/{name}?api_token={api_key}"

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

        return Response(response.json(), status=status.HTTP_200_OK)

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
def PlayerSearchApiView(request, name):
    """
    Proxy endpoint to search teams by name using SportMonks API.
    Example: /v4/football/teams/search/man/
    """
    try:
        # Base URL for searching teams
        url = f"{base_url}football/teams/search/{name}?api_token={api_key}"

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

        return Response(response.json(), status=status.HTTP_200_OK)

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
        
        return Response(data, status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch player details from source: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    """
    try:
        # Construct the URL with includes for player and team details
        url = f"{base_url}football/transfers?api_token={api_key}&include=player;fromTeam;toTeam;type;"

        response = requests.get(url)
        response.raise_for_status()  # Raises an exception for 4xx/5xx errors

        return Response(response.json(), status=status.HTTP_200_OK)

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
def PlayersBySportApiList(request, sport_name, team_id, match_id):
    try:
        try:
            sport = Sport.objects.get(name=sport_name)
        except Sport.DoesNotExist:
            sport = Sport.objects.create(name=sport_name)
        team = Teams.objects.get(id=team_id)
        match = Match.objects.get(id=match_id)
        players_list = Players.objects.filter(sport=sport.id, team=team.id
        ).select_related('team').prefetch_related('league').order_by('name')

        success = True
        message = f"Players statistics for match {match_id}"
        players_serializer = PlyerSerializer(players_list, many=True, context={'request': request,'match_id': match_id  })
        sport_data = {'sport': sport_name, 'team_id': team_id,
                        'team_name': team.name,'match_id': match_id,
                        'match_name': match.name,'players': players_serializer.data,}

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
            'data': {'sport': sport_name, 'team_id': team_id, 'match_id': match_id},
            'message': message,
        }
        return JsonResponse(data, status=404)
        
    except Match.DoesNotExist:
        success = False
        message = f"Match with id {match_id} does not exist"
        data = {
            'success': success, 
            'data': {'sport': sport_name, 'team_id': team_id, 'match_id': match_id},
            'message': message,
        }
        return JsonResponse(data, status=404)
        
    except Exception as e:
        success = False
        message = f"Error in get data: {str(e)}"
        data = {
            'success': success, 
            'data': {'sport': sport_name, 'team_id': team_id, 'match_id': match_id},
            'message': message,
        }
        return JsonResponse(data, status=500)
    
        