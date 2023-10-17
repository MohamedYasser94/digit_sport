from django import forms

from core.models.billing import Purchase, PurchaseItem, Invoice, Billing
from core.models.people import Clients


class AdminPurchaseForm(forms.ModelForm):
    client = forms.ModelChoiceField(queryset=Clients.objects.filter(client_type='Supplier'), )

    class Meta:
        model = Purchase
        fields = '__all__'


class AdminPurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = '__all__'
        exclude=['purchase']


class AdminInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'


class AdminBillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = '__all__'
        exclude=['purchase']
