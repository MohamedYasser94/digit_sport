from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.v1.serializers.blog import AdminBlogArticleSerializer, AdminBlogCategoriesSerializer, \
    AdminBlogTagsiesSerializer, AdminBlogServicesSerializer
from core.models.blog import BlogArticle, BlogCategories, CommonTags, BlogServices


##########################      Blog Categories Admin            ################################
class BlogCategoriesList(ListCreateAPIView):
    queryset = BlogCategories.objects.all()
    serializer_class = AdminBlogCategoriesSerializer



class BlogCategoriesDetail(RetrieveUpdateDestroyAPIView):
    queryset = BlogCategories.objects.all()
    serializer_class = AdminBlogCategoriesSerializer



##########################      Blog Tag Admin            ################################

class BlogTagsList(ListCreateAPIView):
    queryset = CommonTags.objects.all()
    serializer_class = AdminBlogTagsiesSerializer



class BlogTagsDetail(RetrieveUpdateDestroyAPIView):
    queryset = CommonTags.objects.all()
    serializer_class = AdminBlogTagsiesSerializer


##########################      Blog Tag Admin            ################################

class BlogServicesList(ListCreateAPIView):
    queryset = BlogServices.objects.all()
    serializer_class = AdminBlogServicesSerializer


class BlogServicesDetail(RetrieveUpdateDestroyAPIView):
    queryset = BlogServices.objects.all()
    serializer_class = AdminBlogServicesSerializer



##########################      Blog Article Admin            ################################

class BlogArticleList(ListCreateAPIView):
    queryset = BlogArticle.objects.all()
    serializer_class = AdminBlogArticleSerializer



class BlogArticleDetail(RetrieveUpdateDestroyAPIView):
    queryset = BlogArticle.objects.all()
    serializer_class = AdminBlogArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)  # new
    parser_classes = [MultiPartParser,FileUploadParser]