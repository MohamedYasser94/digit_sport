from rest_framework import serializers

from core.models.core import CommonProfile, CommonMediaFiles


class CommonProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonProfile
        fields = '__all__'


class CommonMediaFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonMediaFiles
        fields = '__all__'