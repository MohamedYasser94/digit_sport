import json

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import CASCADE
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.crypto import get_random_string
from django_extensions.db.models import TimeStampedModel

from slugify import slugify

User = get_user_model()


class Notification(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='notification_sender', on_delete=models.CASCADE,
                                     null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='notification_receiver', on_delete=models.CASCADE,
                                       null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='notification_owner', on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    auditor_model = models.ForeignKey(ContentType, related_name='notification_auditor', on_delete=models.PROTECT,
                                      null=True,
                                      blank=True)
    auditor_id = models.PositiveIntegerField(null=True, blank=True)
    auditor = GenericForeignKey('auditor_model', 'auditor_id')
    notification_type = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)
    second_read = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    notification =  models.CharField(max_length=250, null=True, blank=True)
    notification_url = models.CharField(max_length=250, null=True, blank=True)
    notification_slug = models.CharField(max_length=250, null=True, blank=True)
    notification_info = models.CharField(null=True, blank=True, max_length=255)
    notification_desc = models.TextField(null=True, blank=True)
    notification_time = models.DateField(null=True, blank=True)
    notification_notify = models.DateField(null=True, blank=True, )
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    def get_absolute_url(self):
        return reverse('core:AdminNotificationsDetails', kwargs={'slug': self.slug})
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Notification-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Notification, self).save(*args, **kwargs)


class NotificationSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.notification_type


class DeviceInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True, blank=True)
    device_id = models.CharField(max_length=250, null=True, blank=True)
    device_type = models.CharField(max_length=250, null=True, blank=True)
    device_token = models.CharField(max_length=250, null=True, blank=True)
    device_info = models.TextField(null=True, blank=True)
    version_securitypatch = models.CharField(max_length=250, null=True, blank=True)
    version_sdk = models.CharField(max_length=250, null=True, blank=True)
    version_release = models.CharField(max_length=250, null=True, blank=True)
    version_incremental = models.CharField(max_length=250, null=True, blank=True)
    version_codename = models.CharField(max_length=250, null=True, blank=True)
    version_baseos = models.CharField(max_length=250, null=True, blank=True)
    version_preview_sdk = models.CharField(max_length=250, null=True, blank=True)
    version_sdk_int = models.CharField(max_length=250, null=True, blank=True)
    board = models.CharField(max_length=250, null=True, blank=True)
    bootloader = models.CharField(max_length=250, null=True, blank=True)
    brand = models.CharField(max_length=250, null=True, blank=True)
    device = models.CharField(max_length=250, null=True, blank=True)
    display = models.CharField(max_length=250, null=True, blank=True)
    fingerprint = models.CharField(max_length=250, null=True, blank=True)
    hardware = models.CharField(max_length=250, null=True, blank=True)
    host = models.CharField(max_length=250, null=True, blank=True)
    manufacturer = models.CharField(max_length=250, null=True, blank=True)
    model = models.CharField(max_length=250, null=True, blank=True)
    product = models.CharField(max_length=250, null=True, blank=True)
    serial = models.CharField(max_length=250, null=True, blank=True)
    tags = models.CharField(max_length=250, null=True, blank=True)
    type = models.CharField(max_length=250, null=True, blank=True)
    is_physical_device = models.BooleanField(default=False)
    support_ted32 = models.BooleanField(default=False)
    support_ted64 = models.BooleanField(default=False)
    support_arm32 = models.BooleanField(default=False)
    support_arm64 = models.BooleanField(default=False)
    system_feature = models.TextField(null=True, blank=True)
    display_size = models.CharField(max_length=250, null=True, blank=True)
    display_density = models.CharField(max_length=250, null=True, blank=True)
    system_name = models.CharField(max_length=250, null=True, blank=True)
    system_version = models.CharField(max_length=250, null=True, blank=True)
    identifier_for_vendor = models.CharField(max_length=250, null=True, blank=True)
    is_advertising_tracking_enabled = models.BooleanField(default=False)
    is_jailbroken = models.BooleanField(default=False)
    is_tablet = models.BooleanField(default=False)
    is_simulator = models.BooleanField(default=False)
    is_debugger_attached = models.BooleanField(default=False)
    is_running_on_virtual_machine = models.BooleanField(default=False)
    is_running_on_chrome_os = models.BooleanField(default=False)
    is_running_on_fire_os = models.BooleanField(default=False)
    is_running_on_android_things = models.BooleanField(default=False)
    is_running_on_kaios = models.BooleanField(default=False)
    is_running_on_tvos = models.BooleanField(default=False)
    is_running_on_watchos = models.BooleanField(default=False)
    is_running_on_ios = models.BooleanField(default=False)
    is_running_on_macos = models.BooleanField(default=False)
    is_running_on_windows = models.BooleanField(default=False)
    is_running_on_linux = models.BooleanField(default=False)
    is_running_on_android = models.BooleanField(default=False)
    utsname_sysname = models.CharField(max_length=250, null=True, blank=True)
    utsname_nodename = models.CharField(max_length=250, null=True, blank=True)
    utsname_release = models.CharField(max_length=250, null=True, blank=True)
    utsname_version = models.CharField(max_length=250, null=True, blank=True)
    utsname_machine = models.CharField(max_length=250, null=True, blank=True)
    status = models.BooleanField(default=False)
    device_code = models.CharField(max_length=250, null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.device_id

    def save(self, *args, **kwargs):
        if not self.code and not self.slug and not self.device_code:
            device_code = f'{get_random_string(5).upper()}'
            code = f'DeviceInfo-{get_random_string(5).upper()}'
            self.device_code = device_code
            self.code = code
            self.slug = slugify(code)
        super(DeviceInfo, self).save(*args, **kwargs)




class ChatNotification(models.Model):
    # Who the notification is sent to
    target = models.ForeignKey(User, on_delete=models.CASCADE)

    # The user that the creation of the notification was triggered by.
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="from_user")

    redirect_url = models.URLField(max_length=500, null=True, unique=False, blank=True,
                                   help_text="The URL to be visited when a notification is clicked.")

    # statement describing the notification (ex: "Mitch sent you a friend request")
    verb = models.CharField(max_length=255, unique=False, blank=True, null=True)

    # When the notification was created/updated
    timestamp = models.DateTimeField(auto_now_add=True)

    # Some notifications can be marked as "read". (I used "read" instead of "active". I think its more appropriate)
    read = models.BooleanField(default=False)

    # A generic type that can refer to a FriendRequest, Unread Message, or any other type of "Notification"
    # See article: https://simpleisbetterthancomplex.com/tutorial/2016/10/13/how-to-use-generic-relations.html
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return self.verb

    def get_content_object_type(self):
        return str(self.content_object.get_cname)


class MobileDevice(models.Model):
    participant = models.OneToOneField(User, related_name='device', on_delete=CASCADE)
    platform = models.CharField(max_length=20, choices=(('iOS', 'iOS'), ('Android', 'Android'),))
    token = models.TextField()


class MobileNotification(TimeStampedModel):
    recipient = models.ForeignKey(User, related_name='user_device_notifications', on_delete=CASCADE)
    title = models.CharField(max_length=512, null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, default='unread')


class InAppMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=CASCADE)
    content = models.CharField(max_length=512)
