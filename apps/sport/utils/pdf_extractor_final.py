"""
FINAL Enhanced PDF Extractor for Volleyball Match Reports
Handles multi-line player data format from DataProject PDFs
Works without Poppler - uses PyMuPDF only
"""
import fitz  # PyMuPDF
import re
import json
import os
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class VolleyballPDFExtractor:
    """
    Enhanced extractor for Volleyball statistics PDFs.
    Handles DataProject format where player data spans multiple lines.
    """

    def __init__(self):
        self.extraction_log = []
        self.debug_mode = False

    def log(self, message: str):
        """Add message to extraction log"""
        self.extraction_log.append(message)

    def extract(self, pdf_path: str) -> Dict:
        """
        Extract player statistics from PDF.
        Returns structured data with teams and players.
        """
        self.extraction_log = []
        self.log(f"Starting extraction from: {os.path.basename(pdf_path)}")

        if not os.path.exists(pdf_path):
            return {"error": "File not found", "log": self.extraction_log}

        try:
            doc = fitz.open(pdf_path)
            self.log(f"Opened PDF: {len(doc)} pages")

            # Extract text from all pages
            all_lines = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                lines = text.split('\n')
                all_lines.extend([line.strip() for line in lines])

            doc.close()
            self.log(f"Extracted {len(all_lines)} lines of text")

            # Parse player data
            result = self.parse_player_data(all_lines)
            result["file"] = os.path.basename(pdf_path)
            result["log"] = self.extraction_log

            return result

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            return {"error": str(e), "log": self.extraction_log}

    def parse_player_data(self, lines: List[str]) -> Dict:
        """Parse lines to extract teams and player statistics"""
        teams = []
        current_team = None
        i = 0

        # Track which teams we've found (avoid duplicates)
        teams_found = set()

        # Keywords to skip - these are NOT players
        skip_names = [
            'set 1', 'set 2', 'set 3', 'set 4', 'set 5',
            'tot', 'total', 'match', 'date', 'time', 'city',
            'head coach', 'assistant', 'coach', 'referee',
            'vote', 'points won', 'each', 'recept', 'serve',
            'al sahel 25-26', 'kuwait sc 25-26', 'players total',
            'spectators', 'receipts', 'hall', 'duration'
        ]

        while i < len(lines):
            line = lines[i].strip()

            # Detect team names (avoid duplicates)
            if re.search(r'Kuwait\s*SC\s*25-26', line, re.IGNORECASE) and 'Set' not in line:
                if 'Kuwait SC' not in teams_found:
                    current_team = {"name": "Kuwait SC", "players": []}
                    teams.append(current_team)
                    teams_found.add('Kuwait SC')
                    self.log(f"Found team: Kuwait SC at line {i}")
                else:
                    # Already have this team, use existing
                    current_team = next(t for t in teams if t["name"] == "Kuwait SC")
                i += 1
                continue
            elif re.search(r'Al\s*Sahel\s*25-26', line, re.IGNORECASE) and 'Set' not in line:
                if 'Al Sahel' not in teams_found:
                    current_team = {"name": "Al Sahel", "players": []}
                    teams.append(current_team)
                    teams_found.add('Al Sahel')
                    self.log(f"Found team: Al Sahel at line {i}")
                else:
                    # Already have this team, use existing
                    current_team = next(t for t in teams if t["name"] == "Al Sahel")
                i += 1
                continue

            # Look for player number (single/double digit line followed by name)
            if re.match(r'^\d{1,2}$', line) and i + 1 < len(lines):
                next_line = lines[i + 1].strip()

                # Skip if it's a skip keyword
                if any(skip in next_line.lower() for skip in skip_names):
                    i += 1
                    continue

                # Check if next line looks like a name
                if re.search(r'[A-Z][a-z]+', next_line) and not re.match(r'^\d+$', next_line):
                    player_num = line
                    player_name = next_line

                    # Check for Libero marker
                    is_libero = False
                    if player_name.startswith('L '):
                        is_libero = True
                        player_name = player_name[2:].strip()

                    # Also check if name has L embedded (e.g., "18 L Alanzi")
                    if re.match(r'^\d+\s+L\s+', player_name):
                        is_libero = True
                        player_name = re.sub(r'^\d+\s+L\s+', '', player_name)

                    # Skip if player name contains skip keywords
                    if any(skip in player_name.lower() for skip in skip_names):
                        i += 1
                        continue

                    # Collect stats from following lines
                    stats_lines = []
                    j = i + 2
                    while j < len(lines) and j < i + 40:
                        stat_line = lines[j].strip()
                        # Stop if we hit another player number or team name
                        if re.match(r'^\d{1,2}$', stat_line) and j + 1 < len(lines) and re.search(r'[A-Z][a-z]+', lines[j+1]):
                            break
                        if re.search(r'Kuwait.*SC|Al.*Sahel', stat_line, re.IGNORECASE):
                            break
                        if stat_line and stat_line not in ['.', '..']:
                            stats_lines.append(stat_line)
                        j += 1

                    # Parse statistics
                    player_stats = self.parse_player_stats(player_num, player_name, stats_lines, is_libero)

                    if current_team and player_stats:
                        current_team["players"].append(player_stats)
                        self.log(f"Player #{player_num} {player_name}: Pts={player_stats['stats']['pts']}")

                    i = j
                    continue

            i += 1

        return {
            "teams": teams,
            "total_players": sum(len(team["players"]) for team in teams),
            "extraction_status": "success" if teams else "no_data"
        }

    def parse_player_stats(self, number: str, name: str, stats_lines: List[str], is_libero: bool) -> Dict:
        """
        Parse player statistics from collected lines using position-based mapping.
        We collect all numeric tokens (including ones in lines with %), then map by index:
        After skipping up to 3 set indicators and one vote (decimal), indices are:
          0: Points (Tot)
          1: BP (skip)
          2: W-L (skip)
          3: Serve Tot
          4: Serve Err
          5: Serve Pts
          6: Reception Tot
          7: Reception Err
          8: Reception Pos% (skip)
          9: Reception Exc% (skip)
          10: Attack Tot
          11: Attack Err
          12: Attack Blo (skip)
          13: Attack Pts
          14: Attack Pts% (skip)
          15: BK Pts
        """
        # Collect tokens: numbers (allow +/-, decimals, %). We'll strip signs later.
        tokens: List[str] = []
        for ln in stats_lines:
            tokens += re.findall(r"[+\-]?\d+(?:\.\d+)?%?", ln)

        # Remove the first decimal (vote) and any remaining decimals (we don't use them as counts)
        cleaned_nums: List[int] = []
        vote_skipped = False
        for tok in tokens:
            if "." in tok:
                # treat as vote/decimal -> skip; mark first decimal as vote
                if not vote_skipped:
                    vote_skipped = True
                continue
            # strip percentage and signs
            tok = tok.replace('%', '').replace('+', '').replace('-', '')
            if tok == '':
                continue
            try:
                cleaned_nums.append(int(tok))
            except ValueError:
                continue

        # Skip up to 3 set-indicator numbers (<=6)
        base = 0
        while base < len(cleaned_nums) and cleaned_nums[base] <= 6 and base < 3:
            base += 1

        # Prepare stats with defaults
        stats = {
            'pts': 0,
            'serve_total': 0,
            'serve_err': 0,
            'serve_ace': 0,
            'reception_total': 0,
            'reception_err': 0,
            'reception_exc': 0,
            'attack_total': 0,
            'attack_err': 0,
            'attack_pts': 0,
            'block_pts': 0,
        }

        # Helper to safely get by index
        def get(i: int) -> int:
            return cleaned_nums[i] if i < len(cleaned_nums) else 0

        # Map by position, guarding bounds
        stats['pts'] = get(base + 0)
        # base+1 BP skip
        # base+2 W-L skip
        stats['serve_total']   = get(base + 3)
        stats['serve_err']     = get(base + 4)
        stats['serve_ace']     = get(base + 5)
        stats['reception_total']= get(base + 6)
        stats['reception_err']  = get(base + 7)
        # base+8, base+9 are percentages -> skip
        stats['attack_total']  = get(base + 10)
        stats['attack_err']    = get(base + 11)
        # base+12 blocked attempts -> skip
        stats['attack_pts']    = get(base + 13)
        # base+14 percentage -> skip
        stats['block_pts']     = get(base + 15)

        return {
            'player_number': number,
            'player_name': name,
            'is_libero': is_libero,
            'stats': stats,
            'raw_stats_lines': stats_lines[:12],
            'parsed_numbers': cleaned_nums[:20]
        }

    def save_json(self, data: Dict, output_path: str) -> bool:
        """Save extracted data to JSON file"""
        try:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.log(f"JSON saved to: {output_path}")
            return True
        except Exception as e:
            self.log(f"ERROR saving JSON: {str(e)}")
            return False


