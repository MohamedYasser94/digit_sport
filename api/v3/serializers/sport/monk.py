from collections import OrderedDict

from django.core.files.storage import get_storage_class

from api.v3.serializers.blog import *
from apps.sport.models.models import *
from apps.sport.models.monks import *
from core.models.blog import *


class AdminMonkCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MonkCountry
        fields = ['id', 'name', ]