from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import DataSource, MultiSourcePlayers, PlayerDataSourceInfo, PlayerDataConflict


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'priority', 'is_active', 'players_count', 'primary_for_count']
    list_filter = ['is_active', 'priority']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['players_count', 'primary_for_count']

    def players_count(self, obj):
        return MultiSourcePlayers.objects.filter(data_sources=obj).count()
    players_count.short_description = 'Players with data from this source'

    def primary_for_count(self, obj):
        return MultiSourcePlayers.objects.filter(primary_data_source=obj).count()
    primary_for_count.short_description = 'Players using this as primary source'


class PlayerDataSourceInfoInline(admin.TabularInline):
    model = PlayerDataSourceInfo
    extra = 0
    readonly_fields = ['last_updated', 'last_updated_by']
    fields = ['data_source', 'is_primary', 'last_updated', 'last_updated_by', 'notes']


class PlayerDataConflictInline(admin.TabularInline):
    model = PlayerDataConflict
    extra = 0
    readonly_fields = ['created_at', 'resolved_at', 'resolved_by']
    fields = ['field_name', 'source_1', 'value_1', 'source_2', 'value_2', 'resolved', 'resolution_choice']
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(resolved=False)


@admin.register(MultiSourcePlayers)
class MultiSourcePlayersAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sport', 'position', 'get_market_value', 'primary_data_source', 
        'get_sources_count', 'get_conflicts_count', 'status'
    ]
    list_filter = [
        'sport', 'position', 'primary_data_source', 'status', 
        'market_value_source', 'name_source', 'image_source'
    ]
    search_fields = [
        'name', 'display_name', 'common_name', 'first_name', 'last_name',
        'sportmonks_api_id', 'transfermarkt_id', 'transfermarkt_code'
    ]
    readonly_fields = [
        'code', 'slug', 'get_primary_id', 'get_image_display', 'get_conflicts_count', 
        'get_sources_count', 'create_at', 'update_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 'display_name', 'common_name', 'first_name', 'last_name', 
                'name_in_home_country', 'sport', 'team', 'position', 'detailed_position'
            )
        }),
        ('API IDs', {
            'fields': (
                'sportmonks_api_id', 'transfermarkt_id', 'transfermarkt_code', 
                'manual_entry_id', 'source_ids', 'get_primary_id'
            )
        }),
        ('Physical Attributes', {
            'fields': (
                'height', 'weight', 'age', 'birthdate', 'date_of_birth', 
                'gender', 'foot', 'number'
            )
        }),
        ('Location & Nationality', {
            'fields': (
                'country', 'nationality', 'citizenship', 'city', 
                'place_of_birth_country', 'place_of_birth_city', 'birthplace'
            )
        }),
        ('Market Value & Commercial', {
            'fields': (
                'current_market_value', 'highest_market_value', 'market_value_currency',
                'market_value_numeric', 'market_value_history', 'market_value_last_updated',
                'player_agent_name', 'player_agent_href', 'outfitter', 'social_media'
            )
        }),
        ('Contract & Club', {
            'fields': (
                'joined', 'contract_expires', 'contract_extension_date',
                'current_club_name', 'current_club_href', 'in_team'
            )
        }),
        ('Images & Media', {
            'fields': (
                'image', 'image_path', 'image_url', 'get_image_display',
                'country_image', 'url'
            )
        }),
        ('Data Sources', {
            'fields': (
                'primary_data_source', 'name_source', 'image_source', 
                'market_value_source', 'get_sources_count'
            )
        }),
        ('System Fields', {
            'fields': (
                'code', 'slug', 'status', 'create_at', 'update_at', 'get_conflicts_count'
            )
        })
    )
    
    inlines = [PlayerDataSourceInfoInline, PlayerDataConflictInline]

    def get_market_value(self, obj):
        return obj.get_market_value_display()
    get_market_value.short_description = 'Market Value'

    def get_sources_count(self, obj):
        count = obj.data_sources.count()
        if count > 0:
            return format_html(
                '<a href="{}?player__id={}">{} sources</a>',
                reverse('admin:sport_playerdatasourceinfo_changelist'),
                obj.id,
                count
            )
        return '0 sources'
    get_sources_count.short_description = 'Data Sources'

    def get_conflicts_count(self, obj):
        count = obj.conflicts.filter(resolved=False).count()
        if count > 0:
            return format_html(
                '<a href="{}?player__id={}" style="color: red;">{} conflicts</a>',
                reverse('admin:sport_playerdataconflict_changelist'),
                obj.id,
                count
            )
        return '0 conflicts'
    get_conflicts_count.short_description = 'Unresolved Conflicts'

    def get_image_display(self, obj):
        image_url = obj.get_image()
        if image_url:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 25px;" />',
                image_url
            )
        return 'No image'
    get_image_display.short_description = 'Image Preview'

    def get_primary_id(self, obj):
        return obj.get_primary_id()
    get_primary_id.short_description = 'Primary ID (for Flutter app)'


