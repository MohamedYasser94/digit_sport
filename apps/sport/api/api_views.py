import os
from decimal import Decimal as decimal, Decimal
from datetime import datetime
from decimal import Decimal as decimal
import glob
import os
import re
from reportlab.pdfgen import canvas
from django.conf import settings
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, PageBreak
from reportlab.lib.units import inch, cm
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from reportlab.platypus import SimpleDocTemplate
from rest_framework import status

from apps.event.api.serializers import AdminEventAttendeesSerializer
from apps.event.forms.forms import AdminEventAttendeesForm
from apps.event.models.models import Event, EventAttendees, EventAttendeesHistory
from apps.event.models.operations import EventTime
from apps.event.views.utils import CommonEventEventAttendeesIdCardGenerate, \
    CommonEventEventAttendeesIdCardPrintGenerate, CommonEventEventAttendeesCertificatePrintGenerate, \
    CommonEventCertificatePrintGenerate
from core.models.core import QrCode
from core.models.people import Clients
from core.utils.backends import RandomEgyptPhoneGenerator
from core.utils.notification import notify_user_ticket
from core.views.core import AdminCommonQrCode
from core.views.people import AdminClientCommonCreate
from digit_sport.settings import MEDIA_ROOT
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()

@csrf_exempt
def AdminEventAttendeesPrintIdCard(request, slug):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('AdminEventCheckAttendeesPrintIdCard')
    attendee = EventAttendees.objects.get(slug=slug )
    print('attendees', attendee)

    if request.method == 'POST':
        attendee.id_printed = 'Yes'
        attendee.printed_count = attendee.printed_count + 1
        attendee.save()
        attendee = EventAttendees.objects.get(slug=slug)
        serializer = AdminEventAttendeesSerializer(attendee, many=False)

        return JsonResponse(serializer.data, safe=False)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@authenticated_staf
