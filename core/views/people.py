from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


from apps.wallet.models.models import SystemWallet
from apps.wallet.models.transaction import OperationTransaction, OperationTransactionHistory, TreasuryTransactions, \
    OperationTransactionAccounts
from apps.wallet.views.common_transaction import AdminCommonOperationTransactionHistory, \
    AdminCommonOperationTransaction
from core.forms.people import AdminClientsForm, AdminDriverForm, AdminEmployeeForm, AdminEmployeeSalaryrForm, \
    AdminTeamForm, AdminTeamSkillForm, AdminBranchForm
from core.forms.core import AdminCommonProfileForm, AdminCommonMediaFilesForm, AdminCommonSocialLinkForm
from core.models.people import Clients, Driver, Contract, ContractTerms, Employee, EmployeeSalary, \
    EmployeeMonthlyTimesheet, Team, TeamSkill, Branch
from core.models.core import CommonProfile, CommonMediaFiles, CommonSocialLink
from core.models.localization import Country, City, Governorates, Area
from core.utils.backends import RandomEmailAddressGenerator
from core.views.billing import common_invoice
from core.views.core import AdminCommonProfile, AdminCommonMediaHeroFiles, AdminCommonSocialLink, AdminCommonSeo
from core.views.notifications import AdminCommonNotifications
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()


@authenticated_staf
@staff_only
def AdminClientList(request):
    clients = Clients.objects.all()

    if request.method == "POST":
        client_form = AdminClientsForm(request.POST or None, request.FILES or None)


        if client_form:
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            title = request.POST.get('title')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            country = request.POST.get('country')
            governorates = request.POST.get('governorates')
            job_title = request.POST.get('job_title')

            try:
                check_client = Clients.objects.get(email=email)
                if check_client:
                    messages.error(request, "Email Already Exist")
                    return HttpResponseRedirect(reverse_lazy('core:AdminClientList'))
            except:
                pass
            try:
                check_client = Clients.objects.get(phone=phone)
                if check_client:
                    messages.error(request, "Phone Already Exist")
                    return HttpResponseRedirect(reverse_lazy('core:AdminClientList'))
            except:
                pass


            client_object = Clients(first_name=first_name,middle_name=middle_name,last_name=last_name,title=title,  email=email,
                                  client_type='Attendees',  phone=phone,   country=country,governorates=governorates,job_title=job_title,
                                  status='Active')
            client_object.save()
            messages.success(request, _("Clients Add Successfully"), extra_tags='Clients')
            return HttpResponseRedirect(reverse_lazy('core:AdminClientList'))
        else:
            messages.error(request, _("Clients Not Add , Please Try Again"), extra_tags='Clients')
    else:

        context = {
            'clients': clients,
            'client_form': AdminClientsForm(),
            'current_page': _('Clients')
        }
        return render(request, f'{BACKEND_TEMPLATES}/people/client/admin.html', context)
    context = {
        'clients': clients,
        'client_form': AdminClientsForm(),
        'current_page': _('Clients')

    }
    return render(request, f'{BACKEND_TEMPLATES}/people/client/admin.html', context)


def AdminClientCommonCreate(request, first_name,middle_name,last_name,title, company, national_id, email, client_type, status, phone,
                            address, country, governorates,  hero_image,national_image):
    if email == None or email == '':
        email =RandomEmailAddressGenerator(request)
    else:
        email = email




    client = Clients(first_name=first_name,middle_name=middle_name,last_name=last_name,title=title, company=company, national_id=national_id, email=email,
                     client_type=client_type,
                     phone=phone,  address=address, country=country,governorates=governorates, image=hero_image,national_image=national_image,
                     status=status)
    client.save()

    return client

