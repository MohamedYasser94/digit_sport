from django import forms
from django.contrib.auth import (
    get_user_model
)
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _


from apps.wallet.models.models import WalletLocked, Wallet
from apps.wallet.models.transaction import BankTransactions, TreasuryTransactions, ExpensesTransactions

User = get_user_model()



class WalletLockedUserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = WalletLocked
        fields = '__all__'
        exclude=['user', 'user_nuc', 'slug', 'status']

class AddWalletPasswordForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = WalletLocked
        fields = '__all__'
        exclude=['user', 'user_nuc', 'slug']


class WalletUserForm(ModelForm):
    indirect_nuc = forms.CharField(required=False)
    class Meta:
        model = Wallet
        fields = '__all__'
        exclude=['user', 'indirect_nuc', 'slug', 'direct_parent', 'indirect_parent', ]


class WalletLoginForm(forms.Form):
    """
    Description:A form that will be used by user's to login.\n
    """
    wallet_code = forms.CharField(widget=forms.PasswordInput, label=_(u'wallet_code'))
    password = forms.CharField(widget=forms.PasswordInput, label=_(u'Password'))


    def clean(self, *args, **kwargs):
        wallet_code = self.cleaned_data.get("wallet_code")
        password = self.cleaned_data.get("password")

        if wallet_code and password:
            user = WalletLocked.objects.get(wallet_code=wallet_code,password=password,)

            if not user:
                raise forms.ValidationError("Incorrect Information  . Please Login Again")

            # if not user.check_password(password):
            #     raise forms.ValidationError("Incorrect Password")

            # if not user.status:
            #     raise forms.ValidationError("This user is not longer active.")

        return super(WalletLoginForm, self).clean(*args, **kwargs)


class AdminBankTransactionsForm(ModelForm):
    class Meta:
        model = BankTransactions
        fields = '__all__'
        exclude=[ 'slug', 'code','status']


class AdminTreasuryTransactionsForm(ModelForm):
    class Meta:
        model = TreasuryTransactions
        fields = '__all__'
        exclude=[ 'slug', 'code','status']



class AdminExpensesTransactionsForm(ModelForm):
    class Meta:
        model = ExpensesTransactions
        fields = '__all__'
        exclude=[ 'slug', 'code','status','wallet','amount']