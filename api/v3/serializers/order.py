from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from api.v3.serializers.catalog import ProductsSerializer
from api.v3.serializers.client import ClientsSerializer
from api.v3.serializers.core import CommonProfileSerializer
from apps.catalog.models.models import Products


from core.models.core import CommonProfile
from core.models.people import Clients
from core.models.shop import OrderItem, Order, Cashier


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class CashierSerializer(serializers.ModelSerializer):

    client = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = Cashier
        fields = '__all__'

    def get_client(self, obj):
        print('odsfdsbj ', obj)
        print('obj ', obj)
        print('obj people', obj.client)
        client = Clients.objects.filter(id=obj.client.id)
        return ClientsSerializer(client, many=True, context=self.context).data
    def get_address(self, obj):
        print('obj people', obj)
        address = CommonProfile.objects.filter(owner_model=ContentType.objects.get(model='Clients'), owner_id=obj.client.id)
        return CommonProfileSerializer(address, many=True, context=self.context).data



class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = '__all__'

    def get_product(self, product):
        product = Products.objects.filter(id=product.product.id)
        return ProductsSerializer(product, many=True, context=self.context).data
