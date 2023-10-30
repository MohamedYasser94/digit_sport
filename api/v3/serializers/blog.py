from rest_framework import serializers

from core.models.blog import BlogArticle, BlogCategories, CommonTags, BlogServices, BlogVideo
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
        fields =[ 'id','title','image_path','body','author','create_at']



class AdminBlogVideoSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = BlogVideo
        fields = [ 'id','title','image_path','author','video_source','video_url','create_at']
