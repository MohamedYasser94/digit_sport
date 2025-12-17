from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from core.forms.core import AdminCommonProfileForm, AdminCommonMediaFilesForm
from core.models.core import CommonProfile, CommonMediaFiles
from core.utils.notification import notify_user
from core.views.notifications import AdminCommonNotifications
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only
from user.forms.forms import UserSignUpForm

User = get_user_model()


@authenticated_staf
@staff_only
def AdminEmployeeList(request):
    employees = Employee.objects.all()
    branches = Branch.objects.all()
    if request.method == "POST":
        employee_form = AdminEmployeeForm(request.POST or None, request.FILES or None)
        user_form = UserSignUpForm(request.POST or None, request.FILES or None)

        if employee_form:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            national_id = request.POST.get('national_id')
            role = request.POST.get('role')
            branch = request.POST.get('branch')
            status = request.POST.get('status')

            branch = Branch.objects.get(id=branch)

            try:
                national_id = Employee.objects.get(national_id=national_id)
                if national_id:
                    messages.error(request, _("National ID Already Exist"), extra_tags='Employee')
                    return HttpResponseRedirect(reverse_lazy('press:AdminEmployeeList',))
            except:
                pass
            try:
                email = User.objects.get(email=email)
                if email:
                    messages.error(request, _("Email Already Exist"), extra_tags='Employee')
                    return HttpResponseRedirect(reverse_lazy('press:AdminEmployeeList',))
            except:
                pass
            try:
                check_user = User.objects.get(email=email)

                if check_user:
                    messages.error(request, _("User Already Exist , Try Change User Email"), extra_tags='Employee')
                    return HttpResponseRedirect(reverse_lazy('press:AdminEmployeeList',))
            except Exception as e:

                pass

            random_password = f'RC{get_random_string(5).upper()}AE{get_random_string(5).lower()}MP'
            password = make_password(random_password)
            receiver_model = 'Branch'
            access_level = 'Employee'
            groups = Group.objects.get_or_create(name=access_level)
            groups = Group.objects.get(name=access_level)
            user_object = User.objects.create(email=email, position=role, access_level=access_level, phone=phone,
                                              password=password,
                                              first_name=first_name, last_name=last_name
                                              , is_active='Active', is_staff='Active', is_superuser='Inactive',
                                              access_notification='Active', subscribe='Active', groups=groups)

            user_object.save()

            employee_object = Employee(
                sender_model=ContentType.objects.get(model='User'), sender_id=request.user.id,
                receiver_model=ContentType.objects.get(model=receiver_model), receiver_id=branch.id,
                owner_model=ContentType.objects.get(model='User'), owner_id=user_object.id,
                first_name=first_name, last_name=last_name,company_type='Press', email=email, phone=phone, national_id=national_id,
                role=role, status=status)
            employee_object.save()
            notify_users = User.objects.filter(is_superuser='Active', is_active='Active')
            for user in notify_users:
                AdminCommonNotifications(request, _(f'New Employee Add '), False, False,
                                         False,
                                         _(f'New Employee Add {employee_object.email} In Clinic {branch.title}'),
                                         'Employee', employee_object.slug,
                                         _(f'New Employee Add {employee_object.email} In Clinic {branch.title} with pass {random_password} '),
                                         _(f'Employee Add {employee_object.email} In Clinic {branch.title} '
                                           f'  Employee Add {employee_object.email} In Clinic {branch.title} '),
                                         employee_object.created_at, None, 'User', request.user.id,
                                         'User', user.id, 'Employee', employee_object.id,
                                         'User', user_object.id)

            messages.success(request, _("Employee Add Successfully"), extra_tags='Employee')
            try:
                notify_user(request, first_name, email, phone, _(f'Your Account In System {branch.title}'),
                            f'Account With Mail {email} & Password {random_password}',None,'Your Account','Digithup.com',None,None)
            except:
                pass

            return HttpResponseRedirect(reverse_lazy('press:AdminEmployeeList', ))
        else:
            messages.error(request, _("Employee Not Add , Please Try Again"), extra_tags='Employee')
    else:

        context = {

            'employees': employees,
            'branches': branches,
            'employee_form': AdminEmployeeForm(),
            'profile_form': AdminCommonProfileForm(),
            'media_form': AdminCommonMediaFilesForm(),
            'current_page': _('Employee'),
        }

        return render(request, f'{BACKEND_TEMPLATES}/press/employee/admin.html', context)

    context = {

        'employees': employees,
        'branches': branches,
        'employee_form': AdminEmployeeForm(),
        'profile_form': AdminCommonProfileForm(),
        'media_form': AdminCommonMediaFilesForm(),
        'current_page': _('Employee'),
    }

    return render(request, f'{BACKEND_TEMPLATES}/press/employee/admin.html', context)




