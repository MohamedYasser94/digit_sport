# Multi-Source Players System

This system allows fetching player data from multiple sources (Sportmonks API, Transfer Market, manual entry) while maintaining data integrity and resolving conflicts automatically.

## Features

- **Multiple Data Sources**: Support for Sportmonks API, Transfer Market scraping, and manual data entry
- **Automatic Conflict Resolution**: Prioritizes data sources and handles conflicts intelligently
- **Flutter App Compatibility**: Maintains compatibility with existing Flutter app using system IDs and Sportmonks IDs
- **Transfer Market Integration**: Full support for transfer market values, history, and commercial data
- **Admin Interface**: Comprehensive Django admin for managing data sources, conflicts, and players
- **Data Migration**: Tools to migrate existing player data to the new multi-source system

## Models

### DataSource
Represents different data sources with priority levels for conflict resolution:
- Sportmonks (Priority: 90) - Primary source for official sports data
- Transfer Market (Priority: 80) - Best for market values and transfers
- Manual Entry (Priority: 70) - Administrator-entered data

### MultiSourcePlayers
Enhanced player model supporting:
- Multiple API IDs (Sportmonks, Transfer Market, manual)
- All transfer market fields (market value, agent info, contracts)
- Source tracking for conflict resolution
- Backward compatibility with existing Flutter app

### PlayerDataSourceInfo
Tracks which sources provide data for each player.

### PlayerDataConflict
Manages conflicts between different data sources for manual resolution.

## Installation & Setup

### 1. Add to Django Settings
Make sure the app is properly configured and add the admin:

```python
# In your settings.py, ensure these are configured:
SPORT_MONKS_TOKEN = 'your_api_token'
SPORT_MONKS_URL = 'https://api.sportmonks.com/v3/'
```

### 2. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Initialize Data Sources
```bash
# Run this in Django shell or create a management command
from apps.sport.views.multi_source_fetch import initialize_data_sources
initialize_data_sources()
```

### 4. Migrate Existing Players (Optional)
```bash
# Dry run to see what would be migrated
python manage.py migrate_to_multi_source_players --dry-run

# Actual migration (limit for testing)
python manage.py migrate_to_multi_source_players --limit=100

# Full migration
python manage.py migrate_to_multi_source_players
```

## Usage

### Fetching Data from Sportmonks
```python
# Via admin interface or direct API call
POST /admin/multi-source/fetch-sportmonks/
{
    "sport": "football"
}
```

### Processing Transfer Market Data
```python
# Send scraped data as JSON
POST /admin/multi-source/fetch-transfermarkt/
{
    "scraped_data": [
        {
            "name": "Player Name",
            "current_market_value": "€50.00m",
            "position": "Midfielder",
            # ... other Transfer Market fields
        }
    ]
}
```

### Manual Player Entry
```python
POST /admin/multi-source/manual-entry/
{
    "name": "Player Name",
    "position": "Forward",
    "market_value": "€25.00m",
    "sport_id": 1,
    # ... other fields
}
```

### Resolving Conflicts
```python
POST /admin/multi-source/resolve-conflicts/
{
    "conflict_id": 123,
    "resolution": "source_1",  # or "source_2", "manual", "ignore"
    "manual_value": "custom value"  # if resolution is "manual"
}
```

## API Integration

### Flutter App Compatibility
The system maintains backward compatibility with your Flutter app:

```python
# Get primary ID for Flutter app
player = MultiSourcePlayers.objects.get(id=1)
primary_id = player.get_primary_id()  # Returns "sportmonks_12345" or "system_1"
```

### Data Priority System
Data sources have priority levels:
1. **Sportmonks (90)**: Official sports data
2. **Transfer Market (80)**: Market values and commercial data  
3. **Manual Entry (70)**: Administrator overrides

When conflicts arise, higher priority sources take precedence unless manually overridden.

## Custom Admin Integration

Since you're using a custom admin system, the multi-source player system provides comprehensive REST API endpoints for seamless integration:

### API Endpoints for Your Custom Admin

#### Player Management
```javascript
// Get paginated players list with filtering
GET /multi-source/api/players/?name=messi&sport_id=1&has_conflicts=true

// Get detailed player information
GET /multi-source/api/players/123/

// Create new player
POST /multi-source/api/players/create/
{
  "name": "Player Name",
  "sport_id": 1,
  "position": "Forward",
  "current_market_value": "€50.00m"
}

// Update player
PUT /multi-source/api/players/123/update/
{
  "current_market_value": "€60.00m"
}

// Delete player
DELETE /multi-source/api/players/123/delete/
```

