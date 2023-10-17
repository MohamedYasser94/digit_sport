from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from api.v1.serializers.core import CommonMediaFilesSerializer
from apps.catalog.models.models import Categories, Variants, ProductVariants, Products

from core.models.core import CommonMediaFiles


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'


class CatalogVariantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variants
        fields = '__all__'


class ProductVariantsSerializer(serializers.ModelSerializer):
    product_size = Variants.objects.filter(option_type='Size')

    class Meta:
        model = ProductVariants
        fields = '__all__'


class ProductsSerializer(serializers.ModelSerializer):
    product_variants = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = '__all__'

    def get_product_variants(self, product):
        product_variants = ProductVariants.objects.filter(product=product)
        return ProductVariantsSerializer(product_variants, many=True, context=self.context).data

    def get_product_image(self, product):
        product_image = CommonMediaFiles.objects.filter(type='hero',
                                                        owner_model=ContentType.objects.get(model='Products'),
                                                        owner_id=product.id)

        return CommonMediaFilesSerializer(product_image, many=True, context=self.context).data
