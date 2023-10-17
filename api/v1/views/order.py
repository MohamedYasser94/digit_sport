import decimal
import logging
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, QueryDict
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.generics import get_object_or_404
from api.v1.serializers.core import CommonProfileSerializer
from api.v1.serializers.order import OrderItemSerializer, CashierSerializer
from apps.catalog.models.models import Products
from apps.wallet.views.common_transaction import AdminMoneyTransaction



from core.models.core import CommonProfile
from core.models.shop import OrderItem, Cashier
from core.views.billing import billing_transaction, get_transaction
from core.views.people import AdminClientCommonCreate

from helper.catalogHelper import get_current_user_order


def GetCurrentCashierOrder(request):
    # print('GetCurrentCashierOrder')
    """
    Gets the order for the current user.
    """
    cashier_user = request.user.id
    print(
        'cashier_user',cashier_user
    )


    try:
        print(2)
        cashier = Cashier.objects.get(sender_model=ContentType.objects.get(model='User'), sender_id=cashier_user,
                                      ordered='New'
                                      )


    except Exception as e:
        print(3)
        print('GetCurrentCashierOrder', e)
        AdminClientCommonCreate(request, 'Walk-in Customer', 'Walk-in Customer', None, None, 'walkIn', 'Active',
                                '123456', 'Home',
                                'Walk-in Customer', None, None, None, None, None, None)

        cashier = Cashier.objects.create(sender_model=ContentType.objects.get(model='User'), sender_id=cashier_user,
                                         ordered='New', client=Clients.objects.get(name='Walk-in Customer'))


    return cashier


def GetCurrentCashierDraft(request):
    # print('GetCurrentCashierOrder')
    """
    Gets the order for the current user.
    """
    cashier_user = request.user

    try:
        cashier = Cashier.objects.get(sender_model=ContentType.objects.get(model='User'), sender_id=cashier_user.id,
                                      ordered='Draft')
        print('cashier draft', cashier)


    except Exception as e:
        BadRequest = {
            'status': 'Bad Request',
            'message': 'No Draft Found'
        }
        return JsonResponse(BadRequest, status=status.HTTP_400_BAD_REQUEST)

    return cashier


@csrf_exempt
def AdminAddProductToCashier(request, item_id):
    # print('AdminAddProductToCashier')
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    cashier = GetCurrentCashierOrder(request)

    # print('AdminAddProductToCashier request', print(request.method))
    if request.method != 'GET':
        return HttpResponseBadRequest()
    if product := get_object_or_404(Products, id=item_id):
        AdminPosCashierItemIncrement(request, item_id)
    else:
        print('AdminAddProductToCashier product1', product)

        if product.subtract_stock:
            if product.quantity <= 1 and product.subtract_stock != 'Yes':
                return JsonResponse('{message: "Insufficient stock"}',
                                    status=status.HTTP_400_BAD_REQUEST, safe=False)

            product.quantity -= 1
            product.save()
        print('AdminAddProductToCashier product2', product)

        OrderItem.objects.create(sender_model=ContentType.objects.get(model='Cashier'), sender_id=cashier.id,
                                 owner_model=ContentType.objects.get(model=product.owner_model.model),
                                 owner_id=product.owner_id,
                                 product=product, amount=product.final_price, quantity=1)
        cashier.total = (decimal.Decimal(product.final_price) + cashier.total).quantize(decimal.Decimal('0.01'))

    order_items = OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'),
                                           sender_id=cashier.id, )
    serializer = OrderItemSerializer(order_items, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def AdminPosCashierItemIncrement(request, item_id):
    print('AdminPosCashierItemIncrement')
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    cashier = GetCurrentCashierOrder(request)
    quantity = request.GET.get('quantity')
    quantity_type = request.GET.get('quantityType')
    print('quantity_type', quantity_type, )
    put = QueryDict(request.body)
    quantity_delete = put.get('quantity')

    print('request', request.method, )
    print('quantity', quantity, '::', quantity_delete)
    print('quantity_type', quantity_type)

    if request.method == 'DELETE':
        product = get_object_or_404(Products, id=item_id)

        if product.subtract_stock == 'Yes':
            if product.quantity < 1:
                return JsonResponse('{message: "Insufficient stock"}',
                                    status=status.HTTP_400_BAD_REQUEST)

            product.quantity += int(quantity_delete)
            product.save()
            try:

                order_item = OrderItem.objects.get(sender_model=ContentType.objects.get(model='Cashier'),
                                                   sender_id=cashier.id, ordered='New', product=product)

                order_item.amount -= product.final_price * order_item.quantity
                order_item.quantity -= order_item.quantity
                order_item.save()
            except Exception as e:

                print('order item not found add new e', e)
        order_item = OrderItem.objects.get(sender_model=ContentType.objects.get(model='Cashier'), sender_id=cashier.id,
                                           product=product)

        cashier.total = (cashier.total - order_item.amount).quantize(decimal.Decimal('0.01'))
        if cashier.total < 0:
            logging.error("prices below 0! "
                          "You might be running in to the "
                          "10 digit total order price limit")
            cashier.total = 0

        cashier.save()
        if order_item.quantity == 0:
            order_item.delete()

        order_items = OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'),
                                               sender_id=cashier.id, )
        serializer = OrderItemSerializer(order_items, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'GET':
        product = get_object_or_404(Products, id=item_id)
        new_quantity = 0

        if product.subtract_stock == 'Yes':
            if product.quantity <= 1:
                return JsonResponse('{message: "Insufficient stock"}', safe=False,
                                    status=status.HTTP_400_BAD_REQUEST)

            try:
                print('try get')
                quantity = int(quantity)
                order_quantity = 0
                order_amount = 0
                ProductQuantityCalculation(request, cashier.id, item_id, quantity, quantity_type)



            except Exception as e:
                print('try get Error', e)
                # print('content', product.owner_model.model)
                # print('content', product.owner_id)
                # print('content', product.owner)
                # print('cashier', cashier)
                quantity = 1
                OrderItem.objects.create(sender_model=ContentType.objects.get(model='Cashier'), sender_id=cashier.id,
                                         receiver_model=ContentType.objects.get(model=product.owner_model.model),
                                         receiver_id=product.owner_id,
                                         product=product, amount=product.final_price, quantity=quantity)
                product.quantity -= 1

                product.save()

                # print('OrderItem.objects.create', e)

        order_item = OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'),
                                              sender_id=cashier.id, ordered='New', )

        # cashier.total = (decimal.Decimal(product.final_price) + cashier.total).quantize(decimal.Decimal('0.01'))
        cashier.total = order_item.aggregate(TOTAL=Sum('amount'))['TOTAL']
        cashier.quantity = order_item.aggregate(TOTAL=Sum('quantity'))['TOTAL']
        cashier.save()

        order_items = OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'),
                                               sender_id=cashier.id, )
        serializer = OrderItemSerializer(order_items, many=True)
        return JsonResponse(serializer.data, safe=False)

    else:
        return HttpResponseBadRequest()


