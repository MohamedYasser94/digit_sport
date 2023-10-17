from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.crypto import get_random_string
from slugify import slugify

from apps.wallet.models.models import Wallet, SystemWallet
from helper.modelHelper import Transaction_Money_Type, Transaction_Money_Status, Transaction_Money_Category, \
    Transaction_Money_Mode, Transaction_Operation, Active_Status, Approved_Status, Approved_Need

User = get_user_model()
class MoneyTransaction(models.Model):
    sender_model = models.ForeignKey(ContentType,related_name='money_sender', on_delete=models.CASCADE, null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType,related_name='money_receiver', on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='money_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    transaction_type = models.CharField(choices=Transaction_Money_Type, max_length=255)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    month = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TRA-MONEY{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(MoneyTransaction, self).save(*args, **kwargs)
class BankTransactions(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, null=True, blank=True)
    system_wallet = models.ForeignKey(SystemWallet, on_delete=models.PROTECT , null=True, blank=True)
    sender_model = models.ForeignKey(ContentType, related_name='bank_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='bank_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='bank_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    auditor_model = models.ForeignKey(ContentType, related_name='bank_auditor', on_delete=models.PROTECT,
                                      null=True,
                                      blank=True)
    auditor_id = models.PositiveIntegerField(null=True, blank=True)
    auditor = GenericForeignKey('auditor_model', 'auditor_id')
    transaction_type = models.CharField(choices=Transaction_Money_Type, null=True, blank=True, max_length=50)
    transaction_mode = models.CharField(choices=Transaction_Money_Mode, null=True, blank=True, max_length=50)
    transaction_status = models.CharField(choices=Transaction_Money_Status, null=True, blank=True, max_length=50)
    transaction_category = models.CharField(choices=Transaction_Money_Category, null=True, blank=True, max_length=50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    receive = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    send = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    note = models.TextField(null=True, blank=True)
    month = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True, )
    status = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'wallet_user'
        # verbose_name_plural = 'categories'

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'BankTransactions-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(BankTransactions, self).save(*args, **kwargs)


class TreasuryTransactions(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, null=True, blank=True)
    system_wallet = models.ForeignKey(SystemWallet, on_delete=models.PROTECT , null=True, blank=True)
    sender_model = models.ForeignKey(ContentType, related_name='treasury_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='treasury_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='treasury_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    auditor_model = models.ForeignKey(ContentType, related_name='treasury_auditor', on_delete=models.PROTECT,
                                      null=True,
                                      blank=True)
    auditor_id = models.PositiveIntegerField(null=True, blank=True)
    auditor = GenericForeignKey('auditor_model', 'auditor_id')
    transaction_type = models.CharField(choices=Transaction_Money_Type, null=True, blank=True, max_length=50)
    transaction_mode = models.CharField(choices=Transaction_Money_Mode, null=True, blank=True, max_length=50)
    transaction_status = models.CharField(choices=Transaction_Money_Status, null=True, blank=True, max_length=50)
    transaction_category = models.CharField(choices=Transaction_Money_Category, null=True, blank=True, max_length=50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    receive = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    send = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    note = models.TextField(null=True, blank=True)
    month = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True, )
    status = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'wallet_user'
        # verbose_name_plural = 'categories'

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TreasuryTransactions-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(TreasuryTransactions, self).save(*args, **kwargs)


class ExpensesTransactions(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, null=True, blank=True)
    system_wallet = models.ForeignKey(SystemWallet, on_delete=models.PROTECT , null=True, blank=True)

    sender_model = models.ForeignKey(ContentType, related_name='expenses_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='expenses_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='expenses_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    auditor_model = models.ForeignKey(ContentType, related_name='expenses_auditor', on_delete=models.PROTECT,
                                      null=True,
                                      blank=True)
    auditor_id = models.PositiveIntegerField(null=True, blank=True)
    auditor = GenericForeignKey('auditor_model', 'auditor_id')
    transaction_type = models.CharField(choices=Transaction_Money_Type, null=True, blank=True, max_length=50)
    transaction_mode = models.CharField(choices=Transaction_Money_Mode, null=True, blank=True, max_length=50)
    transaction_status = models.CharField(choices=Transaction_Money_Status, null=True, blank=True, max_length=50)
    transaction_category = models.CharField(choices=Transaction_Money_Category, null=True, blank=True, max_length=50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    receive = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    send = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    note = models.TextField(null=True, blank=True)
    month = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True, )
    status = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'wallet_user'
        # verbose_name_plural = 'categories'

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'ExpensesTransactions-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ExpensesTransactions, self).save(*args, **kwargs)


class AppTransactions(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, null=True, blank=True)
    system_wallet = models.ForeignKey(SystemWallet, on_delete=models.PROTECT , null=True, blank=True)

    sender_model = models.ForeignKey(ContentType, related_name='app_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='app_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='app_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    auditor_model = models.ForeignKey(ContentType, related_name='app_auditor', on_delete=models.PROTECT,
                                      null=True,
                                      blank=True)
    auditor_id = models.PositiveIntegerField(null=True, blank=True)
    auditor = GenericForeignKey('auditor_model', 'auditor_id')
    transaction_type = models.CharField(choices=Transaction_Money_Type, null=True, blank=True, max_length=50)
    transaction_mode = models.CharField(choices=Transaction_Money_Mode, null=True, blank=True, max_length=50)
    transaction_status = models.CharField(choices=Transaction_Money_Status, null=True, blank=True, max_length=50)
    transaction_category = models.CharField(choices=Transaction_Money_Category, null=True, blank=True, max_length=50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    receive = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    send = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    note = models.TextField(null=True, blank=True)
    month = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True, )
    status = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'AppTransactions-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(AppTransactions, self).save(*args, **kwargs)


class OperationTransaction(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='operation_sender', on_delete=models.CASCADE,
                                     null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='operation_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='operation_owner', on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    transaction_type = models.CharField(max_length=50, choices=Transaction_Operation, null=False, blank=False, default='Cost')
    reason = models.CharField(max_length=150, null=False, blank=False)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    cost = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    due = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    paid = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    last_amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    ended_amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True, )
    due_date = models.DateField(null=True, blank=True, )
    month = models.CharField(max_length=50, null=True, blank=True)
    year = models.CharField(max_length=50, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    status = models.CharField(max_length=20, choices=Active_Status, null=True,blank=True, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction_type

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TRA-OPERATION{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(OperationTransaction, self).save(*args, **kwargs)



class OperationTransactionHistory(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='operationtransactionhistory_sender', on_delete=models.CASCADE,
                                     null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='operationtransactionhistory_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='operationtransactionhistory_owner', on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    reservation_model = models.ForeignKey(ContentType, related_name='operationtransactionhistory_reservation', on_delete=models.SET_NULL,
                                            null=True,
                                            blank=True)
    reservation_id = models.PositiveIntegerField(null=True, blank=True)
    reservation = GenericForeignKey('reservation_model', 'reservation_id')
    project_model = models.ForeignKey(ContentType, related_name='operationtransactionhistory_project', on_delete=models.SET_NULL,
                                            null=True,
                                            blank=True)
    project_id = models.PositiveIntegerField(null=True, blank=True)
    project = GenericForeignKey('project_model', 'project_id')
    transaction_type = models.CharField(max_length=50, choices=Transaction_Operation, null=False, blank=False, default='Coast')
    reason = models.CharField(max_length=150, null=False, blank=False)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    cost = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    due = models.DecimalField(max_digits=65, decimal_places=2, default=0,null=True, blank=True)
    paid = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    last_amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True, )
    due_date = models.DateField(null=True, blank=True, )
    month = models.CharField(max_length=50, null=True, blank=True)
    year = models.CharField(max_length=50, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, blank=True, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction_type

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TRA-History{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(OperationTransactionHistory, self).save(*args, **kwargs)




class PartnerPercentage(models.Model):
    partner = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    percent = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    approved_count = models.IntegerField(default=0, null=True, blank=True)
    approved_status = models.CharField(choices=Approved_Status, null=True, blank=True, max_length=50, default='Pending')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True, )
    status = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'percent_user'
        # verbose_name_plural = 'categories'

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'PartnerPercentage-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(PartnerPercentage, self).save(*args, **kwargs)

class PercentageTransactions(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, null=True, blank=True)
    system_wallet = models.ForeignKey(SystemWallet, on_delete=models.PROTECT , null=True, blank=True)
    percent_type = models.ForeignKey(PartnerPercentage, on_delete=models.PROTECT)
    sender_model = models.ForeignKey(ContentType, related_name='percentage_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='percentage_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='percentage_owner', on_delete=models.SET_NULL, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    auditor_model = models.ForeignKey(ContentType, related_name='percentage_auditor', on_delete=models.PROTECT,
                                      null=True,
                                      blank=True)
    auditor_id = models.PositiveIntegerField(null=True, blank=True)
    auditor = GenericForeignKey('auditor_model', 'auditor_id')
    transaction_type = models.CharField(choices=Transaction_Money_Type, null=True, blank=True, max_length=50)
    transaction_mode = models.CharField(choices=Transaction_Money_Mode, null=True, blank=True, max_length=50)
    transaction_status = models.CharField(choices=Transaction_Money_Status, null=True, blank=True, max_length=50)
    transaction_category = models.CharField(choices=Transaction_Money_Category, null=True, blank=True, max_length=50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    percent = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    receive = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    send = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    note = models.TextField(null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True, )
    status = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'percent_user'
        # verbose_name_plural = 'categories'

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'PercentageTransactions-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(PercentageTransactions, self).save(*args, **kwargs)
class ActionNeedApproved(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='ana_sender', on_delete=models.CASCADE,
                                     null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='ana_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    approved_model = models.ForeignKey(ContentType, related_name='ana_approved', on_delete=models.CASCADE, null=True,
                                       blank=True)
    approved_id = models.PositiveIntegerField(null=True, blank=True)
    approved = GenericForeignKey('approved_model', 'approved_id')
    approved_status = models.CharField(choices=Approved_Status, null=True, blank=True, max_length=50, default='Pending')
    approved_need = models.CharField(choices=Approved_Need, null=True, blank=True, max_length=50)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'ANA{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ActionNeedApproved, self).save(*args, **kwargs)


class OperationTransactionAccounts(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='operation_accounts_sender', on_delete=models.CASCADE,
                                     null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='operation_accounts_receiver',
                                       on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    recipient_model = models.ForeignKey(ContentType, related_name='operation_accounts_recipient',
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        blank=True)
    recipient_id = models.PositiveIntegerField(null=True, blank=True)
    recipient = GenericForeignKey('owner_model', 'owner_id')
    owner_model = models.ForeignKey(ContentType, related_name='operation_accounts_owner', on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    partners = models.ManyToManyField(PartnerPercentage, related_name='operation_accounts_partners', blank=True)
    auditor = models.ForeignKey(User, related_name='car_operation_auditor', on_delete=models.PROTECT, null=True,
                                blank=True)
    accountant = models.ForeignKey(User, related_name='car_operation_accountant', on_delete=models.PROTECT, null=True,
                                   blank=True)
    treasurer = models.ForeignKey(User, related_name='car_operation_treasurer', on_delete=models.PROTECT, null=True,
                                  blank=True)
    storekeeper = models.ForeignKey(User, related_name='car_operation_storekeeper', on_delete=models.PROTECT, null=True,
                                    blank=True)
    approved_count = models.IntegerField(default=0, null=True, blank=True)
    approved_status = models.CharField(choices=Approved_Status, null=True, blank=True, max_length=50, default='Pending')

    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TRA-OTA{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(OperationTransactionAccounts, self).save(*args, **kwargs)
