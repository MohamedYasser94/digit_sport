from django.http import JsonResponse

from api.v3.serializers.sport.media import AdminYoutubeChannelSerializer
from apps.sport.models import YoutubeChannel
from digit_sport import settings

api_key = settings.SPORT_MONKS_TOKEN
base_url = settings.SPORT_MONKS_URL






def YoutubeChannelApiList(request):



    try:

        channels = YoutubeChannel.objects.filter(status='Active').order_by('-create_at')
        channels_serializer = AdminYoutubeChannelSerializer(channels, many=True)

        success = True
        message = f"Send From Django API YoutubeChannelApiList"
        serializer = {'channels': channels_serializer.data }
        data = {'success': success, 'data': serializer, 'message': message, }
        return JsonResponse(data, safe=False)
    except Exception as e:
        print('error', e)
        success = False
        message = f"error in get data MatchBySportApiList  "
        data = {'success': success, 'data': [], 'message': message, }
        return JsonResponse(data, safe=False)

