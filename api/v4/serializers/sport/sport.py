from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, serializers
from rest_framework.filters import SearchFilter

from apps.sport.models.models import *
from apps.sport.models.monks import *
from core.models.blog import *


# sports/api_views.py
#
# This file contains the primary API views for your Flutter application.
# It uses Django REST Framework (DRF) ViewSets for power and efficiency.


# -----------------------------------------------------------------------------
# SERIALIZERS
# These convert your database models into JSON format for the API.
# -----------------------------------------------------------------------------

class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'name', 'slug']


class LeagueSerializer(serializers.ModelSerializer):
    sport = SportSerializer(read_only=True)

    class Meta:
        model = Leagues
        fields = [
            'id', 'api_id', 'name',  'sport',
            'image_path', 'image', 'currentseason', 'name_tr'

        ]

class TeamWithMatchesSerializer(serializers.ModelSerializer):
    sport = SportSerializer(read_only=True)
    upcoming_fixtures = serializers.SerializerMethodField()
    previous_fixtures = serializers.SerializerMethodField()

    class Meta:
        model = Teams # FIX: Changed from MonkTeam to Teams to match your view
        fields = [
            'api_id', 'name', 'image_path', 'sport',
            'upcoming_fixtures', 'previous_fixtures'
        ]

    def get_upcoming_fixtures(self, obj):
        # Use the pre-fetched data from the context for efficiency
        all_upcoming = self.context.get('upcoming_fixtures', {})
        team_fixtures = all_upcoming.get(obj.api_id, [])
        return FixtureSerializer(team_fixtures, many=True).data

    def get_previous_fixtures(self, obj):
        # Use the pre-fetched data from the context for efficiency
        all_previous = self.context.get('previous_fixtures', {})
        team_fixtures = all_previous.get(obj.api_id, [])
        return FixtureSerializer(team_fixtures, many=True).data

class TeamSerializer(serializers.ModelSerializer):
    sport = SportSerializer(read_only=True)

    class Meta:
        model = MonkTeam
        fields = [
            'id', 'name', 'logo_url', 'sport',
            'custom_translation_name', 'custom_image_url'
        ]


class MatchSerializer(serializers.ModelSerializer):
    # Use nested serializers to include full object details
    league = LeagueSerializer(read_only=True)
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)

    class Meta:
        model = Match
        fields = [
            'id',  'status', 'home_score', 'away_score',
            'league', 'home_team', 'away_team',

        ]


# -----------------------------------------------------------------------------
# API VIEWS (VIEWSETS)
# These define the actual API endpoints your Flutter app will call.
# -----------------------------------------------------------------------------

class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows leagues to be viewed.
    Supports filtering by sport name.
    Example: /api/leagues/?sport__name=Football
    """
    queryset = MonkLeague.objects.filter(sport__isnull=False).select_related('sport')
    serializer_class = LeagueSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['sport__name', 'sport__slug']  # Filter by sport
    search_fields = ['name', 'custom_translation_name']  # Search by league name


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows teams to be viewed.
    Supports filtering by sport and searching by name.
    Example: /api/teams/?sport__slug=football&search=real
    """
    queryset = MonkTeam.objects.filter(sport__isnull=False).select_related('sport')
    serializer_class = TeamSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['sport__slug']
    search_fields = ['name', 'custom_translation_name']


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows matches to be viewed.
    This is the most important endpoint for your app.

    Supports powerful filtering:
    - By date: /api/matches/?match_date=2024-07-27
    - By league: /api/matches/?league__id=12
    - By status: /api/matches/?status=LIVE
    - By team: /api/matches/?team_id=10 (shows matches for a specific team)
    """
    queryset = Match.objects.select_related(
        'league', 'home_team', 'away_team'
    ).order_by('start_time')
    serializer_class = MatchSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]

    # Define a custom filter class for more complex lookups
    # (See implementation below)
    filterset_class = 'sports.filters.MatchFilter'  # Reference to a filter class you will create


# This serializer will format the team data inside each match
class ParticipantSerializer(serializers.ModelSerializer):
    # Using source='team' to get the nested Team object from the FixtureParticipant model
    api_id = serializers.IntegerField(source='team.api_id')
    name = serializers.CharField(source='team.name')
    image_path = serializers.CharField(source='team.image_path')

    class Meta:
        model = FixtureParticipant
        fields = ['api_id', 'name', 'image_path', 'meta_location']


# This serializer will format each individual match (fixture)
class FixtureSerializer(serializers.ModelSerializer):
    # This will nest the list of participants (home/away teams) inside each fixture
    participants = ParticipantSerializer(many=True, read_only=True)
    scores = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Fixtures
        fields = [
            'api_id', 'name', 'starting_at', 'result_info', 'leg', 'details', 'length',
            'statistics', 'events', 'lineups', 'participants', 'scores'
        ]


# This serializer is for the top-level league information
class SimpleLeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leagues
        fields = ['api_id', 'name', 'image_path', 'country','currentseason']