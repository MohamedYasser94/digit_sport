from django.urls import path

from api.v1.views import chat as api_chat
from core.templatetags.social_share import post_to_facebook
from core.utils import utils
from core.utils.export import export_model
from core.views import activity, billing, blog, chat, people, core,emails, front, localization, notifications, payment, \
    social, users, utilities

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
    path('log/<str:model>', activity.AdminActivityLog, name="AdminActivityLog"),
    path('fb/whatsapp/webhooks/', activity.AdminFaceBookWhatsappWebHooks.as_view(),
         name="AdminFaceBookWhatsappWebHooks"),



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
    path('blog/article/detail/<slug:slug>/', blog.AdminBlogArticleDetails, name='AdminBlogArticleDetails'),
    path('blog/article/update/<slug:slug>/', blog.AdminBlogArticleUpdate, name='AdminBlogArticleUpdate'),
    path('blog/article/archive/<slug:slug>/', blog.AdminBlogArticleArchive, name='AdminBlogArticleArchive'),
    path('blog/article/delete/<slug:slug>/', blog.AdminBlogArticleDelete, name='AdminBlogArticleDelete'),
    path('blog/article/images/delete/<slug:slug>/', blog.AdminApiBlogArticleImageDelete, name='AdminApiBlogArticleImageDelete'),
    path('blog/post_to_facebook_url/', post_to_facebook, name='post_to_facebook_url'),

    ########## Services Admin #########
    path('blog/Service/', blog.AdminBlogServicesList, name='AdminBlogServicesList'),
    path('blog/Service/add/', blog.BlogServicesCreate, name='AdminBlogServicesCreate'),
    path('blog/Service/detail/<slug:slug>/', blog.BlogServicesDetail, name='AdminBlogServicesDetails'),
    path('blog/Service/update/<slug:slug>/', blog.BlogServicesUpdate, name='AdminBlogServicesUpdate'),
    path('blog/Service/delete/<slug:slug>/', blog.BlogServicesDelete, name='AdminBlogServicesDelete'),
    path('blog/article/images/delete/<slug:slug>/', blog.AdminApiBlogServicesImageDelete,
         name='AdminApiBlogServicesImageDelete'),

    ########## Inbox Admin #########
    path('inbox/all/<slug:slug>/', emails.AdminEmailList, name='AdminInbox'),
    path('inbox/<slug:slug>/compose/', emails.AdminUserComposeEmail, name='AdminUserComposeEmail'),
    path('inbox/details/<slug:slug>/', emails.AdminDetailsEmail, name='AdminEmailDetails'),
    # path('inbox/<slug:slug>/reply/', emils.AdminReplyEmail, name='AdminReplyEmail'),
    # path('inbox/<slug:slug>/forward/', emils.AdminForwardEmail, name='AdminForwardEmail'),
    # path('inbox/<slug:slug>/delete/', emils.AdminDeleteEmail, name='AdminDeleteEmail'),
    # path('inbox/<slug:slug>/archive/', emils.AdminArchiveEmail, name='AdminArchiveEmail'),
    # path('inbox/<slug:slug>/spam/', emils.AdminSpamEmail, name='AdminSpamEmail'),
    # path('inbox/<slug:slug>/trash/', emils.AdminTrashEmail, name='AdminTrashEmail'),
    # path('inbox/<slug:slug>/restore/', emils.AdminRestoreEmail, name='AdminRestoreEmail'),
    # path('inbox/<slug:slug>/mark_as_read/', emils.AdminMarkAsReadEmail, name='AdminMarkAsReadEmail'),
    # path('inbox/<slug:slug>/mark_as_unread/', emils.AdminMarkAsUnReadEmail, name='AdminMarkAsUnReadEmail'),
    # path('inbox/<slug:slug>/mark_as_important/', emils.AdminMarkAsImportantEmail, name='AdminMarkAsImportantEmail'),
    # path('inbox/<slug:slug>/mark_as_not_important/', emils.AdminMarkAsNotImportantEmail,
    #         name='AdminMarkAsNotImportantEmail'),
    # path('inbox/<slug:slug>/mark_as_starred/', emils.AdminMarkAsStarredEmail, name='AdminMarkAsStarredEmail'),
    # path('inbox/<slug:slug>/mark_as_unstarred/', emils.AdminMarkAsUnStarredEmail, name='AdminMarkAsUnStarredEmail'),
    # path('inbox/<slug:slug>/mark_as_spam/', emils.AdminMarkAsSpamEmail, name='AdminMarkAsSpamEmail'),
    # path('inbox/<slug:slug>/mark_as_not_spam/', emils.AdminMarkAsNotSpamEmail, name='AdminMarkAsNotSpamEmail'),


    ########## Users Admin #########
    path('user/', users.AdminUsersList, name='AdminUserList'),
    path('user/detail/<slug:slug>/', users.AdminUserDetail, name='AdminDetailUser'),
    path('user/update/<slug:slug>', users.AdminUserUpdate, name='AdminUserUpdate'),
    path('user/delete/<slug:slug>/', users.AdminUserDelete, name='AdminUserDelete'),
    path('user/setting/<slug:slug>/', users.AdminUserAccountSettings, name='AdminUserAccountSettings'),
    path('user/profile/<slug:slug>/', users.UserPublicProfile, name='UserPublicProfile'),
    path('user/password/<slug:slug>/', users.AdminUserChangePassword, name='AdminUserChangePassword'),
    path('user/deactivate/<slug:slug>/', users.AdminUserDeactivate, name='AdminDeactivateUser'),
    path('user/statements/<slug:slug>', users.UserStatements, name='UserStatements'),
    path('user/billing/<slug:slug>', users.UserBilling, name='UserBilling'),
    path('user/referrals/<slug:slug>', users.UserReferrals, name='UserReferrals'),
    path('dark/', users.UserDarkModeUpdate, name='UserDarkModeUpdate'),
    path('user/geo/', users.AdminUsersGeoInfoList, name='AdminUsersGeoInfoList'),
    path('user/newsletter/', users.AdminUsersNewsletterList, name='AdminUserNewsletter'),
    path('user/contact/', users.AdminClientContactList, name='AdminClientContactList'),
    path('user/contact/detail/<slug:slug>/', users.AdminClientContactDetail, name='AdminClientContactDetails'),
    path('groups/', users.AdminUserGroupList, name='AdminUserGroupList'),
    path('groups/create/', users.AdminUserGroupCreate, name='AdminUserGroupCreate'),
    path('groups/edit/<int:pk>', users.AdminUserGroupEdit, name='AdminUserGroupUpdate'),
    path('groups/delete/<int:id>', users.AdminUserGroupDelete, name='AdminUserGroupDelete'),

    #################### Social ###################
    path('follower/<slug:slug>', social.AdminUserFollower, name='UserFollower'),
    path('follower/remove/<slug:slug>', social.remove_friend, name='UserRemoveFollower'),
    path('follower/send/<slug:slug>', social.send_friend_request, name='UserSendFollow'),
    path('follower/cancel/<slug:slug>', social.cancel_friend_request, name='UserCancelFollower-request-cancel'),
    path('follower/request/<slug:slug>', social.friend_requests, name='UserRequestsFollower'),
    path('follower/accept/<slug:slug>', social.accept_friend_request, name='UserAcceptFollower'),
    path('follower/decline/<slug:slug>', social.decline_friend_request, name='UserDeclineFollower'),

    ########## Clients Admin #########
    path('people/', people.AdminClientList, name='AdminClientList'),
    path('people/deatail/<slug:slug>/', people.AdminClientDetail, name='AdminClientDetails'),
    path('people/update/<slug:slug>/', people.AdminClientUpdate, name='AdminClientUpdate'),
    path('people/delete/<slug:slug>/', people.AdminClientDelete, name='AdminClientDelete'),

    path('contact/', people.AdminContactList, name='AdminContactList'),
    ########## Driver Admin #########
    path('driver/', people.AdminDriverList, name='AdminDriverList'),
    path('driver/add/', people.AdminDriverList, name='AdminDriverCreate'),
    path('driver/deatail/<slug:slug>/', people.AdminDriverDetails, name='AdminDriverDetails'),
    path('driver/update/<slug:slug>/', people.AdminDriverUpdate, name='AdminDriverUpdate'),
    path('driver/delete/<slug:slug>/', people.AdminDriverDelete, name='AdminDriverDelete'),
    ########## Employee Admin #########
    path('admin/employee/', people.AdminEmployeeList, name='AdminEmployeeList'),
    path('admin/employee/deatail/<slug:slug>/', people.AdminEmployeeDetails, name='AdminEmployeeDetails'),
    path('admin/employee/update/<slug:slug>/', people.AdminEmployeeUpdate, name='AdminEmployeeUpdate'),
    path('admin/employee/archive/<slug:slug>/', people.AdminDriverArchive, name='AdminDriverArchive'),
    ########## Employee Admin #########
    path('admin/employee/salary/add/<slug:slug>/', people.AdminEmployeeSalaryCreate, name='AdminEmployeeSalaryCreate'),
    path('admin/employee/salary/update/<slug:slug>/', people.AdminEmployeeSalaryUpdate,
         name='AdminEmployeeSalaryUpdate'),


