# Test the player matching logic with real Match object
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
django.setup()

from apps.sport.models import Players, Match, Teams

# Get the most recent match
match = Match.objects.filter(home_team__isnull=False, away_team__isnull=False).last()

if not match:
    print("No match found with home_team and away_team set")
    exit(1)

print(f"Testing with Match: {match}")
print(f"Home Team: {match.home_team} ({match.home_team.id})")
print(f"Away Team: {match.away_team} ({match.away_team.id})")
print("\n" + "=" * 70)

# Test names to match
test_names = [
    'Saqer Hamad',
    'Almuwainea Abdullah',
    'Hoag Nicholas',
    'Almisry Hussain'
]

print("TESTING PLAYER MATCHING LOGIC:\n")

for player_name in test_names:
    print(f"\nSearching for: '{player_name}'")
    print("-" * 70)

    # Strategy 1: Exact match
    p = Players.objects.filter(
        name__iexact=player_name,
        team__in=[match.home_team, match.away_team]
    ).first()
    if p:
        print(f"✓ EXACT MATCH: {p.name} (#{p.number}) - Team: {p.team}")
        continue
    print("✗ No exact match")

    # Strategy 2: Partial match
    p = Players.objects.filter(
        name__icontains=player_name,
        team__in=[match.home_team, match.away_team]
    ).first()
    if p:
        print(f"~ PARTIAL MATCH: {p.name} (#{p.number}) - Team: {p.team}")
        continue
    print("✗ No partial match in match teams")

    # Strategy 5: Global fallback
    p = Players.objects.filter(name__icontains=player_name).first()
    if p:
        print(f"⚠ GLOBAL FALLBACK: {p.name} (#{p.number}) - Team: {p.team}")
        print(f"  Problem: Player is in {p.team}, not in match teams")
    else:
        print("✗ NOT FOUND IN DATABASE")
        # Try to find similar names
        for part in player_name.split():
            similar = Players.objects.filter(name__icontains=part)
            if similar.exists():
                print(f"  Names with '{part}':")
                for s in similar[:3]:
                    print(f"    - {s.name} (#{s.number}) - {s.team}")
                break

print("\n" + "=" * 70)
print("All players in match teams:")
print("=" * 70)

if match.home_team:
    print(f"\n{match.home_team.name}:")
    for p in Players.objects.filter(team=match.home_team)[:15]:
        print(f"  {p.number:5} | {p.name}")

if match.away_team:
    print(f"\n{match.away_team.name}:")
    for p in Players.objects.filter(team=match.away_team)[:15]:
        print(f"  {p.number:5} | {p.name}")
