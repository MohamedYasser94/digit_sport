import asyncio

import aiohttp
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from fcm_django.models import FCMDevice
from firebase_admin import messaging

from core.models.core import SiteSetting, SystemSetting
from core.models.notifications import Notification, ChatNotification, DeviceInfo

from helper.commonHelper import BACKEND_TEMPLATES

User = get_user_model()


############ Enmail  Notifcation ##################

def notify_admin(request, name, email, phone, subject, message):
    from_email = settings.DEFAULT_EMAIL_FROM
    site_setting = SiteSetting.objects.all()
    for setting in site_setting:
        to_email = setting.email
        subject = subject
        text_content = message
        context = {'title': name, 'email': email, 'phone': phone, 'subject': subject, 'message': message, }
        html_content = render_to_string(f'{BACKEND_TEMPLATES}/utilities/email/notification/email_notify_user.html',
                                        context)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()


def notify_user(request, name, email, phone, subject, message, url, button_text, button_url, button_text2, button_url2):
    site_setting = SiteSetting.objects.all()
    system_setting = SystemSetting.objects.get(status='Active')
    if system_setting.email_host != None or system_setting.email_host != '' or settings.email_user != None or settings.email_user != '' or settings.email_pass != None or settings.email_pass != '' or settings.email_port != None or settings.email_port != '' or settings.email_use_tls != None or settings.email_use_tls != '':
        email_host = system_setting.email_host
        email_user = system_setting.email_user
        email_pass = system_setting.email_pass
        email_port = system_setting.email_port
        email_use_tls = system_setting.email_use_tls
        from_email = email_user
    else:

        from_email = settings.EMAIL_HOST_USER

    subject = subject
    text_content = message
    context = {'title': name, 'email': email, 'phone': phone, 'subject': subject, 'message': message, 'url': url,
        'button_text': button_text, 'button_url': button_url, 'button_text2': button_text2, 'button_url2': button_url2,

    }
    html_content = render_to_string(f'{BACKEND_TEMPLATES}/utilities/email/notification/email_notify_user.html', context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
async def delay_function():
    await asyncio.sleep(1)















############ Dashboard Notifcation ##################

def create_notification_admin(request, to_user, notification_type, extra_id=None, extra_slug=None, extra_info=None,
                              more_info=None, extra_time=None, extra_notify=None):
    notification = Notification.objects.create(to_user=to_user, notification_type=notification_type, is_read=False,
                                               second_read=False, is_confirmed=False, extra_id=extra_id,
                                               extra_slug=extra_slug, extra_info=extra_info, more_info=more_info,
                                               extra_time=extra_time, extra_notify=extra_notify)


def create_notification_vendor(request, to_user, notification_type, court_info=0, extra_id=0, extra_info=0,
                               extra_time=None, extra_notify=None, extra_slug=0):
    notification = Notification.objects.create(to_user=to_user, notification_type=notification_type,
                                               court_info=court_info, extra_time=extra_time, extra_notify=extra_notify,
                                               extra_slug=extra_slug, extra_id=extra_id, extra_info=extra_info)


def notify_vendor(detail, subject, text_content):
    from_email = settings.DEFAULT_EMAIL_FROM
    vendor = User.objects.get(id=detail.vendor.id)
    print('vensor data', detail)

    to_email = vendor.email
    subject = subject
    text_content = text_content
    html_content = render_to_string(f'{BACKEND_TEMPLATES}/notification/email/vendor.html',
                                    {'data': detail, 'vendor': vendor})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()







def FcmNotifications(request,message_title,message_body,image):
    try:
        # user = User.objects.get(slug=slug)
        # print('user', user.id,slug)
        registration_tokens = []
        message = ''
        response = ''
        device_object = DeviceInfo.objects.filter(user_active=True)
        for item in device_object:

            device = FCMDevice.objects.get(registration_id=item.device_token)

            registration_tokens.append(device.registration_id)
            response = messaging.subscribe_to_topic( registration_tokens, 'notify')
            message = messaging.Message(
                notification=messaging.Notification(
                    title=message_title,
                    body=message_body,
                    image=image
                ),
                token=registration_tokens,
            )
        FCMDevice.objects.send_message(message)
        print('Successfully sent message:', response.success_count)

    except Exception as e:
        print('FcmNotifications error', e)