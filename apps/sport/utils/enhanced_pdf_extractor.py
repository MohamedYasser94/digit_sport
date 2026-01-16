"""
Enhanced PDF Extractor for Volleyball Match Reports
Uses PyMuPDF (fitz) for better text extraction without Poppler dependency
Improved pattern matching and data validation for accurate statistics extraction
"""
import fitz  # PyMuPDF
import re
import json
import os
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EnhancedVolleyballPDFExtractor:
    """
    Advanced extractor for Volleyball Match Reports with improved accuracy.
    Works with DataProject format PDFs and other standard volleyball statistics formats.
    """

    def __init__(self):
        self.extraction_log = []
        self.debug_mode = False  # Turn off to avoid console encoding issues

        # Common team name patterns in PDFs
        self.team_patterns = [
            r'(Kuwait\s+SC|Kuwait\s+Sport\s+Club)',
            r'(Al\s+Sahel|Al-Sahel)',
            r'(Al\s+Arabi|Al-Arabi)',
            r'(Qadisiya|Al\s+Qadisiya)',
            r'(Kazma|Al\s+Kazma)',
            r'(Salmiya|Al\s+Salmiya)',
            r'(Fahaheel|Al\s+Fahaheel)',
        ]

        # Keywords to skip (not player names)
        self.skip_keywords = [
            'total', 'team', 'set', 'match', 'coach', 'referee', 'partial',
            'score', 'point', 'serve', 'reception', 'attack', 'block',
            'players', 'bench', 'substitutes', 'duration', 'period'
        ]

    def log(self, message: str, level: str = "INFO"):
        """Add message to extraction log"""
        log_entry = f"[{level}] {message}"
        self.extraction_log.append(log_entry)
        if self.debug_mode:
            print(log_entry)

    def extract_text_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract and clean text lines from PDF"""
        if not os.path.exists(pdf_path):
            self.log(f"File not found: {pdf_path}", "ERROR")
            return []

        try:
            doc = fitz.open(pdf_path)
            self.log(f"Opened PDF with 1 pages")

            all_text = ""
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")

                # Smart space removal: only remove spaces between letters, keep spaces around numbers
                # This prevents "4 4 4" from becoming "444"
                # Pattern: letter-space-letter becomes letter-letter
                fixed_text = re.sub(r'([a-zA-Z])\s([a-zA-Z])', r'\1\2', text)

                all_text += fixed_text + "\n"
                self.log(f"Page {page_num + 1}: Extracted text")

            doc.close()

            # Split into lines and clean
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            return lines

        except Exception as e:
            self.log(f"Error extracting text from PDF: {str(e)}", "ERROR")
            return []

    def clean_number(self, value: str) -> int:
        """Clean and convert string to integer, handling OCR errors"""
        if not value or value in ['.', '-', '—']:
            return 0

        try:
            # Remove common OCR artifacts
            cleaned = str(value).strip()
            cleaned = cleaned.replace('O', '0').replace('o', '0')  # OCR confusion
            cleaned = cleaned.replace('l', '1').replace('I', '1')  # OCR confusion
            cleaned = re.sub(r'[^\d+-]', '', cleaned)  # Keep only digits and signs

            if not cleaned or cleaned in ['+', '-']:
                return 0

            return int(cleaned)
        except (ValueError, TypeError):
            return 0

    def detect_team_name(self, line: str) -> Optional[str]:
        """Detect team name from a line of text"""
        line_clean = line.strip()

        # Try each team pattern (with space-removed text too)
        for pattern in self.team_patterns:
            match = re.search(pattern, line_clean, re.IGNORECASE)
            if match:
                team_name = match.group(1).strip()
                self.log(f"Detected team: {team_name}")
                return team_name

        # Also try to match common patterns without spaces
        if re.search(r'Kuwait.*?SC', line_clean, re.IGNORECASE):
            return "Kuwait SC"
        if re.search(r'Al.*?Sahel', line_clean, re.IGNORECASE):
            return "Al Sahel"
        if re.search(r'Al.*?Arabi', line_clean, re.IGNORECASE):
            return "Al Arabi"
        if re.search(r'Qadisiya', line_clean, re.IGNORECASE):
            return "Al Qadisiya"

        return None

    def is_player_line(self, line: str) -> bool:
        """Check if a line contains player data"""
        line = line.strip()

        # Must start with a number (jersey number)
        if not re.match(r'^\d+', line):
            return False

        # Must have a name (letters)
        if not re.search(r'[A-Za-z]{2,}', line):
            return False

        # Must have some statistics (numbers)
        numbers = re.findall(r'\d+', line)
        if len(numbers) < 3:  # At least number, and a few stats
            return False

        # Skip lines with skip keywords
        line_lower = line.lower()
        for keyword in self.skip_keywords:
            if keyword in line_lower:
                return False

        return True

    def parse_player_line(self, line: str, next_lines: List[str], current_team: Optional[str]) -> Tuple[Optional[Dict], int]:
        """
        Parse a player and their stats which may span multiple lines.
        Returns (player_data, lines_consumed)

        Expected format:
        Line 1: "4HoagNicholas444 6.3"
        Line 2: "16"
        Line 3: "4+10"
        ...etc
        """
        line = line.strip()

        # Pattern: number + optional L + name + some initial stats
        match = re.match(r'^(\d{1,2})(L)?([A-Za-z\-\']+(?:[A-Z][a-z]+)*)(.*)', line)

        if not match:
            return None, 0

        player_number = match.group(1)
        is_libero = match.group(2) is not None
        player_name_raw = match.group(3)
        rest_of_line = match.group(4)

        # Fix name: split CamelCase (e.g., "HoagNicholas" -> "Hoag Nicholas")
        player_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', player_name_raw)

        # Validate name
        if len(player_name) < 3:
            return None, 0
        if any(keyword in player_name.lower() for keyword in self.skip_keywords):
            return None, 0

        # Collect all stats from this line and following lines
        all_numbers = []

        # Extract from current line
        numbers_in_line = re.findall(r'[+-]?\d+(?:\.\d+)?', rest_of_line)
        all_numbers.extend(numbers_in_line)

        # Collect numbers from next lines until we hit another player or team
        lines_consumed = 0
        for next_line in next_lines:
            next_line = next_line.strip()

            # Stop if we hit another player line
            if re.match(r'^\d{1,2}[LA-Z]', next_line):
                break

            # Stop if we hit a team name
            if self.detect_team_name(next_line):
                break

            # Stop if line looks like a header
            if any(kw in next_line.lower() for kw in ['set', 'vote', 'points', 'serve', 'attack', 'reception']):
                break

            # Extract numbers from this line
            nums = re.findall(r'[+-]?\d+(?:\.\d+)?', next_line)
            if nums:
                all_numbers.extend(nums)
                lines_consumed += 1
            else:
                break

        # Skip votes and other pre-stat numbers (typically 3-4 numbers before actual stats)
        # Looking at the PDF: Vote, BP, W-L are before serve stats
        # After those, we have: Serve(Tot, Err, Pts), Reception(Tot, Err, Pos%, Exc), Attack(Tot, Err, Blo, Pts, Pts%), Block(Pts)

        # Convert to integers
        numbers = [self.clean_number(n) for n in all_numbers]

        self.log(f"Player #{player_number} {player_name}: Found {len(numbers)} numbers", "DEBUG")

        # Map stats - adjust indices based on actual data structure
        stats = {
            'player_number': player_number,
            'player_name': player_name,
            'team': current_team or 'Unknown',
            'is_libero': is_libero,
        }

        # DataProject typical format after name:
        # Set indicators (1-3 sets played), Vote, BP, W-L, then actual stats
        stat_fields = {}

        # Try to find the "Total Points" - usually one of the first larger numbers
        # Skip very small numbers (likely votes < 10)
        idx = 0

        # Skip set indicators and vote (first few small numbers or decimals)
        while idx < len(numbers) and (numbers[idx] < 10 or '.' in str(all_numbers[idx])):
            idx += 1

        # Now we should be at points or serve stats
        stat_fields['pts'] = numbers[idx] if idx < len(numbers) else 0
        idx += 1

        # Skip BP and W-L (next 1-2 numbers)
        idx += 2

        # Serve stats (Total, Err, Ace)
        stat_fields['serve_total'] = numbers[idx] if idx < len(numbers) else 0
        idx += 1
        stat_fields['serve_err'] = numbers[idx] if idx < len(numbers) else 0
        idx += 1
        stat_fields['serve_ace'] = numbers[idx] if idx < len(numbers) else 0
        idx += 1

        # Reception stats (Total, Err, then percentages we skip, then Exc)
        stat_fields['reception_total'] = numbers[idx] if idx < len(numbers) else 0
        idx += 1
        stat_fields['reception_err'] = numbers[idx] if idx < len(numbers) else 0
        idx += 1
        # Skip percentages (usually 2)
        idx += 2
        stat_fields['reception_exc'] = numbers[idx] if idx < len(numbers) else 0
        idx += 1

        # Attack stats (Total, Err, Blo, Pts, skip %, then maybe more)
        stat_fields['attack_total'] = numbers[idx] if idx < len(numbers) else 0
        idx += 1
        stat_fields['attack_err'] = numbers[idx] if idx < len(numbers) else 0
        idx += 1
        stat_fields['attack_blo'] = numbers[idx] if idx < len(numbers) else 0
        idx += 1
        stat_fields['attack_pts'] = numbers[idx] if idx < len(numbers) else 0
        idx += 1
        # Skip attack percentage
        idx += 1

        # Block points
        stat_fields['block_pts'] = numbers[idx] if idx < len(numbers) else 0

        stats['stats'] = stat_fields
        stats['raw_numbers'] = numbers[:15]  # Keep first 15 for debugging

        return stats, lines_consumed

    def extract(self, pdf_path: str) -> Dict:
        """
        Main extraction method.
        Returns structured data with teams and players.
        """
        self.extraction_log = []
        self.log(f"Starting enhanced extraction from: {pdf_path}")

        # Extract text lines from PDF
        lines = self.extract_text_from_pdf(pdf_path)

        if not lines:
            return {
                "error": "Could not extract text from PDF",
                "log": self.extraction_log
            }

        # Initialize result structure
        result = {
            "file": os.path.basename(pdf_path),
            "teams": [],
            "total_players": 0,
            "extraction_status": "processing"
        }

        current_team = None
        current_team_data = None

        # Process lines
        i = 0
        while i < len(lines):
            line = lines[i]

            # Check for team name
            team_name = self.detect_team_name(line)
            if team_name and not any(t['name'] == team_name for t in result['teams']):
                current_team = team_name
                current_team_data = {
                    "name": team_name,
                    "players": [],
                    "page": 1
                }
                result["teams"].append(current_team_data)
                self.log(f"Found team: {team_name}")
                i += 1
                continue

            # Check for player line
            if self.is_player_line(line):
                # Get remaining lines for multi-line parsing
                remaining_lines = lines[i+1:min(i+20, len(lines))]
                player_data, lines_consumed = self.parse_player_line(line, remaining_lines, current_team)

                if player_data and current_team_data:
                    current_team_data["players"].append(player_data)
                    result["total_players"] += 1
                    self.log(
                        f"[+] Player #{player_data['player_number']} {player_data['player_name']} "
                        f"- Pts: {player_data['stats']['pts']}"
                    )
                    # Skip the lines we consumed
                    i += lines_consumed + 1
                else:
                    i += 1
            else:
                i += 1

        # Final status
        result["extraction_status"] = "success" if result["teams"] and result["total_players"] > 0 else "no_data"
        result["log"] = self.extraction_log

        self.log(f"\n=== EXTRACTION COMPLETE ===")
        self.log(f"Teams found: {len(result['teams'])}")
        self.log(f"Total players: {result['total_players']}")

        return result

    def save_json(self, data: Dict, output_path: str) -> bool:
        """Save extracted data to JSON file"""
        try:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.log(f"JSON saved to: {output_path}")
            return True
        except Exception as e:
            self.log(f"ERROR saving JSON: {str(e)}", "ERROR")
            return False


def extract_pdf_to_json(pdf_path: str, output_json_path: Optional[str] = None) -> Dict:
    """
    Convenience function to extract PDF and optionally save to JSON.

    Args:
        pdf_path: Path to PDF file
        output_json_path: Optional path to save JSON output

    Returns:
        dict with extracted data and log
    """
    extractor = EnhancedVolleyballPDFExtractor()
    data = extractor.extract(pdf_path)

    if output_json_path and 'error' not in data:
        extractor.save_json(data, output_json_path)

    return data


# Backward compatibility - map to old parser function
def parse_match_report(pdf_path: str) -> List[Dict]:
    """
    Legacy function signature for compatibility.
    Returns list of player stat dictionaries.
    """
    extractor = EnhancedVolleyballPDFExtractor()
    data = extractor.extract(pdf_path)

    if 'error' in data:
        logger.error(f"Extraction error: {data['error']}")
        return []

    # Convert to old format
    all_players = []
    for team in data.get('teams', []):
        for player in team.get('players', []):
            stats = player.get('stats', {})

            # Map to old format
            player_dict = {
                'player_name': player.get('player_name', ''),
                'player_number': player.get('player_number', ''),
                'team': player.get('team', ''),
                'pts': str(stats.get('pts', 0)),
                'serve_total': str(stats.get('serve_total', 0)),
                'serve_err': str(stats.get('serve_err', 0)),
                'serve_ace': str(stats.get('serve_ace', 0)),
                'reception_total': str(stats.get('reception_total', 0)),
                'reception_err': str(stats.get('reception_err', 0)),
                'reception_exc': str(stats.get('reception_exc', 0)),
                'attack_total': str(stats.get('attack_total', 0)),
                'attack_err': str(stats.get('attack_err', 0)),
                'attack_att': str(stats.get('attack_blo', 0)),
                'attack_pts': str(stats.get('attack_pts', 0)),
                'block_pts': str(stats.get('block_pts', 0)),
            }
            all_players.append(player_dict)

    return all_players
