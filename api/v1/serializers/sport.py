from rest_framework import serializers

from apps.sport.models.models import  *


class AdminSportCategorySerializer(serializers.ModelSerializer)    :
    class Meta:
        model = SportCategory
        fields = "__all__"

class AdminSportSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Sport
        fields = "__all__"

class LeaguesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Leagues
        fields = "__all__"

class SeasonSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Season
        fields = "__all__"


class StagesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Stages
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Group
        fields = "__all__"


class AggregateSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Aggregate
        fields = "__all__"

class RoundSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Round
        fields = "__all__"

class VenuesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Venues
        fields = "__all__"

class SportStateSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = SportState
        fields = "__all__"


class FixturesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Fixtures
        fields = "__all__"


class LiveScoresSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = LiveScores
        fields = "__all__"


class ClubsSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Clubs
        fields = "__all__"

class TeamsSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Teams
        fields = "__all__"


class StatisticsSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Statistics
        fields = "__all__"


class StandingsSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Standings
        fields = "__all__"


class LiveStandingsSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = LiveStandings
        fields = "__all__"

class SchedulesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Schedules
        fields = "__all__"

class PlayersSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Players
        fields = "__all__"



class SquadsSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Squads
        fields = "__all__"


class TVStationsSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = TVStations
        fields = "__all__"


class CoachesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Coaches
        fields = "__all__"


class TopScorersSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = TopScorers
        fields = "__all__"




class RivalsSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Rivals
        fields = "__all__"

class CommentariesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Commentaries
        fields = "__all__"


class RefereesSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Referees
        fields = "__all__"


class TransfersSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Transfers
        fields = "__all__"


class PreMatchOddsSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = PreMatchOdds
        fields = "__all__"


class InPlayOddsSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = InPlayOdds
        fields = "__all__"

class MarketsSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Markets
        fields = "__all__"


class BookmakersSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = Bookmakers
        fields = "__all__"


class MatchSerializer(serializers.ModelSerializer)    :

    class Meta:
        model = Match
        fields = "__all__"


class MatchDetailsSerializer(serializers.ModelSerializer):
    match_team_player = serializers.SerializerMethodField()


    class Meta:
        model = Match
        fields = "__all__"

    def get_match_team_player(self, obj):
        print( obj)
        return MatchTeamPlayerSerializer(MatchTeamPlayer.objects.filter(match=obj.id,),many=True).data




class MatchTeamPlayerSerializer(serializers.ModelSerializer)    :
    class Meta:
        model = MatchTeamPlayer
        fields = "__all__"