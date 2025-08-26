from django.urls import path

from api.v4.views.apps.sport import new_app

app_name = 'api'

urlpatterns = [
    ############# Home Fixtures api urls #############
    path('v4/fixtures/<str:sport>/<str:date>/<str:lang>/list/', new_app.FixturesByDateApiList,
         name='FixturesByDateApiList'),

    path('v4/leagues/toggle-favorite/', new_app.FavoriteLeagueToggle.as_view(), name='toggle-favorite-league'),

    path('v4/fixtures/detail/<int:fixture_id>/<str:lang>/', new_app.FixtureDetailApiView, name='FixtureDetailApiView'),

    ######################### team Screen api urls #########################
    path('v4/teams/<str:sport>/<str:lang>/list/', new_app.TeamScreenApiView, name='TeamScreenApiView'),
    path('v4/teams/detail/<int:team_id>/<str:lang>/', new_app.TeamDetailApiView, name='TeamDetailApiView'),

    ############# league Screen api urls #############
    path('v4/leagues/<str:sport>/<str:lang>/list/', new_app.LeaguesApiView, name='LeaguesApiView'),
    path('v4/leagues/detail/<int:league_id>/<str:lang>/', new_app.LeagueDetailApiView, name='LeagueDetailApiView'),

    # --- NEW URLS FOR SPORTMONKS PROXY ---
    path('v4/football/standings/live/leagues/<int:league_id>/', new_app.LiveStandingsByLeagueApiView, name='LiveStandingsByLeagueApiView'),
    path('v4/football/topscorers/seasons/<int:season_id>/', new_app.TopScorersBySeasonApiView, name='TopScorersBySeasonApiView'),


    ######################### News api urls #########################
    path('v4/news/<str:lang>/list/', new_app.NewsApiView, name='NewsApiView'),
    path('v4/news/detail/<int:news_id>/<str:lang>/', new_app.NewsDetailApiView, name='NewsDetailApiView')

]
