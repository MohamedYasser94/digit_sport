from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect

from core.forms.contact import ContactForm, NewsletterForm
from core.models.services import Contact
from core.utils.notification import notify_admin, create_notification_admin
from Digithup.settings import FRONTEND_TEMPLATES
User = get_user_model()


# Create your views here.


def ContactFront(request):
    users = User.objects.filter(is_superuser=True)
    if request.method == 'POST':
        data = Contact()
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()
            # Send Email & Notification
            try:
                for user in users:
                    create_notification_admin(request, user, 'Message', extra_id=data.id,
                                              extra_info=data.message)

                # notify_admin(data)
                messages.success(request, 'Your message has been sent successfully!')
            except Exception as e:
                print('email',e)

    form = ContactForm()
    context = {'form': form}

    return render(request, f'{FRONTEND_TEMPLATES}/contacts.html', context)


def Newsletter(request):
    if request.method == 'POST':

        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.META['HTTP_REFERER'])


def AboutFront(request):
    return render(request, f'{FRONTEND_TEMPLATES}/about.html', )


def TheTeamFront(request):
    return render(request, f'{FRONTEND_TEMPLATES}/team.html', )


def FAQ(request):
    return render(request, f'{FRONTEND_TEMPLATES}/faq.html', )



