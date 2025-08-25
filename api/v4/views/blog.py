from django.http import JsonResponse
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.v3.serializers.blog import AdminBlogArticleSerializer, AdminBlogCategoriesSerializer, \
    AdminBlogTagsiesSerializer, AdminBlogServicesSerializer
from core.models.blog import BlogArticle, BlogCategories, CommonTags, BlogServices


##########################      Blog Categories Admin            ################################
class BlogCategoriesList(ListCreateAPIView):
    queryset = BlogCategories.objects.all()
    serializer_class = AdminBlogCategoriesSerializer

def AdminBlogCategoriesSerializerList(request):
    blog_list = BlogCategories.objects.all()
    success = True
    data ={}
    message = "Send From Django API"
    serializer = AdminBlogCategoriesSerializer(blog_list, many=True)

    data = {
        'success': success,
        'data': serializer.data,
        'message': message,

    }
    return JsonResponse(data, safe=False)

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


def AdminBlogArticleSerializerList(request):
    blog_list = BlogArticle.objects.all()
    success = True
    data ={}
    message = "Send From Django API"
    serializer = AdminBlogArticleSerializer(blog_list, many=True)

    data = {
        'success': success,
        'data': serializer.data,
        'message': message,

    }
    return JsonResponse(data, safe=False)


class BlogArticleDetail(RetrieveUpdateDestroyAPIView):
    queryset = BlogArticle.objects.all()
    serializer_class = AdminBlogArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)  # new
    parser_classes = [MultiPartParser,FileUploadParser]