import decimal
import logging

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import (HttpResponse,
                         JsonResponse,
                         HttpResponseBadRequest, HttpResponseForbidden)
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from api.v1.serializers.catalog import CategoriesSerializer, ProductsSerializer
from api.v1.serializers.client import ClientsSerializer
from api.v1.serializers.core import CommonProfileSerializer
from api.v1.serializers.order import OrderItemSerializer, OrderSerializer
from api.v1.views.order import GetCurrentCashierOrder
from apps.catalog.models.models import Categories, Products
from apps.catalog.models.vendor import Warehouse
from apps.catalog.views.pos import _show_order

from core.models.people import Clients
from core.models.core import CommonProfile
from core.models.shop import Order, OrderItem, Cash, Cashier
from core.models.transaction import ProductTransaction

from helper.catalogHelper import get_current_user_order, get_can_negative_stock, product_list_from_order

User = get_user_model()


def get_sub_categories(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    category = Clients.objects.all()
    serializer = CategoriesSerializer(category, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def get_sub_category(request, category_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('category_id', category_id)
    category_item = None
    category_items = Categories.objects.filter(id=category_id)
    for rs in category_items:
        category_item = Categories.objects.filter(parent=rs.id)
        print('category_item', category_item)
    serializer = CategoriesSerializer(category_item, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def get_products(request, category_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('category_id', category_id)
    product_item = None
    category = Categories.objects.filter(id=category_id)
    for rs in category:
        product_item = Products.objects.filter(category_id=rs.id)
        print('product_item', product_item)
    serializer = ProductsSerializer(product_item, many=True)
    return JsonResponse(serializer.data, safe=False)


def Clients(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    Clients_list = Clients.objects.all()
    print('Clients', Clients)
    serializer = ClientsSerializer(Clients_list, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def get_Clients(request, Clients_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('Clients_id', Clients_id)

    clients = Clients.objects.filter(id=Clients_id)
    serializer = ClientsSerializer(clients, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def get_Clients_profile(request, clients_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('clients_id', clients_id)
    client = Clients.objects.get(Clientsprofile=clients_id)
    client_address = CommonProfile.objects.get(
        owner_model=ContentType.objects.get(model='Clients'), owner_id=client.id)
    order = get_current_user_order(request.user.id)
    order.Clients = Clients
    order.address = client_address.address
    order.save()

    profile = CommonProfile.objects.get(
        owner_model=ContentType.objects.get(model='Clients'), owner_id=client.id)
    serializer = CommonProfileSerializer(profile, many=True)
    return JsonResponse(serializer.data, safe=False)


def AdminPosRefreshPage(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    cashier = GetCurrentCashierOrder(request)

    print('oderrefresh', cashier)
    cashier = Cashier.objects.get(id=cashier.id)

    order_items = OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'),
                                           ordered='New' )
    for item in order_items:
        product = Products.objects.get(id=item.product.id)
        print('AdminPosRefreshPage' ,product)
        print('AdminPosRefreshPage', item.quantity)
        product.quantity += item.quantity
        product.save()
        item.delete()
        cashier.delete()
    serializer = OrderItemSerializer(order_items, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def updateOrder(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    try:
        order = Order.objects.filter(sender_model=ContentType.objects.get(model='User'), sender_id=request.user.id,
                                     ordered=False, total='0', )
        order.delete()
    except Exception as e:
        pass

       

    order = get_current_user_order(request.user.id)

    if request.method == 'DELETE':
        for item in OrderItem.objects.filter(order=order):
            if item.product.subtract_stock:
                item.product.quantity += 1
                item.product.save()
            item.delete()
        order.total_price = 0
        order.quantity = 0
        order.save()
    serializer = OrderSerializer(order)
    return JsonResponse(serializer.data, safe=False)


def current_order_items(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    order = get_current_user_order(request.user.id)
    order_items = OrderItem.objects.filter(order=order)
    serializer = OrderItemSerializer(order_items, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def current_order_item(request, item_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    order = get_current_user_order(request.user.id)
    print('item_id1', item_id)
    if request.method == 'DELETE':
        order_item = get_object_or_404(OrderItem, id=item_id)
        order_product = order_item.product
        if order_product.subtract_stock:
            order_product.quantity += 1
            order_product.save()
        order.total_price = (
                order.total_price -
                order_item.price).quantize(
            decimal.Decimal('0.01'))
        if order.total_price < 0:
            logging.error("prices below 0! "
                          "You might be running in to the "
                          "10 digit total order price limit")
            order.total_price = 0

        order.save()
        order_item.save()

        order_items = OrderItem.objects.filter(order=order)
        serializer = OrderItemSerializer(order_items, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'ADDONE':

        if product := get_object_or_404(Products, id=item_id):
            ItemIncrement(request, item_id)
        else:
            print('product1', product)

            if product.subtract_stock:
                if product.quantity <= 1 and product.subtract_stock != 'Yes':
                    return JsonResponse('{message: "Insufficient stock"}',
                                        status=status.HTTP_400_BAD_REQUEST, safe=False)

                product.quantity -= 1
                product.save()

            OrderItem.objects.create(order=order, product=product,
                                     price=product.final_price, name=product.title)
            order.total_price = (
                    decimal.Decimal(
                        product.final_price) +
                    order.total_price) \
                .quantize(decimal.Decimal('0.01'))
            order.save()

        order_items = OrderItem.objects.filter(order=order)
        serializer = OrderItemSerializer(order_items, many=True)
        return JsonResponse(serializer.data, safe=False)

    else:
        return HttpResponseBadRequest()


@csrf_exempt
def ItemIncrement(request, item_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    order = get_current_user_order(request.user.id)
    print('item_id', item_id)
    if request.method == 'DELETE':
        product = get_object_or_404(Products, id=item_id)
        print('product', product)

        if product.subtract_stock:
            if product.quantity < 1 and not get_can_negative_stock():
                return JsonResponse('{message: "Insufficient stock"}',
                                    status=status.HTTP_400_BAD_REQUEST)

            product.quantity += 1
            product.save()
            try:
                order_item = OrderItem.objects.get(order=order, product=product)
                print('oder item not found add new', order_item)
                order_item.price -= product.final_price
                order_item.quantity -= 1
                order_item.save()
            except Exception as e:
                pass

               
        order_item = OrderItem.objects.get(order=order, product=product)
        order.total_price = (
                order.total_price -
                order_item.price).quantize(
            decimal.Decimal('0.01'))

        if order.total_price < 0:
            logging.error("prices below 0! "
                          "You might be running in to the "
                          "10 digit total order price limit")
            order.total_price = 0

        order.save()
        if order_item.quantity == 0:
            order_item.delete()

        order_items = OrderItem.objects.filter(order=order)
        serializer = OrderItemSerializer(order_items, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'ADDONE':
        product = get_object_or_404(Products, id=item_id)
        print('product', product)

        if product.subtract_stock:
            if product.quantity <= 1 and not get_can_negative_stock():
                return JsonResponse('{message: "Insufficient stock"}', safe=False,
                                    status=status.HTTP_400_BAD_REQUEST)

            product.quantity -= 1
            product.save()
            try:
                order_item = OrderItem.objects.get(order=order, product=product)
                print('oder item not found add new', order_item)
                order_item.price += product.final_price
                order_item.quantity += 1
                order_item.save()
            except Exception as e:
                OrderItem.objects.create(order=order, product=product,
                                         price=product.final_price, name=product.title)
               

        order.total_price = (
                decimal.Decimal(
                    product.final_price) +
                order.total_price) \
            .quantize(decimal.Decimal('0.01'))
        order.quantity += 1

        order.save()

        order_items = OrderItem.objects.filter(order=order)
        serializer = OrderItemSerializer(order_items, many=True)
        return JsonResponse(serializer.data, safe=False)

    else:
        return HttpResponseBadRequest()


def cash_payment(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    order = get_current_user_order(request.user.id)
    cash, _ = Cash.objects.get_or_create(id=0)

    amount_added = 0

    for product in product_list_from_order(order):
        cash.amount += product.final_price
        amount_added += product.final_price
        cash.save()

    order.done = True
    order.save()
    return JsonResponse({'added': amount_added})


def card_payment(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    order = get_current_user_order(request.user.id)

    order.done = True
    order.save()
    Order.objects.create(user=request.user)

    return HttpResponse()


def BuyTransaction(request, order_id, warehouse_id, Clients_id, count):
    order = Order.objects.get(id=order_id)
    warehouse = Warehouse.objects.get(id=warehouse_id)
    client = Clients.objects.get(id=Clients_id)
    description = ''
    transaction = ProductTransaction(sender_model=ContentType.objects.get(model='Warehouse'), sender_id=warehouse.id,
                                     receiver_model=ContentType.objects.get(model='Clients'), receiver_id=client.id,
                                     order=order, count=count, type='SELL', description=description)
    transaction.save()


def SellTransaction(request, order_id, warehouse_id, client_id, count):
    print('client_id', client_id)
    order = Order.objects.get(id=order_id)
    warehouse = Warehouse.objects.get(id=warehouse_id)
    client = Clients.objects.get(id=client_id)
    description = 'sell transaction from pos'
    transaction = ProductTransaction(sender_model=ContentType.objects.get(model='Warehouse'), sender_id=warehouse.id,
                                     receiver_model=ContentType.objects.get(model='Clients'), receiver_id=client.id,
                                     order=order, count=count, type='SELL', description=description)
    transaction.save()
    order.transaction = 'Cash'
    order.save()


def RefundTransaction(request, order, user, Clients, count, description):
    try:
        transaction = ProductTransaction.objects.get(order=order, user=user, Clients=Clients, type='REFUND')
        transaction.order = order
        transaction.user = user
        transaction.Clients = Clients
        transaction.type = 'REFUND'
        transaction.count = count
        transaction.description = description
        print('not error frm me')
        transaction.save()
    except Exception as e:
       
        print('error frm me')

        transaction = ProductTransaction(order=order, user=user, Clients=Clients, count=count, type='REFUND',
                                         description=description)
        transaction.save()


def cash(request, amount):
    if (request.user.is_authenticated):
        cash, _ = Cash.objects.get_or_create(id=0)
        cash.amount = amount
        cash.save()
        return HttpResponse('')
    else:
        return HttpResponseForbidden('403 Forbidden')


def AdminPosPrintOrder(request, order_id):
    return _show_order(request, order_id, True)
