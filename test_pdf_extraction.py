#!/usr/bin/env python
"""
Test script to debug PDF extraction and data parsing.
Run from Django shell: python manage.py shell < test_pdf_extraction.py
Or run directly: python test_pdf_extraction.py <pdf_path>
"""

import sys
import os
import django

# Setup Django if running as script
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
    sys.path.insert(0, '/Users/mhitl/PycharmProjects/digit_sport')
    django.setup()

from apps.sport.utils.pdf_parser import parse_match_report
from apps.sport.models.models import Match, Players
from apps.sport.models.operations import MatchPlayerReport, PlayerStatics
import json


def test_pdf_extraction(pdf_path):
    """Test PDF extraction and show detailed results"""
    print(f"\n{'='*70}")
    print(f"Testing PDF Extraction: {pdf_path}")
    print(f"{'='*70}\n")

    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found - {pdf_path}")
        return

    try:
        # Parse the PDF
        print("📄 Parsing PDF...")
        parsed_stats = parse_match_report(pdf_path)

        print(f"\n✅ Successfully parsed {len(parsed_stats)} players from PDF\n")

        if not parsed_stats:
            print("⚠️  No players found in PDF")
            return

        # Display extracted data
        print(f"{'='*70}")
        print("Extracted Player Data:")
        print(f"{'='*70}\n")

        for idx, stat in enumerate(parsed_stats, 1):
            print(f"\n[{idx}] {stat['player_number']} - {stat['player_name']}")
            print(f"    Team: {stat.get('team', 'Unknown')}")
            print(f"    Statistics:")
            for key, value in stat.items():
                if key not in ['player_name', 'player_number', 'team']:
                    print(f"      - {key}: {value}")

        # Database matching test
        print(f"\n{'='*70}")
        print("Database Matching Test:")
        print(f"{'='*70}\n")

        matched_count = 0
        unmatched = []

        for stat in parsed_stats:
            player = Players.objects.filter(
                name__icontains=stat['player_name']
            ).first()

            if not player:
                unmatched.append(stat)
            else:
                matched_count += 1
                print(f"✅ Matched: {stat['player_name']} → {player.name} (ID: {player.id})")

        print(f"\n📊 Summary:")
        print(f"  Total players in PDF: {len(parsed_stats)}")
        print(f"  Matched in database: {matched_count}")
        print(f"  Unmatched: {len(unmatched)}")

        if unmatched:
            print(f"\n⚠️  Unmatched players:")
            for p in unmatched:
                print(f"  • {p['player_number']} - {p['player_name']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_match_list():
    """List available matches for testing"""
    print(f"\n{'='*70}")
    print("Available Matches:")
    print(f"{'='*70}\n")

    matches = Match.objects.all()[:10]

    if not matches:
        print("❌ No matches found in database")
        return

    for match in matches:
        print(f"  • {match.slug}: {match}")


def test_player_list():
    """List sample players"""
    print(f"\n{'='*70}")
    print("Sample Players in Database:")
    print(f"{'='*70}\n")

    players = Players.objects.all()[:10]

    if not players:
        print("❌ No players found in database")
        return

    for player in players:
        print(f"  • {player.id}: {player.name} ({player.number})")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        test_pdf_extraction(pdf_path)
    else:
        print("PDF Extraction Test Utility")
        print("=" * 70)
        test_player_list()
        test_match_list()
        print("\nUsage: python test_pdf_extraction.py <pdf_path>")

