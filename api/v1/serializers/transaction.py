from core.models.transaction import MoneyTransaction, ProductTransaction, ShippingTransaction
from rest_framework import serializers

class MoneyTransactionSerializer(serializers.ModelSerializer):


    class Meta:
        model = MoneyTransaction
        fields = '__all__'

class MoneyTransactionObjectRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, MoneyTransaction):
            serializer = MoneyTransactionSerializer(value)

        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data

class ProductTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTransaction
        fields = '__all__'


class ShippingTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingTransaction
        fields = '__all__'