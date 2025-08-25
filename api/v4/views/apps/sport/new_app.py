import threading
from collections import defaultdict
from datetime import timedelta, time
from django.utils import timezone as django_timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from api.v4.serializers.blog import BlogArticleSerializer
from api.v4.serializers.sport.sport import LeagueSerializer, SimpleLeagueSerializer, FixtureSerializer, TeamSerializer, \
    TeamWithMatchesSerializer
from apps.sport.models.models import *
from apps.sport.views.monks import _fetch_and_store_fixtures_from_source
from core.models.blog import BlogArticle

from digit_sport import settings
from datetime import datetime, time, timezone # <<< ADD THIS IMPORT
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

    # <<< FIX: Using the correct list of live statuses from Sportmonks >>>
    live_statuses_from_docs = [
        'INPLAY_1ST_HALF', 'HT', 'INPLAY_2ND_HALF', 'BREAK',
        'INPLAY_ET', 'EXTRA_TIME_BREAK', 'INPLAY_PENALTIES', 'PEN_BREAK',
        'SUSPENDED', 'INTERRUPTED'
    ]

    # The 'state' field in your Fixtures model should store the Sportmonks state string.
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

        # Check if data exists in our database
        fetched_record = FetchedDate.objects.filter(date=fetch_date, sport=sport_obj).first()
        has_fixtures = Fixtures.objects.filter(starting_at__date=fetch_date,
                                               sport=sport_obj).exists() if fetched_record else False

        # --- Main Logic Branch ---
        if fetched_record and has_fixtures:
            print(f"✅ Cache HIT for {sport} on {fetch_date}. Serving from local DB.")

            # For today's date, check if the data is "stale" (e.g., older than 2 minutes)
            today = django_timezone.now().date()
            if fetch_date == today:
                time_since_last_fetch = django_timezone.now() - fetched_record.fetched_at
                # Refresh if data is older than 2 minutes
                if time_since_last_fetch > timedelta(minutes=2):
                    print(f"🔄 Data for today is stale. Starting background refresh...")
                    # Start the fetch in a separate thread so it doesn't block the response
                    thread = threading.Thread(
                        target=_fetch_and_store_fixtures_from_source,
                        args=(sport, fetch_date.strftime('%Y-%m-%d'))
                    )
                    thread.start()

            # Return the cached data immediately
            response_data = _get_serialized_fixtures_for_date(fetch_date)
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # --- CACHE MISS ---
            print(f"❌ Cache MISS for {sport} on {fetch_date}. Fetching synchronously.")
            success = _fetch_and_store_fixtures_from_source(sport, fetch_date.strftime('%Y-%m-%d'))

            if not success:
                return Response({"error": "Failed to fetch data from the source API."},
                                status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # Log the successful fetch
            FetchedDate.objects.update_or_create(
                date=fetch_date, sport=sport_obj, defaults={'fetched_at': django_timezone.now()}
            )

            print(f"✅ Fetch successful. Now serving newly stored data for {fetch_date}.")
            response_data = _get_serialized_fixtures_for_date(fetch_date)
            return Response(response_data, status=status.HTTP_200_OK)

    except Sport.DoesNotExist:
        return Response({"error": f"Sport '{sport}' not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"An unexpected error occurred in FixturesByDateApiList: {str(e)}")
        return Response({"error": "An unexpected server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FavoriteLeagueToggle(APIView):
    """
    Toggles a league as a favorite for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        league_id = request.data.get('league_id')
        if not league_id:
            return Response({'error': 'League ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            league = Leagues.objects.get(api_id=league_id)
        except Leagues.DoesNotExist:
            return Response({'error': 'League not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Try to get the favorite, if it exists, delete it.
        favorite, created = FavoriteLeague.objects.get_or_create(user=request.user, league=league)

        if not created:
            # The favorite already existed, so we delete it (un-star)
            favorite.delete()
            return Response({'status': 'removed'}, status=status.HTTP_200_OK)

        # The favorite was just created (star)
        return Response({'status': 'added'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def FixtureDetailApiView(request, fixture_id, lang):
    """
    API endpoint for Flutter to get all details for a single fixture,
    including participants, scores, events, statistics, and lineups.
    """
    try:
        # Fetch the specific fixture using its primary key (or api_id)
        fixture = Fixtures.objects.prefetch_related(
            'participants__team', 'league', 'season'
        ).get(api_id=fixture_id)

    except Fixtures.DoesNotExist:
        return Response(
            {"error": "Fixture not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected server error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Use your existing FixtureSerializer to structure the data.
    # Ensure this serializer is configured to include nested data for
    # participants, events, statistics, lineups, league, and season.
    # If it's not, you'll need to adjust it or create a new detailed one.

    # For demonstration, we'll manually construct the response dictionary
    # based on what the Flutter app will expect.

    participants_data = []
    for p in fixture.participants.all():
        participants_data.append({
            'api_id': p.team.api_id,
            'name': p.team.name,
            'image_path': p.team.image_path,
            'meta_location': p.meta_location
        })

    # Assuming 'events', 'statistics', and 'lineups' are stored as JSONFields on the Fixture model
    events_data = fixture.events if isinstance(fixture.events, list) else []
    statistics_data = fixture.statistics if isinstance(fixture.statistics, list) else []
    lineups_data = fixture.lineups if isinstance(fixture.lineups, list) else []

    response_data = {
        'api_id': fixture.api_id,
        'name': fixture.name,
        'starting_at': fixture.starting_at,
        'leg': fixture.leg,
        'result_info': fixture.result_info,
        'league': {
            'api_id': fixture.league.api_id,
            'name': fixture.league.name,
            'image_path': fixture.league.image_path
        } if fixture.league else None,
        'season_id': fixture.season.api_id if fixture.season else None,
        'participants': participants_data,
        'events': events_data,
        'statistics': statistics_data,
        'lineups': lineups_data,
        # You may need to serialize scores and other fields similarly
    }

    return Response(response_data, status=status.HTTP_200_OK)


######################### team Screen api urls #########################
@api_view(['GET'])
def TeamScreenApiView(request, sport, lang):
    """
    Optimized API endpoint for Flutter to get teams with their recent and upcoming matches.
    """
    try:
        # 1. Get a set of recent and upcoming fixtures
        starting_at = django_timezone.now() - timedelta(days=7)
        ending_at = django_timezone.now() + timedelta(days=7)
        fixtures = Fixtures.objects.filter(
            starting_at__range=(starting_at, ending_at)
        ).prefetch_related('participants__team')

        # 2. Get the unique teams from those fixtures
        team_ids = set()
        for fixture in fixtures:
            for participant in fixture.participants.all():
                team_ids.add(participant.team.api_id)

        teams = Teams.objects.filter(api_id__in=team_ids).order_by('name')

        if not teams.exists():
            teams = Teams.objects.all()[:10]

        # 3. Prepare fixtures data for efficient lookup in the serializer
        now = django_timezone.now()
        upcoming_fixtures_map = defaultdict(list)
        previous_fixtures_map = defaultdict(list)

        # Separate all fixtures into upcoming and previous
        all_team_fixtures = Fixtures.objects.filter(
            participants__team__api_id__in=team_ids,
        ).distinct()

        for fixture in all_team_fixtures:
            for participant in fixture.participants.all():
                if fixture.starting_at >= now:
                    # Limit to 5 upcoming matches
                    if len(upcoming_fixtures_map[participant.team.api_id]) < 5:
                        upcoming_fixtures_map[participant.team.api_id].append(fixture)
                else:
                    # Limit to 5 previous matches
                    if len(previous_fixtures_map[participant.team.api_id]) < 5:
                        previous_fixtures_map[participant.team.api_id].append(fixture)

        # 4. Pass the prepared data to the serializer via context
        serializer_context = {
            'upcoming_fixtures': upcoming_fixtures_map,
            'previous_fixtures': previous_fixtures_map,
        }

        serializer = TeamWithMatchesSerializer(teams, many=True, context=serializer_context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # Log the full exception for debugging
        print(f"Error in TeamScreenApiView: {e}")
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def TeamDetailApiView(request, team_id, lang):
    """
    API endpoint for Flutter to get detailed information about a team,
    including its players and statistics.
    """
    try:
        team = Teams.objects.get(api_id=team_id)
        serializer = TeamSerializer(team)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Teams.DoesNotExist:
        return Response({"error": "Team not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
################ Leagues  API Endpoints ################

@api_view(['GET'])
def LeaguesApiView(request, sport, lang):
    """
    API endpoint to get a list of leagues for a specific sport.
    """
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
    """
    API endpoint to get basic details for a single league, including its current season.
    """
    try:
        league = Leagues.objects.get(api_id=league_id)
        # Assuming a related name 'seasons' or similar on the League model
        current_season = league.currentseason
        response_data = {
            'api_id': league.api_id,
            'name': league.name,
            'image_path': league.image_path,
            'country': league.country,
            'current_season_id': current_season if current_season else None,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    except Leagues.DoesNotExist:
        return Response({"error": "League not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


  ######################### News api urls #########################
@api_view(['GET'])
def NewsApiView(request, lang):
    """
    API endpoint to get a list of news articles.
    """
    try:
        news_articles = BlogArticle.objects.all().order_by('-published_at')  # Assuming a 'published_at' field
        serializer = BlogArticleSerializer(news_articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def NewsDetailApiView(request, news_id, lang):
    """
    API endpoint to get detailed information about a single news article.
    """
    try:
        news_article = BlogArticle.objects.get(id=news_id)
        serializer =BlogArticleSerializer(news_article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except BlogArticle.DoesNotExist:
        return Response({"error": "News article not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)