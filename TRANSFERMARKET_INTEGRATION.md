# TransferMarket Integration Guide

## Overview
This system updates the main `Players` model with TransferMarket data while maintaining Sportmonks as the primary source for match/league integration.

## Architecture

### Data Sources Priority
1. **Primary Source: Sportmonks** (for Flutter app compatibility)
   - `api_id` field from Sportmonks
   - Team assignments, league relationships
   - Used for match data and league integration

2. **Update Source: TransferMarket** (for detailed player information)
   - Market values
   - Player images
   - Physical attributes (height, weight, foot)
   - Contract information
   - Agent details

### Protected Fields
- `name_tr`: Turkish name - **NEVER updated automatically**, must be edited manually
- `api_id`: Sportmonks ID - preserved
- `team`, `league`: Preserved from Sportmonks

## Implementation Steps

### Step 1: Set Up TransferMarket Data Source

You need to integrate the `load_transfermarket_data()` function in:
`apps/sport/views/update_players_transfermarket.py`

Choose one of these methods:

#### Option A: Read from JSON Files (Recommended for Scrapy)
```python
def load_transfermarket_data():
    import os
    import json
    
    # Path to your Scrapy output
    data_file = os.path.join(settings.BASE_DIR, 'scraped_data', 'transfermarket_players.json')
    
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return []
```

#### Option B: Read from Database Table
```python
def load_transfermarket_data():
    # If you have a ScrapedPlayer model or similar
    from .models import ScrapedTransferMarketPlayer
    
    players = ScrapedTransferMarketPlayer.objects.filter(
        source='transfermarkt',
        is_processed=False
    ).values()
    
    return list(players)
```

#### Option C: Trigger Scrapy Spider
```python
def load_transfermarket_data():
    from scrapy.crawler import CrawlerRunner
    from twisted.internet import reactor
    
    # Run your spider and collect results
    # This is more complex - see Scrapy documentation
    pass
```

### Step 2: TransferMarket Data Format

Your scraping system should provide data in this format:

```json
{
    "name": "Cristiano Ronaldo",
    "first_name": "Cristiano",
    "last_name": "Ronaldo",
    "display_name": "C. Ronaldo",
    "href": "/cristiano-ronaldo/profil/spieler/8198",
    "image_url": "https://img.a.transfermarkt.technology/portrait/header/8198.jpg",
    "current_market_value": "€15.00m",
    "highest_market_value": "€120.00m",
    "age": "39",
    "birthdate": "Feb 5, 1985",
    "place_of_birth": {
        "city": "Funchal",
        "country": "Portugal"
    },
    "height": "1,87m",
    "citizenship": "Portugal",
    "position": "Centre-Forward",
    "foot": "right",
    "number": "7",
    "current_club": {
        "name": "Al Nassr",
        "href": "/al-nassr/startseite/verein/8206"
    },
    "joined": "Jan 1, 2023",
    "contract_expires": "Jun 30, 2025",
    "player_agent": {
        "name": "Jorge Mendes",
        "href": "/jorge-mendes/beraterfirma/berater/413"
    },
    "outfitter": "Nike"
}
```

### Step 3: Player Matching Algorithm

The system uses fuzzy matching to connect Players with TransferMarket data:

1. **By TransferMarket ID** (most accurate)
   - If `player.transfermarkt_id` exists, direct match

2. **By Name + Team** (recommended)
   - 70% weight on player name similarity
   - 30% weight on team name similarity
   - Requires 80% combined match

3. **By Name Only** (fallback)
   - Requires 85% name similarity
   - Less accurate, use only when team data unavailable

### Step 4: Run Migration

```bash
python manage.py migrate sport
```

This adds the following fields to Players model:
- `transfermarkt_id`
- `transfermarkt_url`
- `image_url`
- `current_market_value`
- `highest_market_value`
- `market_value_currency`
- `market_value_numeric`
- `market_value_last_updated`
- `citizenship`
- `foot`
- `place_of_birth_city`
- `place_of_birth_country`
- `joined`
- `contract_expires`
- `player_agent_name`
- `outfitter`

### Step 5: Usage

#### From Admin Interface

1. Navigate to Players admin page
2. Click "Update Players From Transfermarket" button
3. Select sport (Football/Basketball)
4. Click "Update from TransferMarket"
5. Wait for the process to complete

#### Programmatically

```python
from apps.sport.views.update_players_transfermarket import update_player_with_transfermarket_data

# Get player and TransferMarket data
player = Players.objects.get(id=123)
tm_data = get_transfermarket_data_for_player(player)

if tm_data:
    update_player_with_transfermarket_data(player, tm_data)
```

## Scrapy Integration Examples

### Example 1: Basic Scrapy Spider Output

Configure your Scrapy spider to output to JSON:

```python
# settings.py
FEEDS = {
    'scraped_data/transfermarket_players.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'overwrite': True,
    },
}
```

### Example 2: Database Pipeline

Create a Scrapy pipeline to save to database:

```python
class TransferMarketPipeline:
    def process_item(self, item, spider):
        # Save to a temporary model or JSON field
        ScrapedPlayer.objects.update_or_create(
            transfermarkt_id=item['id'],
            defaults={
                'raw_data': dict(item),
                'scraped_at': timezone.now()
            }
        )
        return item
```

## Testing

### Test with Mock Data

Before connecting real scraping:

```python
def load_transfermarket_data():
    """Mock data for testing"""
    return [
        {
            'name': 'Mohamed Salah',
            'href': '/mohamed-salah/profil/spieler/148455',
            'current_market_value': '€65.00m',
            'position': 'Right Winger',
            'age': '32',
            'current_club': {'name': 'Liverpool FC'},
        }
    ]
```

## Troubleshooting

### No Players Updated
- Check that `load_transfermarket_data()` returns data
- Verify player names match between Sportmonks and TransferMarket
- Lower matching threshold temporarily for testing

### Wrong Players Matched
- Increase matching threshold (currently 80%)
- Add more specific team matching
- Manually set `transfermarkt_id` for important players

### Market Values Not Parsing
- Check currency format in TransferMarket data
- Verify `parse_market_value()` regex pattern
- Add logging to see exact value strings

## Best Practices

1. **Run updates during off-peak hours** - Matching can be CPU intensive
2. **Keep TransferMarket data fresh** - Run scraping weekly
3. **Manually verify high-value players** - Check market values for star players
4. **Monitor matching statistics** - Review "Failed to Match" count
5. **Preserve name_tr** - Never overwrite manually added Turkish names

## API Endpoints

- `POST /sport/transfermarket/players/api/get/` - Bulk update all players
- `POST /sport/transfermarket/player/search/` - Search and update single player

## Future Enhancements

1. Add player history tracking
2. Implement conflict resolution UI
3. Support multiple image sources
4. Add TransferMarket API integration (if available)
5. Create detailed match reports showing confidence scores

## Support

For issues or questions:
1. Check Django logs for error messages
2. Review matching statistics in response
3. Verify TransferMarket data format
4. Test with mock data first

