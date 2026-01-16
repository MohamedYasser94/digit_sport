#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
django.setup()

from apps.sport.models import Players, Teams

# Find Kuwait SC and Al Sahel teams
kuwait = Teams.objects.filter(name__icontains='Kuwait').first()
alsahel = Teams.objects.filter(name__icontains='Sahel').first()

print("=" * 70)
print("KUWAIT SC PLAYERS:")
print("=" * 70)
if kuwait:
    count = 0
    for p in kuwait.team_player.all():
        print(f"{p.number:5} | {p.name:30} | ID: {p.id}")
        count += 1
        if count >= 25:
            print(f"... and {kuwait.team_player.count() - count} more")
            break
else:
    print("Kuwait team not found")

print("\n" + "=" * 70)
print("AL SAHEL PLAYERS:")
print("=" * 70)
if alsahel:
    count = 0
    for p in alsahel.team_player.all():
        print(f"{p.number:5} | {p.name:30} | ID: {p.id}")
        count += 1
        if count >= 25:
            print(f"... and {alsahel.team_player.count() - count} more")
            break
else:
    print("Al Sahel team not found")

print("\n" + "=" * 70)
print("SEARCH RESULTS FOR SPECIFIC PLAYERS:")
print("=" * 70)

# Search for players we need to match
search_names = ['Saqer Hamad', 'Almuwainea Abdullah', 'Hoag Nicholas', 'Almisry Hussain']

for name in search_names:
    print(f"\nSearching for: {name}")
    # Try exact match
    exact = Players.objects.filter(name__iexact=name).first()
    if exact:
        print(f"  ✓ EXACT: {exact.name} (#{exact.number}) - Team: {exact.team}")
    else:
        # Try partial match
        partial = Players.objects.filter(name__icontains=name).first()
        if partial:
            print(f"  ~ PARTIAL: {partial.name} (#{partial.number}) - Team: {partial.team}")
        else:
            print(f"  ✗ NOT FOUND")

            # Show similar names
            parts = name.split()
            for part in parts:
                similar = Players.objects.filter(name__icontains=part)
                if similar.exists():
                    print(f"    Similar names with '{part}':")
                    for s in similar[:3]:
                        print(f"      - {s.name} (#{s.number})")
                    break