@staff_only
def AdminApiAttendeesHistoryChangeStatus(request, att_num):
    if not request.user.is_authenticated:
        return redirect('core:AdminIndex')
    if request.method == 'POST':
        barcode = None
        attendees = None
        try:
            barcode = QrCode.objects.get(barcode_number=att_num)
            attendees = EventAttendees.objects.get(id=barcode.owner_id)
            event = Event.objects.get(id=attendees.receiver_id)
            event_time = EventTime.objects.filter(owner_model=ContentType.objects.get(model='Event'),owner_id=event.id).order_by('start_date')

            if event_time.count() <=0:
                data = {'type': 'Error', 'name': _(
                    f'You Need To Add Event Time First  \N{smiling face with sunglasses}  ')}
                return JsonResponse(data=data, safe=False)
            if timezone.now().day < event_time.first().start_date.day:
                data = {'type': 'Error', 'name': _(
                    f'Event Not Start Yet  \N{smiling face with sunglasses}  {event_time.first().start_date.strftime("%Y-%m-%d")}')}
                return JsonResponse(data=data, safe=False)
            if timezone.now().day > event_time.last().end_date.day:
                data = {'type': 'Error', 'name': _(
                    f'Event End  \N{smiling face with sunglasses}  {event_time.last().start_date.strftime("%Y-%m-%d")}')}
                return JsonResponse(data=data, safe=False)



            try:
               check_taken_time = EventTime.objects.get(owner_model=ContentType.objects.get(model='Event'),
                                                        owner_id=event.id, start_date__day=timezone.now().day,
                                                        start_date__month=timezone.now().month,start_date__year=timezone.now().year)
               print('timezone.now().day', timezone.now().day)
               print('check_taken_time.start_date.day', check_taken_time.start_date.day)


            except:
                data = {'type': 'Error', 'name': _(f'No Event Running Now  \N{smiling face with sunglasses}  ')}
                return JsonResponse(data=data, safe=False)
            try:
                attendees_history = EventAttendeesHistory.objects.filter(
                    owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendees.id).last()
                if attendees_history.created_at.strftime('%H:%M') == timezone.now().strftime('%H:%M'):
                    data = {'type': 'Error', 'name': _(f'Slow Down  \N{smiling face with sunglasses}  last check is [{attendees_history.type}]')}
                    return JsonResponse(data=data, safe=False)
            except:
                pass

            try:
                attendees_history = EventAttendeesHistory.objects.filter(
                    owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendees.id).last()
                if attendees_history.type == 'CheckIn' and attendees_history.check_in_date.day == timezone.now().day:
                    type = 'CheckOut'
                    check_in_date = attendees_history.check_in_date
                    check_out_date = timezone.now()
                    check_in_time = attendees_history.check_in_time
                    check_out_time =timezone.now().strftime('%H:%M')
                elif attendees_history.type == 'CheckOut' and attendees_history.check_in_date.day != timezone.now().day:
                    type = 'CheckIn'
                    check_in_date = timezone.now()
                    check_out_date = timezone.now()
                    check_in_time = timezone.now().strftime('%H:%M')
                    check_out_time = timezone.now().strftime('%H:%M')
                elif attendees_history.type == 'Early':
                    type = 'CheckIn'
                    check_in_date = timezone.now()
                    check_out_date = attendees_history.check_out_date
                    check_in_time = timezone.now().strftime('%H:%M')
                    check_out_time = attendees_history.check_out_time
                else:
                    type = 'CheckIn'
                    check_in_date = timezone.now()
                    check_out_date = attendees_history.check_out_date
                    check_in_time = timezone.now().strftime('%H:%M')
                    check_out_time = attendees_history.check_out_time
                attendees_object = EventAttendeesHistory(owner_model=ContentType.objects.get(model='EventAttendees'),
                                                         owner_id=attendees.id, check_in_date=check_in_date,
                                                        check_out_date=check_out_date ,  check_in_time=check_in_time,
                                                         check_out_time=check_out_time, type=type, status='Active')
                attendees_object.save()
                attendees.last_check = type
                attendees.save()
                data = {'type': type, 'name': attendees.get_full_name()}
                return JsonResponse(data=data, safe=False)
            except Exception as e:
                print('ownerslug 4', e)
                check_in_date = timezone.now()
                check_in_time = timezone.now().strftime('%H:%M')
                print('check_in_time', check_in_time)
                attendees_history = EventAttendeesHistory(owner_model=ContentType.objects.get(model='EventAttendees'),
                                                          owner_id=attendees.id, type='CheckIn',check_in_date=check_in_date,
                                                          check_in_time=check_in_time, status='Active')
                attendees_history.save()
                attendees.last_check = 'CheckIn'
                attendees.save()
                data = {'type': attendees_history.type, 'name': attendees.get_full_name()}
            return JsonResponse(data=data, safe=False)
        except Exception as e:
            data = {'type':'Error' , 'name': _(f'SomeThing Wrong , {e}')}
            return JsonResponse(data=data, safe=False)
    else:
        data = {'type':'Error' , 'name': _(f'SomeThing Wrong , ')}
        return JsonResponse(data=data, safe=False)


