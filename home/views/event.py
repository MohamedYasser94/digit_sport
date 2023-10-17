import asyncio
import re

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Image

from apps.event.forms.forms import AdminEventAttendeesForm
from apps.event.models.models import Event, Speaker, EventAttendees
from apps.event.models.operations import EventSpeakers, EventSponsors
from apps.event.views.utils import CommonEventEventAttendeesIdCardGenerate, \
    CommonEventEventAttendeesIdCardPrintGenerate, CommonEventEventAttendeesCertificatePrintGenerate
from core.models.core import QrCode
from core.models.people import Clients
from core.utils.notification import notify_user_ticket, delay_function
from core.views.core import AdminCommonQrCode
from core.views.people import AdminClientCommonCreate
from digit_sport.settings import MEDIA_ROOT
from helper.modelHelper import Governorates_List
from home.views.views import FRONTEND_TEMPLATES

User = get_user_model()


##########################      Services Admin            ################################


def FrontEventList(request):
    events = Event.objects.filter(status='Active', ).order_by('-id')
    paginator = Paginator(events, 5)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'events': events,
        'page_obj': page_obj,
        'current_page': 'Blog',

    }
    return render(request, f'{FRONTEND_TEMPLATES}/event/event.html', context)

def FrontEventDetails(request, slug):
    event = Event.objects.get(slug=slug)
    speakers = EventSpeakers.objects.filter(owner_model=ContentType.objects.get(model='Event'),
                                                owner_id=event.id)
    sponsors = EventSponsors.objects.filter(owner_model=ContentType.objects.get(model='Event'),
                                                owner_id=event.id)

    context = {
        'event': event,
        'speakers': speakers,
        'sponsors': sponsors,
        'current_page': 'Events',

    }
    return render(request, f'{FRONTEND_TEMPLATES}/event/event-details.html', context)

