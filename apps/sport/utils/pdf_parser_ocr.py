import pytesseract
from pdf2image import convert_from_path
import re
import os


def parse_match_report_ocr(pdf_path):
    """
    Parses a volleyball match report PDF using OCR and extracts player statistics.
    """
    # Convert PDF to images
    images = convert_from_path(pdf_path)

    # We focus on the last page as per user's file (it's a 1-page PDF in this case)
    # But logic should handle multiple pages if they exist
    all_stats = []

    for i, image in enumerate(images):
        # Perform OCR
        text = pytesseract.image_to_string(image)

        # Split into lines
        lines = text.split('\n')

        # Identify team sections
        # The PDF has "Kuwait SC 25-26" and "Al Sahel 25-26"

        current_team = None
        for line in lines:
            line = line.strip()
            if not line: continue

            # Detect team headers
            if "Kuwait SC" in line:
                current_team = "Kuwait SC"
                continue
            elif "Al Sahel" in line:
                current_team = "Al Sahel"
                continue

            # Look for player lines: starts with a number, then name, then stats
            # Example: "13 L Safar Ibrahim . . . -2 . . . 17 2 65% ( 29%) . . . . ."
            # Example: "4 Hoag Nicholas 4 4 4 6.3 16 4 +10 16 4 1 11 1 55% ( 36%) 25 1 . 15 60%"

            match = re.match(r'^(\d+)\s+(?:L\s+)?([A-Za-z\s]+)\s+(.*)', line)
            if match:
                p_num = match.group(1)
                p_name = match.group(2).strip()
                remaining = match.group(3)

                # Extract numbers from the remaining part
                # We need to be careful as there are dots and percentages
                # Let's extract all numeric-looking sequences
                parts = re.findall(r'[\d\+\-\%]+', remaining)

                # Mapping based on the visual structure:
                # Tot Pts is usually the first or second number after the name/vote
                # This is tricky with OCR because dots might be missed or misinterpreted

                # For the sake of robustness, we'll try to find the "Tot" column
                # In "4 Hoag Nicholas 4 4 4 6.3 16 4 +10 16 4 1 11 1 55% ( 36%) 25 1 . 15 60%"
                # 16 is Tot Pts

                stats = {
                    'player_name': p_name,
                    'player_number': p_num,
                    'team': current_team,
                    'raw_line': line,
                    'extracted_parts': parts
                }

                # Attempt to map parts to fields (this is heuristic and might need tuning)
                if len(parts) > 5:
                    # This is a very rough mapping and should be refined based on actual needs
                    stats['pts'] = parts[4] if len(parts) > 4 else "0"
                    stats['serve_total'] = parts[7] if len(parts) > 7 else "0"
                    stats['serve_err'] = parts[8] if len(parts) > 8 else "0"
                    stats['serve_ace'] = parts[9] if len(parts) > 9 else "0"

                all_stats.append(stats)

    return all_stats


if __name__ == "__main__":
    pdf_path = "/home/ubuntu/upload/KNL2125-12-28KuwaitSC3x0AlSahel-Matchreport.pdf"
    results = parse_match_report_ocr(pdf_path)
    for r in results:
        print(f"Team: {r['team']} | Player: {r['player_name']} | Pts: {r.get('pts', 'N/A')}")