@csrf_exempt
def AdminEventCheckAttendeesTimeAverage(request, slug):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    event = Event.objects.get(slug=slug)
    event_time = EventTime.objects.filter(owner_model=ContentType.objects.get(model='Event'), owner_id=event.id)
    total_time = 0
    time_spent_at_event = 0

    if request.method == 'GET':
        if event_time.count() <= 0:
            data = {'type': 'Error', 'message': _(
                f'You Need To Add Event Time First')}
            return JsonResponse(data=data, safe=False)

        for time in event_time:
            print('time.total_time',time, time.session_time)
            total_time += time.session_time
        attendees = EventAttendees.objects.filter(receiver_model=ContentType.objects.get(model='Event'),
                                             receiver_id=event.id, )
        if attendees.count() <= 0:
            data = {'type': 'Error', 'message': _(
                f'You Need To Add Attendees First')}
            return JsonResponse(data=data, safe=False)



        for attendee in attendees:
            attendee.average_time = 0
            attendee.average = 0
            attendee.days_average = 0
            attendee.save()

        for attendee in attendees:

            attendee_history = EventAttendeesHistory.objects.filter(
                owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendee.id, )
            for history in attendee_history:

                get_event_time = EventTime.objects.get(owner_model=ContentType.objects.get(model='Event'),
                                                       owner_id=event.id, start_date=history.check_in_date.strftime('%Y-%m-%d'),
                                                       )
                if history.check_in_date.day  == get_event_time.start_date.day:
                    try:
                        if history.check_out_time is None and history.check_in_time is not None:
                            if get_event_time.start_date.day == history.check_in_date.day:
                                event_start_date = (get_event_time.start_time.strftime('%H:%M'))
                                print('event_start_date', event_start_date)
                                history_check_in_date = (history.check_in_date.strftime('%H:%M'))
                                print('history_check_in_date', history_check_in_date)
                                first_check_in = (datetime.strptime(history_check_in_date, '%H:%M') - (
                                    datetime.strptime(event_start_date, '%H:%M'))).total_seconds() / 60
                                print('first_check_in', first_check_in)
                                history.time_out_spent = first_check_in
                                history.save()
                                print('first_check_in', first_check_in, 'time_spent_at_event', time_spent_at_event)
                        if history.check_out_time is not None and history.check_in_time is not None :
                            print('history.check_out_time', history.check_out_time)
                            if  history.type == 'CheckOut':
                                history_check_in_date = (history.check_in_date.strftime('%H:%M'))
                                print('history_check_in_date', history_check_in_date)
                                history_check_out_date = (history.check_out_date.strftime('%H:%M'))
                                print('history_check_out_date', history_check_out_date)
                                time_spent_at_event = (datetime.strptime(history_check_out_date, '%H:%M') - (
                                    datetime.strptime(history_check_in_date, '%H:%M'))).total_seconds() / 60
                                print('time_spent_at_event', time_spent_at_event)
                                history.time_in_spent = time_spent_at_event
                                history.save()
                                attendee.average_time += Decimal(time_spent_at_event)
                                attendee.save()

                            elif  history.type == 'CheckIn':
                                history_check_in_date = (history.check_in_date.strftime('%H:%M'))
                                print('history_check_in_date', history_check_in_date)
                                history_check_out_date = (history.check_out_date.strftime('%H:%M'))
                                print('history_check_out_date', history_check_out_date)
                                time_spent_at_event = (datetime.strptime(history_check_in_date, '%H:%M') - (
                                    datetime.strptime(history_check_out_date, '%H:%M'))).total_seconds() / 60
                                print('time_spent_at_event', time_spent_at_event)
                                history.time_out_spent = time_spent_at_event
                                history.save()
                        attendee.average = (attendee.average_time/(total_time*60) )*100
                        print('attendee.average', attendee.average)
                        attendee.save()
                    except Exception as e:
                        data = {'type': 'Error', 'message': _(f'Attendee Error {e} , ')}
                        return JsonResponse(data=data, safe=False)

                else:
                    data = {'type': 'Error', 'message': _(f'Attendee Not Check In , ')}
                    return JsonResponse(data=data, safe=False)
        data = {'type': 'Success', 'message': _(f'Attendee Average , ')}
        return JsonResponse(data=data, safe=False)



