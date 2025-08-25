from django.contrib.auth import get_user_model

from apps.sport.models.models import SportCategory
from helper.decorators import authenticated_staf, staff_only

from django.core.management import call_command
from django.contrib import messages
from django.shortcuts import redirect
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



@staff_only
def trigger_sync_leagues(request):
    """
    A view that triggers the sync_leagues command.
    """
    messages.info(request, "League synchronization has been started. This may take a few moments.")
    # We use threading here so the admin page doesn't hang while the command runs.
    from threading import Thread
    thread = Thread(target=call_command, args=['sync_leagues'], kwargs={})
    thread.start()
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))


@staff_only
def trigger_sync_all_teams(request):
    """
    A view that triggers the sync_all_teams command.
    """
    messages.info(request, "Team synchronization for all leagues has been started. This may take some time.")
    from threading import Thread
    thread = Thread(target=call_command, args=['sync_all_teams'], kwargs={})
    thread.start()
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))


@staff_only
def trigger_sync_fixtures(request):
    """
    A view that triggers the sync_fixtures command.
    """
    messages.info(request, "Fixture synchronization for the next two weeks has been started.")
    from threading import Thread
    # You can customize the days here if you want different buttons in the admin
    thread = Thread(target=call_command, args=['sync_fixtures'], kwargs={'days_past': 7, 'days_future': 14})
    thread.start()
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))
