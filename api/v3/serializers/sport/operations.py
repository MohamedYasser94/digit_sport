
from rest_framework.fields import SerializerMethodField
from rest_framework.templatetags import rest_framework

from api.v3.serializers.blog import *
from apps.sport.models import *
from apps.sport.models.models import *
from core.models.blog import *
from digit_sport.settings import env




class MatchPlayerReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchPlayerReport
        fields = "__all__"

class PlayerStaticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStatics
        fields = "__all__"
