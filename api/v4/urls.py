from django.urls import path, include

from api.v3.views import notification
from api.v3.views.apps.sport import sport, media, hive, monks
from api.v3.views.apps.sport.monks import FavoriteLeagueToggle

app_name = 'api'
# DELETE_EXPIRED_TOKENS_INTERVAL = DjangoRestJwtRegistrationConfig.settings['DELETE_EXPIRED_TOKENS_INTERVAL']
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

from rest_framework.routers import DefaultRouter




urlpatterns = [

    path('v4/fixtures/<str:sport>/<str:date>/<str:lang>/list/', monks.FixturesByDateApiList,
         name='FixturesByDateApiList'),

    path('v4/leagues/toggle-favorite/', FavoriteLeagueToggle.as_view(), name='toggle-favorite-league'),

    path('v4/fixtures/detail/<int:fixture_id>/<str:lang>/', monks.FixtureDetailApiView, name='FixtureDetailApiView'),

    ############# league api urls #############

    path('v4/leagues/detail/<int:league_id>/<str:lang>/', monks.LeagueDetailApiView, name='LeagueDetailApiView'),
    path('v4/leagues/<int:league_id>/<str:lang>/standings/', monks.LeagueStandingsApiView, name='LeagueStandingsApiView'),

    path('v4/leagues/<int:league_id>/<str:lang>/top-scorers/', monks.LeagueTopScorersApiView, name='LeagueTopScorersApiView'),





               ]
