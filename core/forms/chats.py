from django import forms
from django.contrib.auth import get_user_model

from core.models.chat import Room

User = get_user_model()

class RoomCreationsForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [ 'private_room', 'passcode']