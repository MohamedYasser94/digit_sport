from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from apps.catalog.models.models import Products
from core.models.localization import City
from core.models.shop import OrderItem
from helper.commonHelper import FRONTEND_TEMPLATES

from user.models import UserProfile

User = get_user_model()
################UserProfile##############

def FrontUserProfile(request):
    if not request.user.is_authenticated:
        return redirect('user:CustomerLogin')
    user = User.objects.get(id=request.user.id)
    address = UserProfile.objects.filter(user=user)
    try:
        settings = UserProfile.objects.get(user=user)
    except :
        settings = None
    context = {'user': user,
               'address': address,
               'settings': settings,

               }
    return render(request, f'{FRONTEND_TEMPLATES}/user/profile/profile.html', context)

@login_required(login_url='/login')  # Check login
def FrontLoginUserProfile(request, slug):
    user = User.objects.get(slug=slug)
    address = UserProfile.objects.filter(user=user)
    try:
        settings = UserProfile.objects.get(user=user)
    except :
        settings = None


    context = {'user': user,
               'address': address,
               'settings': settings,

               }
    return render(request, f'{FRONTEND_TEMPLATES}/user/profile/profile.html',context )
def FrontUpdateProfile(request, slug):
    user = User.objects.get(slug=slug)
    address = UserProfile.objects.filter(user=user)
    try:
        settings = UserProfile.objects.get(user=user)
    except :
        settings = None
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, "Profile Updated Successfully")
    context = {'user': user,
               'address': address,
               'settings': settings,

               }
    return render(request, f'{FRONTEND_TEMPLATES}/user/profile/update.html', context)



##########ADress##############

@login_required(login_url='/login')  # Check login
def address_list(request):
    user = User.objects.get(id=request.user.id)
    address = UserProfile.objects.filter(user=user)

    context = {'user': user,
               'address': address,
               }
    return render(request, 'users/dashboard/CustomerProfile.html', context)


@login_required(login_url='/login')  # Check login
def save_address_form(request, form, template_name):
    data = {}
    user = User.objects.get(id=request.user.id)
    address = UserProfile.objects.filter(user=user)
    if request.method == 'POST':

        if form.is_valid():
            form.instance.user = request.user
            form.save()
            data['form_is_valid'] = True
            address = UserProfile.objects.filter(user=user)

            data['html_book_list'] = render_to_string('users/includes/partial_book_list.html', {
                'address': address
            })
        else:
            data['form_is_valid'] = False
            messages.error(request, "Error")
    context = {'form': form, 'address': address}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def load_cities(request):
    governorates_id = request.GET.get('governorates')
    cities = City.objects.filter(governorates_id=governorates_id).order_by('name')
    return render(request, 'users/dashboard/city_dropdown_list_options.html', {'cities': cities})


