from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.crypto import get_random_string
from slugify import slugify

from core.models.Shipping import Courier
from helper.modelHelper import Transaction_Money_Type, Transaction_Product_Type, Transaction_Coast_Type, \
    Transaction_Operation

User = get_user_model()



class ProductTransaction(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='product_transaction_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='product_transaction_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    transaction_type = models.CharField(choices=Transaction_Product_Type, max_length=255)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction_type

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TRA-PRODUCT{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ProductTransaction, self).save(*args, **kwargs)

class ShippingTransaction(models.Model):
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True,)
    earning = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    wallet = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    withdraw = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    withdraw_done = models.BooleanField(default=False)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.courier

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TRA-SHIPPING{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ShippingTransaction, self).save(*args, **kwargs)


