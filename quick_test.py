"""Quick test of PDF extractor"""
import sys
sys.path.insert(0, r'C:\Users\mhitl\PycharmProjects\digit_sport')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')

import django
django.setup()

from apps.sport.utils.pdf_extractor_final import VolleyballPDFExtractor

pdf_path = r"C:\Users\mhitl\PycharmProjects\digit_sport\KNL 21 25-12-28 Kuwait SC 3x0 Al Sahel - Match report.pdf"

print("Testing PDF Extractor...")
extractor = VolleyballPDFExtractor()
result = extractor.extract(pdf_path)

if 'error' in result:
    print(f"ERROR: {result['error']}")
else:
    print(f"\nTeams: {len(result['teams'])}")
    print(f"Total players: {result['total_players']}\n")

    for team in result['teams']:
        print(f"\n{team['name']}: {len(team['players'])} players")
        for p in team['players'][:5]:  # Show first 5
            s = p['stats']
            print(f"  #{p['player_number']} {p['player_name']}")
            print(f"    Pts={s['pts']}, Srv={s['serve_total']}/{s['serve_err']}/{s['serve_ace']}")
            print(f"    Rec={s['reception_total']}/{s['reception_err']}, Att={s['attack_total']}/{s['attack_err']}/{s['attack_pts']}")
            print(f"    Numbers: {p['parsed_numbers'][:10]}")

print("\nDone!")
