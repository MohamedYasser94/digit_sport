from django.urls import path

from user.views.profile import UserProfile, address_list, load_cities, FrontUserProfile, FrontUpdateProfile, \
    FrontLoginUserProfile
from user.views.user import UserActivate, UserLogin, UserLogout, TestPages, \
    resend_activation_email, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, facebook_login, google_login, CustomerRegister

app_name = 'user'

urlpatterns = [

    # path('guest-user/', guest_user_view, title='guest_user_register'),

    ##########User################
    path('signup/', CustomerRegister, name='CustomerRegister'),
    path('login/', UserLogin.as_view(), name='CustomerLogin'),
    path('logout/', UserLogout, name='CustomerLogout'),
    path('activate/<uidb64>/<token>/', UserActivate, name='activate'),
    path('reactivate/', resend_activation_email, name='CustomerResendActivationEmail'),

    path('social/fb', facebook_login, name='CustomerFaceBookLogin'),
    path('social/google', google_login, name='CustomerGoogleLogin'),

    path('test/', TestPages, name='TestPages'),
    #

    ##################UserProfile#################
    path('user/profile/', FrontUserProfile, name='FrontUserProfile'),
    path('user/myprofile/<slug:slug>', FrontLoginUserProfile, name='FrontLoginUserProfile'),
    path('user/uproile/<slug:slug>', UserProfile, name='UpdateImage'),
    path('user/uprofile/<slug:slug>', FrontUpdateProfile, name='FrontUpdateProfile'),
    path('user/upsetting/<slug:slug>', UserProfile, name='UserSettingUpdate'),
    # path('user/upsetting/<slug:slug>', UserSettingUpdate, title='UserSettingUpdate'),  # <-- this one here
    # ###########Password###########
    #
    path('reset/', PasswordResetView.as_view(), name="FrontResetPassword"),
    path('reset/sent/', PasswordResetDoneView.as_view(), name="FrontPasswordResetDone"),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name="FrontPasswordResetConfirm"),
    path('reset/complete/', PasswordResetCompleteView.as_view(), name="FrontPasswordResetComplete"),

    ##########Address################
    path('user/booklist/', address_list, name='address_list'),
    # path('user/cadress/', CreateAddress, title='CreateAddress'),
    path('user/cadress/ajax/load-cities/', load_cities, name='ajax_load_cities'),  # <-- this one here
    # path('user/adress/<int:pk>', DeleteAddress, title='DeleteAddress'),
    # path('user/adress/<int:pk>', UpdateAddress, title='UpdateAddress'),

]
