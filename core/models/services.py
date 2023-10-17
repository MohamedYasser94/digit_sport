from abc import ABC

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from django_otp.models import ThrottlingMixin, Device
from slugify import slugify
from django.utils.translation import gettext_lazy as _
from helper.modelHelper import Active_Status, Otp_Type

# Create your models here.

User = get_user_model()



class Contact(models.Model):

    name = models.CharField(max_length=50, null=True, blank=True, )
    phone = models.CharField(max_length=50,null=True, blank=True, default=0)
    email = models.EmailField(max_length=50, null=True, blank=True, )
    subject = models.CharField(max_length=100, null=True, blank=True, )
    message = models.TextField(null=True, blank=True, )
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('core:AdminClientContactDetail', kwargs={'slug': self.slug})
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Contact-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Contact, self).save(*args, **kwargs)


class Newsletter(models.Model):
    subscribed = models.CharField(max_length=10, choices=Active_Status, default='Active',blank=True,null=True )
    subject = models.CharField(max_length=100, null=True, blank=True, )
    message = models.TextField(null=True, blank=True, )
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def get_absolute_url(self):
        return reverse('core:AdminClientContactDetail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Newsletter-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Newsletter, self).save(*args, **kwargs)

class NewsletterSubscriber(models.Model):
    email = models.EmailField(max_length=50, null=False, )
    subscribed = models.CharField(max_length=10, choices=Active_Status, default='Active',blank=True,null=True )
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


class AccountOtp(ThrottlingMixin, Device):
    owner_model = models.ForeignKey(ContentType, related_name='account_otp', on_delete=models.CASCADE, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=64, help_text=_("The human-readable title of this device."))
    method= models.CharField(max_length=50,choices=Otp_Type, default='None', null=True, blank=True)
    otp = models.CharField(max_length=100, null=True, blank=True)
    qr_code = models.ImageField(upload_to='images/qrcode/%Y/%m', blank=True)
    whatsapp_otp = models.CharField(max_length=100, null=True, blank=True)
    backup_code = models.CharField(max_length=100, null=True, blank=True)
    verified = models.CharField(max_length=20, choices=Active_Status, default='Inactive', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, default='Inactive')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'AccountOtp-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(AccountOtp, self).save(*args, **kwargs)