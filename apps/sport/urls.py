from django.urls import path

from apps.sport.api import api_views
from apps.sport.views import views, utils

app_name = 'sport'

urlpatterns = [




    ##########   Sport  #########
    path('category/', views.AdminSportList, name='AdminSportList'),
    path('category/update/<slug:slug>/', views.AdminSportUpdate, name='AdminSportUpdate'),
    path('category/archive/<slug:slug>/', views.AdminSportArchive, name='AdminSportArchive'),
    path('category/delete/<slug:slug>/', views.AdminSportDelete, name='AdminSportDelete'),


    ##########   Leagues  #########
    path('leagues/', views.AdminLeaguesList, name='AdminLeaguesList'),
    path('category/leagues/<slug:slug>/', views.AdminLeaguesBySport, name='AdminLeaguesBySport'),
    path('leagues/update/<slug:slug>/', views.AdminLeaguesUpdate, name='AdminLeaguesUpdate'),
    path('leagues/archive/<slug:slug>/', views.AdminLeaguesArchive, name='AdminLeaguesArchive'),
    path('leagues/delete/<slug:slug>/', views.AdminLeaguesDelete, name='AdminLeaguesDelete'),


    ##########   Season  #########
    path('season/', views.AdminSeasonList, name='AdminSeasonList'),
    path('leagues/season/<slug:slug>/', views.AdminSeasonByLeague, name='AdminSeasonByLeague'),
    path('season/update/<slug:slug>/', views.AdminSeasonUpdate, name='AdminSeasonUpdate'),
    path('season/archive/<slug:slug>/', views.AdminSeasonArchive, name='AdminSeasonArchive'),
    path('season/delete/<slug:slug>/', views.AdminSeasonDelete, name='AdminSeasonDelete'),


    # ##########   Stages  #########
    # path('stages/', views.AdminStagesList, name='AdminStagesList'),
    # path('stages/update/<slug:slug>/', views.AdminStagesUpdate, name='AdminStagesUpdate'),
    # path('stages/archive/<slug:slug>/', views.AdminStagesArchive, name='AdminStagesArchive'),
    # path('stages/delete/<slug:slug>/', views.AdminStagesDelete, name='AdminStagesDelete'),
    #
    #
    # ##########   Group  #########
    # path('group/', views.AdminGroupList, name='AdminGroupList'),
    # path('group/update/<slug:slug>/', views.AdminGroupUpdate, name='AdminGroupUpdate'),
    # path('group/archive/<slug:slug>/', views.AdminGroupArchive, name='AdminGroupArchive'),
    # path('group/delete/<slug:slug>/', views.AdminGroupDelete, name='AdminGroupDelete'),
    #
    #
    # ##########   Aggregate  #########
    # path('aggregate/', views.AdminAggregateList, name='AdminAggregateList'),
    # path('aggregate/update/<slug:slug>/', views.AdminAggregateUpdate, name='AdminAggregateUpdate'),
    # path('aggregate/archive/<slug:slug>/', views.AdminAggregateArchive, name='AdminAggregateArchive'),
    # path('aggregate/delete/<slug:slug>/', views.AdminAggregateDelete, name='AdminAggregateDelete'),
    #
    #
    # ##########   Round  #########
    # path('round/', views.AdminRoundList, name='AdminRoundList'),
    # path('round/update/<slug:slug>/', views.AdminRoundUpdate, name='AdminRoundUpdate'),
    # path('round/archive/<slug:slug>/', views.AdminRoundArchive, name='AdminRoundArchive'),
    # path('round/delete/<slug:slug>/', views.AdminRoundDelete, name='AdminRoundDelete'),
    #
    #

    ##########   Clubs  #########
    path('clubs/', views.AdminClubsList, name='AdminClubsList'),
    path('clubs/update/<slug:slug>/', views.AdminClubsUpdate, name='AdminClubsUpdate'),
    path('clubs/archive/<slug:slug>/', views.AdminClubsArchive, name='AdminClubsArchive'),
    path('clubs/delete/<slug:slug>/', views.AdminClubsDelete, name='AdminClubsDelete'),

    ##########   Venues  #########
    path('venues/', views.AdminVenuesList, name='AdminVenuesList'),
    path('venues/update/<slug:slug>/', views.AdminVenuesUpdate, name='AdminVenuesUpdate'),
    path('venues/archive/<slug:slug>/', views.AdminVenuesArchive, name='AdminVenuesArchive'),
    path('venues/delete/<slug:slug>/', views.AdminVenuesDelete, name='AdminVenuesDelete'),



    ##########   Team  #########
    path('team/', views.AdminTeamsList, name='AdminTeamsList'),
    path('team/update/<slug:slug>/', views.AdminTeamsUpdate, name='AdminTeamsUpdate'),
    path('team/archive/<slug:slug>/', views.AdminTeamsArchive, name='AdminTeamsArchive'),
    path('team/delete/<slug:slug>/', views.AdminTeamsDelete, name='AdminTeamsDelete'),

    path('team/playr/add/<slug:slug>/', views.AdminTeamPlayerAdd,
         name='AdminTeamPlayerAdd'),


    ##########   Players  #########
    path('player/', views.AdminPlayersList, name='AdminPlayersList'),
    path('player/details/<slug:slug>/', views.AdminPlayersUpdate, name='AdminPlayersDetails'),
    path('player/update/<slug:slug>/', views.AdminPlayersUpdate, name='AdminPlayersUpdate'),
    path('player/archive/<slug:slug>/', views.AdminPlayersArchive, name='AdminPlayersArchive'),
    path('player/delete/<slug:slug>/', views.AdminPlayersDelete, name='AdminPlayersDelete'),

    ##########   Match  #########
    path('season/', views.AdminMatchList, name='AdminMatchList'),
    path('season/match/<slug:slug>/',  views.AdminMatchBySeason, name='AdminMatchBySeason'),

    path('match/update/<slug:slug>/', views.AdminMatchUpdate, name='AdminMatchUpdate'),
    path('match/archive/<slug:slug>/', views.AdminMatchArchive, name='AdminMatchArchive'),
    path('match/delete/<slug:slug>/', views.AdminMatchDelete, name='AdminMatchDelete'),
    path('match/team/playr/list/<slug:slug>/<slug:team_slug>/', views.AdminMatchTeamPlayerList,
         name='AdminMatchTeamPlayerList'),
    path('match/team/playr/add/<slug:slug>/<slug:team_slug>/', views.AdminMatchTeamPlayerAdd, name='AdminMatchTeamPlayerAdd'),







]