@csrf_exempt
def AdminEventAttendeesQuickAddCheckExist(request, mobile_num):
    print('AdminEventAttendeesQuickAddCheckExist')
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'POST':
        mobile_num = request.POST.get('mobile_num')
        event_slug = request.POST.get('event_slug')

        event = Event.objects.get(slug=event_slug)
        try:
            client = Clients.objects.get(phone=mobile_num)
            if client:
                try:
                   attendee = EventAttendees.objects.get(phone=mobile_num, receiver_model=ContentType.objects.get(model='Event'), receiver_id=event.id)
                   if attendee:
                        return JsonResponse({'status': 'Exist', 'message': _(f'Attendee Already Exist')}, safe=False)

                except Exception as e:
                    attendees_object = EventAttendees(sender_model=ContentType.objects.get(model='User'),
                                                      sender_id=request.user.id,
                                                      receiver_model=ContentType.objects.get(model='Event'),
                                                      receiver_id=event.id,
                                                      owner_model=ContentType.objects.get(model='Clients'),
                                                      owner_id=client.id,
                                                      first_name=client.first_name, middle_name=client.middle_name,
                                                      last_name=client.last_name,
                                                      title=client.title, email=client.email, phone=client.phone, )

                    attendees_object.save()
                    AdminCommonQrCode(request, 'Event', event.id, 'Clients', client.id, 'EventAttendees',
                                      attendees_object.id, attendees_object.email, client.phone, None,
                                      attendees_object.get_absolute_url(), 'event:AdminAttendeesDetails',
                                      attendees_object.slug, None, client.phone)

                    CommonEventEventAttendeesIdCardPrintGenerate(request, attendees_object.slug)
                    CommonEventEventAttendeesCertificatePrintGenerate(request, attendees_object.slug)
                    return JsonResponse({'status': 'NotExistButAdd', 'message': _(f'Attendee Not Exist but Add Now For This Event')}, safe=False)
        except Exception as e:

            return JsonResponse({'status': 'NotExist', 'message': _(f'Client Not Exist, {e}')}, safe=False)

@csrf_exempt
def AdminEventAttendeesQuickAddForm(request, slug):
    print('AdminEventAttendeesQuickAddCheckExist')
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('AdminEventAttendeesQuickAddForm')

    if request.method == "POST":
        print('request.POST',)
        attendees_form = AdminEventAttendeesForm(request.POST or None, request.FILES or None)

        if attendees_form:
            event_slug = request.POST.get('event_slug')
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            title = request.POST.get('title')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            attendees_object = None

            regex = re.compile(r'\d')
            if regex.search(first_name) or regex.search(middle_name) or regex.search(last_name):
                messages.error(request, _("Your Name Must Not Contain Any Number"), extra_tags='Event')
                return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration', kwargs={'slug': slug}))

            if phone == None or phone == '':
                phone=  RandomEgyptPhoneGenerator(request)
            else:
                phone = phone
            event = Event.objects.get(slug=event_slug)


            try:
                check_attendees = EventAttendees.objects.get(email=email,
                                                             receiver_model=ContentType.objects.get(model='Event'),
                                                             receiver_id=event.id)
                if check_attendees:
                    messages.error(request, _("Attendees Already Exist"), extra_tags='Event')
                    return JsonResponse({'status': 'Error', 'message': _(f'Attendees Already Exist Form')},
                                        safe=False)
            except:
                pass
            try:
                check_attendees = EventAttendees.objects.get(phone=phone,
                                                             receiver_model=ContentType.objects.get(model='Event'),
                                                             receiver_id=event.id)
                if check_attendees:
                    messages.error(request, _("Attendees Already Exist"), extra_tags='Event')
                    return JsonResponse({'status': 'Error', 'message': _(f'Attendees Already Exist Form')},
                                        safe=False)
            except:
                pass
            try:
                client_object = Clients.objects.get(phone=phone)

                if client_object:
                    attendees_object = EventAttendees(sender_model=ContentType.objects.get(model='User'),
                                                      sender_id=request.user.id,
                                                      receiver_model=ContentType.objects.get(model='Event'),
                                                      receiver_id=event.id,
                                                      owner_model=ContentType.objects.get(model='Clients'),
                                                      owner_id=client_object.id,
                                                      first_name=first_name, middle_name=middle_name,
                                                      last_name=last_name,
                                                      title=title, email=email, phone=phone, )

                    attendees_object.save()
                    AdminCommonQrCode(request, 'Event', event.id, 'Clients', client_object.id, 'EventAttendees',
                                      attendees_object.id, attendees_object.email, phone,
                                      None,
                                      attendees_object.get_absolute_url(), 'event:AdminAttendeesDetails',
                                      attendees_object.slug, None, phone)
                    print('com 1')
                    CommonEventEventAttendeesIdCardPrintGenerate(request, attendees_object.slug)
                    CommonEventEventAttendeesCertificatePrintGenerate(request, attendees_object.slug)

                    messages.success(request, _("Attendees Add Successfully"), extra_tags='Event')
                    return JsonResponse({'status': 'Success', 'message': _(f'Client Exist Attendees Add Successfully')}, safe=False)
            except Exception as e:
                event = Event.objects.get(slug=event_slug)
                AdminClientCommonCreate(request, first_name, middle_name, last_name, title, None, None, email,
                                        'Attendees',
                                        'Active', phone,
                                        None, None, None, None, None)
                client_object = Clients.objects.get(phone=phone)
                attendees_object = EventAttendees(sender_model=ContentType.objects.get(model='User'),
                                                  sender_id=request.user.id,
                                                  receiver_model=ContentType.objects.get(model='Event'),
                                                  receiver_id=event.id,
                                                  owner_model=ContentType.objects.get(model='Clients'),
                                                  owner_id=client_object.id,
                                                  first_name=first_name, middle_name=middle_name, last_name=last_name,
                                                  title=title, email=email, phone=phone, )

                attendees_object.save()
            AdminCommonQrCode(request, 'Event', event.id, 'Clients', client_object.id, 'EventAttendees',
                              attendees_object.id, attendees_object.email, phone, None,
                              attendees_object.get_absolute_url(), 'event:AdminAttendeesDetails',
                              attendees_object.slug, None, phone)
            print('com 2')
            CommonEventEventAttendeesIdCardPrintGenerate(request, attendees_object.slug)
            CommonEventEventAttendeesCertificatePrintGenerate(request, attendees_object.slug)


            messages.success(request, _("Attendees Add Successfully"), extra_tags='Event')
            return JsonResponse({'status': 'Success', 'message': _(f'Attendees Add Successfully')}, safe=False)
        else:
            return JsonResponse({'status': 'Error', 'message': _(f'SomeThing Wrong')}, safe=False)



