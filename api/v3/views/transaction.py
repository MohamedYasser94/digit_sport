from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from core.models.people import Clients
from core.models.shop import Cash, Order
from core.models.transaction import ProductTransaction
from helper.catalogHelper import get_current_user_order, product_list_from_order

User = get_user_model()





@csrf_exempt
def AdminPosPayment(request):
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
def BuyTransaction(request,order_id,user_id,customer_id,count):
    order = Order.objects.get(id=order_id)
    user=User.objects.get(id=user_id)
    customer=Clients.objects.get(id=customer_id)
    description=''
    transaction = ProductTransaction(order=order,user=user,customer=customer,count=count,type='SELL',description=description)
    transaction.save()

def SellTransaction(request,order_id,user_email,customer_id,count):
    print('people',customer_id)
    order = Order.objects.get(id=order_id)
    user = User.objects.get(email=user_email)
    customer = Clients.objects.get(id=customer_id)
    description = 'SEll TransI8ctopn from pos'
    transaction = ProductTransaction(order=order,user=user,customer=customer,count=count,type='SELL',description=description)
    transaction.save()
    order.transaction ='Cash'
    order.save()



def RefundTransaction(request,order,user,customer,count,description):
    try:
        transaction = ProductTransaction.objects.get(order=order,user=user,customer=customer,type='REFUND')
        transaction.order=order
        transaction.user=user
        transaction.customer=customer
        transaction.type = 'REFUND'
        transaction.count=count
        transaction.description= description
        print('not error frm me')
        transaction.save()
    except Exception as e :
       
        print('error frm me')

        transaction = ProductTransaction(order=order,user=user,customer=customer,count=count,type='REFUND',description=description)
        transaction.save()
