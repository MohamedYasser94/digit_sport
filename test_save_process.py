#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
django.setup()

from apps.sport.models import Players, Match, MatchPlayerReport, PlayerStatics

# Get the most recent match
match = Match.objects.filter(home_team__isnull=False, away_team__isnull=False).last()

if not match:
    print("ERROR: No match found with home_team and away_team")
    exit(1)

print(f"Match: {match}")
print(f"Home Team: {match.home_team} - Players: {Players.objects.filter(team=match.home_team).count()}")
print(f"Away Team: {match.away_team} - Players: {Players.objects.filter(team=match.away_team).count()}")
print()

# Load extracted JSON to test with real data
json_file = 'KNL 21 25-12-28 Kuwait SC 3x0 Al Sahel - Match report_final_extracted.json'
if not os.path.exists(json_file):
    print(f"ERROR: {json_file} not found")
    exit(1)

with open(json_file, 'r', encoding='utf-8') as f:
    extraction_data = json.load(f)

print(f"Extracted {extraction_data['total_players']} players from PDF")
print()

# Test saving
updated_count = 0
skipped_count = 0
error_count = 0

for team_data in extraction_data['teams']:
    print(f"\nTeam: {team_data['name']}")
    for player_data in team_data['players'][:5]:  # Test first 5 players per team
        player_name = player_data.get('player_name', '').strip()
        player_number = player_data.get('player_number', '').strip()
        stats = player_data.get('stats', {})

        if not player_name:
            continue

        print(f"\n  Testing: {player_name} (#{player_number})")

        # Try to find player
        player = Players.objects.filter(
            name__icontains=player_name,
            team__in=[match.home_team, match.away_team]
        ).first()

        if not player:
            print(f"    ✗ NOT FOUND in match teams")
            skipped_count += 1
            continue

        print(f"    ✓ FOUND: {player.name} (Team: {player.team})")

        # Try to save
        try:
            defaults = {
                'point_total': str(stats.get('pts', 0)),
                'serve_total': str(stats.get('serve_total', 0)),
                'serve_err': str(stats.get('serve_err', 0)),
                'serve_ace': str(stats.get('serve_ace', 0)),
                'reception_total': str(stats.get('reception_total', 0)),
                'reception_err': str(stats.get('reception_err', 0)),
                'reception_exc': str(stats.get('reception_exc', 0)),
                'attack_total': str(stats.get('attack_total', 0)),
                'attack_err': str(stats.get('attack_err', 0)),
                'attack_pts': str(stats.get('attack_pts', 0)),
                'block_pts': str(stats.get('block_pts', 0)),
                'static_type': 'General'
            }

            mpr, created = MatchPlayerReport.objects.update_or_create(
                player=player,
                match=match,
                defaults=defaults
            )

            ps, created2 = PlayerStatics.objects.update_or_create(
                player=player,
                defaults=defaults
            )

            print(f"    ✓ SAVED: Points={stats.get('pts', 0)}, Serve={stats.get('serve_total', 0)}")
            updated_count += 1

        except Exception as e:
            print(f"    ✗ ERROR: {str(e)}")
            error_count += 1

print(f"\n\n{'='*70}")
print(f"SUMMARY:")
print(f"  Updated: {updated_count}")
print(f"  Skipped: {skipped_count}")
print(f"  Errors: {error_count}")
print(f"{'='*70}")
