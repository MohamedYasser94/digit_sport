from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework.reverse import reverse_lazy
from slugify import slugify

from helper.modelHelper import Client_Type, Active_Status, Email_Validator, \
    Driver_Garage_Status, Transaction_Money_Type, Duration_Type, Employee_Overtime_Type, Company_Type, Employee_Role, \
    Country_List, Governorates_List, Waiting_Status
from helper.viewHelper import get_file_path

User = get_user_model()


class Clients(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='client_sender', on_delete=models.CASCADE, null=True,
                                        blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='client_receiver', on_delete=models.CASCADE, null=True,
                                            blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='client_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    first_name = models.CharField(max_length=50, blank=False, null=False)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    title = models.CharField(max_length=50, blank=True, null=True)
    job_title = models.TextField( blank=True, null=True)
    company = models.CharField(max_length=50, blank=True, null=True)
    national_id = models.CharField(max_length=50, blank=True, null=True,default=0)
    email = models.EmailField(max_length=50, null=True, blank=True, unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True,unique=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    governorates = models.CharField(max_length=100, choices=Governorates_List, default='Cairo', null=True, blank=True)
    client_type = models.CharField(max_length=60, choices=Client_Type, null=True, default='Client')
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    national_image = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    data_confirmed = models.CharField(max_length=60, choices=Waiting_Status, null=True, blank=True, default='Waiting')
    status = models.CharField(max_length=60, choices=Active_Status, null=True, blank=True, default='Active')
    code = models.CharField(unique=True, max_length=20, )
    slug = models.SlugField(null=True, blank=True, max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = None
        if self.first_name or self.last_name:
            return f'{self.first_name} {self.middle_name}'
        else:
            return self.email
    def get_absolute_url(self):
        return reverse('core:AdminClientDetails', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Clients-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(self.code)
        super(Clients, self).save(*args, **kwargs)


class Employee(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='employee_sender', on_delete=models.CASCADE, null=True,
                                        blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='employee_receiver', on_delete=models.CASCADE, null=True,
                                            blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='employee_owner', on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')

    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=50, blank=True, null=True)
    company_type = models.CharField(max_length=60, choices=Company_Type, null=True,blank=True, default='Other')
    national_id = models.CharField(max_length=50,unique=True, blank=True, null=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=60, choices=Employee_Role, null=True, default='Receptionist')
    body = models.TextField()
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    governorates = models.CharField(max_length=100, choices=Governorates_List, default='Cairo', null=True, blank=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    start_day = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=60, choices=Active_Status, null=True, default='Active')
    code = models.CharField(unique=True, max_length=20, )
    slug = models.SlugField(null=True, blank=True, max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name
    def get_absolute_url(self):
        return reverse('core:AdminEmployeeDetails', kwargs={'slug': self.slug})

    def get_full_name(self):
        full_name = None
        if self.first_name or self.last_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return self.email


    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Employee-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(self.code)
        super(Employee, self).save(*args, **kwargs)



class Branch(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=50, blank=True, null=True)
    company_type = models.CharField(max_length=60, choices=Company_Type, null=True, default='Other')
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    governorates = models.CharField(max_length=100, choices=Governorates_List, default='Cairo', null=True, blank=True)
    status = models.CharField(max_length=60, choices=Active_Status, null=True, default='Active')
    code = models.CharField(unique=True, max_length=20, )
    slug = models.SlugField(null=True, blank=True, max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('core:AdminBranchDetails', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Branch-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(self.code)
        super(Branch, self).save(*args, **kwargs)

class Driver(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='driver_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='driver_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='driver_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=50, validators=[UnicodeUsernameValidator], null=False, blank=False)
    email = models.EmailField(max_length=50, validators=[Email_Validator], null=True, blank=True)
    phone = models.CharField(max_length=50, validators=[UnicodeUsernameValidator], null=False, blank=False)
    nationality = models.CharField(max_length=50, validators=[UnicodeUsernameValidator], null=True, blank=True,
                                   default='Egyptian')
    national_id = models.CharField(max_length=20, blank=True, null=True)
    national_start = models.DateField(null=True, blank=True)
    national_end = models.DateField(null=True, blank=True)
    electronic_number = models.CharField(max_length=50, validators=[UnicodeUsernameValidator], null=True, blank=True)
    traffic_management = models.CharField(max_length=50, validators=[UnicodeUsernameValidator], null=True, blank=True)
    license_number = models.CharField(max_length=50, validators=[UnicodeUsernameValidator], null=False, blank=False,
                                      unique=True)
    license_start = models.DateField(null=True, blank=True)
    license_end = models.DateField(null=True, blank=True)
    garage_status = models.CharField(max_length=50, choices=Driver_Garage_Status, null=True, blank=True,
                                     default='In Service')
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    governorates = models.CharField(max_length=100, choices=Governorates_List, default='Cairo', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:AdminDriverDetails', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'DRIVER-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Driver, self).save(*args, **kwargs)


class EmployeeSalary(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='salary_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='salary_receiver', on_delete=models.CASCADE, null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    auditor_model = models.ForeignKey(ContentType, related_name='salary_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    auditor_id = models.PositiveIntegerField(null=True, blank=True)
    auditor = GenericForeignKey('auditor_model', 'auditor_id')

    transaction_type = models.CharField(choices=Transaction_Money_Type, null=True, blank=True, max_length=50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    duration = models.CharField(choices=Duration_Type, max_length=50, default='Months', null=True, blank=True, )
    duration_count = models.IntegerField(default=0, null=True, blank=True, )
    hour_count = models.IntegerField(default=0, null=True, blank=True, )
    hour_cost = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, null=True, blank=True, )
    daily_cost = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, null=True, blank=True, )
    monthly_cost = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, null=True, blank=True, )
    friday_cost = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, null=True, blank=True, )
    discount = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, null=True, blank=True, )
    overtime_type = models.CharField(choices=Employee_Overtime_Type, max_length=50, default='Hour', null=True, blank=True, )
    cost = models.DecimalField(max_digits=65, decimal_places=2, default=0, null=True, blank=True, )
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
    def get_absolute_url(self):
        return reverse('core:AdminEmployeeSalaryDetails', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'EmployeeSalary-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(EmployeeSalary, self).save(*args, **kwargs)


class EmployeeMonthlyTimesheet(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='employeemonthlytimesheet_sender', on_delete=models.CASCADE,
                                     null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='employeemonthlytimesheet_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='employeemonthlytimesheet_owner', on_delete=models.PROTECT, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    auditor_model = models.ForeignKey(ContentType, related_name='employeemonthlytimesheet_auditor', on_delete=models.PROTECT,
                                      null=True,
                                      blank=True)
    auditor_id = models.PositiveIntegerField(null=True, blank=True)
    auditor = GenericForeignKey('auditor_model', 'auditor_id')
    employee_model = models.ForeignKey(ContentType, related_name='employeemonthlytimesheet_employee',
                                      on_delete=models.PROTECT,
                                      null=True,
                                      blank=True)
    employee_id = models.PositiveIntegerField(null=True, blank=True)
    employee = GenericForeignKey('employee_model', 'employee_id')
    salary= models.DecimalField(max_digits=65, decimal_places=2, default=0.00, null=True, blank=True, )
    day = models.PositiveIntegerField(null=True, blank=True)
    operating_hours = models.PositiveIntegerField(null=True, blank=True)
    friday = models.PositiveIntegerField(null=True, blank=True)
    discount = models.PositiveIntegerField(null=True, blank=True)
    overtime = models.PositiveIntegerField(null=True, blank=True)
    total = models.DecimalField(max_digits=65, decimal_places=2, default=0.00, null=True, blank=True, )
    month = models.CharField(max_length=50,  null=True, blank=True)
    year = models.CharField(max_length=50, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
    def get_absolute_url(self):
        return reverse('core:AdminEmployeeSalaryDetails', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MonthlyTimesheet-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(EmployeeMonthlyTimesheet, self).save(*args, **kwargs)


class Contract(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='contract_sender', on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='contract_receiver', on_delete=models.SET_NULL,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='contract_owner', on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    title = models.CharField(max_length=255, unique=True, null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    code = models.CharField(max_length=200, blank=False, null=False, unique=True, )
    status = models.CharField(max_length=60, choices=Active_Status, null=True,blank=True, default='Active')
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'contract'
        # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['code']

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'CON-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Contract, self).save(*args, **kwargs)


class ContractTerms(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='terms_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='terms_receiver', on_delete=models.CASCADE, null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='terms_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    contract = models.ForeignKey(Contract, related_name='contract', on_delete=models.PROTECT)
    order_term = models.IntegerField(default=1)
    terms = models.CharField(max_length=200, )
    terms_details = models.TextField(null=True)
    code = models.CharField(max_length=200, blank=False, null=False, unique=True, )
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order_term',)
        verbose_name = 'contract_term'
        # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['order_term']

    def __str__(self):
        return self.contract

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'CON-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ContractTerms, self).save(*args, **kwargs)


class Team(models.Model):
    owner_model = models.ForeignKey(ContentType, related_name='team_owner', on_delete=models.SET_NULL, null=True,blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=False)
    keyword = models.CharField(max_length=100, blank=True, null=True)
    body = models.TextField(blank=True, null=False)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    job_title = models.CharField(max_length=255, blank=False, null=False)
    skill_level = models.CharField(max_length=255, blank=False, null=False)
    email = models.EmailField(max_length=255, blank=False, null=False)
    phone = models.CharField(max_length=255, blank=False, null=False)
    section = models.CharField(max_length=255, blank=False, null=False)
    experience = models.CharField(max_length=255, blank=False, null=False)
    featured = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    governorates = models.CharField(max_length=100, choices=Governorates_List, default='Cairo', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse_lazy('home:FrontArticleCategoryDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'Team-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Team, self).save(*args, **kwargs)

class TeamSkill(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_skill')
    skill = models.CharField(max_length=255, blank=True, null=True)
    percentage = models.PositiveIntegerField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    status = models.CharField(max_length=20, choices=Active_Status)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.skill

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TeamSkill-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(TeamSkill, self).save(*args, **kwargs)






