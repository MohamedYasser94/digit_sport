from django import forms

from core.models.core import SystemSetting, SiteSetting, QrCode, CommonSeo, CommonMediaFiles, CommonTags, \
    CommonSocialLink, CommonProfile, CommonTranslate, HelpCategories, HelpQuestions


class AdminSiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = '__all__'
        exclude = ['code', 'slug']


class AdminSiteSettingUpdateForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = SiteSetting
        fields = '__all__'
        exclude = ['code', 'slug']


class SystemSettingForm(forms.ModelForm):
    class Meta:
        model = SystemSetting
        fields = '__all__'
        exclude = ['code', 'slug']


class AdminQrCodeForm(forms.ModelForm):
    class Meta:
        model = QrCode
        fields = '__all__'
        exclude = ['code', 'slug']


class AdminCommonSeoForm(forms.ModelForm):
    meta_author = forms.CharField(required=False)
    seo_image = forms.ImageField(required=False)

    class Meta:
        model = CommonSeo
        fields = '__all__'
        exclude = ['owner_model', 'owner_id', 'owner', 'meta_author', 'code', 'slug']


class AdminUpdateCommonSeoForm(forms.ModelForm):
    meta_author = forms.CharField(required=False)
    seo_image = forms.ImageField(required=False)

    class Meta:
        model = CommonSeo
        fields = '__all__'
        exclude = ['owner_model', 'owner_id', 'owner', 'meta_author', 'code', 'slug']


class AdminCommonMediaFilesForm(forms.ModelForm):
    class Meta:
        model = CommonMediaFiles
        fields = '__all__'
        exclude = ['owner_model', 'owner_id', 'owner', 'code', 'slug']


class AdminCommonTagsForm(forms.ModelForm):
    class Meta:
        model = CommonTags
        fields = '__all__'
        exclude = ['owner_model', 'owner_id', 'owner', 'code', 'slug']


class AdminCommonSocialLinkForm(forms.ModelForm):
    # url = forms.CharField(required=False)
    # provider = forms.CharField(required=False)

    class Meta:
        model = CommonSocialLink
        fields = '__all__'
        exclude = ['owner_model', 'owner_id', 'owner', 'code', 'slug']


class AdminCommonProfileForm(forms.ModelForm):
    # url = forms.CharField(required=False)
    # provider = forms.CharField(required=False)

    class Meta:
        model = CommonProfile
        fields = '__all__'
        exclude = ['owner_model', 'owner_id', 'owner', 'code', 'slug']


class AdminCommonTranslateForm(forms.ModelForm):
    # url = forms.CharField(required=False)
    # provider = forms.CharField(required=False)

    class Meta:
        model = CommonTranslate
        fields = '__all__'
        exclude = ['owner_model', 'owner_id', 'owner', 'code', 'slug']


class AdminHelpCategoriesForm(forms.ModelForm):
    class Meta:
        model = HelpCategories
        fields = '__all__'
        exclude = ['owner_model', 'owner_id', 'owner', 'code', 'slug']


class AdminHelpQuestionsForm(forms.ModelForm):
    class Meta:
        model = HelpQuestions
        fields = '__all__'
        exclude = ['code', 'slug']
