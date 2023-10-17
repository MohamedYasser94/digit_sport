import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from core.models.Payment import Payment
from core.models.shop import Order
from home.views.views import FRONTEND_TEMPLATES


class PaymentMyPaymob(LoginRequiredMixin, View):
    '''
    Handle Stripe payment (Stripe API)
    '''

    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
            'order': order
        }
        return render(self.request, f'{FRONTEND_TEMPLATES}/catalog/payments/PaymentPaymob.html', context)

    def post(self, *args, **kwargs):
        # Create Stripe payment
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        chargeID = stripe_payment(settings.STRIPE_SECRET_KEY, token, order.total, str(order.code))
        if (chargeID is not None):
            order.ordered = True

            # Save the payment
            payment = Payment()
            payment.stripe_charge_id = chargeID
            payment.user = self.request.user
            payment.price = order.total
            payment.paid= 'True'
            payment.save()
            order.payment = payment
            order.save()
            #return render(request, 'payments/payment_success.html', )
            return redirect('/')
        else:
            messages.error(self.request, "Something went wrong with Stripe. Please try again later")
            return redirect('home:PaymentStripe',)





