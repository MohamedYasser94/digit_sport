from datetime import datetime

from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from api.v3.serializers.sport.monk import *
from api.v3.serializers.sport.sport import *
from apps.sport.models.models import *
from apps.sport.models.monks import *
from core.models.blog import BlogArticle, BlogVideo

from rest_framework.pagination import PageNumberPagination

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


def SportTeamsByCountryApiList(request, country,sport):

    if country == '' or country == None or country == 'all' or country == ':country':
        country = 'Kuwait'
    else:
        country = country
    if sport == '' or sport == None or sport == 'all' or sport == ':sport':
        sport = 'Volleyball'
    sport_list = Sport.objects.filter(name=sport)

    if sport_list.count() > 0:
        get_sport = Sport.objects.get(name=sport)
        teams_list = Teams.objects.filter(sport=get_sport.id, country=country)
        success = True
        message = f"Send From Django API mix {country}"
        sport_serializer = SportSerializer(sport_list, many=True)
        team_serializer = TeamsSerializer(teams_list, many=True)
        sport_data = {'country': country,
                      'sport': sport_serializer.data,
                        'team': team_serializer.data,
                      }
    else:
        success = False
        message = f"error in get data no data no data with this country {country} or sport {sport}"

        sport_data = {'country': country,
                      'sport': [],
                        'team': [],
                      }

    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)

def SportCountryList(request):

    country_list = MonkCountry.objects.all()




    if country_list.count() > 0:

        success = True
        message = f"Send From Django API mix "
        country_serializer = AdminMonkCountrySerializer(country_list, many=True)

        sport_data = {
                      'country': country_serializer.data,

                      }
    else:
        success = False
        message = f"error in get data no data no data with this country "

        sport_data = {
                      'country': [],

                      }

    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)



def SportLeaguesByCountryApiList(request, country,sport):

    if country == '' or country == None or country == 'all' or country == ':country':
        country = 'Kuwait'
    else:
        country = country
    if sport == '' or sport == None or sport == 'all' or sport == ':sport':
        sport = 'Volleyball'
    sport_list = Sport.objects.filter(name=sport, )
    if sport_list.count() > 0:
        get_sport = Sport.objects.get(name=sport)
        leagues_list = Leagues.objects.filter(sport=get_sport.id, country=country)
        success = True
        message = f"Send From Django API mix {country}"
        sport_serializer = SportSerializer(sport_list, many=True)
        league_serializer = LeaguesSerializer(leagues_list, many=True)
        sport_data = {'country': country,
                      'sport': sport_serializer.data,
                        'league': league_serializer.data,
                      }

    else:
        success = False
        message = f"error in get data no data no data with this country {country} or sport {sport}"

        sport_data = {'country': country,
                      'sport': [],
                        'league': [],
                      }

    data = {'success': success, 'data': sport_data, 'message': message,

                }
    return JsonResponse(data, safe=False)
@api_view(["GET"])
def SportPlayersByCountryApiList(request, country,sport):
    if country == '' or country == None or country == 'all' or country == ':country':
        country = 'Kuwait'
    else:
        country = country
    if sport == '' or sport == None or sport == 'all' or sport == ':sport':
        sport = 'Volleyball'
    get_sport = Sport.objects.get(name=sport)
    players_list = Players.objects.filter(country=country)
    if players_list.count() > 0:
        paginator = PageNumberPagination()
        paginator.page_size = 10
        players_list = Players.objects.filter(country=country)
        result_page = paginator.paginate_queryset(players_list, request)

        success = True
        message = f"Send From Django API mix {country}"
        players_serializer = PlayersSerializer(result_page, many=True)
        sport_data = {'country': country,
                        'player': players_serializer.data,
                      }
    else:
        success = False
        message = f"error in get data no data no data with this country {country} or sport {sport}"

        sport_data = {'country': country,

                        'player': [],
                      }
    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)


def SportMatchesByCountryApiList(request, country,sport):
    print()
    if country == '' or country == None or country == 'all' or country == ':country':
        country = 'Kuwait'
    else:
        country = country
    if sport == '' or sport == None or sport == 'all' or sport == ':sport':
        sport = 'Volleyball'
    sport_list = Sport.objects.all()
    if sport_list.count() > 0:
        get_sport = Sport.objects.get(name=sport)
        matches_list = Match.objects.all().order_by('-start_time')
        success = True
        message = f"Send From Django API mix {country}"
        sport_serializer = SportSerializer(sport_list, many=True)
        match_serializer = MatchSerializer(matches_list, many=True)

        sport_data = {'country': country,
                      'sport': sport_serializer.data,
                        'match': match_serializer.data,
                      }

    else:
        success = False
        message = f"error in get data no data no data with this country {country} or sport {sport}"

        sport_data = {'country': country,
                      'sport': [],
                        'match': [],
                      }

    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)

