import decimal
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import (HttpResponse,
                         HttpResponseForbidden,
                         HttpResponseBadRequest)
from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _

from apps.catalog.models.models import Products, Categories
from core.forms.people import AdminClientsForm
from core.forms.core import AdminCommonProfileForm
from core.models.people import Clients
from core.models.core import CommonMediaFiles
from core.models.shop import Order, OrderItem, Cashier
from helper.catalogHelper import setup_handling, get_company, get_can_negative_stock, \
    product_list_from_order
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only


@authenticated_staf
@staff_only
def AdminCatalogPos(request):
    # Sort products by colour, then by title
    product_list=[]
    try:
        order = Order.objects.filter( total=0, )
        order.delete()
    except Exception as e :
        order = Order.objects.all()
       

    category = Categories.objects.all()
    category_list = list(category.values('title', 'id'))
    products = Products.objects.all()
    for product in products:
        image = CommonMediaFiles.objects.get(type='hero',
                                             owner_model=ContentType.objects.get(model='Products'),
                                             owner_id=product.id)
        product_list.append(
            {"product": product, "image": image, })



    customer = Clients.objects.all()
    customer_list = list(customer.values('name', 'id'))

    customer_form = AdminClientsForm()
    profile_form = AdminCommonProfileForm()
    context = {
        'customer_form': customer_form,
        'profile_form': profile_form,
        'categorys':category,
        'products':products,
        'product_list': product_list,
        'category_list': category_list,
        'customer_list': customer_list,
        'current_page': _('Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/pos/pos.html',context )

def AdminCataloTESTposPAge(request):
    # Sort products by colour, then by title
    product_list=[]
    try:
        order = Order.objects.filter( total=0, )
        order.delete()
    except Exception as e :
        order = Order.objects.all()
       

    category = Categories.objects.all()
    category_list = list(category.values('title', 'id'))
    products = Products.objects.all()
    for product in products:
        image = CommonMediaFiles.objects.get(type='hero',
                                             owner_model=ContentType.objects.get(model='Products'),
                                             owner_id=product.id)
        product_list.append(
            {"product": product, "image": image, })



    customer = Clients.objects.all()
    customer_list = list(customer.values('name', 'id'))

    customer_form = AdminClientsForm()
    profile_form = AdminCommonProfileForm()
    context = {
        'customer_form': customer_form,
        'profile_form': profile_form,
        'products':products,
        'product_list': product_list,
        'category_list': category_list,
        'customer_list': customer_list,
        'current_page': _('Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/pos/update.html',context )
def _addition_no_stock(request):
    cash, current_order, currency = setup_handling(request)

    total_price = current_order.total_price
    list = OrderItem.objects.filter(order=current_order)
    context = {
        'list': list,
        'total_price': total_price,
        'cash': cash,
        'succesfully_payed': False,
        'payment_error': False,
        'amount_added': 0,
        'currency': currency,
        'stock_error': True,
    }
    return render(request, 'pos/addition.html', context=context)


# @login_required
def addition(request):
    cash, current_order, currency = setup_handling(request)

    total_price = current_order.total_price
    list = OrderItem.objects.filter(order=current_order)
    context = {
        'list': list,
        'total_price': total_price,
        'cash': cash,
        'succesfully_payed': False,
        'payment_error': False,
        'amount_added': 0,
        'currency': currency,
        'stock-error': False,
    }
    return render(request, 'catalog/pos/addition.html', context=context)


def _show_order(request, order_id, should_print):
    currency = 'Egp'
    cashier = get_object_or_404(Cashier, id=order_id)
    items = OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'), sender_id=cashier.id,
                                           ordered='New' )
    company = 'Digit Hup'

    context = {
        'items': items,
        'order': cashier,
        'currency': currency,
        'company': company,
        'print': should_print
    }

    return render(request, 'good/pos/invoice/print_invoice.html', context=context)


# @login_required
def view_order(request, order_id):
    return _show_order(request, order_id, False)


# @login_required



# @login_required
def print_current_order(request):
    # Get the user. This is quite a roundabout, sorry
    usr = User.objects.get_by_natural_key(request.user.username)
    q = Order.objects.filter(user=usr) \
        .order_by('-last_change')

    # This is an edge case that would pretty much never occur
    if q.count() < 1:
        return HttpResponseBadRequest
    return _show_order(request, q[0].id, True)


# @login_required
def order_amount(request):
    _, current_order, _ = setup_handling(request)
    return HttpResponse(current_order.total_price)


# @login_required
def order_add_product(request, product_id):
    _, current_order, _ = setup_handling(request)

    if product_id.isdigit():
        try:
            to_add = Products.objects.get(id=product_id)
        except ObjectDoesNotExist:
            to_add = get_object_or_404(Products, code=product_id)

    else:
        to_add = get_object_or_404(Products, code=product_id)

    # Make sure we can't go under 0 stock
    if to_add.stock_applies:
        if to_add.stock < 1 and not get_can_negative_stock():
            return _addition_no_stock(request)

        to_add.stock -= 1
        to_add.save()

    OrderItem.objects.create(order=current_order, product=to_add,
                             price=to_add.price, name=to_add.name)
    current_order.total_price = (
            decimal.Decimal(
                to_add.price) +
            current_order.total_price) \
        .quantize(decimal.Decimal('0.01'))
    current_order.save()

    return addition(request)


# @login_required
def order_remove_product(request, item_id):
    cash, current_order, _ = setup_handling(request)
    order_item = get_object_or_404(OrderItem, id=item_id)
    order_product = order_item.product

    if order_product.subtract_stock:
        order_product.quantity += 1
        order_product.save()

    current_order.total_price = (
            current_order.total_price -
            order_item.price).quantize(
        decimal.Decimal('0.01'))

    if current_order.total_price < 0:
        logging.error("prices below 0! "
                      "You might be running in to the "
                      "10 digit total order price limit")
        current_order.total_price = 0

    current_order.save()
    order_item.delete()

    # I only need default values.
    return addition(request)


@login_required
def reset_order(request):
    cash, current_order, _ = setup_handling(request)

    for item in OrderItem.objects.filter(order=current_order):
        if item.product.stock_applies:
            item.product.stock += 1
            item.product.save()
        item.delete()

    current_order.total_price = 0
    current_order.save()

    # I just need default values. Quite useful
    return addition(request)


@login_required
def payment_cash(request):
    succesfully_payed = False
    payment_error = False
    amount_added = 0
    cash, current_order, currency = setup_handling(request)

    for product in product_list_from_order(current_order):
        cash.amount += product.price
        amount_added += product.price
        cash.save()

    current_order.done = True
    current_order.save()
    current_order = Order.objects.create(user=request.user)
    succesfully_payed = True

    total_price = current_order.total_price
    list = OrderItem.objects.filter(order=current_order)
    context = {
        'list': list,
        'total_price': total_price,
        'cash': cash,
        'succesfully_payed': succesfully_payed,
        'payment_error': payment_error,
        'amount_added': amount_added,
        'currency': currency,
    }
    return render(request, 'pos/addition.html', context=context)


@login_required
def payment_card(request):
    succesfully_payed = False
    payment_error = False
    cash, current_order, currency = setup_handling(request)

    current_order.done = True
    current_order.save()
    current_order = Order.objects.create(user=request.user)
    succesfully_payed = True

    total_price = current_order.total_price
    list = OrderItem.objects.filter(order=current_order)
    context = {
        'list': list,
        'total_price': total_price,
        'cash': cash,
        'succesfully_payed': succesfully_payed,
        'payment_error': payment_error,
        'amount_added': 0,
        'currency': currency,
    }
    return render(request, 'pos/addition.html', context=context)


# We can't use the `@login_required` decorator here because this
# page is never shown to the user and only used in AJAX requests
def pos_category(request, category):
    print('category', category)
    if (request.user.is_authenticated):
        category, _ = Categories.objects.get(id=category)

        return HttpResponse('')
    else:
        return HttpResponseForbidden('403 Forbidden')





@login_required
def view_stock(request):
    stock_products = Products.objects.all()
    company = get_company()

    context = {
        'product': stock_products,
        'company': company
    }

    return render(request, 'catalog/pos/stock.html', context=context)

# class CustomerCreate(CreateView):
#     model = Categories
#     # fields = '__all__'
#     form_class = AdminProductCategoryForm
#     template_name = 'catalog/category/add.html'
#     success_url = reverse_lazy('core:AdminCategory')
#
#     @method_decorator(superuser_only)
#     def dispatch(self, *args, **kwargs):
#         return super(CustomerCreate, self).dispatch(*args, **kwargs)