def CreatePdfFromImages(request,slug):
    event = Event.objects.get(slug=slug)
    # CommonEventCertificatePrintGenerate(request, event.slug)
    attendees= EventAttendees.objects.filter(receiver_model=ContentType.objects.get(model='Event'), receiver_id=event.id).order_by('first_name', 'middle_name')
    try:
        os.makedirs(f'{MEDIA_ROOT}/event/{event.slug}/certificate')
        doc = SimpleDocTemplate((f'{MEDIA_ROOT}/event/{event.slug}/certificate/certificate.pdf'),pagesize=(29 *cm ,19 * cm),orientation='landscape')
    except:
        doc = SimpleDocTemplate((f'{MEDIA_ROOT}/event/{event.slug}/certificate/certificate.pdf'),pagesize=(29 *cm ,19 * cm),orientation='landscape')

    Story=[]
    for infile in attendees:
        infile = infile.certificate_image
        im = Image(infile, 666,382, hAlign='CENTER', mask='auto')

        Story.append(im)
        Story.append(PageBreak())
    doc.build(Story)
    with open(f'{MEDIA_ROOT}/event/{event.slug}/certificate/certificate.pdf', 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=certificate.pdf'
        return response



@csrf_exempt
def AdminEventAttendeesSentConfirmedMail(request, slug):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == "POST":
        attendee = EventAttendees.objects.get(slug=slug)
        client = Clients.objects.get(id=attendee.owner_id)
        event = Event.objects.get(id=attendee.receiver_id)
        if client.data_confirmed == 'Active':

            confirm_message = _(f'Dear, {client.title} {client.first_name} {client.last_name} \n'
                                f'We have send to you to confirm in event : {event.title}  \n'
                                f'we hope to enjoy good time. \n'
                                f'”Thank you for your interest.”')
            notify_user_ticket(request, attendee.slug, confirm_message)
            attendee.mail_send = 'Yes'
            attendee.mail_send_count += 1
            attendee.save()
            return JsonResponse({'status': 'Success', 'message': _(f'Email Sent Successfully')}, safe=False)
        else:

            return JsonResponse({'status': 'Error', 'message': _(f'Attendees Not Confirmed')}, safe=False)
    else:
        return JsonResponse({'status': 'Error', 'message': _(f'SomeThing Wrong')}, safe=False)