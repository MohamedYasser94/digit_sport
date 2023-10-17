
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.catalog.models.models import Categories, Products, Variants, ProductVariants, ProductReviews, Manufacturer, \
    UnitConversion
from apps.catalog.models.vendor import Warehouse

User = get_user_model()


class AdminCatalogCategoryForm(forms.ModelForm):

    class Meta:
        model = Categories
        fields = '__all__'



class AdminCatalogProductForm(forms.ModelForm):



    # product_id = forms.IntegerField(required=False)

    # category = forms.ModelChoiceField(queryset=Categories.objects.all(), label=u"Category", )
    # filter = forms.ModelChoiceField(queryset=Filters.objects.all(), label=u"Filter", required=False,
    #                                 widget=ModelSelect2Widget(
    #                                     search_fields=['title'], dependent_fields={'filters': 'filters'}))
    #
    # manufacturer = forms.ModelChoiceField(queryset=Manufacturer.objects.all(), required=False, label=u"manufacturer",
    #                                       widget=ModelSelect2Widget(
    #                                           search_fields=['title', 'image'],
    #                                           dependent_fields={'manufacturer': 'manufacturer'}))
    #
    # related = forms.ModelChoiceField(queryset=Products.objects.all(), required=False, label=u"related",
    #                                  widget=ModelSelect2Widget(
    #                                      search_fields=['title', 'image'],
    #                                      dependent_fields={'product_related': 'product_related', 'image': 'image'}))

    class Meta:
        model = Products
        fields = '__all__'
        exclude=['seller','variant','final_price']
        widgets = {'title': forms.TextInput(attrs={'class': 'form-control'}),
                   'keywords': forms.TextInput(attrs={'class': 'form-control'}),
                   'category': forms.Select(attrs={'class': 'custom-select'}),
                   'final_price': forms.Select(attrs={'class': 'custom-select'}),
                   'subtract_stock': forms.Select(attrs={'class': 'custom-select'}),
                   'out_of_stock_status': forms.Select(attrs={'class': 'custom-select'}),
                   'slug': forms.TextInput(attrs={'class': 'form-control'}),
                   # 'price': forms.NumberInput(attrs={'class': 'form-control'}),




                   }








class AdminCatalogVariantsForm(forms.ModelForm):


    class Meta:
        model = Variants
        fields = '__all__'


class AdminCatalogUnitConversionForm(forms.ModelForm):


    class Meta:
        model = UnitConversion
        fields = '__all__'
        exclude = ['code','slug']

class AdminCatalogProductVariantsForm(forms.ModelForm):

    #
    # variant_detail = forms.CharField(required=False)
    # variant_price = forms.CharField(required=False)
    # variant_quantity = forms.CharField(required=False)
    # variant_image = forms.CharField(required=False)

    class Meta:
        model = ProductVariants
        fields = '__all__'
        exclude = ['product']





class AdminCatalogProductReviewsForm(forms.ModelForm):
    class Meta:
        model = ProductReviews
        fields = ['review', 'rating', 'review_image']


class AdminCatalogManufacturerForm(forms.ModelForm):
    title = forms.CharField(label=_(u'title'))
    class Meta:
        model = Manufacturer
        fields = ['title','image','status']



class AdminCatalogWarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = '__all__'
        exclude = ['vendor']