def FrontEventRegistration(request, slug):
    event = Event.objects.get(slug=slug)
    attendees_form = AdminEventAttendeesForm()
    governorate = Governorates_List
    if request.method == "POST":
        attendees_form = AdminEventAttendeesForm(request.POST or None, request.FILES or None)

        if attendees_form:
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            sign_type = request.POST.get('sign_type')
            phone = request.POST.get('phone')
            title = request.POST.get('title')
            specialty = request.POST.get('specialty')
            country = request.POST.get('country')
            governorates = request.POST.get('governorates')
            national_image = request.FILES.get('national_image')



            confirm_message = _(f'Dear, {title} {first_name} {last_name} \n'
                                f'We have received your request for registration in  {event.title}  \n'
                                f'and will send you an email once your registration is confirmed. \n'

                                f'”Thank you for your interest.”')

            regex = re.compile(r'\d')
            if regex.search(first_name) or regex.search(middle_name) or regex.search(last_name):
                messages.error(request, _("Your Name Must Not Contain Any Number"), extra_tags='Attendees')
                return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration', kwargs={'slug': slug}))

            if email == None or email == '':
                messages.error(request, _("Please Enter Your Email"), extra_tags='Attendees')
                return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration', kwargs={'slug': slug}))
            if phone == None or phone == '':
                messages.error(request, _("Please Enter Your Phone"), extra_tags='Attendees')
                return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration', kwargs={'slug': slug}))

            try:
                attendees_check = EventAttendees.objects.get(email=email,receiver_model=ContentType.objects.get(model='Event'),
                                                             receiver_id=event.id)
                if  attendees_check:
                    qr_code = QrCode.objects.get(owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendees_check.id)

                    notify_user_ticket(request, attendees_check.slug,confirm_message )
                    messages.warning(request,'You Already Registration in This Event,check email for ticket',extra_tags='Attendees')
                    return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration',kwargs={'slug':slug} ))
            except Exception as e:
                pass
            try:
                attendees_check = EventAttendees.objects.get(phone=phone,receiver_model=ContentType.objects.get(model='Event'),
                                                             receiver_id=event.id)
                if attendees_check:
                    notify_user_ticket(request, attendees_check.slug, confirm_message)
                    messages.warning(request,'You Already Registration in This Event,check email for ticket',extra_tags='Attendees')
                    return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration',kwargs={'slug':slug} ))
            except:
                pass

            try:
                client_phone = Clients.objects.get(phone=phone)
                if client_phone:
                    client_phone = Clients.objects.filter(phone=phone,email=email).count()
                    if client_phone <= 0:
                        messages.warning(request, _("this phone not belong to this  email"), extra_tags='Attendees')
                        return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration',kwargs={'slug':slug} ))
                    else:
                        pass
            except Exception as e:
                pass

            try:
                client_object = Clients.objects.get(email=email)

                if client_object:
                    attendees_object = EventAttendees(sender_model=ContentType.objects.get(model='User'),
                                                      sender_id=request.user.id,
                                                      receiver_model=ContentType.objects.get(model='Event'),
                                                      receiver_id=event.id,
                                                      owner_model=ContentType.objects.get(model='Clients'),
                                                      owner_id=client_object.id,
                                                      first_name=client_object.first_name,middle_name=client_object.middle_name,
                                                      last_name=client_object.last_name,
                                                      email=client_object.email, phone=client_object.phone,title=title,
                                                      image=national_image, national_image=national_image,
                                                      specialty=specialty, country=country, governorates=governorates,
                                                      )
                    attendees_object.save()
            except Exception as e:

                event = Event.objects.get(id=event.id)

                client = AdminClientCommonCreate(request, first_name,middle_name, last_name, title, None, None, email,
                                        'Attendees','Active', phone,
                                        None, country, governorates,None, national_image,)
                client_object = Clients.objects.get(email=client.email)
                attendees_object = EventAttendees(sender_model=ContentType.objects.get(model='User'),
                                                  sender_id=request.user.id,
                                                  receiver_model=ContentType.objects.get(model='Event'),
                                                  receiver_id=event.id, owner_model=ContentType.objects.get(model='Clients'),
                                                  owner_id=client_object.id,
                                                  first_name=first_name, last_name=last_name,
                                                   email=email, phone=phone,title=title,
                                                  image=national_image, national_image=national_image,
                                                    specialty=specialty, country=country, governorates=governorates,
                                                  )
                attendees_object.save()
            AdminCommonQrCode(request, 'Event',event.id,'Clients',client_object.id,'EventAttendees',
                              attendees_object.id, attendees_object.email, phone, None,
                              attendees_object.get_absolute_url(), 'event:AdminAttendeesDetails',
                              attendees_object.slug, None,attendees_object.phone)
            qr_code = QrCode.objects.get(owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendees_object.id)
            CommonEventEventAttendeesIdCardGenerate(request, attendees_object.slug)
            CommonEventEventAttendeesIdCardPrintGenerate(request, attendees_object.slug)
            CommonEventEventAttendeesCertificatePrintGenerate(request, attendees_object.slug)




            try:
                asyncio.run(delay_function())
                notify_user_ticket(request, attendees_object.slug, confirm_message)
            except Exception as e:
                notify_user_ticket(request, attendees_object.slug,confirm_message )


            messages.success(request, confirm_message, extra_tags='Attendees')
            return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistrationDone',kwargs={'slug':slug} ))
        else:
            messages.error(request, _("SomeThing Wrong In Your Request , Please Try Again"), extra_tags='Attendees')


    context = {
        'event': event,
        'attendees_form': attendees_form,
        'governorate': governorate,
        'current_page': 'Events',

    }
    return render(request, f'{FRONTEND_TEMPLATES}/event/event-registration.html', context)


