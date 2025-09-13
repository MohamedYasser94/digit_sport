from django.urls import path
from .views.multi_source_fetch import (
    AdminMultiSourcePlayersGetData,
    AdminTransfermarktPlayersGetData,
    AdminManualPlayerEntry,
    AdminResolvePlayerConflicts,
    AdminGetPlayerConflicts,
    AdminGetDataSourceStats
)
from .views.multi_source_api import (
    get_players_list,
    get_player_detail,
    create_player,
    update_player,
    delete_player,
    get_data_sources,
    create_data_source,
    update_data_source,
    get_conflicts_list,
    resolve_conflict,
    bulk_resolve_conflicts,
    get_system_stats,
    get_dropdown_data,
    search_players_by_name,
    get_player_by_api_id
)
from .views.simple_transfer_market import AdminSimpleTransferMarketFetch
from .views.multi_source_admin import (
    AdminMultiSourcePlayersList,
    AdminMultiSourcePlayersDetails,
    AdminMultiSourcePlayersUpdate,
    AdminMultiSourcePlayersDelete,
    AdminMultiSourcePlayersArchive
)

urlpatterns = [
    # HTML Admin views for multi-source players
    path('', AdminMultiSourcePlayersList, name='AdminMultiSourcePlayersList'),
    path('player/<slug:slug>/', AdminMultiSourcePlayersDetails, name='AdminMultiSourcePlayersDetails'),
    path('player/<slug:slug>/update/', AdminMultiSourcePlayersUpdate, name='AdminMultiSourcePlayersUpdate'),
    path('player/<slug:slug>/delete/', AdminMultiSourcePlayersDelete, name='AdminMultiSourcePlayersDelete'),
    path('player/<slug:slug>/archive/', AdminMultiSourcePlayersArchive, name='AdminMultiSourcePlayersArchive'),
    
    # Multi-source player data fetching (Legacy endpoints)
    path('fetch-sportmonks/', AdminMultiSourcePlayersGetData, name='fetch_sportmonks_players'),
    path('fetch-transfermarkt/', AdminTransfermarktPlayersGetData, name='fetch_transfermarkt_players'),
    
    # Simple Transfer Market integration
    path('fetch-transfermarkt-simple/', AdminSimpleTransferMarketFetch, name='simple_transfermarkt_fetch'),
    path('manual-entry/', AdminManualPlayerEntry, name='manual_player_entry'),
    path('conflicts/', AdminGetPlayerConflicts, name='get_player_conflicts'),
    path('resolve-conflict/', AdminResolvePlayerConflicts, name='resolve_player_conflict'),
    path('stats/', AdminGetDataSourceStats, name='data_source_stats'),
    
    # REST API endpoints for custom admin
    # Player management
    path('api/players/', get_players_list, name='api_players_list'),
    path('api/players/<int:player_id>/', get_player_detail, name='api_player_detail'),
    path('api/players/create/', create_player, name='api_create_player'),
    path('api/players/<int:player_id>/update/', update_player, name='api_update_player'),
    path('api/players/<int:player_id>/delete/', delete_player, name='api_delete_player'),
    
    # Data source management
    path('api/data-sources/', get_data_sources, name='api_data_sources'),
    path('api/data-sources/create/', create_data_source, name='api_create_data_source'),
    path('api/data-sources/<int:source_id>/update/', update_data_source, name='api_update_data_source'),
    
    # Conflict management
    path('api/conflicts/', get_conflicts_list, name='api_conflicts_list'),
    path('api/conflicts/resolve/', resolve_conflict, name='api_resolve_conflict'),
    path('api/conflicts/bulk-resolve/', bulk_resolve_conflicts, name='api_bulk_resolve_conflicts'),
    
    # Utilities and search
    path('api/system-stats/', get_system_stats, name='api_system_stats'),
    path('api/dropdown-data/', get_dropdown_data, name='api_dropdown_data'),
    path('api/search-players/', search_players_by_name, name='api_search_players'),
    path('api/player-by-api-id/', get_player_by_api_id, name='api_player_by_api_id'),
]
