from django import forms
from django.contrib.auth import get_user_model

from apps.event.models.models import EventCategory, Ticket, Event, EventAttendees, EventAttendeesHistory, Speaker, Sponsor, \
    Event
from apps.event.models.operations import EventManagement, EventTime

User = get_user_model()


class AdminEventManagementForm(forms.ModelForm):
    class Meta:
        model = EventManagement
        fields = '__all__'
        exclude = ('slug', 'code')

class AdminEventTimeForm(forms.ModelForm):
    class Meta:
        model = EventTime
        fields = '__all__'
        exclude = ('slug', 'code')