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
    Sport_Stat_Type, Gander_type, Position_List, Language_List, Tv_Type, Sport_Type, Match_Status, Half_List, \
    Match_Statics, Set_List
from helper.viewHelper import get_file_path

# Create your models here.


User = get_user_model()



class YoutubeChannel(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True,)
    url = models.URLField(null=True,blank=True)
    channel_id = models.CharField(max_length=255,null=True,blank=True,)
    image = models.ImageField(upload_to=get_file_path,null=True,blank=True, )
    image_path = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'قناة يوتيوب'
        verbose_name_plural = 'قنوات يوتيوب'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'YoutubeChannel-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(YoutubeChannel, self).save(*args, **kwargs)


class YoutubeVideo(models.Model):
    name = models.CharField(max_length=255,null=True,blank=True,)
    url = models.URLField(null=True,blank=True)
    video_id = models.CharField(max_length=255,null=True,blank=True,)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    image_path = models.URLField(blank=True, null=True)
    channel = models.ForeignKey(YoutubeChannel, on_delete=models.CASCADE, null=True, blank=True, related_name='videos')

    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'فيديو يوتيوب'
        verbose_name_plural = 'فيديوهات يوتيوب'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'YoutubeVideo-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(YoutubeVideo, self).save(*args, **kwargs)



class Media(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True, )
    url = models.URLField(null=True, blank=True)
    channel_id = models.CharField(max_length=255, null=True, blank=True, )
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True, )
    image_path = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'قناة يوتيوب'
        verbose_name_plural = 'قنوات يوتيوب'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Media-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Media, self).save(*args, **kwargs)