##### get data from model ---------> json
from rest_framework import serializers

from apps.catalog.models.models import Categories, Products


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'

class Productserializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'