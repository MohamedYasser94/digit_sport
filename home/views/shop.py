import json
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views import generic, View
from django.views.decorators.csrf import csrf_protect, csrf_exempt



from core.forms.shop import ShopCartForm, CheckoutForm

from core.models.Shipping import CustomerShippingCalculate, ShippingRate
from core.models.core import CommonProfile
from core.models.shop import ShopCart, Wishlist, Order, OrderItem

from home.views.views import FRONTEND_TEMPLATES


User = get_user_model()


@login_required(login_url='/login')  # Check login
def AddToCart(request, id):
    url = request.META.get('HTTP_REFERER')  # get last url
    customer = request.user.id
    current_user = User.objects.get(id=customer)  # Access User Session information

    product = Products.objects.get(pk=id)
    variantid = request.POST.get('variant')  # from variant add to cart
    seller = product.seller.id
    vendor = User.objects.get(id=seller)

    if product.variant != 'None':

        checkinvariant = ShopCart.objects.filter(variant=variantid, user=current_user.id,
                                                 vendor=vendor)  # Check product in shopcart

        if checkinvariant:
            control = 1  # The product is in the cart
        else:
            control = 0  # The product is not in the cart"""
    else:
        checkinproduct = ShopCart.objects.filter(product=id, user=current_user.id,
                                                 vendor=vendor)  # Check product in shopcart
        if checkinproduct:
            control = 1  # The product is in the cart
        else:
            control = 0  # The product is not in the cart"""

    if request.method == 'POST':  # if there is a post
        form = ShopCartForm(request.POST)
        if form.is_valid():
            if control == 1:  # Update  shopcart
                if product.variant == 'None':
                    data = ShopCart.objects.get(product=id, user=current_user.id, vendor=vendor)
                else:
                    data = ShopCart.objects.get(product=id, variant=variantid, user=current_user.id,
                                                vendor=vendor)
                data.quantity += form.cleaned_data['quantity']
                data.save()  # save data
            else:  # Inser to Shopcart
                data = ShopCart()
                data.user_id = current_user.id
                data.product_id = id
                data.variant_id = variantid
                data.vendor = vendor
                data.quantity = form.cleaned_data['quantity']
                data.save()
                # shipping = CustomerShippingCalculate()
                # people = User.objects.get(id=current_user.id)
                # shipping.people = people
                # shipping.cart = data
                # shipping.save()
            messages.success(request, "Product added to Shop Cart ", request.POST)
            
            return HttpResponseRedirect(url)
        else:

          
            
            print(form.errors)
            messages.error(request, "Error")
            return HttpResponseRedirect(url)
    else:  # if there is no post
        if control == 1:  # Update  shopcart
            data = ShopCart.objects.get(product_id=id, user_id=current_user.id)

            data.quantity += 1
            data.save()  #

        else:  # Inser to Shopcart
            data = ShopCart()  # model ile bağlantı kur
            data.user_id = current_user.id
            data.product_id = id
            data.quantity = 1
            data.variant_id = None
            data.vendor = vendor
            data.save()  #
            shipping = CustomerShippingCalculate()
            shipping.customer = current_user
            shipping.cart = data
            shipping.save()
        messages.success(request, "Product added to Shop Cart")
        return HttpResponseRedirect(url)

@csrf_protect
def CartDetails(request):
    sum_product = 0
    sum_variant = 0
    current_user = request.user  # Access User Session information
    cart = ShopCart.objects.filter(user_id=current_user.id)
    for rs in cart:
        if rs.product.variant == 'None':
            sum_product = (rs.product.final_price * rs.quantity)

        else:
            sum_variant = (rs.variant.price * rs.quantity)

    total = sum_product + sum_variant
    context = {'cart': cart,
               'sum_product': sum_product,
               'total': total,
               }
    return render(request, f'{FRONTEND_TEMPLATES}/catalog/shop/cart.html', context)


