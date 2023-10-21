from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.v1.serializers.sport import *


class SportCategoryList(ListCreateAPIView):
    queryset = SportCategory.objects.all()
    serializer_class = AdminSportCategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminSportCategorySerializer
        else:
            return AdminSportCategorySerializer

class SportCategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = SportCategory.objects.all()
    serializer_class = AdminSportCategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminSportCategorySerializer
        else:
            return AdminSportCategorySerializer

class AdminSportSerializerList(ListCreateAPIView):
    queryset = Sport.objects.all()
    serializer_class = AdminSportSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminSportSerializer
        else:
            return AdminSportSerializer


class AdminSportSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Sport.objects.all()
    serializer_class = AdminSportSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AdminSportSerializer
        else:
            return AdminSportSerializer

class AdminLeaguesSerializerList(ListCreateAPIView):
    queryset = Leagues.objects.all()
    serializer_class = LeaguesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LeaguesSerializer
        else:
            return LeaguesSerializer

class AdminLeaguesSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Leagues.objects.all()
    serializer_class = LeaguesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LeaguesSerializer
        else:
            return LeaguesSerializer


class AdminSeasonSerializerList(ListCreateAPIView):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SeasonSerializer
        else:
            return SeasonSerializer

class AdminSeasonSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SeasonSerializer
        else:
            return SeasonSerializer



class AdminStagesSerializerList(ListCreateAPIView):
    queryset = Stages.objects.all()
    serializer_class = StagesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StagesSerializer
        else:
            return StagesSerializer


class AdminStagesSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Stages.objects.all()
    serializer_class = StagesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StagesSerializer
        else:
            return StagesSerializer


