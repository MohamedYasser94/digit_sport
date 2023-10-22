from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api.v1.views import billing, blog
from api.v1.views.apps.sport import sport
from api.v1.views.localization import LanguageListAPIView
from api.v1.views.notification import AdminApiNotificationList
from api.v1.views.user import RegisterView, LoginAPIView, LogoutAPIView, VerifyEmail, RequestPasswordResetEmail, \
    PasswordTokenCheckAPI, SetNewPasswordAPIView, ApiPromoCodeClient, ApiCheckUserDataExist

app_name = 'api'
# DELETE_EXPIRED_TOKENS_INTERVAL = DjangoRestJwtRegistrationConfig.settings['DELETE_EXPIRED_TOKENS_INTERVAL']
urlpatterns = [

#     ##########User API################
#     path('register/', RegisterView.as_view(), name="register"),
#     path('login/', LoginAPIView.as_view(), name="login"),
#     path('logout/', LogoutAPIView.as_view(), name="logout"),
#     path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('request-reset-email/', RequestPasswordResetEmail.as_view(),
#          name="request-reset-email"),
#     path('password-reset/<uidb64>/<token>/',
#          PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
#     path('password-reset-complete', SetNewPasswordAPIView.as_view(),
#          name='password-reset-complete'),
#     path('user/singup/check/data/<str:data>/', ApiCheckUserDataExist, name='ApiCheckUserDataExist'),
#     path('code/<str:coupon>/', ApiPromoCodeClient, name='ApiPromoCodeClient'),
#
# ########## Notification   #########
#
#     path('notification/', AdminApiNotificationList, name='AdminApiNotificationList'),
#
#     ########## localization   #########
#
#     path('lang/', LanguageListAPIView.as_view(), name='AdminLanguageApiListView'),

    # ##################### Blog API ########################
    # path('blog/category/', blog.BlogCategoriesList.as_view(), name='AdminBlogCategoriesAPiList'),
    # path('blog/category/<int:pk>/', blog.BlogCategoriesDetail.as_view(), name='AdminBlogCategoriesAPiList'),
    # path('blog/tag/', blog.BlogTagsList.as_view(), name='AdminBlogTagsAPiList'),
    # path('blog/tag/<int:pk>/', blog.BlogTagsDetail.as_view(), name='AdminBlogTagsAPiList'),
    # path('blog/service/', blog.BlogServicesList.as_view(), name='AdminBlogServicesAPiList'),
    # path('blog/service/<int:pk>/', blog.BlogServicesDetail.as_view(), name='AdminBlogServicesAPiList'),
    # path('blog/article/', blog.BlogArticleList.as_view(), name='AdminBlogArticleAPiList'),
    # path('blog/article/<int:pk>/', blog.BlogArticleDetail.as_view(), name='AdminBlogArticleAPiList'),

    ##################### Sport API ########################
    path('sport/category/', sport.SportCategoryList.as_view(), name='AdminSportCategoryAPiList'),
    path('sport/category/<int:pk>/', sport.SportCategoryDetail.as_view(), name='AdminSportCategoryAPiList'),
    path('sport/sport/', sport.AdminSportSerializerList.as_view(), name='AdminSportAPiList'),
    path('sport/sport/<int:pk>/', sport.AdminSportSerializerDetail.as_view(), name='AdminSportAPiList'),
    path('sport/leagues/', sport.AdminLeaguesSerializerList.as_view(), name='AdminLeaguesAPiList'),
    path('sport/leagues/<int:pk>/', sport.AdminLeaguesSerializerDetail.as_view(), name='AdminLeaguesAPiList'),
    path('sport/season/', sport.AdminSeasonSerializerList.as_view(), name='AdminSeasonAPiList'),
    path('sport/season/<int:pk>/', sport.AdminSeasonSerializerDetail.as_view(), name='AdminSeasonAPiList'),
    path('sport/stages/', sport.AdminStagesSerializerList.as_view(), name='AdminStagesAPiList'),
    path('sport/stages/<int:pk>/', sport.AdminStagesSerializerDetail.as_view(), name='AdminStagesAPiList'),
    path('sport/group/', sport.AdminGroupSerializerList.as_view(), name='AdminGroupAPiList'),
    path('sport/group/<int:pk>/', sport.AdminGroupSerializerDetail.as_view(), name='AdminGroupAPiList'),
    path('sport/aggregate/', sport.AdminAggregateSerializerList.as_view(), name='AdminAggregateAPiList'),
    path('sport/aggregate/<int:pk>/', sport.AdminAggregateSerializerDetail.as_view(), name='AdminAggregateAPiList'),
    path('sport/round/', sport.AdminRoundSerializerList.as_view(), name='AdminRoundAPiList'),
    path('sport/round/<int:pk>/', sport.AdminRoundSerializerDetail.as_view(), name='AdminRoundAPiList'),
    path('sport/venues/', sport.AdminVenuesSerializerList.as_view(), name='AdminVenuesAPiList'),
    path('sport/venues/<int:pk>/', sport.AdminVenuesSerializerDetail.as_view(), name='AdminVenuesAPiList'),
    path('sport/state/', sport.AdminSportStateSerializerList.as_view(), name='AdminSportStateAPiList'),
    path('sport/state/<int:pk>/', sport.AdminSportStateSerializerDetail.as_view(), name='AdminSportStateAPiList'),
    path('sport/fixtures/', sport.AdminFixturesSerializerList.as_view(), name='AdminFixturesAPiList'),
    path('sport/fixtures/<int:pk>/', sport.AdminFixturesSerializerDetail.as_view(), name='AdminFixturesAPiList'),
    path('sport/livescores/', sport.AdminLiveScoresSerializerList.as_view(), name='AdminLiveScoresAPiList'),
    path('sport/livescores/<int:pk>/', sport.AdminLiveScoresSerializerDetail.as_view(), name='AdminLiveScoresAPiList'),
    path('sport/clubs/', sport.AdminClubsSerializerList.as_view(), name='AdminClubsAPiList'),
    path('sport/clubs/<int:pk>/', sport.AdminClubsSerializerDetail.as_view(), name='AdminClubsAPiList'),
    path('sport/teams/', sport.AdminTeamsSerializerList.as_view(), name='AdminTeamsAPiList'),
    path('sport/teams/<int:pk>/', sport.AdminTeamsSerializerDetail.as_view(), name='AdminTeamsAPiList'),
    path('sport/statistics/', sport.AdminStatisticsSerializerList.as_view(), name='AdminStatisticsAPiList'),
    path('sport/statistics/<int:pk>/', sport.AdminStatisticsSerializerDetail.as_view(), name='AdminStatisticsAPiList'),
    path('sport/standings/', sport.AdminStandingsSerializerList.as_view(), name='AdminStandingsAPiList'),
    path('sport/standings/<int:pk>/', sport.AdminStandingsSerializerDetail.as_view(), name='AdminStandingsAPiList'),
    path('sport/livestandings/', sport.AdminLiveStandingsSerializerList.as_view(), name='AdminLiveStandingsAPiList'),
    path('sport/livestandings/<int:pk>/', sport.AdminLiveStandingsSerializerDetail.as_view(), name='AdminLiveStandingsAPiList'),
    path('sport/schedules/', sport.AdminSchedulesSerializerList.as_view(), name='AdminSchedulesAPiList'),
    path('sport/schedules/<int:pk>/', sport.AdminSchedulesSerializerDetail.as_view(), name='AdminSchedulesAPiList'),
    path('sport/players/', sport.AdminPlayersSerializerList.as_view(), name='AdminPlayersAPiList'),
    path('sport/players/<int:pk>/', sport.AdminPlayersSerializerDetail.as_view(), name='AdminPlayersAPiList'),
    path('sport/squads/', sport.AdminSquadsSerializerList.as_view(), name='AdminSquadsAPiList'),
    path('sport/squads/<int:pk>/', sport.AdminSquadsSerializerDetail.as_view(), name='AdminSquadsAPiList'),
    path('sport/tVstations/', sport.AdminTVStationsSerializerList.as_view(), name='AdminTVstationsAPiList'),
    path('sport/tVstations/<int:pk>/', sport.AdminTVStationsSerializerDetail.as_view(), name='AdminTVstationsAPiList'),
    path('sport/coaches/', sport.AdminCoachesSerializerList.as_view(), name='AdminCoachesAPiList'),
    path('sport/coaches/<int:pk>/', sport.AdminCoachesSerializerDetail.as_view(), name='AdminCoachesAPiList'),
    path('sport/topscorers/', sport.AdminTopScorersSerializerList.as_view(), name='AdminTopScorersAPiList'),
    path('sport/topscorers/<int:pk>/', sport.AdminTopScorersSerializerDetail.as_view(), name='AdminTopScorersAPiList'),
    path('sport/rivals/', sport.AdminRivalsSerializerList.as_view(), name='AdminRivalsAPiList'),
    path('sport/rivals/<int:pk>/', sport.AdminRivalsSerializerDetail.as_view(), name='AdminRivalsAPiList'),
    path('sport/commentaries/', sport.AdminCommentariesSerializerList.as_view(), name='AdminCommentariesAPiList'),
    path('sport/commentaries/<int:pk>/', sport.AdminCommentariesSerializerDetail.as_view(), name='AdminCommentariesAPiList'),
    path('sport/referees/', sport.AdminRefereesSerializerList.as_view(), name='AdminRefereesAPiList'),
    path('sport/referees/<int:pk>/', sport.AdminRefereesSerializerDetail.as_view(), name='AdminRefereesAPiList'),
    path('sport/transfers/', sport.AdminTransfersSerializerList.as_view(), name='AdminTransfersAPiList'),
    path('sport/transfers/<int:pk>/', sport.AdminTransfersSerializerDetail.as_view(), name='AdminTransfersAPiList'),
    path('sport/prematchodds/', sport.AdminPreMatchOddsSerializerList.as_view(), name='AdminPreMatchOddsAPiList'),
    path('sport/prematchodds/<int:pk>/', sport.AdminPreMatchOddsSerializerDetail.as_view(), name='AdminPreMatchOddsAPiList'),
    path('sport/inplayodds/', sport.AdminInPlayOddsSerializerList.as_view(), name='AdminInPlayOddsAPiList'),
    path('sport/inplayodds/<int:pk>/', sport.AdminInPlayOddsSerializerDetail.as_view(), name='AdminInPlayOddsAPiList'),
    path('sport/markets/', sport.AdminMarketsSerializerList.as_view(), name='AdminMarketsAPiList'),
    path('sport/markets/<int:pk>/', sport.AdminMarketsSerializerDetail.as_view(), name='AdminMarketsAPiList'),
    path('sport/bookmakers/', sport.AdminBookmakersSerializerList.as_view(), name='AdminBookmakersAPiList'),
    path('sport/bookmakers/<int:pk>/', sport.AdminBookmakersSerializerDetail.as_view(), name='AdminBookmakersAPiList'),
    path('sport/match/', sport.AdminMatchSerializerList.as_view(), name='AdminMatchAPiList'),
    path('sport/match/<int:pk>/', sport.AdminMatchSerializerDetail.as_view(), name='AdminMatchAPiList'),
    path('sport/matchteamplayer/', sport.AdminMatchTeamPlayerSerializerList.as_view(), name='AdminMatchTeamPlayerAPiList'),
    path('sport/matchteamplayer/<int:pk>/', sport.AdminMatchTeamPlayerSerializerDetail.as_view(), name='AdminMatchTeamPlayerAPiList'),










]
# scheduler.interval(UserToken.objects.delete_expired_tokens, DELETE_EXPIRED_TOKENS_INTERVAL)
