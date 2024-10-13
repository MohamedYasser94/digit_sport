from django.urls import path, include

from api.v3.views import notification
from api.v3.views.apps.sport import sport, media

app_name = 'api'
# DELETE_EXPIRED_TOKENS_INTERVAL = DjangoRestJwtRegistrationConfig.settings['DELETE_EXPIRED_TOKENS_INTERVAL']
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('devices', FCMDeviceAuthorizedViewSet)
router.register('devices/notification/device/info', notification.AdminDeviceInfoFromApp,
                basename='AdminDeviceInfoFromApp')
urlpatterns = [path('v3/', include(router.urls)),

               path('v3/devices/fcm/token/post/', notification.DeviceInfoFromApp, name='DeviceInfoFromApp'),

               ################# Sportrs #################
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

               ########################### Old API ###########################

               # path('v3/sport/matches/<str:sport_name>/', sport.MatchesBySportApiList, name='MatchesBySportApiList'),

               path('v3/sport/match/details/<int:match_id>/', sport.MatchDetailsApi, name='MatchDetailsApi'),

               # path('v3/sport/<str:sport_name>/matches/list/<int:leagueId>/', sport.MatchesBySportApiList,
               #      name='MatchesBySportApiList'),



               ##################### Mix Sport Monks API ########################
               path('v3/sport/teams/<str:sport>/list/', sport.SportTeamsApiList, name='SportTeamsApiList'),


               path('v3/sport/<str:sport_name>/<int:team_id>/players/list/', sport.PlayersBySportApiList,
                    name='PlayersBySportApiList'),
               path('v3/sport/players/details/<int:playerid>/', sport.PlayersApiDetails, name='PlayersApiDetails'),

               ##################### Youtube Channel API ########################
               path('v3/media/youtube/channel/', media.YoutubeChannelApiList, name='YoutubeChannelApiList'),
               path('v3/sport/general/news/list/', sport.SportNewsByCountryApiList, name='SportNewsByCountryApiList'),
               path('v3/sport/news/details/<int:article_id>/', sport.SportNewsApiDetails, name='SportNewsApiDetails'),
               path('v3/videos/list/', sport.SportVideosApiList, name='SportVideosApiList'),
               path('v3/sport/general/videos/<str:country>/<str:sport>/', sport.SportVideosByCountryApiList,
                    name='SportVideosByCountryApiList'),

               ]  # scheduler.interval(UserToken.objects.delete_expired_tokens, DELETE_EXPIRED_TOKENS_INTERVAL)
