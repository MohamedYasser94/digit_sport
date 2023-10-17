from django.forms import ModelForm


from core.models.localization import Country, Currency, Language, City, Governorates, Area


class AdminLanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = '__all__'


class AdminCurrencyForm(ModelForm):
    class Meta:
        model = Currency
        fields = '__all__'
        exclude = ['exchange']


class AdminCountryForm(ModelForm):
    class Meta:
        model = Country
        fields= '__all__'
        exclude = ['slug', ]


class AdminGovernoratesForm(ModelForm):
    class Meta:
        model = Governorates
        fields = '__all__'
        exclude = ['slug','country']


class AdminCityForm(ModelForm):
    class Meta:
        model = City
        exclude = ['slug','governorates']


class AdminAreaForm(ModelForm):
    class Meta:
        model = Area
        exclude = ['slug','city']
