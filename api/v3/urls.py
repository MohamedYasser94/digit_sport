from django.urls import path, include

from api.v3.views import blog
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

               ##################### Blog API ########################
               path('v3/blog/category/', blog.AdminBlogCategoriesSerializerList, name='AdminBlogCategoriesAPiList'),
               path('v3/blog/category/<int:pk>/', blog.BlogCategoriesDetail.as_view(),
                    name='AdminBlogCategoriesAPiList'),
               path('v3/blog/tag/', blog.BlogTagsList.as_view(), name='AdminBlogTagsAPiList'),
               path('v3/blog/tag/<int:pk>/', blog.BlogTagsDetail.as_view(), name='AdminBlogTagsAPiList'),
               path('v3/blog/service/', blog.BlogServicesList.as_view(), name='AdminBlogServicesAPiList'),
               path('v3/blog/service/<int:pk>/', blog.BlogServicesDetail.as_view(), name='AdminBlogServicesAPiList'),
               path('v3/blog/article/', blog.AdminBlogArticleSerializerList, name='AdminBlogArticleAPiList'),
               path('v3/blog/article/<int:pk>/', blog.BlogArticleDetail.as_view(), name='AdminBlogArticleAPiList'),

               ################# Sportrs #################
               path('v3/sport/leagues/<str:date>/<str:sport_name>/list/', sport.LeaguesBySportApiList,
                    name='LeaguesBySportApiList'),
               path('v3/sport/matches/<str:date>/<int:leagueid>', sport.MatchesByDateApiList,
                    name='MatchesByDateApiList'),

               path('v3/sport/matches/details/<int:match_id>/', sport.MatchDetailsApi, name='MatchDetailsApi'),



               path('v3/sport/<str:sport_name>/matches/list/<int:leagueId>/', sport.MatchesBySportApiList,
                    name='MatchesBySportApiList'),
               path('v3/sport/<str:sport_name>/matches/<str:type>/<int:leagueId>/', sport.MatchesBySportAndDateApiList,
                    name='MatchesBySportAndDateApiList'),

               path('v3/sport/<str:sport_name>/season/table/list/', sport.SeasonTableBySportApiList,
                    name='SeasonTableBySportApiList'),



               ##################### Mix Sport Monks API ########################
               path('v3/sport/teams/<str:sport>/list/', sport.SportTeamsApiList, name='SportTeamsApiList'),
               path('v3/sport/teams/details/<int:team_id>/', sport.SportTeamsApiDetails, name='SportTeamsApiDetails'),
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
