from django import forms
from django.contrib.auth import get_user_model

from apps.sport.models.models import SportCategory, Sport, Leagues, Season, Stages, Group, Aggregate, \
    Round, Venues, SportState, Fixtures, LiveScores, Clubs, Teams, Statistics, Standings, LiveStandings, Schedules, \
    Players, Squads, TVStations, Coaches, TopScorers, Rivals, Commentaries, Referees, Transfers, PreMatchOdds, \
    InPlayOdds, Markets, Bookmakers, Match, MatchTeamPlayer
from apps.sport.models.monks import *

User = get_user_model()


class AdminMonkCountryForm(forms.ModelForm):
    class Meta:
        model = MonkCountry
        fields = '__all__'
        exclude = ('slug', 'code')


