import datetime

from django.db import models
from django.utils.crypto import get_random_string
from slugify import slugify
from helper.modelHelper import Active_Status, Country_List, Governorates_List


# Create your models here.

class Language(models.Model):
    name = models.CharField(max_length=20, unique=True, default='English')
    code = models.CharField(max_length=5, unique=True, default='en')
    status = models.CharField(max_length=20, choices=Active_Status,default='Active')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField(max_length=20, unique=True, default='Egypt Pound')
    code = models.CharField(max_length=5, unique=True, default='EGP')
    exchange = models.DecimalField(max_digits=65, decimal_places=2, default=6.99, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code





class Country(models.Model):
    name = models.CharField(max_length=100,choices=Country_List, default='Egypt')
    image = models.ImageField(upload_to='images/country/%Y/%m/%d', default='images/lang/en-gb.png', null=True, blank=True)

    status = models.CharField(max_length=20, choices=Active_Status, default='Active',null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code= f'Country-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Country, self).save(*args, **kwargs)




class Governorates(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,choices=Governorates_List, default='Cairo')
    status = models.CharField(max_length=20, choices=Active_Status, default='Active',null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code= f'Governorates-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Governorates, self).save(*args, **kwargs)


class City(models.Model):
    governorates = models.ForeignKey(Governorates, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default='Qena')
    status = models.CharField(max_length=20, choices=Active_Status, default='Active',null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code= f'City-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(City, self).save(*args, **kwargs)


class Area(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=30, default='Qena')
    status = models.CharField(max_length=20, choices=Active_Status, default='Active',null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code= f'Area-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Area, self).save(*args, **kwargs)


class CalendarLocalization(models.Model):
    Year = models.CharField(max_length=20,null=True,blank=True,default='')
    month = models.CharField(max_length=20,null=True,blank=True,default='')
    month_ch = models.CharField(max_length=20,null=True,blank=True,default='')
    day = models.CharField(max_length=20,null=True,blank=True,default='')
    day_ch = models.CharField(max_length=20,null=True,blank=True,default='')

    def __str__(self):
        return self.day