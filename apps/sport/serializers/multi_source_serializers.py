from rest_framework import serializers
from ..models import MultiSourcePlayers, DataSource, PlayerDataSourceInfo, PlayerDataConflict


class DataSourceSerializer(serializers.ModelSerializer):
    players_count = serializers.SerializerMethodField()
    primary_for_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DataSource
        fields = '__all__'
    
    def get_players_count(self, obj):
        return MultiSourcePlayers.objects.filter(data_sources=obj).count()
    
    def get_primary_for_count(self, obj):
        return MultiSourcePlayers.objects.filter(primary_data_source=obj).count()


class PlayerDataSourceInfoSerializer(serializers.ModelSerializer):
    data_source_name = serializers.CharField(source='data_source.name', read_only=True)
    last_updated_by_name = serializers.CharField(source='last_updated_by.username', read_only=True)
    
    class Meta:
        model = PlayerDataSourceInfo
        fields = '__all__'


class PlayerDataConflictSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(source='player.name', read_only=True)
    source_1_name = serializers.CharField(source='source_1.name', read_only=True)
    source_2_name = serializers.CharField(source='source_2.name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = PlayerDataConflict
        fields = '__all__'


class MultiSourcePlayersListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    primary_data_source_name = serializers.CharField(source='primary_data_source.name', read_only=True)
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    market_value_display = serializers.SerializerMethodField()
    sources_count = serializers.SerializerMethodField()
    conflicts_count = serializers.SerializerMethodField()
    primary_id = serializers.SerializerMethodField()
    
    class Meta:
        model = MultiSourcePlayers
        fields = [
            'id', 'name', 'display_name', 'sport_name', 'team_name', 'position',
            'market_value_display', 'primary_data_source_name', 'sources_count',
            'conflicts_count', 'primary_id', 'status', 'create_at', 'update_at'
        ]
    
    def get_market_value_display(self, obj):
        return obj.get_market_value_display()
    
    def get_sources_count(self, obj):
        return obj.data_sources.count()
    
    def get_conflicts_count(self, obj):
        return obj.conflicts.filter(resolved=False).count()
    
    def get_primary_id(self, obj):
        return obj.get_primary_id()


class MultiSourcePlayersDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual player view"""
    primary_data_source_name = serializers.CharField(source='primary_data_source.name', read_only=True)
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    league_names = serializers.SerializerMethodField()
    name_source_name = serializers.CharField(source='name_source.name', read_only=True)
    image_source_name = serializers.CharField(source='image_source.name', read_only=True)
    market_value_source_name = serializers.CharField(source='market_value_source.name', read_only=True)
    market_value_display = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    country_image_url = serializers.SerializerMethodField()
    primary_id = serializers.SerializerMethodField()
    source_info = PlayerDataSourceInfoSerializer(many=True, read_only=True)
    unresolved_conflicts = serializers.SerializerMethodField()
    
    class Meta:
        model = MultiSourcePlayers
        fields = '__all__'
    
    def get_league_names(self, obj):
        return [league.name for league in obj.league.all()]
    
    def get_market_value_display(self, obj):
        return obj.get_market_value_display()
    
    def get_image_url(self, obj):
        return obj.get_image()
    
    def get_country_image_url(self, obj):
        return obj.get_country_image()
    
    def get_primary_id(self, obj):
        return obj.get_primary_id()
    
    def get_unresolved_conflicts(self, obj):
        conflicts = obj.conflicts.filter(resolved=False)
        return PlayerDataConflictSerializer(conflicts, many=True).data


class MultiSourcePlayersCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating players"""
    
    class Meta:
        model = MultiSourcePlayers
        exclude = ['code', 'slug', 'create_at', 'update_at']
    
    def create(self, validated_data):
        # Handle many-to-many fields
        leagues = validated_data.pop('league', [])
        player = MultiSourcePlayers.objects.create(**validated_data)
        if leagues:
            player.league.set(leagues)
        return player
    
    def update(self, instance, validated_data):
        # Handle many-to-many fields
        leagues = validated_data.pop('league', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if leagues is not None:
            instance.league.set(leagues)
        
        return instance


class PlayerSearchSerializer(serializers.Serializer):
    """Serializer for player search parameters"""
    name = serializers.CharField(required=False, allow_blank=True)
    sport_id = serializers.IntegerField(required=False)
    position = serializers.CharField(required=False, allow_blank=True)
    team_id = serializers.IntegerField(required=False)
    primary_data_source_id = serializers.IntegerField(required=False)
    has_conflicts = serializers.BooleanField(required=False)
    market_value_min = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    market_value_max = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)


class DataSourceStatsSerializer(serializers.Serializer):
    """Serializer for data source statistics"""
    source_name = serializers.CharField()
    total_players = serializers.IntegerField()
    primary_source_for = serializers.IntegerField()
    priority = serializers.IntegerField()
    is_active = serializers.BooleanField()


class SystemStatsSerializer(serializers.Serializer):
    """Serializer for overall system statistics"""
    total_players = serializers.IntegerField()
    total_data_sources = serializers.IntegerField()
    unresolved_conflicts = serializers.IntegerField()
    players_with_market_value = serializers.IntegerField()
    players_with_multiple_sources = serializers.IntegerField()
    source_stats = DataSourceStatsSerializer(many=True)


class ConflictResolutionSerializer(serializers.Serializer):
    """Serializer for conflict resolution requests"""
    conflict_id = serializers.IntegerField()
    resolution = serializers.ChoiceField(
        choices=['source_1', 'source_2', 'manual', 'ignore']
    )
    manual_value = serializers.CharField(required=False, allow_blank=True)


class BulkConflictResolutionSerializer(serializers.Serializer):
    """Serializer for bulk conflict resolution"""
    conflict_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    resolution = serializers.ChoiceField(
        choices=['source_1', 'source_2', 'ignore']
    )


class PlayerImportSerializer(serializers.Serializer):
    """Serializer for importing player data"""
    source = serializers.ChoiceField(
        choices=['sportmonks', 'transfermarkt', 'manual']
    )
    sport = serializers.CharField(default='football')
    data = serializers.JSONField(required=False)  # For transfermarkt/manual data
    overwrite_existing = serializers.BooleanField(default=False)


class PlayerExportSerializer(serializers.Serializer):
    """Serializer for exporting player data"""
    format = serializers.ChoiceField(
        choices=['json', 'csv', 'excel'],
        default='json'
    )
    include_conflicts = serializers.BooleanField(default=True)
    include_source_info = serializers.BooleanField(default=True)
    filters = serializers.JSONField(required=False)
