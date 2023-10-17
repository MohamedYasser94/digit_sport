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
from core.forms.subscriptions import AdminCouponForm, AdminMembershipForm, AdminSubscriptionForm
from core.models.core import QrCode
from core.models.subscriptions import Coupon, Membership, Subscription, SubscriptionPayment
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


############## Admin Barcode ##############
# def scan_barcode_from_image(image_path):
#     # Read the image from the provided file path
#     image = cv2.imread(image_path)
#     # Decode barcodes from the image using pyzbar
#     barcodes = pyzbar.decode(image)
#     # Iterate through detected barcodes and extract data from the barcode
#     for barcode in barcodes:
#         # uses UTF-8 encoding
#         barcode_data = barcode.data.decode("utf-8")
#         barcode_type = barcode.type
#         print("Barcode Data:", barcode_data)
#         print("Barcode Type:", barcode_type)
#     return barcodes


# def scan_barcode_from_webcam():
#     # Initialize video capture from the default webcam (index 0)
#     video_capture = cv2.VideoCapture(0)
#     while True:
#         frame = video_capture.read()
#
#         barcodes = pyzbar.decode(frame)
#         for barcode in barcodes:
#             barcode_data = barcode.data.decode("utf-8")
#             barcode_type = barcode.type
#             print("Barcode Data:", barcode_data)
#             print("Barcode Type:", barcode_type)
#
#         # Check for exit condition: Press 'q' to quit the loop
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break
#
#     # Release video capture and close OpenCV windows
#     video_capture.release()
#     cv2.destroyAllWindows()


# scan_barcode_from_webcam()


