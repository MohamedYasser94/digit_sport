from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.catalog.forms.forms import AdminCatalogWarehouseForm
from apps.catalog.models.models import Products, ProductsStock
from apps.catalog.models.vendor import Warehouse

from core.models.localization import Country, Governorates, City
from core.models.people import Employee

from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()
@authenticated_staf
@staff_only
def AdminCatalogWarehouseList(request):
    warehouses = Warehouse.objects.all()
    if request.method == "POST":
        warehouse_form = AdminCatalogWarehouseForm(request.POST or None, request.FILES or None)
        if warehouse_form:
            name = request.POST.get('title')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            country = request.POST.get('country')
            governorates = request.POST.get('governorates')
            city = request.POST.get('city')
            status = 'Active'
           
            try:
                country_id = Country.objects.get(id=country)
            except Exception as e:
               
                country_id = None
            try:
                governorates_id = Governorates.objects.get(id=governorates)
            except Exception as e:
               
                governorates_id = None
            try:
                city_id = City.objects.get(id=city)
            except Exception as e:
               
                city_id = None
            check_user = User.objects.get(id=request.user.id)
            employee = Employee.objects.get(owner_id=check_user.id)

            warehouse_form.save()
            messages.success(request, _("Warehouse Add Successfully"), extra_tags='Warehouse')

            return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogWarehouseList'))
        else:
            
            messages.error(request, _("Warehouse Not Add , Please Try Again"), extra_tags='Warehouse')
            context = {
                'warehouses': warehouses,
                'warehouse_form': AdminCatalogWarehouseForm(),
                'current_page': _('Warehouse')
            }
            return render(request, f'{BACKEND_TEMPLATES}/store/warehouse/admin.html', context)
    else:
        context = {
            'warehouses': warehouses,
            'warehouse_form': AdminCatalogWarehouseForm(),
            'current_page': _('Warehouse')
        }
        return render(request, f'{BACKEND_TEMPLATES}/store/warehouse/admin.html', context)
    context = {
        'warehouses': warehouses,
        'warehouse_form': AdminCatalogWarehouseForm(),
        'current_page': _('Warehouse')

    }
    return render(request, f'{BACKEND_TEMPLATES}/store/warehouse/admin.html', context)


@authenticated_staf
@staff_only
def AdminCatalogWarehouseUpdate(request, slug):
    warehouses = Warehouse.objects.get(slug=slug)
    if request.method == "POST":
        warehouse_form = AdminCatalogWarehouseForm(request.POST or None, request.FILES or None)
        if warehouse_form.is_valid():
            name = request.POST.get('title')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            country = request.POST.get('country')
            governorates = request.POST.get('governorates')
            city = request.POST.get('city')
            status = request.POST.get('status')
            country = Country.objects.get(id=country)
            governorates = Governorates.objects.get(id=governorates)
            city = City.objects.get(id=city)
            warehouse_objects = Warehouse.objects.get(id=id)
            warehouse_objects.title = name
            warehouse_objects.phone = phone
            warehouse_objects.address = address
            warehouse_objects.country = country
            warehouse_objects.governorates = governorates
            warehouse_objects.city = city
            warehouse_objects.status = status
            warehouse_objects.save()
            messages.success(request, _("Warehouse Add Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogWarehouseList'))
        else:
            
            messages.error(request, _("Warehouse Not Add , Please Try Again"), extra_tags='Category')
    else:
        context = {
            'warehouses': warehouses,
            'warehouse_form': AdminCatalogWarehouseForm(),
            'current_page': _('Warehouse')
        }
        return render(request, f'{BACKEND_TEMPLATES}/store/warehouse/admin.html', context)
    context = {
        'warehouses': warehouses,
        'warehouse_form': AdminCatalogWarehouseForm(),
        'current_page': _('Warehouse')

    }
    return render(request, f'{BACKEND_TEMPLATES}/store/warehouse/admin.html')




@authenticated_staf
@staff_only
def AdminCatalogWarehouseDelete(request, slug):
    warehouses = Warehouse.objects.get(slug=slug)
    warehouses.delete()
    messages.success(request, _("Warehouse Delete Successfully"), extra_tags='Warehouse')
    return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogWarehouseList'))


@authenticated_staf
@staff_only
def AdminCatalogWarehouseDetail(request, slug):
    warehouses = Warehouse.objects.get(slug=slug)
    context = {
        'warehouses': warehouses,
        'current_page': _('Warehouse')
    }
    return render(request, f'{BACKEND_TEMPLATES}/store/warehouse/detail.html', context)


@authenticated_staf
@staff_only
def AdminCatalogWarehouseStatus(request, slug):
    warehouses = Warehouse.objects.get(slug=slug)
    if warehouses.status == 'Active':
        warehouses.status = 'Inactive'
        warehouses.save()
        messages.success(request, _("Warehouse Inactive Successfully"), extra_tags='Warehouse')
    else:
        warehouses.status = 'Active'
        warehouses.save()
        messages.success(request, _("Warehouse Active Successfully"), extra_tags='Warehouse')
    return HttpResponseRedirect(reverse_lazy('catalog:AdminCatalogWarehouseList'))


@authenticated_staf
@staff_only
def AdminCatalogProductsStockList(request, ):
    check_user = User.objects.get(id=request.user.id)
    if check_user.access_level == 'ThirdPartyService' or check_user.access_level == 'Employee':
        if check_user.access_level == 'ThirdPartyService':
            warehouse_cheack = Warehouse.objects.get_or_create(sender_model=ContentType.objects.get(model='User'),
                                                               sender_id=request.user.id,
                                                               owner_model=ContentType.objects.get(model='User'),
                                                               owner_id=request.user.id,
                                                               name='Main Warehouse')
            thirdparty_warehouse = Warehouse.objects.get(
                owner_model=ContentType.objects.get(model='User'),
                owner_id=request.user.id,
            )

        elif check_user.access_level == 'Employee':
            thirdparty_warehouse = Warehouse.objects.get(receiver_id=check_user.id)
        else:
            thirdparty_warehouse = None
            messages.error(request, _("You Don't Have Permission To Access This Page ,Or You dont Have Warehouse Yet"),
                           extra_tags='Product')
            context = {
                'check_user': check_user,
                'thirdparty_warehouse': thirdparty_warehouse,

                'current_page': _('Products'),
            }
            return render(request, f'{BACKEND_TEMPLATES}/thirdparty/services/admin.html', context)

    else:
        messages.error(request, _("You Don't Have Permission To Access This Page"), extra_tags='General')
        return HttpResponseRedirect(reverse_lazy('core:AdminError404'))
    products = ProductsStock.objects.filter(receiver_model=ContentType.objects.get(model='Warehouse'),
                                       receiver_id=thirdparty_warehouse.id, )
    context = {

        'products': products,
        'current_page': _('Stock'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/store/stock/admin.html', context)