@authenticated_staf
@staff_only
def AdminEmployeeDetails(request, slug):
    employee = Employee.objects.get(slug=slug)
    image = CommonMediaFiles.objects.get(
        owner_model=ContentType.objects.get(model='Employee'), owner_id=employee.id)
    profile = CommonProfile.objects.get(
        owner_model=ContentType.objects.get(model='Employee'), owner_id=employee.id)
    try:
        employee_timesheet = EmployeeMonthlyTimesheet.objects.filter(
            receiver_model=ContentType.objects.get(model='Employee'), receiver_id=employee.id)
        employee_transaction = OperationTransaction.objects.filter(
            receiver_model=ContentType.objects.get(model='Employee'), receiver_id=employee.id)
    except:
        employee_timesheet = None
        employee_transaction = None
    context = {
        'employee': employee,
        'image': image,
        'profile': profile,
        'employee_timesheet': employee_timesheet,
        'employee_transaction': employee_transaction,
        'current_page': _('Details'),
        'prev_Page': _('Employee'),
        'prev_Page_link': reverse_lazy('core:AdminEmployeeList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/clinic/employee/details.html', context)


@authenticated_staf
@staff_only
def AdminEmployeeUpdate(request, slug):
    employee = Employee.objects.get(slug=slug)
    branches = Branch.objects.all()

    if request.method == "POST":
        employee_form = AdminEmployeeForm(request.POST or None, request.FILES or None)
        if employee_form:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            national_id = request.POST.get('national_id')
            role = request.POST.get('role')
            hero_image = request.FILES.get('hero_image')
            branch = request.POST.get('branch')
            status = request.POST.get('status')

            branch = Branch.objects.get(id=branch)
            try:
                national_id = Employee.objects.get(national_id=national_id)
                if national_id:
                    messages.error(request, _("National ID Already Exist"), extra_tags='Employee')
                    return HttpResponseRedirect(reverse_lazy('press:AdminEmployeeList',))
            except:
                pass


            employee_object = Employee.objects.get(slug=slug)

            employee_object.first_name = first_name
            employee_object.last_name = last_name
            employee_object.email = email
            employee_object.national_id = national_id
            employee_object.role = role
            if hero_image == None or hero_image == '':
                employee_object.image = employee_object.image
            else:
                employee_object.image = hero_image
            employee_object.status = status
            employee_object.save()


            messages.success(request, _("Employee Add Successfully"), extra_tags='Employee')
            return HttpResponseRedirect(reverse_lazy('press:OwnerEmployeeList',  ))
        else:
            messages.error(request, _("Employee Not Add , Please Try Again"), extra_tags='Employee')
            return HttpResponseRedirect(reverse_lazy('press:OwnerEmployeeUpdate', kwargs={'slug': slug}), )
    context = {
        'employee': employee,
        'branches': branches,
        'employee_form': AdminEmployeeForm(),
        'profile_form': AdminCommonProfileForm(),
        'media_form': AdminCommonMediaFilesForm(),
        'current_page': _('Update'),
        'prev_Page': _('Employee'),
        'prev_Page_link': reverse_lazy('core:AdminEmployeeList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/press/employee/update.html', context)


@authenticated_staf
@staff_only
def AdminEmployeeArchive(request, slug):
    employee = Employee.objects.get(slug=slug)
    if request.method == "POST":
        employee.status = 'Archive'
        messages.success(request, _("Employee Delete Successfully"), extra_tags='Employee')
        return HttpResponseRedirect(reverse_lazy('press:AdminClinicEmployeeList'))



@authenticated_staf
@staff_only
def AdminEmployeeDelete(request, slug):
    employee = Employee.objects.get(slug=slug)
    if request.method == "POST":
        employee.status = 'Archive'
        messages.success(request, _("Employee Delete Successfully"), extra_tags='Employee')
        return HttpResponseRedirect(reverse_lazy('press:AdminClinicEmployeeList'))
