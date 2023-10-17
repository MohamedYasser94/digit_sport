from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse, translate_url
from django.utils import timezone
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _, check_for_language
# Create your views here.
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.i18n import LANGUAGE_QUERY_PARAMETER

from digit_sport.settings import LANGUAGE_SESSION_KEY
from core.forms.core import AdminCommonTranslateForm
from core.forms.localization import AdminCountryForm, AdminCurrencyForm, AdminLanguageForm, AdminCityForm, \
    AdminAreaForm, AdminGovernoratesForm
from core.models.localization import Country, Governorates, City, Area, Language, Currency
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import superuser_only, staff_only, authenticated_staf


#############Rosetta##########

@authenticated_staf
@staff_only
def AdminLanguageList(request):
    languages = Language.objects.all()
    language_form = AdminLanguageForm()
    context = {
        'languages': languages,
        'language_form': language_form,
        'current_page': _('Language'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/language/admin.html', context)


class AdminLanguageCreate(CreateView):
    model = Language
    form_class = AdminLanguageForm
    template_name = f'{BACKEND_TEMPLATES}/localization/language/add.html'
    success_url = reverse_lazy('core:AdminLanguageListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['form'] = AdminLanguageForm
        context['prev_Page'] = _('Languages')
        context['prev_Page_link'] = reverse_lazy('core:AdminLanguageListView')
        context['current_page'] = _('Create')
        return context

    @method_decorator(login_required(login_url='/dashboard/login'), staff_only, )
    def dispatch(self, *args, **kwargs):
        return super(AdminLanguageCreate, self).dispatch(*args, **kwargs)


class AdminLanguageUpdate(UpdateView):
    model = Language
    form_class = AdminLanguageForm
    template_name = f'{BACKEND_TEMPLATES}/localization/language/update.html'
    success_url = reverse_lazy('core:AdminLanguageListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['form'] = AdminLanguageForm
        context['prev_Page'] = _('Languages')
        context['prev_Page_link'] = reverse_lazy('core:AdminLanguageListView')
        context['current_page'] = _('Update')
        return context

    @method_decorator(login_required(login_url='/dashboard/login'), staff_only, )
    def dispatch(self, *args, **kwargs):
        return super(AdminLanguageUpdate, self).dispatch(*args, **kwargs)


class AdminLanguageDelete(DeleteView):
    model = Language
    fields = '__all__'
    success_url = reverse_lazy('core:AdminLanguageListView')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    @method_decorator(superuser_only)
    def dispatch(self, *args, **kwargs):
        return super(AdminLanguageDelete, self).dispatch(*args, **kwargs)


def select_language(request, code):
    try:
        cur_language = code
        lasturl = request.META.get('HTTP_REFERER')
        print(code, '1')
        lang = Language.objects.get(code=code)
        # user_setting = UserSetting.objects.get(user=request.user)
        # user_setting.lang = lang
        # user_setting.save()
        translation.activate(code)

        request.session[LANGUAGE_SESSION_KEY] = 'lang'
        return set_language(request)


    except Exception as e:

        return redirect(request.META['HTTP_REFERER'])

    # if request.user.is_authenticated and request.method == 'POST':  # check post
    #     cur_language = code
    #     lasturl = request.META.get('HTTP_REFERER')
    #     print(code,'1')
    #     lang = Language.objects.get(code=cur_language)
    #     # user_setting = UserSetting.objects.get(user=request.user)
    #     # user_setting.lang = lang
    #     # user_setting.save()
    #     translation.activate(lang)
    #     request.session[LANGUAGE_SESSION_KEY] = lang
    #     # return HttpResponse(lang)
    #     return redirect(request.META['HTTP_REFERER'])
    # else:
    #         cur_language = translation.get_language()
    #         lasturl = request.META.get('HTTP_REFERER')
    #         lang = code
    #         print(lang,2)
    #         translation.activate(lang)
    #         print(lasturl)
    #         # request.session.get
    #
    #         request.session[LANGUAGE_SESSION_KEY] = lang
    #         # return HttpResponse(lang)
    #         return HttpResponseRedirect(lasturl)


def set_language(request):
    """
    Redirect to a given URL while setting the chosen language in the session
    (if enabled) and in a cookie. The URL and the language code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
    next_url = request.POST.get("next", request.GET.get("next"))
    if (
            next_url or request.accepts("text/html")
    ) and not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = request.META.get("HTTP_REFERER")
        if not url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
        ):
            next_url = "/"
    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=204)
    if request.method == "POST":
        lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
        if lang_code and check_for_language(lang_code):
            if next_url:
                next_trans = translate_url(next_url, lang_code)
                if next_trans != next_url:
                    response = HttpResponseRedirect(next_trans)
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                lang_code,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )
    return response


############Currency############

@authenticated_staf
@staff_only
def AdminCurrencyListView(request):
    currencies = Currency.objects.all()
    currency_form = AdminCurrencyForm()
    context = {
        'currencies': currencies,
        'currency_form': currency_form,
        'current_page': _('Currency'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/currency/admin.html', context)


@authenticated_staf
@staff_only
def AdminCurrencyDetails(request, slug):
    currency = Currency.objects.get(slug=slug)
    context = {
        'currency': currency,
        'current_page': _('Detail'),
        'prev_Page': _('Currency'),
        'prev_Page_link': reverse_lazy('core:AdminCurrencyListView')

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/currency/detail.html', context)


@authenticated_staf
@staff_only
def AdminCurrencyCreate(request):
    currencies = Currency.objects.all()
    if request.method == "POST":
        currency_form = AdminCurrencyForm(request.POST or None, request.FILES or None)
        if currency_form.is_valid():
            name = request.POST.get('name')
            name_ar = request.POST.get('name_ar')
            code = request.POST.get('code')
            symbol = request.POST.get('symbol')
            status = request.POST.get('status')
            currency_form = Currency(name=name, name_ar=name_ar, code=code, symbol=symbol, status=status)
            currency_form.save()
            messages.success(request, _("Currency Add Successfully"), extra_tags='Currency')
            return HttpResponseRedirect(reverse('core:AdminCurrencyListView'))
        else:
            messages.error(request, _("Currency Not Add , Please Try Again"), extra_tags='Currency')

    else:
        currency_form = AdminCurrencyForm()
        context = {
            'currencies': currencies,
            'currency_form': currency_form,
            'current_page': _('Create'),
            'prev_Page': _('Currency'),
            'prev_Page_link': reverse_lazy('core:AdminCurrencyListView')

        }
        return render(request, f'{BACKEND_TEMPLATES}/localization/currency/add.html', context)
    context = {
        'currencies': currencies,
        'currency_form': currency_form,
        'current_page': _('Create'),
        'prev_Page': _('Currency'),
        'prev_Page_link': reverse_lazy('core:AdminCurrencyListView')

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/currency/add.html', context)


@authenticated_staf
@staff_only
def AdminCurrencyUpdate(request, slug):
    currency = Currency.objects.get(slug=slug)
    if request.method == "POST":
        currency_form = AdminCurrencyForm(request.POST or None, request.FILES or None)
        if currency_form.is_valid():
            name = request.POST.get('name')
            name_ar = request.POST.get('name_ar')
            code = request.POST.get('code')
            symbol = request.POST.get('symbol')
            status = request.POST.get('status')
            currency_form = Currency.objects.get(slug=slug)
            currency_form.name = name
            currency_form.name_ar = name_ar
            currency_form.code = code
            currency_form.symbol = symbol
            currency_form.status = status
            currency_form.save()
            messages.success(request, _("Currency Update Successfully"), extra_tags='Currency')
            return HttpResponseRedirect(reverse('core:AdminCurrencyListView'))
        else:
            messages.error(request, _("Currency Not Update , Please Try Again"), extra_tags='Currency')

    else:
        currency_form = AdminCurrencyForm()
        context = {
            'currency': currency,
            'currency_form': currency_form,
            'current_page': _('Update'),
            'prev_Page': _('Currency'),
            'prev_Page_link': reverse_lazy('core:AdminCurrencyListView')

        }
        return render(request, f'{BACKEND_TEMPLATES}/localization/currency/update.html', context)
    context = {
        'currency': currency,
        'currency_form': currency_form,
        'current_page': _('Update'),
        'prev_Page': _('Currency'),
        'prev_Page_link': reverse_lazy('core:AdminCurrencyListView')

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/currency/update.html', context)


@authenticated_staf
@staff_only
def AdminCurrencyDelete(request, slug):
    if request.method == "POST":
        try:
            currency_object = Currency.objects.get(slug=slug)
            currency_object.delete()
            messages.success(request, "Currency Deleted Successfully", extra_tags='Currency')
            return HttpResponseRedirect(reverse('core:AdminCurrencyListView'))
        except Exception as e:
            print(e)
            messages.error(request, "Currency Not Deleted", extra_tags='Currency')
            return HttpResponseRedirect(reverse('core:AdminCurrencyListView'))


############Country############

@authenticated_staf
@staff_only
def AdminCountryList(request):
    countries = Country.objects.all()
    country_form = AdminCountryForm()
    if request.method == "POST":
        if country_form:
            name = request.POST.get('name')
            image = request.FILES.get('image')
            status = request.POST.get('status')
            country_object = Country(name=name, image=image, status=status)
            country_object.save()
            messages.success(request, "Country Add Successfully", extra_tags='Country')
            return HttpResponseRedirect(reverse('core:AdminCountryList'))
        else:
            messages.error(request, "Country Not Add", extra_tags='Country')

    context = {
        'countries': countries,
        'country_form': country_form,
        'current_page': _('Country'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/country/admin.html', context)


def AdminCountryDetails(request, slug):
    country = Country.objects.get(slug=slug)
    context = {
        'country': country,
        'current_page': _('Detail'),
        'prev_Page': _('Country'),
        'prev_Page_link': reverse_lazy('core:AdminCountryListView')

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/country/detail.html', context)


def AdminCountryUpdate(request, slug):
    country = Country.objects.get(slug=slug)
    if request.method == "POST":
        country_form = AdminCountryForm(request.POST or None, request.FILES or None)
        if country_form.is_valid():
            name = request.POST.get('name')
            image = request.FILES.get('image')
            status = request.POST.get('status')

            country_form = Country.objects.get(slug=slug)
            country_form.name = name
            if image:
                country_form.image = image
            else:
                country_form.image = country_form.image
            country_form.status = status
            country_form.save()
            messages.success(request, _("Country Update Successfully"), extra_tags='Country')
            return HttpResponseRedirect(reverse('core:AdminCountryList'))
        else:
            messages.error(request, _("Country Not Update , Please Try Again"), extra_tags='Country')

    else:
        country_form = AdminCountryForm()
        context = {
            'country': country,
            'country_form': country_form,
            'current_page': _('Update'),
            'prev_Page': _('Country'),
            'prev_Page_link': reverse_lazy('core:AdminCountryList')

        }
        return render(request, f'{BACKEND_TEMPLATES}/localization/country/update.html', context)
    context = {
        'country': country,
        'country_form': country_form,
        'current_page': _('Update'),
        'prev_Page': _('Country'),
        'prev_Page_link': reverse_lazy('core:AdminCountryList')

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/country/update.html', context)


@authenticated_staf
@staff_only
def AdminCountryDelete(request, slug):
    if request.method == "POST":
        try:
            country_object = Country.objects.get(slug=slug)
            country_object.delete()
            messages.success(request, "Country Deleted Successfully", extra_tags='Country')
            return HttpResponseRedirect(reverse('core:AdminCountryList'))
        except Exception as e:
            print(e)
            messages.error(request, "Country Not Deleted", extra_tags='Country')
            return HttpResponseRedirect(reverse('core:AdminCountryList'))


####################Governorates#################
@authenticated_staf
@staff_only
def AdminGovernoratesList(request, slug):
    country = Country.objects.get(slug=slug)
    governorates = Governorates.objects.filter(country=country)
    governorates_form = AdminGovernoratesForm()
    if request.method == "POST":
        if governorates_form:
            name = request.POST.get('name')
            status = request.POST.get('status')
            governorates_object = Governorates(country=country, name=name, status=status)
            governorates_object.save()
            messages.success(request, "Governorates Add Successfully", extra_tags='Governorates')
            return HttpResponseRedirect(reverse('core:AdminGovernoratesList', kwargs={"slug": country.slug}))
        else:
            messages.error(request, "Governorates Not Add", extra_tags='Governorates')

    context = {
        'country': country,
        'governorates': governorates,
        'governorates_form': governorates_form,
        'current_page': _('Governorates'),
        'prev_Page': _('Country'),
        'prev_Page_link': reverse_lazy('core:AdminCountryList', )

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/governorate/admin.html', context)


@authenticated_staf
@staff_only
def GovernoratesUpdate(request, slug, g_slug):
    country = Country.objects.get(slug=slug)
    governorates = Governorates.objects.get(slug=g_slug)
    if request.method == "POST":
        governorates_form = AdminGovernoratesForm(request.POST or None, request.FILES or None)
        name = request.POST.get('name')
        status = request.POST.get('status')

        if governorates_form:
            governorates_object = Governorates.objects.get(slug=g_slug)
            governorates_object.name = name
            governorates_object.status = status
            governorates_object.save()
            messages.success(request, "Governorates Update Successfully", extra_tags='Governorates')
            return HttpResponseRedirect(reverse('core:AdminGovernoratesList', kwargs={"slug": country.slug}))
        else:
            messages.error(request, "Governorates Update Not Update", extra_tags='Governorates')
    context = {
        'country': country,
        'governorates': governorates,
        'governorates_form': AdminGovernoratesForm(),
        'current_page': _('Update'),
        'prev_Page': _('Governorates'),
        'prev_Page_link': reverse_lazy('core:AdminGovernoratesList', kwargs={'slug': slug})
    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/governorate/update.html', context)


@authenticated_staf
@staff_only
def GovernoratesDelete(request, slug, g_slug):
    country = Country.objects.get(slug=slug)
    if request.method == "POST":
        try:
            country = Country.objects.get(slug=slug)
            governorates_object = Governorates.objects.get(slug=g_slug)
            governorates_object.delete()
            messages.success(request, "Governorates Deleted Successfully", extra_tags='Governorates')
            return HttpResponseRedirect(reverse('core:AdminGovernoratesList', kwargs={"slug": country.slug}))
        except:
            messages.error(request, "Error", extra_tags='Governorates')
            return HttpResponseRedirect(reverse('core:AdminGovernoratesList', kwargs={"slug": country.slug}))


##################     CIty    ##############


@authenticated_staf
@staff_only
def AdminCityList(request, slug):
    governorate = Governorates.objects.get(slug=slug)
    cities = City.objects.filter(governorates=governorate)
    city_form = AdminCityForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if city_form:
            name = request.POST.get('name')
            status = request.POST.get('status')
            city_object = City(governorates=governorate, name=name, status=status)
            city_object.save()
            messages.success(request, "City Add Successfully", extra_tags='City')
            return HttpResponseRedirect(reverse('core:AdminCityList', kwargs={"slug": governorate.slug}))
        else:
            messages.error(request, "City Not Add", extra_tags='City')

    context = {

        'governorate': governorate,
        'cities': cities,
        'city_form': city_form,
        'current_page': _('Cities'),
        'prev_Page': _('Governorates'),
        'prev_Page_link': reverse_lazy('core:AdminGovernoratesList', kwargs={'slug': slug})
    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/city/admin.html', context)


@authenticated_staf
@staff_only
def AdminCityUpdate(request, slug, c_slug):
    governorate = Governorates.objects.get(slug=slug)
    cities = City.objects.get(slug=c_slug)

    if request.method == "POST":

        governorate = Governorates.objects.get(slug=slug)
        city_form = AdminCityForm(request.POST or None, request.FILES or None)

        if city_form.is_valid():
            name = request.POST.get('name')
            if city_form:
                city_form = City.objects.get(slug=c_slug)
                city_form.name = name
                city_form.save()
                messages.success(request, "City Update Successfully", extra_tags='City')
                return HttpResponseRedirect(reverse('core:AdminCityList', kwargs={"slug": slug}))
        else:
            messages.error(request, "City Not Update", extra_tags='City')
    else:
        city_form = AdminCityForm()

        context = {
            'city': cities,
            'governorates': governorate,
            'city_form': city_form,
            'current_page': _('Update'),
            'prev_Page': _('Governorates'),
            'prev_Page_link': reverse_lazy('core:AdminCityList', kwargs={'slug': slug})

        }
        return render(request, f'{BACKEND_TEMPLATES}/localization/city/update.html', context)
    context = {
        'city': cities,
        'governorates': governorate,
        'city_form': city_form,
        'current_page': _('Update'),
        'prev_Page': _('Governorates'),
        'prev_Page_link': reverse_lazy('core:AdminCityList', kwargs={'slug': slug})

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/city/update.html', context)


@authenticated_staf
@staff_only
def AdminCityDelete(request, slug, c_slug):
    governorate = Governorates.objects.get(slug=slug)
    if request.method == "POST":
        try:
            city_object = City.objects.get(slug=c_slug)
            city_object.delete()
            messages.success(request, "City Deleted Successfully", extra_tags='City')
            return HttpResponseRedirect(reverse('core:AdminCityList', kwargs={"slug": governorate.slug}))
        except Exception as e:
            print(e)
            messages.error(request, "City Not Deleted", extra_tags='City')
            return HttpResponseRedirect(reverse('core:AdminCityList', kwargs={"slug": governorate.slug}))


##################Area##############
@authenticated_staf
@staff_only
def AdminAreaList(request, slug):
    city = City.objects.get(slug=slug)
    areas = Area.objects.filter(city=city)
    if request.method == "POST":

        area_form = AdminAreaForm(request.POST or None)
        translate_form = AdminCommonTranslateForm(request.POST or None)
        if area_form:
            name = request.POST.get('name')
            status = request.POST.get('status')
            area_object = Area(city=city, name=name, status=status)
            area_object.save()

            messages.success(request, _("City Add Successfully"), extra_tags='Area')

            return HttpResponseRedirect(reverse('core:AdminAreaList', kwargs={"slug": slug}))
        else:

            messages.error(request, _("Area Not Add"), extra_tags='Area')

    else:
        context = {
            'city': city,
            'areas': areas,
            'area_form': AdminAreaForm(),
            'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Area'),
            'prev_Page': _('City'),
            'prev_Page_link': reverse_lazy('core:AdminCityList', kwargs={'slug': slug})

        }
        return render(request, f'{BACKEND_TEMPLATES}/localization/area/admin.html', context)
    context = {
        'city': city,
        'areas': areas,
        'area_form': AdminAreaForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Area'),
        'prev_Page': _('City'),
        'prev_Page_link': reverse_lazy('core:AdminCityList', kwargs={'slug': slug})

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/area/admin.html', context)


@authenticated_staf
@staff_only
def AdminAreaUpdate(request, slug, a_slug):
    city = City.objects.get(slug=slug)
    area = Area.objects.get(slug=a_slug)
    if request.method == "POST":
        area_form = AdminAreaForm(request.POST or None, request.FILES or None)
        if area_form:

            name = request.POST.get('name')
            status = request.POST.get('status')

            area_object = Area.objects.get(slug=a_slug)
            area_object.city = city
            area_object.name = name
            area_object.status = status
            area_object.save()
            messages.success(request, "Area Updated Successfully", extra_tags='Area')
            return HttpResponseRedirect(reverse('core:AdminAreaList', kwargs={"slug": slug}))
        else:
            messages.error(request, "Area Not Updated , Please Try Again", extra_tags='Area')

    else:

        context = {
            'city': city,
            'area': area,
            'area_form': AdminAreaForm(),
            'current_page': _('Update'),
            'prev_Page': _('Area'),
            'prev_Page_link': reverse_lazy('core:AdminAreaList', kwargs={'slug': slug})
        }
        return render(request, f'{BACKEND_TEMPLATES}/localization/area/update.html', context)
    context = {
        'city': city,
        'area': area,
        'area_form': AdminAreaForm(),
        'current_page': _('Update'),
        'prev_Page': _('Area'),
        'prev_Page_link': reverse_lazy('core:AdminAreaList', kwargs={'slug': slug})
    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/area/update.html', context)


@authenticated_staf
@staff_only
def AdminAreaDelete(request, slug, a_slug):
    city = City.objects.get(slug=slug)
    if request.method == "POST":
        try:
            area_object = Area.objects.filter(slug=a_slug)
            area_object.delete()
            messages.success(request, "Area Deleted Successfully", extra_tags='Area')
            return HttpResponseRedirect(reverse('core:AdminAreaList', kwargs={"slug": city.slug}))
        except Exception as e:
            print(e)
            messages.error(request, "Area Not Deleted", extra_tags='Area')
            return HttpResponseRedirect(reverse('core:AdminAreaList', kwargs={"slug": city.slug}))
