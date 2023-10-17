
from django import forms


from core.models.shop import ShopCart, Order, OrderItem


class ShopCartForm(forms.ModelForm):
    class Meta:
        model = ShopCart
        fields = ['quantity',]


class CheckoutForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = [ 'payment_method' ]
        widgets = {
            'payment_method': forms.RadioSelect(attrs={'class': 'custom-select'}),
            'address': forms.RadioSelect(attrs={'class': 'custom-select'}),
        }


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'


class OrderProductForm(forms.ModelForm):

    class Meta:
        model = OrderItem
        fields = '__all__'


