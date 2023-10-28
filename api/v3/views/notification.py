from django.http import HttpResponse, JsonResponse
from rest_framework import status

from api.v1.serializers.notification import AdminNotificationSerializer
from core.models.notifications import Notification


##########################      Catalog Categories Admin            ################################
def AdminApiNotificationList(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('AdminApiNotificationList')

    notification = Notification.objects.all()
    serializer = AdminNotificationSerializer(notification, many=True)
    return JsonResponse(serializer.data, safe=False)