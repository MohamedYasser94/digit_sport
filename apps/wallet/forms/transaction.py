from django import forms
from django.contrib.auth import get_user_model

from apps.medical.models.models import CarTimesheet
from apps.medical.models.transaction import CarCost, CarMoneyTransaction, CarOperationTransaction, Overtime
from apps.wallet.models.transaction import OperationTransaction

User = get_user_model()


class AdminCarCostForm(forms.ModelForm):

    class Meta:
        model = CarCost
        fields = '__all__'
        exclude = ('slug', 'code')



class AdminCarMoneyTransactionForm(forms.ModelForm):

    class Meta:
        model = CarMoneyTransaction
        fields = '__all__'
        exclude = ('slug', 'code')

class AdminCarOperationTransactionForm(forms.ModelForm):

    class Meta:
        model = CarOperationTransaction
        fields = '__all__'
        exclude = ('slug', 'code','due')


class AdminOvertimeForm(forms.ModelForm):

    class Meta:
        model = Overtime
        fields = '__all__'
        exclude = ('slug', 'code',)




class AdminCarTimesheetForm(forms.ModelForm):

    class Meta:
        model = CarTimesheet
        fields = '__all__'
        exclude = ('slug', 'code','car')


class AdminOperationTransactionForm(forms.ModelForm):

    class Meta:
        model = OperationTransaction
        fields = '__all__'
        exclude = ('slug', 'code')