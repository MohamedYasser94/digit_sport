from rest_framework import serializers

from core.models.localization import Language


class AdminLanguageSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Language
        fields = "__all__"


