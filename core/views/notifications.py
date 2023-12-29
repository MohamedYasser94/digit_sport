from datetime import datetime

import firebase_admin
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from fcm_django.models import FCMDevice
from firebase_admin import messaging, credentials
from firebase_admin.messaging import Notification

from core.models.notifications import Notification
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()






def send_message(request):
    current_user = request.user  # Getting current user
    channel_layer = get_channel_layer()
    data = "notification" + "...." + str(datetime.now())  # Pass any data based on your requirement
    # Trigger message sent to group
    async_to_sync(channel_layer.group_send)(
        str(current_user.pk),  # Group Name, Should always be string
        {
            "type": "notify",  # Custom Function written in the consumers.py
            "text": data,
        },
    )

    #
    # # Send message logic here...
    # user_channel_name = get_user_channel_name(request.user.id)
    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(
    #     user_channel_name,
    #     {
    #         "type": "notification_message",
    #         "message": 'message_text'
    #     }
    # )






@authenticated_staf
@staff_only
def AdminNotificationslist(request):
    notifications = Notification.objects.filter( receiver_model=ContentType.objects.get(model='User'),
                                                    receiver_id=request.user.id).order_by('-created_at')


    return render(request, f'{BACKEND_TEMPLATES}/notification/notifications.html', {'notifications': notifications})
@authenticated_staf
@staff_only
def AdminNotificationsDetails(request,slug):
    notification = Notification.objects.get(slug=slug)
    notification.is_read = True
    notification.save()
    domain = Site.objects.get_current().domain
    path = notification.owner.get_absolute_url()
    url = '{domain}{path}'.format(domain=domain, path=path)
    print('url', url)
    return HttpResponseRedirect(url)



def AdminFcmNotifications(request):
    devices = FCMDevice.objects.all()
    print('AdminFcmNotifications')
    for device in devices:
        print('devices',device)
        message = messaging.Message(
            data={
                'title': 'Hello',
                'body': 'World',
            },
            token=device.registration_id,
        )
        response = messaging.send(message)
        print('Successfully sent message:', response)
    return HttpResponse(status=200)
    #     return redirect('admin_fcm_notifications')
    # return render(request, f'{BACKEND_TEMPLATES}/notification/fcm_notifications.html')






@login_required
def vendor_notifications(request):
    if request.user.is_authenticated and request.user.seller:
        goto = request.GET.get('goto', '')
        notification_id = request.GET.get('notification', 0)
        extra_id = request.GET.get('extra_id', 0)
        notification_list = Notification.objects.filter(is_read=False)
        page = request.GET.get('page', 1)

        paginator = Paginator(notification_list, 10)
        try:
            notifications = paginator.page(page)
        except PageNotAnInteger:
            notifications = paginator.page(1)
        except EmptyPage:
            notifications = paginator.page(paginator.num_pages)

        if goto != '':
            notification = Notification.objects.get(pk=notification_id)
            notification.is_read = True
            notification.save()
            if notification.notification_type in [
                Notification.MESSAGE,
                Notification.APPLICATION,
                Notification.NewOrder,
                Notification.NewRegistration,
                Notification.NewVendorCreate,
            ]:
                return redirect('view_application', application_id=notification.extra_id)
        return render(request, 'notification/vendor_notifications.html', {'notifications': notifications})


@login_required
def shipping_notifications(request):
    if request.user.is_authenticated and request.user.deliver:
        goto = request.GET.get('goto', '')
        notification_id = request.GET.get('notification', 0)
        extra_id = request.GET.get('extra_id', 0)
        notification_list = Notification.objects.filter(is_read=False)
        page = request.GET.get('page', 1)

        paginator = Paginator(notification_list, 10)
        try:
            notifications = paginator.page(page)
        except PageNotAnInteger:
            notifications = paginator.page(1)
        except EmptyPage:
            notifications = paginator.page(paginator.num_pages)

        if goto != '':
            notification = Notification.objects.get(pk=notification_id)
            notification.is_read = True
            notification.save()
            if notification.notification_type in [
                Notification.MESSAGE,
                Notification.APPLICATION,
                Notification.NewOrder,
                Notification.NewRegistration,
                Notification.NewVendorCreate,
            ]:
                return redirect('view_application', application_id=notification.extra_id)
        return render(request, 'notification/shipping_notifications.html', {'notifications': notifications})



def AdminCommonNotifications(request, notification_type, is_read, second_read, is_confirmed, notification,
                             notification_url,notification_slug, notification_info,
                             notification_desc, notification_time, notification_notify, sender_model, sender_id,
                             receiver_model, receiver_id, owner_model, owner_id, auditor_model, auditor_id):
    print('notification_type')
    notification_object= Notification(notification_type=notification_type, is_read=is_read, second_read=second_read,
                                       is_confirmed=is_confirmed, notification=notification,
                                       notification_url=notification_url,notification_slug=notification_slug, notification_info=notification_info,
                                       notification_desc=notification_desc, notification_time=notification_time,
                                       notification_notify=notification_notify, sender_model=ContentType.objects.get(model=sender_model),
                                       sender_id=sender_id, receiver_model=ContentType.objects.get(model=receiver_model), receiver_id=receiver_id,
                                       owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id, auditor_model=ContentType.objects.get(model=auditor_model),
                                       auditor_id=auditor_id)
    notification_object.save()
    # return (notification_object.receiver_id,notification_object.notification_type)


@login_required
def chat_notifications(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('/')
    goto = request.GET.get('goto', '')
    notification_id = request.GET.get('notification', 0)
    extra_id = request.GET.get('extra_id', 0)
    notification_list = Notification.objects.filter(is_read=False, to_user=request.user)
    page = request.GET.get('page', 1)

    paginator = Paginator(notification_list, 10)
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)

    if goto != '':
        notification = Notification.objects.get(pk=notification_id)
        notification.is_read = True
        notification.save()
        if notification.notification_type in [
            Notification.MESSAGE,
            Notification.APPLICATION,
            Notification.NewRegistration,
            notification.NewCasesCreate,
            notification.CasesUpdate,

            notification.NoteCasesCreate,
            notification.CasesRemember,
            notification.CasesArchive,

        ]:
            return redirect('view_application', application_id=notification.extra_id)
    return render(request, f'{BACKEND_TEMPLATES}/notification/notifications.html', {'notifications': notifications})
