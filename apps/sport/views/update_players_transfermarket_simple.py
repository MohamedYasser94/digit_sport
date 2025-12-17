"""
Alternative TransferMarket Update - Works with available data
Run this when you have scraped TransferMarket data or MultiSourcePlayers with TM IDs

Usage:
    python manage.py shell
    from apps.sport.views.update_players_transfermarket_simple import update_players_from_multisource
    update_players_from_multisource(sport='football', limit=None)
"""

from django.utils import timezone
from apps.sport.models import Players, Sport
from apps.sport.models.multi_source_players import MultiSourcePlayers
from difflib import SequenceMatcher
import re
from decimal import Decimal


def update_players_from_multisource(sport='football', limit=None):
    """
    Update Players from MultiSourcePlayers that have ANY data
    This works even if transfermarkt_id is not populated
    """

    sport_obj = Sport.objects.filter(name__iexact=sport).first()
    if not sport_obj:
        print(f"❌ Sport '{sport}' not found")
        return

    # Get Players to update
    players = Players.objects.filter(sport=sport_obj)
    if limit:
        players = players[:limit]

    total = players.count()
    updated = 0
    matched = 0
    failed = 0

    print(f"\n🔄 Starting update for {total} players...")
    print("="*70)

    # Get all MultiSourcePlayers data
    multi_players = MultiSourcePlayers.objects.filter(sport=sport_obj)
    multi_dict = {}

    # Index by name for fast lookup
    for mp in multi_players:
        if mp.name:
            key = mp.name.lower().strip()
            if key not in multi_dict:
                multi_dict[key] = mp

    print(f"📊 MultiSourcePlayers available: {len(multi_dict)}")
    print("="*70)

    # Try to match and update each player
    for i, player in enumerate(players, 1):
        if not player.name:
            failed += 1
            continue

        # Try exact match first
        match = multi_dict.get(player.name.lower().strip())

        # Try fuzzy match if no exact match
        if not match:
            best_score = 0.0
            for key, mp in multi_dict.items():
                similarity = SequenceMatcher(None, player.name.lower(), key).ratio()
                if similarity > best_score and similarity >= 0.80:
                    best_score = similarity
                    match = mp

        if match:
            matched += 1
            # Update player with MultiSourcePlayers data
            try:
                if match.image_url and not player.image_url:
                    player.image_url = match.image_url

                if match.current_market_value:
                    player.current_market_value = match.current_market_value
                    # Parse numeric value
                    _parse_market_value(player, match.current_market_value)

                if match.height:
                    player.height = match.height

                if match.weight:
                    player.weight = match.weight

                if match.age:
                    player.age = match.age

                if match.position:
                    player.position = match.position

                if match.foot:
                    player.foot = match.foot

                if match.citizenship:
                    player.citizenship = match.citizenship

                if match.transfermarkt_id:
                    player.transfermarkt_id = match.transfermarkt_id

                if match.joined:
                    player.joined = match.joined

                if match.contract_expires:
                    player.contract_expires = match.contract_expires

                if match.player_agent_name:
                    player.player_agent_name = match.player_agent_name

                if match.outfitter:
                    player.outfitter = match.outfitter

                player.market_value_last_updated = timezone.now()
                player.save()
                updated += 1

                if i % 100 == 0:
                    print(f"✅ Processed: {i}/{total}")
            except Exception as e:
                print(f"❌ Error updating {player.name}: {e}")
                failed += 1
        else:
            failed += 1

    print("="*70)
    print(f"\n📊 FINAL RESULTS:")
    print(f"   Total Players: {total}")
    print(f"   ✅ Updated: {updated}")
    print(f"   ✅ Matched: {matched}")
    print(f"   ⚠️  Failed: {failed}")
    print(f"   Success Rate: {(updated/total*100 if total > 0 else 0):.1f}%")
    print()


def _parse_market_value(player, value_str):
    """Parse market value string to numeric value"""
    if not value_str:
        return

    value_str = str(value_str).strip()

    # Extract numeric value and multiplier (€50.00m, $25M, etc.)
    pattern = r'([€$£¥])?([\d,.]+)([kmb])?'
    match = re.search(pattern, value_str.lower())

    if match:
        currency_symbol, number_str, multiplier = match.groups()

        currency_map = {'€': 'EUR', '$': 'USD', '£': 'GBP', '¥': 'JPY'}

        if currency_symbol:
            player.market_value_currency = currency_map.get(currency_symbol, 'EUR')
        elif not player.market_value_currency:
            player.market_value_currency = 'EUR'

        try:
            number = float(number_str.replace(',', ''))

            if multiplier == 'k':
                number *= 1000
            elif multiplier == 'm':
                number *= 1000000
            elif multiplier == 'b':
                number *= 1000000000

            player.market_value_numeric = Decimal(str(number))
        except (ValueError, TypeError):
            pass


if __name__ == '__main__':
    # Run from command line
    update_players_from_multisource(sport='football')

