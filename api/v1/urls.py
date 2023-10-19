from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api.v1.views import billing, sport,blog
from api.v1.views.localization import LanguageListAPIView
from api.v1.views.notification import AdminApiNotificationList
from api.v1.views.user import RegisterView, LoginAPIView, LogoutAPIView, VerifyEmail, RequestPasswordResetEmail, \
    PasswordTokenCheckAPI, SetNewPasswordAPIView, ApiPromoCodeClient, ApiCheckUserDataExist

app_name = 'api'
# DELETE_EXPIRED_TOKENS_INTERVAL = DjangoRestJwtRegistrationConfig.settings['DELETE_EXPIRED_TOKENS_INTERVAL']
urlpatterns = [

    ##########User API################
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(),
         name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/',
         PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', SetNewPasswordAPIView.as_view(),
         name='password-reset-complete'),
    path('user/singup/check/data/<str:data>/', ApiCheckUserDataExist, name='ApiCheckUserDataExist'),
    path('code/<str:coupon>/', ApiPromoCodeClient, name='ApiPromoCodeClient'),

########## Notification   #########

    path('notification/', AdminApiNotificationList, name='AdminApiNotificationList'),

    ########## localization   #########

    path('lang/', LanguageListAPIView.as_view(), name='AdminLanguageApiListView'),

    ##################### Blog API ########################
    path('blog/category/', blog.BlogCategoriesList.as_view(), name='AdminBlogCategoriesAPiList'),
    path('blog/category/<int:pk>/', blog.BlogCategoriesDetail.as_view(), name='AdminBlogCategoriesAPiList'),
    path('blog/tag/', blog.BlogTagsList.as_view(), name='AdminBlogTagsAPiList'),
    path('blog/tag/<int:pk>/', blog.BlogTagsDetail.as_view(), name='AdminBlogTagsAPiList'),
    path('blog/service/', blog.BlogServicesList.as_view(), name='AdminBlogServicesAPiList'),
    path('blog/service/<int:pk>/', blog.BlogServicesDetail.as_view(), name='AdminBlogServicesAPiList'),
    path('blog/article/', blog.BlogArticleList.as_view(), name='AdminBlogArticleAPiList'),
    path('blog/article/<int:pk>/', blog.BlogArticleDetail.as_view(), name='AdminBlogArticleAPiList'),

    ##################### Sport API ########################
    path('sport/category/', sport.SportCategoryList.as_view(), name='AdminSportCategoryAPiList'),
    path('sport/category/<int:pk>/', sport.SportCategoryDetail.as_view(), name='AdminSportCategoryAPiList'),
    path('sport/sport/', sport.AdminSportSerializerList.as_view(), name='AdminSportAPiList'),
    path('sport/sport/<int:pk>/', sport.AdminSportSerializerDetail.as_view(), name='AdminSportAPiList'),
    path('sport/leagues/', sport.AdminLeaguesSerializerList.as_view(), name='AdminLeaguesAPiList'),
    path('sport/leagues/<int:pk>/', sport.AdminLeaguesSerializerDetail.as_view(), name='AdminLeaguesAPiList'),








]
# scheduler.interval(UserToken.objects.delete_expired_tokens, DELETE_EXPIRED_TOKENS_INTERVAL)
