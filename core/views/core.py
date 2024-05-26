import ctypes
import json
import random
import string

from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView


from core.forms.core import SystemSettingForm, AdminCommonSocialLinkForm, AdminCommonSeoForm, AdminUpdateCommonSeoForm, \
    AdminSiteSettingUpdateForm, AdminSiteSettingForm, AdminCommonTranslateForm, AdminHelpCategoriesForm, \
    AdminHelpQuestionsForm
from core.models.core import SystemSetting, SiteSetting, CommonSeo, CommonSocialLink, HelpCategories, CommonTranslate, \
    HelpQuestions, CommonMediaFiles, CommonTags, CommonComment, CommonProfile, QrCode
from core.models.localization import Country
from core.utils.notification import FcmNotifications
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import superuser_only, staff_only, authenticated_staf, admin_only

User = get_user_model()
UserModel = get_user_model()


@authenticated_staf
@staff_only
def AdminIndex(request):
    data = None
    system_app = SystemSetting.objects.get(title='Digithup')



    context = {

        'current_page': _('Dashboard'),
        'room_name': "broadcast"
    }
    return render(request, f'backend/{BACKEND_TEMPLATES}/index.html', context)



####################### Admin Site Setting  #############
@authenticated_staf
@admin_only
def AdminSiteSettingList(request):
    sites = SiteSetting.objects.all()

    context = {
        'sites': sites,
        'current_page': _('Site Setting'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/core/site/admin.html', context)


@authenticated_staf
@admin_only
def AdminSiteSettingDetails(request, slug):
    site = SiteSetting.objects.get(slug=slug)
    seo = CommonSeo.objects.filter(Q(owner_id=site.id))
    social = CommonSocialLink.objects.filter(Q(owner_id=site.id))
    context = {
        'site': site,
        'seo': seo,
        'social': social,
        'current_page': _('Site Setting'),
        'prev_Page': _('Site Setting'),
        'prev_Page_link': reverse_lazy('core:AdminSiteSettingList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/core/site/details.html', context)


@authenticated_staf
@admin_only
def AdminSiteSettingCreate(request):
    if request.method == "POST":
        setting_form = AdminSiteSettingForm(request.POST or None, request.FILES or None)
        social_form = AdminCommonSocialLinkForm(request.POST or None, request.FILES or None)
        seo_form = AdminCommonSeoForm(request.POST or None, request.FILES or None)
        current_domain = get_current_site(request).domain
        print('current_domain', current_domain)

        if setting_form.is_valid() and seo_form.is_valid():

            product_created = True
            title = setting_form.cleaned_data['title']
            keywords = setting_form.cleaned_data['keywords']
            email = setting_form.cleaned_data['email']
            image = setting_form.cleaned_data['image']
            domain = setting_form.cleaned_data['domain']
            address = setting_form.cleaned_data['address']
            copyright = setting_form.cleaned_data['copyright']
            about = setting_form.cleaned_data['about']
            country_id = request.POST.get('country')
            phone = setting_form.cleaned_data['phone']
            status = setting_form.cleaned_data['status']
            ######### Socail Link ####
            providers = request.POST.getlist('providers')
            urls = request.POST.getlist('urls')
            #########Seo Setting####
            meta_title = request.POST.get('meta_title')
            meta_description = request.POST.get('meta_description')
            meta_keywords = request.POST.get('meta_keywords')
            meta_author = request.POST.get('meta_author')
            seo_image = request.FILES.get('seo_image')
            country = Country.objects.get(id=country_id)
            user_id = request.user.id
            user = User.objects.get(id=user_id)

            setting_form = None
            if not setting_form:
                print(country_id)

                setting_form = SiteSetting(title=title, keywords=keywords, copyright=copyright, email=email,
                                           image=image, domain=domain, country=country, phone=phone, address=address,
                                           about=about, status=status, )
                setting_form.save()

                AdminCommonSeo(request, meta_title, meta_description, meta_keywords, meta_author, seo_image,
                               'SiteSetting', setting_form.id)
                site = Site.objects.get(id=1)
                site.title = title
                site.domain = domain
                site.save()
                setting_form.save()
                for i, url in enumerate(urls):
                    if url != '':
                        AdminCommonSocialLink(request, providers[i], url, 'SiteSetting', setting_form.id)

                # use django messages framework
                messages.success(request,
                                 "Yeeew, check it out on the home page!")
                return HttpResponseRedirect(reverse_lazy('core:AdminSiteSettingList'))
            else:

                messages.error(request, "Error")
    else:
        setting_form = AdminSiteSettingForm()
        social_form = AdminCommonSocialLinkForm()
        seo_form = AdminCommonSeoForm()
        context = {
            'setting_form': setting_form,
            'social_form': social_form,
            'seo_form': seo_form,
            'current_page': _('Add Site Setting'),
            'prev_Page': _('Site Setting'),
            'prev_Page_link': reverse_lazy('core:AdminSiteSettingList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/core/site/add.html', context)
    context = {
        'setting_form': setting_form,
        'social_form': social_form,
        'seo_form': seo_form,
        'current_page': _('Add'),
        'prev_Page': _('Site Info'),
        'prev_Page_link': reverse_lazy('core:AdminSiteSettingList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/core/site/add.html', context)


@authenticated_staf
@admin_only
def AdminSiteSettingUpdate(request, slug):
    site = SiteSetting.objects.get(slug=slug)
    social = CommonSocialLink.objects.filter(owner_model=ContentType.objects.get(model='SiteSetting'), owner_id=site.id)
    try:

        seo = CommonSeo.objects.get(owner_model=ContentType.objects.get(model='SiteSetting'),owner_id=site.id)
    except:

        seo = None
    current_domain = get_current_site(request)
    setting_form = AdminSiteSettingUpdateForm()
    social_form = AdminCommonSocialLinkForm()
    seo_form = AdminUpdateCommonSeoForm()

    if request.method == "POST":
        setting_form = AdminSiteSettingUpdateForm(request.POST or None, request.FILES or None)
        social_form = AdminCommonSocialLinkForm(request.POST or None, request.FILES or None)
        seo_form = AdminUpdateCommonSeoForm(request.POST or None, request.FILES or None)
        if setting_form.is_valid():

            title = setting_form.cleaned_data['title']
            keywords = setting_form.cleaned_data['keywords']
            email = setting_form.cleaned_data['email']
            image = setting_form.cleaned_data['image']
            domain = setting_form.cleaned_data['domain']
            address = setting_form.cleaned_data['address']
            copyright = setting_form.cleaned_data['copyright']
            about = setting_form.cleaned_data['about']
            country_id = request.POST.get('country')
            phone = setting_form.cleaned_data['phone']
            status = setting_form.cleaned_data['status']
            ######### Socail Link ####
            providers = request.POST.getlist('providers')
            url = request.POST.getlist('url')
            #########Seo Setting####
            meta_title = title
            meta_description = keywords
            meta_keywords = title
            meta_author = request.user.id

            try:
                country = Country.objects.get(id=country_id)
            except:
                country = None
            user_id = request.user.id
            setting_object = SiteSetting.objects.get(slug=slug)
            setting_object.title = title
            setting_object.keywords = keywords
            setting_object.copyright = copyright
            setting_object.email = email
            setting_object.domain = domain
            if image == '' or image is None:
                setting_object.image = setting_object.image
            else:
                setting_object.image = image
            setting_object.country = country
            setting_object.phone = phone
            setting_object.address = address
            setting_object.about = about
            setting_object.status = status

            setting_object.save()
            if domain != '' or domain != None:
                domain = request._current_scheme_host
                sites = Site.objects.all()
                for site in sites:
                    site.domain = domain
                    site.name = title
                    site.save()
            print('providers', providers)

            j = 0
            for provider in providers:
                print('provider', provider)
                if provider != '':
                    try:
                        social = CommonSocialLink.objects.get(Q(owner_id=setting_object.id), Q(provider=provider))
                        social.url = url[j]
                        social.save()
                    except Exception as e:
                        print(e)
                        AdminCommonSocialLink(request, provider, url[j], 'SiteSetting', setting_object.id)

                j = j + 1

            AdminCommonSeo(request, meta_title, meta_description, meta_keywords, meta_author, setting_object.image,
                           'SiteSetting', setting_object.id)

            messages.success(request,
                             _("Setting Add Successfully, check it out on the home page!"), extra_tags='Setting')
            return HttpResponseRedirect(reverse_lazy('core:AdminSiteSettingList'))
        else:

            messages.error(request, _("Setting Not Add , check it out on the  page!"), extra_tags='Setting')

    context = {
        'site': site,
        'social': social,
        'seo': seo,
        'current_domain': current_domain,
        'setting_form': AdminSiteSettingUpdateForm(instance=site),
        'social_form': social_form,
        'seo_form': seo_form,
        'current_page': _('Update'),
        'prev_Page': _('Site Info'),
        'prev_Page_link': reverse_lazy('core:AdminSiteSettingList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/core/site/update.html', context)


@authenticated_staf
@admin_only
def AdminSiteSettingDelete(request, slug):
    site = SiteSetting.objects.get(slug=slug)
    if request.method == "POST":
        site.delete()
        messages.success(request, _("Setting Delete Successfully"), extra_tags='Setting')

        return HttpResponseRedirect(reverse_lazy('core:AdminSiteSettingList'))
    else:
        messages.error(request, _("Setting Not Delete , Please Try Again"), extra_tags='Setting')

    return HttpResponseRedirect(reverse_lazy('core:AdminSiteSettingList'))


##########################      System Setting Admin            ################################

@authenticated_staf
@admin_only
def AdminSystemSettingList(request):
    systems = SystemSetting.objects.all()
    context = {
        'systems': systems,
        'current_page': _('System Setting'),
        'prev_Page': _('System Setting'),
        'prev_Page_link': reverse_lazy('core:AdminSystemSettingList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/core/system/admin.html', context)


@authenticated_staf
@admin_only
def AdminSystemSettingDetail(request, slug):
    system = SystemSetting.objects.get(slug=slug)
    context = {
        'system': system,
        'current_page': _('Detail'),
        'prev_Page': _('System Setting'),
        'prev_Page_link': reverse_lazy('core:AdminSystemSetting'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/core/system/details.html', context)


class AdminSystemSettingCreate(CreateView):
    model = SystemSetting
    form_class = SystemSettingForm
    template_name = f'{BACKEND_TEMPLATES}/core/system/admin.html'
    success_url = reverse_lazy('core:AdminSystemSetting')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['prev_Page'] = _('System Setting')
        context['prev_Page_link'] = reverse_lazy('core:AdminSystemSettingList')
        context['current_page'] = _('Create')
        return context

    @method_decorator(authenticated_staf, superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(AdminSystemSettingCreate, self).dispatch(*args, **kwargs)


@authenticated_staf
@superuser_only
def AdminSystemSettingUpdate(request, slug):
    system = SystemSetting.objects.get(slug=slug)
    if request.method == "POST":
        system_form = SystemSettingForm(request.POST or None, request.FILES or None, instance=system)
        if system_form:
            vendor = request.POST.get('vendor')
            maintenance = request.POST.get('maintenance')
            maintenance_temp = request.POST.get('maintenance_temp')
            title = request.POST.get('title')
            frontend_temp = request.POST.get('frontend_temp')
            home_index = request.POST.get('home_index')
            backend_temp = request.POST.get('backend_temp')
            membership = request.POST.get('membership')
            registration = request.POST.get('registration')
            app = request.POST.get('app')
            fb_id = request.POST.get('fb_id')
            fb_secret = request.POST.get('fb_secret')
            gp_id = request.POST.get('gp_id')
            gb_secret = request.POST.get('gb_secret')
            email_host = request.POST.get('email_host')
            email_user = request.POST.get('email_user')
            email_pass = request.POST.get('email_pass')
            email_from = request.POST.get('email_from')
            api_url = request.POST.get('api_url')

            check_title = SystemSetting.objects.filter(title=title).exclude(slug=slug)
            if check_title:
                messages.error(request, _("Setting Already Exist , Please Try Again"), extra_tags='Setting')
                return HttpResponseRedirect(reverse_lazy('core:AdminSystemSettingUpdate', kwargs={'slug': slug}))

            system_object = SystemSetting.objects.get(slug=slug)
            system_object.title = title
            system_object.vendor = vendor
            system_object.maintenance = maintenance
            system_object.maintenance_temp = maintenance_temp
            system_object.frontend_temp = frontend_temp
            system_object.home_index = home_index
            system_object.backend_temp = backend_temp
            system_object.membership = membership
            system_object.registration = registration
            system_object.app = app
            system_object.fb_id = fb_id
            system_object.fb_secret = fb_secret
            system_object.gp_id = gp_id
            system_object.gb_secret = gb_secret
            system_object.email_host = email_host
            system_object.email_user = email_user
            system_object.email_pass = email_pass
            system_object.email_from = email_from
            system_object.api_url = api_url

            system_object.save()

            messages.success(request, _("Setting Update Successfully"), extra_tags='Setting')

            return HttpResponseRedirect(reverse_lazy('core:AdminSystemSettingList'))
        else:
            messages.error(request, _("Setting Not Update , Please Try Again"), extra_tags='Setting')

    else:
        context = {
            'system': system,
            'system_form': SystemSettingForm(instance=system),
            'current_page': _('Update'),
            'prev_Page': _('System Setting'),
            'prev_Page_link': reverse_lazy('core:AdminSystemSettingList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/core/system/update.html', context)
    context = {
        'system': system,
        'system_form': SystemSettingForm(),
        'current_page': _('Update'),
        'prev_Page': _('System Setting'),
        'prev_Page_link': reverse_lazy('core:AdminSystemSettingList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/core/system/update.html', context)


@authenticated_staf
@admin_only
def AdminSystemSettingDelete(request, slug):
    system = SystemSetting.objects.get(slug=slug)
    if request.method == "POST":
        system.delete()
        messages.success(request, _("Setting Delete Successfully"), extra_tags='Setting')

        return HttpResponseRedirect(reverse_lazy('core:AdminSystemSettingList'))
    else:
        messages.error(request, _("Setting Not Delete , Please Try Again"), extra_tags='Setting')

    return HttpResponseRedirect(reverse_lazy('core:AdminSystemSettingList'))


def AdminError403(request, ):
    return render(request, f'{BACKEND_TEMPLATES}/error/403.html', status=403)


def AdminError404(request, ):
    return render(request, f'{BACKEND_TEMPLATES}/error/404.html', status=404)


##########  Help Category Admin #########

@authenticated_staf
@staff_only
def AdminHelpDocumentationList(request):
    categories = HelpCategories.objects.all()

    context = {
        'categories': categories,
        'category_form': AdminHelpCategoriesForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Help Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/core/help/documentation/documentation.html', context)


@authenticated_staf
@staff_only
def AdminHelpFaqList(request):
    categories = HelpCategories.objects.all()
    questions = HelpQuestions.objects.all()
    popular_questions = HelpQuestions.objects.all().order_by('-views')[:5]

    context = {
        'categories': categories,
        'questions': questions,
        'popular_questions': popular_questions,
        'category_form': AdminHelpCategoriesForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Help Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/core/help/documentation/faq.html', context)


@authenticated_staf
@staff_only
def AdminHelpTutorialList(request):
    categories = HelpCategories.objects.all()
    questions = HelpQuestions.objects.all()
    current_language = request.LANGUAGE_CODE
    translate = None
    tutorials_list = []
    for question in questions:
        image = CommonMediaFiles.objects.get(type='hero',
                                             owner_model=ContentType.objects.get(model='HelpQuestions'),
                                             owner_id=question.id)
        translates = CommonTranslate.objects.get(
            owner_model=ContentType.objects.get(model='HelpQuestions'), owner_id=question.id)
        video = CommonMediaFiles.objects.get(type='video', owner_id=question.id,
                                             owner_model=ContentType.objects.get(model='HelpQuestions'),
                                             )
        if current_language == 'ar':
            print('list', current_language)

            translate = translates
        elif current_language == 'en':
            print('list', current_language)
            translate = question
        tutorials_list.append(
            {"question": question, "image": image, "video": video, "translate": translate, })

    context = {
        'categories': categories,
        'tutorials': tutorials_list,
        'category_form': AdminHelpCategoriesForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Help Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/core/help/documentation/tutorial.html', context)


@authenticated_staf
@staff_only
def AdminHelpCategoriesList(request):
    categories = HelpCategories.objects.all()

    if request.method == "POST":
        category_form = AdminHelpCategoriesForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if category_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')

            status = request.POST.get('status')
            image = request.FILES.get('hero_image')

            category_object = HelpCategories(title=title, keyword=keyword, status=status
                                             , image=image)
            category_object.save()

            messages.success(request, _("Category Add Successfully"), extra_tags='HelpCategories')

            return HttpResponseRedirect(reverse_lazy('core:AdminHelpCategoriesList'))
        else:

            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='HelpCategories')

    else:
        context = {
            'categories': categories,
            'category_form': AdminHelpCategoriesForm(),
            'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Help Categories')

        }
        return render(request, f'{BACKEND_TEMPLATES}/core/help/category/admin.html', context)
    context = {
        'categories': categories,
        'category_form': AdminHelpCategoriesForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Help Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/core/help/category/admin.html', context)


@authenticated_staf
@staff_only
def AdminHelpCategoriesUpdate(request, slug):
    categories = HelpCategories.objects.all()
    category = HelpCategories.objects.get(slug=slug)

    if request.method == "POST":
        category_form = AdminHelpCategoriesForm(request.POST or None, request.FILES or None, instance=category)

        if category_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            parent = request.POST.get('parent')
            status = request.POST.get('status')
            image = request.FILES.get('hero_image')

            check_title = HelpCategories.objects.filter(title=title).exclude(slug=slug)
            if check_title:
                messages.error(request, _("Category Already Exist , Please Try Again"), extra_tags='HelpCategories')
                return HttpResponseRedirect(reverse_lazy('core:AdminHelpCategoriesUpdate', kwargs={'slug': slug}))

            try:
                parent_id = HelpCategories.objects.get(id=parent)
            except Exception as e:
                parent_id = None
            category_object = HelpCategories.objects.get(slug=slug)
            category_object.title = title
            category_object.keyword = keyword
            category_object.parent = parent_id
            category_object.status = status
            if image:
                category_object.image = image
            category_object.save()

            messages.success(request, _("Category Update Successfully"), extra_tags='HelpCategories')

            return HttpResponseRedirect(reverse_lazy('core:AdminHelpCategoriesList'))
        else:
            messages.error(request, _("Category Not Update , Please Try Again"), extra_tags='HelpCategories')

    else:
        context = {
            'categories': categories,
            'category': category,

            'category_form': AdminHelpCategoriesForm(instance=category),

            'current_page': _('Help Categories')

        }
        return render(request, f'{BACKEND_TEMPLATES}/core/help/category/update.html', context)
    context = {
        'categories': categories,
        'category': category,

        'category_form': AdminHelpCategoriesForm(),

        'current_page': _('Help Categories')

    }
    return render(request, f'{BACKEND_TEMPLATES}/core/help/category/update.html', context)


@authenticated_staf
@staff_only
def AdminHelpCategoriesDelete(request, slug):
    category = HelpCategories.objects.get(slug=slug)

    category.delete()

    messages.success(request, _("Category Delete Successfully"), extra_tags='HelpCategories')

    return HttpResponseRedirect(reverse_lazy('core:AdminHelpCategoriesList'))


##########  Help Questions Admin #########

@authenticated_staf
@staff_only
def AdminHelpQuestionsList(request):
    questions = HelpQuestions.objects.all()
    questions_list = []
    for question in questions:
        image = CommonMediaFiles.objects.get(type='hero',
                                             owner_model=ContentType.objects.get(model='HelpQuestions'),
                                             owner_id=question.id)
        translate = CommonTranslate.objects.get(
            owner_model=ContentType.objects.get(model='HelpQuestions'), owner_id=question.id)
        questions_list.append(
            {"question": question, "image": image, "translate": translate, })

    context = {
        'questions': questions_list,
        'current_page': _('Help Questions'),

    }

    return render(request, f'{BACKEND_TEMPLATES}/core/help/questions/admin.html', context)


@authenticated_staf
@staff_only
def AdminHelpQuestionsDetail(request, slug):
    categories = HelpCategories.objects.all()
    question = HelpQuestions.objects.get(slug=slug)

    image = CommonMediaFiles.objects.get(type='hero',
                                         owner_model=ContentType.objects.get(model='HelpQuestions'),
                                         owner_id=question.id)

    video = CommonMediaFiles.objects.get(type='video',
                                         owner_model=ContentType.objects.get(model='HelpQuestions'),
                                         owner_id=question.id)
    translate = CommonTranslate.objects.get(
        owner_model=ContentType.objects.get(model='HelpQuestions'), owner_id=question.id)
    seo = CommonSeo.objects.get(
        owner_model=ContentType.objects.get(model='HelpQuestions'), owner_id=question.id)
    current_language = request.LANGUAGE_CODE
    questions = HelpQuestions.objects.all()
    questions_list = []
    for question in questions:
        image = CommonMediaFiles.objects.get(type='hero',
                                             owner_model=ContentType.objects.get(model='HelpQuestions'),
                                             owner_id=question.id)
        translates = CommonTranslate.objects.get(
            owner_model=ContentType.objects.get(model='HelpQuestions'), owner_id=question.id)
        video = CommonMediaFiles.objects.get(type='video', owner_id=question.id,
                                             owner_model=ContentType.objects.get(model='HelpQuestions'),
                                             )
        if current_language == 'ar':
            print('list', current_language)

            translate = translates
        elif current_language == 'en':
            print('list', current_language)
            translate = question
        questions_list.append(
            {"question": question, "image": image, "video": video, "translate": translate, })
    if current_language == 'ar':
        question = translate
    elif current_language == 'en':
        question = question

    context = {
        'categories': categories,
        'question': question,
        'image': image,
        'video': video,
        'translate': translate,
        'seo': seo,
        'questions': questions_list,

        'current_page': _('Help Questions'),

    }

    return render(request, f'{BACKEND_TEMPLATES}/core/help/questions/details.html', context)


@authenticated_staf
@staff_only
def AdminCreateHelpQuestions(request):
    if request.method == "POST":

        questions_form = AdminHelpQuestionsForm(request.POST or None, request.FILES or None)

        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)

        if questions_form.is_valid():

            product_created = True

            category = questions_form.cleaned_data['category']
            title = questions_form.cleaned_data['title']
            body = questions_form.cleaned_data['body']
            keyword = questions_form.cleaned_data['keyword']
            status = questions_form.cleaned_data['status']

            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')

            category = HelpCategories.objects.get(title=category)
            hero_image = request.FILES.get('hero_image')
            images = request.FILES.getlist('images')
            image_url = request.POST.getlist('image_url')
            video_url = request.POST.get('video_url')
            video_cover = request.FILES.get('video_cover')
            ########## Seo #########
            meta_title = title
            meta_description = keyword
            meta_keywords = title
            seo_image = hero_image
            author = User.objects.get(id=request.user.id)

            if questions_form:
                questions_object = HelpQuestions(title=title, keyword=keyword, category=category,
                                                 body=body, status=status, )
                questions_object.save()
                translate = CommonTranslate(title=title_tr, keyword=keyword_tr, body=body_tr,
                                            owner_model=ContentType.objects.get(model='HelpQuestions'),
                                            owner_id=questions_object.id)
                translate.save()
                seo_object = CommonSeo(owner_model=ContentType.objects.get(model='HelpQuestions'),
                                       owner_id=questions_object.id, meta_title=meta_title,
                                       meta_description=meta_description, meta_keywords=meta_keywords,
                                       meta_author=author, seo_image=seo_image, )
                seo_object.save()
                hero = CommonMediaFiles(image=hero_image, type='hero',
                                        owner_model=ContentType.objects.get(model='HelpQuestions'),
                                        owner_id=questions_object.id)
                hero.save()
                video = CommonMediaFiles(video=video_url, video_cover=video_cover, type='video',
                                         owner_model=ContentType.objects.get(model='HelpQuestions'),
                                         owner_id=questions_object.id)
                video.save()
                i = 0
                for image in images:
                    image = CommonMediaFiles(image=image, type='image',
                                             owner_model=ContentType.objects.get(model='HelpQuestions'),
                                             owner_id=questions_object.id)
                    image.save()
                    i = i + 1

                messages.success(request, _("Questions Add Successfully"), extra_tags='HelpQuestions')

                return HttpResponseRedirect(reverse_lazy('core:AdminHelpQuestionsList'))

        else:

            messages.error(request, _("Questions Not Add , Please Try Again"), extra_tags='HelpQuestions')
    else:

        questions_form = AdminHelpQuestionsForm()

        translate_form = AdminCommonTranslateForm()
        context = {'questions_form': questions_form,
                   'translate_form': translate_form,
                   'current_page': _('Add'),
                   'prev_Page': _('Products'),
                   'prev_Page_link': reverse_lazy('core:AdminHelpQuestionsList'),
                   }

        return render(request, f'{BACKEND_TEMPLATES}/core/help/questions/add.html',
                      context=context
                      )
    context = {'questions_form': questions_form,
               'translate_form': translate_form,
               'current_page': _('Add'),
               'prev_Page': _('Products'),
               'prev_Page_link': reverse_lazy('core:AdminHelpQuestionsList'),
               }

    return render(request, f'{BACKEND_TEMPLATES}/core/help/questions/add.html',
                  context=context
                  )


@authenticated_staf
@staff_only
def AdminHelpQuestionsUpdate(request, slug):
    question = HelpQuestions.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(
        owner_model=ContentType.objects.get(model='HelpQuestions'), owner_id=question.id)
    hero_image = CommonMediaFiles.objects.get(type='hero',
                                              owner_model=ContentType.objects.get(model='HelpQuestions'),
                                              owner_id=question.id)
    video = CommonMediaFiles.objects.get(type='video',
                                         owner_model=ContentType.objects.get(model='HelpQuestions'),
                                         owner_id=question.id)
    images = CommonMediaFiles.objects.filter(type='image',
                                             owner_model=ContentType.objects.get(model='HelpQuestions'),
                                             owner_id=question.id)
    if request.method == "POST":

        questions_form = AdminHelpQuestionsForm(request.POST or None, request.FILES or None)

        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)

        if questions_form:
            category = request.POST.get('category')
            title = request.POST.get('title')
            body = request.POST.get('body')
            keyword = request.POST.get('keyword')
            status = request.POST.get('status')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')
            hero_image = request.FILES.get('hero_image')
            images = request.FILES.getlist('images')
            image_url = request.POST.getlist('image_url')
            video_url = request.POST.get('video_url')
            video_cover = request.FILES.get('video_cover')
            ########## Seo #########
            meta_title = title
            meta_description = keyword
            meta_keywords = title
            seo_image = hero_image
            category = HelpCategories.objects.get(title=category)

            author = User.objects.get(id=request.user.id)

            questions_object = HelpQuestions.objects.get(slug=slug)
            questions_object.title = title
            questions_object.keyword = keyword
            questions_object.category = category
            questions_object.body = body
            questions_object.status = status
            if hero_image == '' or hero_image is None:
                questions_object.image = questions_object.image
            else:
                questions_object.image = hero_image
            questions_object.save()
            translate = CommonTranslate(title=title_tr, keyword=keyword_tr, body=body_tr,
                                        owner_model=ContentType.objects.get(model='HelpQuestions'),
                                        owner_id=questions_object.id)
            translate.save()
            seo_form = CommonSeo(owner_model=ContentType.objects.get(model='HelpQuestions'),
                                 owner_id=questions_object.id, meta_title=meta_title,
                                 meta_description=meta_description, meta_keywords=meta_keywords,
                                 meta_author=author, seo_image=seo_image, )
            seo_form.save()
            hero = CommonMediaFiles(image=hero_image, type='hero',
                                    owner_model=ContentType.objects.get(model='HelpQuestions'),
                                    owner_id=questions_object.id)
            hero.save()
            video = CommonMediaFiles(video=video_url, video_cover=video_cover, type='video',
                                     owner_model=ContentType.objects.get(model='HelpQuestions'),
                                     owner_id=questions_object.id)
            video.save()
            i = 0
            for image in images:
                image = CommonMediaFiles(image=image, type='image',
                                         owner_model=ContentType.objects.get(model='HelpQuestions'),
                                         owner_id=questions_object.id)
                image.save()
                i = i + 1

            messages.success(request, _("Questions Add Successfully"), extra_tags='HelpQuestions')

            return HttpResponseRedirect(reverse_lazy('core:AdminHelpQuestionsList'))

        else:

            messages.error(request, _("Questions Not Add , Please Try Again"), extra_tags='HelpQuestions')
    else:

        questions_form = AdminHelpQuestionsForm()

        translate_form = AdminCommonTranslateForm()
        context = {
            'question': question,
            'translate': translate,
            'hero_image': hero_image,
            'video': video,
            'images': images,
            'questions_form': questions_form,
            'translate_form': translate_form,
            'current_page': _('Add'),
            'prev_Page': _('Products'),
            'prev_Page_link': reverse_lazy('core:AdminHelpQuestionsList'),
        }

        return render(request, f'{BACKEND_TEMPLATES}/core/help/questions/update.html',
                      context=context
                      )
    context = {
        'question': question,
        'translate': translate,
        'questions_form': questions_form,
        'translate_form': translate_form,
        'current_page': _('Add'),
        'prev_Page': _('Products'),
        'prev_Page_link': reverse_lazy('core:AdminHelpQuestionsList'),
    }

    return render(request, f'{BACKEND_TEMPLATES}/core/help/questions/update.html',
                  context=context
                  )


@authenticated_staf
@staff_only
def AdminHelpQuestionsDelete(request, slug):
    question = HelpQuestions.objects.get(slug=slug)
    hero_image = CommonMediaFiles.objects.get(type='hero',
                                              owner_model=ContentType.objects.get(model='HelpQuestions'),
                                              owner_id=question.id)
    video = CommonMediaFiles.objects.get(type='video',
                                         owner_model=ContentType.objects.get(model='HelpQuestions'),
                                         owner_id=question.id)
    images = CommonMediaFiles.objects.filter(type='image',
                                             owner_model=ContentType.objects.get(model='HelpQuestions'),
                                             owner_id=question.id)
    if request.method == "POST":
        hero_image.delete()
        video.delete()
        for image in images:
            image.delete()
        question.delete()

        messages.success(request, _("Questions Delete Successfully"), extra_tags='HelpQuestions')
        return HttpResponseRedirect(reverse_lazy('core:AdminHelpQuestionsList'))


def AdminCommonMediaHeroFiles(request, hero_image, owner_model, owner_id):
    try:
        hero_object = CommonMediaFiles.objects.get(type='hero', owner_model=ContentType.objects.get(model=owner_model),
                                                   owner_id=owner_id)
        if hero_image:
            hero_object.image = hero_image
        else:
            hero_object.image = hero_object.image
        hero_object.save()
    except:
        hero_object = CommonMediaFiles(image=hero_image, type='hero',
                                       owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id)
        hero_object.save()


def AdminCommonMediaImagesFiles(request, image, owner_model, owner_id):
    try:
        image_object = CommonMediaFiles.objects.get(type='image',
                                                    owner_model=ContentType.objects.get(model=owner_model),
                                                    owner_id=owner_id, image=image)
        image_object.image = image
        image_object.save()
    except:
        image_object = CommonMediaFiles(image=image, type='image',
                                        owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id)
        image_object.save()


def AdminCommonMediaFiles(request, file, owner_model, owner_id):
    try:
        image_object = CommonMediaFiles.objects.get(type='file', owner_model=ContentType.objects.get(model=owner_model),
                                                    owner_id=owner_id)
        image_object.file = file
        image_object.save()
    except:
        image_object = CommonMediaFiles(file=file, type='file', owner_model=ContentType.objects.get(model=owner_model),
                                        owner_id=owner_id)
        image_object.save()


def AdminCommonMediaVideoFiles(request, video, video_cover, owner_model, owner_id):
    print("video_cover", video_cover)
    try:
        video_object = CommonMediaFiles.objects.get(type='video',
                                                    owner_model=ContentType.objects.get(model=owner_model),
                                                    owner_id=owner_id)
        video_object.video = video
        if video_cover:
            video_object.video_cover = video_cover
        else:
            video_object.video_cover = video_object.video_cover
        video_object.save()
    except:
        video_object = CommonMediaFiles(video=video, video_cover=video_cover, type='video',
                                        owner_model=ContentType.objects.get(model=owner_model),
                                        owner_id=owner_id)
        video_object.save()


def AdminCommonTags(request, title, keyword, owner_model, owner_id):
    try:
        tags_object = CommonTags.objects.get(owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id)
        tags_object.title = title
        tags_object.keyword = keyword
        tags_object.save()
    except:
        tags_object = CommonTags(title=title, keyword=keyword, owner_model=ContentType.objects.get(model=owner_model),
                                 owner_id=owner_id)
        tags_object.save()


def AdminCommonSeo(request, meta_title, meta_description, meta_keywords, meta_author, seo_image, owner_model, owner_id):
    if meta_author != None:
        meta_author = User.objects.get(id=meta_author)

    try:
        seo_object = CommonSeo.objects.get(owner_model=ContentType.objects.get(model=owner_model),
                                           owner_id=owner_id)
        seo_object.meta_title = meta_title
        seo_object.meta_description = meta_description
        seo_object.meta_keywords = meta_keywords
        if meta_author != None:
            seo_object.meta_author = meta_author
        if seo_image != None:
            seo_object.seo_image = seo_image
        seo_object.save()
    except:
        if meta_author != None:
            seo_object = CommonSeo(owner_model=ContentType.objects.get(model=owner_model),
                                   owner_id=owner_id, meta_title=meta_title,
                                   meta_description=meta_description, meta_keywords=meta_keywords,
                                   meta_author=meta_author, seo_image=seo_image, )
        else:
            seo_object = CommonSeo(owner_model=ContentType.objects.get(model=owner_model),
                                   owner_id=owner_id, meta_title=meta_title,
                                   meta_description=meta_description, meta_keywords=meta_keywords,
                                   seo_image=seo_image, )
        seo_object.save()


def AdminCommonComment(request, profile, name, email, body, owner_model, owner_id):
    comment_object = CommonComment(profile=profile, name=name, email=email,
                                   body=body,
                                   owner_model=ContentType.objects.get(model=owner_model),
                                   owner_id=owner_id)
    comment_object.save()


def AdminCommonSocialLink(request, provider, url, owner_model, owner_id):
    try:
        social = CommonSocialLink.objects.get(owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id,
                                              provider=provider)
        social.provider = provider
        social.url = url
        social.save()
    except:

        social = CommonSocialLink(provider=provider, url=url, owner_model=ContentType.objects.get(model=owner_model),
                                  owner_id=owner_id)
        social.save()


def AdminCommonProfile(request, phone, address_type, address, country, governorates, city, area, note, owner_model,
                       owner_id):
    try:
        print("try")
        profile = CommonProfile.objects.get(owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id)
        profile.phone = phone
        profile.address_type = address_type
        profile.address = address
        profile.country = country
        profile.governorates = governorates
        profile.city = city
        profile.area = area
        profile.note = note
        profile.save()
    except:
        print("except")
        profile = CommonProfile(phone=phone, address_type=address_type, address=address, country=country,
                                governorates=governorates, city=city, area=area, note=note,
                                owner_model=ContentType.objects.get(model=owner_model),
                                owner_id=owner_id)
        profile.save()


def AdminCommonTranslate(request, title, keyword, body, owner_model, owner_id):
    try:
        translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model=owner_model),
                                                owner_id=owner_id)
        translate.title = title
        translate.keyword = keyword
        translate.body = body
        translate.save()
    except:
        translate = CommonTranslate(title=title, keyword=keyword, body=body,
                                    owner_model=ContentType.objects.get(model=owner_model),
                                    owner_id=owner_id)
        translate.save()


def AdminCommonQrCode(request,sender_model,sender_id,receiver_model,receiver_id,  owner_model, owner_id,name,
                      description, body,url,url_pat,slug,icon,barcode_number):
    url = request.build_absolute_uri(reverse(url_pat, args=[slug]))
    try:
        qrcode = QrCode.objects.get(owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id)
        qrcode.sender_model = ContentType.objects.get(model=sender_model)
        qrcode.sender_id = sender_id
        qrcode.receiver_model = ContentType.objects.get(model=receiver_model)
        qrcode.receiver_id = receiver_id
        qrcode.save()
    except:

        if barcode_number == None:
            barcode_number = random.randint(100002000002, 9949999399939,)
        try:
            if barcode_number.startswith("+"):
                barcode_number = barcode_number.replace("+", "")
                random_number1 = str(random.randint(6666, 9999))
                barcode_secret = barcode_number[-4:]
                new_barcode_number = barcode_number[:-6] + random_number1
                random_number2 = str(random.randint(2222, 9999))
                new_barcode_number = random_number2 + barcode_secret + new_barcode_number[:4]
                barcode_number = new_barcode_number
        except Exception as e:
            random_number1 = str(random.randint(6666, 9999))
            barcode_number = str(barcode_number)
            barcode_secret = barcode_number[-4:]
            new_barcode_number = barcode_number[:-6] + random_number1
            random_number2 = str(random.randint(2222, 9999))
            new_barcode_number = random_number2 + barcode_secret + new_barcode_number[:4]
            barcode_number = new_barcode_number
        try:
            barcode_check = QrCode.objects.get(barcode_number=barcode_number)
            if barcode_check:
                barcode_number = random.randint(100002000002, 9949999399939,)
        except:

            random_number1 = str(random.randint(6666, 9999))
            barcode_secret =  barcode_number[-4:]
            new_barcode_number = barcode_number[:-6] + random_number1
            random_number2 = str(random.randint(2222, 9999))
            new_barcode_number = random_number2 +barcode_secret+ new_barcode_number[:4]
            barcode_number = new_barcode_number
        if len(str(barcode_number)) > 7:
            barcode_number =  str(barcode_number)[:7]
        print("barcode_number", barcode_number)



        qr_code = QrCode(sender_model=ContentType.objects.get(model=sender_model), sender_id=sender_id,
                            receiver_model=ContentType.objects.get(model=receiver_model), receiver_id=receiver_id,
            owner_model=ContentType.objects.get(model=owner_model), owner_id=owner_id
                         ,name=name, description=description, body=body,url=url,icon=icon,barcode_number=barcode_number)
        qr_code.save()



