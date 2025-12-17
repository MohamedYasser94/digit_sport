"""
Debug script to test TransferMarket data loading and matching
Run from Django shell or as management command

Usage:
    python manage.py shell
    exec(open('debug_transfermarket.py').read())

Or directly:
    python debug_transfermarket.py
"""

import os
import sys
from django.conf import settings

# Configure Django if running directly
if not settings.configured:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
    django.setup()

from apps.sport.models import Players, Sport
from apps.sport.models.multi_source_players import MultiSourcePlayers
from apps.sport.views.update_players_transfermarket import (
    load_transfermarket_data,
    _get_cached_tm_data,
    find_tm_data_by_id,
    find_tm_data_by_name_and_team,
    find_tm_data_by_name
)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_multisource_players():
    """Check MultiSourcePlayers data availability"""
    print_section("1. MULTISOURCE PLAYERS DATA CHECK")

    total = MultiSourcePlayers.objects.count()
    with_tm_id = MultiSourcePlayers.objects.filter(
        transfermarkt_id__isnull=False
    ).exclude(transfermarkt_id='').count()

    print(f"Total MultiSourcePlayers: {total}")
    print(f"With transfermarkt_id: {with_tm_id}")
    print(f"Coverage: {(with_tm_id/total*100 if total > 0 else 0):.1f}%")

    if with_tm_id > 0:
        print("\n✅ TransferMarket data is available in MultiSourcePlayers")

        # Show samples
        print("\nSample players with TM data:")
        samples = MultiSourcePlayers.objects.filter(
            transfermarkt_id__isnull=False
        ).exclude(transfermarkt_id='')[:5]

        for player in samples:
            print(f"  - {player.name[:30]:30} | TM ID: {player.transfermarkt_id:10} | Value: {player.current_market_value or 'N/A'}")
    else:
        print("\n❌ NO TransferMarket data in MultiSourcePlayers!")
        print("   → You need to populate MultiSourcePlayers first")
        print("   → Run your TransferMarket scraper or import data")
        return False

    return True


def test_data_loading():
    """Test the load_transfermarket_data function"""
    print_section("2. DATA LOADING TEST")

    print("Loading TransferMarket data...")
    data = load_transfermarket_data()

    print(f"✅ Loaded {len(data)} players")

    if len(data) == 0:
        print("❌ ERROR: No data loaded!")
        return False

    # Check data quality
    has_name = sum(1 for p in data if p.get('name'))
    has_market_value = sum(1 for p in data if p.get('current_market_value'))
    has_image = sum(1 for p in data if p.get('image_url'))

    print(f"\nData Quality:")
    print(f"  With name: {has_name}/{len(data)} ({has_name/len(data)*100:.1f}%)")
    print(f"  With market_value: {has_market_value}/{len(data)} ({has_market_value/len(data)*100:.1f}%)")
    print(f"  With image_url: {has_image}/{len(data)} ({has_image/len(data)*100:.1f}%)")

    # Show sample
    if data:
        print("\nSample data:")
        sample = data[0]
        for key, value in sample.items():
            if value:
                print(f"  {key}: {str(value)[:60]}")

    return True


def test_matching_by_id():
    """Test matching by TransferMarket ID"""
    print_section("3. MATCHING BY ID TEST")

    # Get a player with TM ID
    test_player = MultiSourcePlayers.objects.filter(
        transfermarkt_id__isnull=False
    ).exclude(transfermarkt_id='').first()

    if not test_player:
        print("❌ No test player with TM ID available")
        return False

    print(f"Test player: {test_player.name} (TM ID: {test_player.transfermarkt_id})")

    # Try to find by ID
    found = find_tm_data_by_id(test_player.transfermarkt_id)

    if found:
        print(f"✅ Found: {found.get('name')}")
        return True
    else:
        print(f"❌ Not found by ID")
        return False


