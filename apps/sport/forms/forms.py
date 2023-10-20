from django import forms
from django.contrib.auth import get_user_model

from apps.sport.models.models import SportCategory, Sport, Leagues, Season, Stages, Group, Aggregate, \
    Round,Venues,SportState,Fixtures,LiveScores,Clubs,Teams,Statistics,Standings,LiveStandings,Schedules,\
    Players,Squads,TVStations,Coaches,TopScorers,Rivals,Commentaries,Referees,Transfers,PreMatchOdds,\
    InPlayOdds,Markets,Bookmakers,Match

User = get_user_model()


class AdminSportCategoryForm(forms.ModelForm):
    class Meta:
        model = SportCategory
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminSportForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminLeaguesForm(forms.ModelForm):
    class Meta:
        model = Leagues
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminSeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = '__all__'
        exclude = ('slug', 'code')



class AdminStagesForm(forms.ModelForm):
    class Meta:
        model = Stages
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminAggregateForm(forms.ModelForm):
    class Meta:
        model = Aggregate
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminRoundForm(forms.ModelForm):
    class Meta:
        model = Round
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminVenuesForm(forms.ModelForm):
    class Meta:
        model = Venues
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminSportStateForm(forms.ModelForm):
    class Meta:
        model = SportState
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminFixturesForm(forms.ModelForm):
    class Meta:
        model = Fixtures
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminLiveScoresForm(forms.ModelForm):
    class Meta:
        model = LiveScores
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminClubsForm(forms.ModelForm):
    class Meta:
        model = Clubs
        fields = '__all__'
        exclude = ('slug', 'code')

class AdminTeamsForm(forms.ModelForm):
    class Meta:
        model = Teams
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminStatisticsForm(forms.ModelForm):
    class Meta:
        model = Statistics
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminStandingsForm(forms.ModelForm):
    class Meta:
        model = Standings
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminLiveStandingsForm(forms.ModelForm):
    class Meta:
        model = LiveStandings
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminSchedulesForm(forms.ModelForm):
    class Meta:
        model = Schedules
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminPlayersForm(forms.ModelForm):
    class Meta:
        model = Players
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminSquadsForm(forms.ModelForm):
    class Meta:
        model = Squads
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminTVStationsForm(forms.ModelForm):

    class Meta:
        model = TVStations
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminCoachesForm(forms.ModelForm):
    class Meta:
        model = Coaches
        fields = '__all__'
        exclude = ('slug', 'code')

class AdminTopScorersForm(forms.ModelForm):
    class Meta:
        model = TopScorers
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminRivalsForm(forms.ModelForm):
    class Meta:
        model = Rivals
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminCommentariesForm(forms.ModelForm):
    class Meta:
        model = Commentaries
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminRefereesForm(forms.ModelForm):
    class Meta:
        model = Referees
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminTransfersForm(forms.ModelForm):

    class Meta:
        model = Transfers
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminPreMatchOddsForm(forms.ModelForm):
    class Meta:
        model = PreMatchOdds
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminInPlayOddsForm(forms.ModelForm):
    class Meta:
        model = InPlayOdds
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminMarketsForm(forms.ModelForm):
    class Meta:
        model = Markets
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminBookmakersForm(forms.ModelForm):
    class Meta:
        model = Bookmakers
        fields = '__all__'
        exclude = ('slug', 'code')


class AdminMatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = '__all__'
        exclude = ('slug', 'code')