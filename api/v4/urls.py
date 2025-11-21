from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api.v4.views import user
from api.v4.views.apps.sport import new_app

app_name = 'api'

urlpatterns = [

    ##########User API################
    path('auth/signup/register/', user.UserRegister, name="UserRegister"),
    path('auth/login/', user.UserLogin, name="UserLogin"),
    path('auth/logout/', user.UserLogout, name="UserLogout"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ############# Home Fixtures api urls #############
    path('v4/fixtures/<str:sport>/<str:date>/<str:lang>/list/', new_app.FixturesByDateApiList,name='FixturesByDateApiList'),
    path('v4/leagues/toggle-favorite/', new_app.FavoriteLeagueToggle.as_view(), name='toggle-favorite-league'),
    path('v4/fixtures/detail/<int:fixture_id>/<str:lang>/', new_app.FixtureDetailApiView, name='FixtureDetailApiView'),
    ######################### team Screen api urls #########################
    path('v4/teams/<str:sport>/<str:lang>/list/', new_app.TeamScreenApiView, name='TeamScreenApiView'),
    path('v4/teams/detail/<int:team_id>/<str:lang>/', new_app.TeamDetailApiView, name='TeamDetailApiView'),
    path('v4/teams/top', new_app.TopTeamsApiView, name='TopTeamsApiView'),
    ############# league Screen api urls #############
    path('v4/leagues/<str:sport>/<str:lang>/list/', new_app.LeaguesApiView, name='LeaguesApiView'),
    path('v4/leagues/detail/<int:league_id>/<str:lang>/', new_app.LeagueDetailApiView, name='LeagueDetailApiView'),
    # --- NEW URLS FOR SPORTMONKS PROXY ---
    path('v4/football/standings/live/leagues/<int:league_id>/', new_app.LiveStandingsByLeagueApiView, name='LiveStandingsByLeagueApiView'),
    path('v4/football/topscorers/seasons/<int:season_id>/', new_app.TopScorersBySeasonApiView, name='TopScorersBySeasonApiView'),
    path('v4/football/topassists/seasons/<int:season_id>/', new_app.TopAssistsBySeasonApiView, name='TopScorersBySeasonApiView'),
    path('v4/football/players/detail/<int:player_id>/<str:lang>/', new_app.PlayerDetailApiView, name='PlayerDetailApiView'),
    path('v4/football/headtohead/current-scores/<int:team1_id>/<int:team2_id>/',new_app.PreviousMatchesApiView,name='PreviousMatchesApiView'),
    path('v4/football/team/<int:team_id>/', new_app.TeamLatestUpcomingApiView, name='TeamLatestUpcomingApiView'),
    path('v4/football/standings/seasons/<int:season_id>/', new_app.standingsByseasonsApiView, name='SeasonDetailApiView'),
    path('v4/football/information/leagues/<int:league_id>/',new_app.LeagueInformationApiView,name='LeagueInformationApiView'),
    path('v4/football/information/schedules/seasons/<int:season_id>/',new_app.SeasonSchedulesApiView,name='SeasonSchedulesApiView'),
    path('v4/football/leagues/search/<str:name>/', new_app.LeagueSearchApiView, name='LeagueSearchApiView'),
    path('v4/football/teams/search/<str:name>/', new_app.TeamSearchApiView, name='TeamSearchApiView'),
    path('v4/football/players/search/<str:name>/', new_app.PlayerSearchApiView, name='PlayerSearchApiView'),
    ######################### News api urls #########################
    path('v4/news/<str:lang>/list/', new_app.NewsApiView, name='NewsApiView'),
    path('v4/football/transfers/', new_app.TransfersApiView, name='TransfersApiView'),
    path('v4/news/detail/<int:news_id>/<str:lang>/', new_app.NewsDetailApiView, name='NewsDetailApiView'),
    path('v4/news/teams/<int:team_id>/<str:lang>/list/', new_app.TeamNewsApiView, name='TeamNewsApiView'),
    path('v4/favorites/toggle/', new_app.favorite_toggle, name='toggle-favorite'),
    path('v4/favorites/list/', new_app.list_user_favorites, name='list-user-favorites'),
    path('v4/match/details/<int:match_id>', new_app.MatchDetailsApi,name='MatchDetailsApi'),
    path('v4/match/standings/<int:league_id>/<int:season_id>/', new_app.LeagueStandingsApi, name='league-standings'),
    path('v4/sport/player/<str:sport_name>/team/<int:team_id>/match/<int:match_id>/players/', new_app.PlayersReportdetailsApi, name='PlayersReportdetailsApi'),
    path('players/<int:player_id>/basic/', new_app.PlayerBasicDetailsApi, name='player-basic-details'),
    path('teams/<int:team_id>/', new_app.TeamDetailsApi, name='team-details'),
    path('league/<int:league_id>/matches/', new_app.LeagueMatchesApi, name='league-matches'),
    path('team/<int:team_id>/matches/', new_app.TeamMatchesApi, name='team-matches'),
    path('h2h/<int:team1_id>/<int:team2_id>/', new_app.HeadToHeadApi, name='h2h-stats'),
]