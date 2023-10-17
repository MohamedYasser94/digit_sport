from rest_framework import serializers

from core.models.people import Clients




class ClientsSerializer(serializers.ModelSerializer):
    get_absolute_url = serializers.SerializerMethodField()
    my_absolute_url = serializers.URLField(source='get_absolute_url', read_only=True)
    class Meta:
        model = Clients
        fields = ['id', 'title', 'code', 'get_absolute_url', 'my_absolute_url', 'create_at']

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()


# class ClientsObjectRelatedField(serializers.RelatedField):
#     def to_representation(self, value):
#         if isinstance(value, Clients):
#             serializer = ClientsSerializer(value)
#
#         else:
#             raise Exception('Unexpected type of tagged object')
#
#         return serializer.data

