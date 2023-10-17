from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView


from core.models.blog import BlogArticle, BlogCategories, CommonTags
from core.models.core import CommonMediaFiles
from home.views.views import FRONTEND_TEMPLATES

User = get_user_model()


##########################      Services Admin            ################################


def BlogList(request):
    articles = BlogArticle.objects.all()
    article_list = []
    for article in articles:
        cover = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model = 'BlogArticle'),owner_id=article.id, type='hero')
        data = {'article': article, 'cover': cover, }
        article_list.append(data)


    last_article = BlogArticle.objects.all().order_by('-id')
    categories = BlogCategories.objects.all()
    tags = CommonTags.objects.all()
    paginator = Paginator(articles, 5)  # Show 25 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'articles': article_list,

        'last_article': last_article,
        'categories': categories,
        'tags': tags,
        'page_obj': page_obj,
        'current_page': 'Blog',

    }
    return render(request, f'{FRONTEND_TEMPLATES}/blog/blog.html', context)


def ArticleDetailFront(request, slug):
    articles = BlogArticle.objects.all()
    article = BlogArticle.objects.get(slug=slug)
    cover = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model = 'BlogArticle'),owner_id=article.id, type='hero')
    video = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model = 'BlogArticle'),owner_id=article.id, type='video')
    images = CommonMediaFiles.objects.filter(owner_model=ContentType.objects.get(model = 'BlogArticle'),owner_id=article.id, type='image')
    random_articles = BlogArticle.objects.filter().order_by('?')
    article_list = []
    for article in random_articles:
        cover = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model = 'BlogArticle'),owner_id=article.id, type='hero')
        data = {'article': article, 'cover': cover, }
        article_list.append(data)
    try:
        previous_article = BlogArticle.objects.get(id=article.id - 1)
    except Exception as e:
        previous_article = None
    try:
        next_article = BlogArticle.objects.get(id=article.id + 1)
    except Exception as e:
        next_article = None
    print(next_article)
    categories = BlogCategories.objects.all()
    article_category = BlogCategories.objects.get(blogarticle=article)
    tags = CommonTags.objects.all()
    article_tag = CommonTags.objects.filter(blogarticle=article)
    page_title = _('Blog')
    article.viewed()

    context = {
        'current_page': article.title,
        'prev_Page': _('Blog'),
        'prev_Page_link': reverse_lazy('home:FrontBlog'),
        'page_title': page_title,
        'articles': articles,
        'article': article,
        'cover': cover,
        'video': video,
        'images': images,
        'random_articles': article_list,
        'previous_article': previous_article,
        'next_article': next_article,
        'categories': categories, 'article_category': article_category,
        'tags': tags, 'article_tag': article_tag,
        'current_page': 'Blog',
    }
    return render(request, f'{FRONTEND_TEMPLATES}/blog/article-detail.html', context)

def FrontArticleWithTimeDetails(request, slug,y,m,d):
    articles = BlogArticle.objects.all()
    article = BlogArticle.objects.get(slug=slug, created_at__year=y, created_at__month=m, created_at__day=d)
    cover = CommonMediaFiles.objects.get(Q(owner_id=article.id), type='hero')
    video = CommonMediaFiles.objects.get(Q(owner_id=article.id), type='video')
    images = CommonMediaFiles.objects.filter(Q(owner_id=article.id), type='image')
    random_articles = BlogArticle.objects.filter().order_by('?')
    article_list = []
    for article in random_articles:
        cover = CommonMediaFiles.objects.get(Q(owner_id=article.id), type='hero')
        data = {'article': article, 'cover': cover, }
        article_list.append(data)
    try:
        previous_article = BlogArticle.objects.get(id=article.id - 1)
    except Exception as e:
        previous_article = None
    try:
        next_article = BlogArticle.objects.get(id=article.id + 1)
    except Exception as e:
        next_article = None
    print(next_article)
    categories = BlogCategories.objects.all()
    article_category = BlogCategories.objects.get(blogarticle=article)
    tags = CommonTags.objects.all()
    article_tag = CommonTags.objects.filter(blogarticle=article)
    page_title = _('Blog')
    article.viewed()

    context = {
        'current_page': article.title,
        'prev_Page': _('Blog'),
        'prev_Page_link': reverse_lazy('home:FrontBlog'),
        'page_title': page_title,
        'articles': articles,
        'article': article,
        'cover': cover,
        'video': video,
        'images': images,
        'random_articles': article_list,
        'previous_article': previous_article,
        'next_article': next_article,
        'categories': categories, 'article_category': article_category,
        'tags': tags, 'article_tag': article_tag,
        'current_page': 'Blog',
    }
    return render(request, f'{FRONTEND_TEMPLATES}/blog/article-detail.html', context)

def AuthorDetailFront(request, slug):
    articles = BlogArticle.objects.all()
    author = User.objects.get(slug=slug)
    random_articles = BlogArticle.objects.filter().order_by('?')

    page_title = _('Blog')

    context = {
        'page_title': page_title,
        'author': author,

        'random_articles': random_articles,
        'current_page': 'Blog',
    }
    return render(request, f'{FRONTEND_TEMPLATES}/blog/article-detail.html', context)


class ArticleCategoryList(ListView):
    model = BlogCategories
    template_name = f'{FRONTEND_TEMPLATES}/blog/blog.html'


class ArticleCategoryDetailFront(DetailView):
    model = BlogCategories

    template_name = f'{FRONTEND_TEMPLATES}/blog/article-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


class ArticleTagList(ListView):
    model = CommonTags
    template_name = f'{FRONTEND_TEMPLATES}/blog/blog.html'


class ArticleTagDetailFront(DetailView):
    model = CommonTags

    template_name = f'{FRONTEND_TEMPLATES}/blog/article-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


def ProductSearch(request):
    q = request.GET['q']
    data = BlogArticle.objects.filter(title__icontains=q).order_by('-id')
    images = BlogArticle.objects.filter(article__title=q, )
    context = {'data': data,
               'images': images,
               }
    return render(request, 'Search/search_products.html', context)


class CommonTagsList(ListView):
    model = CommonTags
    template_name = f'{FRONTEND_TEMPLATES}/catalog/tags/admin.html'

    # @method_decorator(superuser_only)
    # def dispatch(self, *args, **kwargs):
    #     return super(CommonTagsList, self).dispatch(*args, **kwargs)


class CommonTagsDetail(DetailView):
    model = CommonTags
    context_object_name = 'tags'
    template_name = f'{FRONTEND_TEMPLATES}/catalog/tags/details.html'
