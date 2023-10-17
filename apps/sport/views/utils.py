import os
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.shortcuts import redirect

from apps.event.models.models import EventCategory, Event, Speaker, Sponsor, EventAttendees
from core.models.core import QrCode
from core.models.people import Clients
from core.views.core import AdminCommonQrCode
from digit_sport.settings import MEDIA_ROOT
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


def FrontIndexEventAppData(request):
    event_categories = EventCategory.objects.all()
    events = Event.objects.filter(status='Active').order_by('-id')
    coming_event = Event.objects.filter(status='Active').order_by('-id')
    speakers = Speaker.objects.filter(status='Active').order_by('-id')
    sponsors = Sponsor.objects.filter(status='Active').order_by('-id')

    context = {'event_categories': event_categories, 'events': events, 'coming_event': coming_event,
               'speakers': speakers, 'sponsors': sponsors,

               }

    return context


def CommonEventAttendeesQrImageGenerate(request, slug):
    attendee = EventAttendees.objects.get(slug=slug)
    client = Clients.objects.get(id=attendee.owner_id)
    event = Event.objects.get(id=attendee.receiver_id)
    try:
        qrcode = QrCode.objects.get(owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendee.id)
        qrcode.delete()
    except:
        pass
    try:
        check_qrcode = QrCode.objects.get(barcode_number=attendee.phone)
        if check_qrcode:
            barcode_number = random.randint(100002000002, 9949999399939, )
        else:
            barcode_number = attendee.phone
    except:
        barcode_number = attendee.phone

    AdminCommonQrCode(request,'Event',event.id,'Clients',client.id,  'EventAttendees', attendee.id, attendee.email, attendee.phone, None,
                      attendee.get_absolute_url(), 'event:AdminAttendeesDetails', attendee.slug, None, barcode_number)
    CommonEventEventAttendeesIdCardPrintGenerate(request, slug)
    CommonEventEventAttendeesCertificatePrintGenerate(request, slug)
    return redirect(request.META['HTTP_REFERER'])


def CommonEventEventAttendeesIdCardGenerate(request, slug):
    attendee = EventAttendees.objects.get(slug=slug)
    client = Clients.objects.get(id=attendee.owner_id)
    event = Event.objects.get(id=attendee.receiver_id)
    qrcode = QrCode.objects.get(owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendee.id)
    attendee_image = Image.open(event.card_image)
    try:
        attendee_image.save(f"{MEDIA_ROOT}/event/{event.slug}/id_card/image.jpeg", "jpeg")
    except:
        os.makedirs(f'{MEDIA_ROOT}/event/{event.slug}/id_card')
        attendee_image.save(f"{MEDIA_ROOT}/event/{event.slug}/id_card/image.jpeg", "jpeg")

    image_object = ImageDraw.Draw(attendee_image)
    image_object.text((220, 450), (f'{client.title} {client.first_name}'), fill=(0, 0, 0),
                      font=ImageFont.truetype("static/font/Cairo/static/Cairo-SemiBold.ttf", 90), align="center", )
    image_object.text((365, 550), (f' {client.last_name}'), fill=(0, 0, 0),
                      font=ImageFont.truetype("static/font/Cairo/static/Cairo-SemiBold.ttf", 80), align="center", )
    barcode_image = Image.open(qrcode.barcode_image)
    barcode_image = barcode_image.convert("CMYK")
    barcode_image.save(f"{MEDIA_ROOT}/event/{event.slug}/id_card/new.jpeg", "jpeg")
    attendee_image.paste(barcode_image, (365, 750))
    card_image = attendee_image.save(f'{MEDIA_ROOT}/event/{event.slug}/id_card/{attendee.slug}.jpeg', quality=100)
    attendee_image = Image.open(f'{MEDIA_ROOT}/event/{event.slug}/id_card/{attendee.slug}.jpeg')
    thumb_io = BytesIO()
    attendee_image.save(thumb_io, attendee_image.format, quality=100)
    attendee.card_image.save((f'{MEDIA_ROOT}/event/{event.slug}/id_card/{qrcode.barcode_number}.jpeg'), ContentFile(thumb_io.getvalue()),
                             save=True)
    attendee.save()


def CommonEventEventAttendeesIdCardPrintGenerate(request, slug):
    attendee = EventAttendees.objects.get(slug=slug)
    client = Clients.objects.get(id=attendee.owner_id)
    event = Event.objects.get(id=attendee.receiver_id)
    qrcode = QrCode.objects.get(owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendee.id)

    attendee_image = Image.new('RGB', (1039, 1299), color=(255, 255, 255))
    try:
        attendee_image.save(f"{MEDIA_ROOT}/event/{event.slug}/id_print/image.jpeg", "jpeg")
    except:
        os.makedirs(f'{MEDIA_ROOT}/event/{event.slug}/id_print')
        attendee_image.save(f"{MEDIA_ROOT}/event/{event.slug}/id_print/image.jpeg", "jpeg")

    image_object = ImageDraw.Draw(attendee_image)

    image_object.text((350, 10), (f'{client.title} {client.first_name}'), fill=(0, 0, 0),
                      font=ImageFont.truetype("static/font/Cairo/static/Cairo-SemiBold.ttf", 90), align="center", )
    image_object.text((450, 150), (f' {client.last_name}'), fill=(0, 0, 0),
                      font=ImageFont.truetype("static/font/Cairo/static/Cairo-SemiBold.ttf", 80), align="center", )
    barcode_image = Image.open(qrcode.barcode_image)
    barcode_image = barcode_image.convert("CMYK")
    barcode_image.save(f"{MEDIA_ROOT}/event/{event.slug}/id_print/new.jpeg", "jpeg")
    attendee_image.paste(barcode_image, (365, 325))
    card_image = attendee_image.save(f"{MEDIA_ROOT}/event/{event.slug}/id_print/{attendee.slug}.jpeg", quality=100)
    attendee_image = Image.open(f"{MEDIA_ROOT}/event/{event.slug}/id_print/{attendee.slug}.jpeg")
    thumb_io = BytesIO()
    attendee_image.save(thumb_io, attendee_image.format, quality=100)
    attendee.print_card.save((f"{MEDIA_ROOT}/event/{event.slug}/id_print/{qrcode.barcode_number}.jpeg"), ContentFile(thumb_io.getvalue()),
                             save=True)
    attendee.save()


