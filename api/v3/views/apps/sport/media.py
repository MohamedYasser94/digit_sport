from datetime import datetime

import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.v3.serializers.sport.media import AdminYoutubeChannelSerializer
from api.v3.serializers.sport.monk import *
from api.v3.serializers.sport.sport import *
from apps.sport.models import YoutubeChannel
from apps.sport.models.models import *
from apps.sport.models.monks import *
from apps.sport.views.monks import AdminMonksFixturesGetData
from core.models.blog import BlogArticle, BlogVideo
from core.utils.pagination import PageNumberPagination
from core.views.notifications import AdminFcmNotifications
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

