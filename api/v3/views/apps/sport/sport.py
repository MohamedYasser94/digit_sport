from django.http import JsonResponse
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.v3.serializers.blog import AdminBlogArticleSerializer, AdminBlogVideoSerializer
from api.v3.serializers.sport import *
from core.models.blog import BlogArticle, BlogVideo


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
    serializer_class = SportSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SportSerializer
        else:
            return SportSerializer


class AdminSportSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Sport.objects.all()
    serializer_class = SportSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SportSerializer
        else:
            return SportSerializer


class AdminLeaguesSerializerListold(ListCreateAPIView):
    queryset = Leagues.objects.all()
    serializer_class = LeaguesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LeaguesSerializer
        else:
            return LeaguesSerializer


def AdminLeaguesSerializerList(request):
    league_list = Leagues.objects.all()
    success = True
    data = {}
    message = "Send From Django API"
    serializer = LeaguesSerializer(league_list, many=True)

    data = {'success': success, 'data': serializer.data, 'message': message,

    }
    return JsonResponse(data, safe=False)


class AdminLeaguesSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Leagues.objects.all()
    serializer_class = LeaguesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LeaguesSerializer
        else:
            return LeaguesSerializer


class AdminLeaguesAPiByCountryList(ListCreateAPIView):
    queryset = Leagues.objects.all()
    serializer_class = LeaguesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        country = self.kwargs['country']
        return Leagues.objects.filter(country=country)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LeaguesSerializer
        else:
            return LeaguesSerializer


class AdminLeaguesAPiSearchList(ListCreateAPIView):
    queryset = Leagues.objects.all()
    serializer_class = LeaguesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        search = self.kwargs['name']
        return Leagues.objects.filter(name__icontains=search)

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


class AdminSeasonAPiByTeamList(ListCreateAPIView):
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


class AdminTeamsSerializerListold(ListCreateAPIView):
    queryset = Teams.objects.all()
    serializer_class = TeamsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TeamsSerializer
        else:
            return TeamsSerializer


def AdminTeamsSerializerList(request):
    team_list = Teams.objects.all()
    success = True
    data = {}
    message = "Send From Django API"
    serializer = TeamsSerializer(team_list, many=True)

    data = {'success': success, 'data': serializer.data, 'message': message,

    }
    return JsonResponse(data, safe=False)


class AdminTeamsSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = Teams.objects.all()
    serializer_class = TeamsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TeamsSerializer
        else:
            return TeamsSerializer


class AdminTeamsAPiByCountryList(ListCreateAPIView):
    queryset = Teams.objects.all()
    serializer_class = TeamsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        country = self.kwargs['country']
        return Teams.objects.filter(country=country)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TeamsSerializer
        else:
            return TeamsSerializer


class AdminTeamsAPiSearchList(ListCreateAPIView):
    queryset = Teams.objects.all()
    serializer_class = TeamsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        search = self.kwargs['name']
        return Teams.objects.filter(name__icontains=search)

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


class AdminPlayersAPiLatestList(ListCreateAPIView):
    queryset = Players.objects.all()
    serializer_class = PlayersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return Players.objects.all().order_by('-id')[:10]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PlayersSerializer
        else:
            return PlayersSerializer


class AdminPlayersAPiByCountryList(ListCreateAPIView):
    queryset = Players.objects.all()
    serializer_class = PlayersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        country = self.kwargs['country']
        return Players.objects.filter(country=country)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PlayersSerializer
        else:
            return PlayersSerializer


class AdminPlayersAPiByTeamList(ListCreateAPIView):
    queryset = Players.objects.all()
    serializer_class = PlayersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        team = self.kwargs['team']
        return Players.objects.filter(team=team)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PlayersSerializer
        else:
            return PlayersSerializer


class AdminPlayersAPiSearchList(ListCreateAPIView):
    queryset = Players.objects.all()
    serializer_class = PlayersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        search = self.kwargs['name']
        return Players.objects.filter(name__icontains=search)

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
            return MatchDetailsSerializer
        else:
            return MatchSerializer


class AdminMatchAPiLatestList(ListCreateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return Match.objects.all().order_by('-id')[:10]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchSerializer
        else:
            return MatchSerializer


class AdminMatchAPiByLeagueList(ListCreateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchSerializer
        else:
            return MatchSerializer


class AdminMatchAPiByTeamList(ListCreateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        team = self.kwargs['team']
        return Match.objects.filter(team=team)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchSerializer
        else:
            return MatchSerializer


class AdminMatchAPiSearchList(ListCreateAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        search = self.kwargs['name']
        return Match.objects.filter(name__icontains=search)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchSerializer
        else:
            return MatchSerializer


class AdminMatchTeamPlayerSerializerList(ListCreateAPIView):
    queryset = MatchTeamPlayer.objects.all()
    serializer_class = MatchTeamPlayerSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchTeamPlayerSerializer
        else:
            return MatchTeamPlayerSerializer


class AdminMatchTeamPlayerSerializerDetail(RetrieveUpdateDestroyAPIView):
    queryset = MatchTeamPlayer.objects.all()
    serializer_class = MatchTeamPlayerSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchTeamPlayerSerializer
        else:
            return MatchTeamPlayerSerializer


class AdminMatchTeamPlayerAPiByTeamList(ListCreateAPIView):
    queryset = MatchTeamPlayer.objects.all()
    serializer_class = MatchTeamPlayerSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchTeamPlayerSerializer
        else:
            return MatchTeamPlayerSerializer


class AdminMatchTeamPlayerAPiByMatchList(ListCreateAPIView):
    queryset = MatchTeamPlayer.objects.all()
    serializer_class = MatchTeamPlayerSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchTeamPlayerSerializer
        else:
            return MatchTeamPlayerSerializer


class AdminMatchTeamPlayerAPiByPlayerList(ListCreateAPIView):
    queryset = MatchTeamPlayer.objects.all()
    serializer_class = MatchTeamPlayerSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchTeamPlayerSerializer
        else:
            return MatchTeamPlayerSerializer


class AdminMatchTeamPlayerAPiSearchList(ListCreateAPIView):
    queryset = MatchTeamPlayer.objects.all()
    serializer_class = MatchTeamPlayerSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MatchTeamPlayerSerializer
        else:
            return MatchTeamPlayerSerializer


############# Mix Serializer #####################
def SportByCountryApiList(request, country):
    print()
    if country == '' or country == None or country == 'all' or country == ':country':
        country = 'Kuwait'
    else:
        country = country
    sport_list = Sport.objects.filter(country=country)
    league_list = Leagues.objects.filter(country=country)
    team_list = Teams.objects.filter(country=country)
    match_list = Match.objects.filter(league__country=country)
    news_list = BlogArticle.objects.filter(country=country)
    video_list = BlogVideo.objects.filter(country=country)
    success = True
    message = f"Send From Django API mix {country}"
    sport_serializer = SportSerializer(sport_list, many=True)
    league_serializer = LeaguesSerializer(league_list, many=True)
    team_serializer = TeamsSerializer(team_list, many=True)
    match_serializer = MatchSerializer(match_list, many=True)
    news_serializer = AdminBlogArticleSerializer(news_list, many=True)
    video_serializer = AdminBlogVideoSerializer(video_list, many=True)

    sport_data = {'sport': sport_serializer.data, 'league': league_serializer.data, 'team': team_serializer.data,
                  'match': match_serializer.data, 'news': news_serializer.data, 'video': video_serializer.data}

    sport_data = {'country': country,
        'sport': sport_serializer.data,
                  }



    data = {'success': success, 'data': sport_data, 'message': message,

    }
    return JsonResponse(data, safe=False)
