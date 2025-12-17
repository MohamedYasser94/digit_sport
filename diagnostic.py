"""
DIAGNOSTIC SCRIPT - Check what data you actually have
Run this to understand your data situation

Usage:
    python manage.py shell < diagnostic.py

Or in shell:
    exec(open('diagnostic.py').read())
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')

import django
django.setup()

from apps.sport.models import Players, Sport
from apps.sport.models.multi_source_players import MultiSourcePlayers


def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


print_section("1. PLAYERS MODEL STATUS")

# Check Players table
total_players = Players.objects.count()
players_with_tm_id = Players.objects.filter(transfermarkt_id__isnull=False).exclude(transfermarkt_id='').count()
players_with_image_url = Players.objects.filter(image_url__isnull=False).exclude(image_url='').count()
players_with_market_value = Players.objects.filter(current_market_value__isnull=False).exclude(current_market_value='').count()

print(f"Total Players: {total_players}")
print(f"  - With transfermarkt_id: {players_with_tm_id}")
print(f"  - With image_url: {players_with_image_url}")
print(f"  - With market_value: {players_with_market_value}")

print_section("2. MULTISOURCE PLAYERS STATUS")

# Check MultiSourcePlayers table
total_multi = MultiSourcePlayers.objects.count()
multi_with_tm_id = MultiSourcePlayers.objects.filter(transfermarkt_id__isnull=False).exclude(transfermarkt_id='').count()
multi_with_name = MultiSourcePlayers.objects.filter(name__isnull=False).exclude(name='').count()
multi_with_market_value = MultiSourcePlayers.objects.filter(current_market_value__isnull=False).exclude(current_market_value='').count()
multi_with_image = MultiSourcePlayers.objects.filter(image_url__isnull=False).exclude(image_url='').count()

print(f"Total MultiSourcePlayers: {total_multi}")
print(f"  - With transfermarkt_id: {multi_with_tm_id}")
print(f"  - With name: {multi_with_name}")
print(f"  - With market_value: {multi_with_market_value}")
print(f"  - With image_url: {multi_with_image}")

print_section("3. SAMPLE DATA FROM MULTISOURCE")

if total_multi > 0:
    samples = MultiSourcePlayers.objects.all()[:5]
    for player in samples:
        print(f"\n📦 {player.name or 'NO NAME'}")
        print(f"   TM ID: {player.transfermarkt_id or 'None'}")
        print(f"   Market Value: {player.current_market_value or 'None'}")
        print(f"   Height: {player.height or 'None'}")
        print(f"   Position: {player.position or 'None'}")
        print(f"   Image URL: {'Yes' if player.image_url else 'No'}")

print_section("4. DATA READINESS")

if multi_with_name > 0:
    print("✅ MultiSourcePlayers has names")
    if multi_with_market_value > 0 or multi_with_image > 0:
        print("✅ MultiSourcePlayers has enriched data (market value or images)")
        print("\n→ YOU CAN RUN: update_players_from_multisource('football')")
    else:
        print("⚠️  MultiSourcePlayers has NO enriched data yet")
        print("→ Need to run: AdminMonksPlayersGetData + TransferMarket scraping")
elif multi_with_tm_id > 0:
    print("⚠️  MultiSourcePlayers has TM IDs but no names")
    print("→ Need to populate MultiSourcePlayers first")
else:
    print("❌ MultiSourcePlayers is empty or has no useful data")
    print("→ Need to run: AdminMonksPlayersGetData first")

print_section("5. RECOMMENDATIONS")

if total_players > 0:
    print(f"You have {total_players} Players in main model")

    if total_multi > 0 and multi_with_name > 0:
        print("\n✅ READY: Run name-based matching update")
        print("   Command: python manage.py shell")
        print("   Code: from apps.sport.views.update_players_transfermarket_simple import update_players_from_multisource")
        print("         update_players_from_multisource('football')")
    else:
        print("\n❌ NEED DATA: First populate MultiSourcePlayers")
        print("   Steps:")
        print("   1. Run: AdminMonksPlayersGetData (fetch from Sportmonks)")
        print("   2. Run: TransferMarket scraper/importer")
        print("   3. Then run: update_players_from_multisource('football')")

print("\n" + "="*70 + "\n")