def ProductQuantityCalculation(request, cashier, product, quantity, quantity_type):
    print('ProductQuantityCalculation')
    print('cashier', cashier)
    print('product', product)
    print('quantity', quantity)
    quantity = int(quantity)
    order_quantity = 0
    order_amount = 0
    product_quantity = 0
    cashier = Cashier.objects.get(id=cashier)
    product = Products.objects.get(id=product)
    order_item = OrderItem.objects.get(sender_model=ContentType.objects.get(model='Cashier'),
                                       sender_id=cashier.id,
                                       ordered='New', product=product.id, )
    print('order_item', order_item.quantity)
    item_quantity = int(order_item.quantity)
    if quantity_type == 'Add':
        print('Add Increment')
        order_quantity = order_item.quantity + 1
        product.quantity -= 1
        product.save()
        print('order_quantity', order_quantity)
        order_amount = int(order_item.amount) + int(product.final_price)
    else:
        if quantity_type == 'Increment' and quantity > item_quantity:
            print('Increment')
            order_quantity = order_item.quantity + 1
            product.quantity -= 1
            product.save()
            print('order_quantity', order_quantity)
            order_amount = int(order_item.amount) + int(product.final_price)
        elif quantity_type == 'Increment' and quantity < item_quantity:
            print('Decrement')
            order_quantity = order_item.quantity - 1
            product.quantity += 1
            product.save()
            print('order_quantity', order_quantity)
            order_amount = int(order_item.amount) - int(product.final_price)
    order_item.quantity = order_quantity
    order_item.amount = order_amount

    order_item.save()


@csrf_exempt
def AdminPosUpdateCashierOrder(request):
    print('AdminPosUpdateCashierOrder1')
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)


    cashier = GetCurrentCashierOrder(request)

    if request.method == 'DELETE':
        for item in OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'),
                                             sender_id=cashier.id, ):
            if item.product.subtract_stock:
                item.product.quantity += item.quantity
                item.product.save()
            item.delete()

        cashier.total = 0
        cashier.save()

    serializer = CashierSerializer(cashier, )
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def AdminPosUpdateCashierDraft(request):
    print('AdminPosUpdateCashierDraft')
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    cashier = Cashier.objects.filter(sender_model=ContentType.objects.get(model='User'), sender_id=request.user.id,
                                     ordered='Draft')
    print('cashier', cashier)

    if request.method == 'DELETE':
        for item in OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'),
                                             sender_id=cashier.id, ):
            if item.product.subtract_stock:
                item.product.quantity += item.quantity
                item.product.save()
            item.delete()

        cashier.total = 0
        cashier.save()

    serializer = CashierSerializer(cashier, many=True)
    return JsonResponse(serializer.data, safe=False)