def FrontEventRegistrationWithoutEmail(request, slug):
    event = Event.objects.get(slug=slug)
    attendees_form = AdminEventAttendeesForm()
    governorate = Governorates_List
    if request.method == "POST":
        attendees_form = AdminEventAttendeesForm(request.POST or None, request.FILES or None)
        if attendees_form:
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            sign_type = request.POST.get('sign_type')
            phone = request.POST.get('phone')
            specialty = request.POST.get('specialty')
            country = request.POST.get('country')
            governorates = request.POST.get('governorates')
            national_image = request.FILES.get('national_image')
            attendees_object = None

            if email == None or email == '':
                messages.error(request, _("Please Enter Your Email"), extra_tags='Attendees')
                return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration', kwargs={'slug': slug}))

            try:
                attendees_check = EventAttendees.objects.get(email=email)
                if attendees_check:
                    qr_code = QrCode.objects.get(owner_model=ContentType.objects.get(model='EventAttendees'),
                                                 owner_id=attendees_check.id)
                    notify_user_ticket(request, attendees_check.get_full_name(), email, phone,
                                       _(f'your invitation Created in {event.title}'),
                                       f'thank for registration in {event.title} , the event stat in {event.start_date}',
                                       event.get_pub_url(), 'Your Ticket', request._current_scheme_host,
                                       qr_code.barcode_number,
                                       (f'{request._current_scheme_host}{attendees_check.get_card_image()}'))
                    messages.warning(request, 'You Already Registration in This Event,check Your email ', extra_tags='Attendees')
                    return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration', kwargs={'slug': slug}))
            except Exception as e:
                pass

            if phone == None or phone == '':
                messages.error(request, _("Please Enter Your Phone"), extra_tags='Attendees')
                return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration', kwargs={'slug': slug}))
            if sign_type == 'SignIn':
                try:
                    client_check = Clients.objects.get(phone=phone)
                except Exception as e:
                    messages.warning(request, _("Sorry No Record In Website For This Data Please SignUp"),
                                     extra_tags='Attendees')
                    return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration', kwargs={'slug': slug}))

            try:
                attendees_check = EventAttendees.objects.get(phone=phone)
                if attendees_check:
                    qr_code = QrCode.objects.get(owner_model=ContentType.objects.get(model='EventAttendees'),
                                                 owner_id=attendees_check.id)
                    notify_user_ticket(request, attendees_check.get_full_name(), email, phone,
                                       _(f'your invitation Created in {event.title}'),
                                       f'thank for registration in {event.title} , the event stat in {event.start_date}',
                                       event.get_pub_url(), 'Your Ticket', request._current_scheme_host,
                                       qr_code.barcode_number,
                                       (f'{request._current_scheme_host}{attendees_check.get_card_image()}'))
                    messages.warning(request, 'You Already Registration in This Event', extra_tags='Attendees')
                    return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration', kwargs={'slug': slug}))
            except Exception as e:
                pass
            try:
                check_attendees = EventAttendees.objects.get(phone=phone)
                if check_attendees:
                    messages.warning(request, _("You Already Registration in This Event"), extra_tags='Attendees')
                    return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration', kwargs={'slug': slug}))
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
                                                      first_name=client_object.first_name,
                                                      middle_name=client_object.middle_name,
                                                      last_name=client_object.last_name,
                                                      email=client_object.email, phone=client_object.phone,
                                                      image=national_image, national_image=national_image,
                                                      specialty=specialty, country=country, governorates=governorates,
                                                      )
                    attendees_object.save()
            except Exception as e:
                event = Event.objects.get(id=event.id)
                AdminClientCommonCreate(request, first_name, middle_name, last_name, None, None,None, email, None,
                                        'Active', phone,
                                        None, country, governorates, None, national_image, )
                client_object = Clients.objects.get(phone=phone)
                attendees_object = EventAttendees(sender_model=ContentType.objects.get(model='User'),
                                                  sender_id=request.user.id,
                                                  receiver_model=ContentType.objects.get(model='Event'),
                                                  receiver_id=event.id,
                                                  owner_model=ContentType.objects.get(model='Clients'),
                                                  owner_id=client_object.id,
                                                  first_name=first_name, last_name=last_name,
                                                  email=email, phone=phone,
                                                  image=national_image, national_image=national_image,
                                                  specialty=specialty, country=country, governorates=governorates,
                                                  )
                attendees_object.save()
            AdminCommonQrCode(request,'Event',event.id,'Clients',client_object.id, 'EventAttendees', attendees_object.id, attendees_object.email, phone, None,
                              attendees_object.get_absolute_url(), 'event:AdminAttendeesDetails',
                              attendees_object.slug, None, attendees_object.phone)

            qr_code = QrCode.objects.get(owner_model=ContentType.objects.get(model='EventAttendees'),
                                         owner_id=attendees_object.id)
            CommonEventEventAttendeesIdCardPrintGenerate(request, attendees_object.slug)
            CommonEventEventAttendeesCertificatePrintGenerate(request, attendees_object.slug)


            try:
                notify_user_ticket(request, attendees_object.get_full_name(), email, phone,
                                   _(f'your invitation Created in {event.title}'),
                                   f'thank for registration in {event.title} , the event stat in {event.start_date}',
                                   event.get_pub_url(), 'Your Ticket', request._current_scheme_host,
                                   qr_code.barcode_number,
                                   (f'{request._current_scheme_host}{attendees_object.get_card_image()}'))
            except Exception as e:
                notify_user_ticket(request, attendees_object.get_full_name(), email, phone,
                                   _(f'your invitation Created in {event.title}'),
                                   f'thank for registration in {event.title} , the event stat in {event.start_date}',
                                   event.get_pub_url(), 'Your Ticket', request._current_scheme_host,
                                   qr_code.barcode_number,
                                   None)

            messages.success(request, _("Your Registration Request Successfully Created,We Will Send conformation In "
                                        "Mail"), extra_tags='Attendees')
            return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration', kwargs={'slug': slug}))
        else:
            messages.error(request, _("SomeThing Wrong In Your Request , Please Try Again"), extra_tags='Attendees')

    context = {
        'event': event,
        'attendees_form': attendees_form,
        'governorate': governorate,
        'current_page': 'Events',

    }
    return render(request, f'{FRONTEND_TEMPLATES}/event/event-registration.html', context)


