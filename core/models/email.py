from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from slugify import slugify

from helper.modelHelper import Active_Status, Email_status
from helper.viewHelper import get_file_path

User = get_user_model()

class EmailLabel(models.Model):
    owner_model = models.ForeignKey(ContentType, related_name='email_label_owner', on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    name = models.CharField(max_length=150, null=True, blank=True)
    color = models.CharField(max_length=150, null=True, blank=True)
    status = models.CharField(max_length=60, choices=Active_Status, null=True, default='Active')
    code = models.CharField(unique=True, max_length=20, )
    slug = models.SlugField(null=True, blank=True, max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'EmailLabel-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(self.code)
        super(EmailLabel, self).save(*args, **kwargs)

class Email(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='email_sender', on_delete=models.CASCADE, null=True,
                                        blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='email_receiver', on_delete=models.CASCADE, null=True,
                                            blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='email_owner', on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    emil_to = models.EmailField(max_length=50, null=True, blank=True)
    emil_cc = models.EmailField(max_length=50, null=True, blank=True)
    emil_bcc = models.EmailField(max_length=50, null=True, blank=True)

    subject = models.CharField(max_length=150, null=True, blank=True)
    body = models.TextField()
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    html_code = models.TextField(null=True, blank=True)
    locations = models.CharField(max_length=250, null=True, blank=True)
    attachment = models.FileField(upload_to=get_file_path, null=True, blank=True)
    label = models.ManyToManyField(EmailLabel, related_name='email_label')
    status = models.CharField(max_length=60, choices=Email_status, null=True, default='Unread')
    code = models.CharField(unique=True, max_length=20, )
    slug = models.SlugField(null=True, blank=True, max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('core:AdminEmailDetails', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Email-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(self.code)
        super(Email, self).save(*args, **kwargs)