class AdminGroupSerializerList(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GroupSerializer
        else:
            return GroupSerializer


class AdminGroupSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GroupSerializer
        else:
            return GroupSerializer


class AdminAggregateSerializerList(ListCreateAPIView):
    queryset = Aggregate.objects.all()
    serializer_class = AggregateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AggregateSerializer
        else:
            return AggregateSerializer


class AdminAggregateSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Aggregate.objects.all()
    serializer_class = AggregateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AggregateSerializer
        else:
            return AggregateSerializer


class AdminRoundSerializerList(ListCreateAPIView):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RoundSerializer
        else:
            return RoundSerializer


class AdminRoundSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RoundSerializer
        else:
            return RoundSerializer


class AdminVenuesSerializerList(ListCreateAPIView):
    queryset = Venues.objects.all()
    serializer_class = VenuesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return VenuesSerializer
        else:
            return VenuesSerializer


class AdminVenuesSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Venues.objects.all()
    serializer_class = VenuesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return VenuesSerializer
        else:
            return VenuesSerializer


class AdminSportStateSerializerList(ListCreateAPIView):
    queryset = SportState.objects.all()
    serializer_class = SportStateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SportStateSerializer
        else:
            return SportStateSerializer


class AdminSportStateSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = SportState.objects.all()
    serializer_class = SportStateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SportStateSerializer
        else:
            return SportStateSerializer


class AdminFixturesSerializerList(ListCreateAPIView):
    queryset = Fixtures.objects.all()
    serializer_class = FixturesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FixturesSerializer
        else:
            return FixturesSerializer


class AdminFixturesSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Fixtures.objects.all()
    serializer_class = FixturesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return FixturesSerializer
        else:
            return FixturesSerializer



class AdminLiveScoresSerializerList(ListCreateAPIView):
    queryset = LiveScores.objects.all()
    serializer_class = LiveScoresSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LiveScoresSerializer
        else:
            return LiveScoresSerializer


class AdminLiveScoresSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = LiveScores.objects.all()
    serializer_class = LiveScoresSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LiveScoresSerializer
        else:
            return LiveScoresSerializer



class AdminClubsSerializerList(ListCreateAPIView):
    queryset = Clubs.objects.all()
    serializer_class = ClubsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ClubsSerializer
        else:
            return ClubsSerializer


class AdminClubsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Clubs.objects.all()
    serializer_class = ClubsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ClubsSerializer
        else:
            return ClubsSerializer

class AdminTeamsSerializerList(ListCreateAPIView):
    queryset = Teams.objects.all()
    serializer_class = TeamsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TeamsSerializer
        else:
            return TeamsSerializer


class AdminTeamsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Teams.objects.all()
    serializer_class = TeamsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TeamsSerializer
        else:
            return TeamsSerializer


class AdminTeamsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Teams.objects.all()
    serializer_class = TeamsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TeamsSerializer
        else:
            return TeamsSerializer


class AdminStatisticsSerializerList(ListCreateAPIView):
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StatisticsSerializer
        else:
            return StatisticsSerializer


class AdminStatisticsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Statistics.objects.all()
    serializer_class = StatisticsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StatisticsSerializer
        else:
            return StatisticsSerializer


class AdminStandingsSerializerList(ListCreateAPIView):
    queryset = Standings.objects.all()
    serializer_class = StandingsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StandingsSerializer
        else:
            return StandingsSerializer


class AdminStandingsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Standings.objects.all()
    serializer_class = StandingsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StandingsSerializer
        else:
            return StandingsSerializer


class AdminLiveStandingsSerializerList(ListCreateAPIView):
    queryset = LiveStandings.objects.all()
    serializer_class = LiveStandingsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LiveStandingsSerializer
        else:
            return LiveStandingsSerializer


class AdminLiveStandingsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = LiveStandings.objects.all()
    serializer_class = LiveStandingsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LiveStandingsSerializer
        else:
            return LiveStandingsSerializer


class AdminSchedulesSerializerList(ListCreateAPIView):
    queryset = Schedules.objects.all()
    serializer_class = SchedulesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SchedulesSerializer
        else:
            return SchedulesSerializer


class AdminSchedulesSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Schedules.objects.all()
    serializer_class = SchedulesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SchedulesSerializer
        else:
            return SchedulesSerializer


class AdminPlayersSerializerList(ListCreateAPIView):
    queryset = Players.objects.all()
    serializer_class = PlayersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PlayersSerializer
        else:
            return PlayersSerializer


class AdminPlayersSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Players.objects.all()
    serializer_class = PlayersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PlayersSerializer
        else:
            return PlayersSerializer


class AdminSquadsSerializerList(ListCreateAPIView):
    queryset = Squads.objects.all()
    serializer_class = SquadsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SquadsSerializer
        else:
            return SquadsSerializer


class AdminSquadsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Squads.objects.all()
    serializer_class = SquadsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SquadsSerializer
        else:
            return SquadsSerializer


class AdminTVStationsSerializerList(ListCreateAPIView):
    queryset = TVStations.objects.all()
    serializer_class = TVStationsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TVStationsSerializer
        else:
            return TVStationsSerializer


class AdminTVStationsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = TVStations.objects.all()
    serializer_class = TVStationsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TVStationsSerializer
        else:
            return TVStationsSerializer


class AdminCoachesSerializerList(ListCreateAPIView):
    queryset = Coaches.objects.all()
    serializer_class = CoachesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CoachesSerializer
        else:
            return CoachesSerializer


class AdminCoachesSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Coaches.objects.all()
    serializer_class = CoachesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CoachesSerializer
        else:
            return CoachesSerializer


class AdminTopScorersSerializerList(ListCreateAPIView):
    queryset = TopScorers.objects.all()
    serializer_class = TopScorersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TopScorersSerializer
        else:
            return TopScorersSerializer


class AdminTopScorersSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = TopScorers.objects.all()
    serializer_class = TopScorersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TopScorersSerializer
        else:
            return TopScorersSerializer


class AdminRivalsSerializerList(ListCreateAPIView):
    queryset = Rivals.objects.all()
    serializer_class = RivalsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RivalsSerializer
        else:
            return RivalsSerializer


class AdminRivalsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Rivals.objects.all()
    serializer_class = RivalsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RivalsSerializer
        else:
            return RivalsSerializer


class AdminCommentariesSerializerList(ListCreateAPIView):
    queryset = Commentaries.objects.all()
    serializer_class = CommentariesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CommentariesSerializer
        else:
            return CommentariesSerializer


class AdminCommentariesSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Commentaries.objects.all()
    serializer_class = CommentariesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CommentariesSerializer
        else:
            return CommentariesSerializer


class AdminRefereesSerializerList(ListCreateAPIView):
    queryset = Referees.objects.all()
    serializer_class = RefereesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RefereesSerializer
        else:
            return RefereesSerializer


class AdminRefereesSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Referees.objects.all()
    serializer_class = RefereesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RefereesSerializer
        else:
            return RefereesSerializer



class AdminTransfersSerializerList(ListCreateAPIView):
    queryset = Transfers.objects.all()
    serializer_class = TransfersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TransfersSerializer
        else:
            return TransfersSerializer


class AdminTransfersSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Transfers.objects.all()
    serializer_class = TransfersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TransfersSerializer
        else:
            return TransfersSerializer


class AdminPreMatchOddsSerializerList(ListCreateAPIView):
    queryset = PreMatchOdds.objects.all()
    serializer_class = PreMatchOddsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PreMatchOddsSerializer
        else:
            return PreMatchOddsSerializer


class AdminPreMatchOddsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = PreMatchOdds.objects.all()
    serializer_class = PreMatchOddsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PreMatchOddsSerializer
        else:
            return PreMatchOddsSerializer


class AdminInPlayOddsSerializerList(ListCreateAPIView):
    queryset = InPlayOdds.objects.all()
    serializer_class = InPlayOddsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return InPlayOddsSerializer
        else:
            return InPlayOddsSerializer


class AdminInPlayOddsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = InPlayOdds.objects.all()
    serializer_class = InPlayOddsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return InPlayOddsSerializer
        else:
            return InPlayOddsSerializer


class AdminMarketsSerializerList(ListCreateAPIView):
    queryset = Markets.objects.all()
    serializer_class = MarketsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MarketsSerializer
        else:
            return MarketsSerializer


class AdminMarketsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Markets.objects.all()
    serializer_class = MarketsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MarketsSerializer
        else:
            return MarketsSerializer


class AdminBookmakersSerializerList(ListCreateAPIView):
    queryset = Bookmakers.objects.all()
    serializer_class = BookmakersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BookmakersSerializer
        else:
            return BookmakersSerializer


class AdminBookmakersSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Bookmakers.objects.all()
    serializer_class = BookmakersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BookmakersSerializer
        else:
            return BookmakersSerializer


class AdminMatchSerializerList(ListCreateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchSerializer
        else:
            return MatchSerializer


class AdminMatchSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchSerializer
        else:
            return MatchSerializer

