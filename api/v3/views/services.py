import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView


from core.forms.catalog import AdminServicesForm
from core.models.core import QrCode, SystemSetting
from core.models.services import Services
##########################      Services Admin            ################################
from Digithup.settings import FRONTEND_TEMPLATES



def FrontRollList(request):
    import requests
    import json
    api_request = requests.get(
        "https://www.lawhup.net/en/api/roll/list/")
    api = json.loads(api_request.content)

    api_url = SystemSetting.objects.get(title='Digithup')
    try:
        qrcode = QrCode.objects.get(name='roll')
    except  QrCode.DoesNotExist:
        qrcode = None
    courts = Court.objects.all()
    court_list = list(courts.values('title', 'id', ))
    rolls = Roll.objects.all()
    roll_list = list(rolls.values('title', 'court', 'id', 'description', 'image', ))
    context = {
        'qrcode': qrcode,
        'court_list': court_list,
        'rolls': rolls,
        'roll_list': roll_list,
        'apiUrl':api_url,
        'api':api,
    }
    return render(request, f'{FRONTEND_TEMPLATES}/services/roll.html', context)



def FrontRollDetails(request,slug):
    qrcode = QrCode.objects.filter(name='roll')
    courts = Court.objects.all()
    court_list = list(courts.values('title', 'id', ))
    rolls = Roll.objects.get(slug=slug)

    context = {
        'qrcode': qrcode,
        'court_list': court_list,
        'rolls': rolls,

    }
    return render(request, f'{FRONTEND_TEMPLATES}/services/roll-detail.html', context)
    # return render(request, 'justica/labtest/qrcode.html', )


@csrf_exempt
def FrontRollCircuitApi(request, court_id):
    # if not request.user.is_authenticated:
    #     return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    circuit_items = None
    courts = Court.objects.filter(id=court_id)
    for court in courts:
        circuit_items = CourtCircuit.objects.filter(court=court)

    serializer = CourtCircuitSerializer(circuit_items, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def FrontRollListApi(request):
    # if not request.user.is_authenticated:
    #     return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    roll_items = Roll.objects.all()
    serializer = RollSerializer(roll_items, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def FrontRolCircuitListApi(request, circuit_id):
    # if not request.user.is_authenticated:
    #     return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    roll_items = None
    circuits = CourtCircuit.objects.filter(id=circuit_id)
    for circuit in circuits:
        roll_items = Roll.objects.filter(circuit=circuit)

    serializer = RollSerializer(roll_items, many=True)
    return JsonResponse(serializer.data, safe=False)


