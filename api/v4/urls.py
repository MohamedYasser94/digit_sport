from django.urls import path, include

from api.v3.views import notification
from api.v3.views.apps.sport import sport, media, hive, monks

app_name = 'api'
# DELETE_EXPIRED_TOKENS_INTERVAL = DjangoRestJwtRegistrationConfig.settings['DELETE_EXPIRED_TOKENS_INTERVAL']
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('devices', FCMDeviceAuthorizedViewSet)
router.register('devices/notification/device/info', notification.AdminDeviceInfoFromApp,
                basename='AdminDeviceInfoFromApp')
urlpatterns = [path('v3/', include(router.urls)),

               path('v3/devices/fcm/token/add/', notification.DeviceFcmAdd, name='DeviceFcmAdd'),
               path('v3/devices/fcm/token/status/', notification.DeviceFcmChangeUserStatus,
                    name='DeviceFcmChangeUserStatus'),
               path('v3/user/update/hive/data/', hive.UpdateHiveData, name='DeleteHiveData'),

               ################# Sports #################
               path('v3/<str:sport_name>/leagues/<str:date>/list/', sport.LeaguesBySportAndDateApiList,
                    name='LeaguesBySportAndDateApiList'),
               path('v3/leagues/<int:leagueid>/matches/date/<str:date>/', sport.LeaguesBySportAndDateMatchesApiList,
                    name='LeaguesBySportAndDateMatchesApiList'),
               path('v3/leagues/details/<int:leagueid>/', sport.LeaguesDetailsApi, name='LeaguesDetailsApi'),

               path('v3/leagues/<int:leagueId>/matches/type/<str:type>/', sport.LeagueMatchesByTypeApiList,
                    name='LeagueMatchesByTypeApiList'),

               path('v3/leagues/<int:leagueId>/teams/list/', sport.LeagueTeamsApiList, name='LeagueTeamsApiList'),

               path('v3/matches/details/<int:match_id>/', sport.MatchDetailsApi, name='MatchDetailsApi'),

               path('v3/teams/<int:team_id>/matches/<str:day_type>/list/', sport.TeamMatchesApiList,
                    name='TeamMatchesApiList'),

               path('v3/season/<str:league_id>/table/list/', sport.SeasonTableByLeagueApiList,
                    name='SeasonTableByLeagueApiList'),

               path('v3/sport/teams/details/<int:team_id>/', sport.SportTeamsApiDetails, name='SportTeamsApiDetails'),
               path('v3/sport/teams/<str:sport>/list/', sport.SportTeamsApiList, name='SportTeamsApiList'),
               path('v3/sport/tables/<int:group>/list/', sport.SportTablesApiList, name='SportTablesApiList'),
               path('v3/sport/teams/<int:team_id>/<int:league_id>/players/list/', sport.SportTeamsPlayersApiDetails,
                    name='SportTeamsPlayersApiDetails'),
               path('v3/sport/players/details/<int:player_id>/', sport.SportPlayersApiDetails,
                    name='SportPlayersApiDetails'),

               ########################### Hive Flutter  API ###########################
               path('v3/hive/leagues/list/', hive.HiveLeaguesApiList, name='HiveLeaguesApiList'),
               path('v3/hive/teams/list/', hive.HiveTeamApiList, name='HiveTeamApiList'),
               path('v3/hive/matches/list/', hive.HiveMatchesApiList, name='HiveMatchesApiList'),

               path('v3/hive/table/list/', hive.HiveTableApiList, name='HiveTableApiList'),
               path('v3/hive/standing/list/', hive.HiveStandingApiList, name='HiveStandingApiList'),

               path('v3/hive/rounds/list/', hive.HiveRoundsApiList, name='HiveRoundsApiList'),
               path('v3/hive/goals/list/', hive.HiveGoalsApiList, name='HiveGoalsApiList'),

               #####################  Monks App API ########################
               path('v3/hive/monks/leagues/list/', monks.HiveMonksLeaguesApiList, name='HiveMonksLeaguesApiList'),
               path('v3/hive/db/monks/leagues/list/', monks.HiveDBMonksLeaguesApiList,
                    name='HiveDBMonksLeaguesApiList'),
               path('v3/hive/monks/leagues/<str:date>/<str:locale>/list/', monks.HiveMonksLeaguesByDateApiList,
                    name='HiveMonksLeaguesByDateApiList'),
               path('v3/hive/monks/leagues/fixtures/<int:league_id>/<str:date>/<str:locale>/list/',
                    monks.HiveMonksLeaguesFixturesByDateApiList, name='HiveMonksLeaguesFixturesByDateApiList'),

               path('v3/hive/monks/fixtures/<str:date>/<str:locale>/list/', monks.HiveMonksFixturesByDateApiList,
                    name='HiveMonksFixturesByDateApiList'),
path('v4/fixtures/<str:date>/<str:lang>/list/', monks.FixturesByDateApiList,
                    name='FixturesByDateApiList'),
               path('v3/hive/monks/fixtures/details/<int:fixture_id>/<str:locale>/', monks.HiveMonksFixturesDetailsApi,
                    name='HiveMonksFixturesDetailsApi'),
               path('v3/hive/db/monks/teams/list/', monks.HiveDBMonksTeamsApiList, name='HiveDBMonksTeamsApiList'),

               ##################### News  API ########################
               path('v3/media/youtube/channel/', media.YoutubeChannelApiList, name='YoutubeChannelApiList'),
               path('v3/sport/general/news/list/', sport.SportNewsByCountryApiList, name='SportNewsByCountryApiList'),
               path('v3/sport/news/details/<int:article_id>/', sport.SportNewsApiDetails, name='SportNewsApiDetails'),
               path('v3/videos/list/', sport.SportVideosApiList, name='SportVideosApiList'),
               path('v3/sport/general/videos/<str:country>/<str:sport>/', sport.SportVideosByCountryApiList,
                    name='SportVideosByCountryApiList'),

               ]  # scheduler.interval(UserToken.objects.delete_expired_tokens, DELETE_EXPIRED_TOKENS_INTERVAL)