@authenticated_staf
@staff_only
def AdminClientDetail(request, slug):
    client = Clients.objects.get(slug=slug)
    context = {
        'people': client,
        'current_page': _('Details'),
        'prev_Page': _('Clients'),
        'prev_Page_link': reverse_lazy('core:AdminClientList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/people/client/details.html', context)




@authenticated_staf
@staff_only
def AdminClientUpdate(request, slug):
    client = Clients.objects.get(slug=slug)

    if request.method == "POST":
        client_form = AdminClientsForm(request.POST or None, request.FILES or None)
        profile_form = AdminCommonProfileForm(request.POST or None, request.FILES or None)
        media_form = AdminCommonMediaFilesForm(request.POST or None, request.FILES or None)

        if client_form:

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
            data_confirmed = request.POST.get('data_confirmed')
            status = request.POST.get('status')


            client_object = Clients.objects.get(slug=slug)
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
            client_object.data_confirmed = data_confirmed
            client_object.status = status
            client_object.save()

            messages.success(request, _("Clients Update Successfully"), extra_tags='Clients')

            return HttpResponseRedirect(reverse_lazy('core:AdminClientList'))

        else:
            messages.error(request, _("Clients Not Update , Please Try Again"), extra_tags='Clients')

    context = {
        'client': client,

        'client_form': AdminClientsForm(),
        'current_page': _('Update'),
        'prev_Page': _('Clients'),
        'prev_Page_link': reverse_lazy('core:AdminClientList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/people/client/update.html', context)


@authenticated_staf
@staff_only
def AdminPosAddCustomer(request):  # sourcery skip: aug-assign, convert-to-enumerate

    if request.method == "POST":

        customer_form = AdminClientsForm(request.POST or None, request.FILES or None)
        profile_form = AdminCommonProfileForm(request.POST or None, request.FILES or None)
        if customer_form.is_valid() and profile_form.is_valid():

            customer_created = True
            name = customer_form.cleaned_data['title']
            email = customer_form.cleaned_data['email']
            image = request.FILES.get('image')
            phone = profile_form.cleaned_data['phone']
            country = profile_form.cleaned_data['country']
            governorates = profile_form.cleaned_data['governorates']
            city = profile_form.cleaned_data['city']
            area = profile_form.cleaned_data['area']
            address = profile_form.cleaned_data['address']
            note = profile_form.cleaned_data['note']
            customer_form = None
            if not customer_form:

                customer_form = Clients(name=name, email=email, image=image)
                customer_form.save()
                profile_form = CommonProfile(customer=customer_form, phone=phone, country=country,
                                             governorates=governorates, city=city, area=area,
                                             address=address, note=note)
                profile_form.save()

                messages.success(request,
                                 "Yeeew, check it out on the home page!")
                return HttpResponseRedirect(reverse_lazy('core:AdminPos'))
            else:

                messages.error(request, "Error")
    else:
        customer_form = AdminClientsForm()
        profile_form = AdminCommonProfileForm()
        context = {
            'customer_form': customer_form,
            'profile_form': profile_form,

        }
        return render(request, 'catalog/pos/pos.html', context)
    context = {

        'customer_form': customer_form,
        'profile_form': profile_form,

    }
    return render(request, 'catalog/pos/pos.html', context)

@authenticated_staf
@staff_only
def AdminClientDelete(request, slug):
    clients = Clients.objects.all()
    client = Clients.objects.get(slug=slug)
    if request.method == "POST":
        try:
            client.delete()
            context ={
                'clients': clients,
            }
            messages.success(request, _("Clients Delete Successfully"), extra_tags='Clients')
            return render(request, f'{BACKEND_TEMPLATES}/people/client/admin.html',context )
        except Exception as e:
            messages.error(request, _(f"Clients Not Delete {e} , Please Try Again"), extra_tags='Clients')
    else:
        context = {
            'clients': clients,
        }
        return render(request, f'{BACKEND_TEMPLATES}/people/client/admin.html', context)
    context = {
        'clients': clients,
    }
    return render(request, f'{BACKEND_TEMPLATES}/people/client/admin.html', context)


################## Driver ####################


@authenticated_staf
@staff_only
def AdminDriverList(request):
    drivers = Driver.objects.all()
    driver = None
    driver_list = []
    try:
        for driver in drivers:
            image = CommonMediaFiles.objects.get(
                owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)
            profile = CommonProfile.objects.get(
                owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)

            driver_list.append(
                {"driver": driver, "image": image, "profile": profile, })
    except Exception as e:
       
        driver_list.append(
            {"driver": driver, "image": None, "profile": None, })
    if request.method == "POST":
        driver_form = AdminDriverForm(request.POST or None, request.FILES or None)
        profile_form = AdminCommonProfileForm(request.POST or None, request.FILES or None)
        media_form = AdminCommonMediaFilesForm(request.POST or None, request.FILES or None)
        if driver_form:
            name = request.POST.get('title')

            phone = request.POST.get('phone')
            cost = request.POST.get('cost')

            start_day = request.POST.get('start_day')




            traffic_management = request.POST.get('traffic_management')
            license_number = request.POST.get('license_number')
            license_start = request.POST.get('license_start')
            license_end = request.POST.get('license_end')
            status = request.POST.get('status')
            hero_image = request.FILES.get('hero_image')

            address = request.POST.get('address')
            note = request.POST.get('note')
            try:
                check_license = Driver.objects.get(license_number=license_number)
                if check_license:
                    messages.error(request, "License Number Already Exist")
                    return HttpResponseRedirect(reverse_lazy('core:AdminDriverList'))

            except Exception as e:
                pass
               

            country = None
            governorates = None
            city = None
            area = None


            month = datetime.strptime(start_day, ("%Y-%m-%d")).month
            year = datetime.strptime(start_day, ("%Y-%m-%d")).year
            try:

                auditor = OperationTransactionAccounts.objects.all().count()
                if auditor <= 0:
                    messages.error(request, "Please Add Auditor Account First", extra_tags='Driver')
                    return HttpResponseRedirect(reverse_lazy('core:AdminDriverList'))
            except Exception as e:
                pass
            auditor = OperationTransactionAccounts.objects.all().last()

            driver_form = Driver(name=name,  phone=phone,


                                 traffic_management=traffic_management, license_number=license_number,
                                 license_start=license_start,
                                 license_end=license_end, status=status)
            driver_form.save()

            try:
                AdminCommonEmployeeSalary(request, 'Salary', cost, 0, 0, 0,
                                          0, 0, cost, 0,
                                          0, None, cost, 'User', request.user.id, 'Driver',
                                          driver_form.id, 'User', auditor.auditor.id)
                AdminCommonEmployeeMonthlyTimesheet(request, 0, 0, 0, 0, 0, 0,
                                                    month, year, None, 'User', request.user.id, 'Driver',
                                                    driver_form.id,
                                                    'Driver', driver_form.id, 'User', auditor.auditor.id, 'Driver',
                                                    driver_form.id)
                AdminCommonMediaHeroFiles(request, hero_image, 'Driver', driver_form.id)
                AdminCommonProfile(request, phone, 'Business', address, country, governorates, city, area, note,
                                   'Driver', driver_form.id)
            except Exception as e:

                driver_object = Driver.objects.get(id=driver_form.id)
                driver_object.delete()
                messages.error(request, _("Driver Not Add"), extra_tags='Driver')

                return HttpResponseRedirect(reverse_lazy('core:AdminDriverList'))

            messages.success(request, _("Driver Add Successfully"), extra_tags='Driver')

            return HttpResponseRedirect(reverse_lazy('core:AdminDriverList'))

        else:

            messages.error(request, _("Driver Not Add , Please Try Again"), extra_tags='Driver')
    else:
        context = {
            'drivers': driver_list,
            'driver_form': AdminDriverForm(),
            'profile_form': AdminCommonProfileForm(),
            'media_form': AdminCommonMediaFilesForm(),
            'current_page': _('Drivers')
        }
        return render(request, f'{BACKEND_TEMPLATES}/people/driver/admin.html', context)
    context = {
        'drivers': driver_list,
        'driver_form': AdminDriverForm(),
        'profile_form': AdminCommonProfileForm(),
        'media_form': AdminCommonMediaFilesForm(),
        'current_page': _('Drivers')

    }
    return render(request, f'{BACKEND_TEMPLATES}/people/driver/admin.html', context)


@authenticated_staf
@staff_only
def AdminDriverDetails(request, slug):
    driver = Driver.objects.get(slug=slug)
    image = CommonMediaFiles.objects.get(
        owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)
    profile = CommonProfile.objects.get(
        owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)
    employee_cost = EmployeeSalary.objects.get(receiver_model=ContentType.objects.get(model='Driver'),
                                               receiver_id=driver.id)
    if driver.garage_status == 'Out Service':
        reservation_payment = True

    else:
        reservation_payment = False
        reservation = None

    try:
        employee_timesheet = EmployeeMonthlyTimesheet.objects.filter(
            receiver_model=ContentType.objects.get(model='Driver'), receiver_id=driver.id)
        employee_transaction = OperationTransaction.objects.filter(
            receiver_model=ContentType.objects.get(model='Driver'), receiver_id=driver.id)
    except:
        employee_timesheet = None
        employee_transaction = None
    context = {
        'driver': driver,
        'image': image,
        'profile': profile,
        'employee_cost': employee_cost,
        'reservation_payment': reservation_payment,
        'reservation': reservation,
        'employee_timesheet': employee_timesheet,
        'employee_transaction': employee_transaction,
        'current_page': _('Details'),
        'prev_Page': _('Driver'),
        'prev_Page_link': reverse_lazy('core:AdminDriverList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/people/driver/details.html', context)


@authenticated_staf
@staff_only
def AdminDriverUpdate(request, slug):
    driver = Driver.objects.get(slug=slug)
    try:
        image = CommonMediaFiles.objects.get(
            owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)
        profile = CommonProfile.objects.get(
            owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)
        employee_cost = EmployeeSalary.objects.get(receiver_model=ContentType.objects.get(model='Driver'),
                                                   receiver_id=driver.id)
    except:
        image = None
        profile = None
        employee_cost = None

    if request.method == "POST":
        driver_form = AdminDriverForm(request.POST or None, request.FILES or None)
        profile_form = AdminCommonProfileForm(request.POST or None, request.FILES or None)
        media_form = AdminCommonMediaFilesForm(request.POST or None, request.FILES or None)
        print(11)
        if driver_form:

            print('driver_form.is_valid()')
            name = request.POST.get('title')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            national_id = request.POST.get('national_id')
            nationality = request.POST.get('nationality')
            national_start = request.POST.get('national_start')
            national_end = request.POST.get('national_end')
            electronic_number = request.POST.get('electronic_number')
            traffic_management = request.POST.get('traffic_management')
            license_number = request.POST.get('license_number')
            license_start = request.POST.get('license_start')
            license_end = request.POST.get('license_end')
            country = request.POST.get('country')
            governorates = request.POST.get('governorates')
            city = request.POST.get('city')
            area = request.POST.get('area')
            address = request.POST.get('address')
            status = request.POST.get('status')
            hero_image = request.FILES.get('hero_image')
            note = request.POST.get('note')

            try:
                country = Country.objects.get(id=country)
            except:
                country = profile.country
            try:
                governorates = Governorates.objects.get(id=governorates)
            except:
                governorates = profile.governorates
            try:
                city = City.objects.get(id=city)
            except:
                city = profile.city
            try:
                area = Area.objects.get(id=area)
            except:
                area = profile.area

            if hero_image is None:
                hero_image = image.image

            try:
                print('try')
                driver_object = Driver.objects.get(slug=slug)
                driver_object.title = name
                driver_object.email = email
                driver_object.phone = phone
                driver_object.national_id = national_id
                driver_object.nationality = nationality
                driver_object.national_start = national_start
                driver_object.national_end = national_end
                driver_object.electronic_number = electronic_number
                driver_object.traffic_management = traffic_management
                driver_object.license_number = license_number
                driver_object.license_start = license_start
                driver_object.license_end = license_end
                driver_object.status = status
                driver_object.save()
                print('driver_object.save()')

                AdminCommonMediaHeroFiles(request, hero_image, 'Driver', driver_object.id)
                AdminCommonProfile(request, phone, 'Business', address, country, governorates, city, area, note,
                                   'Driver', driver_object.id)
            except Exception as e:
               
               
                messages.error(request, "Error")

            messages.success(request, _("Driver Update Successfully"), extra_tags='Driver')

            return HttpResponseRedirect(reverse_lazy('core:AdminDriverList'))

        else:
            messages.error(request, _("Driver Not Update , Please Try Again"), extra_tags='Driver')
    else:

        context = {
            'driver': driver,
            'image': image,
            'profile': profile,
            'employee_cost': employee_cost,
            'driver_form': AdminDriverForm(),
            'profile_form': AdminCommonProfileForm(),
            'media_form': AdminCommonMediaFilesForm(),
            'current_page': _('Update'),
            'prev_Page': _('Driver'),
            'prev_Page_link': reverse_lazy('core:AdminDriverList'),
        }
        return render(request, f'{BACKEND_TEMPLATES}/people/driver/update.html', context)
    context = {
        'driver': driver,
        'image': image,
        'profile': profile,
        'employee_cost': employee_cost,
        'driver_form': AdminDriverForm(),
        'profile_form': AdminCommonProfileForm(),
        'media_form': AdminCommonMediaFilesForm(),

        'current_page': _('Update'),
        'prev_Page': _('Driver'),
        'prev_Page_link': reverse_lazy('core:AdminDriverList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/people/driver/update.html', context)


@authenticated_staf
@staff_only
def AdminDriverDelete(request, slug):
    drivers = Driver.objects.all()
    driver_list = []
    for driver in drivers:
        image = CommonMediaFiles.objects.get(
            owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)
        profile = CommonProfile.objects.get(
            owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)

        driver_list.append(
            {"driver": driver, "image": image, "profile": profile, })
    driver = Driver.objects.get(slug=slug)
    if driver.garage_status == 'Out Service':
       
        messages.error(request, _("License Number Already Exist , Please Try Again"), extra_tags='Driver')
        return HttpResponseRedirect(reverse_lazy('core:AdminDriverList'))

    else:
        print(2)
        image = CommonMediaFiles.objects.get(
            owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)
        image.delete()
        profile = CommonProfile.objects.get(
            owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)
        profile.delete()
        driver.delete()
        messages.success(request, _("Driver Delete Successfully"), extra_tags='Driver')
        return HttpResponseRedirect(reverse_lazy('core:AdminDriverList'))


################## Employee ####################


@authenticated_staf
@staff_only
def AdminEmployeeList(request):
    employees = Employee.objects.all()
    employee = None
    employee_list = []
    try:
        for employee in employees:
            image = CommonMediaFiles.objects.get(
                owner_model=ContentType.objects.get(model='Employee'), owner_id=employee.id)
            profile = CommonProfile.objects.get(
                owner_model=ContentType.objects.get(model='Employee'), owner_id=employee.id)

            employee_list.append(
                {"employee": employee, "image": image, "profile": profile, })
    except Exception as e:
        print('Empo', e)
        employee_list.append(
            {"employee": employee, "image": None, "profile": None, })
    if request.method == "POST":
        employee_form = AdminEmployeeForm(request.POST or None, request.FILES or None)
        profile_form = AdminCommonProfileForm(request.POST or None, request.FILES or None)
        media_form = AdminCommonMediaFilesForm(request.POST or None, request.FILES or None)

        if employee_form:

            name = request.POST.get('title')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            national_id = request.POST.get('national_id')
            cost = request.POST.get('cost')
            friday_cost = request.POST.get('friday_cost')
            start_day = request.POST.get('start_day')
            governorates = request.POST.get('governorates')
            address = request.POST.get('address')
            status = request.POST.get('status')
            hero_image = request.FILES.get('hero_image')
            month = datetime.strptime(start_day, ("%Y-%m-%d")).month
            year = datetime.strptime(start_day, ("%Y-%m-%d")).year
            try:
                national_id = Employee.objects.get(national_id=national_id)
                if national_id:
                    messages.error(request, _("National ID Already Exist"), extra_tags='Employee')
                    return HttpResponseRedirect(reverse_lazy('core:AdminEmployeeList'))
            except:
                pass

            auditor = OperationTransactionAccounts.objects.all().last()
            try:
                governorates = Governorates.objects.get(id=governorates)
            except:
                governorates = None

            employee_form = Employee(name=name, email=email, national_id=national_id, start_day=start_day,
                                     status=status)

            employee_form.save()
            AdminCommonEmployeeSalary(request, 'Salary', cost, 0, 0, 0,
                                      0, 0, cost, friday_cost,
                                      0, None, cost, 'User', request.user.id, 'Employee',
                                      employee_form.id, 'User', auditor.auditor.id)
            AdminCommonEmployeeMonthlyTimesheet(request, 0, 0, 0, 0, 0, 0,
                                                month, year, None, 'User', request.user.id, 'Employee',
                                                employee_form.id,
                                                'Employee', employee_form.id, 'User', auditor.auditor.id, 'Employee',
                                                employee_form.id, )

            try:
                AdminCommonMediaHeroFiles(request, hero_image, 'Employee', employee_form.id)
                AdminCommonProfile(request, phone, 'Business', address, None, governorates, None, None, None,
                                   'Employee', employee_form.id)
            except Exception as e:
               

                employee_object = Employee.objects.get(id=employee_form.id)
                employee_object.delete()

            messages.success(request, _("Employee Add Successfully"), extra_tags='Employee')

            return HttpResponseRedirect(reverse_lazy('core:AdminEmployeeList'))

        else:

            messages.error(request, _("Employee Not Add , Please Try Again"), extra_tags='Employee')
    else:

        context = {
            'employees': employee_list,
            'employee_form': AdminEmployeeForm(),
            'profile_form': AdminCommonProfileForm(),
            'media_form': AdminCommonMediaFilesForm(),
            'current_page': _('Employee'),
        }
        return render(request, f'{BACKEND_TEMPLATES}/people/employee/admin.html', context)
    context = {
        'employees': employee_list,
        'employee_form': AdminEmployeeForm(),
        'profile_form': AdminCommonProfileForm(),
        'media_form': AdminCommonMediaFilesForm(),
        'current_page': _('Employee'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/people/employee/admin.html', context)


@authenticated_staf
@staff_only
def AdminEmployeeDetails(request, slug):
    employee = Employee.objects.get(slug=slug)
    image = CommonMediaFiles.objects.get(
        owner_model=ContentType.objects.get(model='Employee'), owner_id=employee.id)
    profile = CommonProfile.objects.get(
        owner_model=ContentType.objects.get(model='Employee'), owner_id=employee.id)
    employee_cost = EmployeeSalary.objects.get(receiver_model=ContentType.objects.get(model='Employee'),
                                               receiver_id=employee.id)
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
        'employee_cost': employee_cost,
        'employee_timesheet': employee_timesheet,
        'employee_transaction': employee_transaction,
        'current_page': _('Details'),
        'prev_Page': _('Employee'),
        'prev_Page_link': reverse_lazy('core:AdminEmployeeList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/people/employee/details.html', context)


@authenticated_staf
@staff_only
def AdminEmployeeUpdate(request, slug):
    employee = Employee.objects.get(slug=slug)
    image = CommonMediaFiles.objects.get(
        owner_model=ContentType.objects.get(model='Employee'), owner_id=employee.id)
    profile = CommonProfile.objects.get(
        owner_model=ContentType.objects.get(model='Employee'), owner_id=employee.id)
    try:
        employee_cost = EmployeeSalary.objects.get(receiver_model=ContentType.objects.get(model='Employee'),
                                                   receiver_id=employee.id)
    except:
        employee_cost = None

    if request.method == "POST":
        employee_form = AdminEmployeeForm(request.POST or None, request.FILES or None)
        profile_form = AdminCommonProfileForm(request.POST or None, request.FILES or None)
        media_form = AdminCommonMediaFilesForm(request.POST or None, request.FILES or None)
        print(11)
        if employee_form:

            print('driver_form.is_valid()')
            name = request.POST.get('title')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            national_id = request.POST.get('national_id')
            cost = request.POST.get('cost')
            friday_cost = request.POST.get('friday_cost')
            country = request.POST.get('country')
            governorates = request.POST.get('governorates')
            city = request.POST.get('city')
            area = request.POST.get('area')
            address = request.POST.get('address')
            status = request.POST.get('status')
            hero_image = request.FILES.get('hero_image')
            note = request.POST.get('note')

            try:
                country = Country.objects.get(id=country)
            except:
                country = profile.country
            try:
                governorates = Governorates.objects.get(id=governorates)
            except:
                governorates = profile.governorates
            try:
                city = City.objects.get(id=city)
            except:
                city = profile.city
            try:
                area = Area.objects.get(id=area)
            except:
                area = profile.area

            if hero_image is None:
                hero_image = image.image

            try:

                employee_object = Employee.objects.get(slug=slug)
                employee_object.title = name
                employee_object.email = email
                employee_object.phone = phone
                employee_object.national_id = national_id

                employee_object.status = status
                employee_object.save()
                auditor = OperationTransactionAccounts.objects.all().last()
                AdminCommonEmployeeSalary(request, 'Salary', 0, 0, 0, 0,
                                          0, 0, 0, friday_cost,
                                          0, None, cost, 'User', request.user.id, 'Employee',
                                          employee_object.id, 'User', auditor.auditor.id)

                print('driver_object.save()')

                AdminCommonMediaHeroFiles(request, hero_image, 'Employee', employee_object.id)
                AdminCommonProfile(request, phone, 'Business', address, country, governorates, city, area, note,
                                   'Employee', employee_object.id)
            except Exception as e:
               
               
                messages.error(request, "Error")

            messages.success(request, _("Employee Update Successfully"), extra_tags='Employee')

            return HttpResponseRedirect(reverse_lazy('core:AdminEmployeeList'))

        else:
            messages.error(request, _("Employee Not Update , Please Try Again"), extra_tags='Employee')
    else:
        context = {
            'employee': employee,
            'image': image,
            'profile': profile,
            'employee_cost': employee_cost,
            'employee_form': AdminEmployeeForm(),
            'profile_form': AdminCommonProfileForm(),
            'media_form': AdminCommonMediaFilesForm(),
            'current_page': _('Update'),
            'prev_Page': _('Employee'),
            'prev_Page_link': reverse_lazy('core:AdminEmployeeList'),
        }
        return render(request, f'{BACKEND_TEMPLATES}/people/employee/update.html', context)
    context = {
        'employee': employee,
        'image': image,
        'profile': profile,
        'employee_cost': employee_cost,
        'employee_form': AdminEmployeeForm(),
        'profile_form': AdminCommonProfileForm(),
        'media_form': AdminCommonMediaFilesForm(),
        'current_page': _('Update'),
        'prev_Page': _('Employee'),
        'prev_Page_link': reverse_lazy('core:AdminEmployeeList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/people/employee/update.html', context)


@authenticated_staf
@staff_only
def AdminDriverArchive(request, slug):
    drivers = Driver.objects.all()
    driver_list = []
    for driver in drivers:
        image = CommonMediaFiles.objects.get(
            owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)
        profile = CommonProfile.objects.get(
            owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)

        driver_list.append(
            {"driver": driver, "image": image, "profile": profile, })
    driver = Driver.objects.get(slug=slug)
    if driver.garage_status == 'OutService':
       
        messages.error(request, _("License Number Already Exist , Please Try Again"), extra_tags='Driver')
        return HttpResponseRedirect(reverse_lazy('core:AdminDriverList'))

    else:
        print(2)
        image = CommonMediaFiles.objects.get(
            owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)
        image.delete()
        profile = CommonProfile.objects.get(
            owner_model=ContentType.objects.get(model='Driver'), owner_id=driver.id)
        profile.delete()
        driver.delete()
        messages.success(request, _("Driver Delete Successfully"), extra_tags='Driver')
        return HttpResponseRedirect(reverse_lazy('core:AdminDriverList'))


def AdminCommonEmployeeSalary(request, transaction_type, amount, duration, duration_count, hour_count, hour_cost,
                              daily_cost, monthly_cost, friday_cost,
                              discount, overtime_type, cost, sender_model, sender_id, receiver_model, receiver_id,
                              auditor_model, auditor_id):
    try:
        employee_salary = EmployeeSalary.objects.get(receiver_model=ContentType.objects.get(model=receiver_model),
                                                     receiver_id=receiver_id)
        employee_salary.transaction_type = transaction_type
        employee_salary.amount = amount
        employee_salary.duration = duration
        employee_salary.duration_count = duration_count
        employee_salary.hour_count = hour_count
        employee_salary.hour_cost = hour_cost
        employee_salary.daily_cost = daily_cost
        employee_salary.monthly_cost = monthly_cost
        employee_salary.friday_cost = friday_cost
        employee_salary.discount = discount
        employee_salary.overtime_type = overtime_type
        employee_salary.cost = cost
        employee_salary.sender_model = ContentType.objects.get(model=sender_model)
        employee_salary.sender_id = sender_id
        employee_salary.save()
    except Exception as e:
        print('EmployeeSalary', e)

        EmployeeSalary.objects.create(
            transaction_type=transaction_type,
            amount=amount,
            duration=duration,
            duration_count=duration_count,
            hour_count=hour_count,
            hour_cost=hour_cost,
            daily_cost=daily_cost,
            monthly_cost=monthly_cost,
            friday_cost=friday_cost,
            discount=discount,
            overtime_type=overtime_type,
            cost=cost,
            sender_model=ContentType.objects.get(model=sender_model),
            sender_id=sender_id,
            receiver_model=ContentType.objects.get(model=receiver_model),
            receiver_id=receiver_id,
            auditor_model=ContentType.objects.get(model=auditor_model),
            auditor_id=auditor_id,
        )


def AdminCommonEmployeeMonthlyTimesheet(request, day, operating_hours, friday, discount, overtime, total,
                                        month, year,
                                        note, sender_model, sender_id, owner_model, owner_id, receiver_model,
                                        receiver_id, auditor_model, auditor_id, employee_model, employee_id):
    try:
        employee_monthly_timesheet = EmployeeMonthlyTimesheet.objects.get(
            employee_model=ContentType.objects.get(model=employee_model),
            employee_id=employee_id, month=month, year=year)
        employee_monthly_timesheet.day += day
        employee_monthly_timesheet.operating_hours += operating_hours
        employee_monthly_timesheet.friday += friday
        employee_monthly_timesheet.discount += discount
        employee_monthly_timesheet.overtime += overtime
        employee_monthly_timesheet.total += total
        employee_monthly_timesheet.note = note
        employee_monthly_timesheet.sender_model = ContentType.objects.get(model=sender_model)
        employee_monthly_timesheet.sender_id = sender_id
        employee_monthly_timesheet.save()
    except:
        EmployeeMonthlyTimesheet.objects.create(

            day=day,
            operating_hours=operating_hours,
            friday=friday,
            discount=discount,
            overtime=overtime,
            total=total,
            month=month,
            year=year,
            note=note,
            sender_model=ContentType.objects.get(model=sender_model),
            sender_id=sender_id,
            owner_model=ContentType.objects.get(model=owner_model),
            owner_id=owner_id,
            receiver_model=ContentType.objects.get(model=receiver_model),
            receiver_id=receiver_id,
            auditor_model=ContentType.objects.get(model=auditor_model),
            auditor_id=auditor_id,
            employee_model=ContentType.objects.get(model=employee_model),
            employee_id=employee_id,
        )


################## Salary ####################
@authenticated_staf
@staff_only
def AdminEmployeeSalaryCreate(request, slug):

    system_wallet = SystemWallet.objects.get(secret='SystemWallet')
    if request.method == "POST":
        salary_form = AdminEmployeeSalaryrForm(request.POST or None)
        media_form = AdminCommonMediaFilesForm(request.POST or None, request.FILES or None)
        receiver_name = None
        print(11)
        if salary_form:
            salary = request.POST.get('salary')
            receiver_model = request.POST.get('receiver_model')
            paid = request.POST.get('paid')
            print('paid', paid)
            date = request.POST.get('date')
            hero_image = request.FILES.get('hero_image')
            note = request.POST.get('note')
            if receiver_model == 'Driver':

                receiver_id = Driver.objects.get(slug=slug).id

                garage_check = Driver.objects.get(slug=slug).garage_status
                if garage_check == 'In Seervice':
                    messages.error(request, _("You can not pay salary to driver who is no longer Work In Active Project"),
                                   extra_tags='Salary')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    receiver_name = Driver.objects.get(slug=slug).title
                    salary_operation_history = OperationTransactionHistory.objects.filter(
                        sender_model=ContentType.objects.get(model='Driver'), sender_id=receiver_id).last()
            elif receiver_model == 'Employee':
                receiver_id = Employee.objects.get(slug=slug).id
                receiver_name = Employee.objects.get(slug=slug).title
                salary_operation_history = OperationTransactionHistory.objects.filter(
                    sender_model=ContentType.objects.get(model='Employee'), sender_id=receiver_id).last()
            check_have_salary = EmployeeSalary.objects.get(receiver_model=ContentType.objects.get(model=receiver_model),receiver_id=receiver_id)
            if check_have_salary.cost == 0:
                messages.error(request, _("You can not pay salary to This Person, Because He/She Have No Salary"),
                               extra_tags='Salary')
                return redirect(request.META['HTTP_REFERER'])

            month = datetime.strptime(date, ("%Y-%m-%d")).month
            year = datetime.strptime(date, ("%Y-%m-%d")).year
            if Decimal(system_wallet.treasury) < Decimal(paid):
                messages.error(request, _("A Treasury account does not cover your application , Please Try Again"),
                               extra_tags='Salary')
                return redirect(request.META['HTTP_REFERER'])
            if   Decimal(paid) >Decimal(check_have_salary.cost):
                messages.error(request, _("Paid amount is greater than the due amount , Please Try Again "),
                               extra_tags='Salary')
                return redirect(request.META['HTTP_REFERER'])
            try:
                if Decimal(paid) > Decimal(salary_operation_history.due):
                    messages.error(request, _("Paid amount is greater than the due amount , Please Try Again"),
                                   extra_tags='Salary')
                    return redirect(request.META['HTTP_REFERER'])
            except:
                pass


            auditor = OperationTransactionAccounts.objects.all().last()
            try:
                print('try')
                employee_salary = EmployeeSalary.objects.get(
                    receiver_model=ContentType.objects.get(model=receiver_model), receiver_id=receiver_id)
                if int(paid) < int(employee_salary.cost):
                    due = int(employee_salary.cost) - int(paid)
                    next_month = datetime.strptime(date, ("%Y-%m-%d")) + timedelta(days=30)
                else:
                    due = 0
                    next_month = None

                salary_object = EmployeeMonthlyTimesheet(sender_model=ContentType.objects.get(model='User'),
                                                         sender_id=request.user.id,
                                                         receiver_model=ContentType.objects.get(model=receiver_model),
                                                         receiver_id=receiver_id,
                                                         owner_model=ContentType.objects.get(model='EmployeeSalary'),
                                                         owner_id=employee_salary.id,
                                                         auditor_model=ContentType.objects.get(model='User'),
                                                         auditor_id=auditor.auditor.id,
                                                         employee_model=ContentType.objects.get(model=receiver_model),
                                                         employee_id=receiver_id, salary=paid,
                                                         month=month, year=year)
                salary_object.save()

                system_wallet.treasury -= Decimal(paid)
                system_wallet.save()
                treasury_object = TreasuryTransactions(system_wallet=system_wallet,
                                                       sender_model=ContentType.objects.get(model='User'),
                                                       sender_id=request.user.id,
                                                       receiver_model=ContentType.objects.get(model='SystemWallet'),
                                                       receiver_id=system_wallet.id,
                                                       owner_model=ContentType.objects.get(model='EmployeeMonthlyTimesheet'),
                                                       owner_id=salary_object.id,
                                                       auditor_model=ContentType.objects.get(model='User'),
                                                       auditor_id=auditor.auditor.id, transaction_type='Salary',
                                                       transaction_mode='Treasury',
                                                       transaction_status='Complete',
                                                       transaction_category='Expense', amount=Decimal(paid),
                                                       receive=0, send=Decimal(paid),
                                                       note=_(f'Employee {receiver_name} Salary {note} Money Operation'), )
                treasury_object.save()

                AdminCommonOperationTransaction(request, 'EmployeeMonthlyTimesheet', salary_object.id, receiver_model,
                                                receiver_id,
                                                'EmployeeSalary', employee_salary.id,
                                                'Salary',
                                                _(f'Monthly Salary Payment For {receiver_name} in Month {month}'),
                                                employee_salary.cost, due, paid, date, next_month, month, year)
                AdminCommonOperationTransactionHistory(request, 'EmployeeMonthlyTimesheet', salary_object.id,
                                                       receiver_model, receiver_id,
                                                       'EmployeeSalary', employee_salary.id,
                                                       'Salary',
                                                       _(f'Monthly Salary Payment For {receiver_name} in Month {month}'),
                                                       employee_salary.cost, due, paid, date, next_month, month, year)
                AdminCommonMediaHeroFiles(request, hero_image, receiver_model, receiver_id)
                common_invoice(request, _(f'Monthly Salary Payment For {receiver_name} in Month {month}'),
                               salary_object.code,
                               salary_object.created_at, 'CURRENT', _(f'Monthly Salary Payment'), hero_image, 'STAFF',
                               'User',
                               request.user.id, receiver_model, receiver_id, 'EmployeeSalary', employee_salary.id,
                               'EmployeeMonthlyTimesheet', salary_object.id,
                               )
                users = User.objects.filter(access_notification=True)
                for user in users:
                    AdminCommonNotifications(request, _(f'Salary'), False, False, False,
                                             salary_object.id,
                                             'core:EmployeeMonthlyTimesheet', salary_object.slug,
                                             _(f'Monthly Salary Payment For {receiver_name} in Month {month}'),
                                             _(f'Monthly Salary Payment For {receiver_name} in Month {month}'),
                                             salary_object.created_at, next_month, 'User', request.user.id,
                                              'EmployeeMonthlyTimesheet', salary_object.id,receiver_model, receiver_id,
                                             'User',
                                             auditor.auditor.id)
                AdminEmployeeMonthlyTimesheetMonthCheck(request, salary_object.slug,receiver_model,receiver_id,'EmployeeSalary',employee_salary.id)

            except Exception as e:
               
               
                messages.error(request, "Error")

            messages.success(request, _("Salary Update Successfully"), extra_tags='Salary')

            return redirect(request.META['HTTP_REFERER'])

        else:
            messages.error(request, _("Salary Not Update , Please Try Again"), extra_tags='Salary')
    else:
        context = {

            'salary_form': AdminEmployeeSalaryrForm(),
            'profile_form': AdminCommonProfileForm(),
            'media_form': AdminCommonMediaFilesForm(),
            'current_page': _('Update'),
            'prev_Page': _('Employee'),
            'prev_Page_link': redirect(request.META['HTTP_REFERER']),
        }
        return redirect(request.META['HTTP_REFERER'])
    context = {

        'salary_form': AdminEmployeeSalaryrForm(),
        'current_page': _('Update'),
        'prev_Page': _('Employee'),
        'prev_Page_link': redirect(request.META['HTTP_REFERER']),

    }
    return render(request, f'{BACKEND_TEMPLATES}/people/employee/update.html', context)




def AdminEmployeeMonthlyTimesheetMonthCheck(request, slug,receiver_model,receiver_id,owner_model,owner_id):
    employee_monthly_timesheet = EmployeeMonthlyTimesheet.objects.get(slug=slug)
    operation_object = OperationTransaction.objects.get(sender_id=employee_monthly_timesheet.id,)
    auditor = OperationTransactionAccounts.objects.all().last()
    if Decimal(operation_object.due) == 0:
        operation_object.due =Decimal(operation_object.amount)
        operation_object.paid = 0
        if operation_object.month == 12:
            operation_object.month = int(1)
            operation_object.year += int(1)
        else:
                operation_object.month = int(int(operation_object.month) + 1)
        operation_object.save()
        AdminCommonOperationTransactionHistory(request, 'EmployeeMonthlyTimesheet', operation_object.sender_id, receiver_model,
                                               operation_object.receiver_id,
                                               owner_model, owner_id,
                                               'Salary', operation_object.reason, operation_object.amount,
                                               operation_object.due,
                                               operation_object.paid, datetime.now(),
                                               operation_object.update_at, operation_object.month, operation_object.year)
        salary_object = EmployeeMonthlyTimesheet(sender_model=ContentType.objects.get(model='User'),
                                                 sender_id=request.user.id,
                                                 receiver_model=ContentType.objects.get(model=receiver_model),
                                                 receiver_id=receiver_id,
                                                 owner_model=ContentType.objects.get(model='EmployeeSalary'),
                                                 owner_id=owner_id,
                                                 auditor_model=ContentType.objects.get(model='User'),
                                                 auditor_id=auditor.auditor.id,
                                                 employee_model=ContentType.objects.get(model=receiver_model),
                                                 employee_id=receiver_id, salary=operation_object.amount,
                                                 month=operation_object.month, year=operation_object.year)
        salary_object.save()


@authenticated_staf
@staff_only
def AdminEmployeeSalaryUpdate(request, slug):
    salary_transaction = OperationTransaction.objects.get(slug=slug)
    employee_salary = EmployeeSalary.objects.get(id=salary_transaction.owner_id)
    employee_timesheet = EmployeeMonthlyTimesheet.objects.filter(owner_id=employee_salary.id,
                                                                 month=salary_transaction.month,
                                                                 year=salary_transaction.year).last()
    system_wallet = SystemWallet.objects.get(secret='SystemWallet')

    if request.method == "POST":
        salary_form = AdminEmployeeSalaryrForm(request.POST or None)
        media_form = AdminCommonMediaFilesForm(request.POST or None, request.FILES or None)
        receiver_name = None
        print(11)
        if salary_form:

            paid = request.POST.get('operation_amount')
            date = request.POST.get('operation_paid_date')
            hero_image = request.FILES.get('hero_image')
            note = request.POST.get('note')

            month = datetime.strptime(date, ("%Y-%m-%d")).month
            year = datetime.strptime(date, ("%Y-%m-%d")).year

            auditor = OperationTransactionAccounts.objects.all().last()
            if int(paid) < int(salary_transaction.paid):
                due = int(salary_transaction.paid) - int(paid)
                next_month = datetime.strptime(date, ("%Y-%m-%d")) + timedelta(days=30)
            elif int(paid) > int(salary_transaction.paid):
                messages.error(request, _("Paid amount is greater than the due amount , Please Try Again"),
                               extra_tags='Operation Transaction')
                return redirect(request.META['HTTP_REFERER'])
            else:
                due = 0
                next_month = None
            salary_object = EmployeeMonthlyTimesheet.objects.get(owner_id=employee_salary.id, month=month, year=year)
            salary_object.salary += Decimal(paid)
            salary_object.note = note
            salary_object.save()


            salary_transaction.paid += Decimal(paid)
            salary_transaction.due -= Decimal(paid)
            salary_transaction.paid_date = date
            salary_transaction.save()
            model_name = ContentType.objects.get(model=salary_transaction.receiver_model.title)
            print(model_name)
            model = model_name.model
            print('nodel', model)
            model_get = ContentType.objects.get(model=model).get_object_for_this_type(id=salary_transaction.receiver_id)
            print('salary_transaction.receiver_model', salary_transaction.receiver_model)
            system_wallet.treasury -= Decimal(paid)
            system_wallet.save()
            treasury_object = TreasuryTransactions(system_wallet=system_wallet,
                                                   sender_model=ContentType.objects.get(model='User'),
                                                   sender_id=request.user.id,
                                                   receiver_model=ContentType.objects.get(model='SystemWallet'),
                                                   receiver_id=system_wallet.id,
                                                   owner_model=ContentType.objects.get(
                                                       model='EmployeeMonthlyTimesheet'),
                                                   owner_id=salary_object.id,
                                                   auditor_model=ContentType.objects.get(model='User'),
                                                   auditor_id=auditor.auditor.id, transaction_type='Salary',
                                                   transaction_mode='Treasury',
                                                   transaction_status='Complete',
                                                   transaction_category='Expense', amount=Decimal(paid),
                                                   receive=0, send=Decimal(paid),
                                                   note=_(f'Employee {model_get.title} Salary {note} Money Operation'), )
            treasury_object.save()

            AdminCommonOperationTransactionHistory(request, 'EmployeeMonthlyTimesheet', salary_object.id,
                                                   model, salary_transaction.receiver_id,
                                                   'EmployeeSalary', employee_salary.id,
                                                   'Salary',
                                                   _(f'Monthly Salary Payment For {model_get.title} in Month {month}'),
                                                   employee_salary.cost, due, paid, date, next_month, month, year)
            AdminCommonMediaHeroFiles(request, hero_image, model,
                                      salary_transaction.receiver_id)
            common_invoice(request, _(f'Monthly Salary Payment For {model_get.title} in Month {month}'),
                           salary_object.code,
                           salary_object.created_at, 'CURRENT', _(f'Monthly Salary Payment'), hero_image, 'STAFF',
                           'User',
                           request.user.id, model, salary_transaction.receiver_id,
                           'EmployeeSalary', employee_salary.id,
                           'EmployeeMonthlyTimesheet', salary_object.id,
                           )
            users = User.objects.filter(admin=True)
            for user in users:
                AdminCommonNotifications(request, _(f'Salary'), False, False, False,
                                         _(f'{model_get.title} Salary'),
                                         model, model_get.slug,
                                         _(f'Monthly Salary Payment For {model_get.title} in Month {month}'),
                                         _(f'Monthly Salary Payment For {model_get.title} in Month {month}'),
                                         salary_object.created_at, next_month, 'User', request.user.id,
                                         'User', user.id, model, salary_transaction.receiver_id,
                                         'User', auditor.auditor.id)
            AdminEmployeeMonthlyTimesheetMonthCheck(request, salary_object.slug, model, salary_transaction.receiver_id,'EmployeeSalary',employee_salary.id)


            messages.success(request, _("Salary Update Successfully"), extra_tags='Salary')
            if model == 'driver':
                return redirect('core:AdminDriverDetails', slug=model_get.slug)
            elif model == 'employee':
                return redirect('core:AdminEmployeeDetails', slug=model_get.slug)



        else:
            messages.error(request, _("Salary Not Update , Please Try Again"), extra_tags='Salary')
    else:
        context = {
            'salary_transaction': salary_transaction,
            'employee_salary': employee_salary,
            'employee_timesheet': employee_timesheet,

            'salary_form': AdminEmployeeSalaryrForm(),
            'profile_form': AdminCommonProfileForm(),
            'media_form': AdminCommonMediaFilesForm(),
            'current_page': _('Update'),
            'prev_Page': _('Employee'),
            'prev_Page_link': redirect(request.META['HTTP_REFERER']),
        }
        return render(request, f'{BACKEND_TEMPLATES}/people/salary/update.html', context)
    context = {
        'salary_transaction': salary_transaction,
        'employee_salary': employee_salary,
        'employee_timesheet': employee_timesheet,

        'salary_form': AdminEmployeeSalaryrForm(),
        'current_page': _('Update'),
        'prev_Page': _('Employee'),
        'prev_Page_link': redirect(request.META['HTTP_REFERER']),

    }
    return render(request, f'{BACKEND_TEMPLATES}/people/salary/update.html', context)


################## Contact ####################
@authenticated_staf
@staff_only
def AdminContactList(request):
    clients = Clients.objects.all()
    client_list = []
    for client in clients:
        image = CommonMediaFiles.objects.get(
            owner_model=ContentType.objects.get(model='Clients'), owner_id=client.id)
        profile = CommonProfile.objects.get(
            owner_model=ContentType.objects.get(model='Clients'), owner_id=client.id)

        client_list.append(
            {"people": client, "image": image, "profile": profile, })
    if request.method == "POST":
        client_form = AdminClientsForm(request.POST or None, request.FILES or None)
        profile_form = AdminCommonProfileForm(request.POST or None, request.FILES or None)
        media_form = AdminCommonMediaFilesForm(request.POST or None, request.FILES or None)

        if client_form.is_valid():

            name = request.POST.get('title')
            company = request.POST.get('company')
            national_id = request.POST.get('national_id')
            email = request.POST.get('email')
            client_type = request.POST.get('client_type')
            status = request.POST.get('status')
            hero_image = request.FILES.get('hero_image')
            phone = request.POST.get('phone')
            country = request.POST.get('country')
            governorates = request.POST.get('governorates')
            city = request.POST.get('city')
            area = request.POST.get('area')
            address = request.POST.get('address')
            note = request.POST.get('note')

            try:
                country = Country.objects.get(id=country)
            except:
                country = None
            try:
                governorates = Governorates.objects.get(id=governorates)
            except:
                governorates = None
            try:
                city = City.objects.get(id=city)
            except:
                city = None
            try:
                area = Area.objects.get(id=area)
            except:
                area = None

            client_form = Clients(name=name, company=company, national_id=national_id, email=email,
                                  client_type=client_type, status=status)
            client_form.save()
            try:
                AdminCommonMediaHeroFiles(request, hero_image, 'Clients', client_form.id)
                AdminCommonProfile(request, phone, 'Business', address, country, governorates, city, area, note,
                                   'Clients', client_form.id)
            except Exception as e:

                client_object = Clients.objects.get(id=client_form.id)
                client_object.delete()

            messages.success(request, _("Clients Add Successfully"), extra_tags='Clients')

            return HttpResponseRedirect(reverse_lazy('core:AdminClientList'))

        else:

            messages.error(request, _("Clients Not Add , Please Try Again"), extra_tags='Clients')
    else:
        client_form = AdminClientsForm()

        context = {
            'clients': client_list,
            'client_form': AdminClientsForm(),
            'profile_form': AdminCommonProfileForm(),
            'media_form': AdminCommonMediaFilesForm(),
            'current_page': _('Clients')
        }
        return render(request, f'{BACKEND_TEMPLATES}/people/contact/admin.html', context)
    context = {
        'clients': client_list,
        'client_form': AdminClientsForm(),
        'profile_form': AdminCommonProfileForm(),
        'media_form': AdminCommonMediaFilesForm(),
        'current_page': _('Clients')

    }
    return render(request, f'{BACKEND_TEMPLATES}/people/contact/admin.html', context)


################## Contract ####################

def AdminCommonContract(request, title, start_date, end_date, status,
                        sender_model, sender_id, receiver_model, receiver_id, owner_model, owner_id):
    print('status', status)

    try:
        contract_object = Contract.objects.get(title=title)
        contract_object.start_date = start_date
        contract_object.end_date = end_date
        contract_object.status = status
        contract_object.sender_model = ContentType.objects.get(model=sender_model)
        contract_object.sender_id = sender_id
        contract_object.receiver_model = ContentType.objects.get(model=receiver_model)
        contract_object.receiver_id = receiver_id
        contract_object.owner_model = ContentType.objects.get(model=owner_model)
        contract_object.owner_id = owner_id

        contract_object.save()
    except:
        contract_object = Contract(title=title, start_date=start_date, end_date=end_date, status=status,
                                   sender_model=ContentType.objects.get(model=sender_model), sender_id=sender_id,
                                   receiver_model=ContentType.objects.get(model=receiver_model),
                                   receiver_id=receiver_id,
                                   owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id)
        contract_object.save()
    return contract_object


@authenticated_staf
@staff_only
def AdminCommonContractTerms(request, contract, order_term, terms, terms_details,
                             sender_model, sender_id, receiver_model, receiver_id, owner_model, owner_id):
    try:
        contract_object = ContractTerms.objects.get(contract=contract)
        contract_object.order_term = order_term
        contract_object.terms = terms
        contract_object.terms_details = terms_details

        contract_object.sender_model = ContentType.objects.get(model=sender_model)
        contract_object.sender_id = sender_id
        contract_object.receiver_model = ContentType.objects.get(model=receiver_model)
        contract_object.receiver_id = receiver_id
        contract_object.owner_model = ContentType.objects.get(model=owner_model)
        contract_object.owner_id = owner_id
        contract_object.save()
    except:
        contract_object = ContractTerms(contract=contract, order_term=order_term, terms=terms,
                                        terms_details=terms_details,
                                        sender_model=ContentType.objects.get(model=sender_model), sender_id=sender_id,
                                        receiver_model=ContentType.objects.get(model=receiver_model),
                                        receiver_id=receiver_id,
                                        owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id)
        contract_object.save()

    return contract_object



############### Branch ####################

@authenticated_staf
@staff_only
def AdminBranchList(request):
    branches = Branch.objects.all()
    branch_form = AdminBranchForm()
    if request.method == 'POST':
        title = request.POST.get('title')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        if branch_form:
            branch_form = Branch(title=title, phone=phone, email=email, address=address)
            branch_form.save()
            messages.success(request, _("Branch Add Successfully"), extra_tags='Branch')
            return HttpResponseRedirect(reverse_lazy('core:AdminBranchList'))
        else:
            messages.error(request, _("Branch Not Add , Please Try Again"), extra_tags='Branch')

    context = {
        'branches': branches,
        'branch_form': AdminBranchForm(),

        'current_page': _('Branch')
    }
    return render(request, f'{BACKEND_TEMPLATES}/people/branch/admin.html', context)


############ Team ####################

@authenticated_staf
@staff_only
def AdminTeamList(request):
    team_list = Team.objects.all()
    context = {
        'teams': team_list,
        'current_page': _('Team')
    }
    return render(request, f'{BACKEND_TEMPLATES}/people/team/admin.html', context)

@authenticated_staf
@staff_only
def AdminTeamDetails(request, slug):
    teams = Team.objects.get(slug=slug)

    context = {
        'teams': teams,


        'current_page': _('Team'),
        'prev_Page': _('Clients'),
        'prev_Page_link': reverse_lazy('core:AdminClientList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/people/people/details.html', context)


@authenticated_staf
@staff_only
# @superuser_only
def AdminTeamCreate(request):  # sourcery skip: aug-assign, convert-to-enumerate

    if request.method == "POST":

        team_form = AdminTeamForm(request.POST or None, request.FILES or None)
        skill_form = AdminTeamSkillForm(request.POST or None, request.FILES or None)
        social_form = AdminCommonSocialLinkForm(request.POST or None, request.FILES or None)
        if team_form :

            name = request.POST.get('title')
            description = request.POST.get('description')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            hero_image = request.FILES.get('hero_image')
            job_title = request.POST.get('job_title')
            skill_level = request.POST.get('skill_level')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            section = request.POST.get('section')
            experience = request.POST.get('experience')
            featured = request.POST.get('featured')
            status = request.POST.get('status')
            skill = request.POST.getlist('skill')
            percentage = request.POST.getlist('percentage')
            images = request.FILES.getlist('images')
            provider = request.POST.getlist('provider')
            url = request.POST.getlist('url')
            customer_form = None
            if not customer_form:

                team_object = Team(owner_model=ContentType.objects.get(model='User'),
                                      owner_id=request.user.id,  name=name,
                                        description=description, keyword=keyword, body=body,
                                        image=hero_image, job_title=job_title, skill_level=skill_level,
                                        email=email, phone=phone, section=section, experience=experience,
                                        featured=featured, status=status)

                team_object.save()
                for i in range(len(skill)):
                    skill_object = TeamSkill(owner_model=ContentType.objects.get(model='Team'),
                                             owner_id=team_object.id, skill=skill[i], percentage=percentage[i],image=images[i])
                    skill_object.save()
                for i in range(len(provider)):
                    AdminCommonSocialLink(request, provider[i], url[i], 'Team', team_object.id)

                AdminCommonSeo(request, name, description, keyword, request.user.id, hero_image,
                               'Team', team_object.id)

                messages.success(request,
                                    f"Team {team_object.name} has been created successfully", extra_tags='Team')
                return HttpResponseRedirect(reverse_lazy('core:AdminTeamList'))
            else:

                messages.error(request,
                                    f"Team  has not been created successfully", extra_tags='Team')
                return HttpResponseRedirect(reverse_lazy('core:AdminTeamList'))
    else:

        context = {
            'team_form': AdminTeamForm(),
            'skill_form': AdminTeamSkillForm(),
            'social_form': AdminCommonSocialLinkForm(),
            'current_page': _('Add'),
            'prev_Page': _('Team'),
            'prev_Page_link': reverse_lazy('core:AdminTeamList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/people/team/add.html', context)
    context = {
        'team_form': AdminTeamForm(),
        'skill_form': AdminTeamSkillForm(),
        'social_form': AdminCommonSocialLinkForm(),
       'current_page': _('Add'),
        'prev_Page': _('Team'),
        'prev_Page_link': reverse_lazy('core:AdminTeamList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/people/team/add.html', context)



@authenticated_staf
@staff_only
def AdminTeamUpdate(request, slug):
    team = Team.objects.get(slug=slug)
    team_skill = TeamSkill.objects.filter(team=team.id)
    social = CommonSocialLink.objects.filter(owner_model=ContentType.objects.get(model='Team'), owner_id=team.id,
                                          )
    if request.method == "POST":
        team_form = AdminTeamForm(request.POST or None, request.FILES or None, instance=team)
        skill_form = AdminTeamSkillForm(request.POST or None, request.FILES or None)
        social_form = AdminCommonSocialLinkForm(request.POST or None, request.FILES or None)
        if team_form :

            name = request.POST.get('title')
            description = request.POST.get('description')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            hero_image = request.FILES.get('hero_image')
            job_title = request.POST.get('job_title')
            skill_level = request.POST.get('skill_level')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            section = request.POST.get('section')
            experience = request.POST.get('experience')
            featured = request.POST.get('featured')
            status = request.POST.get('status')
            skill = request.POST.getlist('skill')
            percentage = request.POST.getlist('percentage')
            images = request.FILES.getlist('images')
            provider = request.POST.getlist('provider')
            url = request.POST.getlist('url')
            customer_form = None
            if not customer_form:

                team_object = Team(owner_model=ContentType.objects.get(model='User'),
                                      owner_id=request.user.id,  name=name,
                                        description=description, keyword=keyword, body=body,
                                        image=hero_image, job_title=job_title, skill_level=skill_level,
                                        email=email, phone=phone, section=section, experience=experience,
                                        featured=featured, status=status)

                team_object.save()
                for i in range(len(skill)):
                    skill_object = TeamSkill(owner_model=ContentType.objects.get(model='Team'),
                                             owner_id=team_object.id, skill=skill[i], percentage=percentage[i],image=images[i])
                    skill_object.save()
                for i in range(len(provider)):
                    AdminCommonSocialLink(request, provider[i], url[i], 'Team', team_object.id)

                AdminCommonSeo(request, name, description, keyword, request.user.id, hero_image,
                               'Team', team_object.id)

                messages.success(request,
                                    f"Team {team_object.name} has been created successfully", extra_tags='Team')
                return HttpResponseRedirect(reverse_lazy('core:AdminTeamList'))
            else:

                    messages.error(request,
                                        f"Team  has not been created successfully", extra_tags='Team')
                    return HttpResponseRedirect(reverse_lazy('core:AdminTeamList'))
    else:

            context = {
                'team': team,
                'team_skill': team_skill,
                'social': social,
                'team_form': AdminTeamForm(instance=team),
                'skill_form': AdminTeamSkillForm(),
                'social_form': AdminCommonSocialLinkForm(),
                'current_page': _('Update'),
                'prev_Page': _('Team'),
                'prev_Page_link': reverse_lazy('core:AdminTeamList'),

            }
            return render(request, f'{BACKEND_TEMPLATES}/people/team/update.html', context)


@authenticated_staf
@staff_only
def AdminTeamArchive(request, slug):
    team = Team.objects.get(slug=slug)
    if request.method == "POST":

        team.status = 'Archive'
        team.save()
        messages.success(request, f"Team {team.title} has been archived successfully", extra_tags='Team')
        return HttpResponseRedirect(reverse_lazy('core:AdminTeamList'))
