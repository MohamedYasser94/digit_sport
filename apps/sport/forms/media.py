from django import forms

from apps.sport.models.media import *

User = get_user_model()


class YoutubeChannelForm(forms.ModelForm):
    class Meta:
        model = YoutubeChannel
        fields = '__all__'
        exclude = ('slug', 'code')


class YoutubeVideoForm(forms.ModelForm):
    class Meta:
        model = YoutubeVideo
        fields = '__all__'
        exclude = ('slug', 'code')


class MediaForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = '__all__'
        exclude = ('slug', 'code')

