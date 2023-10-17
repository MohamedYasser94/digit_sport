from attr.filters import exclude
from django import forms
from django.contrib.auth import (
    authenticate,
    get_user_model
)

from django.utils.translation import gettext_lazy as _

from core.models.localization import City


User = get_user_model()


class UserUpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ['first_name', 'last_name', ]


class UserUpdateImageForm(forms.ModelForm):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ['image', ]



