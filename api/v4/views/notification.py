import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fcm_django.models import FCMDevice

from rest_framework import viewsets, permissions, status

from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import *



from api.v4.serializers.notification import AdminNotificationSerializer, DeviceInfoSerializer
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
def DeviceFcmAdd(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            print(f'JSON parsing error: {e}')
            return JsonResponse({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)

        device_token = data.get('device_token')
        device_type = data.get('device_type')
        device_info = data.get('device_info')

        # Validate required fields
        if not device_token:
            print('Missing device_token')
            return JsonResponse({'error': 'device_token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if FCM device already exists
            fcm_object = FCMDevice.objects.get(registration_id=device_token)
            if device_type:
                fcm_object.type = device_type
                fcm_object.save()

            return JsonResponse({'status': 'success', 'message': 'Device token already registered'}, status=status.HTTP_200_OK)

        except FCMDevice.DoesNotExist:
            try:
                # Create new device info
                device_object = DeviceInfo(
                    device_token=device_token,
                    device_type=device_type,
                    device_info=device_info
                )
                device_object.save()

                # Create FCM device
                fcm_object = FCMDevice(
                    device_id=device_object.id,
                    registration_id=device_token,
                    type=device_type
                )
                fcm_object.save()
                AdminFcmNotifications(request)

                data_response = {
                    'status': 'success',
                    'message': 'Device Info saved successfully',
                    'device_token': device_token,
                    'device_code': device_object.device_code,
                }
                return JsonResponse(data_response, status=status.HTTP_201_CREATED)

            except Exception as e:
                print(f'Error creating device: {str(e)}')
                import traceback
                traceback.print_exc()
                return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f'Unexpected error: {str(e)}')
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'error': 'Method not allowed'}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def DeviceFcmChangeUserStatus(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        device_token = data.get('device_token')
        notify_status = data.get('notify_status')
        print('DeviceFcmChangeUserStatus',  notify_status) # True or False
        try:
            device_object = DeviceInfo.objects.filter(device_token=device_token)
            for device in device_object:
                device.user_active = notify_status
                device.save()

            if notify_status == False:
                return HttpResponse(status=HTTP_202_ACCEPTED)
            else:
                return HttpResponse(status=HTTP_201_CREATED)
        except Exception as e:

            return HttpResponse(status=HTTP_404_NOT_FOUND)


    return HttpResponse(status=HTTP_400_BAD_REQUEST)














