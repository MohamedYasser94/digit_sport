from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, serializers
from rest_framework.filters import SearchFilter

from apps.sport.models.models import *
from apps.sport.models.monks import *
from apps.sport.models.operations import MatchPlayerReport, MatchPlayerReportSerializer
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

class SimpleTeamSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    custom_image_url = serializers.SerializerMethodField()
    custom_translation_name = serializers.SerializerMethodField()

    class Meta:
        model = Teams
        fields = [
            'id', 'name', 'logo_url', 
            'custom_translation_name', 'custom_image_url'
        ]

    def get_logo_url(self, obj):
        if obj.image_path:
            return obj.image_path
        elif obj.image and hasattr(obj.image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_custom_image_url(self, obj):
        return obj.image_path if obj.image_path else None

    def get_custom_translation_name(self, obj):
        return None

class MatchSerializer(serializers.ModelSerializer):
    home_team = SimpleTeamSerializer(read_only=True)
    away_team = SimpleTeamSerializer(read_only=True)
    state = serializers.SerializerMethodField()
    start_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = Match
        fields = [
            'id', 'status', 'home_score', 'away_score',
            'home_team', 'away_team', 'state', 'start_time'
        ]

    def get_state(self, obj):
        state_name = obj.played if obj.played else "Not Started"
        state_mapping = {
            'Yes': 'Full Time','No': 'Not Started','Live': 'LIVE',
            '1st Half': '1H', '2nd Half': '2H','Half Time': 'HT',
            'Full Time': 'FT', 'Not Started': 'NS'
        }
        short_name = state_mapping.get(state_name, 'NS')
        
        return {
            "name": state_name,
            "short_name": short_name
        }

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
            'team', 'league']

class NationalitySerializer(serializers.Serializer):
    name = serializers.CharField(source='nationality', read_only=True)
    api_name = serializers.CharField(source='api_nationality', read_only=True)
    flag = serializers.SerializerMethodField()
    
    def get_flag(self, obj):
        request = self.context.get('request')
        if obj.country_image:
            try:
                if request:
                    return request.build_absolute_uri(obj.country_image.url)
                return obj.country_image.url
            except:
                return None
        return None

class PlayerSerializer(serializers.ModelSerializer):
    nationality = NationalitySerializer(source='*', read_only=True)
    match_report = serializers.SerializerMethodField()
    
    class Meta:
        model = Players
        fields = ['id', 'api_id', 'common_name', 'display_name', 'first_name', 'last_name','name','position', 'number',
            'height', 'weight', 'birthdate','age','gender','nationality','image_path','match_report']
    
    def get_match_report(self, obj):
        try:
            match_id = self.context.get('match_id')
            if not match_id:
                return []
            
            match_reports = MatchPlayerReport.objects.filter(
                player_id=obj.id,
                match_id=match_id
            ).select_related('match')
            
            if not match_reports.exists():
                return []
            
            serializer = MatchPlayerReportSerializer(
                match_reports,
                many=True,
                context=self.context
            )
            return serializer.data
            
        except Exception as e:
            print(f"Error in get_match_report for player {obj.id}, match {match_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

class PlayerBasicInfoSerializer(serializers.ModelSerializer):
    shirt_number = serializers.CharField(source='number', read_only=True)
    date_of_birth = serializers.CharField(source='birthdate', read_only=True)
    position = serializers.CharField(read_only=True)
    nationality = serializers.CharField(read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    
    class Meta:
        model = Players
        fields = [
            'id','name', 'shirt_number','date_of_birth','age','position','nationality',
            'team_name','sport_name','image_path','height','weight','gender'
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


class MatchDetailsSerializer(serializers.ModelSerializer):
    venues_name = serializers.ReadOnlyField(source='venues.name')
    league_id = serializers.ReadOnlyField(source='league.id')
    league_name = serializers.ReadOnlyField(source='league.name')
    league_image = serializers.SerializerMethodField()
    sport_name = serializers.ReadOnlyField(source='sport.name')
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()
    round_name = serializers.ReadOnlyField(source='round.name')
    round_id = serializers.ReadOnlyField(source='round.id')
    match_statistics = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    season_id = serializers.ReadOnlyField(source='season.id')
    season_name = serializers.ReadOnlyField(source='season.name')


    class Meta:
        model = Match
        fields = [
            'id', 'venues_name', 'league_id', 'league_name', 'league_image', 
            'home_score', 'away_score', 'score', 'start_time', 
            'home_team', 'away_team', 'sport_name', 'round_name', 'round_id',
            'match_statistics', 'state', 'season_id', 'season_name'
        ]

    def get_league_image(self, obj):
        try:
            league_image = 'https://api.jawlasp.com' + str(obj.league.image.url)
            return league_image
        except:
            league_image = None
            return league_image

    def get_home_team(self, obj):
        request = self.context['request']
        return TeamForMatchSerializer(
            Teams.objects.get(id=obj.home_team.id), 
            many=False,
            context={'request': request}
        ).data

    def get_away_team(self, obj):
        request = self.context['request']
        return TeamForMatchSerializer(
            Teams.objects.get(id=obj.away_team.id), 
            many=False,
            context={'request': request}
        ).data
    
    def get_match_statistics(self, obj):
        try:
            match_statistics = MatchStatics.objects.filter(match=obj, status='Active')
            return MatchStaticsSerializer(match_statistics, many=True).data
        except Exception as e:
            print(f"Error in match statistics: {e}")
            return []

    def get_state(self, obj):
        if obj.played == 'Yes':
            state_data = {
                "name": 'Full Time',
                "short_name": 'FT',
            }
            return state_data
        
        else:
            state_data = {
                "name": "Not Started",
                "short_name": "NS",
            }
            return state_data    


class TeamForMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teams
        fields = ['id', 'name', 'image_path', 'image', ]

class MatchStaticsSerializer(serializers.ModelSerializer):
    type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = MatchStatics
        fields = ['type', 'type_display', 'home', 'away']
    
    def get_type_display(self, obj):
        return dict(Match_Statics).get(obj.type, obj.type) if obj.type else None

class MatchGoalsSerializer(serializers.ModelSerializer):
    set_display = serializers.SerializerMethodField()
    
    class Meta:
        model = MatchGoals
        fields = [
            'home_score', 'away_score', 'set', 'set_display'
        ] 
    
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
