from django import forms
from django.contrib.auth import get_user_model

from apps.sport.models import *

User = get_user_model()


class AdminMatchReportForm(forms.ModelForm):
    class Meta:
        model = MatchReport
        fields = '__all__'
        exclude = ('slug', 'code')

class AdminMatchPlayerReportForm(forms.ModelForm):
    class Meta:
        model = MatchPlayerReport
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminPlayerStaticsForm(forms.ModelForm):
    class Meta:
        model = PlayerStatics
        fields = '__all__'
        exclude = ('slug', 'code')