from django.urls import path

from apps.sport.views import views, monks, media,operations

app_name = 'sport'

urlpatterns = [

    ##########   Sport  #########
    path('category/', views.AdminSportList, name='AdminSportList'),
    path('category/update/<slug:slug>/', views.AdminSportUpdate, name='AdminSportUpdate'),
    path('category/archive/<slug:slug>/', views.AdminSportArchive, name='AdminSportArchive'),
    path('category/delete/<slug:slug>/', views.AdminSportDelete, name='AdminSportDelete'),
    path('category/country/<slug:slug>/', views.AdminSportByCountry, name='AdminSportByCountry'),

    ##########   Leagues  #########
    path('leagues/', views.AdminLeaguesList, name='AdminLeaguesList'),
    path('category/leagues/<slug:slug>/', views.AdminLeaguesBySport, name='AdminLeaguesBySport'),
    path('leagues/update/<slug:slug>/', views.AdminLeaguesUpdate, name='AdminLeaguesUpdate'),
    path('leagues/archive/<slug:slug>/', views.AdminLeaguesArchive, name='AdminLeaguesArchive'),
    path('leagues/delete/<slug:slug>/', views.AdminLeaguesDelete, name='AdminLeaguesDelete'),
    path('leagues/teams/<slug:slug>/', views.AdminLeaguesTeams, name='AdminLeaguesTeams'),
    path('leagues/match/<slug:slug>/', views.AdminMatchByLeague, name='AdminMatchByLeague'),
    path('monk/leagues/api/get/', monks.AdminMonksLeaguesGetData, name='AdminMonksLeaguesGetData'),

    ##########   Season  #########
    path('season/', views.AdminSeasonList, name='AdminSeasonList'),
    path('leagues/season/<slug:slug>/', views.AdminSeasonByLeague, name='AdminSeasonByLeague'),
    path('season/update/<slug:slug>/', views.AdminSeasonUpdate, name='AdminSeasonUpdate'),
    path('season/archive/<slug:slug>/', views.AdminSeasonArchive, name='AdminSeasonArchive'),
    path('season/delete/<slug:slug>/', views.AdminSeasonDelete, name='AdminSeasonDelete'),
    path('season/match/<slug:slug>/', views.AdminMatchBySeason, name='AdminMatchBySeason'),
    path('monk/season/api/get/', monks.AdminMonksSeasonGetData, name='AdminMonksSeasonGetData'),

    ##########   Group #########
    path('group/', views.AdminGroupList, name='AdminGroupList'),
    # path('season/group/<slug:slug>/', views.AdminGroupBySeason, name='AdminGroupBySeason'),
    path('group/update/<slug:slug>/', views.AdminGroupUpdate, name='AdminGroupUpdate'),
    path('group/archive/<slug:slug>/', views.AdminGroupArchive, name='AdminGroupArchive'),
    path('group/delete/<slug:slug>/', views.AdminGroupDelete, name='AdminGroupDelete'),


    ##########   Round  #########
    path('round/', views.AdminRoundList, name='AdminRoundList'),
    # path('round/add/<slug:slug>/', views.AdminRoundCreate, name='AdminRoundCreate'),
    path('round/update/<slug:slug>/', views.AdminRoundUpdate, name='AdminRoundUpdate'),
    path('round/archive/<slug:slug>/', views.AdminRoundArchive, name='AdminRoundArchive'),
    path('round/delete/<slug:slug>/', views.AdminRoundDelete, name='AdminRoundDelete'),
    path('monk/round/api/get/', monks.AdminMonksRoundGetData, name='AdminMonksRoundGetData'),

##########  League Sport Season Table  #########
    path('season/league/table/', views.AdminSeasonLeagueTableList, name='AdminSeasonLeagueTableList'),
    path('season/league/table/update/<slug:slug>/', views.AdminSeasonLeagueTableUpdate, name='AdminSeasonLeagueTableUpdate'),
    path('season/table/archive/<slug:slug>/', views.AdminSeasonLeagueTableArchive, name='AdminSeasonLeagueTableArchive'),
    path('season/league/table/delete/<slug:slug>/', views.AdminSeasonLeagueTableDelete, name='AdminSeasonLeagueTableDelete'),

    ##########  Team Sport Season Table  #########
    path('season/team/table/<slug:slug>/', views.AdminSeasonTeamTableList, name='AdminSeasonTeamTableList'),
    path('season/team/table/add/<slug:slug>/', views.AdminSeasonTeamTableCreate, name='AdminSeasonTeamTableCreate'),
    path('season/team/table/update/<slug:slug>/', views.AdminSeasonTeamTableUpdate, name='AdminSeasonTeamTableUpdate'),
    # path('season/table/archive/<slug:slug>/', views.AdminSeasonTableArchive, name='AdminSeasonTableArchive'),
    path('season/table/delete/<slug:slug>/', views.AdminSeasonTableDelete, name='AdminSeasonTableDelete'),

    ##########   Stages  #########
    path('stages/', views.AdminStagesList, name='AdminStagesList'),
    path('monk/stages/api/get/', monks.AdminMonksStagesGetData, name='AdminMonksStagesGetData'),


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
    path('monk/venues/api/get/', monks.AdminMonksVenuesGetData, name='AdminMonksVenuesGetData'),

    ##########   Team  #########
    path('team/', views.AdminTeamsList, name='AdminTeamsList'),
    path('team/add/<slug:slug>/', views.AdminTeamsCreate, name='AdminTeamsCreate'),
    path('team/playr/serch/', views.AdminTeamSearch, name='AdminTeamSearch'),
    path('team/update/<slug:slug>/', views.AdminTeamsUpdate, name='AdminTeamsUpdate'),
    path('team/archive/<slug:slug>/', views.AdminTeamsArchive, name='AdminTeamsArchive'),
    path('team/delete/<slug:slug>/', views.AdminTeamsDelete, name='AdminTeamsDelete'),
    path('monk/teams/list/', monks.AdminMonksTeamsList, name='AdminMonksTeamsList'),
    path('monk/teams/api/get/', monks.AdminMonksTeamsGetData, name='AdminMonksTeamsGetData'),
    path('team/playr/list/<slug:slug>/', views.AdminTeamPlayerList, name='AdminTeamPlayerList'),
    path('team/playr/add/<slug:slug>/', views.AdminTeamPlayerAdd, name='AdminTeamPlayerAdd'),



    ##########   Players  #########
    path('player/', views.AdminPlayersList, name='AdminPlayersList'),
    path('player/details/<slug:slug>/', views.AdminPlayersUpdate, name='AdminPlayersDetails'),
    path('player/update/<slug:slug>/', views.AdminPlayersUpdate, name='AdminPlayersUpdate'),
    path('player/archive/<slug:slug>/', views.AdminPlayersArchive, name='AdminPlayersArchive'),
    path('player/delete/<slug:slug>/', views.AdminPlayersDelete, name='AdminPlayersDelete'),
    path('player/static/add/<slug:slug>/', views.AdminPlayerStaticAdd, name='AdminPlayerStaticAdd'),
    path('monk/players/api/get/', monks.AdminMonksPlayersGetData, name='AdminMonksPlayersGetData'),

    ##########   Match  #########
    path('match/', views.AdminMatchList, name='AdminMatchList'),

    path('match/details/<slug:slug>/', views.AdminMatchDetails, name='AdminMatchDetails'),
    path('match/update/<slug:slug>/', views.AdminMatchUpdate, name='AdminMatchUpdate'),
    path('match/archive/<slug:slug>/', views.AdminMatchArchive, name='AdminMatchArchive'),
    path('match/delete/<slug:slug>/', views.AdminMatchDelete, name='AdminMatchDelete'),
    path('match/control/<slug:slug>/', views.AdminMatchControl, name='AdminMatchControl'),
    path('match/summary/add/<slug:slug>/', views.AdminMatchSummaryAdd, name='AdminMatchSummaryAdd'),
    path('match/static/add/<slug:slug>/', views.AdminMatchStaticAdd, name='AdminMatchStaticAdd'),

    path('match/goals/add/<slug:slug>/', views.AdminMatchGoalsAdd, name='AdminMatchGoalsAdd'),


    ##########   Match By Team #########
    path('match/team/player/<slug:match_slug>/<slug:slug>/', views.AdminMatchTeamPlayerList,
         name='AdminMatchTeamPlayerList'),
    path('match/player/static/add/<slug:match_slug>/<slug:slug>/', views.AdminMatchPlayerStaticAdd,
            name='AdminMatchPlayerStaticAdd'),


    path('match/team/playr/transfer/<slug:slug>/', views.AdminTeamPlayerMatchAdd, name='AdminTeamPlayerMatchAdd'),
    path('match/team/playr/list/<slug:slug>/<slug:team_slug>/', views.AdminMatchDetailsByTeam,
         name='AdminMatchDetailsByTeam'),
    path('match/team/playr/add/<slug:slug>/<slug:team_slug>/', views.AdminMatchTeamPlayerAdd,
         name='AdminMatchTeamPlayerAdd'),
    path('match/team/event/add/<slug:slug>/<slug:team_slug>/', views.AdminMatchTeamEventAdd,
         name='AdminMatchTeamEventAdd'),


################## Match Report ##################
    path('match/report/', operations.AdminMatchReportList, name='AdminMatchReportList'),
    path('match/report/update/<slug:slug>/', operations.AdminMatchReportUpdate, name='AdminMatchReportUpdate'),
    path('match/report/archive/<slug:slug>/', operations.AdminMatchReportArchive, name='AdminMatchReportArchive'),
    path('match/report/delete/<slug:slug>/', operations.AdminMatchReportDelete, name='AdminMatchReportDelete'),


    ################## Match Player Report ##################
    path('match/player/report/', operations.AdminMatchPlayerReportList, name='AdminMatchPlayerReportList'),
    path('match/player/report/update/<slug:slug>/', operations.AdminMatchPlayerReportUpdate, name='AdminMatchPlayerReportUpdate'),
    path('match/player/report/archive/<slug:slug>/', operations.AdminMatchPlayerReportArchive, name='AdminMatchPlayerReportArchive'),
    path('match/player/report/delete/<slug:slug>/', operations.AdminMatchPlayerReportDelete, name='AdminMatchPlayerReportDelete'),

    ##########   Api Data  #########
    path('country/api/', monks.AdminMonksCountryList, name='AdminMonksCountryList'),
    path('country/api/add/', monks.AdminMonksCountryList, name='AdminMonksCountryAdd'),
    path('country/api/update/<slug:slug>/', monks.AdminMonksCountryList, name='AdminMonksCountryUpdate'),
    path('country/api/archive/<slug:slug>/', monks.AdminMonksCountryList, name='AdminMonksCountryArchive'),
    path('monk/country/api/get/', monks.AdminMonksCountryGetData, name='AdminMonksCountryGetData'),

    ################## Media ##################
    path('media/', media.AdminYoutubeChannelList, name='AdminYoutubeChannelList'),
    # path('media/update/<slug:slug>/', views.AdminMediaUpdate, name='AdminMediaUpdate'),
    # path('media/archive/<slug:slug>/', views.AdminMediaArchive, name='AdminMediaArchive'),
    # path('media/delete/<slug:slug>/', views.AdminMediaDelete, name='AdminMediaDelete'),
    path('notfy/add/', media.AdminNotificationAdd, name='AdminNotificationAdd'),

]