def test_matching_by_name_and_team():
    """Test matching by name and team"""
    print_section("4. MATCHING BY NAME + TEAM TEST")

    # Get a player from Players model to test
    test_player = Players.objects.filter(
        team__isnull=False,
        name__isnull=False
    ).exclude(team__name='').first()

    if not test_player:
        print("❌ No test player with team available")
        return False

    print(f"Test player: {test_player.name} (Team: {test_player.team.name})")

    # Try to find by name+team
    found = find_tm_data_by_name_and_team(test_player.name, test_player.team.name)

    if found:
        print(f"✅ Found match: {found.get('name')} ({found.get('current_club', {}).get('name', 'N/A')})")
        return True
    else:
        print(f"⚠️  No match found by name+team")
        print(f"   This is OK if names don't match exactly")
        return None


def test_matching_by_name():
    """Test matching by name only"""
    print_section("5. MATCHING BY NAME ONLY TEST")

    # Get a player from Players model
    test_player = Players.objects.filter(
        name__isnull=False
    ).exclude(name='').first()

    if not test_player:
        print("❌ No test player available")
        return False

    print(f"Test player: {test_player.name}")

    # Try to find by name
    found = find_tm_data_by_name(test_player.name)

    if found:
        print(f"✅ Found match: {found.get('name')}")
        return True
    else:
        print(f"⚠️  No match found by name")
        print(f"   This requires 85%+ name similarity")
        return None


def test_main_flow():
    """Test the main update flow with a small sample"""
    print_section("6. MAIN UPDATE FLOW TEST")

    from apps.sport.views.update_players_transfermarket import (
        get_transfermarket_data_for_player,
        update_player_with_transfermarket_data
    )

    # Get a few test players
    test_players = Players.objects.filter(team__isnull=False)[:5]

    if not test_players:
        print("❌ No players available to test")
        return False

    print(f"Testing with {test_players.count()} sample players...\n")

    matched = 0
    for player in test_players:
        tm_data = get_transfermarket_data_for_player(player)

        if tm_data:
            matched += 1
            print(f"✅ {player.name[:30]:30} → {tm_data.get('name')[:30]:30} ({tm_data.get('current_market_value', 'N/A')})")
        else:
            print(f"❌ {player.name[:30]:30} → No match")

    print(f"\nMatch rate: {matched}/{test_players.count()} ({matched/test_players.count()*100:.1f}%)")

    if matched > 0:
        print("✅ Matching is working!")
        return True
    else:
        print("❌ No matches found")
        return False


def generate_recommendations():
    """Generate recommendations based on test results"""
    print_section("7. RECOMMENDATIONS")

    # Run all tests
    test1 = test_multisource_players()
    test2 = test_data_loading()
    test3 = test_matching_by_id()
    test4 = test_matching_by_name_and_team()
    test5 = test_matching_by_name()
    test6 = test_main_flow()

    print_section("SUMMARY & ACTION ITEMS")

    if not test1:
        print("🔴 ACTION: Populate MultiSourcePlayers with TransferMarket data")
        print("   Run your TransferMarket scraper first")
        return

    if not test2:
        print("🔴 ACTION: Data loading failed")
        print("   Check MultiSourcePlayers model and database connection")
        return

    if not test3:
        print("🟡 WARNING: ID matching not working")
        print("   Players don't have transfermarkt_id yet")

    if test4 is None or test5 is None:
        print("🟡 WARNING: Name-based matching has low accuracy")
        print("   Consider manually adding transfermarkt_id for important players")

    if test6:
        print("✅ SUCCESS: System is working correctly!")
        print("\nYou can now run the full update:")
        print("  1. Go to Admin Panel")
        print("  2. Click 'Update Players From Transfermarket'")
        print("  3. Select sport and run update")

        players_count = Players.objects.count()
        print(f"\nWill update {players_count} players")
    else:
        print("⚠️  Low match rate detected")
        print("   This might be due to name mismatches")
        print("   Recommendation: Manually add transfermarkt_id for key players")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("  TransferMarket Integration Debug Script")
    print("="*70)

    try:
        generate_recommendations()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70 + "\n")