# Compatibility function
def extract_pdf_to_json(pdf_path: str, output_json_path: Optional[str] = None) -> Dict:
    """Extract PDF and optionally save to JSON"""
    extractor = VolleyballPDFExtractor()
    data = extractor.extract(pdf_path)

    if output_json_path and 'error' not in data:
        extractor.save_json(data, output_json_path)

    return data


# Legacy compatibility
def parse_match_report(pdf_path: str) -> List[Dict]:
    """
    Legacy function for backward compatibility.
    Returns list of player dictionaries.
    """
    extractor = VolleyballPDFExtractor()
    data = extractor.extract(pdf_path)

    if 'error' in data:
        logger.error(f"Extraction error: {data['error']}")
        return []

    # Convert to old format
    all_players = []
    for team in data.get('teams', []):
        team_name = team.get('name', '')
        for player in team.get('players', []):
            stats = player.get('stats', {})
            player_dict = {
                'player_name': player.get('player_name', ''),
                'player_number': player.get('player_number', ''),
                'team': team_name,
                'pts': str(stats.get('pts', 0)),
                'serve_total': str(stats.get('serve_total', 0)),
                'serve_err': str(stats.get('serve_err', 0)),
                'serve_ace': str(stats.get('serve_ace', 0)),
                'reception_total': str(stats.get('reception_total', 0)),
                'reception_err': str(stats.get('reception_err', 0)),
                'reception_exc': str(stats.get('reception_exc', 0)),
                'attack_total': str(stats.get('attack_total', 0)),
                'attack_err': str(stats.get('attack_err', 0)),
                'attack_att': str(stats.get('attack_pts', 0)),  # Map attack_pts to attack_att
                'attack_pts': str(stats.get('attack_pts', 0)),
                'block_pts': str(stats.get('block_pts', 0)),
            }
            all_players.append(player_dict)

    return all_players
