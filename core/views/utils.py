from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from core.models.core import CommonMediaFiles
from core.models.people import Clients, Driver
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()


##########  Car Garage Admin #########
@authenticated_staf
@staff_only
def AdminIndexDefaultAppData(request):
    client_count = Clients.objects.all().count()

    driver_count = Driver.objects.all().count()
    cars_image = CommonMediaFiles.objects.filter(type='hero',owner_model=ContentType.objects.get(model='Car'),   ).order_by('-id')[:3]


    context = {

        'client_count': client_count,

        'driver_count': driver_count,
        'cars_image': cars_image,
    }

    return context

