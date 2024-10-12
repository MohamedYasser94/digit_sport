from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fcm_django.models import FCMDevice

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from api.v3.serializers.notification import *
from core.models.notifications import *
from core.views.notifications import AdminFcmNotifications


##########################      Catalog Categories Admin            ################################
def AdminApiNotificationList(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('AdminApiNotificationList')

    notification = Notification.objects.all()
    serializer = AdminNotificationSerializer(notification, many=True)
    return JsonResponse(serializer.data, safe=False)


class AdminDeviceInfoFromApp(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = DeviceInfoSerializer
    queryset = DeviceInfo.objects.all()

    def list(self, request):
        queryset = DeviceInfo.objects.all()
        serializer = DeviceInfoSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = DeviceInfoSerializer(data=request.data)
        print('AdminDeviceInfoFromApp',request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, pk=None):
        queryset = DeviceInfo.objects.all()
        device = get_object_or_404(queryset, pk=pk)
        serializer = DeviceInfoSerializer(device)
        return Response(serializer.data)

    def update(self, request, pk=None):
        device = DeviceInfo.objects.get(pk=pk)
        serializer = DeviceInfoSerializer(device, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        device = DeviceInfo.objects.get(pk=pk)
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


# @permission_classes([permissions.AllowAny])
@csrf_exempt
def DeviceInfoFromApp(request):

    if request.method == 'POST':
        data = json.loads(request.body)
        device_token = data.get('device_token')
        device_type = data.get('device_type')
        device_info = data.get('device_info')
        try:
            try:
                fcm_object = FCMDevice.objects.get(registration_id=device_token )
                fcm_object.type = device_type
                # device_object = DeviceInfo.objects.get( device_token=device_token )
                # device_object.device_type = device_type
                # device_object.save()

                return JsonResponse(data, status=status.HTTP_200_OK)

            except Exception as e:

                device_object = DeviceInfo(
                    device_token=device_token,
                    device_type=device_type,
                    device_info=device_info
                )
                device_object.save()
                fcm_object = FCMDevice(device_id=device_object.id, registration_id=device_token, type=device_type, )
                fcm_object.save()
                AdminFcmNotifications(request)
                data = {
                    'status': 'success',
                    'message': 'Device Info saved successfully',
                    'device_token': device_token,
                    'device_code': device_object.device_code,
                }
                return JsonResponse(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)










