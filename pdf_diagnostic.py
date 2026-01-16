#!/usr/bin/env python
"""
PDF Diagnostic Tool - Debug PDF extraction issues

Run this to diagnose why PDFs aren't being parsed correctly.
"""

import sys
import os

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')

import django
django.setup()

from apps.sport.utils.pdf_parser import parse_match_report
from pdf2image import convert_from_path
import pytesseract
import re


def diagnose_pdf(pdf_path):
    """Comprehensive PDF diagnostic"""

    print("\n" + "="*80)
    print("PDF DIAGNOSTIC TOOL")
    print("="*80)

    # Step 1: File check
    print(f"\n[Step 1] FILE CHECK")
    print(f"Path: {pdf_path}")

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return

    file_size = os.path.getsize(pdf_path) / 1024 / 1024
    print(f"✅ File exists")
    print(f"✅ File size: {file_size:.2f} MB")

    # Step 2: PDF to Images
    print(f"\n[Step 2] PDF TO IMAGES CONVERSION")
    try:
        images = convert_from_path(pdf_path)
        print(f"✅ Successfully converted to {len(images)} pages")
    except Exception as e:
        print(f"❌ Error converting PDF: {e}")
        return

    # Step 3: OCR on each page
    print(f"\n[Step 3] OCR TEXT EXTRACTION")

    for page_idx, image in enumerate(images):
        print(f"\n--- Page {page_idx + 1} ---")
        try:
            text = pytesseract.image_to_string(image)
            lines = text.split('\n')

            print(f"  ✅ OCR successful")
            print(f"  📊 Total characters: {len(text)}")
            print(f"  📊 Total lines: {len(lines)}")
            print(f"  📊 Non-empty lines: {len([l for l in lines if l.strip()])}")

            # Show first 10 non-empty lines
            print(f"\n  First 10 lines of OCR output:")
            count = 0
            for line in lines:
                if line.strip() and count < 10:
                    print(f"    [{count+1}] {line[:80]}")
                    count += 1

            if count == 0:
                print(f"    ⚠️  No text extracted from this page!")

        except Exception as e:
            print(f"  ❌ OCR error: {e}")
            continue

    # Step 4: Full parser test
    print(f"\n[Step 4] FULL PARSER TEST")
    try:
        parsed = parse_match_report(pdf_path)
        print(f"✅ Parser returned {len(parsed)} players")

        if len(parsed) > 0:
            print(f"\n  Sample players extracted:")
            for p in parsed[:3]:
                print(f"    #{p['player_number']} - {p['player_name']}")
                print(f"      Points: {p['pts']}")
        else:
            print(f"⚠️  No players extracted!")
            print(f"\n  DIAGNOSIS:")
            print(f"  • Check if PDF contains player statistics table")
            print(f"  • Ensure team headers are visible (Kuwait SC, Al Sahel, etc.)")
            print(f"  • Verify player data has number, name, and statistics")
            print(f"  • Try OCR with higher resolution PDF")

    except Exception as e:
        print(f"❌ Parser error: {e}")
        import traceback
        traceback.print_exc()

    # Step 5: Recommendations
    print(f"\n[Step 5] RECOMMENDATIONS")

    if len(parsed) == 0:
        print("""
The parser could not extract any players. Try these solutions:

1. CHECK PDF FORMAT
   • Ensure PDF contains a statistics table
   • Look for team names (Kuwait SC, Al Sahel, etc.)
   • Check if player numbers, names, and stats are visible

2. IMPROVE PDF QUALITY
   • Use a higher resolution PDF (150+ DPI)
   • Ensure text is clear and crisp
   • Avoid heavily compressed PDFs

3. PREPARE BETTER PDF
   • Scan with better quality settings
   • Ensure good contrast (black text on white)
   • Remove extra images or content

4. TEST OCR SEPARATELY
   • Try: python manage.py test_pdf_upload "file.pdf" --verbose
   • Check debug output for actual OCR text

5. MANUAL DATA ENTRY
   • If PDF parsing fails, enter data manually via admin
   • Or use alternative data import method
        """)
    else:
        print(f"✅ SUCCESS! {len(parsed)} players extracted")

    print("\n" + "="*80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_diagnostic.py <pdf_path>")
        print("Example: python pdf_diagnostic.py match_report.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]
    diagnose_pdf(pdf_path)

