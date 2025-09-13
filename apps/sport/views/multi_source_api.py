from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ..models import (
    MultiSourcePlayers, DataSource, PlayerDataSourceInfo, 
    PlayerDataConflict, Sport, Teams, Leagues
)
from ..serializers.multi_source_serializers import (
    MultiSourcePlayersListSerializer, MultiSourcePlayersDetailSerializer,
    MultiSourcePlayersCreateUpdateSerializer, DataSourceSerializer,
    PlayerDataConflictSerializer, PlayerSearchSerializer,
    ConflictResolutionSerializer, BulkConflictResolutionSerializer,
    SystemStatsSerializer
)
from .multi_source_fetch import initialize_data_sources


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_players_list(request):
    """
    Get paginated list of multi-source players with filtering
    """
    # Initialize data sources if needed
    initialize_data_sources()
    
    # Get query parameters
    search_serializer = PlayerSearchSerializer(data=request.query_params)
    search_serializer.is_valid(raise_exception=True)
    
    search_data = search_serializer.validated_data
    
    # Base queryset
    queryset = MultiSourcePlayers.objects.select_related(
        'sport', 'team', 'primary_data_source'
    ).prefetch_related('data_sources', 'conflicts')
    
    # Apply filters
    if search_data.get('name'):
        queryset = queryset.filter(
            Q(name__icontains=search_data['name']) |
            Q(display_name__icontains=search_data['name']) |
            Q(common_name__icontains=search_data['name'])
        )
    
    if search_data.get('sport_id'):
        queryset = queryset.filter(sport_id=search_data['sport_id'])
    
    if search_data.get('position'):
        queryset = queryset.filter(position__icontains=search_data['position'])
    
    if search_data.get('team_id'):
        queryset = queryset.filter(team_id=search_data['team_id'])
    
    if search_data.get('primary_data_source_id'):
        queryset = queryset.filter(primary_data_source_id=search_data['primary_data_source_id'])
    
    if search_data.get('has_conflicts'):
        queryset = queryset.annotate(
            conflicts_count=Count('conflicts', filter=Q(conflicts__resolved=False))
        ).filter(conflicts_count__gt=0)
    
    if search_data.get('market_value_min'):
        queryset = queryset.filter(market_value_numeric__gte=search_data['market_value_min'])
    
    if search_data.get('market_value_max'):
        queryset = queryset.filter(market_value_numeric__lte=search_data['market_value_max'])
    
    # Order by update time (most recent first)
    queryset = queryset.order_by('-update_at')
    
    # Paginate
    paginator = CustomPagination()
    page = paginator.paginate_queryset(queryset, request)
    
    serializer = MultiSourcePlayersListSerializer(page, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_player_detail(request, player_id):
    """
    Get detailed information about a specific player
    """
    player = get_object_or_404(
        MultiSourcePlayers.objects.select_related(
            'sport', 'team', 'primary_data_source', 'name_source',
            'image_source', 'market_value_source'
        ).prefetch_related(
            'league', 'source_info__data_source', 'conflicts'
        ),
        id=player_id
    )
    
    serializer = MultiSourcePlayersDetailSerializer(player)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_player(request):
    """
    Create a new multi-source player
    """
    serializer = MultiSourcePlayersCreateUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    player = serializer.save()
    
    # Create manual entry data source info
    manual_source = DataSource.objects.get(slug='manual')
    PlayerDataSourceInfo.objects.create(
        player=player,
        data_source=manual_source,
        is_primary=True,
        last_updated_by=request.user,
        raw_data={'created_via_api': True, 'created_by': request.user.username}
    )
    
    response_serializer = MultiSourcePlayersDetailSerializer(player)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_player(request, player_id):
    """
    Update an existing multi-source player
    """
    player = get_object_or_404(MultiSourcePlayers, id=player_id)
    
    partial = request.method == 'PATCH'
    serializer = MultiSourcePlayersCreateUpdateSerializer(
        player, data=request.data, partial=partial
    )
    serializer.is_valid(raise_exception=True)
    
    player = serializer.save()
    
    # Update or create manual entry data source info
    manual_source = DataSource.objects.get(slug='manual')
    source_info, created = PlayerDataSourceInfo.objects.get_or_create(
        player=player,
        data_source=manual_source,
        defaults={'is_primary': False}
    )
    source_info.last_updated_by = request.user
    source_info.raw_data = {
        'updated_via_api': True,
        'updated_by': request.user.username,
        'update_fields': list(request.data.keys())
    }
    source_info.save()
    
    response_serializer = MultiSourcePlayersDetailSerializer(player)
    return Response(response_serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_player(request, player_id):
    """
    Delete a multi-source player
    """
    player = get_object_or_404(MultiSourcePlayers, id=player_id)
    player_name = player.name
    player.delete()
    
    return Response({
        'message': f'Player "{player_name}" deleted successfully'
    }, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_data_sources(request):
    """
    Get all data sources with statistics
    """
    sources = DataSource.objects.all().order_by('-priority')
    serializer = DataSourceSerializer(sources, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_data_source(request):
    """
    Create a new data source
    """
    serializer = DataSourceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    source = serializer.save()
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_data_source(request, source_id):
    """
    Update a data source
    """
    source = get_object_or_404(DataSource, id=source_id)
    serializer = DataSourceSerializer(source, data=request.data)
    serializer.is_valid(raise_exception=True)
    source = serializer.save()
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conflicts_list(request):
    """
    Get list of unresolved conflicts with pagination
    """
    queryset = PlayerDataConflict.objects.filter(resolved=False).select_related(
        'player', 'source_1', 'source_2'
    ).order_by('-created_at')
    
    # Filter by player name if provided
    player_name = request.query_params.get('player_name')
    if player_name:
        queryset = queryset.filter(player__name__icontains=player_name)
    
    # Filter by field name if provided
    field_name = request.query_params.get('field_name')
    if field_name:
        queryset = queryset.filter(field_name=field_name)
    
    # Paginate
    paginator = CustomPagination()
    page = paginator.paginate_queryset(queryset, request)
    
    serializer = PlayerDataConflictSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_conflict(request):
    """
    Resolve a single conflict
    """
    serializer = ConflictResolutionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    conflict_id = serializer.validated_data['conflict_id']
    resolution = serializer.validated_data['resolution']
    manual_value = serializer.validated_data.get('manual_value', '')
    
    try:
        conflict = PlayerDataConflict.objects.get(id=conflict_id, resolved=False)
        
        # Apply the resolution to the player
        if resolution == 'source_1':
            setattr(conflict.player, conflict.field_name, conflict.value_1)
        elif resolution == 'source_2':
            setattr(conflict.player, conflict.field_name, conflict.value_2)
        elif resolution == 'manual':
            setattr(conflict.player, conflict.field_name, manual_value)
        
        if resolution != 'ignore':
            conflict.player.save()
        
        # Mark conflict as resolved
        conflict.resolved = True
        conflict.resolution_choice = resolution
        conflict.manual_value = manual_value if resolution == 'manual' else None
        conflict.resolved_by = request.user
        conflict.resolved_at = timezone.now()
        conflict.save()
        
        return Response({'message': 'Conflict resolved successfully'})
        
    except PlayerDataConflict.DoesNotExist:
        return Response(
            {'error': 'Conflict not found or already resolved'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_resolve_conflicts(request):
    """
    Resolve multiple conflicts at once
    """
    serializer = BulkConflictResolutionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    conflict_ids = serializer.validated_data['conflict_ids']
    resolution = serializer.validated_data['resolution']
    
    conflicts = PlayerDataConflict.objects.filter(
        id__in=conflict_ids, 
        resolved=False
    ).select_related('player')
    
    resolved_count = 0
    
    for conflict in conflicts:
        # Apply the resolution to the player
        if resolution == 'source_1':
            setattr(conflict.player, conflict.field_name, conflict.value_1)
        elif resolution == 'source_2':
            setattr(conflict.player, conflict.field_name, conflict.value_2)
        
        if resolution != 'ignore':
            conflict.player.save()
        
        # Mark conflict as resolved
        conflict.resolved = True
        conflict.resolution_choice = resolution
        conflict.resolved_by = request.user
        conflict.resolved_at = timezone.now()
        conflict.save()
        
        resolved_count += 1
    
    return Response({
        'message': f'{resolved_count} conflicts resolved successfully'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_system_stats(request):
    """
    Get comprehensive system statistics
    """
    # Basic counts
    total_players = MultiSourcePlayers.objects.count()
    total_data_sources = DataSource.objects.count()
    unresolved_conflicts = PlayerDataConflict.objects.filter(resolved=False).count()
    
    # Players with market value
    players_with_market_value = MultiSourcePlayers.objects.exclude(
        Q(current_market_value__isnull=True) | Q(current_market_value='')
    ).count()
    
    # Players with multiple sources
    players_with_multiple_sources = MultiSourcePlayers.objects.annotate(
        sources_count=Count('data_sources')
    ).filter(sources_count__gt=1).count()
    
    # Source-specific stats
    source_stats = []
    for source in DataSource.objects.all():
        source_stats.append({
            'source_name': source.name,
            'total_players': MultiSourcePlayers.objects.filter(data_sources=source).count(),
            'primary_source_for': MultiSourcePlayers.objects.filter(primary_data_source=source).count(),
            'priority': source.priority,
            'is_active': source.is_active
        })
    
    stats_data = {
        'total_players': total_players,
        'total_data_sources': total_data_sources,
        'unresolved_conflicts': unresolved_conflicts,
        'players_with_market_value': players_with_market_value,
        'players_with_multiple_sources': players_with_multiple_sources,
        'source_stats': source_stats
    }
    
    serializer = SystemStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dropdown_data(request):
    """
    Get data for dropdown menus in the admin interface
    """
    sports = Sport.objects.all().values('id', 'name')
    teams = Teams.objects.all().values('id', 'name', 'sport_id')
    leagues = Leagues.objects.all().values('id', 'name', 'sport_id')
    data_sources = DataSource.objects.filter(is_active=True).values('id', 'name', 'priority')
    
    # Position choices from your model
    position_choices = [
        {'value': choice[0], 'label': choice[1]}
        for choice in MultiSourcePlayers._meta.get_field('position').choices
    ]
    
    return Response({
        'sports': list(sports),
        'teams': list(teams),
        'leagues': list(leagues),
        'data_sources': list(data_sources),
        'position_choices': position_choices
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_players_by_name(request):
    """
    Quick search for players by name (for autocomplete)
    """
    query = request.query_params.get('q', '').strip()
    if len(query) < 2:
        return Response([])
    
    players = MultiSourcePlayers.objects.filter(
        Q(name__icontains=query) |
        Q(display_name__icontains=query) |
        Q(common_name__icontains=query)
    ).select_related('sport', 'team')[:10]
    
    results = []
    for player in players:
        results.append({
            'id': player.id,
            'name': player.name,
            'display_name': player.display_name,
            'sport_name': player.sport.name if player.sport else None,
            'team_name': player.team.name if player.team else None,
            'position': player.position,
            'primary_id': player.get_primary_id()
        })
    
    return Response(results)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_player_by_api_id(request):
    """
    Find player by API ID (for Flutter app compatibility)
    """
    sportmonks_id = request.query_params.get('sportmonks_id')
    transfermarkt_id = request.query_params.get('transfermarkt_id')
    
    player = None
    
    if sportmonks_id:
        player = MultiSourcePlayers.objects.filter(
            sportmonks_api_id=sportmonks_id
        ).first()
    elif transfermarkt_id:
        player = MultiSourcePlayers.objects.filter(
            transfermarkt_id=transfermarkt_id
        ).first()
    
    if not player:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = MultiSourcePlayersDetailSerializer(player)
    return Response(serializer.data)