def SportMatchesLastApiList(request,sport, date):

    if date == '' or date == None or date == 'all' or date == ':date':
        date = datetime.now()
    else:
        date = date
    if sport == '' or sport == None or sport == 'all' or sport == ':sport':
        sport = Sport.objects.all()
        matches_list = Match.objects.filter( start_time__date=date).order_by('start_time')
    else:
        sport = sport
        matches_list = Match.objects.filter(league__sport=sport, start_time__date=date).order_by('start_time')
    if matches_list.count() > 0:



        success = True
        message = f"Send From Django API mix "

        match_serializer = MatchSerializer(matches_list, many=True)

        sport_data = {'date': date,

                        'match': match_serializer.data,
                      }

    else:
        success = False
        message = f"error in get data no data no data with this date {date} "

        sport_data = {'date': date,

                        'match': [],
                      }

    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)


def SportMatchesApiDetails(request, matchid):

        try:
            matches_list = Match.objects.filter(id=matchid)
            get_match = Match.objects.get(id=matchid)
            home_team = Teams.objects.filter(id=get_match.home_team.id)
            away_team = Teams.objects.filter(id=get_match.away_team.id)
            home_team_players = MatchTeamPlayer.objects.filter(match=matchid, team=get_match.home_team.id)
            away_team_players = MatchTeamPlayer.objects.filter(match=matchid, team=get_match.away_team.id)
            summary_list = MatchSummary.objects.filter(match=matchid)
            statics_list = MatchStatics.objects.filter(match=matchid)

            match_serializer = MatchDetailsSerializer(matches_list, many=True)
            home_team_serializer = TeamsSerializer(home_team, many=True)
            away_team_serializer = TeamsSerializer(away_team, many=True)
            home_team_players_serializer = MatchTeamPlayerSerializer(home_team_players, many=True)
            away_team_players_serializer = MatchTeamPlayerSerializer(away_team_players, many=True)
            summary_serializer = MatchSummarySerializer(summary_list, many=True)
            statics_serializer = MatchStaticsSerializer(statics_list, many=True)


            sport_data = {'match': match_serializer.data,
                        'home_team': home_team_serializer.data,
                        'away_team': away_team_serializer.data,
                        'home_team_players': home_team_players_serializer.data,
                        'away_team_players': away_team_players_serializer.data,
                        'summary': summary_serializer.data,
                        'statics': statics_serializer.data,

                        }
            success = True
            message = f"Send From Django API mix {matchid} "

            data = {'success': success, 'data': sport_data, 'message': message,

                    }
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(e)
            success = False
            message = f"error in get data  match Details  "

            sport_data = {'match': [],

                        }

            data = {'success': success, 'data': sport_data, 'message': message,

                    }
            return JsonResponse(data, safe=False)

def SportNewsByCountryApiList(request, country,sport):
    print()
    if country == '' or country == None or country == 'all' or country == ':country':
        country = 'Kuwait'
    else:
        country = country
    if sport == '' or sport == None or sport == 'all' or sport == ':sport':
        sport = 'Volleyball'
    sport_list = Sport.objects.filter(name=sport, )
    if sport_list.count() > 0:
        get_sport = Sport.objects.get(name=sport)
        news_list = BlogArticle.objects.filter(sport=get_sport.id, country=country)
        success = True
        message = f"Send From Django API mix {country}"
        sport_serializer = SportSerializer(sport_list, many=True)
        news_serializer = AdminBlogArticleSerializer(news_list, many=True)
        sport_data = {'country': country,
                      'sport': sport_serializer.data,
                        'articles': news_serializer.data,
                      }

    else:
        success = False
        message = f"error in get data no data no data with this country {country} or sport {sport}"

        sport_data = {'country': country,
                      'sport': [],
                        'articles': [],
                      }

    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)

def SportNewsApiDetails(request, newsid):

    try:
        news_list = BlogArticle.objects.filter(id=newsid)
        success = True
        message = f"Send From Django API News Details {newsid} "
        news_serializer = AdminBlogArticleDetailsSerializer(news_list, many=True)
        sport_data = {'news': news_serializer.data,

                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=False)
    except:
        success = False
        message = f"error in get data  News Details  "

        sport_data = {'news': [],

                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=False)

def SportVideosByCountryApiList(request, country,sport):
    print()
    if country == '' or country == None or country == 'all' or country == ':country':
        country = 'Kuwait'
    else:
        country = country
    if sport == '' or sport == None or sport == 'all' or sport == ':sport':
        sport = 'Volleyball'
    sport_list = Sport.objects.filter(name=sport, )
    if sport_list.count() > 0:
        get_sport = Sport.objects.get(name=sport)
        video_list = BlogVideo.objects.filter(sport=get_sport.id, country=country)
        success = True
        message = f"Send From Django API mix {country}"
        sport_serializer = SportSerializer(sport_list, many=True)
        video_serializer = AdminBlogVideoSerializer(video_list, many=True)
        sport_data = {'country': country,
                      'sport': sport_serializer.data,
                        'video': video_serializer.data,
                      }

    else:
        success = False
        message = f"error in get data no data no data with this country {country} or sport {sport}"

        sport_data = {'country': country,
                      'sport': [],
                        'video': [],

                      }

    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)