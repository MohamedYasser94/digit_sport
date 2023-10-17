from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from api.v1.serializers.common import FrontCommonMediaFilesSerializer
from apps.catalog.models.models import Categories, Products

from core.models.core import CommonMediaFiles
from home.views.views import FRONTEND_TEMPLATES


def FrontCatagoriesList(request):
    categories = Categories.objects.all()
    products = Products.objects.all()
    product_list = []
    for product in products:
        image = CommonMediaFiles.objects.get(type='hero',
                                             owner_model=ContentType.objects.get(model='Products'),
                                             owner_id=product.id)
        product_list.append(
            {"product": product, "image": image, })

    context = {
        'categories': categories,

        'products': product_list,

    }
    return render(request, f'{FRONTEND_TEMPLATES}/catalog/category/categories.html', context)


def CategoryDetails(request, slug):
    category = Categories.objects.get(slug=slug)
    products = Products.objects.filter(category=category)
    product_list = []
    for product in products:
        images = CommonMediaFiles.objects.get(type='hero',
                                              owner_model=ContentType.objects.get(model='Products'),
                                              owner_id=product.id)
        product_list = [{"category": category, "product": product, "images": images}]
    context = {
        'categories': product_list,


        'products': product_list,
    }
    return render(request, f'{FRONTEND_TEMPLATES}/catalog/category/category.html', context)


def ProductDetails(request, slug):
    try:
        product = Products.objects.get(slug=slug)
    except ObjectDoesNotExist  :
        return render(request, f'{FRONTEND_TEMPLATES}/catalog/product/details.html',)
    product_image = CommonMediaFiles.objects.filter(
        owner_model=ContentType.objects.get(model='Products'),
        owner_id=product.id)
    image_list = list(product_image.values('type', 'id', 'image'))
    product_variant = ProductVariants.objects.filter(product=product)
    print('product_variant',product_variant)

    try:
        previous_product = Products.objects.get(id=product.id - 1)
        print('previous_product ', previous_product)
    except Exception as e:
        print('pre error ', e)
        previous_product = product
    try:
        next_product = Products.objects.get(id=product.id + 1)

    except:
        next_product = product
    products_related = Products.objects.all()
    products_related_list = []
    for product_id in products_related:
        try:
            image = CommonMediaFiles.objects.get(type='hero',
                                                 owner_model=ContentType.objects.get(model='Products'),
                                                 owner_id=product_id.id)
        except Exception as e :
            image=None
        products_related_list.append({"product": product_id, "image": image, })

    context = {
        'product': product,
        'product_variant':product_variant,
        'title': product.title,
        'products_related': products_related_list,
        'product_image': product_image,
        'image_list': image_list,
        'previous_product': previous_product,
        'next_product': next_product,
    }
    return render(request, f'{FRONTEND_TEMPLATES}/catalog/product/details.html', context)


@csrf_exempt
def ProductImageDetails(request, id):
    images = CommonMediaFiles.objects.filter(id=id)
    serializer = FrontCommonMediaFilesSerializer(images, many=True)
    return JsonResponse(serializer.data, safe=False)
