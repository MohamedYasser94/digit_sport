import re
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.event.api.api_views import CreatePdfFromImages
from apps.event.forms.forms import AdminTicketCategoryForm, AdminEventForm, AdminEventAttendeesForm, AdminSpeakerForm, \
    AdminSponsorForm
from apps.event.forms.operations import AdminEventTimeForm
from apps.event.models.models import EventCategory, Event, Speaker, Sponsor, EventAttendees, EventAttendeesHistory
from apps.event.models.operations import EventManagement, EventSpeakers, EventSponsors, EventTime
from apps.event.views.utils import CommonEventEventAttendeesIdCardGenerate, \
    CommonEventEventAttendeesIdCardPrintGenerate, CommonEventEventAttendeesCertificatePrintGenerate
from apps.press.models.models import PressCategory
from core.models import Employee
from core.models.core import QrCode
from core.models.operations import Custody
from core.models.people import Clients
from core.utils.backends import RandomEgyptPhoneGenerator
from core.utils.notification import notify_user_ticket
from core.views.core import AdminCommonQrCode
from core.views.people import AdminClientCommonCreate
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only, superuser_only

User = get_user_model()


##########################      Blog Category Admin            ################################

@authenticated_staf
@staff_only
def AdminEventCategoryList(request):
    categories = EventCategory.objects.all()

    if request.method == "POST":
        category_form = AdminTicketCategoryForm(request.POST or None, request.FILES or None)

        if category_form.is_valid():
            title = request.POST.get('title')
            category_object = EventCategory(title=title, status='Active')

            category_object.save()
            messages.success(request, _("Category Add Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('event:AdminEventCategoryList'))
        else:

            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Category')

    else:
        context = {'categories': categories, 'category_form': AdminTicketCategoryForm(), 'current_page': _('Categories')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/category/admin.html', context)
    context = {'categories': categories, 'category_form': AdminTicketCategoryForm(), 'current_page': _('Categories')

               }
    return render(request, f'{BACKEND_TEMPLATES}/event/category/admin.html', context)


@authenticated_staf
@staff_only
def AdminTicketCategoryUpdate(request, slug):
    category = EventCategory.objects.get(slug=slug)

    if request.method == "POST":
        category_form = AdminTicketCategoryForm(request.POST or None, request.FILES or None, instance=category)

        if category_form.is_valid():
            category_form.save()
            messages.success(request, _("Category Update Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('event:AdminEventCategoryList'))
        else:

            messages.error(request, _("Category Not Update , Please Try Again"), extra_tags='Category')

    else:
        context = {'category': category, 'category_form': AdminTicketCategoryForm(instance=category),
                   'current_page': _('Update'), 'prev_Page': _('Categories'),
                   'prev_Page_link': reverse_lazy('event:AdminEventCategoryList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/category/update.html', context)
    context = {'category': category, 'category_form': AdminTicketCategoryForm(instance=category),
               'current_page': _('Update'), 'prev_Page': _('Categories'),
               'prev_Page_link': reverse_lazy('event:AdminEventCategoryList'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/event/category/update.html', context)


@authenticated_staf
@staff_only
def AdminTicketCategoryDelete(request, slug):
    category = PressCategory.objects.get(slug=slug)

    if request.method == "POST":
        category.delete()

        messages.success(request, _("Category Delete Successfully"), extra_tags='Category')

        return HttpResponseRedirect(reverse_lazy('press:AdminPressCategoriesList'))
    else:
        context = {'category': category,

                   'current_page': _('Delete'), 'prev_Page': _('Categories'),
                   'prev_Page_link': reverse_lazy('event:AdminEventCategoryList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/press/category/delete.html', context)


################################# OwnerPressServicesList ################################

@authenticated_staf
@staff_only
def AdminEventList(request):
    events = Event.objects.filter(status='Active').order_by('-id')
    if request.method == "POST":
        event_form = AdminEventForm(request.POST or None, request.FILES or None)
        if event_form:
            title = request.POST.get('title')
            category = request.POST.get('category')
            description = request.POST.get('description')
            location = request.POST.get('location')
            map = request.POST.get('map')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            session_time = 0
            image = request.FILES.get('image')
            card_image = request.FILES.get('card_image')
            certificate_image = request.FILES.get('certificate_image')
            notes = request.POST.get('notes')

            event_object = Event(title=title, category_id=category, description=description,
                                      location=location, start_date=start_date, end_date=end_date,session_time=session_time,
                                     map=map, image=image,card_image=card_image,certificate_image=certificate_image,notes=notes, status='Active')
            event_object.save()
            event_management = EventManagement(sender_model=ContentType.objects.get(model='User'),
                                                         sender_id=request.user.id,
                                                         owner_model=ContentType.objects.get(model='Event'),
                                                         owner_id=event_object.id, status='Active')

            event_management.save()

            AdminCommonQrCode(request,'Event',event_object.id,'Event',event_object.id, 'Event', event_object.id, event_object.title, None, None,
                              event_object.get_absolute_url(), 'event:AdminEventDetails', event_object.slug,
                              None,None)
            event_object_update = Event.objects.get(id=event_object.id)
            start_date = event_object_update.start_date
            end_date = event_object_update.end_date
            total_time = (end_date - start_date).total_seconds() / 60
            event_object_update.total_time = total_time
            event_object_update.save()
            messages.success(request, _("Event Add Successfully"), extra_tags='Event')
            return HttpResponseRedirect(reverse_lazy('event:AdminEventList'))
        else:
            messages.error(request, _("Event Not Add , Please Try Again"), extra_tags='Event')

    context = {'events': events, 'event_form': AdminEventForm(), 'current_page': _('Event'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/event/event/admin.html', context)


@authenticated_staf
@staff_only
def AdminEventDetails(request, slug):
    event = Event.objects.get(slug=slug)
    attendee_list = []
    attendee_history = None
    total_attendees = EventAttendees.objects.filter(receiver_model=ContentType.objects.get(model='Event'),
                                              receiver_id=event.id, )

    for attendee in total_attendees:
        attendee_history = EventAttendeesHistory.objects.filter(
            owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendee.id).last()
        attendee_list.append({'attendee': attendee, 'attendee_history': attendee_history})
    attendee_lists = list(total_attendees.values('code', 'id'))
    attendee_in = EventAttendees.objects.filter(receiver_model=ContentType.objects.get(model='Event'),
                                                receiver_id=event.id,last_check='CheckIn' ).count()
    attendee_out = EventAttendees.objects.filter(receiver_model=ContentType.objects.get(model='Event'),
                                                    receiver_id=event.id,last_check='CheckOut' ).count()
    attendee_total = EventAttendees.objects.filter(receiver_model=ContentType.objects.get(model='Event'),
                                                receiver_id=event.id).count()
    attendee_abs = attendee_total - attendee_in - attendee_out
    speakers = EventSpeakers.objects.filter(owner_model=ContentType.objects.get(model='Event'),
                                            owner_id=event.id)
    sponsors = EventSponsors.objects.filter(owner_model=ContentType.objects.get(model='Event'),
                                            owner_id=event.id)

    start_date = event.start_date
    end_date = event.end_date
    total_time = end_date - start_date

    context = {'event': event,
                'attendee_list': attendee_list,

               'attendees': total_attendees,
               'attendee_history': attendee_history,
                'attendee_lists': attendee_lists,
                'attendee_in': attendee_in,
                'attendee_out': attendee_out,
                'attendee_abs': attendee_abs,
                'speakers': speakers,
                'sponsors': sponsors,
                'start_date': start_date,
                'end_date': end_date,
                'total_time': total_time,
               'current_page': _('Event'),
               'prev_Page': _('Event'),
               'prev_Page_link': reverse_lazy('event:AdminEventList'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/event/event/details.html', context)


@authenticated_staf
@staff_only
def AdminEventUpdate(request, slug):
    event = Event.objects.get(slug=slug)

    if request.method == "POST":
        event_form = AdminEventForm(request.POST or None, request.FILES or None, instance=event)
        if event_form:
            title = request.POST.get('title')
            category = request.POST.get('category')
            description = request.POST.get('description')
            location = request.POST.get('location')
            map = request.POST.get('map')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            image = request.FILES.get('image')
            card_image = request.FILES.get('card_image')
            certificate_image = request.FILES.get('certificate_image')
            about_image1 = request.FILES.get('about_image1')
            about_image2 = request.FILES.get('about_image2')
            countdown_image = request.FILES.get('countdown_image')
            notes = request.POST.get('notes')
            status = request.POST.get('status')

            start_time = datetime.strptime(start_date, '%Y-%m-%dT%H:%M').strftime("%H:%M")
            end_time = datetime.strptime(end_date, '%Y-%m-%dT%H:%M').strftime("%H:%M")


            event_object = Event.objects.get(slug=slug)
            event_object.title = title
            event_object.category_id = category
            event_object.description = description
            event_object.location = location
            event_object.map = map
            event_object.start_date = start_date
            event_object.end_date = end_date
            event_object.start_time = start_time
            event_object.end_time = end_time

            if image is None or image == '':
                event_object.image = event_object.image
            else:
                event_object.image = image
            if card_image is  None or card_image == '':
                event_object.card_image = event_object.card_image
            else:
                event_object.card_image = card_image
            if certificate_image is None or certificate_image == '':
                event_object.certificate_image = event_object.certificate_image
            else:
                event_object.certificate_image = certificate_image
            if about_image1 is None or about_image1 == '':
                event_object.about_image1 = event_object.about_image1
            else:
                event_object.about_image1 = about_image1
            if about_image2 is None or about_image2 == '':
                event_object.about_image2 = event_object.about_image2
            else:
                event_object.about_image2 = about_image2
            if countdown_image is None or countdown_image == '':
                event_object.countdown_image = event_object.countdown_image
            else:
                event_object.countdown_image = countdown_image
            event_object.notes = notes
            event_object.status = status
            event_object.save()
            event_object_update = Event.objects.get(id=event_object.id)
            start_date = event_object_update.start_date
            end_date = event_object_update.end_date
            total_time = (end_date - start_date).total_seconds() / 60
            event_object_update.total_time = total_time
            event_object_update.save()
            messages.success(request, _("Event Update Successfully"), extra_tags='Event')
            return HttpResponseRedirect(reverse_lazy('event:AdminEventList'))
        else:
            messages.error(request, _("Event Not Update , Please Try Again"), extra_tags='Event')

    else:
        context = {'event': event, 'event_form': AdminEventForm(instance=event), 'current_page': _('Update'),
                   'prev_Page': _('Event'), 'prev_Page_link': reverse_lazy('event:AdminEventList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/event/update.html', context)
    context = {'event': event, 'event_form': AdminEventForm(instance=event), 'current_page': _('Update'),
               'prev_Page': _('Event'), 'prev_Page_link': reverse_lazy('event:AdminEventList'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/event/event/update.html', context)


@authenticated_staf
@staff_only
def AdminEventManagement(request, slug):
    event = Event.objects.get(slug=slug)
    speakers = Speaker.objects.filter(status='Active')
    sponsors = Sponsor.objects.filter(status='Active')
    employees = Employee.objects.filter(status='Active')
    custody = Custody.objects.filter(status='Active')

    context = {'event': event,
               'speakers': speakers,
               'sponsors': sponsors,
               'employees': employees,
               'custody': custody,
               'current_page': _('Management'), 'prev_Page': _('Event'),
               'prev_Page_link': reverse_lazy('event:AdminEventList'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/event/event/management.html', context)


@authenticated_staf
@staff_only
def AdminEventManagementTime(request, slug):
    event = Event.objects.get(slug=slug)

    if request.method == "POST":
        event_form = AdminEventTimeForm(request.POST or None, request.FILES or None)
        if event_form:
            start_date = request.POST.getlist('[start_date]')
            end_date = request.POST.getlist('[end_date]')
            start_time = request.POST.getlist('[start_time]')
            end_time = request.POST.getlist('[end_time]')
            print('Time management',request.POST)
            for s_date, e_date, s_time, e_time in zip(start_date, end_date, start_time, end_time):
                try:
                    event_time_check = EventTime.objects.get(
                                                  owner_model=ContentType.objects.get(model='Event'),
                                                  owner_id=event.id,start_date=s_date, end_date=e_date, )
                    if event_time_check:
                        messages.error(request, _("Event Time Already Exist"), extra_tags='Event')
                        return HttpResponseRedirect(reverse_lazy('event:AdminEventManagementTime', kwargs={'slug': slug}))
                except:
                    pass
            for s_date, e_date, s_time, e_time in zip(start_date, end_date, start_time, end_time):
                s_date = datetime.strptime(s_date, '%Y-%m-%d').strftime("%Y-%m-%d")
                e_date = datetime.strptime(e_date, '%Y-%m-%d').strftime("%Y-%m-%d")
                s_time = datetime.strptime(s_time, '%H:%M').strftime("%H:%M")
                e_time = datetime.strptime(e_time, '%H:%M').strftime("%H:%M")
                if s_date > e_date:
                    messages.error(request, _("Start Date Must Be Less Than End Date"), extra_tags='Event')
                    return HttpResponseRedirect(reverse_lazy('event:AdminEventManagementTime', kwargs={'slug': slug}))
                if s_date != e_date:
                    messages.error(request, _("Start Date Must Be Equal To End Date"), extra_tags='Event')
                    return HttpResponseRedirect(reverse_lazy('event:AdminEventManagementTime', kwargs={'slug': slug}))

                if s_time > e_time:
                    messages.error(request, _("Start Time Must Be Less Than End Time"), extra_tags='Event')
                    return HttpResponseRedirect(reverse_lazy('event:AdminEventManagementTime', kwargs={'slug': slug}))
            for s_date, e_date, s_time, e_time in zip(start_date, end_date, start_time, end_time):
                total_days = (datetime.strptime(e_date, '%Y-%m-%d') - datetime.strptime(s_date, '%Y-%m-%d')).days
                session_time = (datetime.strptime(e_time, '%H:%M') - datetime.strptime(s_time, '%H:%M')).total_seconds() / 3600


                event_time_object = EventTime(sender_model=ContentType.objects.get(model='User'),
                                                sender_id=request.user.id,
                                                owner_model=ContentType.objects.get(model='Event'),
                                                owner_id=event.id,
                                                start_date=s_date, end_date=e_date,total_days=total_days, start_time=s_time, end_time=e_time,session_time=session_time)
                event_time_object.save()
            messages.success(request, _("Event Time Add Successfully"), extra_tags='Event')
            return HttpResponseRedirect(reverse_lazy('event:AdminEventManagementTime', kwargs={'slug': slug}))
        else:
            messages.error(request, _("Event Time Not Add , Please Try Again"), extra_tags='Event')
    context = {'event': event,

               'current_page': _('Time Management'), 'prev_Page': _('Event'),
               'prev_Page_link': reverse_lazy('event:AdminEventList'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/event/event/management_time.html', context)
@authenticated_staf
@staff_only
def AdminEventCheckIn(request, slug):
    event = Event.objects.get(slug=slug)



    context = {
        'event': event,

        'current_page': _('Event'), 'prev_Page': _('Event'),
        'prev_Page_link': reverse_lazy('event:AdminEventList'),

    }

    return render(request, f'{BACKEND_TEMPLATES}/event/event/checkin.html', context)


@authenticated_staf
@staff_only
def AdminEventCheckOut(request, slug):
    event = Event.objects.get(slug=slug)

    context = {'event': event, 'current_page': _('Event'), 'prev_Page': _('Event'),
               'prev_Page_link': reverse_lazy('event:AdminEventList'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/event/event/checkout.html', context)


@authenticated_staf
@staff_only
def AdminEventArchive(request, slug):
    event = Event.objects.get(slug=slug)

    if request.method == "POST":
        event.status = 'Archive'
        event.save()
        messages.success(request, _("Event Archive Successfully"), extra_tags='Event')
        return HttpResponseRedirect(reverse_lazy('event:AdminEventList'))
    else:
        context = {'event': event,

                   'current_page': _('Archive'), 'prev_Page': _('Event'),
                   'prev_Page_link': reverse_lazy('event:AdminEventList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/event/archive.html', context)


@authenticated_staf

@superuser_only
def AdminEventDelete(request, slug):
    event = Event.objects.get(slug=slug)

    if request.method == "POST":
        try:
            event.delete()
            messages.success(request, _("Event Delete Successfully"), extra_tags='Event')
            return HttpResponseRedirect(reverse_lazy('event:AdminEventList'))
        except Exception as e:
            messages.error(request, _(f"Event Not Delete {e} , Please Try Again"), extra_tags='Event')
            return HttpResponseRedirect(reverse_lazy('event:AdminEventList'))
    else:
        messages.error(request, _("Event Not Delete , Please Try Again"), extra_tags='Event')
        redirect(request.META['HTTP_REFERER'])



@authenticated_staf
@staff_only
def AdminEventAttendeesQuickAdd(request,slug):
    event = Event.objects.get(slug=slug)
    attendees = EventAttendees.objects.filter(status='Active')

    if request.method == "POST":
        attendees_form = AdminEventAttendeesForm(request.POST or None, request.FILES or None)

        if attendees_form:
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            title = request.POST.get('title')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            attendees_object = None

            try:
                check_attendees = EventAttendees.objects.get(email=email,receiver_model=ContentType.objects.get(model='Event'),
                                                             receiver_id=event.id)
                if check_attendees:
                    messages.error(request, _("Attendees Already Exist"), extra_tags='Event')
                    return redirect(request.META['HTTP_REFERER'])
            except:
                pass
            try:
                check_attendees = EventAttendees.objects.get(phone=phone,receiver_model=ContentType.objects.get(model='Event'),
                                                             receiver_id=event.id)
                if check_attendees:
                    messages.error(request, _("Attendees Already Exist"), extra_tags='Event')
                    return HttpResponseRedirect(reverse_lazy('event:AdminEventDetails', kwargs={'slug': slug}))
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
                                                      first_name=first_name,middle_name=middle_name, last_name=last_name,
                                                      title=title,email=email, phone=phone,)

                    attendees_object.save()
                    AdminCommonQrCode(request,'Event',event.id,'Clients',client_object.id, 'EventAttendees', attendees_object.id, attendees_object.email, phone,
                                      None,
                                      attendees_object.get_absolute_url(), 'event:AdminAttendeesDetails',
                                      attendees_object.slug, None,phone)
                    CommonEventEventAttendeesIdCardPrintGenerate(request, attendees_object.slug)
                    CommonEventEventAttendeesCertificatePrintGenerate(request, attendees_object.slug)
            except Exception as e:

                event = Event.objects.get(slug=slug)
                AdminClientCommonCreate(request, first_name,middle_name, last_name,title, None, None, email, 'Attendees',
                                        'Active', phone,
                                        None, None, None, None,None)
                client_object = Clients.objects.get(phone=phone)
                attendees_object = EventAttendees(sender_model=ContentType.objects.get(model='User'),
                                                  sender_id=request.user.id,
                                                  receiver_model=ContentType.objects.get(model='Event'),
                                                  receiver_id=event.id, owner_model=ContentType.objects.get(model='Clients'),
                                                  owner_id=client_object.id,
                                                  first_name=first_name,middle_name=middle_name, last_name=last_name,
                                                  title=title,email=email, phone=phone,)

                attendees_object.save()
            AdminCommonQrCode(request,'Event',event.id,'Clients',client_object.id, 'EventAttendees', attendees_object.id, attendees_object.email, phone, None,
                              attendees_object.get_absolute_url(), 'event:AdminAttendeesDetails',
                              attendees_object.slug, None,phone)
            CommonEventEventAttendeesIdCardPrintGenerate(request, attendees_object.slug)
            CommonEventEventAttendeesCertificatePrintGenerate(request, attendees_object.slug)


            messages.success(request, _("Attendees Add Successfully"), extra_tags='Event')
            return HttpResponseRedirect(reverse_lazy('event:AdminEventDetails', kwargs={'slug': slug} ))
        else:
            messages.error(request, _("Attendees Not Add , Please Try Again"), extra_tags='Event')
    context = {'event': event,
               'attendees': attendees,
               'attendees_form': AdminEventAttendeesForm(),
               'current_page': _('Attendees'),
               'prev_Page': _('Event'),
               'prev_Page_link': reverse_lazy('event:AdminEventList'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/event/event/details.html', context)


# try:
#     CommonEventEventAttendeesIdCardPrintGenerate(request, attend.slug)
#     CommonEventEventAttendeesCertificatePrintGenerate(request, attend.slug)
# except:
#     pass
@authenticated_staf
@staff_only
def AdminEventAttendeesList(request, slug):
    event = Event.objects.get(slug=slug)
    # attendees = EventAttendees.objects.filter(receiver_model=ContentType.objects.get(model='Event'),
    #                                           receiver_id=event.id, ).order_by('-id')
    attendees = EventAttendees.objects.filter(receiver_model=ContentType.objects.get(model='Event'),
                                                receiver_id=event.id, ).order_by('first_name', 'middle_name')
    try:
       CreatePdfFromImages(request, slug)
    except Exception as e:
        messages.error(request, _(f"Attendees Not Print {e} , Please Try Again"), extra_tags='Attendees')
    attendees_list = []
    for attend in attendees:

        try:
           qrcode = QrCode.objects.get(owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attend.id)
        except:
            qrcode = None

        attendees_list.append({'attend': attend, 'qrcode': qrcode})

    attendees_form = AdminEventAttendeesForm()
    if request.method == "POST":
        attendees_form = AdminEventAttendeesForm(request.POST or None, request.FILES or None)
        if attendees_form:
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            title = request.POST.get('title')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            national_image = request.FILES.get('national_image')
            notes = request.POST.get('notes')

            regex = re.compile(r'\d')
            if regex.search(first_name) or regex.search(middle_name) or regex.search(last_name):
                messages.error(request, _("Your Name Must Not Contain Any Number"), extra_tags='Attendees')
                return HttpResponseRedirect(reverse_lazy('home:FrontEventRegistration', kwargs={'slug': slug}))

            if email is None or email == '':
                messages.error(request, _("Email Is Required"), extra_tags='Attendees')
                return HttpResponseRedirect(reverse_lazy('event:AdminEventAttendeesList', kwargs={'slug': slug} ))
            if phone is None or phone == '':
                messages.error(request, _("Phone Is Required"), extra_tags='Attendees')
                return HttpResponseRedirect(reverse_lazy('event:AdminEventAttendeesList', kwargs={'slug': slug} ))

            try:
                email = EventAttendees.objects.get(email=email)
                if email:
                    messages.error(request, _("Email Already Exist"), extra_tags='Attendees')
                    return HttpResponseRedirect(reverse_lazy('event:AdminEventAttendeesList', kwargs={'slug': slug} ))
            except:
                pass


            try:
                phone = EventAttendees.objects.get(phone=phone)
                if phone:
                    messages.error(request, _("Phone Already Exist"), extra_tags='Attendees')
                    return HttpResponseRedirect(reverse_lazy('event:AdminEventAttendeesList', kwargs={'slug': slug} ))
            except:
                pass

            event = Event.objects.get(id=event.id)
            AdminClientCommonCreate(request, first_name, middle_name, last_name,title, None, None, email,
                                   'Attendees', 'Active', phone,
                                   None, None, None, None,national_image)
            client_object = Clients.objects.get(phone=phone)

            attendees_object = EventAttendees(sender_model=ContentType.objects.get(model='User'),
                                              sender_id=request.user.id,
                                              receiver_model=ContentType.objects.get(model='Event'),
                                              receiver_id=event.id, owner_model=ContentType.objects.get(model='Clients'),
                                              owner_id=client_object.id,
                                              first_name=first_name, last_name=last_name,
                                               email=email, phone=phone,
                                              national_image=national_image,
                                              notes=notes)
            attendees_object.save()
            AdminCommonQrCode(request,'Event',event.id,'Clients',client_object.id, 'EventAttendees', attendees_object.id, attendees_object.email, phone, None,
                              attendees_object.get_absolute_url(), 'event:AdminAttendeesDetails',
                              attendees_object.slug, None,phone)
            CommonEventEventAttendeesIdCardPrintGenerate(request, attendees_object.slug)
            CommonEventEventAttendeesCertificatePrintGenerate(request, attendees_object.slug)

            messages.success(request, _("Attendees Add Successfully"), extra_tags='Attendees')
            return HttpResponseRedirect(reverse_lazy('event:AdminEventAttendeesList', kwargs={'slug': slug} ))
        else:
            messages.error(request, _("Attendees Not Add , Please Try Again"), extra_tags='Attendees')

    context = { 'event':event,'attendees': attendees_list, 'attendees_form': attendees_form,
               'current_page': _('Attendees'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/event/attendees/admin.html', context)


@authenticated_staf
@staff_only
def AdminEventAttendeesIdCardPrint(request, slug):
    attendee = EventAttendees.objects.get(slug=slug)
    client = Clients.objects.get(id=attendee.owner_id)
    qrcode = QrCode.objects.get(owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendee.id)
    CommonEventEventAttendeesIdCardPrintGenerate(request, slug)
    attendee.id_printed = 'Yes'
    attendee.printed_count = attendee.printed_count + 1
    attendee.save()
    context = {'attendee': attendee,
                    'client': client,
               'qrcode': qrcode,
                  'current_page': _('ID Card'), 'prev_Page': _('Attendees'),
                'prev_Page_link': reverse_lazy('event:AdminEventAttendeesList', kwargs={'slug': slug}),

                }

    return render(request, f'{BACKEND_TEMPLATES}/event/attendees/id_card.html', context)

@authenticated_staf
@staff_only
def AdminEventAttendeesCertificatePrint(request, slug):
    attendee = EventAttendees.objects.get(slug=slug)
    client = Clients.objects.get(id=attendee.owner_id)
    CommonEventEventAttendeesCertificatePrintGenerate(request, slug)
    attendee.certificate_printed = 'Yes'
    attendee.certificate_printed_count = attendee.certificate_printed_count + 1
    attendee.save()
    context = {'attendee': attendee,
                    'client': client,
                  'current_page': _('ID Card'), 'prev_Page': _('Attendees'),
                'prev_Page_link': reverse_lazy('event:AdminEventAttendeesList', kwargs={'slug': slug}),

                }

    return render(request, f'{BACKEND_TEMPLATES}/event/attendees/certificate.html', context)





@authenticated_staf
@staff_only
def AdminEventSpeakersAdd(request, slug):
    event = Event.objects.get(slug=slug)
    speakers = Speaker.objects.filter(status='Active')

    if request.method == "POST":
        speaker_form = AdminSpeakerForm(request.POST or None, request.FILES or None)

        if speaker_form:
            event_speaker = request.POST.getlist('[event_speaker]')
            start_date = request.POST.getlist('[start_date]')
            end_date = request.POST.getlist('[end_date]')
            start_time = request.POST.getlist('[start_time]')
            end_time = request.POST.getlist('[end_time]')

            event_management = EventManagement.objects.get(
                                                         owner_model=ContentType.objects.get(model='Event'),
                                                         owner_id=event.id, )
            for speaker ,st_d,en_d,st_t,en_t in zip(event_speaker,start_date,end_date,start_time,end_time):

                speaker_object = Speaker.objects.get(id=speaker)
                event_speaker = EventSpeakers(sender_model=ContentType.objects.get(model='User'),
                                                sender_id=request.user.id,
                                              receiver_model=ContentType.objects.get(model='Speaker'),
                                                receiver_id=speaker_object.id,
                                                owner_model=ContentType.objects.get(model='Event'),
                                                owner_id=event.id,
                                                start_date=st_d, end_date=en_d,
                                                start_time=st_t, end_time=en_t)

                event_speaker.save()
                messages.success(request, _("Speaker Add Successfully"), extra_tags='Event')

            
            messages.success(request, _("Speaker Add Successfully"), extra_tags='Event')
            return HttpResponseRedirect(reverse_lazy('event:AdminEventDetails', kwargs={'slug': slug}))
        else:
            messages.error(request, _("Speaker Not Add , Please Try Again"), extra_tags='Event')
    context = {'event': event,
                'speakers': speakers,
               'speaker_form': AdminSpeakerForm(),
               'current_page': _('Speaker'),
                'prev_Page': _('Event'),
                'prev_Page_link': reverse_lazy('event:AdminEventList'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/event/event/speaker.html', context)


@authenticated_staf
@staff_only
def AdminEventSponsorsAdd(request, slug):
    event = Event.objects.get(slug=slug)
    sponsors = Sponsor.objects.filter(status='Active')

    if request.method == "POST":
        sponsor_form = AdminSponsorForm(request.POST or None, request.FILES or None)

        if sponsor_form:
            event_sponsor = request.POST.getlist('[event_sponsor]')
            event_location = request.POST.getlist('[event_location]')

            event_management = EventManagement.objects.get(
                owner_model=ContentType.objects.get(model='Event'),
                owner_id=event.id, )
            for sponsor, location, in zip(event_sponsor, event_location):

                sponsor_object = Sponsor.objects.get(id=sponsor)
                event_sponsor = EventSponsors(sender_model=ContentType.objects.get(model='User'),
                                              sender_id=request.user.id,
                                              receiver_model=ContentType.objects.get(model='Sponsor'),
                                              receiver_id=sponsor_object.id,
                                              owner_model=ContentType.objects.get(model='Event'),
                                              owner_id=event.id,
                                              location=location, )

                event_sponsor.save()

            messages.success(request, _("Sponsors Add Successfully"), extra_tags='Event')
            return HttpResponseRedirect(reverse_lazy('event:AdminEventDetails', kwargs={'slug': slug}))
        else:
            messages.error(request, _("Sponsors Not Add , Please Try Again"), extra_tags='Event')
    context = {'event': event,
               'sponsors': sponsors,
               'speaker_form': AdminSponsorForm(),
               'current_page': _('Sponsors'),
               'prev_Page': _('Event'),
               'prev_Page_link': reverse_lazy('event:AdminEventList'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/event/event/sponsor.html', context)


@authenticated_staf
@staff_only
def AdminEventAttendeesDetails(request, slug):
    attendee = EventAttendees.objects.get(slug=slug)
    event = Event.objects.get(id=attendee.receiver_id)
    event_time = EventTime.objects.filter(owner_model=ContentType.objects.get(model='Event'),
                                            owner_id=event.id, )
    attendee_history = EventAttendeesHistory.objects.filter(
        owner_model=ContentType.objects.get(model='EventAttendees'), owner_id=attendee.id,)
    print('attendee_history',attendee_history)
    attendee.days_average = None
    attendee.save()
    day_list= []
    count = event_time.count()
    print('count',count)
    day_count = 0
    average = ''
    for day in event_time :
        day_list.append(day.start_date.strftime("%Y-%m-%d"))
        day_list = list(dict.fromkeys(day_list))
    print('day_list',day_list)
    for day in day_list:
        day = datetime.strptime(day, '%Y-%m-%d').strftime("%d")
        time_get = EventAttendeesHistory.objects.filter(owner_model=ContentType.objects.get(model='EventAttendees'),
                                                            owner_id=attendee.id,
                                                            type='CheckOut',check_in_date__day=day).aggregate(TOTAL=Sum('time_in_spent'))['TOTAL']
        get_event_time = EventTime.objects.get(owner_model=ContentType.objects.get(model='Event'),
                                                owner_id=event.id, start_date__day=day)
        print('time_get',time_get)
        if time_get != None:
            day_count +=1
            average += (f'Time in Day: {day_count} Is {time_get } With Avarage {str(((time_get / (get_event_time.session_time * 60)) * 100))}%')
    attendee.days_average = average
    attendee.save()

    random_phone_number=RandomEgyptPhoneGenerator(request)

    context = {
           'attendee': attendee,
              'attendee_history': attendee_history,

            'random_phone_number':random_phone_number,
               'current_page': _('Details'),
               'prev_Page': _('Event'),
               'prev_Page_link': reverse_lazy('event:AdminEventList'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/event/event/attendee_details.html', context)

################################# Press Addon ################################




@authenticated_staf
@staff_only
def AdminAttendeesDetails(request, slug):
    attendees = EventAttendees.objects.get(slug=slug)
    attendees_history = EventAttendeesHistory.objects.filter(owner_model=ContentType.objects.get(model='Attendees'),
                                                             owner_id=attendees.id)
    context = {'attendees': attendees, 'attendees_history': attendees_history, 'current_page': _('Attendees'),
               'prev_Page': _('Attendees'), 'prev_Page_link': reverse_lazy('event:AdminAttendeesList'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/event/attendees/details.html', context)


@authenticated_staf
@staff_only
def AdminAttendeesUpdate(request, slug):
    attendee = EventAttendees.objects.get(slug=slug)
    client = Clients.objects.get(id=attendee.owner_id)

    event = Event.objects.get(id=attendee.receiver_id)

    if request.method == "POST":
        attendees_form = AdminEventAttendeesForm(request.POST or None, request.FILES or None, instance=attendee)
        if attendees_form:
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            title = request.POST.get('title')
            job_title = request.POST.get('job_title')
            company = request.POST.get('company')
            national_id = request.POST.get('national_id')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            client_type = request.POST.get('client_type')
            country = request.POST.get('country')
            governorates = request.POST.get('governorates')
            city = request.POST.get('city')
            area = request.POST.get('area')
            hero_image = request.FILES.get('hero_image')
            national_image = request.FILES.get('national_image')
            status = request.POST.get('status')

            attendee_object = EventAttendees.objects.get(slug=slug)
            attendee_object.first_name = first_name
            attendee_object.middle_name = middle_name
            attendee_object.last_name = last_name
            attendee_object.title = title
            attendee_object.job_title = job_title
            attendee_object.company = company
            attendee_object.national_id = national_id
            attendee_object.email = email
            attendee_object.phone = phone
            attendee_object.client_type = client_type
            attendee_object.country = country
            attendee_object.governorates = governorates
            attendee_object.city = city
            attendee_object.area = area
            if hero_image == None or hero_image == '':
                attendee_object.image = attendee_object.image
            else:
                attendee_object.image = hero_image
            if national_image == None or national_image == '':
                attendee_object.national_image = attendee_object.national_image
            else:
                attendee_object.national_image = national_image
            attendee_object.status = status

            attendee_object.save()
            client_object = Clients.objects.get(id=attendee_object.owner_id)
            client_object.first_name = first_name
            client_object.middle_name = middle_name
            client_object.last_name = last_name
            client_object.title = title
            client_object.job_title = job_title
            client_object.company = company
            client_object.national_id = national_id
            client_object.email = email
            client_object.phone = phone
            client_object.client_type = client_type
            client_object.country = country
            client_object.governorates = governorates
            client_object.city = city
            client_object.area = area
            if hero_image is not None or hero_image != '':
                client_object.image = hero_image
            else:
                client_object.image = client_object.image
            if national_image is not None or national_image != '':
                client_object.national_image = national_image
            else:
                client_object.national_image = client_object.national_image

            client_object.status = status

            client_object.save()
            messages.success(request, _("Attendees Update Successfully"), extra_tags='Attendees')
            return HttpResponseRedirect(reverse_lazy('event:AdminEventAttendeesList' , kwargs={'slug': event.slug}))
        else:
            messages.error(request, _("Attendees Not Update , Please Try Again"), extra_tags='Attendees')

    context = {'attendee': attendee,'client':client, 'attendees_form': AdminEventAttendeesForm(instance=attendee),
               'current_page': _('Update'), 'prev_Page': _('Attendees'),
               'prev_Page_link': reverse_lazy('event:AdminEventAttendeesList' , kwargs={'slug': event.slug}),

               }
    return render(request, f'{BACKEND_TEMPLATES}/event/attendees/update.html', context)


@authenticated_staf
@staff_only
def AdminAttendeesArchive(request, slug):
    attendees = EventAttendees.objects.get(slug=slug)

    if request.method == "POST":
        attendees.status = 'Archive'
        attendees.save()
        messages.success(request, _("Attendees Archive Successfully"), extra_tags='Attendees')
        return HttpResponseRedirect(reverse_lazy('event:AdminEventAttendeesList' ))
    else:
        context = {'attendees': attendees,

                   'current_page': _('Archive'), 'prev_Page': _('Attendees'),
                   'prev_Page_link': reverse_lazy('event:AdminEventAttendeesList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/attendees/archive.html', context)


@authenticated_staf
@staff_only
def AdminAttendeesDelete(request, slug):
    attendees = EventAttendees.objects.get(slug=slug)
    if request.method == "POST":

        attendees.delete()
        messages.success(request, _("Attendees Delete Successfully"), extra_tags='Attendees')
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect(request.META['HTTP_REFERER'])





##########   Speakers #########

@authenticated_staf
@staff_only
def AdminSpeakersList(request):
    speakers = Speaker.objects.all()

    if request.method == "POST":
        speaker_form = AdminSpeakerForm(request.POST or None, request.FILES or None)

        if speaker_form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            company = request.POST.get('company')
            position = request.POST.get('position')
            image = request.FILES.get('image')
            national_image = request.FILES.get('national_image')
            keywords = request.POST.get('keywords')
            notes = request.POST.get('notes')
            speaker_object = Speaker(first_name=first_name, last_name=last_name, company=company, email=email,
                                     phone=phone, position=position, image=image, national_image=national_image,
                                     keywords=keywords, notes=notes, status='Active')
            speaker_object.save()

            messages.success(request, _("Speaker Add Successfully"), extra_tags='Speaker')
            return HttpResponseRedirect(reverse_lazy('event:AdminSpeakersList'))
        else:
            messages.error(request, _("Speaker Not Add , Please Try Again"), extra_tags='Speaker')

    context = {'speakers': speakers, 'speaker_form': AdminSpeakerForm(), 'current_page': _('Speaker'), }
    return render(request, f'{BACKEND_TEMPLATES}/event/speaker/admin.html', context)


@authenticated_staf
@staff_only
def AdminSpeakersDetails(request, slug):
    speaker = Speaker.objects.get(slug=slug)

    context = {'speaker': speaker, 'current_page': _('Speaker'), 'prev_Page': _('Speaker'),
               'prev_Page_link': reverse_lazy('event:AdminSpeakersList'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/event/speaker/details.html', context)


@authenticated_staf
@staff_only
def AdminSpeakersUpdate(request, slug):
    speaker = Speaker.objects.get(slug=slug)

    if request.method == "POST":
        speaker_form = AdminSpeakerForm(request.POST or None, request.FILES or None, instance=speaker)

        if speaker_form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            company = request.POST.get('company')
            position = request.POST.get('position')
            image = request.FILES.get('image')
            national_image = request.FILES.get('national_image')
            keywords = request.POST.get('keywords')
            notes = request.POST.get('notes')

            speaker_object = Speaker.objects.get(slug=slug)
            speaker_object.first_name = first_name
            speaker_object.last_name = last_name
            speaker_object.company = company
            speaker_object.email = email
            speaker_object.phone = phone
            speaker_object.position = position
            if image is not None or image != '':
                speaker_object.image = image
            else:
                speaker_object.image = speaker.image
            if national_image is not None or national_image != '':
                speaker_object.national_image = national_image
            else:
                speaker_object.national_image = speaker.national_image
            speaker_object.keywords = keywords
            speaker_object.notes = notes
            speaker_object.save()
            messages.success(request, _("Speaker Update Successfully"), extra_tags='Speaker')
            return HttpResponseRedirect(reverse_lazy('event:AdminSpeakersList'))
        else:
            messages.error(request, _("Speaker Not Update , Please Try Again"), extra_tags='Speaker')

    else:
        context = {'speaker': speaker, 'speaker_form': AdminSpeakerForm(instance=speaker), 'current_page': _('Update'),
                   'prev_Page': _('Speaker'), 'prev_Page_link': reverse_lazy('event:AdminSpeakersList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/speaker/update.html', context)
    context = {'speaker': speaker, 'speaker_form': AdminSpeakerForm(instance=speaker), 'current_page': _('Update'),
               'prev_Page': _('Speaker'), 'prev_Page_link': reverse_lazy('event:AdminSpeakersList'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/event/speaker/update.html', context)


@authenticated_staf
@staff_only
def AdminSpeakersArchive(request, slug):
    speaker = Speaker.objects.get(slug=slug)

    if request.method == "POST":
        speaker.status = 'Archive'
        speaker.save()
        messages.success(request, _("Speaker Archive Successfully"), extra_tags='Speaker')
        return HttpResponseRedirect(reverse_lazy('event:AdminSpeakersList'))
    else:
        context = {'speaker': speaker,

                   'current_page': _('Archive'), 'prev_Page': _('Speaker'),
                   'prev_Page_link': reverse_lazy('event:AdminSpeakersList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/speaker/archive.html', context)


@authenticated_staf
@staff_only
def AdminSpeakersDelete(request, slug):
    speaker = Speaker.objects.get(slug=slug)

    if request.method == "POST":
        speaker.delete()

        messages.success(request, _("Speaker Delete Successfully"), extra_tags='Speaker')

        return HttpResponseRedirect(reverse_lazy('event:AdminSpeakersList'))
    else:
        context = {'speaker': speaker,

                   'current_page': _('Delete'), 'prev_Page': _('Speaker'),
                   'prev_Page_link': reverse_lazy('event:AdminSpeakersList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/speaker/delete.html', context)


# ##########   Sponsors #########

@authenticated_staf
@staff_only
def AdminSponsorsList(request):
    sponsors = Sponsor.objects.all()

    if request.method == "POST":
        sponsors_form = AdminSponsorForm(request.POST or None, request.FILES or None)

        if sponsors_form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            company = request.POST.get('company')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            position = request.POST.get('position')
            keywords = request.POST.get('keywords')
            address = request.POST.get('address')
            image = request.FILES.get('image')
            national_image = request.FILES.get('national_image')

            notes = request.POST.get('notes')
            sponsors_object = Sponsor(first_name=first_name, last_name=last_name, company=company, email=email,
                                      phone=phone, keywords=keywords, address=address, image=image,
                                      national_image=national_image, notes=notes,
                                      status='Active')
            sponsors_object.save()

            messages.success(request, _("Sponsor Add Successfully"), extra_tags='Sponsor')
            return HttpResponseRedirect(reverse_lazy('event:AdminSponsorsList'))
        else:
            messages.error(request, _("Sponsor Not Add , Please Try Again"), extra_tags='Sponsor')

    context = {'sponsors': sponsors, 'sponsors_form': AdminSponsorForm(), 'current_page': _('Sponsor'), }
    return render(request, f'{BACKEND_TEMPLATES}/event/sponsor/admin.html', context)


@authenticated_staf
@staff_only
def AdminSponsorsDetails(request, slug):
    sponsors = Sponsor.objects.get(slug=slug)

    context = {'sponsors': sponsors, 'current_page': _('Sponsor'), 'prev_Page': _('Sponsor'),
               'prev_Page_link': reverse_lazy('event:AdminSponsorsList'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/event/sponsor/details.html', context)


@authenticated_staf
@staff_only
def AdminSponsorsUpdate(request, slug):
    sponsor = Sponsor.objects.get(slug=slug)

    if request.method == "POST":
        sponsors_form = AdminSponsorForm(request.POST or None, request.FILES or None, instance=sponsor)

        if sponsors_form.is_valid():
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            company = request.POST.get('company')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            position = request.POST.get('position')
            keywords = request.POST.get('keywords')
            address = request.POST.get('address')
            image = request.FILES.get('image')
            national_image = request.FILES.get('national_image')
            notes = request.POST.get('notes')
            sponsor_object = Sponsor.objects.get(slug=slug)
            sponsor_object.first_name = first_name
            sponsor_object.last_name = last_name
            sponsor_object.company = company
            sponsor_object.email = email
            sponsor_object.phone = phone
            sponsor_object.position = position
            sponsor_object.keywords = keywords
            sponsor_object.address = address
            if image is not None or image != '':
                sponsor_object.image = image
            else:
                sponsor_object.image = sponsor_object.image
            if national_image is not None or national_image != '':
                sponsor_object.national_image = national_image
            else:
                sponsor_object.national_image = sponsor_object.national_image
            sponsor_object.notes = notes
            sponsor_object.save()
            messages.success(request, _("Sponsor Update Successfully"), extra_tags='Sponsor')
            return HttpResponseRedirect(reverse_lazy('event:AdminSponsorsList'))
        else:
            messages.error(request, _("Sponsor Not Update , Please Try Again"), extra_tags='Sponsor')

    else:
        context = {'sponsor': sponsor, 'sponsor_form': AdminSponsorForm(instance=sponsor), 'current_page': _('Update'),
                   'prev_Page': _('Sponsor'), 'prev_Page_link': reverse_lazy('event:AdminSponsorsList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/sponsor/update.html', context)
    context = {'sponsor': sponsor, 'sponsor_form': AdminSponsorForm(instance=sponsor), 'current_page': _('Update'),
               'prev_Page': _('Sponsor'), 'prev_Page_link': reverse_lazy('event:AdminSponsorsList'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/event/sponsor/update.html', context)


@authenticated_staf
@staff_only
def AdminSponsorsArchive(request, slug):
    sponsors = Sponsor.objects.get(slug=slug)

    if request.method == "POST":
        sponsors.status = 'Archive'
        sponsors.save()
        messages.success(request, _("Sponsor Archive Successfully"), extra_tags='Sponsor')
        return HttpResponseRedirect(reverse_lazy('event:AdminSponsorsList'))
    else:
        context = {'sponsors': sponsors,

                   'current_page': _('Archive'), 'prev_Page': _('Sponsor'),
                   'prev_Page_link': reverse_lazy('event:AdminSponsorsList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/sponsor/archive.html', context)


@authenticated_staf
@staff_only
def AdminSponsorsDelete(request, slug):
    sponsors = Sponsor.objects.get(slug=slug)

    if request.method == "POST":
        sponsors.delete()

        messages.success(request, _("Sponsor Delete Successfully"), extra_tags='Sponsor')

        return HttpResponseRedirect(reverse_lazy('event:AdminSponsorsList'))
    else:
        context = {'sponsors': sponsors,

                   'current_page': _('Delete'), 'prev_Page': _('Sponsor'),
                   'prev_Page_link': reverse_lazy('event:AdminSponsorsList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/sponsor/delete.html', context)


# ##########   Event #########

@authenticated_staf
@staff_only
def AdminEventsList(request):
    events = EventCategory.objects.all()

    if request.method == "POST":
        events_form = AdminTicketCategoryForm(request.POST or None, request.FILES or None)

        if events_form.is_valid():
            title = request.POST.get('title')
            category = request.POST.get('category')
            description = request.POST.get('description')
            image = request.FILES.get('image')
            location = request.POST.get('location')
            map = request.POST.get('map')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            notes = request.POST.get('notes')
            status = request.POST.get('status')
            events_object = EventCategory(title=title, category_id=category, description=description, image=image,
                                          location=location, start_date=start_date, end_date=end_date,
                                          start_time=start_time, end_time=end_time, map=map, notes=notes, status=status)
            events_object.save()

            messages.success(request, _("Event Add Successfully"), extra_tags='Event')
            return HttpResponseRedirect(reverse_lazy('event:AdminEventsList'))
        else:
            messages.error(request, _("Event Not Add , Please Try Again"), extra_tags='Event')

    context = {'events': events, 'events_form': AdminTicketCategoryForm(), 'current_page': _('Event'), }
    return render(request, f'{BACKEND_TEMPLATES}/event/event/admin.html', context)


@authenticated_staf
@staff_only
def AdminEventsDetails(request, slug):
    events = EventCategory.objects.get(slug=slug)

    context = {'events': events, 'current_page': _('Event'), 'prev_Page': _('Event'),
               'prev_Page_link': reverse_lazy('event:AdminEventsList'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/event/event/details.html', context)


@authenticated_staf
@staff_only
def AdminEventsUpdate(request, slug):
    events = EventCategory.objects.get(slug=slug)

    if request.method == "POST":
        events_form = AdminTicketCategoryForm(request.POST or None, request.FILES or None, instance=events)

        if events_form.is_valid():
            events_form.save()
            messages.success(request, _("Event Update Successfully"), extra_tags='Event')
            return HttpResponseRedirect(reverse_lazy('event:AdminEventsList'))
        else:
            messages.error(request, _("Event Not Update , Please Try Again"), extra_tags='Event')

    else:
        context = {'events': events, 'events_form': AdminTicketCategoryForm(instance=events),
                   'current_page': _('Update'), 'prev_Page': _('Event'),
                   'prev_Page_link': reverse_lazy('event:AdminEventsList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/event/update.html', context)
    context = {'events': events, 'events_form': AdminTicketCategoryForm(instance=events), 'current_page': _('Update'),
               'prev_Page': _('Event'), 'prev_Page_link': reverse_lazy('event:AdminEventsList'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/event/event/update.html', context)


@authenticated_staf
@staff_only
def AdminEventsArchive(request, slug):
    events = EventCategory.objects.get(slug=slug)

    if request.method == "POST":
        events.status = 'Archive'
        events.save()
        messages.success(request, _("Event Archive Successfully"), extra_tags='Event')
        return HttpResponseRedirect(reverse_lazy('event:AdminEventsList'))
    else:
        context = {'events': events,

                   'current_page': _('Archive'), 'prev_Page': _('Event'),
                   'prev_Page_link': reverse_lazy('event:AdminEventsList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/event/archive.html', context)


@authenticated_staf
@staff_only
def AdminEventsDelete(request, slug):
    events = EventCategory.objects.get(slug=slug)

    if request.method == "POST":
        events.delete()

        messages.success(request, _("Event Delete Successfully"), extra_tags='Event')

        return HttpResponseRedirect(reverse_lazy('event:AdminEventsList'))
    else:
        context = {'events': events,

                   'current_page': _('Delete'), 'prev_Page': _('Event'),
                   'prev_Page_link': reverse_lazy('event:AdminEventsList'),

                   }
        return render(request, f'{BACKEND_TEMPLATES}/event/event/delete.html', context)
