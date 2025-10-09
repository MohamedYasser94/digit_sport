
from django import forms
from django.contrib.auth import get_user_model

from core.models.blog import *

User = get_user_model()


class AdminBlogCategoriesForm(forms.ModelForm):
    category_id = forms.IntegerField(required=False)

    class Meta:
        model = BlogCategories
        fields = '__all__'


class AdminCommonTagsForm(forms.ModelForm):
    class Meta:
        model = CommonTags
        fields = '__all__'


class AdminBlogArticleTagsForm(forms.ModelForm):
    category_id = forms.IntegerField(required=False)

    class Meta:
        model = CommonTags
        fields = '__all__'
        exclude = ['tag_status']





class AdminBlogArticleForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(queryset=CommonTags.objects.filter(status='Active'))
    category = forms.ModelChoiceField(queryset=BlogCategories.objects.filter(status='Active'))
    team = forms.ModelChoiceField(queryset=Teams.objects.filter(status='Active'), required=False)
    
    class Meta:
        model = BlogArticle
        fields = '__all__'
        exclude = ['slug', 'views', 'author', 'article_type']

    # def __init__(self, *args, **kwargs):
    #     super(AdminBlogArticleForm, self).__init__(*args, **kwargs)
    #
    #     # Get the inital values set in the view
    #     inital = kwargs.get('initial')
    #
    #     # Override the product query set with a list of product excluding those already in the pricelist
    #     self.fields['tags'].queryset = BlogTags.objects.exclude(status='Active')



class AdminBlogVideoForm(forms.ModelForm):
    category_id = forms.IntegerField(required=False)


    class Meta:
        model = BlogVideo
        fields = '__all__'