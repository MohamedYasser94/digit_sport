from rest_framework import serializers

from apps.catalog import Station, Reservation


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['id','title','status','image']

class ReservationSerializer(serializers.ModelSerializer):
    station = StationSerializer()

    class Meta:
        model = Reservation
        fields =  ['id','station','minutes','active','employee','start_time']
