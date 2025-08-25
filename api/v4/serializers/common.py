from rest_framework import serializers

from core.models.core import CommonMediaFiles


class FrontCommonMediaFilesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = CommonMediaFiles
        fields = "__all__"





