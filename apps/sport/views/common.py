from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from core.models import Employee
from core.models.people import Clients
from core.utils.notification import notify_user

User = get_user_model()

def CommonUserCreate(request, user_type, first_name,middle_name, last_name, email, phone, national_id,company, role, hero_image):
    random_password = f'RD{get_random_string(5).upper()}AH{get_random_string(5).lower()}MP'
    password = make_password(random_password)
    print('random_password', random_password, password)
    access_level = None
    if user_type == 'employee':
        receiver_model = 'Employee'
        is_staff = 'Active'
        access_level = 'Employee'
    elif user_type == 'client':
        receiver_model = 'Clients'
        access_level = 'Client'
        is_staff = 'Inactive'


    groups = Group.objects.get_or_create(name=user_type)
    groups = Group.objects.get(name=user_type)

    user_object = User.objects.create(email=email, position=role, access_level=access_level, phone=phone,
                                      password=password, image=hero_image,
                                      first_name=first_name,middle_name=middle_name, last_name=last_name
                                      , is_active='Active', is_staff=is_staff, is_superuser='Inactive',
                                      access_notification='Inactive', subscribe='Active', groups=groups)

    user_object.save()

    if user_type == 'employee':
        employee_object = Employee(
            sender_model=ContentType.objects.get(model='User'), sender_id=request.user.id,
            owner_model=ContentType.objects.get(model='User'), owner_id=user_object.id,
            first_name=first_name, last_name=last_name, company_type='Other', email=email, phone=phone,
            national_id=national_id,
            role=role, image=hero_image, status='Active')
        employee_object.save()
    elif user_type == 'client':
        client_object = Clients(
            sender_model=ContentType.objects.get(model='User'), sender_id=request.user.id,
            owner_model=ContentType.objects.get(model='User'), owner_id=user_object.id,
            first_name=first_name, last_name=last_name, company=company, email=email, phone=phone,
            image=hero_image, status='Active')
        client_object.save()

    notify_user(request, first_name, email, phone, _(f'Your Account In Xtreme is Created '),
                f'Account With Mail {email} & Password {random_password}', None, 'Your Account', 'xtremeeg.com', None,
                None)