from django import forms

from apps.sport.models.monks import *

User = get_user_model()


class AdminMonkCountryForm(forms.ModelForm):
    class Meta:
        model = MonkCountry
        fields = '__all__'
        exclude = ('slug', 'code')


