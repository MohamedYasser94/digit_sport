from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify

from apps.catalog.models.models import Categories
from core.models.core import CommonProfile
from core.models.localization import Country, Governorates, City, Area
from helper.modelHelper import Commission_System, Active_Status, Shipping_Status, Waiting_Status

User = get_user_model()


class CommissionSystem(models.Model):
    title = models.CharField(max_length=255)
    commission = models.DecimalField(max_digits=65, decimal_places=2, default=9.99, null=True, blank=True)
    detail = models.CharField(max_length=755, blank=True, null=True)
    commission_type = models.CharField(max_length=50, choices=Commission_System)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.commission_type


class CommissionCategory(models.Model):
    commission_type = models.ForeignKey(CommissionSystem, on_delete=models.CASCADE, null=False)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, null=False)
    commission = models.DecimalField(max_digits=65, decimal_places=2, default=9.99, null=True, blank=True)
    commission_status = models.CharField(max_length=20, choices=Active_Status, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.commission_type.title


class ShippingZone(models.Model):
    zone_name = models.CharField(max_length=128, null=True, blank=True, unique=True)
    commission_type = models.ForeignKey(CommissionSystem, on_delete=models.CASCADE, null=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=False)
    governorates = models.ManyToManyField(Governorates)
    city = models.ManyToManyField(City)
    area = models.ManyToManyField(Area)
    safe = models.BooleanField(default=True)
    rate = models.DecimalField(max_digits=65, decimal_places=2, default=9.99, null=True, blank=True)
    rate_status = models.CharField(max_length=20, choices=Shipping_Status, default='Active')
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.zone_name} {str(self.rate)}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.zone_name)
        super(ShippingZone, self).save(*args, **kwargs)


class ShippingCategory(models.Model):
    commission_type = models.ForeignKey(CommissionSystem, on_delete=models.CASCADE, null=False)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, null=False)
    weight = models.PositiveIntegerField(blank=True, null=True)
    length = models.PositiveIntegerField(blank=True, null=True)
    rate = models.DecimalField(max_digits=65, decimal_places=2, default=9.99, null=True, blank=True)
    rate_status = models.CharField(max_length=20, choices=Shipping_Status, default='Active')
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.category.title} {str(self.rate)}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category)
        super(ShippingCategory, self).save(*args, **kwargs)


class ShippingRate(models.Model):
    rate_name = models.CharField(max_length=128, null=True, blank=True, unique=True)
    shipping_zone = models.ManyToManyField(ShippingZone, related_name='zones')
    shipping_category = models.ManyToManyField(ShippingCategory, related_name='categories')
    rate = models.DecimalField(max_digits=65, decimal_places=2, default=9.99, null=True, blank=True)
    rate_status = models.CharField(max_length=20, choices=Shipping_Status, default='Active')

    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.rate_name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.rate_name)
        super(ShippingRate, self).save(*args, **kwargs)



class CustomerShippingCalculate(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='calculate_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='calculate_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='calculate_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')

    address = models.ForeignKey(CommonProfile, on_delete=models.CASCADE, null=True,blank=True)
    shipping_rate = models.ForeignKey(ShippingRate, on_delete=models.CASCADE, null=True,blank=True)
    rate = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, null=True, blank=True)
    shipping_error = models.CharField(max_length=128, null=True, blank=True, )
    done_calc = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.rate

    def __str__(self):
        return self.address


class Courier(models.Model):
    receiver_model = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    status = models.CharField(max_length=10, choices=Waiting_Status)

    def __str__(self):
        return self.receiver


    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'COURIER-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Courier, self).save(*args, **kwargs)


