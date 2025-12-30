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
    logo_url = serializers.SerializerMethodField()
    class Meta:
        model = MonkTeam
        fields = [
            'id', 'name', 'logo_url', 'sport',
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
    start_time = serializers.DateTimeField()
    class Meta:
        model = Match
        fields = [
            'id', 'status', 'home_score', 'away_score',
            'home_team', 'away_team', 'state', 'start_time'
        ]

    def get_state(self, obj):
        state_name = obj.played if obj.played else "Not Started"
        state_mapping = {
            'Yes': 'Full Time',
            'No': 'Not Started',
            'Live': 'LIVE',
            '1st Half': '1H',
            '2nd Half': '2H',
            'Half Time': 'HT',
            'Full Time': 'FT',
             'Not Started': 'NS'
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
        fields = ['id','api_id', 'name','name_tr', 'image_path','image','country','currentseason']

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
    
    # TransferMarket fields
    market_value = serializers.CharField(source='current_market_value', read_only=True)
    highest_market_value = serializers.CharField(read_only=True)
    preferred_foot = serializers.CharField(source='foot', read_only=True)
    citizenship = serializers.CharField(read_only=True)
    contract_expires = serializers.CharField(read_only=True)
    joined = serializers.CharField(read_only=True)
    player_agent = serializers.CharField(source='player_agent_name', read_only=True)
    outfitter = serializers.CharField(read_only=True)
    place_of_birth_city = serializers.CharField(read_only=True)
    place_of_birth_country = serializers.CharField(read_only=True)
    transfermarkt_id = serializers.CharField(read_only=True)
    transfermarkt_url = serializers.CharField(read_only=True)
    market_value_last_updated = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Players
        fields = [
            'id', 'name', 'shirt_number', 'date_of_birth', 'age', 'position', 'nationality',
            'team_name', 'sport_name', 'image_path', 'height', 'weight', 'gender',
            # TransferMarket fields
            'market_value', 'highest_market_value', 'preferred_foot', 'citizenship',
            'contract_expires', 'joined', 'player_agent', 'outfitter',
            'place_of_birth_city', 'place_of_birth_country',
            'transfermarkt_id', 'transfermarkt_url', 'market_value_last_updated'
        ]


class PlayerTransferSerializer(serializers.ModelSerializer):
    """
    Serializer for player transfer history.
    Returns transfer details including from/to teams, fee, and date.
    Falls back to text team names when FK is null.
    """
    from_team_id = serializers.IntegerField(source='from_team.id', read_only=True, allow_null=True)
    from_team_name = serializers.SerializerMethodField()
    from_team_logo = serializers.SerializerMethodField()

    to_team_id = serializers.IntegerField(source='to_team.id', read_only=True, allow_null=True)
    to_team_name = serializers.SerializerMethodField()
    to_team_logo = serializers.SerializerMethodField()

    transfer_date = serializers.DateField(source='date', read_only=True)
    transfer_fee = serializers.CharField(source='fee', read_only=True)
    transfer_fee_numeric = serializers.IntegerField(source='fee_numeric', read_only=True)
    is_free_transfer = serializers.SerializerMethodField()
    is_loan = serializers.BooleanField(read_only=True)
    market_value_at_transfer = serializers.CharField(source='market_value', read_only=True)
    market_value_numeric = serializers.IntegerField(source='market_value_numeric', read_only=True)
    currency = serializers.CharField(source='market_value_currency', read_only=True)
    season = serializers.CharField(read_only=True)

    class Meta:
        model = Transfers
        fields = [
            'id', 'transfer_date', 'season',
            'from_team_id', 'from_team_name', 'from_team_logo',
            'to_team_id', 'to_team_name', 'to_team_logo',
            'transfer_fee', 'transfer_fee_numeric', 'is_free_transfer', 'is_loan',
            'market_value_at_transfer', 'market_value_numeric', 'currency',
            'position'
        ]

    def get_from_team_name(self, obj):
        """Get from team name - prefer FK, fallback to text field"""
        if obj.from_team:
            return obj.from_team.name
        return getattr(obj, 'from_team_name', None)

    def get_to_team_name(self, obj):
        """Get to team name - prefer FK, fallback to text field"""
        if obj.to_team:
            return obj.to_team.name
        return getattr(obj, 'to_team_name', None)

    def get_from_team_logo(self, obj):
        if obj.from_team:
            if obj.from_team.image_path:
                return obj.from_team.image_path
            elif obj.from_team.image and hasattr(obj.from_team.image, 'url'):
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.from_team.image.url)
                return obj.from_team.image.url
        return None

    def get_to_team_logo(self, obj):
        if obj.to_team:
            if obj.to_team.image_path:
                return obj.to_team.image_path
            elif obj.to_team.image and hasattr(obj.to_team.image, 'url'):
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.to_team.image.url)
                return obj.to_team.image.url
        return None

    def get_is_free_transfer(self, obj):
        return obj.free_transfer == 'Yes'


