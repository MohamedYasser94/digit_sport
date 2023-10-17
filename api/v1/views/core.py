from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from api.v1.serializers.core import CommonProfileSerializer

from core.models.core import CommonProfile


@csrf_exempt
def AdminCommonClientProfile(request, profile_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print(request.user)

    customer_profile = CommonProfile.objects.filter(id=profile_id)
    serializer = CommonProfileSerializer(customer_profile, many=True)
    return JsonResponse(serializer.data, safe=False)