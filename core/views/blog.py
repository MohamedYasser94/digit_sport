import logging
from datetime import datetime


from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from apps.sport.models.models import Sport
from core.forms.blog import AdminBlogCategoriesForm, AdminCommonTagsForm,  AdminBlogArticleForm, \
    AdminBlogArticleTagsForm, AdminBlogVideoForm
from core.forms.core import AdminCommonSeoForm, AdminCommonMediaFilesForm, AdminCommonTranslateForm
from core.models.blog import BlogArticle, BlogCategories,  CommonTags, BlogVideo
from core.models.core import CommonSeo, CommonTranslate, CommonMediaFiles
from core.utils.notification import FcmNotifications

from core.views.core import AdminCommonMediaHeroFiles, AdminCommonMediaImagesFiles, \
    AdminCommonMediaVideoFiles, AdminCommonTranslate, AdminCommonSeo
from core.views.notifications import AdminCommonNotifications
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import author_only, authenticated_staf, staff_only



User = get_user_model()
logger = logging.getLogger(__name__)


@authenticated_staf
@author_only
def BlogDashboard(request):
    return render(request, 'good/blog/blog-dashboard.html')


##########################      Blog Category Admin            ################################


@authenticated_staf
@staff_only
def AdminBlogCategoriesList(request):
    categories = BlogCategories.objects.all()
    categories_list = []
    for category in categories:
        translate = CommonTranslate.objects.get(
            owner_model=ContentType.objects.get(model='BlogCategories'), owner_id=category.id)

        categories_list.append(
            {"category": category, "translate": translate, })

    if request.method == "POST":
        category_form = AdminBlogCategoriesForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if category_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            parent = request.POST.get('parent')
            status = request.POST.get('status')
            image = request.FILES.get('image')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            try:
                parent_id = BlogCategories.objects.get(id=parent)
            except Exception as e:
                parent_id = None
            category_object = BlogCategories(title=title, keyword=keyword, parent=parent_id, status=status
                                             , image=image)
            category_object.save()
            translate_object = CommonTranslate(title=title_tr, keyword=keyword_tr,
                                               owner_model=ContentType.objects.get(model='BlogCategories'),
                                               owner_id=category_object.id)
            translate_object.save()
            messages.success(request, _("Category Add Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('core:AdminBlogCategoriesList'))
        else:

            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Category')

    else:
        context = {
            'categories': categories_list,
            'category_form': AdminBlogCategoriesForm(),
            'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Categories')

        }
        return render(request, f'{BACKEND_TEMPLATES}/blog/category/admin.html', context)
    context = {
        'categories': categories,
        'category_form': AdminBlogCategoriesForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/blog/category/admin.html', context)


@authenticated_staf
@staff_only
def AdminBlogCategoryDetails(request, slug):
    category = BlogCategories.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(
        owner_model=ContentType.objects.get(model='BlogCategories'), owner_id=category.id)
    context = {
        'category': category,
        'translate': translate,
        'current_page': _('Details'),
        'prev_Page': _('Categories'),
        'prev_Page_url': reverse_lazy('core:AdminBlogCategoriesList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/blog/category/details.html', context)


@authenticated_staf
@staff_only
def AdminBlogCategoryUpdate(request, slug):
    category = BlogCategories.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(
        owner_model=ContentType.objects.get(model='BlogCategories'), owner_id=category.id)
    category_form = AdminBlogCategoriesForm(request.POST or None, request.FILES or None)
    translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        title = request.POST.get('title')
        keyword = request.POST.get('keyword')
        parent = request.POST.get('parent')
        status = request.POST.get('status')
        title_tr = request.POST.get('title_tr')
        keyword_tr = request.POST.get('keyword_tr')

        try:
            parent_id = BlogCategories.objects.get(id=parent)
        except Exception as e:
            parent_id = None
        if category_form:

            category_object = BlogCategories.objects.get(slug=slug)
            category_object.title = title
            category_object.keyword = keyword
            category_object.parent = parent_id
            category_object.status = status
            category_object.save()
            translate.title = title_tr
            translate.keyword = keyword_tr
            translate.save()
            messages.success(request, _("Category Update Successfully"), extra_tags='Category')
            return HttpResponseRedirect(reverse_lazy('core:AdminBlogCategoriesList'))
        else:
            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Category')
    else:
        context = {
            'category': category,
            'translate': translate,
            'category_form': AdminBlogCategoriesForm(),
            'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Update'),
            'prev_Page': _('Categories'),
            'prev_Page_link': reverse_lazy('core:AdminBlogCategoriesList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/blog/category/update.html', context)

    context = {
        'category': category,
        'translate': translate,
        'category_form': AdminBlogCategoriesForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Update'),
        'prev_Page': _('Categories'),
        'prev_Page_link': reverse_lazy('core:AdminBlogCategoriesList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/blog/category/update.html', context)


@authenticated_staf
@staff_only
def AdminBlogCategoryArchive(request, slug):
    category = BlogCategories.objects.get(slug=slug)
    if request.method == "POST":
        category.status = 'Archive'
        category.save()

    messages.success(request, _("Category Archive Successfully"), extra_tags='Category')

    return HttpResponseRedirect(reverse_lazy('core:AdminBlogCategoriesList'))


@authenticated_staf
@staff_only
def AdminBlogCategoryDelete(request, slug):
    category = BlogCategories.objects.get(slug=slug)
    if request.method == "POST":
        category.delete()
        messages.success(request, _("Category Delete Successfully"), extra_tags='Category')

        return HttpResponseRedirect(reverse_lazy('core:AdminBlogCategoriesList'))
    return HttpResponseRedirect(reverse_lazy('core:AdminBlogCategoriesList'))


##########################        Blog Tags Admin                ################################


@authenticated_staf
@staff_only
def AdminBlogTagsList(request):
    tags = CommonTags.objects.all()
    if request.method == "POST":
        tag_form = AdminCommonTagsForm(request.POST or None, request.FILES or None)
        if tag_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            status = request.POST.get('status')
            tag_object = CommonTags(title=title, keyword=keyword, status=status
                                    )
            tag_object.save()
            messages.success(request, _("Category Add Successfully"), extra_tags='Tags')
            return HttpResponseRedirect(reverse_lazy('core:AdminBlogTagsList'))
        else:
            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Tags')
    else:
        context = {
            'tags': tags,
            'tag_form': AdminCommonTagsForm(),

            'current_page': _('Categories')

        }
        return render(request, f'{BACKEND_TEMPLATES}/blog/tags/admin.html', context)
    context = {
        'tags': tags,
        'tag_form': AdminCommonTagsForm(),

        'current_page': _('Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/blog/tags/admin.html', context)


@authenticated_staf
@staff_only
def AdminBlogTagsDetails(request, slug):
    tag = CommonTags.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(
        owner_model=ContentType.objects.get(model='CommonTags'), owner_id=tag.id)
    context = {
        'tag': tag,
        'translate': translate,
        'current_page': _('Details'),
        'prev_Page': _('Tags'),
        'prev_Page_url': reverse_lazy('core:AdminBlogTagsList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/blog/tags/details.html', context)


@authenticated_staf
@staff_only
def AdminBlogTagsUpdate(request, slug):
    tag = CommonTags.objects.get(slug=slug)
    if request.method == "POST":
        tag_form = AdminCommonTagsForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if tag_form.is_valid() and translate_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            status = request.POST.get('status')
            tag.title = title
            tag.keyword = keyword
            tag.status = status
            tag.save()
            messages.success(request, _("Category Update Successfully"), extra_tags='Tags')
            return HttpResponseRedirect(reverse_lazy('core:AdminBlogTagsList'))
        else:
            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Tags')
    else:
        context = {
            'tag': tag,

            'tag_form': AdminCommonTagsForm(),
            'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Update'),
            'prev_Page': _('Tags'),
            'prev_Page_link': reverse_lazy('core:AdminBlogTagsList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/blog/tags/update.html', context)


@authenticated_staf
@staff_only
def AdminBlogTagsArchive(request, slug):
    tag = CommonTags.objects.get(slug=slug)
    if request.method == "POST":
        tag.status = 'Archive'
        tag.save()
        messages.success(request, _("Category Archive Successfully"), extra_tags='Tags')

        return HttpResponseRedirect(reverse_lazy('core:AdminBlogTagsList'))


@authenticated_staf
@staff_only
def AdminBlogTagsDelete(request, slug):
    tag = CommonTags.objects.get(slug=slug)
    if request.method == "POST":
        tag.delete()
        messages.success(request, _("Category Delete Successfully"), extra_tags='Tags')

        return HttpResponseRedirect(reverse_lazy('core:AdminBlogTagsList'))
    return HttpResponseRedirect(reverse_lazy('core:AdminBlogTagsList'))


##########################      Blog Article Admin            ################################


@authenticated_staf
@staff_only
def AdminBlogArticleList(request):
    articles = BlogArticle.objects.all()

    context = {
        'articles': articles,
        'current_page': _('Articles')
    }
    return render(request, f'{BACKEND_TEMPLATES}/blog/article/admin.html', context)


@authenticated_staf
@staff_only
def AdminBlogArticleDetails(request, slug):
    article = BlogArticle.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(
        owner_model=ContentType.objects.get(model='BlogArticle'), owner_id=article.id)
    context = {
        'article': article,
        'translate': translate,
        'current_page': _('Details'),
        'prev_Page': _('Articles'),
        'prev_Page_url': reverse_lazy('core:AdminBlogArticleList'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/blog/article/details.html', context)


@authenticated_staf
@author_only
def AdminBlogArticleCreate(request):
    blog_tags = CommonTags.objects.all()
    if request.method == "POST":
        article_form = AdminBlogArticleForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        category_form = AdminBlogCategoriesForm(request.POST or None, request.FILES or None)
        tags_form = AdminBlogArticleTagsForm(request.POST or None, request.FILES or None)
        seo_form = AdminCommonSeoForm(request.POST or None, request.FILES or None)
        if article_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            category = request.POST.get('category')
            body = request.POST.get('body')
            pub_time = request.POST.get('pub_time')
            pub_type = request.POST.get('pub_type')
            is_featured = request.POST.get('is_featured')
            comment_status = request.POST.get('comment_status')
            tags = request.POST.getlist('tags')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')
            author= request.POST.get('author')
            country = request.POST.get('country')
            sport = request.POST.get('sport')
            ########## Image #########
            hero_image = request.FILES.get('hero_image')
            images = request.FILES.getlist('images')
            image_path = request.POST.get('image_path')
            image_url = request.POST.getlist('image_url')
            video_url = request.POST.get('video_url')
            video_cover = request.FILES.get('video_cover')
            ########## Seo #########
            meta_title = title
            meta_keywords = keyword
            meta_description = keyword
            seo_image = hero_image
            ########## Category #########
            if category == '' or category == None:
                category_id = None
            else:
                category_id = BlogCategories.objects.get(id=category)

            if sport == '' or sport == None:
                sport = None
            else:
                sport = Sport.objects.get(id=sport)


            article_object = BlogArticle(title=title, keyword=keyword, category=category_id, body=body,
                                         pub_time=pub_time, pub_type=pub_type, is_featured=is_featured,
                                         sport=sport, country=country,image_path=image_path,image=hero_image,
                                         author=author, comment_status=comment_status)
            article_object.save()

            AdminCommonSeo(request, meta_title, meta_description, meta_keywords, None, seo_image, 'BlogArticle',
                           article_object.id)
            image_url  = article_object.image.url
            image = request.build_absolute_uri(image_url)
            FcmNotifications(request, title, keyword, image)



            messages.success(request, _("Article Add Successfully, check it out on the home page!"),
                             extra_tags='Article')

            return HttpResponseRedirect(reverse('core:AdminBlogArticleList'))

    else:
        article_form = AdminBlogArticleForm()
        tags_form = AdminBlogArticleTagsForm()
        context = {
            'blog_tags': blog_tags,
            'article_form': article_form,
            'tags_form': tags_form,
            'seo_form': AdminCommonSeoForm,
            'current_page': _('Add'),
            'prev_Page': _('Articles'),
            'prev_Page_url': reverse_lazy('core:AdminBlogArticleList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/blog/article/add.html', context)
    context = {
        'blog_tags': blog_tags,
        'article_form': article_form,
        'tags_form': tags_form,
        'seo_form': AdminCommonSeoForm,
        'current_page': _('Add'),
        'prev_Page': _('Articles'),
        'prev_Page_url': reverse_lazy('core:AdminBlogArticleList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/blog/article/add.html', context)

@authenticated_staf
@author_only
def AdminBlogArticleSCreate(request):
    blog_tags = CommonTags.objects.all()
    if request.method == "POST":
        article_form = AdminBlogArticleForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        category_form = AdminBlogCategoriesForm(request.POST or None, request.FILES or None)
        tags_form = AdminBlogArticleTagsForm(request.POST or None, request.FILES or None)
        seo_form = AdminCommonSeoForm(request.POST or None, request.FILES or None)
        if article_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            category = request.POST.get('category')
            body = request.POST.get('body')
            pub_time = request.POST.get('pub_time')
            pub_type = request.POST.get('pub_type')
            is_featured = request.POST.get('is_featured')
            comment_status = request.POST.get('comment_status')
            tags = request.POST.getlist('tags')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')
            author= request.POST.get('author')
            country = request.POST.get('country')
            sport = request.POST.get('sport')
            ########## Image #########
            hero_image = request.FILES.get('hero_image')
            images = request.FILES.getlist('images')
            image_path = request.POST.get('image_path')
            image_url = request.POST.getlist('image_url')
            video_url = request.POST.get('video_url')
            video_cover = request.FILES.get('video_cover')
            ########## Seo #########
            meta_title = title
            meta_keywords = keyword
            meta_description = keyword
            seo_image = hero_image
            ########## Category #########
            if pub_time == '' or pub_time == None:
                pub_time = datetime.now()
            else:
                pub_time = pub_time
            if category == '' or category == None:
                category_id = None
            else:
                category_id = BlogCategories.objects.get(id=category)

            if sport == '' or sport == None:
                sport = None
            else:
                sport = Sport.objects.get(id=sport)
            if author == '' or author == None:
                author = 'Blog'
            else:
                author = author



            article_object = BlogArticle(title=title, keyword=title, category=category_id, body=body,
                                         pub_time=pub_time, pub_type=pub_type, is_featured=is_featured,
                                         sport=sport, country=country,image_path=image_path,image=hero_image,
                                         author=author, comment_status=comment_status)
            article_object.save()
            AdminCommonTranslate(request, title_tr, keyword_tr, body_tr, 'BlogArticle', article_object.id)
            # try:
            #     if image_path != None or image_path != '':
            #         request_host(request)
            #
            #         image_path =  request_host(request) + str(article_object.image.url)
            #         print(' image_path ,', image_path)
            #         article_object.image_path = image_path
            #         article_object.save()
            # except Exception as e:
            #     pass
            image_url = article_object.image.url
            image = request.build_absolute_uri(image_url)
            FcmNotifications(request, title, keyword, article_object.image_path)

            messages.success(request, _("Article Add Successfully, check it out on the home page!"),
                             extra_tags='Article')

            return HttpResponseRedirect(reverse('core:AdminBlogArticleList'))

    else:
        article_form = AdminBlogArticleForm()
        tags_form = AdminBlogArticleTagsForm()
        context = {
            'blog_tags': blog_tags,
            'article_form': article_form,
            'tags_form': tags_form,
            'seo_form': AdminCommonSeoForm,
            'current_page': _('Add'),
            'prev_Page': _('Articles'),
            'prev_Page_url': reverse_lazy('core:AdminBlogArticleList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/blog/article/sadd.html', context)
    context = {
        'blog_tags': blog_tags,
        'article_form': article_form,
        'tags_form': tags_form,
        'seo_form': AdminCommonSeoForm,
        'current_page': _('Add'),
        'prev_Page': _('Articles'),
        'prev_Page_url': reverse_lazy('core:AdminBlogArticleList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/blog/article/sadd.html', context)

@authenticated_staf
@author_only
def AdminBlogArticleUpdate(request, slug):  # sourcery skip: aug-assign, convert-to-enumerate
    article = BlogArticle.objects.get(slug=slug)
    categories = BlogCategories.objects.all()
    tags = CommonTags.objects.all()
    article_tag = CommonTags.objects.filter(owner_model=ContentType.objects.get(model='BlogArticle'),
                                            owner_id=article.id)

    if request.method == "POST":
        article_form = AdminBlogArticleForm(request.POST or None, request.FILES or None)

        if article_form:

            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            category = request.POST.get('category')
            body = request.POST.get('body')
            pub_time = request.POST.get('pub_time')
            pub_type = request.POST.get('pub_type')
            is_featured = request.POST.get('is_featured')
            comment_status = request.POST.get('comment_status')
            tags = request.POST.getlist('tags')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')
            ########## Image #########
            hero_image = request.FILES.get('hero_image')
            images = request.FILES.getlist('images')
            image_path = request.POST.get('image_path')
            image_url = request.POST.getlist('image_url')
            video_url = request.POST.get('video_url')
            video_cover = request.FILES.get('video_cover')
            author = request.POST.get('author')
            country = request.POST.get('country')
            sport = request.POST.get('sport')
            ########## Seo #########
            meta_title = title
            meta_keywords = keyword
            meta_description = keyword
            seo_image = hero_image
            ########## Category #########
            if pub_time == '' or pub_time == None:
                pub_time = datetime.now()
            if category == '' or category == None:
                category_id = None
            else:
                category_id = BlogCategories.objects.get(id=category)
            if sport == '' or sport == None:
                sport = None
            else:
                sport = Sport.objects.get(id=sport)
            article_object = BlogArticle.objects.get(slug=slug)
            article_object.title = title
            article_object.keyword = title
            article_object.category = category_id
            article_object.body = body
            article_object.pub_time = pub_time
            article_object.pub_type = pub_type
            article_object.is_featured = is_featured
            article_object.comment_status = comment_status
            article_object.author = 'Blog'
            article_object.country = country
            article_object.sport = sport

            if hero_image:
                article_object.image = hero_image
            article_object.image_path = request._current_scheme_host + str(article_object.image.url)
            article_object.save()
            AdminCommonSeo(request, meta_title, meta_description, meta_keywords, None, seo_image, 'BlogArticle',
                           article_object.id)
            image_url = article_object.image.url
            image = request.build_absolute_uri(image_url)
            FcmNotifications(request, title, keyword, article_object.image_path)

            messages.success(request, _("Article Update Successfully, check it out on the home page!"),
                             extra_tags='Article')

            return HttpResponseRedirect(reverse('core:AdminBlogArticleList'))
    context = {
        'categories': categories,
        'tags': tags,
        'article': article,
        'article_tag': article_tag,
        # 'article_cover': article_cover,
        # 'article_video': article_video,
        # 'article_images': article_images,
        # 'article_translate': article_translate,
        # 'article_seo': article_seo,
        'article_form': AdminBlogArticleForm(),
        'tags_form': AdminBlogArticleTagsForm(),
        'seo_form': AdminCommonSeoForm,
        'current_page': _('Update'),
        'prev_Page': _('Article'),
        'prev_Page_link': reverse_lazy('core:AdminBlogArticleList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/blog/article/update.html', context)


@authenticated_staf
@author_only
def AdminBlogArticleArchive(request, slug):
    article = BlogArticle.objects.get(slug=slug)

    if request.method == "POST":
        article.status = 'Archive'
        messages.success(request, _("Article deleted successfully"))
        return HttpResponseRedirect(reverse('core:AdminBlogArticleList'))
    return HttpResponseRedirect(reverse('core:AdminBlogArticleList'))


@authenticated_staf
@staff_only
def AdminBlogArticleDelete(request, slug):
    article = BlogArticle.objects.get(slug=slug)

    if request.method == "POST":
        try:
            article_cover = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model='BlogArticle')
                                                         , owner_id=article.id, type='hero')
            article_video = CommonMediaFiles.objects.get(owner_model=ContentType.objects.get(model='BlogArticle'),
                                                         owner_id=article.id, type='video')

            article_translate = CommonTranslate.objects.get(
                owner_model=ContentType.objects.get(model='BlogArticle'), owner_id=article.id)
            article_seo = CommonSeo.objects.get(owner_model=ContentType.objects.get(model='BlogArticle'),
                                                owner_id=article.id)
            article_tag = CommonTags.objects.filter(owner_model=ContentType.objects.get(model='BlogArticle'),
                                                    owner_id=article.id)
            article_images = CommonMediaFiles.objects.filter(owner_model=ContentType.objects.get(model='BlogArticle')
                                                             , owner_id=article.id, type='image')
            article_cover.delete()
            article_video.delete()
            article_translate.delete()
            article_seo.delete()
            for tag in article_tag:
                article.tags.remove(tag)
            for image in article_images:
                image.delete()
            article.delete()

        except Exception as e:

            article.delete()
        messages.success(request, _("Article deleted successfully"))
        return HttpResponseRedirect(reverse('core:AdminBlogArticleList'))
    return HttpResponseRedirect(reverse('core:AdminBlogArticleList'))


def AdminApiBlogArticleImageDelete(request, slug):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == "POST":
        try:
            article_image = CommonMediaFiles.objects.get(slug=slug)
            article_image.delete()
            return JsonResponse({'status': 'success', 'message': 'Image Delete Successfully'},
                                status=status.HTTP_200_OK)
        except Exception as e:

            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)




##########################      Blog Video Admin            ################################


@authenticated_staf
@staff_only
def AdminBlogVideoList(request):
    videos = BlogVideo.objects.all()

    if request.method == "POST":
        video_form = AdminBlogVideoForm(request.POST or None, request.FILES or None)
        if video_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            country = request.POST.get('country')
            sport = request.POST.get('sport')
            author = request.POST.get('author')
            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            video_source = request.POST.get('video_source')
            video_url = request.POST.get('video_url')

            sport= Sport.objects.get(id=sport)
            video_object = BlogVideo(title=title, keyword=keyword, country=country, sport=sport,
                                     author=author, image=image,image_path=image_path, video_source=video_source, video_url=video_url)

            video_object.save()
            messages.success(request, _("Video Add Successfully, check it out on the home page!"),
                             extra_tags='Video')
            return HttpResponseRedirect(reverse('core:AdminBlogVideoList'))
        else:
            messages.error(request, _("Video Not Add , Please Try Again"), extra_tags='Video')

    context = {
        'videos': videos,
        'video_form': AdminBlogVideoForm(),
        'current_page': _('Videos')
    }
    return render(request, f'{BACKEND_TEMPLATES}/blog/video/admin.html', context)