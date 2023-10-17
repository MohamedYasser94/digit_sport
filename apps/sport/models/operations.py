from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from slugify import slugify

from apps.event.models.models import Speaker, Sponsor, Ticket
from core.models.operations import Custody
from core.models.people import Employee
from helper.modelHelper import Active_Status, Public_Status

# Create your models here.


User = get_user_model()


class EventManagement(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='eventmanagement_sender', on_delete=models.CASCADE, null=True,blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='eventmanagement_receiver', on_delete=models.CASCADE, null=True,blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='eventmanagement_owner', on_delete=models.SET_NULL, null=True,blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    code = models.CharField(max_length=200, blank=False, null=False, unique=True, )
    status = models.CharField(max_length=60, choices=Active_Status, null=True, blank=True, default='Active')
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def get_absolute_url(self):
        return reverse('event:EventManagementDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'EventManagement-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(EventManagement, self).save(*args, **kwargs)

class EventTime(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='eventtime_sender', on_delete=models.CASCADE, null=True,blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='eventtime_receiver', on_delete=models.CASCADE, null=True,blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='eventtime_owner', on_delete=models.SET_NULL, null=True,blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    total_days = models.CharField(max_length=250, blank=True, null=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    total_time = models.CharField(max_length=250, blank=True, null=True)
    session_time = models.PositiveIntegerField(blank=True, null=True)
    visitor = models.IntegerField(blank=True, null=True)
    exact_visitor = models.IntegerField(blank=True, null=True)
    attendee_time = models.CharField(max_length=250, blank=True, null=True)
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, blank=True, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def get_absolute_url(self):
        return reverse('event:EventTimeDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'EventTime-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(EventTime, self).save(*args, **kwargs)


class EventSpeakers(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='eventspeakers_sender', on_delete=models.CASCADE, null=True,blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='eventspeakers_receiver', on_delete=models.CASCADE, null=True,blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='eventspeakers_owner', on_delete=models.SET_NULL, null=True,blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    attendee_count = models.IntegerField(blank=True, null=True)
    review = models.TextField(blank=True, null=False)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, blank=True, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
    def get_absolute_url(self):
        return reverse('event:EventSpeakersDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'EventSpeakers-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(EventSpeakers, self).save(*args, **kwargs)


class EventSponsors(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='eventsponsors_sender', on_delete=models.CASCADE, null=True,blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='eventsponsors_receiver', on_delete=models.CASCADE, null=True,blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='eventsponsors_owner', on_delete=models.SET_NULL, null=True,blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, blank=True, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
    def get_absolute_url(self):
        return reverse('event:EventSponsorsDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'EventSponsors-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(EventSponsors, self).save(*args, **kwargs)


class EventRoom(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='eventroom_sender', on_delete=models.CASCADE, null=True,blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='eventroom_receiver', on_delete=models.CASCADE, null=True,blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    event = models.ForeignKey(EventManagement, related_name='eventroom_event', on_delete=models.CASCADE, null=True,blank=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=False)
    capacity = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, blank=True, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
    def get_absolute_url(self):
        return reverse('event:EventRoomDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'EventRoom-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(EventRoom, self).save(*args, **kwargs)


class RoomStock(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='roomstock_sender', on_delete=models.CASCADE, null=True,blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='roomstock_receiver', on_delete=models.CASCADE, null=True,blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='roomstock_owner', on_delete=models.SET_NULL, null=True,blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    supplier = models.CharField(max_length=255, blank=True, null=True)
    supplier_note = models.TextField(blank=True, null=False)
    stock = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=255,choices=Active_Status, blank=True, null=True,default='Active')
    note = models.TextField(blank=True, null=False)
    code = models.CharField(max_length=200, blank=False, null=False, unique=True, )
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def get_absolute_url(self):
        return reverse('event:RoomStockDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'RoomStock-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(RoomStock, self).save(*args, **kwargs)


class ConferenceCustody(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='conferencecustody_sender', on_delete=models.CASCADE, null=True,blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='conferencecustody_receiver', on_delete=models.CASCADE, null=True,blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='conferencecustody_owner', on_delete=models.SET_NULL, null=True,blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    custody = models.ForeignKey(Custody, related_name='conferencecustody_custody', on_delete=models.CASCADE, null=True,blank=True)
    item_count = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=False)
    approve_transfer = models.CharField(max_length=255,choices=Public_Status, blank=True, null=True,default='No')
    approve_transfer_by = models.ForeignKey(User, related_name='conferencecustody_approve_transfer_by', on_delete=models.SET_NULL, null=True,blank=True)
    approve_transfer_date = models.DateField(blank=True, null=True)
    approve_transfer_note = models.TextField(blank=True, null=False)
    approve_transfer_status = models.CharField(max_length=255,choices=Active_Status, blank=True, null=True,default='Active')
    approve_transfer_return = models.CharField(max_length=255,choices=Public_Status, blank=True, null=True,default='No')
    approve_transfer_return_by = models.ForeignKey(User, related_name='conferencecustody_approve_transfer_return_by', on_delete=models.SET_NULL, null=True,blank=True)
    approve_transfer_return_date = models.DateField(blank=True, null=True)
    approve_transfer_return_note = models.TextField(blank=True, null=False)
    need_condition = models.CharField(max_length=255, choices=Public_Status, blank=True, null=True, default='No')
    condition = models.CharField(max_length=255, blank=True, null=True, default='No')
    condition_note = models.TextField(blank=True, null=False)
    code = models.CharField(max_length=200, blank=False, null=False, unique=True, )
    status = models.CharField(max_length=60, choices=Active_Status, null=True, blank=True, default='Active')
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('event:ConferenceCustodyDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'ConferenceCustody-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(ConferenceCustody, self).save(*args, **kwargs)


class AttendeesCustody(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='attendeescustody_sender', on_delete=models.CASCADE, null=True,blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='attendeescustody_receiver', on_delete=models.CASCADE, null=True,blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='attendeescustody_owner', on_delete=models.SET_NULL, null=True,blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    custody = models.ForeignKey(Custody, related_name='attendeescustody_custody', on_delete=models.CASCADE, null=True,blank=True)
    item_count = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, blank=True, default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event:AttendeesCustodyDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'AttendeesCustody-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(AttendeesCustody, self).save(*args, **kwargs)

class AttendeesAddon(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='attendeesaddon_sender', on_delete=models.CASCADE, null=True,blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='attendeesaddon_receiver', on_delete=models.CASCADE, null=True,blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='attendeesaddon_owner', on_delete=models.SET_NULL, null=True,blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    item = models.ForeignKey(ConferenceCustody, related_name='attendeesaddon_item', on_delete=models.CASCADE, null=True,blank=True)
    item_count = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.code
    def get_absolute_url(self):
        return reverse('event:ConferenceAttendeesAddonDetails', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code =f'AttendeesAddon-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(AttendeesAddon, self).save(*args, **kwargs)





