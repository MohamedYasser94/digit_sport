from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
# Create your views here.
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from api.v1.serializers.localization import AdminLanguageSerializer
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import superuser_only, staff_only
from core.forms.localization import AdminCountryForm, AdminCurrencyForm, AdminLanguageForm, AdminCityForm, \
    AdminAreaForm, AdminGovernoratesForm
from core.models.localization import Country, Governorates, City, Area, Language, Currency



#############Languge##########

class LanguageListAPIView(ListView):
    model = Language
    template_name = BACKEND_TEMPLATES + 'localization/language_list.html'
    context_object_name = 'languages'
    paginate_by = 10

    @method_decorator(login_required)
    @method_decorator(staff_only)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Language.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Languages')
        return context


class LanguageAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Language.objects.all()
    serializer_class = AdminLanguageSerializer

