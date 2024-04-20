from api.v3.serializers.blog import *
from apps.sport.models.monks import *


class AdminMonkCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MonkCountry
        fields = ['id', 'name', ]