@csrf_protect
@csrf_exempt
def updateCartItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)
    customer = request.user.id
    product = Products.objects.get(id=productId)
    orderItem, created = ShopCart.objects.get_or_create(user=customer, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    if action == 'delete':
        orderItem.delete()
        messages.success(request, "Your item deleted form Shop Cart.")
    return JsonResponse('Item was added', safe=False)


@login_required(login_url='/login')  # Check login
class WishlistView(generic.View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            wish_item = Wishlist.objects.filter(user=request.user)
            context = {
                'wish_item': wish_item
            }
            return render(self.request, f'{FRONTEND_TEMPLATES}/catalog/shop/wishlist.html', context)
        else:
            return HttpResponseRedirect(reverse('home:HomeIndex'))


@login_required(login_url='/login')  # Check login
def addWishlist(request):
    if request.method == "POST":
        product_var_id = request.POST.get('product-id')
        product_var = Products.objects.get(id=product_var_id)
        try:
            if wish_item := Wishlist.objects.get(user=request.user, product=product_var):
                wish_item.quantity += 1
                wish_item.save()
        except:
            Wishlist.objects.create(user=request.user, product=product_var)
        finally:
            return HttpResponseRedirect(reverse('home:Wishlist'))


def deletefromWishlist(request, id):
    Wishlist.objects.filter(id=id).delete()
    messages.success(request, "Your item deleted form Wishlist.")
    return HttpResponseRedirect(reverse('home:Wishlist'))



@login_required
def Checkout(request):
    current_user = request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id)

    try:
        shipping_init = CustomerShippingCalculate.objects.get(customer=current_user, done_calc=False)
        shipping_init.save()
    except Exception as e:
        print('e',e)
        shipping_init = CustomerShippingCalculate(customer=current_user, done_calc=False, )
        shipping_init.save()


    total = 0
    Subtotal = 0
    shipping_estimate = 0
    shipping_area=None

    for rs in shopcart:

        if rs.product.variant == 'None':
            shipping = CustomerShippingCalculate.objects.get(id=shipping_init.id,customer=current_user, done_calc=False)
            Subtotal += (rs.product.final_price * rs.quantity)
            total += (rs.product.final_price * rs.quantity) + shipping.rate
        else:
            shipping = CustomerShippingCalculate.objects.get(id=shipping_init.id,customer=current_user, done_calc=False)
            Subtotal += (rs.variant.price * rs.quantity)
            total += (rs.variant.price * rs.quantity) + shipping.rate
        shipping_estimate += shipping.rate
        shipping_area = ShippingRate.objects.filter(shipping_category__category=rs.product.category,rate=shipping_estimate )


    if request.method == 'POST':  # if there is a post
        form = CheckoutForm(request.POST)
        if form.is_valid():
            address = request.POST.get('address')
            # address = UserAddress.objects.get(id=address)
            payment_method = request.POST.get('payment_method')
            payment_method = PaymentMethods.objects.get(id=payment_method)
            data = Order()
            data.address = address
            data.payment_method = payment_method
            data.payment_status = 'Pending'
            data.user_id = current_user.id
            data.email = current_user.email
            data.total = total
            data.shipping_amount = shipping_estimate
            data.ip = request.META.get('REMOTE_ADDR')
            ordercode = get_random_string(5).upper()  # random cod
            data.code = ordercode
            data.save()  #
            create_shipping = CustomerShippingCalculate.objects.get(customer=current_user, done_calc=False)
            create_shipping.order=data
            create_shipping.customer=current_user
            create_shipping.done_calc=True
            if shipping_estimate == 0:
                create_shipping.shipping_error='not deliver for your address'
            else:
                for ra in shipping_area:
                    create_shipping.shipping_rate=ra
            create_shipping.save()
            for rs in shopcart:
                detail = OrderItem()
                detail.order_id = data.id  # Orders Id
                detail.product_id = rs.product_id
                vendor =rs.product.seller
                detail.vendor = vendor
                detail.user_id = current_user.id
                detail.quantity = rs.quantity
                detail.tracking = 'trk-' + str(uuid4()).split('-')[1]
                if rs.product.variant == 'None':
                    detail.price = rs.product.final_price
                else:
                    detail.price = rs.variant.price
                detail.variant_id = rs.variant_id
                detail.amount = rs.amount
                detail.save()
                # ***Reduce quantity of sold product from Amount of Product
                if rs.product.variant == 'None' and rs.product.subtract_stock == 'Yes':
                    product = Products.objects.get(id=rs.product_id)
                    product.quantity -= rs.quantity
                    product.save()
                elif rs.product.subtract_stock == 'Yes':
                    variant = Variants.objects.get(id=rs.variant_id)
                    variant.quantity -= rs.quantity
                    variant.save()
                # ************ <> *****************

                # Send Email & Notification
                # try:
                #     product_transaction(request,rs.product_id,rs.quantity,vendor)
                #     create_notification_vendor(request, detail.vendor.vendor, 'NewOrder', extra_id=detail.id,
                #                                extra_info=rs.product)
                #     notify_customer(data)
                #     notify_vendor(detail)
                # except Exception as e:
                #     pass

            ShopCart.objects.filter(user_id=current_user.id).delete()  # Clear & Delete shopcart
            request.session['cart_items'] = 0
            messages.success(request, "Your Orders has been completed. Thank you ")
            return redirect('home:payment', payment_option=payment_method)
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect(reverse('home:Checkout'))

    form = CheckoutForm()
    profile = User.objects.get(id=current_user.id)
    address = CommonProfile.objects.filter(user=current_user)

    context = {'cart': shopcart,
               'Subtotal': Subtotal,
               'total': total,
               'form': form,
               'profile': profile,
               'address': address,
               'shipping_estimate': shipping_estimate,
               'shipping_error': shipping_init,
               'shipping_init':shipping_init,

               }
    return render(request, f'{FRONTEND_TEMPLATES}/catalog/shop/checkout.html', context)


def ShippingOrderCalculate(request):
    shipping_rate = 0
    data = json.loads(request.body)
    print(data)
    customer = User.objects.get(id=request.user.id)
    cart = ShopCart.objects.filter(user=customer)
    AddressId = data['AddressId']
    CalculateId = data['CalculateId']
    action = data['action']
    print('Action:', action)
    print('AddressId:', AddressId)
    print('CalculateId:', CalculateId)
    address = CommonProfile.objects.get(id=AddressId)

    try:
        for rs in cart:
            shipping_area = ShippingRate.objects.filter(shipping_category__category=rs.product.category,
                                                        shipping_zone__city=address.city)
            # shipping_city = ShippingRate.objects.get(shipping_zone__city=address.area,
            #                                             shipping_category__category=rs.product.category)
            # shipping_governorate = ShippingRate.objects.get(shipping_zone__governorates=address.area,
            #                                                    shipping_category__category=rs.product.category)
            print(shipping_area)
            for ra in shipping_area:
                shipping_rate = ra.rate
                # elif shipping_city:
                #     shipping_rate = shipping_city.rate + 10
                # elif shipping_governorate:
                #     shipping_rate = shipping_governorate.rate + 30

                # print(shipping_governorate)
                # print(shipping_city)
            print(shipping_rate)
    except :
        shipping_rate = 0
        shipping_error= 'not deliver for your address'
        messages.error(request, 'not deliver for your address')

    try:
        shipping = CustomerShippingCalculate.objects.get(id=CalculateId,customer=customer, done_calc=False)

        shipping = shipping
        shipping.customer = customer
        shipping.address = address
        shipping.rate = shipping_rate
        if shipping_rate == 0:
            shipping_error = 'not deliver for your address'
            shipping.shipping_error = shipping_error
        shipping.save()
        messages.success(request, 'update')
    except Exception as e:
        print('e',e)
        shipping = CustomerShippingCalculate()
        shipping.customer = customer
        shipping.address = address
        shipping.rate = shipping_rate
        if shipping_rate == 0:
            shipping_error = 'not deliver for your address'
            shipping.shipping_error = shipping_error
        shipping.save()
        messages.success(request, 'create')

    # orderItem, created = ShopCart.objects.get_or_create(user=people, product=product)
    #
    # if action == 'add':
    #     orderItem.quantity = (orderItem.quantity + 1)
    # elif action == 'remove':
    #     orderItem.quantity = (orderItem.quantity - 1)
    # orderItem.save()
    #
    # if orderItem.quantity <= 0:
    #     orderItem.delete()
    #
    # if action == 'delete':
    #     orderItem.delete()
    #     messages.success(request, "Your item deleted form Shop Cart.")
    return JsonResponse('Item was added', safe=False, )


class PaymentView(LoginRequiredMixin, View):
    '''
    Handle Stripe payment (Stripe API)
    '''

    def get(self, request, *args, **kwargs):
        order = Order.objects.filter(user=self.request.user, status='New').last()
        # payment_method = PaymentMethods.objects.get(id=order.payment_method.id)
        payment_method ='Paymob'
        print(payment_method)
        if payment_method == "COD":
            Order.objects.filter(pk=order.pk).update(payment_status='Cash on shipping')
            print('cod')
            return render(request, f'{FRONTEND_TEMPLATES}/catalog/payments/payment_success.html', )
        elif payment_method == 'Stripe':
            print('Stripe')
            return redirect('home:PaymentStripe', )
        elif payment_method == 'Fawry':
            print('Fawry')
            return redirect('home:PaymentFawry', )

        elif payment_method == 'Paymob':
            print(payment_method)
            return redirect('home:PaymentMyPaymob', )
        elif payment_method is None:
            print('none')
            return HttpResponse('error')
        else:
            return HttpResponse('error thing')
