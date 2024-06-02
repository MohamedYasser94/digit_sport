import asyncio

import aiohttp
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from fcm_django.models import FCMDevice
from firebase_admin import messaging

from core.models.core import SiteSetting, SystemSetting
from core.models.notifications import Notification, ChatNotification
from core.models.people import Clients
from core.models.shop import Order
from core.models.social import FriendList
from core.utils.whatsapp import WhatsApp
from digit_sport.settings import WhatsApp_TOKEN, WhatsApp_phone_number
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

# Call the delay_function() function from a synchronous function
asyncio.run(delay_function())

# def notify_user_ticket(request, slug, message):
#     attendee = EventAttendees.objects.get(slug=slug)
#     client = Clients.objects.get(id=attendee.owner_id)
#     event = Event.objects.get(id=attendee.receiver_id)
#
#     name = f'Dear, {client.title} {client.first_name} {client.middle_name}'
#     email = client.email
#     phone = client.phone
#     if client.data_confirmed == 'Active':
#         subject = _(f'your invitation Created in {event.title}')
#     else:
#         subject = _(f'your invitation request in {event.title}')
#     message = message
#     url = (f'{request._current_scheme_host}{event.get_pub_url()}')
#     button_text = 'View Event'
#     button_url = (f'{request._current_scheme_host}{event.get_pub_url()}')
#     button_text2 = 'View Ticket'
#     button_url2 = (f'{request._current_scheme_host}{event.get_pub_url()}')
#     image_url = (f'{request._current_scheme_host}{attendee.card_image.url}')
#     ticket_code = attendee.code
#     start_date = event.start_date.strftime('%d,%m,%y')
#     start_time = event.start_time.strftime('%H:%M')
#     Location = event.location
#     map = event.map
#     event_details = event.description
#     event_url = (f'{request._current_scheme_host}{event.get_pub_url()}')
#     print_url = (f'{request._current_scheme_host}{attendee.get_print_url()}')
#
#     site_setting = SiteSetting.objects.all()
#     system_setting = SystemSetting.objects.get(status='Active')
#     if system_setting.email_host != None or system_setting.email_host != '' or settings.email_user != None or settings.email_user != '' or settings.email_pass != None or settings.email_pass != '' or settings.email_port != None or settings.email_port != '' or settings.email_use_tls != None or settings.email_use_tls != '':
#         email_host = system_setting.email_host
#         email_user = system_setting.email_user
#         email_pass = system_setting.email_pass
#         email_port = system_setting.email_port
#         email_use_tls = system_setting.email_use_tls
#         from_email = email_user
#     else:
#
#         from_email = settings.EMAIL_HOST_USER
#
#     subject = subject
#     text_content = message
#     context = {'title': name, 'email': email, 'phone': phone, 'subject': subject, 'message': message, 'url': url,
#         'button_text': button_text, 'button_url': button_url, 'button_text2': button_text2, 'button_url2': button_url2,
#         'image_url': image_url, 'ticket_code': ticket_code, 'start_date': start_date, 'start_time': start_time,
#         'Location': Location, 'map': map, 'event_details': event_details, 'event_url': event_url,'print_url':print_url
#
#     }
#     if client.data_confirmed == 'Active':
#         html_content = render_to_string(f'{BACKEND_TEMPLATES}/utilities/email/ticket/ticket.html', context)
#     else:
#         html_content = render_to_string(f'{BACKEND_TEMPLATES}/utilities/email/ticket/request.html', context)
#     msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
#     msg.attach_alternative(html_content, 'text/html')
#
#     msg.send()


def CommonWhatappNotification(request, name, phone, message):
    messenger = WhatsApp(WhatsApp_TOKEN, phone_number_id=WhatsApp_phone_number)
    # messenger.send_message(title, phone)
    messenger.send_message(message, phone)
    messenger.send_location(lat=1.29, long=103.85, name="Singapore", address="Singapore",
        recipient_id="+201015666808", )

    response = messenger.send_message(

        message=message, recipient_id=phone, )
    print('whatapp response', response)


async def send_whatsapp_message(phone_number, message):
    """Sends a WhatsApp message using asyncio."""
    url = f'https://api.whatsapp.com/send?phone={phone_number}&text={message}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                print('Message sent successfully.')
            else:
                print('Failed to send message.')


async def main():
    """Sends a WhatsApp message using asyncio."""
    phone_number = settings.WHATSAPP_PHONE_NUMBER
    message = 'This is a test message.'
    await send_whatsapp_message(phone_number, message)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


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


def notify_customer(data):
    from_email = settings.DEFAULT_EMAIL_FROM
    data = Order.objects.get(id=data.id)
    to_email = data.email
    subject = 'Order confirmation'
    text_content = 'Thank you for the order!'
    html_content = render_to_string('notify/email_notify_customer.html', {'data': data})
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


def create_notification_chat(request, target, from_user, object_id):
    print('content_type', object_id)
    content = ContentType.objects.get_for_model(FriendList)
    redirect_url = f"{settings.BASE_URL}/profile/{from_user.slug}/",
    verb = f"Sent To Yoy Follow {from_user.email}.",

    notification = ChatNotification.objects.create(target=target, from_user=from_user, content_type=content,
                                                   object_id=object_id, redirect_url=redirect_url, verb=verb,
                                                   read=False)



def FcmNotifications(request,message_title,message_body,image):
    try:
        # user = User.objects.get(slug=slug)
        # print('user', user.id,slug)
        registration_tokens = []
        device = FCMDevice.objects.all()
        for item in device:
            registration_tokens.append(item.registration_id)
        response = messaging.subscribe_to_topic( registration_tokens, 'news')
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