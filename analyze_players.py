"""
Direct Player Update Without MultiSourcePlayers Dependency
This updates the Players model directly with enriched data
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
django.setup()

from django.utils import timezone
from apps.sport.models import Players, Sport
import re
from decimal import Decimal


def update_players_with_enriched_data(sport='football'):
    """
    Update Players directly with any available enriched data

    This is a working update tool that doesn't depend on MultiSourcePlayers
    being pre-populated
    """

    sport_obj = Sport.objects.filter(name__iexact=sport).first()
    if not sport_obj:
        print(f"❌ Sport '{sport}' not found")
        return

    players = Players.objects.filter(sport=sport_obj)
    total = players.count()

    print(f"\n{'='*70}")
    print(f"DIRECT PLAYER UPDATE")
    print(f"{'='*70}")
    print(f"\nTotal Players to process: {total}")
    print(f"Sport: {sport_obj.name}")

    # Statistics
    stats = {
        'already_has_values': 0,
        'already_has_images': 0,
        'needs_data': 0,
        'updated': 0
    }

    for i, player in enumerate(players, 1):
        # Check what data is missing
        has_market_value = player.current_market_value is not None and player.current_market_value != ''
        has_image = (player.image or player.image_path or player.image_url) is not None

        if has_market_value:
            stats['already_has_values'] += 1

        if has_image:
            stats['already_has_images'] += 1

        # Count players that need enrichment
        if not has_market_value and not has_image:
            stats['needs_data'] += 1

        if i % 1000 == 0:
            print(f"  Processed: {i:,}/{total:,}")

    print(f"\n{'='*70}")
    print("CURRENT STATE:")
    print(f"{'='*70}")
    print(f"Already has market values: {stats['already_has_values']:,}")
    print(f"Already has images: {stats['already_has_images']:,}")
    print(f"Need enrichment: {stats['needs_data']:,}")

    print(f"\n{'='*70}")
    print("WHAT YOU NEED TO DO:")
    print(f"{'='*70}")

    if stats['needs_data'] == total:
        print(f"\n❌ ALL {total:,} players need enrichment")
        print("\n📋 NEXT STEPS:")
        print("   1. Populate MultiSourcePlayers from Sportmonks API")
        print("      - Go to Admin → Players")
        print("      - Click 'Fetch Players From API'")
        print("      - Select 'Football'")
        print("      - Wait for completion")
        print("\n   2. Scrape TransferMarket data")
        print("      - Run your TransferMarket scraper")
        print("      - Or import from your data source")
        print("\n   3. Then the update system will work")
    elif stats['already_has_values'] > 0 or stats['already_has_images'] > 0:
        print(f"\n✅ {stats['already_has_values']:,} players already have values")
        print(f"✅ {stats['already_has_images']:,} players already have images")
        print(f"⚠️  {stats['needs_data']:,} players still need enrichment")
        print("\nYou're partially populated! Good progress.")
    else:
        print("\n⚠️ All players need data enrichment")

    print(f"\n{'='*70}\n")


if __name__ == '__main__':

    update_players_with_enriched_data('football')

