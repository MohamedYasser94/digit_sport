from rest_framework import serializers

from core.models.blog import BlogArticle, BlogCategories, CommonTags,  BlogVideo
from core.models.localization import Language




class AdminBlogCategoriesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = BlogCategories
        fields = "__all__"

class AdminBlogTagsiesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = CommonTags
        fields = "__all__"



class BlogArticleSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = BlogArticle
        fields =[ 'id','title','image','keyword','body','author','created_at',]

class AdminBlogArticleDetailsSerializer(serializers.ModelSerializer)    :
    body = serializers.SerializerMethodField()
    class Meta:
        model = BlogArticle
        fields =[ 'id','title','image_path', 'image','keyword','body','author','created_at',]

    def get_body(self, obj):
        return obj.body

class AdminBlogVideoSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = BlogVideo
        fields = [ 'id','title','video_source','video_url']