@csrf_exempt
def AdminPosGetCashierDraft(request,order_code):
    print('AdminPosUpdateCashierDraft')
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('cashier', order_code)

    cashier = Cashier.objects.get(code=order_code)

    print('cashier', cashier)

    if request.method == 'DELETE':
        for item in OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'),
                                             sender_id=cashier.id, ):
            if item.product.subtract_stock:
                item.product.quantity += item.quantity
                item.product.save()
            item.delete()

        cashier.total = 0
        cashier.save()
    order_items = OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'),
                                             sender_id=cashier.id, )
    serializer = OrderItemSerializer(order_items, many=True)

    return JsonResponse(serializer.data, safe=False)
@csrf_exempt
def AdminPosCashierItems(request):
    # print('AdminPosCashierItems', )
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    cashier = GetCurrentCashierOrder(request)

    order_items = OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'),
                                           sender_id=cashier.id, )
    serializer = OrderItemSerializer(order_items, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def AdminPosDeleteOrderItem(request, item_id):
    print('AdminPosDeleteOrderItem', )
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



    else:
        return HttpResponseBadRequest()


@csrf_exempt
def AdminPosDraftCashierOrder(request, order_id):
    print('AdminPosDraftCashierOrder')
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    put = QueryDict(request.body)
    client_id = put.get('client_id')
    client = Clients.objects.get(id=client_id)
    print('request', request.method, )
    print('client_id', client_id)

    cashier = Cashier.objects.get(id=order_id)

    print('order_id', order_id)

    try:
        order_item = OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'),
                                              sender_id=cashier.id,
                                              ordered='New')
        print('item', order_item)
        for item in order_item:
            client_id = put.get('client_id')

            item.receiver_model = ContentType.objects.get(model='Clients')
            item.receiver_id = client_id
            item.ordered = 'Draft'
            item.save()
            print('item', item)

        print('cashier', cashier.ordered)
        billing_transaction(request, 'Cashier', cashier.id, cashier.total, 0, None)
        transaction = get_transaction(request, 'Cashier', cashier.id)
        print('get_transaction', transaction)
        AdminMoneyTransaction(request, 'Cashier', cashier.id, 'Billing', transaction.id, 'Sell', cashier.total)

        cashier.receiver_model = ContentType.objects.get(model='MoneyTransaction')
        cashier.receiver_id = transaction.id
        cashier.client = client
        cashier.ordered = 'Draft'
        cashier.save()
        draft = Cashier.objects.filter(sender_model=ContentType.objects.get(model='User'), sender_id=request.user.id,
                                       ordered='Draft',id=order_id)
        new_cashier = GetCurrentCashierOrder(request)
        # print('new_cashier', new_cashier)

        serializer = CashierSerializer(draft, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        print('AdminPosDraftCashierOrder', e)
        return HttpResponseBadRequest()

@csrf_exempt
def AdminCashierClientProfile(request, client_id):
    print('AdminCashierClientProfile')
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('client_id', client_id)
    client = Clients.objects.get(id=client_id)
    # user_id = request.user.id
    cashier = GetCurrentCashierOrder(request)

    cashier.client = client

    cashier.save()
    client_profile = CommonProfile.objects.filter(
        owner_model=ContentType.objects.get(model='Clients'), owner_id=client_id)

    serializer = CommonProfileSerializer(client_profile, many=True)
    return JsonResponse(serializer.data, safe=False)



@csrf_exempt
def AdminPosCashPayment(request,order_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)


    cashier = Cashier.objects.get(id=order_id)
    cashier.ordered='Completed'
    cashier.payment_status='Completed'
    cashier.save()
    items = OrderItem.objects.filter(sender_model=ContentType.objects.get(model='Cashier'), sender_id=cashier.id,
                                     )
    for item in items:
        item.ordered = 'Completed'
        item.receiver_model = ContentType.objects.get(model='Clients')
        item.receiver_id = cashier.client.id
        item.save()

    AdminMoneyTransaction(request, 'Cashier', cashier.id, 'User', request.user.id, 'Sell', cashier.total)
    print('cash',cashier)
    print('money_transaction',cashier.id)

    serializer = CashierSerializer(cashier, )
    return JsonResponse(serializer.data, safe=False)