from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from core.models.blog import BlogArticle



class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'http'

    def items(self):
        return BlogArticle.objects.all()

    def lastmod(self, obj):
        return obj.create_at

    def location(self, obj):
        return f'/blog/{obj.slug}'





class StaticSitemap(Sitemap):
    changefreq = "yearly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return ['home:HomeIndex', 'home:Contact']

    def location(self, item):
        return reverse(item)