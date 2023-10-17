from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from core.models.Payment import Payment
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import superuser_only, authenticated_staf


@authenticated_staf
@superuser_only
def AdminPaymentGatewayList(request):
    payment_method = Payment.objects.all()

    context = {
        'payment_method': payment_method,
        'title': _('Payment Gateway'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/payment/payments/admin.html', context)









