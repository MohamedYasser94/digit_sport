from rest_framework import serializers

from core.models.blog import BlogArticle, BlogCategories, CommonTags, BlogServices
from core.models.localization import Language




class AdminBlogCategoriesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = BlogCategories
        fields = "__all__"

class AdminBlogTagsiesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = CommonTags
        fields = "__all__"

class AdminBlogServicesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = BlogServices
        fields = "__all__"


class AdminBlogArticleSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = BlogArticle
        fields = "__all__"
        extra_kwargs = {
            'tags': {'required': False},
            'extra_image': {'required': False},
        }



