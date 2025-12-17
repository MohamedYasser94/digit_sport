"""
Example implementation for integrating TransferMarket scraping with the Players update system

Choose one of the following methods based on your existing scraping setup
"""

# ============================================================================
# METHOD 1: Read from Scrapy JSON Output Files
# ============================================================================
def load_transfermarket_data_from_json():
    """
    If your Scrapy spider outputs to JSON files
    """
    import os
    import json
    from django.conf import settings

    # Adjust path to your scrapy output directory
    data_file = os.path.join(
        settings.BASE_DIR,
        'scraped_data',  # Your scrapy output folder
        'transfermarket_players.json'
    )

    if not os.path.exists(data_file):
        print(f"Warning: {data_file} not found")
        return []

    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # If data is a list, return it
            if isinstance(data, list):
                return data

            # If data is wrapped in a key, extract it
            if isinstance(data, dict) and 'players' in data:
                return data['players']

            return []
    except Exception as e:
        print(f"Error loading TransferMarket data: {e}")
        return []


# ============================================================================
# METHOD 2: Read from Multiple JSON Files (One per player)
# ============================================================================
def load_transfermarket_data_from_files():
    """
    If your scraper saves each player to a separate JSON file
    """
    import os
    import json
    from django.conf import settings

    data_dir = os.path.join(settings.BASE_DIR, 'scraped_data', 'players')

    if not os.path.exists(data_dir):
        return []

    players = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(data_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    player_data = json.load(f)
                    players.append(player_data)
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    return players


# ============================================================================
# METHOD 3: Read from Database Table (if you save scraped data to DB)
# ============================================================================
def load_transfermarket_data_from_database():
    """
    If you have a model that stores scraped TransferMarket data
    """
    from django.apps import apps

    # Adjust to your model name
    try:
        ScrapedPlayer = apps.get_model('sport', 'ScrapedTransferMarketPlayer')

        # Get unprocessed scraped players
        scraped_players = ScrapedPlayer.objects.filter(
            is_processed=False,
            source='transfermarkt'
        ).values(
            'name', 'transfermarkt_id', 'current_market_value',
            'position', 'height', 'age', 'foot', 'image_url',
            'current_club', 'joined', 'contract_expires',
            'player_agent', 'outfitter'
        )

        return list(scraped_players)

    except LookupError:
        print("ScrapedTransferMarketPlayer model not found")
        return []


# ============================================================================
# METHOD 4: Trigger Scrapy Spider and Get Results
# ============================================================================
def load_transfermarket_data_with_scrapy():
    """
    Trigger your Scrapy spider programmatically
    This is more complex and may require running in a separate process
    """
    import subprocess
    import json
    import os
    from django.conf import settings

    # Path to your scrapy project
    scrapy_project = os.path.join(settings.BASE_DIR, 'your_scrapy_project')
    output_file = os.path.join(settings.BASE_DIR, 'scraped_data', 'temp_players.json')

    # Run scrapy spider
    try:
        subprocess.run([
            'scrapy', 'crawl', 'transfermarkt_spider',
            '-o', output_file,
            '-t', 'json'
        ], cwd=scrapy_project, check=True, timeout=300)

        # Read the output
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Clean up temp file
            os.remove(output_file)
            return data

    except subprocess.TimeoutExpired:
        print("Scrapy spider timed out")
    except Exception as e:
        print(f"Error running scrapy: {e}")

    return []


# ============================================================================
# METHOD 5: Read from CSV File
# ============================================================================
def load_transfermarket_data_from_csv():
    """
    If you export scraped data to CSV
    """
    import os
    import csv
    from django.conf import settings

    csv_file = os.path.join(settings.BASE_DIR, 'scraped_data', 'players.csv')

    if not os.path.exists(csv_file):
        return []

    players = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert CSV row to dictionary matching expected format
                player_data = {
                    'name': row.get('name'),
                    'transfermarkt_id': row.get('player_id'),
                    'href': row.get('url'),
                    'current_market_value': row.get('market_value'),
                    'position': row.get('position'),
                    'age': row.get('age'),
                    'height': row.get('height'),
                    'foot': row.get('foot'),
                    'image_url': row.get('image'),
                    'citizenship': row.get('nationality'),
                }
                players.append(player_data)
    except Exception as e:
        print(f"Error loading CSV: {e}")

    return players


# ============================================================================
# INTEGRATION INTO YOUR PROJECT
# ============================================================================
"""
To integrate this into your project:

1. Copy one of the methods above
2. Paste it into: apps/sport/views/update_players_transfermarket.py
3. Replace the load_transfermarket_data() function with your chosen method
4. Adjust paths and field mappings to match your data structure

Example:

# In apps/sport/views/update_players_transfermarket.py

def load_transfermarket_data():
    # Use METHOD 1 (JSON files)
    import os
    import json
    from django.conf import settings
    
    data_file = os.path.join(settings.BASE_DIR, 'scraped_data', 'transfermarket_players.json')
    
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return []
"""


# ============================================================================
# DATA VALIDATION
# ============================================================================
def validate_transfermarket_data(data):
    """
    Validate that scraped data has required fields
    """
    required_fields = ['name']  # Minimum requirement
    recommended_fields = [
        'name', 'current_market_value', 'position',
        'image_url', 'height', 'age'
    ]

    issues = []

    for i, player in enumerate(data):
        # Check required fields
        for field in required_fields:
            if not player.get(field):
                issues.append(f"Player {i}: Missing required field '{field}'")

        # Warn about missing recommended fields
        missing_recommended = [
            field for field in recommended_fields
            if not player.get(field)
        ]
        if missing_recommended:
            issues.append(
                f"Player {i} ({player.get('name', 'Unknown')}): "
                f"Missing recommended fields: {', '.join(missing_recommended)}"
            )

    return issues


# ============================================================================
# TEST YOUR INTEGRATION
# ============================================================================
def test_transfermarket_integration():
    """
    Test your TransferMarket data integration
    Run this to verify everything works before using in production
    """
    print("Testing TransferMarket integration...")

    # Load data using your chosen method
    data = load_transfermarket_data_from_json()  # Or your method

    if not data:
        print("❌ No data loaded. Check your data source.")
        return False

    print(f"✓ Loaded {len(data)} players")

    # Validate data
    issues = validate_transfermarket_data(data)
    if issues:
        print(f"⚠ Found {len(issues)} data issues:")
        for issue in issues[:5]:  # Show first 5 issues
            print(f"  - {issue}")
        if len(issues) > 5:
            print(f"  ... and {len(issues) - 5} more")
    else:
        print("✓ All data validated successfully")

    # Show sample player
    if data:
        print("\nSample player data:")
        sample = data[0]
        for key, value in sample.items():
            if value:
                print(f"  {key}: {value}")

    return True


if __name__ == '__main__':
    # Run test
    test_transfermarket_integration()

