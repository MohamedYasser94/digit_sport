from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView


from api.v1.views.blog import BlogArticleList, BlogArticleDetail, BlogCategoriesList, BlogCategoriesDetail, \
    BlogTagsDetail, BlogTagsList, BlogServicesList, BlogServicesDetail
from api.v1.views.catalog import APiGetProductVariant, AdminPosCategoryProducts, AdminPosSubCategories, \
    AdminPosSubCategory, AdminPosAllProducts
from api.v1.views.chat import AdminApiChatRoomCheck, AdminApiChatRoomGetMessage
from api.v1.views.client import AdminApiClients, AdminApiClient
from api.v1.views.core import AdminCommonClientProfile
from api.v1.views.localization import LanguageListAPIView
from api.v1.views.notification import AdminApiNotificationList
from api.v1.views.order import AdminAddProductToCashier, AdminPosCashierItemIncrement, \
    AdminPosCashierItems, AdminPosUpdateCashierOrder, AdminCashierClientProfile, AdminPosDraftCashierOrder, \
    AdminPosUpdateCashierDraft, AdminPosGetCashierDraft, AdminPosCashPayment
from api.v1.views.pos import cash, AdminPosRefreshPage, AdminPosPrintOrder
from api.v1.views.purchase import APiGetPurchaseProduct
from api.v1.views.transaction import  card_payment, AdminPosPayment
from api.v1.views.user import RegisterView, LoginAPIView, LogoutAPIView, VerifyEmail, RequestPasswordResetEmail, \
    PasswordTokenCheckAPI, SetNewPasswordAPIView, ApiPromoCodeClient,  ApiCheckUserDataExist
from api.v1.views.wallet import ApiWalletRequestResetCode
from apps.catalog.api.api import category_list_api, category_details_api, CategoryListAPi, ProductsListApi, ProductsApi, \
    CategoryApi

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
    path('blog/category/', BlogCategoriesList.as_view(), name='AdminBlogCategoriesAPiList'),
    path('blog/category/<int:pk>/', BlogCategoriesDetail.as_view(), name='AdminBlogCategoriesAPiList'),
    path('blog/tag/', BlogTagsList.as_view(), name='AdminBlogTagsAPiList'),
    path('blog/tag/<int:pk>/', BlogTagsDetail.as_view(), name='AdminBlogTagsAPiList'),
    path('blog/service/', BlogServicesList.as_view(), name='AdminBlogServicesAPiList'),
    path('blog/service/<int:pk>/', BlogServicesDetail.as_view(), name='AdminBlogServicesAPiList'),
    path('blog/article/', BlogArticleList.as_view(), name='AdminBlogArticleAPiList'),
    path('blog/article/<int:pk>/', BlogArticleDetail.as_view(), name='AdminBlogArticleAPiList'),

    ############### Chat ############

        path('room/<slug:slug>', AdminApiChatRoomCheck, name='AdminApiChatRoomCheck'),
        path('room/chat/<slug:slug>', AdminApiChatRoomGetMessage, name='AdminApiChatRoomGetMessage'),

    ########## Catalog API #########
    path('api/category', category_list_api, name='category_list_api'),
    path('api/category/<int:id>', category_details_api, name='category_details_api'),
    path('admin/api/category', category_list_api, name='category_list_api'),

    path('api/v2/catalog/category', CategoryListAPi.as_view(), name='CategoryListAPi'),
    path('api/v2/catalog/category/<int:id>', CategoryApi.as_view(), name='CategoryAPi'),
    path('api/v2/catalog/products/', ProductsListApi.as_view(), name='ProductsListAPi'),
    path('api/v2/category/product/<int:id>', ProductsApi.as_view(), name='ProductsAPi'),

    ########## purchase Admin API #########
    path('catlog/purchase/items/<str:product_code>/', APiGetPurchaseProduct, name='APiGetPurchaseProduct'),

    ########## Product Home API #########
    path('catlog/product/variant/<str:variant_code>/', APiGetProductVariant, name='APiGetProductVariant'),
    ######################### Wallet Admin Api #####################
    path('core/wallet/reset/<int:user_id>/', ApiWalletRequestResetCode, name='ApiWalletRequestResetCode'),


    ######################### Clients Admin Api #####################
    path('core/clients/', AdminApiClients, name='AdminApiClients'),
    path('core/clients/<int:client_id>/', AdminApiClient, name='AdminApiClient'),

    #################### Core Admin Api ####################
    path('core/people/profile/<int:profile_id>/', AdminCommonClientProfile, name='AdminCommonClientProfile'),

    ################### POS Admin API ###########################
    path('pos/category/', AdminPosSubCategories, name='AdminPosSubCategories'),
    path('pos/category/<int:category_id>/', AdminPosSubCategory, name='AdminPosSubCategory'),
    path('pos/products/', AdminPosAllProducts, name='AdminPosAllProducts'),
    path('pos/products/<int:category_id>/', AdminPosCategoryProducts, name='AdminPosCategoryProducts'),
    path('pos/cashier/item/<int:item_id>/', AdminAddProductToCashier, name='AdminAddProductToCashier'),
    path('pos/cashier/update/', AdminPosUpdateCashierOrder, name='AdminPosUpdateCashierOrder'),
    path('pos/cashier/draft/<int:order_id>/', AdminPosDraftCashierOrder, name='AdminPosDraftCashierOrder'),
    path('pos/cashier/draft/update/', AdminPosUpdateCashierDraft, name='AdminPosUpdateCashierDraft'),
    path('pos/cashier/draft/get/<str:order_code>', AdminPosGetCashierDraft, name='AdminPosGetCashierDraft'),
    path('pos/cashier/', AdminPosCashierItems, name='AdminPosCashierItems'),
    path('pos/orderitem/<int:item_id>/', AdminAddProductToCashier, name='AdminPosCurrentOrderItem'),
    path('pos/cashier/quantity/<int:item_id>/', AdminPosCashierItemIncrement, name='AdminPosCashierItemIncrement'),
    path('pos/cashier/people/profile/<int:client_id>/', AdminCashierClientProfile, name='AdminCashierClientProfile'),
    path('pos/refreshpage/', AdminPosRefreshPage, name='AdminPosRefreshPage'),
    ################### POS Finish API ###########################

    path('pos/printorder/<int:order_id>/', AdminPosPrintOrder, name='AdminPosPrintOrder'),
    path('pos/pay/cash/<int:order_id>/', AdminPosCashPayment, name='AdminPosCashPayment'),

    path('pos/pay/cash/', AdminPosPayment, name='AdminPosPayment'),

    path('pos/cash/<int:amount>', cash, name='AdminPosCash'),

    path('pos/pay/card/', card_payment, name='api_card_payment'),





]
# scheduler.interval(UserToken.objects.delete_expired_tokens, DELETE_EXPIRED_TOKENS_INTERVAL)
