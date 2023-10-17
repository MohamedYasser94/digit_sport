from django import forms

from core.models.front import Banners, Slider, Testimonials


class AdminTestimonialsForm(forms.ModelForm):
    class Meta:
        model = Testimonials
        fields = '__all__'
        exclude = ['code', 'slug']


class SliderAddForm(forms.ModelForm):
    class Meta:
        model = Slider
        fields = '__all__'


class BannersAddForm(forms.ModelForm):
    class Meta:
        model = Banners
        fields = '__all__'
        widgets = {
            'position': forms.Select(attrs={'class': 'custom-select'}),

        }
