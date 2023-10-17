import datetime
import uuid

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, User, AbstractUser, Permission, Group, \
    PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.validators import validate_integer
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from core.models.localization import Country, City, Area, Governorates, Language, Currency
from helper.modelHelper import Active_Status, User_Position, Email_Validator, Access_Level, User_Status, Country_List, \
    Governorates_List
from helper.viewHelper import get_file_path
from user.apps import DjangoRestJwtRegistrationConfig
from user.managers import TokenManager


class UserManager(BaseUserManager):

    def create_user(self, email, password=None):

        if email is None:
            raise TypeError(_('Users must have an email address.'))
        if User.objects.filter(email=self.normalize_email(email).lower()).exists():
            raise ValueError('This email has already been registered.')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):

        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, password)
        user.is_superuser = 'Active'
        user.is_staff = 'Active'
        user.is_active = 'Active'
        user.is_author = 'Active'
        user.admin = 'Active'
        user.is_customer = 'Active'
        user.is_verified = 'Active'
        user.is_online = 'Active'
        user.access_notification = 'Active'
        user.access_level = 'SuperAdmin'
        user.subscribe = 'Active'
        user.save()
        groups = Group.objects.get_or_create(name='superuser')
        groups = Group.objects.get(name='superuser')
        groups.user_set.add(user)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Description:This is going to be the main User Model
    """
    email = models.EmailField(verbose_name='email address', max_length=50, validators=[Email_Validator], unique=True,
                              error_messages={
                                  'unique': "This email has already been registered."})

    first_name = models.CharField(max_length=25, validators=[UnicodeUsernameValidator], blank=True, null=True)
    middle_name = models.CharField(max_length=25, validators=[UnicodeUsernameValidator], blank=True, null=True)
    last_name = models.CharField(max_length=25, validators=[UnicodeUsernameValidator], blank=True, null=True)
    position = models.CharField(max_length=30, validators=[UnicodeUsernameValidator], blank=True, null=True,
                                default='Client')
    phone = models.CharField(max_length=20, validators=[validate_integer], blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    auth_provider = models.CharField(
        max_length=50, blank=False,
        null=False, validators=[UnicodeUsernameValidator], default='email')
    is_superuser = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    admin =models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    is_staff = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    is_author = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    is_active = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    is_customer = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    subscribe = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    seller = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    deliver = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    is_verified = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    access_level = models.CharField(max_length=20, choices=Access_Level, default='Customer')
    access_notification = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    groups = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
    slug = models.SlugField(unique=True)
    nuc = models.CharField(unique=True, max_length=200)
    have_wallet = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    fcm_token = models.TextField(blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_online = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    hide_email = models.CharField(max_length=20, choices=User_Status, default='Inactive' , blank=True, null=True)
    country = models.CharField(max_length=100, choices=Country_List, default='Egypt', null=True, blank=True)
    governorates = models.CharField(max_length=100, choices=Governorates_List, default='Cairo', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        if self.first_name or self.last_name:
            return f'{self.first_name} {self.last_name} (Email: {self.email})'
        else:
            return self.email

    def save(self, *args, **kwargs):
        if not self.nuc and not self.slug :
            self.nuc = str(get_random_string(5).upper()
                           + str(uuid.uuid4()).split('-')[1] + 'NUC'
                           + uuid.uuid4().hex[:6].upper())
            self.slug = slugify(self.email)
            self.auth_provider = 'email'
        super(User, self).save(*args, **kwargs)

        # get token for current user

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def get_full_name(self):
        full_name = None
        if self.first_name or self.last_name:
            return f'{self.first_name} {self.last_name}'
        else:
            return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def has_perm(self, perm, obj=None):
        # Does the user have a specific permission?
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_admin(self):
        # "Is the user an admin member?"
        return self.is_admin

        # In this method, check that the date of the last visit is not older than 15 minutes

    def user_online(self):
        if self.last_activity:
            return (timezone.now() - self.last_activity) < timezone.timedelta(minutes=15)
        return False

    # If the user visited the site no more than 15 minutes ago,
    def get_online_info(self):
        if self.user_online():
            # then we return information that he is online
            return _('Online')
        if self.last_activity:
            # otherwise we write a message about the last visit
            return _('Last visit {}').format(naturaltime(self.last_activity))
            # If you have only recently added information about a user visiting the site
            # then for some users there may not be any information about the visit, we will return information that the last visit is unknown
        return _('Unknown')


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, max_length=20, null=True, blank=True)
    note = models.CharField(max_length=50, validators=[UnicodeUsernameValidator], blank=True, null=True)
    position = models.CharField(max_length=15, validators=[UnicodeUsernameValidator], choices=User_Position,
                                default='Guest', null=True, blank=True)
    lang = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, blank=True)
    dark_mode = models.CharField(max_length=10, choices=Active_Status, default='Inactive', null=True, blank=True)
    notification = models.CharField(max_length=10, choices=Active_Status, default='Active', null=True, blank=True)
    deactivate = models.CharField(max_length=10, choices=Active_Status, default='Inactive', null=True, blank=True)
    delete_account = models.CharField(max_length=10, choices=Active_Status, default='Inactive', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id





class UserGeoInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.CharField(max_length=30, null=True, blank=True)
    device_type = models.CharField(max_length=300, null=True, blank=True)
    browser_type = models.CharField(max_length=300, null=True, blank=True)
    browser_version = models.CharField(max_length=300, null=True, blank=True)
    os_type = models.CharField(max_length=300, null=True, blank=True)
    os_version = models.CharField(max_length=300, null=True, blank=True)
    location_country = models.CharField(max_length=300, null=True, blank=True)
    location_city = models.CharField(max_length=300, null=True, blank=True)
    create_at = models.DateTimeField(auto_now=True, null=False)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user"]
        verbose_name_plural = "User Geo Info"

    def __str__(self):
        return self.user


class UserToken(models.Model):
    objects = TokenManager()
    REGISTRATION_TOKEN = 'rt'
    REGISTRATION_DELETE_TOKEN = 'rd'
    PASSWORD_CHANGE_TOKEN = 'pc'
    EMAIL_CHANGE_TOKEN = 'ec'
    TOKEN_TYPES = (
        (REGISTRATION_TOKEN, _('Registration token')),
        (REGISTRATION_DELETE_TOKEN, _('Registration Delete UserToken')),
        (PASSWORD_CHANGE_TOKEN, _('Password Change UserToken')),
        (EMAIL_CHANGE_TOKEN, _('Change Email UserToken')),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    token = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=TOKEN_TYPES, max_length=3, default=REGISTRATION_TOKEN)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, default=None)

    def __str__(self):
        return self.token

    @property
    def lifetime(self):
        app_settings = DjangoRestJwtRegistrationConfig.settings
        return {
            UserToken.REGISTRATION_TOKEN: app_settings['REGISTRATION_TOKEN_LIFETIME'],
            UserToken.REGISTRATION_DELETE_TOKEN: app_settings['REGISTRATION_DELETE_TOKEN_LIFETIME'],
            UserToken.PASSWORD_CHANGE_TOKEN: app_settings['PASSWORD_CHANGE_TOKEN_LIFETIME'],
            UserToken.EMAIL_CHANGE_TOKEN: app_settings['EMAIL_CHANGE_TOKEN_LIFETIME'],
        }[self.type]

    @property
    def expires_at(self):
        return self.created_at.astimezone(datetime.timezone.utc) + datetime.timedelta(seconds=self.lifetime)


