import pytesseract
from pdf2image import convert_from_path
import re
import os
import logging

logger = logging.getLogger(__name__)


def parse_match_report(pdf_path):
    """
    Parses a volleyball match report PDF using OCR and extracts player statistics.
    Returns a list of dictionaries, each containing player stats.

    Expected PDF format: Team headers followed by player rows with name and stats
    More flexible to handle various PDF formats and OCR variations.
    """
    try:
        images = convert_from_path(pdf_path)
    except Exception as e:
        logger.error(f"Error converting PDF to images: {e}")
        print(f"Error converting PDF to images: {e}")
        return []

    if not images:
        logger.error("No pages found in PDF")
        return []

    all_stats = []
    found_any_player = False

    for page_idx, image in enumerate(images):
        try:
            # Perform OCR
            text = pytesseract.image_to_string(image)
            logger.debug(f"Page {page_idx + 1} OCR text length: {len(text)} characters")
            print(f"[DEBUG] Page {page_idx + 1} OCR output (first 500 chars):\n{text[:500]}\n")

            if not text or len(text.strip()) < 10:
                logger.warning(f"Page {page_idx + 1}: No meaningful OCR text extracted")
                continue

            lines = text.split('\n')
            current_team = None

            for line_idx, line in enumerate(lines):
                line = line.strip()
                if not line or len(line) < 2:
                    continue

                # Detect team headers (more flexible)
                if re.search(r'kuwait|sabah|al.?razawi', line, re.IGNORECASE):
                    current_team = "Kuwait SC"
                    logger.debug(f"Found team: {current_team}")
                    print(f"[DEBUG] Team detected: {current_team} from line: {line}")
                    continue
                elif re.search(r'sahel|qadisiya|fahaheel', line, re.IGNORECASE):
                    current_team = "Al Sahel"
                    logger.debug(f"Found team: {current_team}")
                    print(f"[DEBUG] Team detected: {current_team} from line: {line}")
                    continue

                # Skip obvious header rows
                if re.search(r'^\s*#|Player|Name|Set|Total|Match|Point|Vote|No\.|Pos|Pts', line, re.IGNORECASE):
                    continue

                # More flexible player line matching
                # Look for: number at start, then text, then numbers
                # Allow more varied formatting
                match = re.match(r'^(\d+)\s+(.{2,40}?)\s+([\d\s]+)$', line)

                if match:
                    try:
                        p_num = match.group(1).strip()
                        p_name = match.group(2).strip()
                        stats_str = match.group(3).strip()

                        # Extract all numeric parts
                        parts = re.findall(r'\d+', stats_str)

                        # Skip if too few numbers
                        if len(parts) < 1:
                            continue

                        # Skip known non-player entries
                        if re.search(r'^\s*(TOTAL|TEAM|COACH|REFEREE|SUB|BENCH)\s*$', p_name, re.IGNORECASE):
                            continue

                        # Skip if name looks like header
                        if len(p_name) < 2 or p_name.upper() in ['SET', 'VOTE', 'POINT']:
                            continue

                        logger.debug(f"Matched player: #{p_num} - {p_name} with {len(parts)} stat numbers")
                        print(f"[DEBUG] Matched: #{p_num} {p_name}, stats: {parts}")

                        # Initialize stats with defaults
                        stats = {
                            'player_name': p_name,
                            'player_number': p_num,
                            'team': current_team,
                            'pts': '0',
                            'serve_total': '0',
                            'serve_err': '0',
                            'serve_ace': '0',
                            'reception_total': '0',
                            'reception_err': '0',
                            'reception_exc': '0',
                            'attack_total': '0',
                            'attack_err': '0',
                            'attack_att': '0',
                            'attack_pts': '0',
                            'block_pts': '0',
                        }

                        # Map available statistics based on position in parts
                        # Try to map stats intelligently based on number count
                        if len(parts) >= 1:
                            stats['pts'] = parts[0]

                        # For remaining stats, map sequentially
                        if len(parts) >= 2:
                            stats['serve_total'] = parts[1]
                        if len(parts) >= 3:
                            stats['serve_err'] = parts[2]
                        if len(parts) >= 4:
                            stats['serve_ace'] = parts[3]
                        if len(parts) >= 5:
                            stats['reception_total'] = parts[4]
                        if len(parts) >= 6:
                            stats['reception_err'] = parts[5]
                        if len(parts) >= 7:
                            stats['reception_exc'] = parts[6]
                        if len(parts) >= 8:
                            stats['attack_total'] = parts[7]
                        if len(parts) >= 9:
                            stats['attack_err'] = parts[8]
                        if len(parts) >= 10:
                            stats['attack_att'] = parts[9]
                        if len(parts) >= 11:
                            stats['attack_pts'] = parts[10]
                        if len(parts) >= 12:
                            stats['block_pts'] = parts[11]

                        all_stats.append(stats)
                        found_any_player = True
                        print(f"[DEBUG] Added player to stats list. Total: {len(all_stats)}")

                    except Exception as e:
                        logger.error(f"Error parsing player line '{line}': {e}")
                        print(f"[DEBUG] Error on line: {line} - {e}")
                        continue

        except Exception as e:
            logger.error(f"Error processing page {page_idx + 1}: {e}")
            print(f"[DEBUG] Error processing page {page_idx + 1}: {e}")
            continue

    logger.info(f"Successfully extracted {len(all_stats)} player records from PDF")
    print(f"[DEBUG] Final result: {len(all_stats)} players extracted")
    if not found_any_player:
        print("[DEBUG] WARNING: No players were found in the PDF!")
    return all_stats
