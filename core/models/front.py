# Create your models here.
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from slugify import slugify

from helper.modelHelper import Active_Status, Banners_Position




class Testimonials(models.Model):

    title = models.CharField(max_length=150, null=False, verbose_name="Title")
    description = models.CharField(max_length=1500, null=True, blank=True, verbose_name="Description" )
    author = models.CharField(max_length=150,null=True, blank=True, )
    position = models.CharField(max_length=150, null=True, blank=True, )
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=Active_Status, null=True, blank=True, default="Active")
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Testimonials-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Testimonials, self).save(*args, **kwargs)

class PrivacyPolicy(models.Model):
    status = models.CharField(max_length=30, choices=Active_Status, null=True, blank=True, default="Active")
    title = models.CharField(max_length=150, null=True, blank=True, verbose_name="Title")
    description = models.TextField(max_length=1500, null=True, blank=True)
    author = models.CharField(max_length=150, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('home:FrontPrivacyPolicyDetails', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'PrivacyPolicy-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(PrivacyPolicy, self).save(*args, **kwargs)

class TermsOfService(models.Model):
    status = models.CharField(max_length=30, choices=Active_Status, null=True,blank=True,default="Active")
    title = models.CharField(max_length=150,  null=True,blank=True, verbose_name="Title")
    description = models.TextField(max_length=1500,  null=True,blank=True )
    author = models.CharField(max_length=150, null=True,blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('home:FrontTermsOfServiceDetails', kwargs={'slug': self.slug})
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TermsOfService-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(TermsOfService, self).save(*args, **kwargs)

class Slider(models.Model):
    STATUS = (
        ('True', 'Enable'),
        ('False', 'Disable'),
    )
    group = models.CharField(max_length=150, null=False, verbose_name="Group", unique=True)
    status = models.CharField(max_length=10, choices=Active_Status, default="Active")
    title = models.CharField(max_length=50, null=False, verbose_name="Title", unique=True)
    sort_order = models.IntegerField(default=0, null=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def status_verbose(self):
        return dict(Slider.STATUS)[self.status]




class Banners(models.Model):
    position = models.CharField(max_length=150, null=False, choices=Banners_Position, unique=True)
    status = models.CharField(max_length=10, choices=Active_Status, default="Active")
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.position.title



