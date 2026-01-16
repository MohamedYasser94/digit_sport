import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
django.setup()

from apps.sport.models import Players, Teams

# Search for players
names_to_find = ['Saqer', 'Almuwainea', 'Hoag', 'Almisry', 'Hamad', 'Abdullah', 'Nicholas', 'Hussain']

print("Searching for player name parts...")
all_matches = {}
for name_part in names_to_find:
    matches = Players.objects.filter(name__icontains=name_part)
    if matches.exists():
        all_matches[name_part] = list(matches.values('id', 'name', 'number', 'team__name')[:5])

for part, matches in all_matches.items():
    print(f"\nMatches for '{part}':")
    for m in matches:
        print(f"  - {m['name']} (#{m['number']}) Team: {m['team__name']}")
