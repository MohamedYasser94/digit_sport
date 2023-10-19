from django.contrib.auth import get_user_model

from apps.sport.models.models import SportCategory
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()


##########  Car Garage Admin #########
@authenticated_staf
@staff_only
def AdminIndexEventAppData(request):
    current_user = User.objects.get(id=request.user.id)
    user_group = User.objects.get(id=request.user.id).groups

    context = {

    }

    return context


def AdminGetCurrentUser(request):
    check_current_user = User.objects.get(id=request.user.id)


def FrontIndexSportAppData(request):
    sport_category = SportCategory.objects.all()


    context = {'sport_category': sport_category,

               }

    return context
