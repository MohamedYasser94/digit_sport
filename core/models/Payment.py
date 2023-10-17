from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.crypto import get_random_string
from slugify import slugify

from helper.modelHelper import Active_Status, Payment_Gateway, Payment_Status

User = get_user_model()


class Payment(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='payment_sender', on_delete=models.SET_NULL, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='payment_receiver', on_delete=models.SET_NULL, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='payment_owner', on_delete=models.SET_NULL, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    amount = models.FloatField(default=0.00, blank=True, null=True)
    fee = models.FloatField(default=0.00, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=Active_Status, default='Active')
    payment_method = models.CharField(max_length=50, choices=Payment_Status, null=False, blank=False)
    payment_gateway = models.CharField(max_length=100,choices=Payment_Gateway, null=True, blank=True)
    code = models.CharField(unique=True, max_length=20, )
    slug = models.SlugField(null=True, blank=True, max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.code
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Payment-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
            super(Payment, self).save(*args, **kwargs)





class BankAccount(models.Model):
    receiver_model = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    bank_name = models.CharField(max_length=200, blank=True, null=True, )
    account_number = models.CharField(max_length=200, blank=True, null=True, )
    swift_code = models.CharField(max_length=200, blank=True, null=True, )
    account_name = models.CharField(max_length=200, blank=True, null=True, )
    country = models.CharField(max_length=200, blank=True, null=True, )
    account_email = models.CharField(max_length=200, blank=True, null=True, )
    crypto_address = models.CharField(max_length=200, blank=True, null=True, )
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=Active_Status, default='Active')
    code = models.CharField(unique=True, max_length=20, )
    slug = models.SlugField(null=True, blank=True, max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bank_name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'BankAccount-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
            super(BankAccount, self).save(*args, **kwargs)
