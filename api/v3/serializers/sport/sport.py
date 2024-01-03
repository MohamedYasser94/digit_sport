from api.v3.serializers.blog import *
from apps.sport.models.models import *
from core.models.blog import *


class AdminSportCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SportCategory
        fields = "__all__"


class SportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sport
        fields = ['id', 'name','image_path','country', ]

    def get_match(self, obj):
        return MatchSerializer(Match.objects.filter(sport=obj.id, ), many=True).data

class MatchBySportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'name','image_path','country' ]

class TeamsBySportSerializer(serializers.ModelSerializer):
    # teams = serializers.SerializerMethodField()

    class Meta:
        model = Sport
        fields = ['id', 'name', ]

    def get_teams(self, obj):
        return TeamsSerializer(Teams.objects.filter(sport=obj.id, ), many=True).data


class LeaguesBySportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'name', 'image_path', 'image', 'leagues']


class MatchesBySportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'name', 'image_path', 'image', 'matches']


class NewsBySportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'name', 'image_path', 'image', 'news']


class VideosBySportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'name', 'image_path', 'image', 'videos']


class LeaguesSerializer(serializers.ModelSerializer):
    matches = serializers.SerializerMethodField()
    sport = serializers.ReadOnlyField(source='sport.name')
    class Meta:
        model = Leagues
        fields = ['id', 'name', 'image_path','country','matches' ,'sport']

    def get_matches(self, obj):
        return MatchSerializer(Match.objects.filter(league=obj.id, ), many=True).data


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = "__all__"


class StagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stages
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class AggregateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aggregate
        fields = "__all__"


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = "__all__"


class VenuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venues
        fields = "__all__"


class SportStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportState
        fields = "__all__"


class FixturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fixtures
        fields = "__all__"


class LiveScoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveScores
        fields = "__all__"


class ClubsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clubs
        fields = "__all__"


class TeamsSerializer(serializers.ModelSerializer):
    sport = serializers.ReadOnlyField(source='sport.name')
    league = serializers.ReadOnlyField(source='league.name')

    class Meta:
        model = Teams
        fields = ['id', 'name', 'image_path','sport','league' ]


class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = "__all__"


class StandingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standings
        fields = "__all__"


class LiveStandingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveStandings
        fields = "__all__"


class SchedulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedules
        fields = "__all__"


class PlayersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = '__all__'


class SquadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Squads
        fields = "__all__"


class TVStationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TVStations
        fields = "__all__"


class CoachesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coaches
        fields = "__all__"


class TopScorersSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopScorers
        fields = "__all__"


class RivalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rivals
        fields = "__all__"


class CommentariesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commentaries
        fields = "__all__"


class RefereesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referees
        fields = "__all__"


class TransfersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfers
        fields = "__all__"


class PreMatchOddsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreMatchOdds
        fields = "__all__"


class InPlayOddsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InPlayOdds
        fields = "__all__"


class MarketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Markets
        fields = "__all__"


class BookmakersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmakers
        fields = "__all__"


class MatchSerializer(serializers.ModelSerializer):
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()
    venues = serializers.ReadOnlyField(source='venues.name')
    sport = serializers.ReadOnlyField(source='sport.name')
    league_name = serializers.ReadOnlyField(source='league.name')

    class Meta:
        model = Match
        fields = "__all__"

    def get_home_team(self, obj):
        return TeamsSerializer(Teams.objects.filter(id=obj.home_team.id, ), many=True).data

    def get_away_team(self, obj):
        return TeamsSerializer(Teams.objects.filter(id=obj.away_team.id, ), many=True).data


class MatchDetailsSerializer(serializers.ModelSerializer):
    venues = serializers.ReadOnlyField(source='venues.name')
    league_name = serializers.ReadOnlyField(source='league.name')
    sport_name = serializers.ReadOnlyField(source='sport.name')

    class Meta:
        model = Match
        fields = "__all__"


class MatchTeamPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchTeamPlayer
        fields = "__all__"

class MatchGoalsSerializer(serializers.ModelSerializer):
    team_image = serializers.ReadOnlyField(source='team.image_path')
    player_name = serializers.ReadOnlyField(source='player.name')
    class Meta:
        model = MatchGoals
        fields = "__all__"

class MatchSummarySerializer(serializers.ModelSerializer):
    team_image = serializers.ReadOnlyField(source='team.image_path')
    player_name = serializers.ReadOnlyField(source='player.name')
    class Meta:
        model = MatchSummary
        fields = "__all__"


class MatchStaticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchStatics
        fields = "__all__"


class MatchTeamLineupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchTeamLineups
        fields = "__all__"


class MatchTeamLineupsPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchTeamLineupsPlayer
        fields = "__all__"


class MatchPlayerSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = MatchPlayerSummary
        fields = "__all__"


class SeasonTableSerializer(serializers.ModelSerializer):
    team_name = serializers.ReadOnlyField(source='team.name')
    image_path = serializers.ReadOnlyField(source='team.image_path')
    sport_name = serializers.ReadOnlyField(source='sport.name')
    class Meta:
        model = SeasonTable
        fields = "__all__"