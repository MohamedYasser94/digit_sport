#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
django.setup()

from apps.sport.models import Players, Sport
from apps.sport.models.multi_source_players import MultiSourcePlayers

print("\n" + "="*70)
print("DATA DIAGNOSTIC")
print("="*70)

# Check Players
total_players = Players.objects.count()
players_with_market_value = Players.objects.filter(current_market_value__isnull=False).exclude(current_market_value='').count()

print(f"\nPlayers Model:")
print(f"  Total: {total_players}")
print(f"  With market_value: {players_with_market_value}")

# Check MultiSourcePlayers
total_multi = MultiSourcePlayers.objects.count()
multi_with_name = MultiSourcePlayers.objects.filter(name__isnull=False).exclude(name='').count()
multi_with_tm_id = MultiSourcePlayers.objects.filter(transfermarkt_id__isnull=False).exclude(transfermarkt_id='').count()
multi_with_market_value = MultiSourcePlayers.objects.filter(current_market_value__isnull=False).exclude(current_market_value='').count()
multi_with_image = MultiSourcePlayers.objects.filter(image_url__isnull=False).exclude(image_url='').count()

print(f"\nMultiSourcePlayers Model:")
print(f"  Total: {total_multi}")
print(f"  With names: {multi_with_name}")
print(f"  With transfermarkt_id: {multi_with_tm_id}")
print(f"  With market_value: {multi_with_market_value}")
print(f"  With image_url: {multi_with_image}")

# Show sample
print(f"\nSample Data:")
if total_multi > 0:
    samples = MultiSourcePlayers.objects.all()[:3]
    for i, player in enumerate(samples, 1):
        print(f"\n  {i}. {player.name or 'NO NAME'}")
        print(f"     TM ID: {player.transfermarkt_id or 'None'}")
        print(f"     Market Value: {player.current_market_value or 'None'}")
        print(f"     Height: {player.height or 'None'}")
        print(f"     Position: {player.position or 'None'}")
else:
    print("  No MultiSourcePlayers data")

# Recommendations
print(f"\n" + "="*70)
print("RECOMMENDATIONS:")
print("="*70)

if total_multi == 0:
    print("\n❌ MultiSourcePlayers is EMPTY")
    print("   Action: You need to populate it first")
    print("   1. Go to Admin Panel")
    print("   2. Click 'Fetch Players From API'")
    print("   3. Select 'Football'")
    print("   4. Wait for completion")
elif multi_with_market_value == 0:
    print(f"\n⚠️  MultiSourcePlayers has {multi_with_name} players")
    print("   BUT NO MARKET VALUES or IMAGES")
    print("   Action: You need to scrape TransferMarket data")
    print("   Then enrich MultiSourcePlayers with market values")
else:
    print(f"\n✅ MultiSourcePlayers has enriched data!")
    print(f"   Market values: {multi_with_market_value}")
    print(f"   Action: Run update_players_from_multisource('football')")
    print("   Command: python data_update.py")

print("\n" + "="*70 + "\n")

