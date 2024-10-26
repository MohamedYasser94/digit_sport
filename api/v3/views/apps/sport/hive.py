from django.http import JsonResponse
from rest_framework.status import *
from api.v3.serializers.sport.hive import *
from api.v3.serializers.sport.sport import TeamSeasonTableSerializer
from apps.sport.models.models import *




#################### Hive Api ##################
def HiveLeaguesApiList(request, ):
    league_list = Leagues.objects.all()
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