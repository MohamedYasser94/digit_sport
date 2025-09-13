from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from ..models import MultiSourcePlayers, Sport, DataSource
from ..views.multi_source_fetch import initialize_data_sources, process_transfermarkt_player_data
import json


@csrf_exempt
@login_required
def AdminSimpleTransferMarketFetch(request):
    """
    Simple Transfer Market data fetch using existing scrapy data
    Just processes pre-scraped data from your existing system
    """
    if request.method == "POST":
        # Initialize data sources
        initialize_data_sources()
        
        try:
            transfermarkt_source = DataSource.objects.get(slug='transfermarkt')
        except DataSource.DoesNotExist:
            return JsonResponse({'type': 'Error', 'message': 'Transfer Market data source not found'})

        # This will process data from your existing scrapy spiders
        # You can either:
        # 1. Read from your scrapy output files
        # 2. Trigger your scrapy spiders
        # 3. Process existing scraped data
        
        processed, added, updated, conflicts = 0, 0, 0, 0
        
        # Example: Read scraped data from a JSON file (if you save scrapy output to files)
        try:
            # You can modify this to read from your scrapy data source
            scraped_data = get_transfer_market_scraped_data()
            
            for player_data in scraped_data:
                result = process_transfermarkt_player_data(player_data, transfermarkt_source, request.user)
                
                if result['action'] == 'created':
                    added += 1
                elif result['action'] == 'updated':
                    updated += 1
                elif result['action'] == 'conflict':
                    conflicts += 1
                
                processed += 1
            
            success_message = f'Transfer Market data processed. Processed: {processed}, Added: {added}, Updated: {updated}'
            if conflicts > 0:
                success_message += f', Conflicts: {conflicts}'
            
            return JsonResponse({'type': 'Success', 'message': success_message})
            
        except Exception as e:
            return JsonResponse({'type': 'Error', 'message': f'Error processing Transfer Market data: {str(e)}'})

    return JsonResponse({'type': 'Error', 'message': 'Invalid request method.'})


def get_transfer_market_scraped_data():
    """
    Get scraped data from your existing transfer market system
    Modify this function to integrate with your scrapy spiders
    """
    # Option 1: Read from scrapy output files
    # if os.path.exists('scrapy_output.json'):
    #     with open('scrapy_output.json', 'r') as f:
    #         return json.load(f)
    
    # Option 2: Trigger scrapy and get results
    # You can run your scrapy spiders here and return the data
    
    # Option 3: Mock data for testing (replace with your actual scrapy integration)
    return [
        {
            'name': 'Cristiano Ronaldo',
            'current_market_value': '€15.00m',
            'age': '39',
            'position': 'Centre-Forward',
            'citizenship': 'Portugal',
            'height': '1,87m',
            'foot': 'right',
            'joined': 'Jan 1, 2023',
            'contract_expires': 'Jun 30, 2025',
            'player_agent': {'name': 'Jorge Mendes'},
            'current_club': {'name': 'Al Nassr'},
            'code': 'cristiano-ronaldo',
            'href': '/cristiano-ronaldo/profil/spieler/8198'
        }
        # Add more mock data or integrate with your scrapy system
    ]


def convert_scraped_data_to_player_format(scraped_data):
    """
    Convert scraped data from your existing format to the format expected by the system
    """
    converted_data = []
    
    for item in scraped_data:
        # Map your scrapy fields to the player model fields
        player_data = {
            'name': item.get('name'),
            'current_market_value': item.get('current_market_value'),
            'age': item.get('age'),
            'position': item.get('position'),
            'nationality': item.get('citizenship'),
            'height': item.get('height'),
            'preferred_foot': item.get('foot'),
            'joined_date': item.get('joined'),
            'contract_expires': item.get('contract_expires'),
            'agent': item.get('player_agent', {}).get('name'),
            'current_club': item.get('current_club', {}).get('name'),
            'code': item.get('code'),
            'href': item.get('href'),
            'image_url': item.get('image_url'),
            'place_of_birth': item.get('place_of_birth'),
            'highest_market_value': item.get('highest_market_value'),
            'market_value_history': item.get('market_value_history'),
            'social_media': item.get('social_media', [])
        }
        
        # Extract ID from href if available
        if item.get('href'):
            import re
            match = re.search(r'/spieler/(\d+)', item['href'])
            if match:
                player_data['id'] = match.group(1)
        
        converted_data.append(player_data)
    
    return converted_data
