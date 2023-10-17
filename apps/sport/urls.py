from django.urls import path

from apps.sport.api import api_views
from apps.sport.views import views, utils

app_name = 'sport'

urlpatterns = [

    ##########   Category  #########
    path('event/category/', views.AdminEventCategoryList, name='AdminEventCategoryList'),
    path('event/category/update/<slug:slug>/', views.AdminTicketCategoryUpdate, name='AdminEventCategoryUpdate'),
    path('event/category/delete/<slug:slug>/', views.AdminTicketCategoryDelete, name='AdminEventCategoryDelete'),
    ##########   Event #########
    path('event/list/', views.AdminEventList, name='AdminEventList'),
    path('event/detail/<slug:slug>/', views.AdminEventDetails, name='AdminEventDetails'),
    path('event/update/<slug:slug>/', views.AdminEventUpdate, name='AdminEventUpdate'),
    path('event/management/<slug:slug>/', views.AdminEventManagement, name='AdminEventManagement'),
    path('event/management/time/<slug:slug>/', views.AdminEventManagementTime, name='AdminEventManagementTime'),
    path('event/archive/<slug:slug>/', views.AdminEventArchive, name='AdminEventArchive'),
    path('event/delete/<slug:slug>/', views.AdminEventDelete, name='AdminEventDelete'),
    path('event/checkin/<slug:slug>/', views.AdminEventCheckIn, name='AdminEventCheckIn'),
    path('event/checkout/<slug:slug>/', views.AdminEventCheckOut, name='AdminEventCheckOut'),
    path('event/attendees/quckadd/<slug:slug>/', views.AdminEventAttendeesQuickAdd, name='AdminEventAttendeesQuickAdd'),

    path('event/attendees/history/details/<slug:slug>/', views.AdminEventAttendeesDetails,
         name='AdminEventAttendeesDetails'),
    path('event/attendees/api/cheack/exist/<str:mobile_num>/', api_views.AdminEventAttendeesQuickAddCheckExist,
         name='AdminEventAttendeesQuickAddCheckExist'),
    path('event/attendees/api/cheack/form/<slug:slug>/', api_views.AdminEventAttendeesQuickAddForm,
         name='AdminEventAttendeesQuickAddForm'),
    path('event/attendees/api/status/<str:att_num>', api_views.AdminApiAttendeesHistoryChangeStatus,
         name='AdminApiAttendeesHistoryChangeStatus'),
    path('event/attendees/api/avg/<slug:slug>/', api_views.AdminEventCheckAttendeesTimeAverage,
         name='AdminEventCheckAttendeesTimeAverage'),
    path('event/attendees/api/print/id_card/<slug:slug>/', api_views.AdminEventAttendeesPrintIdCard,
         name='AdminEventAttendeesPrintIdCard'),

    path('event/attendees/idcard/print/<slug:slug>/', views.AdminEventAttendeesIdCardPrint,
         name='AdminEventAttendeesIdCardPrint'),

    path('event/attendees/certificate/print/<slug:slug>/', views.AdminEventAttendeesCertificatePrint,
         name='AdminEventAttendeesCertificatePrint'),
path('event/attendees/email/sent/<slug:slug>/', api_views.AdminEventAttendeesSentConfirmedMail,
         name='AdminEventAttendeesSentConfirmedMail'),
path('event/attendees/regnrate_code/<slug:slug>/', utils.CommonEventAttendeesQrImageGenerate,
         name='CommonEventAttendeesQrImageGenerate'),
path('event/attendees/certificate/pdf/<slug:slug>/', api_views.CreatePdfFromImages,
         name='CreatePdfFromImages'),
    path('event/speaker/add/<slug:slug>/', views.AdminEventSpeakersAdd, name='AdminEventSpeakersAdd'),
    path('event/sponsor/add/<slug:slug>/', views.AdminEventSponsorsAdd, name='AdminEventSponsorsAdd'),

    ##########   Attendees #########
    path('event/attendees/list/<slug:slug>/', views.AdminEventAttendeesList, name='AdminEventAttendeesList'),
    path('attendees/detail/<slug:slug>/', views.AdminAttendeesDetails, name='AdminAttendeesDetails'),
    path('attendees/update/<slug:slug>/', views.AdminAttendeesUpdate, name='AdminAttendeesUpdate'),
    path('attendees/archive/<slug:slug>/', views.AdminAttendeesArchive, name='AdminAttendeesArchive'),
    path('attendees/delete/<slug:slug>/', views.AdminAttendeesDelete, name='AdminAttendeesDelete'),

    ##########   Speakers #########
    path('speakers/list/', views.AdminSpeakersList, name='AdminSpeakersList'),
    path('speakers/detail/<slug:slug>/', views.AdminSpeakersDetails, name='AdminSpeakersDetails'),
    path('speakers/update/<slug:slug>/', views.AdminSpeakersUpdate, name='AdminSpeakersUpdate'),
    path('speakers/archive/<slug:slug>/', views.AdminSpeakersArchive, name='AdminSpeakersArchive'),
    path('speakers/delete/<slug:slug>/', views.AdminSpeakersDelete, name='AdminSpeakersDelete'),

    ##########   Sponsors #########
    path('sponsors/list/', views.AdminSponsorsList, name='AdminSponsorsList'),
    path('sponsors/detail/<slug:slug>/', views.AdminSponsorsDetails, name='AdminSponsorsDetails'),
    path('sponsors/update/<slug:slug>/', views.AdminSponsorsUpdate, name='AdminSponsorsUpdate'),
    path('sponsors/archive/<slug:slug>/', views.AdminSponsorsUpdate, name='AdminSponsorsArchive'),
    path('sponsors/delete/<slug:slug>/', views.AdminSponsorsDelete, name='AdminSponsorsDelete'),

    # ##########   Operations #########
    # path('event/list/', views.AdminPressCategoriesUpdate, name='AdminEventList'),
    # path('event/detail/<slug:slug>/', views.AdminPressCategoriesUpdate, name='AdminEventDetails'),
    # path('event/update/<slug:slug>/', views.AdminPressCategoriesUpdate, name='AdminEventUpdate'),
    # path('event/archive/<slug:slug>/', views.AdminPressCategoriesUpdate, name='AdminEventArchive'),
    # path('event/delete/<slug:slug>/', views.AdminPressCategoriesUpdate, name='AdminEventDelete'),

    # ##########   Press Releases #########
    # path('press-releases/list/', views.AdminPressCategoriesUpdate, name='AdminPressReleasesList'),
    # path('press-releases/detail/<slug:slug>/', views.AdminPressCategoriesUpdate, name='AdminPressReleasesDetails'),
    # path('press-releases/update/<slug:slug>/', views.AdminPressCategoriesUpdate, name='AdminPressReleasesUpdate'),
    # path('press-releases/archive/<slug:slug>/', views.AdminPressCategoriesUpdate, name='AdminPressReleasesArchive'),
    # path('press-releases/delete/<slug:slug>/', views.AdminPressCategoriesUpdate, name='AdminPressReleasesDelete'),
    #

]
