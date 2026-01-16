"""
PDF Diagnostic Integration - Generate diagnostic report for PDFs
"""

import pytesseract
from pdf2image import convert_from_path
import re
import logging

logger = logging.getLogger(__name__)


def generate_pdf_diagnostic_report(pdf_path):
    """
    Generate a diagnostic report for a PDF file.
    Returns a dictionary with diagnostic information.

    Returns:
    {
        'success': bool,
        'file_ok': bool,
        'pages_count': int,
        'ocr_works': bool,
        'text_extracted': str,
        'pages': [
            {
                'page_num': int,
                'char_count': int,
                'line_count': int,
                'sample_lines': [str],
                'has_team': bool,
                'has_players': bool,
                'issues': [str]
            }
        ],
        'issues': [str],
        'recommendations': [str],
        'summary': str
    }
    """

    diagnostic = {
        'success': False,
        'file_ok': False,
        'pages_count': 0,
        'ocr_works': False,
        'text_extracted': '',
        'pages': [],
        'issues': [],
        'recommendations': [],
        'summary': ''
    }

    try:
        import os
        if not os.path.exists(pdf_path):
            diagnostic['issues'].append(f"File not found: {pdf_path}")
            diagnostic['recommendations'].append("Check file path and try again")
            return diagnostic

        diagnostic['file_ok'] = True
        file_size = os.path.getsize(pdf_path) / 1024 / 1024

        # Convert PDF to images
        try:
            images = convert_from_path(pdf_path)
            diagnostic['pages_count'] = len(images)
        except Exception as e:
            diagnostic['issues'].append(f"Failed to convert PDF: {str(e)}")
            diagnostic['recommendations'].append("PDF may be corrupted. Try with a different PDF file")
            return diagnostic

        if not images:
            diagnostic['issues'].append("No pages found in PDF")
            diagnostic['recommendations'].append("PDF appears to be empty")
            return diagnostic

        # Run OCR on each page
        all_text = ""
        team_found = False
        player_found = False

        for page_idx, image in enumerate(images):
            try:
                text = pytesseract.image_to_string(image)
                all_text += text + "\n"

                lines = text.split('\n')
                non_empty_lines = [l.strip() for l in lines if l.strip()]

                page_diagnostic = {
                    'page_num': page_idx + 1,
                    'char_count': len(text),
                    'line_count': len(non_empty_lines),
                    'sample_lines': non_empty_lines[:10],
                    'has_team': False,
                    'has_players': False,
                    'issues': []
                }

                # Check for team headers
                if any(re.search(r'kuwait|sabah|sahel|razawi|qadisiya', line, re.IGNORECASE)
                       for line in non_empty_lines):
                    page_diagnostic['has_team'] = True
                    team_found = True

                # Check for players (number at start of line)
                if any(re.match(r'^\d+\s+', line) for line in non_empty_lines):
                    page_diagnostic['has_players'] = True
                    player_found = True

                # Check for issues
                if len(text) < 100:
                    page_diagnostic['issues'].append("Very little text extracted")
                if len(non_empty_lines) < 5:
                    page_diagnostic['issues'].append("Few lines of text found")

                diagnostic['pages'].append(page_diagnostic)
                diagnostic['ocr_works'] = True

            except Exception as e:
                diagnostic['pages'].append({
                    'page_num': page_idx + 1,
                    'char_count': 0,
                    'line_count': 0,
                    'sample_lines': [],
                    'has_team': False,
                    'has_players': False,
                    'issues': [f"OCR error: {str(e)}"]
                })

        # Analyze results
        if not diagnostic['ocr_works']:
            diagnostic['issues'].append("OCR failed on all pages")
            diagnostic['recommendations'].append("Install tesseract: sudo apt-get install tesseract-ocr")

        if not team_found:
            diagnostic['issues'].append("No team headers found (Kuwait SC, Al Sahel, etc.)")
            diagnostic['recommendations'].append("Ensure PDF contains team names at start of player sections")

        if not player_found:
            diagnostic['issues'].append("No player data found (no numbers at line start)")
            diagnostic['recommendations'].append("Verify PDF has player numbers, names, and statistics")

        if all_text and len(all_text) < 200:
            diagnostic['issues'].append("Very little text extracted from PDF")
            diagnostic['recommendations'].append("PDF may be scanned image. Try higher resolution scan")

        # Generate summary
        if team_found and player_found:
            diagnostic['success'] = True
            diagnostic['summary'] = "✅ PDF looks good! Should parse successfully"
            diagnostic['recommendations'] = ["Try uploading again"]
        else:
            diagnostic['summary'] = "⚠️ PDF has issues - extraction likely to fail"
            if not team_found:
                diagnostic['recommendations'].append("Add team headers or verify team data")
            if not player_found:
                diagnostic['recommendations'].append("Ensure player numbers and data are visible")

            if not diagnostic['ocr_works']:
                diagnostic['recommendations'].append("Check if text can be selected in PDF viewer")
                diagnostic['recommendations'].append("If not, use digital/OCR-processed PDF instead of scanned image")

        diagnostic['text_extracted'] = all_text[:1000]  # Store first 1000 chars

    except Exception as e:
        logger.error(f"Diagnostic error: {e}")
        diagnostic['issues'].append(f"Diagnostic error: {str(e)}")
        diagnostic['recommendations'].append("Contact support with this error message")

    return diagnostic


def format_diagnostic_for_display(diagnostic):
    """
    Format diagnostic report as readable text for user display.
    """

    lines = []

    lines.append("=" * 70)
    lines.append("PDF DIAGNOSTIC REPORT")
    lines.append("=" * 70)

    # File info
    lines.append(f"\n📄 FILE CHECK")
    lines.append(f"  File OK: {'✅' if diagnostic['file_ok'] else '❌'}")

    # Pages
    if diagnostic['pages_count'] > 0:
        lines.append(f"\n📑 PAGES: {diagnostic['pages_count']} page(s)")

    # OCR Status
    lines.append(f"\n🔍 OCR: {'✅ Working' if diagnostic['ocr_works'] else '❌ Not working'}")

    # Page details
    if diagnostic['pages']:
        lines.append(f"\n📊 PAGE ANALYSIS:")
        for page in diagnostic['pages'][:3]:  # Show first 3 pages
            lines.append(f"\n  Page {page['page_num']}:")
            lines.append(f"    Characters: {page['char_count']}")
            lines.append(f"    Non-empty lines: {page['line_count']}")
            lines.append(f"    Has team header: {'✅' if page['has_team'] else '❌'}")
            lines.append(f"    Has player data: {'✅' if page['has_players'] else '❌'}")

            if page['sample_lines']:
                lines.append(f"    Sample text:")
                for sample in page['sample_lines'][:5]:
                    lines.append(f"      {sample[:60]}")

            if page['issues']:
                lines.append(f"    Issues: {', '.join(page['issues'])}")

    # Issues
    if diagnostic['issues']:
        lines.append(f"\n⚠️  ISSUES FOUND:")
        for issue in diagnostic['issues']:
            lines.append(f"  • {issue}")

    # Summary
    lines.append(f"\n📋 SUMMARY:")
    lines.append(f"  {diagnostic['summary']}")

    # Recommendations
    if diagnostic['recommendations']:
        lines.append(f"\n💡 RECOMMENDATIONS:")
        for rec in diagnostic['recommendations']:
            lines.append(f"  • {rec}")

    lines.append("\n" + "=" * 70)

    return "\n".join(lines)

