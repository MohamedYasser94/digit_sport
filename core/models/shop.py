from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from slugify import slugify

from apps.catalog.models.models import Products, Variants
from core.models.Payment import  Payment

from core.models.core import CommonMediaFiles
from core.models.people import Clients
from helper.modelHelper import Payment_Status, Order_Status, Delivery_By, Payment_Methods

User = get_user_model()


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product

    def get_item_price(self):
        return self.product.final_price


class ShopCart(models.Model):
    user = models.ForeignKey(User, related_name='Clients',on_delete=models.SET_NULL, null=True)
    vendor = models.ForeignKey(User,related_name='ProductVendor', on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True, blank=True)
    variant = models.ForeignKey(Variants, on_delete=models.SET_NULL, null=True,blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField()

    def __str__(self):
        return self.product.title

    @property
    def image(self):
        return CommonMediaFiles.objects.get(type='hero', owner_model=ContentType.objects.get(model='Products'), owner_id=self.product.id)

    @property
    def price(self):
        return (self.product.final_price)



    @property
    def amount(self):
        if self.variant is None:
            return self.quantity * self.product.final_price
        elif self.variant != None:
            return self.quantity * self.variant.price



class Order(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='order_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='order_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='order_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    payment_method = models.CharField(max_length=50, choices=Payment_Methods, null=False, blank=False)
    payment_status = models.CharField( max_length=100, null=False, blank=False, default="Pending", choices=Payment_Status)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    shipping_amount = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, null=True, blank=True)  # 100.00
    total = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, null=True, blank=True)  # 100.00
    quantity = models.IntegerField(default=0,blank=True,null=True)
    status = models.CharField(max_length=10, choices=Order_Status, default='New', null=True, blank=True)
    ordered = models.BooleanField(default=False)
    email = models.CharField(max_length=100)
    ip = models.CharField(blank=True, max_length=20)
    note = models.CharField(blank=True, max_length=100)
    code = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            order_code = f'PUR-{get_random_string(5).upper()}'
            self.code = order_code
            self.slug = slugify(order_code)
        super(Order, self).save(*args, **kwargs)



    def get_previous_bills(self):
        return Order.objects.filter(update_at=timezone.now(), status = 'Completed')

    #total_filter = Order.objects.filter(ordered=True).aggregate(total_price=Sum('total')),

    def get_all_earnings(self):
        return sum(p.total for p in self.get_previous_bills())
    #
    # def total_sale(self):
    #     total = Order.objects.aggregate(TOTAL=Sum('total'))['TOTAL']
    #     return total

class Cashier(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='cashier_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='cashier_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    client = models.ForeignKey(Clients,related_name='cashier_client', on_delete=models.SET_NULL, null=True, blank=True)

    payment_method = models.CharField(max_length=50, choices=Payment_Methods, null=True, blank=True)
    payment_status = models.CharField( max_length=100, null=True, blank=True, default="Pending", choices=Payment_Status)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    total = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, null=True, blank=True)  # 100.00
    quantity = models.IntegerField(default=0,blank=True,null=True)
    ordered = models.CharField(max_length=10, choices=Order_Status, default='New')
    note = models.CharField(blank=True, max_length=100)
    code = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            order_code = f'Cashier-{get_random_string(5).upper()}'
            self.code = order_code
            self.slug = slugify(order_code)
        super(Cashier, self).save(*args, **kwargs)


    def get_previous_bills(self):
        return Order.objects.filter(update_at=timezone.now(), status = 'Completed')

    #total_filter = Order.objects.filter(ordered=True).aggregate(total_price=Sum('total')),

    def get_all_earnings(self):
        return sum(p.total for p in self.get_previous_bills())
    #
    # def total_sale(self):
    #     total = Order.objects.aggregate(TOTAL=Sum('total'))['TOTAL']
    #     return total
class OrderItem(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='item_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='item_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='item_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    product_model = models.ForeignKey(ContentType,related_name='item_product', on_delete=models.CASCADE, null=True, blank=True)
    product_id = models.PositiveIntegerField(null=True, blank=True)
    product = GenericForeignKey('product_model', 'product_id')
    tracking = models.CharField(max_length=10, editable=False,null=True,blank=True,unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=65, decimal_places=2, default=6.99, null=True, blank=True)  # 100.00
    ordered = models.CharField(max_length=10, choices=Order_Status, default='New')
    delivery_by = models.CharField(max_length=10, choices=Delivery_By, default='Self')
    delivery_taken_datetime = models.DateField(null=True, blank=True)
    delivery_person_ip = models.GenericIPAddressField(
        protocol="both", unpack_ipv4=False, null=True, blank=True)
    code = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.title
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            order_code = f'PUR-{get_random_string(5).upper()}'
            self.code = order_code
            self.slug = slugify(order_code)
        super(OrderItem, self).save(*args, **kwargs)



class Refund(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='refund_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='refund_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    total_price = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    quantity = models.IntegerField(default=0)
    transaction = models.CharField(max_length=200, blank=True, null=True, default='REFUND')
    code = models.CharField(max_length=200, blank=False, null=False)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('view_order', args=[self.id])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            refund_code = f'REF-{get_random_string(5).upper()}'
            self.code = refund_code
            self.slug = slugify(refund_code)
        super(Refund, self).save(*args, **kwargs)


class RefundItem(models.Model):
    receiver_model = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    refund = models.ForeignKey(Refund, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

class Cash(models.Model):
    amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)