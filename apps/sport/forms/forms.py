from django import forms
from django.contrib.auth import get_user_model

from apps.event.models.models import EventCategory, Ticket, Event, EventAttendees, EventAttendeesHistory, Speaker, Sponsor, \
    Event

User = get_user_model()


class AdminTicketCategoryForm(forms.ModelForm):
    class Meta:
        model = EventCategory
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminEventAttendeesForm(forms.ModelForm):
    class Meta:
        model = EventAttendees
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminEventAttendeesHistoryForm(forms.ModelForm):
    class Meta:
        model = EventAttendeesHistory
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminSpeakerForm(forms.ModelForm):
    class Meta:
        model = Speaker
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminSponsorForm(forms.ModelForm):
    class Meta:
        model = Sponsor
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        exclude = ('slug', 'code')
