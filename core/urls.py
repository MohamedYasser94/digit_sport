from django.urls import path
from django.views.generic import TemplateView


from core.views import blog,  core,emails,  localization, notifications, \
     users, utilities

app_name = 'core'

urlpatterns = [

    path('', core.AdminIndex, name='AdminIndex'),
    path('login/', users.AdminLogin.as_view(), name='AdminLogin'),
    path('lockscreen', users.AdminLockscreen.as_view(), name='AdminLockscreen'),
    path('logout/', users.AdminLogout, name='AdminLogout'),
    path('notifications/', notifications.AdminNotificationslist, name='AdminNotificationsList'),
    path('notifications/<slug:slug>/', notifications.AdminNotificationsDetails, name='AdminNotificationsDetails'),
    path('403/', core.AdminError403, name='AdminError403'),
    path('404/', core.AdminError404, name='AdminError404'),




    ########## Blog Admin #########

    path('blog/', blog.BlogDashboard, name='AdminBlogDashboard'),
    path('blog/category/', blog.AdminBlogCategoriesList, name='AdminBlogCategoriesList'),
    path('blog/category/detail/<slug:slug>/', blog.AdminBlogCategoryDetails, name='AdminBlogCategoryDetails'),
    path('blog/category/update/<slug:slug>/', blog.AdminBlogCategoryUpdate, name='AdminBlogCategoryUpdate'),
    path('blog/category/archive/<slug:slug>/', blog.AdminBlogCategoryArchive, name='AdminBlogCategoryArchive'),
    path('blog/category/delete/<slug:slug>/', blog.AdminBlogCategoryDelete, name='AdminBlogCategoryDelete'),

    ########## Tags Admin #########
    path('blog/tags/', blog.AdminBlogTagsList, name='AdminBlogTagsList'),
    path('blog/tags/detail/<slug:slug>/', blog.AdminBlogTagsDetails, name='AdminBlogTagsDetails'),
    path('blog/tags/update/<slug:slug>/', blog.AdminBlogTagsUpdate, name='AdminBlogTagsUpdate'),
    path('blog/tags/archive/<slug:slug>/', blog.AdminBlogTagsArchive, name='AdminBlogTagsArchive'),
    path('blog/tags/delete/<slug:slug>/', blog.AdminBlogTagsDelete, name='AdminBlogTagsDelete'),

    ########## Blog Article Admin #########
    path('blog/article/', blog.AdminBlogArticleList, name='AdminBlogArticleList'),
    path('blog/article/add/', blog.AdminBlogArticleCreate, name='AdminBlogArticleCreate'),

    path('blog/article/sadd/', blog.AdminBlogArticleSCreate, name='AdminBlogArticleSCreate'),
    path('blog/article/detail/<slug:slug>/', blog.AdminBlogArticleDetails, name='AdminBlogArticleDetails'),
    path('blog/article/update/<slug:slug>/', blog.AdminBlogArticleUpdate, name='AdminBlogArticleUpdate'),
    path('blog/article/archive/<slug:slug>/', blog.AdminBlogArticleArchive, name='AdminBlogArticleArchive'),
    path('blog/article/delete/<slug:slug>/', blog.AdminBlogArticleDelete, name='AdminBlogArticleDelete'),
    path('blog/article/images/delete/<slug:slug>/', blog.AdminApiBlogArticleImageDelete, name='AdminApiBlogArticleImageDelete'),



########## Blog Video Admin #########
    path('blog/video/', blog.AdminBlogVideoList, name='AdminBlogVideoList'),
    path('blog/video/detail/<slug:slug>/', blog.AdminBlogArticleDetails, name='AdminBlogVideoDetails'),
    path('blog/video/update/<slug:slug>/', blog.AdminBlogArticleUpdate, name='AdminBlogVideoUpdate'),
    path('blog/video/archive/<slug:slug>/', blog.AdminBlogArticleArchive, name='AdminBlogVideoArchive'),
    path('blog/video/delete/<slug:slug>/', blog.AdminBlogArticleDelete, name='AdminBlogVideoDelete'),



    ########## Inbox Admin #########
    path('inbox/all/<slug:slug>/', emails.AdminEmailList, name='AdminInbox'),
    path('inbox/<slug:slug>/compose/', emails.AdminUserComposeEmail, name='AdminUserComposeEmail'),
    path('inbox/details/<slug:slug>/', emails.AdminDetailsEmail, name='AdminEmailDetails'),



    ########## Users Admin #########
    path('user/', users.AdminUsersList, name='AdminUserList'),
    path('user/detail/<slug:slug>/', users.AdminUserDetail, name='AdminDetailUser'),
    path('user/update/<slug:slug>', users.AdminUserUpdate, name='AdminUserUpdate'),
    path('user/delete/<slug:slug>/', users.AdminUserDelete, name='AdminUserDelete'),
    path('user/setting/<slug:slug>/', users.AdminUserAccountSettings, name='AdminUserAccountSettings'),

    path('user/password/<slug:slug>/', users.AdminUserChangePassword, name='AdminUserChangePassword'),
    path('user/deactivate/<slug:slug>/', users.AdminUserDeactivate, name='AdminDeactivateUser'),
    path('user/statements/<slug:slug>', users.UserStatements, name='UserStatements'),
    path('user/billing/<slug:slug>', users.UserBilling, name='UserBilling'),
    path('user/referrals/<slug:slug>', users.UserReferrals, name='UserReferrals'),
    path('dark/', users.UserDarkModeUpdate, name='UserDarkModeUpdate'),
    path('user/geo/', users.AdminUsersGeoInfoList, name='AdminUsersGeoInfoList'),
    path('user/fcmtoken/', users.AdminUsersFcmTokenList, name='AdminUsersFcmTokenList'),

    path('groups/', users.AdminUserGroupList, name='AdminUserGroupList'),
    path('groups/create/', users.AdminUserGroupCreate, name='AdminUserGroupCreate'),
    path('groups/edit/<int:pk>', users.AdminUserGroupEdit, name='AdminUserGroupUpdate'),
    path('groups/delete/<int:id>', users.AdminUserGroupDelete, name='AdminUserGroupDelete'),



    ########## Site Setting Admin #########
    path('site/', core.AdminSiteSettingList, name='AdminSiteSettingList'),

    path('site/detail/<slug:slug>/', core.AdminSiteSettingDetails, name='AdminSiteSettingDetails'),
    path('site/update/<slug:slug>/', core.AdminSiteSettingUpdate, name='AdminSiteSettingUpdate'),
    path('site/delete/<slug:slug>/', core.AdminSiteSettingDelete, name='AdminSiteSettingDelete'),

    ########## System Setting Admin #########
    path('setting/', core.AdminSystemSettingList, name='AdminSystemSettingList'),
    path('setting/detail/<slug:slug>/', core.AdminSystemSettingDetail, name='AdminSystemSettingDetails'),
    path('setting/update<slug:slug>/', core.AdminSystemSettingUpdate, name='AdminSystemSettingUpdate'),
    path('setting/delete/<slug:slug>/', core.AdminSystemSettingDelete, name='AdminSystemSettingDelete'),


    ########## localization   #########
    path('lang', localization.AdminLanguageList, name='AdminLanguageList'),
    path('lang/add/', localization.AdminLanguageCreate.as_view(), name='AdminLanguageCreate'),
    path('lang/update/<int:pk>/', localization.AdminLanguageUpdate.as_view(), name='AdminLanguageUpdate'),
    path('lang/delete/<int:pk>/', localization.AdminLanguageDelete.as_view(), name='AdminLanguageDelete'),
    path('lang/set/<str:code>/', localization.select_language, name='AdminUserSetLanguage'),

    path('country', localization.AdminCountryList, name='AdminCountryList'),
    path('country/update/<slug:slug>/', localization.AdminCountryUpdate, name='AdminCountryUpdate'),
    path('country/delete/<slug:slug>/', localization.AdminCountryDelete, name='AdminCountryDelete'),

    path('<slug:slug>/governorates/', localization.AdminGovernoratesList, name='AdminGovernoratesList'),
    path('<slug:slug>/governorates/update/<slug:g_slug>/', localization.GovernoratesUpdate,
         name='AdminGovernoratesUpdate'),
    path('<slug:slug>/governorates/delete/<slug:g_slug>/', localization.GovernoratesDelete,
         name='AdminGovernoratesDelete'),

    path('<slug:slug>/city/', localization.AdminCityList, name='AdminCityList'),
    path('<slug:slug>/city/update/<slug:c_slug>/', localization.AdminCityUpdate, name='AdminCityUpdate'),
    path('<slug:slug>/city/delete/<slug:c_slug>/', localization.AdminCityDelete, name='AdminCityDelete'),

    path('<slug:slug>/area/', localization.AdminAreaList, name='AdminAreaList'),
    path('<slug:slug>/area/update/<slug:a_slug>/', localization.AdminAreaUpdate, name='AdminAreaUpdate'),
    path('<slug:slug>/area/delete/<slug:a_slug>/', localization.AdminAreaDelete, name='AdminAreaDelete'),

    path('currency', localization.AdminCurrencyListView, name='AdminCurrencyList'),
    path('currency/add/', localization.AdminCurrencyCreate, name='AdminCurrencyCreate'),
    path('currency/<slug:slug>/', localization.AdminCurrencyDetails, name='AdminCurrencyDetails'),
    path('currency/update/<slug:slug>/', localization.AdminCurrencyUpdate, name='AdminCurrencyUpdate'),
    path('currency/delete/<slug:slug>/', localization.AdminCurrencyDelete, name='AdminCurrencyDelete'),

    # ########## Qr Code Admin #########
    path('qr/', utilities.AdminQrCodeList, name='AdminQrCodeList'),
    # path('qr/add/', AdminQrCodeCreate.as_view(), name='AdminCreateQrCode'),
    path('qr/detail/<slug:slug>/', utilities.AdminQrCodeDetails, name='AdminQrCodeDetails'),
    path('qr/update/<slug:slug>/', utilities.AdminQrCodeUpdate, name='AdminQrCodeUpdate'),
    path('qr/delete/<slug:slug>/', utilities.AdminQrCodeDelete, name='AdminQrCodeDelete'),




    ##########  Help  Admin #########
    path('help/documentation/', core.AdminHelpDocumentationList, name='AdminHelpDocumentationList'),
    path('help/faq/', core.AdminHelpFaqList, name='AdminHelpFaqList'),
    path('help/tutorial/', core.AdminHelpTutorialList, name='AdminHelpTutorialList'),

    ##########  Help Category Admin #########
    path('help/category/', core.AdminHelpCategoriesList, name='AdminHelpCategoriesList'),
    path('help/category/update/<slug:slug>/', core.AdminHelpCategoriesUpdate, name='AdminHelpCategoriesUpdate'),
    path('help/category/delete/<slug:slug>/', core.AdminHelpCategoriesDelete, name='AdminHelpCategoriesDelete'),
    ##########  Help Questions Admin #########

    path('help/questions/', core.AdminHelpQuestionsList, name='AdminHelpQuestionsList'),
    path('help/questions/add/', core.AdminCreateHelpQuestions, name='AdminHelpQuestionsCreate'),
    path('help/questions/detail/<slug:slug>/', core.AdminHelpQuestionsDetail, name='AdminHelpQuestionsDetails'),
    path('help/questions/update/<slug:slug>/', core.AdminHelpQuestionsUpdate, name='AdminHelpQuestionsUpdate'),
    path('help/questions/delete/<slug:slug>/', core.AdminHelpQuestionsDelete, name='AdminHelpQuestionsDelete'),



    ########### Bot Url ############


]