########## Team Admin #########
    path('branch/', people.AdminBranchList, name='AdminBranchList'),
    path('branch/deatail/<slug:slug>/', people.AdminTeamDetails, name='AdminBranchDetails'),
    path('branch/update/<slug:slug>/', people.AdminTeamUpdate, name='AdminBranchUpdate'),
    path('branch/delete/<slug:slug>/', people.AdminTeamArchive, name='AdminBranchDelete'),

    ########## Team Admin #########
    path('team/', people.AdminTeamList, name='AdminTeamList'),
    path('team/add/', people.AdminTeamCreate, name='AdminTeamCreate'),
    path('team/deatail/<slug:slug>/', people.AdminTeamDetails, name='AdminTeamDetails'),
    path('team/update/<slug:slug>/', people.AdminTeamUpdate, name='AdminTeamUpdate'),
    path('team/delete/<slug:slug>/', people.AdminTeamArchive, name='AdminTeamArchive'),

    #############################Admin Invoice Urls############################################
    ########## invoice Admin #########
    path('invoice/', billing.AdminInvoiceList, name='AdminInvoiceList'),
    path('invoice/detail/<slug:slug>/', billing.AdminInvoiceDetails, name='AdminInvoiceDetails'),
    path('invoice/pdf/<slug:slug>/', billing.AdminInvoicePDF, name='AdminInvoicePDF'),

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

    ########## Slider   #########
    path('testimonials/', front.AdminTestimonialsList, name='AdminTestimonialsList'),
    path('testimonials/<slug:slug>/', front.AdminTestimonialsDetail, name='AdminTestimonialsDetails'),
    path('testimonials/edit/<slug:slug>/', front.AdminTestimonialsUpdate, name='AdminTestimonialsUpdate'),
    path('testimonials/delete/<slug:slug>/', front.AdminTestimonialsArchive, name='AdminTestimonialsArchive'),

    ########## Slider   #########
    path('slider', front.SliderView.as_view(), name='AdminSliderList'),
    path('slider/add/', front.SliderCreate.as_view(), name='AdminSliderCreate'),
    path('slider/<int:pk>/', front.SliderDetailView.as_view(), name='AdminSliderDetails'),
    path('slider/edit/<int:pk>/', front.SliderEdit.as_view(), name='AdminSliderUpdate'),
    path('slider/delete/<int:pk>/', front.SliderDelete.as_view(), name='AdminSliderDelete'),

    ########## Banners   #########
    path('banner', front.BannersView.as_view(), name='AdminBannerList'),
    path('banner/add/', front.BannerCreate, name='AdminBannerCreate'),
    path('banner/<int:pk>/', front.BannerDetailView.as_view(), name='AdminBannerDetails'),
    path('banner/edit/<int:pk>/', front.BannerEdit.as_view(), name='AdminBannerUpdate'),
    path('banner/delete/<int:pk>/', front.BannerDelete.as_view(), name='AdminBannerDelete'),
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

    ########## Coupon Admin #########
    path('coupon/', utilities.AdminCouponList, name='AdminCouponList'),
    path('coupon/detail/<slug:slug>/', utilities.AdminCouponDetails, name='AdminCouponDetails'),
    path('coupon/update/<slug:slug>/', utilities.AdminCouponUpdate, name='AdminCouponUpdate'),
    path('coupon/delete/<slug:slug>/', utilities.AdminCouponDelete, name='AdminCouponDelete'),

    ########## Membership Admin #########
    path('membership/', utilities.AdminMembershipList, name='AdminMembershipList'),
    path('membership/detail/<slug:slug>/', utilities.AdminMembershipDetails, name='AdminMembershipDetails'),
    path('membership/update/<slug:slug>/', utilities.AdminMembershipUpdate, name='AdminMembershipUpdate'),
    path('membership/archive/<slug:slug>/', utilities.AdminMembershipArchive, name='AdminMembershipArchive'),
    path('membership/delete/<slug:slug>/', utilities.AdminMembershipArchive, name='AdminMembershipDelete'),

    ########## Subscription Admin #########
    path('subscription/', utilities.AdminSubscriptionList, name='AdminSubscriptionList'),
    path('subscription/detail/<slug:slug>/', utilities.AdminSubscriptionDetails, name='AdminSubscriptionDetails'),
    path('subscription/update/<slug:slug>/', utilities.AdminSubscriptionUpdate, name='AdminSubscriptionUpdate'),
    path('subscription/archive/<slug:slug>/', utilities.AdminSubscriptionArchive, name='AdminSubscriptionArchive'),

    ########## Subscription Payment Admin #########
    path('subscriptionpayment/', utilities.AdminSubscriptionPaymentList, name='AdminSubscriptionPaymentList'),

    path('subscriptionpayment/detail/<slug:slug>/', utilities.AdminSubscriptionDetails,
         name='AdminSubscriptionPaymentDetails'),
    path('subscriptionpayment/update/<slug:slug>/', utilities.AdminSubscriptionUpdate,
         name='AdminSubscriptionPaymentUpdate'),
    path('subscriptionpayment/archive/<slug:slug>/', utilities.AdminSubscriptionArchive,
         name='AdminSubscriptionPaymentArchive'),

    ############# PayMent ##################
    path('payment/gateway/', payment.AdminPaymentGatewayList, name='AdminPaymentGatewayList'),


    ###############Utility Admin ###############
    path('export_model', export_model, name='AdminExportModel'),

    ########## Chat Admin #########
    path('room/', chat.rooms, name='rooms'),
    path('room/<uuid:pk>/', chat.room, name='room'),
    path('room/create/', chat.create_room, name='create_room'),
    path('room/edit/<uuid:pk>/', chat.edit_room, name='edit_room'),
    path('room/delete/<uuid:pk>/', chat.delete_room, name='delete_room'),

    ################ Chat ######################
    path('messenger/', chat.AdminChatMessenger, name='AdminChatMessenger'),
    path('messenger/friend/', chat.AdminChatDrawer, name='AdminChatDrawer'),

    path('<user_id>/', chat.account_view, name="UserView"),
    path('messenger/chat/', api_chat.private_chat_room_view, name='AdminApiPrivateChatRoom'),
    path('messenger/chat/private/', api_chat.create_or_return_private_chat, name='AdminApiPrivateChat'),

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



    ########### Otp Url ############
    # path('api/otp/setup/', ApiAdminOtpSetupView, name='ApiAdminOtpSetupView'),
    # path('api/otp/qrcode/', ApiAdminOtpQrCodeView, name='ApiAdminOtpQrCodeView'),
    # path('otp/setup/', AdminOtpSetupView.as_view(), name='AdminOtpSetupView'),
    # path('api/otp/otp/', ApiAdminOtpCodeView, name='ApiAdminOtpCodeView'),
    # path('api/otp/verify/', ApiAdminOtpVerifyView, name='ApiAdminOtpVerifyView'),

]
