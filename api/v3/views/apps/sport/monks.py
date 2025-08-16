import threading

import requests
from django.http import JsonResponse
from django.utils import timezone as django_timezone
from datetime import datetime, time, timezone, timedelta
from collections import defaultdict
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK
from rest_framework.views import APIView

from api.v4.serializers.sport.hive import HiveLeaguesSerializer, HiveTeamsSerializer
from api.v4.serializers.sport.sport import SimpleLeagueSerializer, FixtureSerializer
from apps.sport.models import Sport, Leagues, Teams, Fixtures, FetchedDate, Standings, TopScorer, FavoriteLeague
from apps.sport.views.monks import _fetch_and_store_fixtures_from_source
from digit_sport import settings

api_key = settings.SPORT_MONKS_TOKEN
base_url = settings.SPORT_MONKS_URL


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





################ Leagues and Teams API Endpoints ################
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


@api_view(['GET'])
def LeagueStandingsApiView(request, season_id, lang):
    """
    API endpoint to get the standings table for a given season.
    Handles both single league tables and grouped standings.
    """
    try:
        # Assuming a 'Standings' model with a foreign key to Season
        standings = Standings.objects.filter(season_id=season_id).order_by('group_id', 'position')

        if not standings.exists():
            return Response([], status=status.HTTP_200_OK)  # Return empty list if no standings

        # Serialize the data
        # This assumes you have a serializer that can handle the standings model
        # For demonstration, we'll construct it manually
        standings_data = []
        for standing in standings:
            standings_data.append({
                'position': standing.position,
                'group_id': standing.group.api_id if standing.group else None,
                'group_name': standing.group.name if standing.group else None,
                'participant': {
                    'api_id': standing.participant.api_id,
                    'name': standing.participant.name,
                    'image_path': standing.participant.image_path,
                },
                'points': standing.points,
                'played': standing.games_played,
                'won': standing.won,
                'draw': standing.draw,
                'lost': standing.lost,
                'goals_scored': standing.goals_scored,
                'goals_against': standing.goals_against,
            })

        return Response(standings_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def LeagueTopScorersApiView(request, season_id, lang):
    """
    API endpoint to get the top goal scorers and top assist providers for a season.
    """
    try:
        # Assuming a 'Topscorers' model linked to a Season
        top_scorers = TopScorer.objects.filter(season_id=season_id, type='goals').order_by('-total')[:20]
        top_assists = TopScorer.objects.filter(season_id=season_id, type='assists').order_by('-total')[:20]

        scorers_data = [{
            'position': scorer.position,
            'player': {
                'api_id': scorer.player.api_id,
                'name': scorer.player.name,
                'image_path': scorer.player.image_path,
            },
            'participant': {
                'api_id': scorer.participant.api_id,
                'name': scorer.participant.name,
                'image_path': scorer.participant.image_path,
            },
            'total': scorer.total,
        } for scorer in top_scorers]

        assists_data = [{
            'position': assist.position,
            'player': {
                'api_id': assist.player.api_id,
                'name': assist.player.name,
                'image_path': assist.player.image_path,
            },
            'participant': {
                'api_id': assist.participant.api_id,
                'name': assist.participant.name,
                'image_path': assist.participant.image_path,
            },
            'total': assist.total,
        } for assist in top_assists]

        response_data = {
            'goals': scorers_data,
            'assists': assists_data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"An unexpected server error occurred: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)






