from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from slugify import slugify

from helper.modelHelper import WALLET_STATUS, Current_App, Access_Level, Transaction_Money_Category

User = get_user_model()
UserModel = get_user_model()


class WalletLocked(models.Model):
    user = models.OneToOneField(User, related_name='wallet_locked_user', on_delete=models.PROTECT)
    user_nuc = models.CharField(max_length=200, blank=False, null=False)
    wallet_code = models.CharField(max_length=200, blank=False, null=False, default='None')
    password = models.CharField(max_length=200, blank=False, null=False, default='None')
    status = models.CharField(max_length=20, choices=WALLET_STATUS, default='Create', null=True, blank=True)
    first_login = models.BooleanField(default=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'network_user'
        # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['user']

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'LOCKED-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(WalletLocked, self).save(*args, **kwargs)
class WalletResetPassword(models.Model):
    wallet_locked = models.OneToOneField(WalletLocked, related_name='wallet_reset', on_delete=models.PROTECT)
    user = models.OneToOneField(User, related_name='reset_user', on_delete=models.PROTECT, null=True, blank=True)
    owner_model = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    reset_code = models.CharField(max_length=200, blank=False, null=False, default='None')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(max_length=128, unique=True, null=True, blank=True, )
    status = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'WALLET-ResetPassword-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(WalletResetPassword, self).save(*args, **kwargs)

#
class Wallet(models.Model):
    wallet_locked = models.OneToOneField(WalletLocked, related_name='wallet_locked', on_delete=models.PROTECT)
    user = models.OneToOneField(User, related_name='wallet_user', on_delete=models.PROTECT, null=True, blank=True)
    owner_model = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    user_nuc = models.CharField(max_length=200, blank=True, null=True)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    mode = models.CharField(max_length=20, choices=Access_Level, default='User', null=True, blank=True)
    app = models.CharField(max_length=20, choices=Current_App, default='Digithup', null=True, blank=True)
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
    def get_absolute_url(self):
        return reverse_lazy('wallet:AdminUserWalletLocked')

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'WALLET-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Wallet, self).save(*args, **kwargs)

class WalletMoney(models.Model):
    wallet = models.OneToOneField(Wallet, on_delete=models.PROTECT)
    user = models.OneToOneField(User, on_delete=models.PROTECT , null=True, blank=True)
    owner_model = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    transaction_category = models.CharField(choices=Transaction_Money_Category, null=True, blank=True, max_length=50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    earning = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    paid = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    due = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    receive = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    send = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
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
            code = f'WalletMoney-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(WalletMoney, self).save(*args, **kwargs)
class SystemWallet(models.Model):
    wallet_locked = models.OneToOneField(WalletLocked, related_name='systemwallet_locked', on_delete=models.PROTECT,null=True, blank=True)
    user = models.OneToOneField(User, related_name='systemwallet_user', on_delete=models.PROTECT, null=True, blank=True)
    owner_model = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    secret= models.CharField(max_length=200, blank=True, null=True, default='SystemWallet' ,unique=True,editable=False)
    user_nuc = models.CharField(max_length=200, blank=True, null=True)
    transaction_category = models.CharField(choices=Transaction_Money_Category, null=True, blank=True, max_length=50)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)  # 100.00
    earning = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    profit = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)  # 100.00
    paid = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    due = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    receive = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    send = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    bank = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)   # 100.00
    treasury = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    custody = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    projects = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    projects_actual = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    projects_earning = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    projects_paid = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    projects_due = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    stores = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    stores_actual = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    actual = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True) 
    expenses = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    car_expenses = models.DecimalField(max_digits=50, decimal_places=2, default=0, null=True, blank=True)
    month = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=255, null=True, blank=True)
    mode = models.CharField(max_length=20, choices=Access_Level, default='User', null=True, blank=True)
    app = models.CharField(max_length=20, choices=Current_App, default='Digithup', null=True, blank=True)
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
            code = f'SystemWallet-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SystemWallet, self).save(*args, **kwargs)



