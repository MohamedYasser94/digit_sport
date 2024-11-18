import json

from django.http import JsonResponse, HttpResponse
from rest_framework.status import *
from api.v3.serializers.sport.hive import *
from api.v3.serializers.sport.sport import TeamSeasonTableSerializer
from apps.sport.models.models import *
from core.models.notifications import DeviceInfo


def UpdateHiveData(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        device_token = data.get('device_token')
        try:
            device_object = DeviceInfo.objects.get(device_token=device_token)
            if device_object.need_update == True:
                device_object.need_update = False
                device_object.save()
                return HttpResponse(status=HTTP_202_ACCEPTED)
            else:
                return HttpResponse(status=HTTP_200_OK)
        except Exception as e:
            return HttpResponse(status=HTTP_404_NOT_FOUND)

    return HttpResponse(status=HTTP_400_BAD_REQUEST)
#################### Hive Api ##################
def HiveLeaguesApiList(request, ):
    sport = Sport.objects.all().exclude(name='football')
    league_list = Leagues.objects.filter(sport__in=sport)
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


def HiveTeamApiList(request, ):
    try:
        team_list = Teams.objects.all()
        team_serializer = HiveTeamsSerializer(team_list, many=True, context={'request': request})
        success = True
        message = f"HiveTeamApiList  "
        sport_data = {'teams': team_serializer.data}
        data = {'success': success, 'message': message, 'data': sport_data, }

        return JsonResponse(data, safe=False, status=HTTP_200_OK)
    except Exception as e:
        print('error HiveTeamApiList', e)
        success = False
        message = f"error in get data   {e}  "
        data = {'success': success, 'message': message, 'data': [], }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)


def HiveMatchesApiList(request, ):
    try:
        matches  = Match.objects.all()
        match_serializer = HiveMatchDetailsSerializer(matches, many=True, context={'request': request})
        success = True
        message = f"HiveMatchesApiList  "
        sport_data = {'matches': match_serializer.data}
        data = {'success': success, 'message': message, 'data': sport_data, }

        return JsonResponse(data, safe=False, status=HTTP_200_OK)
    except Exception as e:
        print('error HiveMatchesApiList', e)
        success = False
        message = f"error in get data   {e}  "
        data = {'success': success, 'message': message, 'data': [], }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)




def HiveTableApiList(request, ):
    try:
        table  = LeagueSeasonTable.objects.all()
        table_serializer = HiveLeagueSeasonTableSerializer(table, many=True, context={'request': request})
        success = True
        message = f"HiveTableApiList  "
        sport_data = {'table': table_serializer.data}
        data = {'success': success, 'message': message, 'data': sport_data, }

        return JsonResponse(data, safe=False, status=HTTP_200_OK)
    except Exception as e:
        print('error HiveTableApiList', e)
        success = False
        message = f"error in get data   {e}  "
        data = {'success': success, 'message': message, 'data': [], }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)

def HiveStandingApiList(request, ):
    try:
        table  = TeamSeasonTable.objects.all()
        table_serializer = HiveTeamSeasonTableSerializer(table, many=True, context={'request': request})
        success = True
        message = f"HiveTableApiList  "
        sport_data = {'table': table_serializer.data}
        data = {'success': success, 'message': message, 'data': sport_data, }

        return JsonResponse(data, safe=False, status=HTTP_200_OK)
    except Exception as e:
        print('error HiveTableApiList', e)
        success = False
        message = f"error in get data   {e}  "
        data = {'success': success, 'message': message, 'data': [], }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)
def HiveRoundsApiList(request, ):
    try:
        rounds  = Round.objects.all()
        rounds_serializer = HiveRoundSerializer(rounds, many=True, context={'request': request})
        success = True
        message = f"HiveRoundsApiList  "
        sport_data = {'rounds': rounds_serializer.data}
        data = {'success': success, 'message': message, 'data': sport_data, }

        return JsonResponse(data, safe=False, status=HTTP_200_OK)
    except Exception as e:
        print('error HiveRoundsApiList', e)
        success = False
        message = f"error in get data   {e}  "
        data = {'success': success, 'message': message, 'data': [], }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)



def HiveGoalsApiList(request, ):
    try:
        goals  = MatchGoals.objects.all()
        goals_serializer = HiveGoalsSerializer(goals, many=True, context={'request': request})
        success = True
        message = f"HiveGoalsApiList  "
        sport_data = {'goals': goals_serializer.data}
        data = {'success': success, 'message': message, 'data': sport_data, }

        return JsonResponse(data, safe=False, status=HTTP_200_OK)
    except Exception as e:
        print('error HiveGoalsApiList', e)
        success = False
        message = f"error in get data   {e}  "
        data = {'success': success, 'message': message, 'data': [], }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)