from django import forms
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import render
from requests import request
from slugify import slugify

from core.models.localization import Governorates, City
from core.models.vendor import Vendor
from user.forms.forms import UserSignUpForm

User = get_user_model()


class AdminCreateVendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = '__all__'
        exclude=['slug']

        def clean_title(self, title):
            email = slugify(title)
            if Vendor.objects.filter(email=email).exists():
                raise ValidationError('Vendor with this Email already exists.')

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['governorates'].queryset = Governorates.objects.none()
    #     self.fields['city'].queryset = City.objects.none()
    #
    #     if 'country' in self.data:
    #         try:
    #             country_id = int(self.data.get('country'))
    #             self.fields['governorates'].queryset = Governorates.objects.filter(country_id=country_id).order_by('title')
    #         except (ValueError, TypeError):
    #             pass  # invalid input from the people; ignore and fallback to empty City queryset
    #     elif self.instance.pk:
    #         self.fields['governorates'].queryset = self.instance.country.city_set.order_by('title')
    #     if 'governorates' in self.data:
    #         try:
    #             governorates_id = int(self.data.get('governorates'))
    #             self.fields['city'].queryset = City.objects.filter(governorates_id=governorates_id).order_by('title')
    #         except (ValueError, TypeError):
    #             pass  # invalid input from the people; ignore and fallback to empty City queryset
    #     elif self.instance.pk:
    #         self.fields['city'].queryset = self.instance.country.city_set.order_by('title')


class AlreadyUserSellerRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ['seller',]
        def save(self, commit=True):
            """
            Description:Save the provided password in hashed format.\n
            """
            user = super(AlreadyUserSellerRegisterForm, self).save(commit=False)
            user.seller = True
            user.active = True  # send confirmation email via signals
            if commit:
                user.save()
            return user
class AdminStoreAddFormm(forms.ModelForm):
    class Meta:
        model = Vendor

        fields = '__all__'


        # exclude=['vendor']

    # exclude = ('vendor',)  # ETA: added comma to make this a tuple
    def user(self):

        user = User.objects.filter(pk=id)
        if user is None:
            messages.error(
                request, 'Account is not active,please check your email')
            return render(request, 'users/dashboard/CustomerRegister.html', context={
                "title": "Register",
                "form": UserSignUpForm
            })
        else:
            def save(self, commit=True):
                obj = super(AdminStoreAddFormm, self).save(False)
                # obj.vendor = User.objects.filter(vendor=)
                commit and obj.save()
                return obj


class AdminVendorStoreEditForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = '__all__'

        exclude = ['status','activation','slug','email','category']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['governorates'].queryset = Governorates.objects.none()
        self.fields['city'].queryset = City.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['governorates'].queryset = Governorates.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the people; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['governorates'].queryset = self.instance.country.city_set.order_by('title')
        if 'governorates' in self.data:
            try:
                governorates_id = int(self.data.get('governorates'))
                self.fields['city'].queryset = City.objects.filter(governorates_id=governorates_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the people; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.country.city_set.order_by('title')
