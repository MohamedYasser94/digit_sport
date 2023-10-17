import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from api.v1.serializers.order import OrderSerializer, OrderItemSerializer
from api.v1.views.transaction import RefundTransaction
from apps.catalog.models.models import Products

from core.models.core import CommonProfile
from core.models.shop import Order, OrderItem, Refund, RefundItem
from core.models.transaction import ProductTransaction
from helper.catalogHelper import get_can_negative_stock


@login_required(login_url='/dashboard/login')
def OrdersList(request):
    commission = None
    order = Order.objects.all()

    context = {
        'order': order,

    }
    return render(request, 'order/orders/admin.html', context)

@login_required(login_url='/dashboard/login')
def OrdersDetails(request,slug):

    order = Order.objects.get(slug=slug)
    order_item = OrderItem.objects.filter(order=order)
    customer_profile = CommonProfile.objects.get(customer=order.customer)
    transaction =ProductTransaction.objects.get(order=order)

    context = {
        'order': order,
        'order_item': order_item,
        'customer_profile': customer_profile,
        'transaction': transaction,

    }
    return render(request, 'order/orders/details.html', context)

@login_required(login_url='/dashboard/login')
def RefundList(request):
    commission = None
    refund = Refund.objects.all()

    context = {
        'refund': refund,

    }
    return render(request, 'order/refund/admin.html', context)

@login_required(login_url='/dashboard/login')
def RefundDetails(request,slug):

    order = Order.objects.get(slug=slug)
    order_item = OrderItem.objects.filter(order=order)
    customer_profile = CommonProfile.objects.get(customer=order.customer)
    transaction =ProductTransaction.objects.get(order=order)

    context = {
        'order': order,
        'order_item': order_item,
        'customer_profile': customer_profile,
        'transaction': transaction,

    }
    return render(request, 'order/refund/details.html', context)
@csrf_exempt
def RefundUpdateOrder(request,item_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('catch',item_id)
    order_item = OrderItem.objects.get(id=item_id)
    try:

        order = Order.objects.get(orderitem=order_item)
        print('catch2', order)
        serializer = OrderSerializer(order ,many=True)
        return JsonResponse(serializer.data, safe=False)

    except Exception as e :
        order = Order.objects.get(orderitem=order_item)
        print('order from refund order',order)
       
    if request.method == 'DELETE':
        for item in OrderItem.objects.filter(order=order):
            if item.product.subtract_stock:
                item.product.quantity += 1
                item.product.save()
            item.delete()
        order.total_price = 0
        order.quantity =0
        order.save()
    else:
        order = Order.objects.filter(orderitem=order_item)
        print('order return from else')
    serializer = OrderSerializer(order ,many=True)
    return JsonResponse(serializer.data,safe=False )


def refundUpdateOrderItems(request,order_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    order =  Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    serializer = OrderItemSerializer(order_items, many=True)
    return JsonResponse(serializer.data, safe=False)


@login_required(login_url='/dashboard/login')
@csrf_exempt
def getRefundOrder(request, slug):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('category_id', slug)
    order = None
    try:
        order = Order.objects.filter(slug=slug)
    except Exception as e :
        pass
       

    serializer = OrderSerializer(order, many=True)
    return JsonResponse(serializer.data, safe=False)
@login_required(login_url='/dashboard/login')
@csrf_exempt
def getRefundOrderItems(request, slug):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('category_id', slug)
    order_items = None
    try:
        order = Order.objects.filter(slug=slug)
        for rs in order:
            order_items = OrderItem.objects.filter(order=rs)
    except Exception as e:
        pass
       

    serializer = OrderItemSerializer(order_items, many=True)
    return JsonResponse(serializer.data, safe=False)


@login_required(login_url='/dashboard/login')
@csrf_exempt
def RefundOrderItem(request,item_id,product_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('item_id',item_id)
    print('product_id',product_id)

    order_item = OrderItem.objects.get(id=item_id)
    if not order_item:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    else:
        order = Order.objects.get(orderitem=order_item)
        print('product_id2', product_id)
        print('item_id', item_id)
        if request.method == 'DELETE':
            product = get_object_or_404(Products, id=product_id)
            print('product', product)

            if product.subtract_stock:
                if product.quantity < 1 and not get_can_negative_stock():
                    return JsonResponse('{message: "Insufficient stock"}',
                                        status=status.HTTP_400_BAD_REQUEST)

                product.quantity += 1
                product.save()
                order_item = OrderItem.objects.get(id=item_id, product=product)
                print('oder quantity', order_item.quantity)
                order_item.price -= product.final_price
                order_item.quantity -= 1
                order_item.save()
            order.total_price = order.total_price - product.final_price
            print('transiction return')
            order.quantity -=1


            if order.total_price <= 0:
                logging.error("prices below 0! "
                              "You might be running in to the "
                              "10 digit total order price limit")
                order.total_price = 0

            order.save()
            try:
                print('TRY')
                refund = Refund.objects.get(order=order)
                refund.order=order
                refund.user=order.user
                refund.customer=order.customer
                refund.total_price=order.total_price
                refund.quantity=order.quantity
                refund.transaction='REFUND'
                refund.save()
                try:
                    refund_item = RefundItem.objects.get(refund=refund,product=product)
                    refund_item.product=product
                    refund_item.price +=product.final_price
                    refund_item.quantity +=1
                    refund_item.title=product.title
                    refund_item.save()
                except Exception as e :
                    print('Not Same Order',e)
                    price = product.final_price
                    refund_item = RefundItem(refund=refund, product=product, price=price, quantity=1,
                                             name=product.title)
                    refund_item.save()



            except Exception as e:
               
                print('EXEPTION')
                refund =Refund(order=order,user=order.user,customer=order.customer,
                               total_price=order.total_price,quantity=order.quantity,transaction='REFUND')
                refund.save()
                price=product.final_price
                refund_item=RefundItem(refund=refund,product=product,price=price,quantity=1,name=product.title)
                refund_item.save()

            description='Refund  from Refund'
            RefundTransaction(request, order, order.user, order.customer, order.quantity, description)
            if order_item.quantity == 0:
                order_item.delete()

            order_items = OrderItem.objects.filter(order=order)
            serializer = OrderItemSerializer(order_items, many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            return HttpResponseBadRequest('{message: "Insufficient stock"}',
                                        status=status.HTTP_400_BAD_REQUEST)


@login_required(login_url='/dashboard/login')
def RefundAdd(request):

    order = Order.objects.all()
    order_list = list(order.values('id', 'user','people','code'))

    context = {
        'order_list': order_list,

    }
    return render(request, 'order/refund/add.html', context)
