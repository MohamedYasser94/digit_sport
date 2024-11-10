from rest_framework.fields import SerializerMethodField
from rest_framework.templatetags import rest_framework

from api.v3.serializers.blog import *
from api.v3.serializers.sport.operations import *
from api.v3.serializers.sport.sport import TeamForMatchSerializer
from apps.sport.models import *
from apps.sport.models.models import *
from core.models.blog import *
from digit_sport.settings import env


class HiveLeaguesSerializer(serializers.ModelSerializer):
    sport_name = serializers.ReadOnlyField(source='sport.name')
    # league_matches = serializers.SerializerMethodField()
    class Meta:
        model = Leagues
        fields = ['id', 'name','short_code', 'image', 'country','sport','sport_name', 'create_at', 'status' ]

    # def get_league_matches(self, obj):
    #     request = self.context['request']
    #     return HiveMatchDetailsSerializer(Match.objects.filter(league=obj.id), many=True,context={'request': request}).data

class HiveTeamsSerializer(serializers.ModelSerializer):
    league_id = serializers.ReadOnlyField(source='league.id')
    sport_name = serializers.ReadOnlyField(source='sport.name')
    class Meta:
        model = Teams
        fields = ['id','league_id', 'name','short_code', 'image', 'country',
                  'country_image', 'sport_name','founded',
                  'create_at',  'status']



class HiveMatchDetailsSerializer(serializers.ModelSerializer):
    venues_name = serializers.ReadOnlyField(source='venues.name')
    league_id = serializers.ReadOnlyField(source='league.id')
    league_name = serializers.ReadOnlyField(source='league.name')
    league_short_code = serializers.ReadOnlyField(source='league.short_code')
    league_image = serializers.SerializerMethodField()
    sport_name = serializers.ReadOnlyField(source='sport.name')
    home_team_object = serializers.SerializerMethodField()
    away_team_object = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ['id',  'league_id', 'league_name','league_short_code', 'league_image','round','venues_name','played', 'current_half', 'current_minute',
                  'start_time',  'score', 'home_score', 'away_score','home_team','home_team_object', 'away_team','away_team_object', 'sport_name']

    def get_league_image(self, obj):
        try:
            league_image = 'https://api.jawlasp.com' + str(obj.league.image.url)
            return league_image
        except:
            league_image = None
            return league_image

    def get_home_team_object(self, obj):
        request = self.context['request']
        return TeamForMatchSerializer(Teams.objects.get(id=obj.home_team.id, ), many=False,context={'request': request}).data

    def get_away_team_object(self, obj):
        request = self.context['request']
        return TeamForMatchSerializer(Teams.objects.get(id=obj.away_team.id, ), many=False,context={'request': request}).data

class HiveLeagueSeasonTableSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeagueSeasonTable
        fields = "__all__"



class HiveTeamSeasonTableSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='team.id')
    team_id = serializers.ReadOnlyField(source='team.id')
    team_slug = serializers.ReadOnlyField(source='team.slug')
    team_name = serializers.ReadOnlyField(source='team.name')
    sport_name = serializers.ReadOnlyField(source='sport.name')
    image = serializers.SerializerMethodField()
    class Meta:
        model = TeamSeasonTable
        fields = "__all__"


    def get_image(self, obj):
       try:
           team_image = 'https://api.jawlasp.com' + str(obj.team.image.url)
           return team_image
       except:
        team_image = None
        return team_image


class HiveRoundSerializer(serializers.ModelSerializer):

    class Meta:
        model = Round
        fields = ['id', 'name', 'starting_at', 'league'  ]


class HiveGoalsSerializer(serializers.ModelSerializer):

    class Meta:
        model = MatchGoals
        fields = "__all__"