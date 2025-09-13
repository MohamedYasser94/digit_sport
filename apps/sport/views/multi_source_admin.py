from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from ..forms.forms import AdminPlayersForm
from ..models import MultiSourcePlayers, Sport, Teams, Leagues, DataSource

from .multi_source_fetch import initialize_data_sources

# Import your existing decorators
# from your_app.decorators import authenticated_staff, staff_only

BACKEND_TEMPLATES = 'good'  # Adjust this to match your template path


def AdminMultiSourcePlayersList(request):
    """
    Enhanced players list view using MultiSourcePlayers model
    Compatible with existing HTML template structure
    """
    # Initialize data sources
    initialize_data_sources()
    
    sport_list = ['basketball', 'volleyball', 'football']
    
    # Use MultiSourcePlayers instead of Players
    players = MultiSourcePlayers.objects.all().select_related('sport', 'team', 'primary_data_source')
    teams = Teams.objects.all()
    
    # GET logic with pagination
    players_list = MultiSourcePlayers.objects.all().order_by('name')
    paginator = Paginator(players_list, 25)  # Show 25 players per page
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    if request.method == "POST":
        # Manual player creation using MultiSourcePlayers
        name = request.POST.get('name')
        position = request.POST.get('position')
        age = request.POST.get('age')
        birthdate = request.POST.get('birthdate')
        status = request.POST.get('status')
        height = request.POST.get('height')
        country = request.POST.get('country')
        team_id = request.POST.get('team')
        leagues = request.POST.getlist('leagues')
        sport_id = request.POST.get('sport')
        gender = request.POST.get('gender')
        image = request.FILES.get('image')
        image_path = request.POST.get('image_path')
        keyword = request.POST.get('keyword')
        current_market_value = request.POST.get('market_value', '')

        # Handle sport
        sport_obj = None
        if sport_id:
            try:
                sport_obj = Sport.objects.get(id=sport_id)
            except Sport.DoesNotExist:
                pass

        # Handle team
        team_obj = None
        in_team = 'No'
        if team_id:
            try:
                team_obj = Teams.objects.get(id=team_id)
                in_team = 'Yes'
            except Teams.DoesNotExist:
                pass

        # Get manual data source
        try:
            manual_source = DataSource.objects.get(slug='manual')
        except DataSource.DoesNotExist:
            initialize_data_sources()
            manual_source = DataSource.objects.get(slug='manual')

        # Create MultiSourcePlayers object
        player_object = MultiSourcePlayers(
            name=name,
            position=position,
            age=age,
            height=height,
            country=country,
            team=team_obj,
            sport=sport_obj,
            in_team=in_team,
            gender=gender,
            keyword=keyword,
            image=image,
            image_path=image_path,
            current_market_value=current_market_value,
            primary_data_source=manual_source,
            manual_entry_id=f"manual_{request.user.id}_{page_obj.paginator.count + 1}"
        )
        
        # Parse birthdate
        if birthdate:
            try:
                from datetime import datetime
                birthdate_obj = datetime.strptime(birthdate, '%Y-%m-%d').date()
                player_object.birthdate = birthdate_obj
                player_object.date_of_birth = birthdate
            except (ValueError, TypeError):
                pass
        
        player_object.save()
        
        # Add leagues
        for league_id in leagues:
            try:
                league_object = Leagues.objects.get(id=league_id)
                player_object.league.add(league_object)
            except Leagues.DoesNotExist:
                pass
        
        player_object.save()
        
        # Update team player count
        if team_obj:
            try:
                team_obj.player_count += 1
                team_obj.save()
            except:
                pass

        messages.success(request, _("Player Added Successfully"), extra_tags='Players')
        return HttpResponseRedirect(reverse_lazy('sport:AdminMultiSourcePlayersList'))

    # Get statistics for the template
    total_players = MultiSourcePlayers.objects.count()
    unresolved_conflicts = 0
    try:
        from ..models import PlayerDataConflict
        unresolved_conflicts = PlayerDataConflict.objects.filter(resolved=False).count()
    except:
        pass

    context = {
        'page_obj': page_obj,
        'players_form': AdminPlayersForm(),
        'current_page': _('Multi-Source Players'),
        'total_players': total_players,
        'unresolved_conflicts': unresolved_conflicts,
        'sport_list': sport_list,
        'teams': teams,
    }

    return render(request, f'{BACKEND_TEMPLATES}/sport/players/multi_source_admin.html', context)


