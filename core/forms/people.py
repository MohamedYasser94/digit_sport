from django import forms

from core.models.people import Clients, Driver, Contract, Employee, EmployeeSalary, EmployeeMonthlyTimesheet, Team, \
    TeamSkill, Branch


class AdminClientsForm(forms.ModelForm):

    class Meta:
        model = Clients
        fields = '__all__'
        exclude=['slug','code']


class AdminDriverForm(forms.ModelForm):

    class Meta:
        model = Driver
        fields = '__all__'
        exclude=['slug','code']


class AdminEmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = '__all__'
        exclude=['slug','code']


class AdminBranchForm(forms.ModelForm):

    class Meta:
        model = Branch
        fields = '__all__'
        exclude=['slug','code']

class AdminEmployeeSalaryrForm(forms.ModelForm):

    class Meta:
        model = EmployeeSalary
        fields = '__all__'
        exclude=['slug','code']
class AdminEmployeeMonthlyTimesheetForm(forms.ModelForm):

    class Meta:
        model = EmployeeMonthlyTimesheet
        fields = '__all__'
        exclude=['slug','code']

class AdminContractForm(forms.ModelForm):

    class Meta:
        model = Contract
        fields = '__all__'
        exclude=['slug','code']



class AdminTeamForm(forms.ModelForm):

    class Meta:
        model = Team
        fields = '__all__'
        exclude=['slug','code']


class AdminTeamSkillForm(forms.ModelForm):

    class Meta:
        model = TeamSkill
        fields = '__all__'
        exclude=['slug','code']