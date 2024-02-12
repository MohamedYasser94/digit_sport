

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

from apps.sport.models.models import Match
from helper.modelHelper import *
from helper.viewHelper import get_file_path

# Create your models here.


User = get_user_model()

class MatchReport(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='match_player_reports')
    status = models.CharField(max_length=200, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = 'match report'
        verbose_name_plural = 'match reports'


    def __str__(self):
        return f'{self.match} report'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MatchReport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MatchReport, self).save(*args, **kwargs)

class MatchPlayerReport(models.Model):
    report = models.ForeignKey(MatchReport, on_delete=models.CASCADE, related_name='report_sets',null=True, blank=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='report_math',null=True, blank=True)
    team = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='report_team',null=True, blank=True)
    player = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='report_player',null=True, blank=True)
    set1 = models.CharField(max_length=30,   null=True, blank=True)
    set2 = models.CharField(max_length=30,   null=True, blank=True)
    set3 = models.CharField(max_length=30,   null=True, blank=True)
    set4 = models.CharField(max_length=30,   null=True, blank=True)
    set5 = models.CharField(max_length=30,   null=True, blank=True)
    vote = models.CharField(max_length=30,   null=True, blank=True)
    point_total = models.CharField(max_length=30,   null=True, blank=True)
    point_bp = models.CharField(max_length=30,   null=True, blank=True)
    point_wl = models.CharField(max_length=30,   null=True, blank=True)
    serve_total = models.CharField(max_length=30,   null=True, blank=True)
    serve_err = models.CharField(max_length=30,   null=True, blank=True)
    serve_pts = models.CharField(max_length=30,   null=True, blank=True)
    reception_total = models.CharField(max_length=30,   null=True, blank=True)
    reception_err = models.CharField(max_length=30,   null=True, blank=True)
    reception_pos = models.CharField(max_length=30,   null=True, blank=True)
    reception_exc = models.CharField(max_length=30,   null=True, blank=True)
    attack_total = models.CharField(max_length=30,   null=True, blank=True)
    attack_err = models.CharField(max_length=30,   null=True, blank=True)
    attack_pos = models.CharField(max_length=30,   null=True, blank=True)
    attack_exc = models.CharField(max_length=30,   null=True, blank=True)
    block_pts = models.CharField(max_length=30,   null=True, blank=True)

    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'match player report'
        verbose_name_plural = 'match player reports'


    def __str__(self):
        return f'{self.match} report'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MatchReport-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MatchReport, self).save(*args, **kwargs)


