import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
django.setup()

from apps.sport.models import Match

print("Checking matches...")
matches = Match.objects.filter(home_team__isnull=False, away_team__isnull=False)
print(f"Found {matches.count()} matches with home_team and away_team set")

if matches.exists():
    m = matches.last()
    print(f"\nLatest match: {m}")
    print(f"Home team: {m.home_team}")
    print(f"Away team: {m.away_team}")
    print(f"Home team players: {m.home_team.team_player.count() if m.home_team else 0}")
    print(f"Away team players: {m.away_team.team_player.count() if m.away_team else 0}")
else:
    print("No matches found with both teams set")
    print("\nChecking all matches...")
    all_matches = Match.objects.all()[:5]
    for m in all_matches:
        print(f"  {m}: home={m.home_team}, away={m.away_team}")
