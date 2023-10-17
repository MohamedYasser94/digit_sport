##### get data from model ---------> json
from rest_framework import serializers

from apps.event.models.models import EventAttendees
from apps.press.models.models import PressCategory, PressServices, Printers, PrinterJob, \
    PressMachine, MachineJob




class AdminEventAttendeesSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventAttendees
        fields = '__all__'
