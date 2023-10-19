from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.sport.models import *
from api.v1.serializers.sport import *



class SportCategoryList(ListCreateAPIView):
    queryset = SportCategory.objects.all()
    serializer_class = AdminSportCategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminSportCategorySerializer
        else:
            return AdminSportCategorySerializer

class SportCategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = SportCategory.objects.all()
    serializer_class = AdminSportCategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminSportCategorySerializer
        else:
            return AdminSportCategorySerializer

class AdminSportSerializerList(ListCreateAPIView):
    queryset = Sport.objects.all()
    serializer_class = AdminSportSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminSportSerializer
        else:
            return AdminSportSerializer


class AdminSportSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Sport.objects.all()
    serializer_class = AdminSportSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminSportSerializer
        else:
            return AdminSportSerializer

class AdminLeaguesSerializerList(ListCreateAPIView):
    queryset = Leagues.objects.all()
    serializer_class = LeaguesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LeaguesSerializer
        else:
            return LeaguesSerializer

class AdminLeaguesSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Leagues.objects.all()
    serializer_class = LeaguesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LeaguesSerializer
        else:
            return LeaguesSerializer


class AdminSeasonSerializerList(ListCreateAPIView):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SeasonSerializer
        else:
            return SeasonSerializer

class AdminSeasonSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SeasonSerializer
        else:
            return SeasonSerializer