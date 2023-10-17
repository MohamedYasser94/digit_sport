from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.crypto import get_random_string
from slugify import slugify

from apps.catalog.models.models import Categories
from core.models.localization import Country, Governorates, City
from helper.modelHelper import Active_Status

User = get_user_model()


class Vendor(models.Model):

    vendor = models.ForeignKey(User,related_name='store_vendor', on_delete=models.CASCADE, blank=True ,)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, blank=True,null=True,default=1)
    title = models.CharField(max_length=150 , null=True,blank=True ,default=' ' ,)
    email = models.EmailField( max_length=50,  null=True,blank=True , unique=True, verbose_name='Vendor Email')
    status = models.BooleanField(default=False)
    activation = models.BooleanField(default=False)
    code = models.CharField(max_length=100, editable=False,)
    slug = models.SlugField(null=False, blank=False, unique=True)
    create_at = models.DateTimeField(auto_now=True ,null=False)
    update_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            self.code = f'VEND-{get_random_string(5).upper()}'
            self.slug = slugify(f'VEND-{self.title}-{get_random_string(3)}')
        super(Vendor, self).save(*args, **kwargs)
        ## method to create a fake table field in read only mode


    def get_absolute_url(self):
        view_name = "vendor:detail_slug"
        return reverse(view_name, kwargs={"slug": self.slug})
class Warehouse(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='warehouse_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='warehouse_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType,related_name='warehouse_owner', on_delete=models.CASCADE, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    vendor = models.ForeignKey(Vendor, related_name='warehouse_vendor', on_delete=models.CASCADE, blank=True,null=True )
    name = models.CharField(max_length=200, unique=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    governorates = models.ForeignKey(Governorates, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=60, choices=Active_Status, null=True, default='Active')
    code = models.CharField(max_length=200, null=True, blank=True, unique=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('view_warehouse', args=[self.id])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            warehouse_code = f'WAH-{get_random_string(5).upper()}'
            self.code = warehouse_code
            self.slug = slugify(warehouse_code)
        super(Warehouse, self).save(*args, **kwargs)