class PlayerMarketValueHistorySerializer(serializers.Serializer):
    """Serializer for player market value history"""
    date = serializers.DateField()
    age = serializers.IntegerField()
    market_value = serializers.IntegerField()
    market_value_formatted = serializers.CharField()
    club_name = serializers.CharField()
    club_tm_id = serializers.CharField()


class PlayerSeasonStatsSerializer(serializers.Serializer):
    """Serializer for player season stats"""
    season = serializers.CharField()
    competition_name = serializers.CharField()
    club_name = serializers.CharField()
    appearances = serializers.IntegerField()
    goals = serializers.IntegerField()
    assists = serializers.IntegerField()
    yellow_cards = serializers.IntegerField()
    red_cards = serializers.IntegerField()
    minutes_played = serializers.IntegerField()


class PlayerAchievementSerializer(serializers.Serializer):
    """Serializer for player achievements/trophies"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    achievement_type = serializers.CharField()
    competition_name = serializers.CharField()
    club_name = serializers.CharField()
    season = serializers.CharField()
    year = serializers.IntegerField()
    count = serializers.IntegerField()
    is_international = serializers.BooleanField()


class PlayerWithTransfersSerializer(serializers.ModelSerializer):
    """
    Extended player serializer that includes transfer history, market value history,
    season stats, and achievements. Use this for full player details.
    """
    shirt_number = serializers.CharField(source='number', read_only=True)
    date_of_birth = serializers.CharField(source='birthdate', read_only=True)
    position = serializers.CharField(read_only=True)
    main_position = serializers.CharField(read_only=True)
    other_positions = serializers.JSONField(read_only=True)
    nationality = serializers.CharField(read_only=True)
    team_id = serializers.IntegerField(source='team.id', read_only=True)
    team_name = serializers.SerializerMethodField()
    team_logo = serializers.SerializerMethodField()
    sport_name = serializers.CharField(source='sport.name', read_only=True)

    # Basic info
    full_name = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)

    # TransferMarket fields
    market_value = serializers.CharField(source='current_market_value', read_only=True)
    market_value_numeric = serializers.IntegerField(source='current_market_value_numeric', read_only=True)
    highest_market_value = serializers.CharField(read_only=True)
    highest_market_value_numeric = serializers.IntegerField(read_only=True)
    highest_market_value_date = serializers.DateField(read_only=True)
    preferred_foot = serializers.CharField(source='foot', read_only=True)
    citizenship = serializers.CharField(read_only=True)
    citizenships = serializers.JSONField(read_only=True)
    contract_expires = serializers.CharField(read_only=True)
    contract_expires_date = serializers.DateField(read_only=True)
    joined = serializers.CharField(read_only=True)
    joined_date = serializers.DateField(read_only=True)
    player_agent = serializers.CharField(source='player_agent_name', read_only=True)
    player_agent_url = serializers.CharField(read_only=True)
    outfitter = serializers.CharField(read_only=True)
    place_of_birth_city = serializers.CharField(read_only=True)
    place_of_birth_country = serializers.CharField(read_only=True)
    transfermarkt_id = serializers.CharField(read_only=True)
    transfermarkt_url = serializers.CharField(read_only=True)
    market_value_last_updated = serializers.DateTimeField(read_only=True)
    is_retired = serializers.BooleanField(read_only=True)

    # Social media
    social_media = serializers.JSONField(read_only=True)

    # Career totals
    total_appearances = serializers.IntegerField(read_only=True)
    total_goals = serializers.IntegerField(read_only=True)
    total_assists = serializers.IntegerField(read_only=True)
    total_yellow_cards = serializers.IntegerField(read_only=True)
    total_red_cards = serializers.IntegerField(read_only=True)
    total_minutes_played = serializers.IntegerField(read_only=True)

    # Transfer history
    transfers = serializers.SerializerMethodField()
    transfer_count = serializers.SerializerMethodField()

    # Market value history
    market_value_history = serializers.SerializerMethodField()

    # Season stats
    season_stats = serializers.SerializerMethodField()

    # Achievements
    achievements = serializers.SerializerMethodField()

    class Meta:
        model = Players
        fields = [
            'id', 'api_id', 'name', 'full_name', 'display_name', 'description',
            'shirt_number', 'date_of_birth', 'age', 'position', 'main_position', 'other_positions',
            'nationality', 'team_id', 'team_name', 'team_logo', 'sport_name',
            'image_path', 'image_url', 'height', 'weight', 'gender',
            # TransferMarket fields
            'market_value', 'market_value_numeric', 'highest_market_value',
            'highest_market_value_numeric', 'highest_market_value_date',
            'preferred_foot', 'citizenship', 'citizenships',
            'contract_expires', 'contract_expires_date', 'joined', 'joined_date',
            'player_agent', 'player_agent_url', 'outfitter',
            'place_of_birth_city', 'place_of_birth_country',
            'transfermarkt_id', 'transfermarkt_url', 'market_value_last_updated',
            'is_retired', 'social_media',
            # Career totals
            'total_appearances', 'total_goals', 'total_assists',
            'total_yellow_cards', 'total_red_cards', 'total_minutes_played',
            # Related data
            'transfers', 'transfer_count', 'market_value_history', 'season_stats', 'achievements'
        ]

    def get_team_name(self, obj):
        """Get team name - prefer FK, fallback to text field"""
        if obj.team:
            return obj.team.name
        return obj.team_text

    def get_team_logo(self, obj):
        if obj.team:
            if obj.team.image_path:
                return obj.team.image_path
            elif obj.team.image and hasattr(obj.team.image, 'url'):
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.team.image.url)
                return obj.team.image.url
        return None

    def get_transfers(self, obj):
        """Get player's transfer history, ordered by date (most recent first)"""
        transfers = Transfers.objects.filter(player=obj).select_related(
            'from_team', 'to_team'
        ).order_by('-date')[:20]  # Limit to last 20 transfers
        return PlayerTransferSerializer(transfers, many=True, context=self.context).data

    def get_transfer_count(self, obj):
        """Get total number of transfers for this player"""
        return Transfers.objects.filter(player=obj).count()

    def get_market_value_history(self, obj):
        """Get player's market value history"""
        try:
            from apps.sport.models.models import PlayerMarketValueHistory
            history = PlayerMarketValueHistory.objects.filter(player=obj).order_by('-date')[:50]
            return PlayerMarketValueHistorySerializer(history, many=True).data
        except Exception:
            return []

    def get_season_stats(self, obj):
        """Get player's season statistics"""
        try:
            from apps.sport.models.models import PlayerSeasonStats
            stats = PlayerSeasonStats.objects.filter(player=obj).order_by('-season')[:30]
            return PlayerSeasonStatsSerializer(stats, many=True).data
        except Exception:
            return []

    def get_achievements(self, obj):
        """Get player's achievements/trophies"""
        try:
            from apps.sport.models.models import PlayerAchievement
            achievements = PlayerAchievement.objects.filter(player=obj).order_by('-year', '-season')
            return PlayerAchievementSerializer(achievements, many=True).data
        except Exception:
            return []


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

class SeasonDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['id', 'name', 'starting_at', 'ending_at']

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
            league_image = 'https://jawlasp.com' + str(obj.league.image.url)
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

class TeamPlayerSimpleSerializer(serializers.ModelSerializer):
    shirt_number = serializers.CharField(source='number', read_only=True)
    
    class Meta:
        model = Players
        fields = [
            'id','name','shirt_number','position','nationality','image_path','age'
        ]

class TeamBasicInfoSerializer(serializers.ModelSerializer):
    stadium_name = serializers.CharField(read_only=True, source='venue.name', allow_null=True)
    coach_name = serializers.SerializerMethodField()
    current_players = serializers.SerializerMethodField()
    
    class Meta:
        model = Teams
        fields = [
            'id','name','founded','country','stadium_name','coach_name','image','image_path','current_players'
        ]
    
    def get_coach_name(self, obj):
        return getattr(obj, 'coach', None) or "Not Available"
    
    def get_current_players(self, obj):
        try:
            current_players = Players.objects.filter(
                team=obj.id,
                status='Active',
            ).select_related('team').order_by('position', 'number')
            
            serializer = TeamPlayerSimpleSerializer(
                current_players,
                many=True,
                context=self.context
            )
            return serializer.data
            
        except Exception as e:
            print(f"Error getting current players for team {obj.id}: {str(e)}")
            return []        


class LeagueSearchSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Leagues
        fields = ['id', 'name', 'image', 'sport_name', 'country', 'currentseason']

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.image.url)
                return obj.image.url
            except:
                pass
        return obj.image_path

class TeamSearchSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Teams
        fields = ['id', 'name', 'image', 'sport_name', 'country', 'gender']

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.image.url)
                return obj.image.url
            except:
                pass
        return obj.image_path

class PlayerSearchSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Players
        fields = ['id', 'name', 'image', 'position', 'team_name', 'sport_name', 'nationality']

    def get_image(self, obj):
        if obj.image:
            try:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.image.url)
                return obj.image.url
            except:
                pass
        return obj.image_path