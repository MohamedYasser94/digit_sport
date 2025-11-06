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
    state = serializers.JSONField(source='state_data', required=False, allow_null=True)
    periods = serializers.JSONField(required=False, allow_null=True)
    events = serializers.JSONField(required=False, allow_null=True)  
    class Meta:
        model = Fixtures
        fields = [
            'api_id', 'name', 'starting_at', 'result_info', 'leg', 'details', 'length',
            'statistics', 'events', 'lineups', 'participants', 'scores', 'state', 'periods', 'events'
        ]


# This serializer is for the top-level league information
class SimpleLeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leagues
        fields = ['api_id', 'name', 'image_path', 'country','currentseason']


class PlyerSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    league = LeagueSerializer(read_only=True)

    class Meta:
        model = Players
        fields = [
            'id', 'api_id', 'common_name', 'display_name', 'first_name', 'last_name',
            'position', 'height', 'weight', 'birthdate', 'nationality', 'image_path',
            'team', 'league'
        ]

class MatchTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teams
        fields = ['id', 'name', 'code', 'image', 'image_path']  

class matchLeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leagues
        fields = ['id', 'name', 'country', 'type', 'image', 'country_image']

class matchVenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venues
        fields = ['id', 'name', 'location', 'capacity']  

class matchSeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['id', 'name', ] 

class FixtureDetailsSerializer(serializers.ModelSerializer):
    league = matchLeagueSerializer(read_only=True)
    season = matchSeasonSerializer(read_only=True)
    venue = matchVenueSerializer(read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True, source='participants.all')  
    match_status = serializers.SerializerMethodField()
    match_datetime = serializers.SerializerMethodField()
    
    class Meta:
        model = Fixtures
        fields = [
            'id', 'name', 'participants',  
            'match_datetime', 'league', 'season', 'venue', 'result_info', 'state', 
            'match_status', 'statistics', 'events', 'scores', 'create_at', 'update_at'
        ]

    def _get_team_image_url(self, team, request):
        if team.image_path:
            return team.image_path
        if team.image and hasattr(team.image, 'url'):
            if request:
                return request.build_absolute_uri(team.image.url)
            else:
                return team.image.url
        return ""
    
    def _extract_team_from_scores(self, obj, team_type):
        if obj.scores and isinstance(obj.scores, list):
            for score_item in obj.scores:
                if (isinstance(score_item, dict) and 
                    score_item.get('score', {}).get('meta_location') == team_type):
                    team_name = score_item.get('score', {}).get('participant_name', '').strip()
                    return team_name if team_name else f"{team_type.title()} Team"
        teams = self._extract_teams_from_name(obj.name)
        if team_type == 'home':
            return teams[0] if teams[0] else "Home Team"
        else:
            return teams[1] if len(teams) > 1 and teams[1] else "Away Team"

    def _extract_teams_from_name(self, name):
        if not name:
            return ['Home Team', 'Away Team']
        if name and len(set(name)) == 1:
            return ['Home Team', 'Away Team']
        separators = [' vs ', ' - ', ' @ ']
        for sep in separators:
            if sep in name:
                parts = name.split(sep)
                if len(parts) >= 2:
                    team1 = parts[0].strip() or 'Home Team'
                    team2 = parts[1].strip() or 'Away Team'
                    return [team1, team2]
        return [name or 'Home Team', 'Away Team']

    def get_match_status(self, obj):
        if obj.time_status == 'LIVE':
            return 'live'
        elif obj.state == 'FT' or obj.state == 'finished':
            return 'finished'
        else:
            return 'upcoming'

    def get_match_datetime(self, obj):
        if obj.starting_at:
            return obj.starting_at.strftime('%Y-%m-%d %H:%M')
        return None



class FixtureGoalsSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    player = serializers.CharField(required=False)
    team = serializers.CharField(required=False)
    minute = serializers.IntegerField(required=False)
    type = serializers.CharField(required=False)
    set = serializers.CharField(required=False)
    
    def to_representation(self, instance):
        if isinstance(instance, dict):
            return {
                'id': instance.get('id'),
                'player': instance.get('player', {}).get('name') if isinstance(instance.get('player'), dict) else instance.get('player'),
                'team': instance.get('team', {}).get('name') if isinstance(instance.get('team'), dict) else instance.get('team'),
                'minute': instance.get('minute'),
                'type': instance.get('type'),
                'set': instance.get('set', '1stSet')
            }
        return instance

class MatchGoalsSerializer(serializers.ModelSerializer):
    home_team = MatchTeamSerializer(read_only=True)
    away_team = MatchTeamSerializer(read_only=True)
    match = serializers.StringRelatedField()
    match_info = serializers.SerializerMethodField()
    set_display = serializers.SerializerMethodField()
    
    class Meta:
        model = MatchGoals
        fields = [
            'id', 'match', 'match_info',
            'home_team', 'away_team',
            'home_score', 'away_score', 
            'set', 'set_display',
            'create_at', 'update_at'
        ]
    
    def get_match_info(self, obj):
        if obj.match:
            return {
                'id': obj.match.id,
                'name': obj.match.name,
                'start_time': obj.match.start_time.strftime('%Y-%m-%d %H:%M') if obj.match.start_time else None,
                'location': obj.match.location
            }
        return None
    
    def get_set_display(self, obj):
        return dict(Set_List).get(obj.set, obj.set) if obj.set else None

class TeamSeasonTableSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    league = LeagueSerializer(read_only=True)
    goal_difference_display = serializers.SerializerMethodField()
    form_matches = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamSeasonTable
        fields = [
            'id', 'team', 'league', 'position', 'points', 
            'played', 'win', 'draw', 'lose', 'remaining',
            'goals_for', 'goals_against', 'goals_difference', 'goal_difference_display',
            'goals_for_run', 'goals_against_run', 'goals_difference_run',
            'percentage', 'form', 'form_matches', 'description',
            'create_at', 'update_at'
        ]
        ordering = ['position']
    
    def get_goal_difference_display(self, obj):
        if obj.goals_difference > 0:
            return f"+{obj.goals_difference}"
        elif obj.goals_difference < 0:
            return f"{obj.goals_difference}"
        return "0"
    
    def get_form_matches(self, obj):
        if obj.form:
            return list(obj.form)
        return []