############## Admin Coupon ##############
@authenticated_staf
@superuser_only
def AdminCouponList(request):
    coupons = Coupon.objects.all()
    if request.method == "POST":
        coupon_form = AdminCouponForm(request.POST or None, request.FILES or None)
        if coupon_form.is_valid():
            coupon_form.save()
            messages.success(request, _("Coupon Add Successfully"), extra_tags='Coupon')
            return HttpResponseRedirect(reverse('core:AdminCouponList'))
        else:
            messages.error(request, _("Coupon Not Add Successfully"), extra_tags='Coupon')
    else:
        coupon_form = AdminCouponForm()
        context = {'coupons': coupons, 'coupon_form': coupon_form, 'current_page': _('Coupon'), }
        return render(request, f'{BACKEND_TEMPLATES}/utilities/coupon/admin.html', context)

    context = {'coupons': coupons, 'coupon_form': coupon_form, 'current_page': _('Coupon'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/coupon/admin.html', context)


@authenticated_staf
@superuser_only
def AdminCouponDetails(request, slug):
    coupon = Coupon.objects.get(slug=slug)
    context = {'coupon': coupon, 'current_page': _('Coupon'), 'prev_Page': _('Coupon'),
        'prev_Page_link': reverse_lazy('core:AdminCouponList'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/coupon/details.html', context)


@authenticated_staf
@superuser_only
def AdminCouponUpdate(request, slug):
    coupon = Coupon.objects.get(slug=slug)
    if request.method == "POST":
        coupon_form = AdminCouponForm(request.POST or None, request.FILES or None, instance=coupon)
        if coupon_form.is_valid():
            coupon_form.save()
            messages.success(request, _("Coupon Update Successfully"), extra_tags='Coupon')
            return HttpResponseRedirect(reverse('core:AdminCouponList'))
        else:
            messages.error(request, _("Coupon Not Update Successfully"), extra_tags='Coupon')
    else:
        coupon_form = AdminCouponForm(instance=coupon)
        context = {'coupon': coupon, 'coupon_form': coupon_form, 'current_page': _('Update'), 'prev_Page': _('Coupon'),
            'prev_Page_link': reverse_lazy('core:AdminCouponList'), }
        return render(request, f'{BACKEND_TEMPLATES}/utilities/coupon/update.html', context)

    context = {'coupon': coupon, 'coupon_form': coupon_form, 'current_page': _('Update'), 'prev_Page': _('Coupon'),
        'prev_Page_link': reverse_lazy('core:AdminCouponList'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/coupon/update.html', context)


@authenticated_staf
@superuser_only
def AdminCouponDelete(request, slug):
    coupon = Coupon.objects.get(slug=slug)
    if request.method == "POST":
        coupon.delete()
        messages.success(request, _("Coupon Delete Successfully"), extra_tags='Coupon')

    return HttpResponseRedirect(reverse('core:AdminCouponList'))


############### Admin Membership  ##############
@authenticated_staf
@superuser_only
def AdminMembershipList(request):
    memberships = Membership.objects.all()
    if request.method == "POST":
        membership_form = AdminMembershipForm(request.POST or None, request.FILES or None)
        if membership_form:
            membership_type = request.POST.get('membership_type')
            duration = request.POST.get('duration')
            duration_period = request.POST.get('duration_period')
            price = request.POST.get('price')
            status = request.POST.get('status')
            membership_object = Membership(membership_type=membership_type, duration=duration,
                                           duration_period=duration_period, price=price, status=status)
            membership_object.save()
            messages.error(request, _("Membership Add Successfully"), extra_tags='Membership')
            return HttpResponseRedirect(reverse('core:AdminMembershipList'))
        else:
            messages.error(request, _("Membership Not Add Successfully"), extra_tags='Membership')
    else:
        membership_form = AdminMembershipForm()
        context = {'memberships': memberships, 'membership_form': membership_form, 'current_page': _('Membership'), }
        return render(request, f'{BACKEND_TEMPLATES}/utilities/membership/admin.html', context)

    context = {'memberships': memberships, 'membership_form': membership_form, 'current_page': _('Membership'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/membership/admin.html', context)


@authenticated_staf
@superuser_only
def AdminMembershipDetails(request, slug):
    membership = Membership.objects.get(slug=slug)
    context = {'membership': membership, 'current_page': _('Membership'), 'prev_Page': _('Membership'),
        'prev_Page_link': reverse_lazy('core:AdminMembershipList'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/membership/details.html', context)


@authenticated_staf
@superuser_only
def AdminMembershipUpdate(request, slug):
    membership = Membership.objects.get(slug=slug)
    if request.method == "POST":
        membership_form = AdminMembershipForm(request.POST or None, request.FILES or None, instance=membership)
        if membership_form.is_valid():
            membership_form.save()
            messages.success(request, _("Membership Update Successfully"), extra_tags='Membership')
            return HttpResponseRedirect(reverse('core:AdminMembershipList'))
        else:
            messages.error(request, _("Membership Not Update Successfully"), extra_tags='Membership')
    else:
        membership_form = AdminMembershipForm(instance=membership)
        context = {'membership': membership, 'membership_form': membership_form, 'current_page': _('Update'),
            'prev_Page': _('Membership'), 'prev_Page_link': reverse_lazy('core:AdminMembershipList'), }
        return render(request, f'{BACKEND_TEMPLATES}/utilities/membership/update.html', context)

    context = {'membership': membership, 'membership_form': membership_form, 'current_page': _('Update'),
        'prev_Page': _('Membership'), 'prev_Page_link': reverse_lazy('core:AdminMembershipList'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/membership/update.html', context)


@authenticated_staf
@superuser_only
def AdminMembershipArchive(request, slug):
    membership = Membership.objects.get(slug=slug)
    if request.method == "POST":
        membership.status = 'Archive'
        membership.save()
        messages.success(request, _("Membership Archive Successfully"), extra_tags='Membership')

    return HttpResponseRedirect(reverse('core:AdminMembershipList'))


############### Admin User Subscription  ##############

@authenticated_staf
@superuser_only
def AdminSubscriptionList(request):
    subscriptions = Subscription.objects.all()
    users = User.objects.all().exclude(is_superuser=True, )
    if request.method == "POST":
        subscription_form = AdminSubscriptionForm(request.POST or None, request.FILES or None)
        if subscription_form:
            user = request.POST.get('user')
            membership = request.POST.get('membership')
            start_date = request.POST.get('start_date')

            status = 'Active'
            membership = Membership.objects.get(id=membership)
            user = User.objects.get(id=user)
            duration = membership.duration
            end_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=duration)

            subscription_object = Subscription(sender_model=ContentType.objects.get(model='User'),
                                               sender_id=request.user.id,
                                               owner_model=ContentType.objects.get(model='User'), owner_id=user.id,
                                               membership=membership, start_date=start_date, end_date=end_date,
                                               expires=end_date, status=status)
            subscription_object.save()
            messages.error(request, _("Subscription Add Successfully"), extra_tags='Subscription')
            return HttpResponseRedirect(reverse('core:AdminSubscriptionList'))
        else:
            messages.error(request, _("Subscription Not Add Successfully"), extra_tags='Subscription')
    context = {'subscriptions': subscriptions, 'users': users, 'subscription_form': AdminSubscriptionForm(),
        'current_page': _('Subscription'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/subscription/admin.html', context)


@authenticated_staf
@superuser_only
def AdminSubscriptionDetails(request, slug):
    subscription = Subscription.objects.get(slug=slug)
    context = {'subscription': subscription, 'current_page': _('Subscription'), 'prev_Page': _('Subscription'),
        'prev_Page_link': reverse_lazy('core:AdminSubscriptionList'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/subscription/details.html', context)


@authenticated_staf
@superuser_only
def AdminSubscriptionUpdate(request, slug):
    subscription = Subscription.objects.get(slug=slug)
    users = User.objects.all().exclude(is_superuser=True)
    if request.method == "POST":
        subscription_form = AdminSubscriptionForm(request.POST or None, request.FILES or None)
        if subscription_form:
            user = request.POST.get('user')
            membership = request.POST.get('membership')
            start_date = request.POST.get('start_date')

            status = request.POST.get('status')
            membership = Membership.objects.get(id=membership)
            user = User.objects.get(id=user)
            duration = membership.duration
            end_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=duration)

            subscription_object = Subscription.objects.get(slug=slug)
            subscription_object.sender_model = ContentType.objects.get(model='User')
            subscription_object.sender_id = request.user.id
            subscription_object.owner_model = ContentType.objects.get(model='User')
            subscription_object.owner_id = user.id
            subscription_object.membership = membership
            subscription_object.start_date = start_date
            subscription_object.end_date = end_date
            subscription_object.expires = end_date
            subscription_object.status = status
            subscription_object.save()
            messages.success(request, _("Subscription Add Successfully"), extra_tags='Subscription')
            return HttpResponseRedirect(reverse('core:AdminSubscriptionList'))
        else:
            messages.error(request, _("Subscription Not Add Successfully"), extra_tags='Subscription')

    context = {'subscription': subscription, 'users': users,
        'subscription_form': AdminSubscriptionForm(instance=subscription), 'current_page': _('Update'),
        'prev_Page': _('Subscription'), 'prev_Page_link': reverse_lazy('core:AdminSubscriptionList'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/subscription/update.html', context)


@authenticated_staf
@superuser_only
def AdminSubscriptionArchive(request, slug):
    subscription = Subscription.objects.get(slug=slug)
    if request.method == "POST":
        subscription.status = 'Archive'
        subscription.save()
        messages.success(request, _("Subscription Archive Successfully"), extra_tags='Subscription')

    return HttpResponseRedirect(reverse('core:AdminSubscriptionList'))


# def export_csv(request):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="members.csv"'
#     writer = csv.writer(response)
#     writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Membership', 'Subscription'])
#     users = User.objects.all().order_by('-id')
#     for user in users:
#         try:
#             membership = Membership.objects.get(user=user)
#             subscription = Subscription.objects.get(membership=membership)
#         except:
#             membership = None
#             subscription = None
#         writer.writerow([user.first_name, user.last_name, user.email, user.phone, membership, subscription])
#     return response


############### Admin  Subscription Payment  ##############

@authenticated_staf
@superuser_only
def AdminSubscriptionPaymentList(request):
    payments = SubscriptionPayment.objects.all()

    context = {'payments': payments, 'current_page': _('Subscription'), }
    return render(request, f'{BACKEND_TEMPLATES}/utilities/payments/admin.html', context)
