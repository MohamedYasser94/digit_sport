from django.urls import path

from apps.sport.api import api_views
from apps.sport.views import views, utils

app_name = 'sport'

urlpatterns = [

    ##########   Category  #########
    path('sport/category/', views.AdminSportCategoryList, name='AdminSportCategoryList'),
    path('sport/category/update/<slug:slug>/', views.AdminSportCategoryUpdate, name='AdminSportCategoryUpdate'),
    path('sport/category/archive/<slug:slug>/', views.AdminSportCategoryDelete, name='AdminSportCategoryArchive'),
    path('sport/category/delete/<slug:slug>/', views.AdminSportCategoryDelete, name='AdminSportCategoryDelete'),


    ##########   Sport  #########
    path('sport/sport/', views.AdminSportList, name='AdminSportList'),
    path('sport/sport/update/<slug:slug>/', views.AdminSportUpdate, name='AdminSportUpdate'),
    path('sport/sport/archive/<slug:slug>/', views.AdminSportArchive, name='AdminSportArchive'),
    path('sport/sport/delete/<slug:slug>/', views.AdminSportDelete, name='AdminSportDelete'),


    ##########   Leagues  #########
    path('sport/leagues/', views.AdminLeaguesList, name='AdminLeaguesList'),
    path('sport/leagues/update/<slug:slug>/', views.AdminLeaguesUpdate, name='AdminLeaguesUpdate'),
    path('sport/leagues/archive/<slug:slug>/', views.AdminLeaguesArchive, name='AdminLeaguesArchive'),
    path('sport/leagues/delete/<slug:slug>/', views.AdminLeaguesDelete, name='AdminLeaguesDelete'),


    ##########   Season  #########
    path('sport/season/', views.AdminSeasonList, name='AdminSeasonList'),
    path('sport/season/update/<slug:slug>/', views.AdminSeasonUpdate, name='AdminSeasonUpdate'),
    path('sport/season/archive/<slug:slug>/', views.AdminSeasonArchive, name='AdminSeasonArchive'),
    path('sport/season/delete/<slug:slug>/', views.AdminSeasonDelete, name='AdminSeasonDelete'),


    # ##########   Stages  #########
    # path('sport/stages/', views.AdminStagesList, name='AdminStagesList'),
    # path('sport/stages/update/<slug:slug>/', views.AdminStagesUpdate, name='AdminStagesUpdate'),
    # path('sport/stages/archive/<slug:slug>/', views.AdminStagesArchive, name='AdminStagesArchive'),
    # path('sport/stages/delete/<slug:slug>/', views.AdminStagesDelete, name='AdminStagesDelete'),
    #
    #
    # ##########   Group  #########
    # path('sport/group/', views.AdminGroupList, name='AdminGroupList'),
    # path('sport/group/update/<slug:slug>/', views.AdminGroupUpdate, name='AdminGroupUpdate'),
    # path('sport/group/archive/<slug:slug>/', views.AdminGroupArchive, name='AdminGroupArchive'),
    # path('sport/group/delete/<slug:slug>/', views.AdminGroupDelete, name='AdminGroupDelete'),
    #
    #
    # ##########   Aggregate  #########
    # path('sport/aggregate/', views.AdminAggregateList, name='AdminAggregateList'),
    # path('sport/aggregate/update/<slug:slug>/', views.AdminAggregateUpdate, name='AdminAggregateUpdate'),
    # path('sport/aggregate/archive/<slug:slug>/', views.AdminAggregateArchive, name='AdminAggregateArchive'),
    # path('sport/aggregate/delete/<slug:slug>/', views.AdminAggregateDelete, name='AdminAggregateDelete'),
    #
    #
    # ##########   Round  #########
    # path('sport/round/', views.AdminRoundList, name='AdminRoundList'),
    # path('sport/round/update/<slug:slug>/', views.AdminRoundUpdate, name='AdminRoundUpdate'),
    # path('sport/round/archive/<slug:slug>/', views.AdminRoundArchive, name='AdminRoundArchive'),
    # path('sport/round/delete/<slug:slug>/', views.AdminRoundDelete, name='AdminRoundDelete'),
    #
    #

    ##########   Clubs  #########
    path('sport/clubs/', views.AdminClubsList, name='AdminClubsList'),
    path('sport/clubs/update/<slug:slug>/', views.AdminClubsUpdate, name='AdminClubsUpdate'),
    path('sport/clubs/archive/<slug:slug>/', views.AdminClubsArchive, name='AdminClubsArchive'),
    path('sport/clubs/delete/<slug:slug>/', views.AdminClubsDelete, name='AdminClubsDelete'),

    ##########   Venues  #########
    path('sport/venues/', views.AdminVenuesList, name='AdminVenuesList'),
    path('sport/venues/update/<slug:slug>/', views.AdminVenuesUpdate, name='AdminVenuesUpdate'),
    path('sport/venues/archive/<slug:slug>/', views.AdminVenuesArchive, name='AdminVenuesArchive'),
    path('sport/venues/delete/<slug:slug>/', views.AdminVenuesDelete, name='AdminVenuesDelete'),



    ##########   Team  #########
    path('sport/team/', views.AdminTeamsList, name='AdminTeamsList'),
    path('sport/team/update/<slug:slug>/', views.AdminTeamsUpdate, name='AdminTeamsUpdate'),
    path('sport/team/archive/<slug:slug>/', views.AdminTeamsArchive, name='AdminTeamsArchive'),
    path('sport/team/delete/<slug:slug>/', views.AdminTeamsDelete, name='AdminTeamsDelete'),


    ##########   Players  #########
    path('sport/player/', views.AdminPlayersList, name='AdminPlayersList'),
    path('sport/player/update/<slug:slug>/', views.AdminPlayersUpdate, name='AdminPlayersUpdate'),
    path('sport/player/archive/<slug:slug>/', views.AdminPlayersArchive, name='AdminPlayersArchive'),
    path('sport/player/delete/<slug:slug>/', views.AdminPlayersDelete, name='AdminPlayersDelete'),

    ##########   Match  #########
    path('sport/match/', views.AdminMatchList, name='AdminMatchList'),
    path('sport/match/update/<slug:slug>/', views.AdminMatchUpdate, name='AdminMatchUpdate'),
    path('sport/match/archive/<slug:slug>/', views.AdminMatchArchive, name='AdminMatchArchive'),
    path('sport/match/delete/<slug:slug>/', views.AdminMatchDelete, name='AdminMatchDelete'),







]
