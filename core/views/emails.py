from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from core.models.email import Email
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import staff_only, authenticated_staf
User = get_user_model()
UserModel = get_user_model()




################# Inbox ########################
@authenticated_staf
@staff_only
def AdminEmailList(request, slug):
    user = User.objects.get(slug=slug)
    emails = Email.objects.filter(owner_model=ContentType.objects.get(model='User'), owner_id=user.id)


    context = {
        'current_user': user,
        'emails': emails,

    }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/email/inbox.html', context)


@authenticated_staf
@staff_only
def AdminUserComposeEmail(request, slug):
    user = User.objects.get(slug=slug)
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        email = Email.objects.create(
            owner_model=ContentType.objects.get(model='User'),
            owner_id=user.id,
            subject=subject,
            message=message,
            sender=request.user,
            receiver=user
        )
        email.save()
        return redirect('home:AdminEmailList', slug=slug)



    context = {
        'current_user': user,

    }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/email/compose.html', context)


@authenticated_staf
@staff_only
def AdminDetailsEmail(request):
    user = User.objects.all()

    context = {
        'current_user': user,

    }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/inbox/details.html', context)