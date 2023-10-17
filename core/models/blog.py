import contextlib
import logging


from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.sitemaps import ping_google
from django.core.cache import cache
from django.db import models
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from slugify import slugify

from core.models.core import CommonTags
from core.utils.utils import cache_decorator
from helper.viewHelper import get_file_path

# Create your models here.

logger = logging.getLogger(__name__)
from helper.modelHelper import Active_Status, Service_Type, Featured_Status

User = get_user_model()


class BlogCategories(MPTTModel):
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    title = models.CharField(max_length=20, validators=[UnicodeUsernameValidator])
    keyword = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    status = models.CharField(max_length=20, choices=Active_Status)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'category'
        # verbose_name_plural = 'categories'

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse_lazy('home:FrontArticleCategoryDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'CAT-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(BlogCategories, self).save(*args, **kwargs)

class BlogServices(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    service_type = models.CharField(max_length=50, choices=Service_Type, default='Service')
    keyword = models.CharField(max_length=500, null=False, blank=False)
    category = models.ForeignKey(BlogCategories, on_delete=models.CASCADE)
    tags = models.ManyToManyField(CommonTags,related_name='services_tags', blank=True)
    body = models.TextField(blank=True,null=True)
    project_name = models.CharField(max_length=100, null=True, blank=True)
    project_type = models.CharField(max_length=100, null=True, blank=True)
    skills = models.CharField(max_length=100, null=True, blank=True)
    demo = models.URLField(max_length=255, null=True, blank=True)
    files = models.FileField(blank=True, upload_to=get_file_path)
    pdf = models.FileField(blank=True, upload_to=get_file_path)
    cloud_file = models.URLField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=50, null=True, blank=True)
    featured = models.CharField(max_length=255, choices=Featured_Status, default='Inactive')
    status = models.CharField(max_length=60, choices=Active_Status, null=True, default='Active')
    sort_order = models.SmallIntegerField(default=0, null=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('ServicesDetail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Our-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(BlogServices, self).save(*args, **kwargs)






class BlogArticle(models.Model):
    """article"""
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Publish', 'Publish'),
    )
    COMMENT_STATUS = (
        ('Open', 'Open'),
        ('Close', 'Close'),
    )
    Article_Type = (
        ('Article', 'Article'),
        ('Page', 'Page'),
    )
    title = models.CharField(max_length=255, unique=True)
    keyword = models.CharField(max_length=255, null=False, blank=False, default='')
    category = models.ForeignKey(BlogCategories, verbose_name='Classification', on_delete=models.CASCADE, blank=False,
                                 null=False)
    tags = models.ManyToManyField(CommonTags, verbose_name='article_tag', blank=True)
    body = models.TextField(blank=True, null=True)
    pub_time = models.DateField( 'release time', blank=False, null=False, default=now)
    pub_type = models.CharField(  'Article status', max_length=10,choices=STATUS_CHOICES, default='Draft')
    is_featured = models.CharField(max_length=255, choices=Active_Status, default='Inactive')
    comment_status = models.CharField('Comment status',max_length=10, choices=COMMENT_STATUS,default='Close')
    article_type = models.CharField('type', max_length=10, choices=Article_Type, default='Article')
    views = models.PositiveIntegerField('Pageviews', default=0)
    author = models.ForeignKey( User, verbose_name='author',blank=False,null=False,on_delete=models.CASCADE)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    create_at = models.DateTimeField(auto_now=True, null=False)
    update_at = models.DateTimeField(auto_now=True)

    def body_to_string(self):
        return self.body

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id', '-pub_time']
        verbose_name = "article"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Article-{get_random_string(5).upper()}'
            self.code =code
            self.slug = code
        super(BlogArticle, self).save(*args, **kwargs)
        with contextlib.suppress(Exception):
            ping_google()



    def get_absolute_url(self):
        return reverse('home:FrontArticleWithTimeDetails', kwargs={
            'slug': self.slug,
            'y': self.update_at.year,
            'm': self.update_at.month,
            'd': self.update_at.day
        })

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        tree = self.category.get_category_tree()
        return list(map(lambda c: (c.title, c.get_absolute_url()), tree))

    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    def comment_list(self):
        cache_key = 'article_comments_{id}'.format(id=self.id)
        if value := cache.get(cache_key):
            logger.info('get article comments:{id}'.format(id=self.id))
            return value
        else:
            comments = self.comment_set.filter(is_enable=True)
            cache.set(cache_key, comments, 60 * 100)
            logger.info('set article comments:{id}'.format(id=self.id))
            return comments

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)
        return reverse('admin:%s_%s_change' % info, args=(self.pk,))

    @cache_decorator(expiration=60 * 100)
    def next_article(self):
        # Next
        return BlogArticle.objects.filter(
            id__gt=self.id, status='p').order_by('id').first()

    @cache_decorator(expiration=60 * 100)
    def prev_article(self):
        # Previous Article
        return BlogArticle.objects.filter(id__lt=self.id, status='p').first()



