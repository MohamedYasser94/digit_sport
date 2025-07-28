from collections import defaultdict
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, date
from collections import defaultdict
import requests
from django.http import JsonResponse
from rest_framework.status import *
from api.v3.serializers.sport.hive import *
from api.v3.serializers.sport.sport import TeamSeasonTableSerializer
from api.v4.serializers.sport.sport import SimpleLeagueSerializer, FixtureSerializer
from apps.sport.models.models import *
from digit_sport import settings

api_key = settings.SPORT_MONKS_TOKEN
base_url = settings.SPORT_MONKS_URL

#################### Hive Api ##################
def HiveMonksLeaguesApiList(request, ):
    url = f'https://api.sportmonks.com/v3/my/leagues?api_token={api_key}'
    try:
        success = True
        message = f"HiveLeaguesApiList  "
        response = requests.get(
            url,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": f"Bearer {api_key}",
            },
        )
        if response.status_code == 200:
            data = response.json()
            # sport_data = {'leagues': data, }
            # data = {'success': success, 'message': message, 'data': sport_data, }
            return JsonResponse(data, safe=False, status=HTTP_200_OK)
        else:
            success = False
            message = f"error in get data   {response}  "
            sport_data = {'leagues': [], }
            data = {'success': success, 'message': message, 'data': sport_data, }
            return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)
    except Exception as e:
        print('error HiveLeaguesApiList', e)
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'leagues': [], }
        data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)

def HiveDBMonksLeaguesApiList(request, ):
    sport = Sport.objects.get(name='football')
    league_list = Leagues.objects.filter(sport=sport)
    try:
        success = True
        message = f"HiveLeaguesApiList  "
        league_serializer = HiveLeaguesSerializer(league_list, many=True,context={'request': request,})
        sport_data = {'leagues': league_serializer.data}
        data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_200_OK)
    except Exception as e:
        print('error HiveLeaguesApiList', e)
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'leagues': [], }
        data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)

def HiveMonksLeaguesByDateApiList(request, date,locale):
    url = f'{base_url}football/leagues/date/{date}?api_token={api_key}&locale={locale}&include=today;currentSeason;country'
    try:
        success = True
        message = f"HiveLeaguesApiList  "
        response = requests.get(
            url,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": f"Bearer {api_key}",
            },
        )

        data = response.json()
        # sport_data = {'leagues': data, }
        # data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_200_OK)

    except Exception as e:
        print('error HiveLeaguesApiList', e)
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'leagues': [], }
        data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)


def HiveMonksLeaguesFixturesByDateApiList(request, league_id,date,locale):
    url = f'{base_url}football/fixtures/date/{date}?api_token={api_key}&locale={locale}&include=participants;league;statistics;timeline;round;events;periods;state;scores&filters=fixtureLeagues:{league_id}'
    try:
        success = True
        message = f"HiveLeaguesApiList  "
        response = requests.get(
            url,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": f"Bearer {api_key}",
            },
        )

        data = response.json()
        # sport_data = {'leagues': data, }
        # data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_200_OK)

    except Exception as e:
        print('error HiveLeaguesApiList', e)
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'leagues': [], }
        data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)


def HiveMonksFixturesByDateApiList(request, date,locale):
    url = f'{base_url}football/fixtures/date/{date}?api_token={api_key}&locale={locale}&include=participants;league;statistics;timeline;round;events;periods;state;scores'
    try:
        success = True
        message = f"HiveLeaguesApiList  "
        response = requests.get(
            url,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": f"Bearer {api_key}",
            },
        )

        data = response.json()
        # sport_data = {'leagues': data, }
        # data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_200_OK)

    except Exception as e:
        print('error HiveLeaguesApiList', e)
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'leagues': [], }
        data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)


@api_view(['GET'])
def FixturesByDateApiList(request, date, lang):
    """
    API endpoint for Flutter to get all fixtures for a specific date,
    grouped by league.
    """
    # If the date is 'today', use the current date.
    if date.lower() == 'today':
        fetch_date = datetime.today().date()
    else:
        try:
            fetch_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Please use YYYY-MM-DD or 'today'."},
                status=status.HTTP_400_BAD_REQUEST
            )

    try:
        # 1. Fetch all fixtures for the given date from your database
        # Use prefetch_related for efficiency
        fixtures_for_day = Fixtures.objects.filter(
            starting_at__date=fetch_date
        ).prefetch_related(
            'participants__team', 'league'
        ).order_by('league__name', 'starting_at')

        # 2. Group fixtures by league using a dictionary
        leagues_with_fixtures = defaultdict(list)
        for fixture in fixtures_for_day:
            if fixture.league:  # Only include fixtures that are linked to a league
                leagues_with_fixtures[fixture.league].append(fixture)

        # 3. Build the final structured response
        response_data = []
        for league, fixtures in leagues_with_fixtures.items():
            # Serialize the league and its matches
            league_serializer = SimpleLeagueSerializer(league)
            fixtures_serializer = FixtureSerializer(fixtures, many=True)

            response_data.append({
                'league': league_serializer.data,
                'matches': fixtures_serializer.data
            })

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        # Return a generic error message
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



def HiveMonksFixturesDetailsApi(request, fixture_id,locale):
    url = f'{base_url}football/fixtures/{fixture_id}?api_token={api_key}&locale={locale}&include=scores;sport;periods;league;round;formations;stage;group;aggregate;season;trends;referees;coaches;venue;state;lineups;events;timeline;statistics;participants;events.player;lineups.player;lineups.details'
    try:
        success = True
        message = f"HiveLeaguesApiList  "
        response = requests.get(
            url,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": f"Bearer {api_key}",
            },
        )

        data = response.json()
        # sport_data = {'leagues': data, }
        # data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_200_OK)

    except Exception as e:
        print('error HiveLeaguesApiList', e)
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'leagues': [], }
        data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)



def HiveDBMonksTeamsApiList(request, ):
    sport = Sport.objects.get(name='football')
    team_list = Teams.objects.filter(sport=sport)
    try:
        success = True
        message = f"HiveLeaguesApiList  "
        team_serializer = HiveTeamsSerializer(team_list, many=True,context={'request': request,})
        sport_data = {'teams': team_serializer.data}
        data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_200_OK)
    except Exception as e:
        print('error HiveLeaguesApiList', e)
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'teams': [], }
        data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)


