from itertools import chain

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction, IntegrityError
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from slugify import slugify

from core.models.people import Employee
from helper.modelHelper import Active_Status, Absent_Type, Absent_Status, Public_Status
from helper.viewHelper import get_file_path

User = get_user_model()

class CustodyCategory(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    keyword = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy('home:FrontArticleCategoryDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'CustodyCategory-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(CustodyCategory, self).save(*args, **kwargs)

class Custody(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='custody_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='custody_receiver', on_delete=models.CASCADE, null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='custody_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    title = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(CustodyCategory, on_delete=models.CASCADE, related_name='custody_category')
    description = models.TextField(blank=True, null=True)
    keyword = models.CharField(max_length=100, blank=True, null=True)
    body = models.TextField(blank=True, null=False)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    type = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    section = models.CharField(max_length=255, blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    store = models.CharField(max_length=255, blank=True, null=True)
    can_transfer = models.CharField(max_length=255,choices=Public_Status, blank=True, null=True,default='Yes')
    store_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse_lazy('home:FrontArticleCategoryDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'Custody-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)


class CustodyHistory(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='custodyhistory_sender', on_delete=models.CASCADE, null=True,blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='custodyhistory_receiver', on_delete=models.CASCADE, null=True,blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='custodyhistory_owner', on_delete=models.SET_NULL, null=True,blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    custody = models.ForeignKey(Custody, on_delete=models.CASCADE, related_name='custody_history')
    description = models.TextField(blank=True, null=False)
    body = models.TextField(blank=True, null=False)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    type = models.CharField(max_length=255, blank=False, null=False)
    location = models.CharField(max_length=255, blank=False, null=False)
    section = models.CharField(max_length=255, blank=False, null=False)
    store = models.CharField(max_length=255, blank=False, null=False)
    store_date = models.DateField(blank=True, null=True)
    in_date = models.DateField(blank=True, null=True)
    out_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
    def get_absolute_url(self):
        return reverse_lazy('home:FrontArticleCategoryDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'CustodyHistory-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)


class CustodyTransferRequest(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='custodyrequest_sender', on_delete=models.CASCADE, null=True,blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='custodyrequest_receiver', on_delete=models.CASCADE, null=True,blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='custodyrequest_owner', on_delete=models.SET_NULL, null=True,blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    custody = models.ForeignKey(Custody, on_delete=models.CASCADE, related_name='custody_request')
    description = models.TextField(blank=True, null=False)
    approve = models.CharField(max_length=255,choices=Public_Status, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    section = models.CharField(max_length=255, blank=True, null=True)
    store = models.CharField(max_length=255, blank=True, null=True)
    store_date = models.DateField(blank=True, null=True)
    in_date = models.DateField(blank=True, null=True)
    out_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
    def get_absolute_url(self):
        return reverse_lazy('home:FrontArticleCategoryDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'CustodyTransferRequest-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(CustodyTransferRequest, self).save(*args, **kwargs)




























