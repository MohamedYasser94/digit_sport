from api.v3.serializers.blog import *
from apps.sport.models.media import *
from core.models.blog import *


class AdminYoutubeChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YoutubeChannel
        fields = "__all__"


class AdminYoutubeVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = YoutubeVideo
        fields = "__all__"


class AdminMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = "__all__"