@csrf_exempt  
def AdminMultiSourcePlayersUpdate(request, slug):
    """
    Update a multi-source player
    """
    player = get_object_or_404(MultiSourcePlayers, slug=slug)
    
    if request.method == "POST":
        # Update player fields
        player.name = request.POST.get('name', player.name)
        player.position = request.POST.get('position', player.position)
        player.age = request.POST.get('age', player.age)
        player.height = request.POST.get('height', player.height)
        player.country = request.POST.get('country', player.country)
        player.gender = request.POST.get('gender', player.gender)
        player.keyword = request.POST.get('keyword', player.keyword)
        player.current_market_value = request.POST.get('market_value', player.current_market_value)
        
        # Handle file upload
        if 'image' in request.FILES:
            player.image = request.FILES['image']
        
        image_path = request.POST.get('image_path')
        if image_path:
            player.image_path = image_path
            
        # Handle birthdate
        birthdate = request.POST.get('birthdate')
        if birthdate:
            try:
                from datetime import datetime
                birthdate_obj = datetime.strptime(birthdate, '%Y-%m-%d').date()
                player.birthdate = birthdate_obj
                player.date_of_birth = birthdate
            except (ValueError, TypeError):
                pass
        
        # Handle sport
        sport_id = request.POST.get('sport')
        if sport_id:
            try:
                player.sport = Sport.objects.get(id=sport_id)
            except Sport.DoesNotExist:
                pass
        
        # Handle team
        team_id = request.POST.get('team')
        if team_id:
            try:
                player.team = Teams.objects.get(id=team_id)
                player.in_team = 'Yes'
            except Teams.DoesNotExist:
                pass
        else:
            player.team = None
            player.in_team = 'No'
            
        player.save()
        
        # Handle leagues
        leagues = request.POST.getlist('leagues')
        player.league.clear()
        for league_id in leagues:
            try:
                league_object = Leagues.objects.get(id=league_id)
                player.league.add(league_object)
            except Leagues.DoesNotExist:
                pass
        
        messages.success(request, _("Player Updated Successfully"), extra_tags='Players')
        return HttpResponseRedirect(reverse_lazy('sport:AdminMultiSourcePlayersList'))
    
    context = {
        'player': player,
        'players_form': AdminPlayersForm(instance=player),
        'current_page': _('Update Player')
    }
    
    return render(request, f'{BACKEND_TEMPLATES}/sport/players/update.html', context)


def AdminMultiSourcePlayersDetails(request, slug):
    """
    View detailed information about a multi-source player
    """
    player = get_object_or_404(MultiSourcePlayers, slug=slug)
    
    # Get data source information with related data
    try:
        source_info = player.source_info.all().select_related('data_source').order_by('-updated_at')
    except:
        source_info = []
    
    # Get unresolved conflicts
    try:
        conflicts = player.conflicts.filter(resolved=False).select_related('source_1', 'source_2')
    except:
        conflicts = []
    
    # Get related data for context
    all_players_count = MultiSourcePlayers.objects.count()
    active_players_count = MultiSourcePlayers.objects.filter(status='Active').count()
    
    # Get market value history (if it exists in JSON format)
    market_value_history = []
    if player.market_value_history:
        try:
            import json
            if isinstance(player.market_value_history, str):
                market_value_history = json.loads(player.market_value_history)
            elif isinstance(player.market_value_history, list):
                market_value_history = player.market_value_history
            else:
                market_value_history = []
        except (json.JSONDecodeError, TypeError):
            market_value_history = []
    
    # Process market value history to show recent entries
    if market_value_history:
        # Show only the last 10 entries
        market_value_history = market_value_history[-10:]
        # Update player object with processed history
        player.market_value_history = market_value_history
    
    # Get all data sources that have info for this player
    data_sources = []
    if player.primary_data_source:
        data_sources.append(player.primary_data_source)
    
    # Add any additional sources from source_info
    for info in source_info:
        if info.data_source not in data_sources:
            data_sources.append(info.data_source)
    
    # Prepare API IDs display
    api_ids = {}
    if player.sportmonks_api_id:
        api_ids['Sportmonks'] = player.sportmonks_api_id
    if player.transfermarkt_id:
        api_ids['Transfer Market'] = player.transfermarkt_id
    if player.manual_entry_id:
        api_ids['Manual Entry'] = player.manual_entry_id
    
    context = {
        'player': player,
        'source_info': source_info,
        'conflicts': conflicts,
        'data_sources': data_sources,
        'api_ids': api_ids,
        'all_players_count': all_players_count,
        'active_players_count': active_players_count,
        'current_page': _('Player Details'),
        'page_title': f"{player.name} - {_('Player Details')}"
    }
    
    return render(request, f'{BACKEND_TEMPLATES}/sport/players/details.html', context)


@csrf_exempt
def AdminMultiSourcePlayersDelete(request, slug):
    """
    Delete a multi-source player
    """
    player = get_object_or_404(MultiSourcePlayers, slug=slug)
    
    if request.method == "POST":
        player_name = player.name
        # Update team player count
        if player.team:
            try:
                player.team.player_count -= 1
                player.team.save()
            except:
                pass
        
        player.delete()
        messages.success(request, _(f"Player {player_name} deleted successfully"), extra_tags='Players')
        return HttpResponseRedirect(reverse_lazy('sport:AdminMultiSourcePlayersList'))
    
    context = {
        'player': player,
        'current_page': _('Delete Player')
    }
    
    return render(request, f'{BACKEND_TEMPLATES}/sport/players/delete.html', context)


@csrf_exempt
def AdminMultiSourcePlayersArchive(request, slug):
    """
    Archive/unarchive a multi-source player
    """
    player = get_object_or_404(MultiSourcePlayers, slug=slug)
    
    if request.method == "POST":
        if player.status == 'Active':
            player.status = 'Inactive'
            messages.success(request, _(f"Player {player.name} archived successfully"), extra_tags='Players')
        else:
            player.status = 'Active'
            messages.success(request, _(f"Player {player.name} activated successfully"), extra_tags='Players')
        
        player.save()
        return HttpResponseRedirect(reverse_lazy('sport:AdminMultiSourcePlayersList'))
    
    context = {
        'player': player,
        'current_page': _('Archive Player')
    }
    
    return render(request, f'{BACKEND_TEMPLATES}/sport/players/archive.html', context)
