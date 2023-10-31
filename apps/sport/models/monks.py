from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from slugify import slugify

from helper.modelHelper import Active_Status, Public_Status, Country_List, Governorates_List, Sport_Core_type, \
    Sport_Stat_Type, Gander_type, Position_List, Language_List, Tv_Type, Sport_Type, Match_Status
from helper.viewHelper import get_file_path

# Create your models here.


User = get_user_model()





class MonkCountry(models.Model):

    api_id = models.IntegerField(null=True, blank=True)
    continent = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    name_ar = models.CharField(max_length=200, null=True, blank=True)
    official_name = models.CharField(max_length=200, null=True, blank=True)
    fifa_name = models.CharField(max_length=200, null=True, blank=True)
    iso2 = models.CharField(max_length=200, null=True, blank=True)
    iso3 = models.CharField(max_length=200, null=True, blank=True)
    latitude = models.CharField(max_length=200, null=True, blank=True)
    longitude = models.CharField(max_length=200, null=True, blank=True)
    image_path = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    borders = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MonkCountry-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MonkCountry, self).save(*args, **kwargs)