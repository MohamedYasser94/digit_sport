from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework import status

from api.v1.serializers.catalog import ProductsSerializer
from apps.catalog.models.models import Products

from helper.decorators import staff_only, authenticated_staf


@authenticated_staf
@staff_only
# @csrf_exempt
# @csrf_protect
def APiGetPurchaseProduct(request, product_code):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    print('product_id', product_code)
    product_code = product_code.strip()
    if request.method == 'GET':
        product = Products.objects.filter(Q(code=product_code) | Q(title=product_code))
        if product.exists():
            serializer = ProductsSerializer(product, many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            return JsonResponse('Product not found', status=status.HTTP_404_NOT_FOUND, safe=False)
    else:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