@admin.register(PlayerDataSourceInfo)
class PlayerDataSourceInfoAdmin(admin.ModelAdmin):
    list_display = ['player', 'data_source', 'is_primary', 'last_updated', 'last_updated_by']
    list_filter = ['data_source', 'is_primary', 'last_updated']
    search_fields = ['player__name', 'data_source__name']
    readonly_fields = ['last_updated']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('player', 'data_source', 'last_updated_by')


@admin.register(PlayerDataConflict)
class PlayerDataConflictAdmin(admin.ModelAdmin):
    list_display = [
        'player', 'field_name', 'source_1', 'source_2', 'resolved', 
        'resolution_choice', 'created_at'
    ]
    list_filter = [
        'resolved', 'field_name', 'source_1', 'source_2', 'resolution_choice', 'created_at'
    ]
    search_fields = ['player__name', 'field_name']
    readonly_fields = ['created_at', 'resolved_at']
    
    fieldsets = (
        ('Conflict Information', {
            'fields': ('player', 'field_name', 'created_at')
        }),
        ('Source 1', {
            'fields': ('source_1', 'value_1')
        }),
        ('Source 2', {
            'fields': ('source_2', 'value_2')
        }),
        ('Resolution', {
            'fields': (
                'resolved', 'resolution_choice', 'manual_value', 
                'resolved_by', 'resolved_at'
            )
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'player', 'source_1', 'source_2', 'resolved_by'
        )

    actions = ['mark_as_resolved', 'use_source_1', 'use_source_2']

    def mark_as_resolved(self, request, queryset):
        count = queryset.filter(resolved=False).update(
            resolved=True, 
            resolution_choice='ignore',
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{count} conflicts marked as resolved (ignored).')
    mark_as_resolved.short_description = 'Mark selected conflicts as resolved (ignore)'

    def use_source_1(self, request, queryset):
        from django.utils import timezone
        count = 0
        for conflict in queryset.filter(resolved=False):
            # Apply source 1 value to the player
            setattr(conflict.player, conflict.field_name, conflict.value_1)
            conflict.player.save()
            
            # Mark conflict as resolved
            conflict.resolved = True
            conflict.resolution_choice = 'source_1'
            conflict.resolved_by = request.user
            conflict.resolved_at = timezone.now()
            conflict.save()
            count += 1
            
        self.message_user(request, f'{count} conflicts resolved using Source 1 values.')
    use_source_1.short_description = 'Resolve using Source 1 values'

    def use_source_2(self, request, queryset):
        from django.utils import timezone
        count = 0
        for conflict in queryset.filter(resolved=False):
            # Apply source 2 value to the player
            setattr(conflict.player, conflict.field_name, conflict.value_2)
            conflict.player.save()
            
            # Mark conflict as resolved
            conflict.resolved = True
            conflict.resolution_choice = 'source_2'
            conflict.resolved_by = request.user
            conflict.resolved_at = timezone.now()
            conflict.save()
            count += 1
            
        self.message_user(request, f'{count} conflicts resolved using Source 2 values.')
    use_source_2.short_description = 'Resolve using Source 2 values'
