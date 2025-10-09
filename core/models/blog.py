import contextlib
import logging


from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator

from django.core.cache import cache
from django.db import models
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from slugify import slugify

from apps.sport.models.models import Sport, Teams
from core.models.core import CommonTags
from core.utils.utils import cache_decorator
from helper.viewHelper import get_file_path

# Create your models here.

logger = logging.getLogger(__name__)
from helper.modelHelper import Active_Status, Service_Type, Featured_Status, Country_List, Publish_Status, \
    COMMENT_STATUS, Article_Type, Video_Source

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





class BlogArticle(models.Model):
    """article"""

    title = models.CharField(max_length=100, )
    keyword = models.CharField(max_length=100, null=True, blank=True, default='')
    category = models.ForeignKey(BlogCategories, verbose_name='Classification', on_delete=models.CASCADE, blank=True,
                                 null=True)
    tags = models.ManyToManyField(CommonTags, verbose_name='article_tag', blank=True)
    body = models.TextField(blank=True, null=True)
    pub_time = models.DateField( 'release time', blank=True, null=True, default=now)
    pub_type = models.CharField(  'Article status', max_length=10,choices=Publish_Status, default='Published', blank=True, null=True, )
    is_featured = models.CharField(max_length=100, choices=Active_Status, default='Inactive', blank=True, null=True, )
    comment_status = models.CharField('Comment status',max_length=10, choices=COMMENT_STATUS,default='Close', blank=True, null=True, )
    article_type = models.CharField('type', max_length=10, choices=Article_Type, default='Article', blank=True, null=True, )
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_news', null=True, blank=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team_news', null=True, blank=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    image_path = models.CharField(max_length=100, null=True, blank=True)
    video_url = models.URLField(max_length=100, null=True, blank=True)
    views = models.PositiveIntegerField('Pageviews', default=0, blank=True, null=True, )
    author = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now=True, null=False)
    updated_at = models.DateTimeField(auto_now=True)

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




class BlogVideo(models.Model):
    title = models.CharField(max_length=100, )
    keyword = models.CharField(max_length=100, null=True, blank=True, default='')
    category = models.ForeignKey(BlogCategories, verbose_name='Classification', on_delete=models.CASCADE, blank=True,
                                 null=True)
    tags = models.ManyToManyField(CommonTags, verbose_name='article_tag', blank=True)
    body = models.TextField(blank=True, null=True)
    pub_time = models.DateField('release time', blank=True, null=True, default=now)
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='sport_video', null=True, blank=True)
    views = models.PositiveIntegerField('Pageviews', default=0, blank=True, null=True, )
    author = models.CharField(max_length=100, null=True, blank=True, default='Admin')
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    image_path = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(blank=True,null=True, upload_to=get_file_path)
    video_source = models.CharField(max_length=100, null=True, blank=True,choices=Video_Source, default='Youtube')
    video_url = models.URLField(max_length=100, null=True, blank=True)
    video_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=60, choices=Active_Status, null=True, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    create_at = models.DateTimeField(auto_now=True, null=False)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id', '-pub_time']
        verbose_name = "Video"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Video-{get_random_string(5).upper()}'
            self.code =code
            self.slug = code
        super(BlogVideo, self).save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('home:FrontVideoWithTimeDetails', kwargs={
            'slug': self.slug,
            'y': self.update_at.year,
            'm': self.update_at.month,
            'd': self.update_at.day
        })