#### Conflict Management
```javascript
// Get unresolved conflicts
GET /multi-source/api/conflicts/?player_name=messi

// Resolve single conflict
POST /multi-source/api/conflicts/resolve/
{
  "conflict_id": 456,
  "resolution": "source_1"  // or "source_2", "manual", "ignore"
}

// Bulk resolve conflicts
POST /multi-source/api/conflicts/bulk-resolve/
{
  "conflict_ids": [456, 789, 123],
  "resolution": "source_1"
}
```

#### Data Source Management
```javascript
// Get all data sources with statistics
GET /multi-source/api/data-sources/

// Create new data source
POST /multi-source/api/data-sources/create/
{
  "name": "ESPN API",
  "slug": "espn",
  "priority": 85,
  "api_base_url": "https://api.espn.com"
}
```

#### System Statistics
```javascript
// Get comprehensive system stats
GET /multi-source/api/system-stats/

// Response includes:
{
  "total_players": 15420,
  "total_data_sources": 3,
  "unresolved_conflicts": 45,
  "players_with_market_value": 8934,
  "players_with_multiple_sources": 6785,
  "source_stats": [
    {
      "source_name": "Sportmonks",
      "total_players": 12000,
      "primary_source_for": 10000,
      "priority": 90,
      "is_active": true
    }
  ]
}
```

#### Utility Endpoints
```javascript
// Get dropdown data for forms
GET /multi-source/api/dropdown-data/

// Search players for autocomplete
GET /multi-source/api/search-players/?q=messi

// Find player by API ID (Flutter compatibility)
GET /multi-source/api/player-by-api-id/?sportmonks_id=12345
```

## Transfer Market Features

### Market Value Tracking
- Current market value with currency detection
- Historical market value data (JSON field)
- Highest achieved market value
- Automatic numeric parsing for sorting/filtering

### Commercial Information
- Player agent details
- Equipment sponsors (outfitters)
- Social media links
- Contract information

### Club Information
- Current club details
- Join date and contract expiration
- Transfer Market club links

## Data Flow

1. **Sportmonks API**: Fetches official player data with sport stats
2. **Transfer Market**: Scrapes market values, commercial data, detailed player info
3. **Manual Entry**: Allows administrators to add/override data
4. **Conflict Resolution**: Automatically resolves based on source priority
5. **Flutter App**: Consumes data using primary IDs (maintains compatibility)

## Best Practices

### Data Source Management
- Keep Sportmonks as primary for official sports data
- Use Transfer Market for market values and commercial information
- Reserve manual entry for corrections and special cases

### Conflict Resolution
- Review conflicts regularly through admin interface
- Set clear priorities for your organization's needs
- Use manual resolution for important discrepancies

### Performance Optimization
- Use database indexes on API IDs and market values
- Implement caching for frequently accessed market value data
- Consider background tasks for large data imports

## Troubleshooting

### Common Issues

**Migration Errors**: Ensure all dependencies are installed and database is accessible
```bash
pip install -r requirements.txt
python manage.py check
```

**API Timeouts**: Implement retry logic and rate limiting
```python
# In fetch functions, add delays between requests
import time
time.sleep(0.1)  # 100ms delay
```

**Conflict Resolution**: Use admin interface to resolve data conflicts
- Go to `/admin/sport/playerdataconflict/`
- Review conflicts and choose appropriate resolution

### Performance Monitoring
Monitor the following metrics:
- Data fetch success rates
- Conflict resolution times
- API response times
- Database query performance

## Future Enhancements

1. **Additional Data Sources**: Easy to add new sources by extending the DataSource model
2. **Automated Conflict Resolution**: ML-based conflict resolution for common cases
3. **Real-time Updates**: WebSocket integration for live data updates
4. **API Versioning**: RESTful API for external integrations
5. **Data Validation**: Enhanced validation rules for different data sources

## Contributing

When adding new data sources:
1. Create a new DataSource entry with appropriate priority
2. Add field mappings in `MultiSourcePlayers._update_with_conflict_resolution()`
3. Create processing functions in `multi_source_fetch.py`
4. Add admin interface enhancements
5. Update tests and documentation

## Testing

```bash
# Run tests
python manage.py test apps.sport.tests.test_multi_source

# Test with limited data
python manage.py migrate_to_multi_source_players --dry-run --limit=10
```

## Support

For issues or questions:
1. Check the Django admin logs
2. Review conflict resolution queue
3. Verify API credentials and connectivity
4. Check database indexes and performance
