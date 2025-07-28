import random
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _

from core.forms.core import AdminQrCodeForm

from core.models.core import QrCode

from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import superuser_only, authenticated_staf, staff_only

# Create your views here.

User = get_user_model()


############## Admin QrCode ##############

@authenticated_staf
@staff_only
def AdminQrCodeList(request):
    qrcode = QrCode.objects.all()
    if request.method == "POST":
        qr_form = AdminQrCodeForm(request.POST or None, request.FILES or None)
        if qr_form:
            name = request.POST.get('name')
            url = request.POST.get('url')
            # url = request.build_absolute_uri(reverse(url_pat, args=[slug]))
            random_number = random.randint(1000000, 99999999)

            qr_code = QrCode(owner_model=ContentType.objects.get(model='User'), owner_id=request.user.id,
                              name=name,  url=url,
                             barcode_number=random_number)
            qr_code.save()
            messages.success(request, _("QrCode Add Successfully"), extra_tags='QrCode')
            return HttpResponseRedirect(reverse('core:AdminQrCodeList'))
        else:
            messages.error(request, _("QrCode Not Add Successfully"), extra_tags='QrCode')

    context = {'qrcode': qrcode, 'qr_form': AdminQrCodeForm(), 'current_page': _('QrCode'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/qrcode/admin.html', context)


@authenticated_staf
@staff_only
def AdminQrCodeDetails(request, slug):
    qr = QrCode.objects.get(slug=slug)
    context = {'qr': qr, 'current_page': _('QrCode'), 'prev_Page': _('QrCode'),
        'prev_Page_link': reverse_lazy('core:AdminQrCodeList'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/qrcode/details.html', context)


@authenticated_staf
@staff_only
def AdminQrCodeUpdate(request, slug):
    qr = QrCode.objects.get(slug=slug)
    if request.method == "POST":
        qr_form = AdminQrCodeForm(request.POST or None, request.FILES or None, instance=qr)
        if qr_form.is_valid():
            qr_form.save()
            messages.success(request, _("QrCode Update Successfully"), extra_tags='QrCode')
            return HttpResponseRedirect(reverse('core:AdminQrCodeList'))
        else:
            messages.error(request, _("QrCode Not Update Successfully"), extra_tags='QrCode')

    context = {'qr': qr, 'qr_form': AdminQrCodeForm(), 'current_page': _('Update'), 'prev_Page': _('QrCode'),
        'prev_Page_link': reverse_lazy('core:AdminQrCodeList'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/qrcode/update.html', context)


@authenticated_staf
@staff_only
def AdminQrCodeDelete(request, slug):
    qr = QrCode.objects.get(slug=slug)
    if request.method == "POST":
        qr.delete()
        messages.success(request, _("QrCode Delete Successfully"), extra_tags='QrCode')

    return HttpResponseRedirect(reverse('core:AdminQrCodeList'))



