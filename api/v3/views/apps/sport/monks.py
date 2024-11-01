import requests
from django.http import JsonResponse
from rest_framework.status import *
from api.v3.serializers.sport.hive import *
from api.v3.serializers.sport.sport import TeamSeasonTableSerializer
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


def HiveMonksLeaguesByDateApiList(request, date,locale):
    url = f'{base_url}football/leagues/date/{date}?api_token={api_key}&locale={locale}&include=today;currentSeason'
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


