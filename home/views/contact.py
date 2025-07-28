from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt


from core.utils.notification import notify_admin, create_notification_admin
from core.views.notifications import AdminCommonNotifications
from helper.commonHelper import BACKEND_TEMPLATES
from home.views.views import FRONTEND_TEMPLATES
from user.models import User


# Create your views here.

def FrontAbout(request):
    context = {

    }
    return render(request, f'{FRONTEND_TEMPLATES}/contact/about.html', context)


def ContactFront(request):
    users = User.objects.filter(is_superuser=True)
    if request.method == 'GET':
        return render(request, f'{FRONTEND_TEMPLATES}/contact/contact.html', )

    if request.method == 'POST':
        data = Contact()
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()
            # Send Email & Notification
            try:
                for user in users:
                    create_notification_admin(request, user, 'Message', extra_id=data.id, extra_info=data.message)

                notify_admin(data)
                messages.success(request, 'Your message has been sent successfully!')
                messages.success(request, "Yeeew, check it out on the home page!", extra_tags='ContactForm')
            except Exception as e:
                print('email', e)

    form = ContactForm()
    context = {'form': form}

    return redirect(request.META['HTTP_REFERER'], context)


@csrf_exempt
def FrontContactForm(request):
    form = ContactForm(request.POST)

    if request.method == 'POST':

        name = request.POST.get('title')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if form.is_valid():
            contact_object = Contact.objects.create(name=name, email=email, phone=phone, subject=subject,
                                                    message=message)
            contact_object.save()
            messages.success(request, "Thank you for your message, we will get back to you soon!",
                             extra_tags='ContactForm')
            users = User.objects.filter(access_notification=True)
            for user in users:
                AdminCommonNotifications(request, _(f'New Message From Customer'), False, False, False,
                                         _(f'New Message From Customer'), 'Contact', contact_object.id,
                                         _(f'New Message From Customer Subject  {subject}'),
                                         _(f'New Message From Customer Subject  {subject}'), contact_object.create_at,
                                         None, 'Contact', contact_object.id, 'User', user.id, 'Contact',
                                         contact_object.id, 'Contact', contact_object.id)


            else:
                print('error')
                messages.error(request, "Something Wrong ,Please Try Again", extra_tags='ContactForm')

    form = ContactForm()
    context = {'form': form}
    return redirect(request.META['HTTP_REFERER'], context)


def contact_view(request):
    users = User.objects.filter(admin=True)
    if request.method == 'POST':
        data = Contact()

        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            # Send Email & Notification
            try:
                for user in users:
                    create_notification_admin(request, user, 'NewOrder', extra_id=data.id, extra_info=data.message)
                    notify_admin(data)
                    messages.success(request, "Yeeew, check it out on the home page!")
                print('sent')
                print('data', data.email)
            except Exception as e:

                bad_request = Contact.objects.get(id=data.id)
                bad_request.delete()
                messages.error(request, "Yeeew, check it out on the home page!", extra_tags='ContactForm')
            else:
                print('error')
                messages.error(request, "Yeeew, check it out on the home page!", extra_tags='ContactForm')

    form = ContactForm()
    context = {'form': form}
    return redirect(request.META['HTTP_REFERER'], context)


@csrf_exempt
def FrontSendPhoneForm(request):
    form = ContactSendPhoneForm(request.POST)
    if request.method == 'POST':
        phone = request.POST.get('phone')

        if phone.isdigit():
            phone = phone
        else:
            messages.error(request, "ليه كده😒, رقم ياسطي الي هو وان تو ثري ", extra_tags='ContactForm')
            return redirect(request.META['HTTP_REFERER'])
        if phone.startswith('010') or phone.startswith('011') or phone.startswith('012') or phone.startswith('015'):
            phone = phone
        else:
            messages.error(request, "معلش ينجم رقم مصري بس دلوقتي 😎 ", extra_tags='ContactForm')
            return redirect(request.META['HTTP_REFERER'])

        if form:
            contact_object = Contact.objects.create(phone=phone, )
            contact_object.save()
            # Send Email & Notification
            try:
                users = User.objects.all()
                for user in users:
                    AdminCommonNotifications(request, _(f'New Message From Customer'), False, False, False,
                                             _(f'New Message From Customer'), 'Contact', contact_object.id,
                                             _(f'New Message From Customer Subject  {phone}'),
                                             _(f'New Message From Customer Subject  {phone}'), contact_object.create_at,
                                             None, 'Contact', contact_object.id, 'User', user.id, 'Contact',
                                             contact_object.id, 'Contact',
                                             contact_object.id)  # notify_admin(request,name,email, phone, subject, message)
            except Exception as e:
                print('Exception Contact ',
                      e)  # bad_request = Contact.objects.get(id=contact_object.id)  # bad_request.delete()  # messages.error(request, "Yeeew, check it out on the home page!",extra_tags='ContactForm')
            messages.success(request, "متشكرين ينجم 😉 ", extra_tags='ContactForm')

        else:
            pass

            # messages.error(request, "Yeeew, check it out on the home page!", extra_tags='ContactForm')

    form = ContactForm()
    context = {'form': form}
    return redirect(request.META['HTTP_REFERER'], context)


def FrontOurVision(request):
    context = {

    }
    return render(request, f'{FRONTEND_TEMPLATES}/contact/vision.html', context)


def FrontOurPortfolio(request):
    context = {

    }
    return render(request, f'{FRONTEND_TEMPLATES}/contact/portfolio.html', context)

def FrontOurTest(request):
    context = {

    }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/email/ticket/ticket.html', context)

def FrontNewsletterSubscriber(request):
    news_form = NewsletterSubscriberForm(request.POST)
    if request.method == 'POST':
        email = request.POST.get('email')
        if news_form:
            news_object = NewsletterSubscriber(email=email)
            news_object.save()
            messages.success(request, "Thank you for your subscribe,", extra_tags='Subscribe')

        else:

            messages.error(request, "something Wrong , Please Try Again", extra_tags='Subscribe')

    context = {'news_form': news_form}
    return redirect(request.META['HTTP_REFERER'], context)
