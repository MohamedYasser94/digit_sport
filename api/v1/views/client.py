from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from api.v1.serializers.client import ClientsSerializer
from core.models.people import Clients


def AdminApiClients(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    client_list = Clients.objects.all()

    serializer = ClientsSerializer(client_list, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def AdminApiClient(request, client_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    client = Clients.objects.filter(id=client_id)
    serializer = ClientsSerializer(client, many=True)
    return JsonResponse(serializer.data, safe=False)