def FrontEventRegistrationDone(request,slug):
    event = Event.objects.get(slug=slug)
    context = {
        'event': event,
        'current_page': 'Events',

    }
    return render(request, f'{FRONTEND_TEMPLATES}/event/registration-done.html', context)

def FrontEventPrintId(request,slug):
    attendee = EventAttendees.objects.get(slug=slug)
    event = Event.objects.get(id=attendee.receiver_id)
    doc = SimpleDocTemplate((f"{MEDIA_ROOT}/event/{event.slug}/id_print/card{attendee.code}.pdf"), pagesize=(9 * cm, 11.5 * cm),
                            orientation='portrait',rightMargin=0,leftMargin=0,topMargin=0,bottomMargin=0)

    Story = []
    image = attendee.card_image
    Story.append(Image(image, width=8.5 * cm ,
                       height=11 * cm , hAlign='CENTER',))
    doc.build(Story)
    with open(f"{MEDIA_ROOT}/event/{event.slug}/id_print/card{attendee.code}.pdf", 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=ticket.pdf'
        return response


#########################     Front Speaker List          ################################
def FrontSpeakerList(request,):
    speakers = Speaker.objects.all()
    context = {
        'speakers': speakers,
        'current_page': 'Speakers',

    }
    return render(request, f'{FRONTEND_TEMPLATES}/event/speaker.html', context)


def FrontSpeakerDetails(request, slug):
    context = {
        'current_page': 'Blog',

    }
    return render(request, f'{FRONTEND_TEMPLATES}/event/speaker-details.html', context)