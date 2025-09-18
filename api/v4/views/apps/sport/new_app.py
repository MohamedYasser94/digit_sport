import threading
from collections import defaultdict
from datetime import timedelta, time
from django.utils import timezone as django_timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import requests

from api.v4.serializers.blog import BlogArticleSerializer, BlogVideoSerializer
from api.v4.serializers.sport.sport import LeagueSerializer, SimpleLeagueSerializer, FixtureSerializer, TeamSerializer, \
    TeamWithMatchesSerializer, PlyerSerializer
from apps.sport.models.models import *
from apps.sport.views.fetch_monks import _fetch_and_store_fixtures_from_source
from core.models.blog import BlogArticle, BlogVideo

from digit_sport import settings
from datetime import datetime, time, timezone

api_key = settings.SPORT_MONKS_TOKEN
base_url = settings.SPORT_MONKS_URL


############# Home Fixtures api urls #############


def _get_serialized_fixtures_for_date(fetch_date):
    """Queries the DB for a given date, serializes the data, and returns it."""
    start_of_day_utc = datetime.combine(fetch_date, time.min, tzinfo=timezone.utc)
    end_of_day_utc = datetime.combine(fetch_date, time.max, tzinfo=timezone.utc)

    fixtures_for_day = Fixtures.objects.filter(
        starting_at__range=(start_of_day_utc, end_of_day_utc)
    ).select_related('league', 'season').prefetch_related('participants__team').order_by('league__name', 'starting_at')

    leagues_with_fixtures = defaultdict(list)
    for fixture in fixtures_for_day:
        if fixture.league:
            leagues_with_fixtures[fixture.league].append(fixture)

    leagues_data = []
    for league, fixtures in leagues_with_fixtures.items():
        league_serializer = SimpleLeagueSerializer(league)
        fixture_serializer = FixtureSerializer(fixtures, many=True)
        leagues_data.append({
            'league': league_serializer.data,
            'matches': fixture_serializer.data
        })

    live_statuses_from_docs = [
        'INPLAY_1ST_HALF', 'HT', 'INPLAY_2ND_HALF', 'BREAK',
        'INPLAY_ET', 'EXTRA_TIME_BREAK', 'INPLAY_PENALTIES', 'PEN_BREAK',
        'SUSPENDED', 'INTERRUPTED'
    ]

    live_count = fixtures_for_day.filter(
        state__in=live_statuses_from_docs
    ).count()

    return {
        'live_count': live_count,
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
        has_fixtures = Fixtures.objects.filter(starting_at__date=fetch_date,
                                               sport=sport_obj).exists() if fetched_record else False

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

            response_data = _get_serialized_fixtures_for_date(fetch_date)
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            success = _fetch_and_store_fixtures_from_source(sport, fetch_date.strftime('%Y-%m-%d'))
            if not success:
                return Response({"error": "Failed to fetch data from the source API."},
                                status=status.HTTP_503_SERVICE_UNAVAILABLE)
            FetchedDate.objects.update_or_create(
                date=fetch_date, sport=sport_obj, defaults={'fetched_at': django_timezone.now()}
            )
            response_data = _get_serialized_fixtures_for_date(fetch_date)
            return Response(response_data, status=status.HTTP_200_OK)

    except Sport.DoesNotExist:
        return Response({"error": f"Sport '{sport}' not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred.{e}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        return Response(response.json(), status=status.HTTP_200_OK)

    except requests.exceptions.HTTPError as err:
        return Response(
            {"error": f"Failed to fetch player details from source: {err.response.status_code} {err.response.reason}"},
            status=err.response.status_code
        )
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