def CommonEventEventAttendeesCertificatePrintGenerate(request, slug):
    attendee = EventAttendees.objects.get(slug=slug)
    client = Clients.objects.get(id=attendee.owner_id)
    event = Event.objects.get(id=attendee.receiver_id)
    qrcode = QrCode.objects.get(owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendee.id)

    attendee_image = Image.new('RGB', (3008, 2280), color=(255, 255, 255))
    try:
        attendee_image.save(f"{MEDIA_ROOT}/event/{event.slug}/certificate_print/image.jpeg", "jpeg")
    except:
        os.makedirs(f'{MEDIA_ROOT}/event/{event.slug}/certificate_print')
        attendee_image.save(f"{MEDIA_ROOT}/event/{event.slug}/certificate_print/image.jpeg", "jpeg")
    image_object = ImageDraw.Draw(attendee_image)
    image_object.text((1100, 1200), (f'{client.title} {client.first_name} {client.middle_name} {client.last_name}'), fill=(0, 0, 0),
                      font=ImageFont.truetype("static/font/Cairo/static/Cairo-SemiBold.ttf", 120), align="center", )
    att_text = 'Has Participated in the Scientific activities\n of the Conference as one of the attendees'
    image_object.text((900, 1500), (f'{att_text}'),
                      fill=(0, 0, 0),
                      font=ImageFont.truetype("static/font/Cairo/static/Cairo-SemiBold.ttf", 100), align="center", )

    barcode_image = Image.open(qrcode.image)
    barcode_image = barcode_image.convert("CMYK")
    barcode_image.save(f"{MEDIA_ROOT}/event/{event.slug}/certificate_print/new_certificate.jpeg", "jpeg")
    attendee_image.paste(barcode_image, (700, 1900))
    card_image = attendee_image.save(f"{MEDIA_ROOT}/event/{event.slug}/certificate_print/{attendee.slug}.jpeg", quality=100)
    attendee_image = Image.open(f"{MEDIA_ROOT}/event/{event.slug}/certificate_print/{attendee.slug}.jpeg")
    thumb_io = BytesIO()
    attendee_image.save(thumb_io, attendee_image.format, quality=100)
    print('asd')
    attendee.certificate_image.save((f"{MEDIA_ROOT}/event/{event.slug}/certificate_print/{qrcode.barcode_number}.jpeg"), ContentFile(thumb_io.getvalue()),
                             save=True)
    attendee.save()


def CommonEventCertificatePrintGenerate(request, slug):
    event = Event.objects.get(slug=slug)
    attendees= EventAttendees.objects.filter(receiver_model=ContentType.objects.get(model='Event'), receiver_id=event.id)
    for attendee in attendees:
        client = Clients.objects.get(id=attendee.owner_id)
        event = Event.objects.get(id=attendee.receiver_id)
        qrcode = QrCode.objects.get(owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendee.id)


        attendee_image = Image.new('RGB', (3008, 2280), color=(255, 255, 255))
        try:
            attendee_image.save(f"{MEDIA_ROOT}/event/{event.slug}/certificate_print/image.jpeg", "jpeg")
        except:
            os.makedirs(f'{MEDIA_ROOT}/event/{event.slug}/certificate_print')
            attendee_image.save(f"{MEDIA_ROOT}/event/{event.slug}/certificate_print/image.jpeg", "jpeg")

        image_object = ImageDraw.Draw(attendee_image)
        image_object.text((1100, 1200), (f'{client.title} {client.first_name} {client.middle_name} {client.last_name}'),
                          fill=(0, 0, 0),
                          font=ImageFont.truetype("static/font/Cairo/static/Cairo-SemiBold.ttf", 120), align="center", )
        att_text = 'Has Participated in the Scientific activities\n of the Conference as one of the attendees'
        image_object.text((900, 1500), (f'{att_text}'),
                          fill=(0, 0, 0),
                          font=ImageFont.truetype("static/font/Cairo/static/Cairo-SemiBold.ttf", 90), align="center", )

        barcode_image = Image.open(qrcode.image)
        barcode_image = barcode_image.convert("CMYK")
        barcode_image.save(f"{MEDIA_ROOT}/event/{event.slug}/id_print/new_certificate.jpeg", "jpeg")
        attendee_image.paste(barcode_image, (700, 1900))
        card_image = attendee_image.save(f"{MEDIA_ROOT}/event/{event.slug}/certificate_print/{attendee.slug}.jpeg", quality=100)
        attendee_image = Image.open(f"{MEDIA_ROOT}/event/{event.slug}/certificate_print/{attendee.slug}.jpeg")
        thumb_io = BytesIO()
        attendee_image.save(thumb_io, attendee_image.format, quality=100)
        print('asd')
        attendee.certificate_image.save((f"{MEDIA_ROOT}/event/{event.slug}/certificate_print/{qrcode.barcode_number}.jpeg"),
                                        ContentFile(thumb_io.getvalue()),
                                        save=True)
        attendee.save()