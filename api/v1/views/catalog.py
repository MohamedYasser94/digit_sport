from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from api.v1.serializers.catalog import CategoriesSerializer, ProductsSerializer, ProductVariantsSerializer
from apps.catalog.models.models import Categories, Products, ProductVariants
from core.models.people import Clients


##########################      Catalog Categories Admin            ################################
def AdminPosSubCategories(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    category = Clients.objects.all()
    serializer = CategoriesSerializer(category, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def AdminPosSubCategory(request, category_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('category_id', category_id)
    category_item = None
    category_items = Categories.objects.filter(id=category_id)
    for category in category_items:
        category_item = Categories.objects.filter(parent=category.id)
        print('category_item', category_item)
    serializer = CategoriesSerializer(category_item, many=True)
    return JsonResponse(serializer.data, safe=False)

def AdminPosAllProducts(request ):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    product_item = Products.objects.all()
    serializer = ProductsSerializer(product_item, many=True)
    return JsonResponse(serializer.data, safe=False)
@csrf_exempt
def AdminPosCategoryProducts(request, category_id):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    product_item = None
    categories = Categories.objects.filter(id=category_id)
    for category in categories:
        product_item = Products.objects.filter(category_id=category.id)

    serializer = ProductsSerializer(product_item, many=True)
    return JsonResponse(serializer.data, safe=False)



########## Product Home API #########


def APiGetProductVariant(request, variant_code):

    variant = None
    try:
        variant = ProductVariants.objects.filter(Q(code=variant_code) |Q(title=variant_code))


    except Exception as e:
        print('eroro from get prches oreder ',e)



    serializer = ProductVariantsSerializer(variant, many=True)
    return JsonResponse(serializer.data, safe=False)