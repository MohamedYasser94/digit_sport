import datetime

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.crypto import get_random_string
# Create your models here.
from slugify import slugify
from django.utils.translation import gettext_lazy as _
from helper.modelHelper import Active_Status, MEMBERSHIP_CHOICES, PERIOD_DURATION, Coupon_Type, Subscription_Status, \
    Payment_Status, Payment_Methods

User = get_user_model()

class Membership(models.Model):
    membership_type = models.CharField(choices=MEMBERSHIP_CHOICES, default='Free', max_length=30)
    duration = models.PositiveIntegerField(default=30)
    duration_period = models.CharField(max_length=100, default='Months', choices=PERIOD_DURATION)
    price = models.DecimalField(max_digits=65, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.membership_type

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Membership-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Membership, self).save(*args, **kwargs)

class Subscription(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='subscription_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='subscription_receiver', on_delete=models.CASCADE, null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='subscription_owner', on_delete=models.PROTECT, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    expires = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Subscription_Status, null=True, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.owner

    @property
    def remaining_days(self):
        remaining = ( self.end_date.date() -datetime.datetime.now().date()).days
        return remaining

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Subscription-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Subscription, self).save(*args, **kwargs)


class SubscriptionHistory(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='subscriptionhistory_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='subscriptionhistory_receiver', on_delete=models.CASCADE, null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='subscriptionhistory_owner', on_delete=models.PROTECT, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    expires = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Subscription_Status, null=True, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.owner
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Subscription-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SubscriptionHistory, self).save(*args, **kwargs)


class SubscriptionPayment(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='subscriptionpayment_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='subscriptionpayment_receiver', on_delete=models.CASCADE, null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='subscriptionpayment_owner', on_delete=models.PROTECT, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, null=True, blank=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    expires = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    due = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=Payment_Methods, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=Payment_Status, null=True, blank=True)
    next_payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Subscription_Status, null=True, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.owner
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'SubscriptionPayment-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SubscriptionPayment, self).save(*args, **kwargs)

class Coupon(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='coupon_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='coupon_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    coupon = models.CharField(max_length=50, null=False, blank=False)
    type = models.CharField(max_length=50,choices=Coupon_Type, null=False, blank=False,default='coupon')
    period = models.IntegerField( null=True, blank=True, default=0)
    status = models.CharField(max_length=60, choices=Active_Status, null=True, default='Inactive')
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    used_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.coupon

    def save(self, *args, **kwargs):
        if not self.slug :
            self.slug = slugify(f'{self.type}-{get_random_string(5).upper()}')
        super(Coupon, self).save(*args, **kwargs)


