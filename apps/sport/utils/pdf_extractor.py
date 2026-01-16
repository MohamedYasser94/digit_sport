"""
Advanced PDF to JSON Extractor for Volleyball Match Reports
Handles DataProject format PDFs with OCR and data validation
"""
import pytesseract
from pdf2image import convert_from_path
import re
import json
import os
from pathlib import Path


class VolleyballPDFExtractor:
    """
    Universal extractor for Volleyball Match Reports (DataProject format).
    Converts PDF to structured JSON with validation.
    """

    def __init__(self, dpi=400):
        self.dpi = dpi
        self.extraction_log = []
        self.team_indicators = ["SC", "Club", "Team", "Sahel", "Kuwait", "Al", "National", "League"]
        self.skip_keywords = ['point', 'total', 'set', 'match', 'coach', 'players', 'duration', 'partial', 'score', 'period', 'break']

    def log(self, message):
        """Add message to extraction log for debugging"""
        self.extraction_log.append(message)

    def clean_value(self, val):
        """Clean OCR noise and convert to integer"""
        if not val or val == '.':
            return 0
        try:
            # Remove common OCR misinterpretations
            cleaned = str(val).replace('%', '').replace('(', '').replace(')', '').replace('.', '0').strip()
            # Extract numeric value
            match = re.search(r'[+-]?\d+', cleaned)
            return int(match.group()) if match else 0
        except:
            return 0

    def parse_line_as_player(self, line):
        """
        Attempt to parse a line as a player record.
        Returns dict with player data or None if not a valid player line.
        """
        # Pattern: Number [L] Name [Stats...]
        player_pattern = re.compile(r'^(\d+)\s+(?:L\s+)?([A-Za-z\s\.\-\']+)\s+(.*)')

        match = player_pattern.match(line)
        if not match:
            return None

        number = match.group(1)
        name = match.group(2).strip()
        remaining = match.group(3)

        # Validate player name
        if name.lower() in self.skip_keywords or len(name) < 2:
            return None

        # Extract numeric values
        parts = []
        for part in remaining.split():
            if part == '.':
                parts.append(0)
            else:
                val = self.clean_value(part)
                if part != '' and val >= 0:
                    parts.append(val)

        if len(parts) < 5:
            return None

        return {
            'number': number,
            'name': name,
            'raw_stats': parts
        }

    def map_stats(self, raw_stats):
        """
        Map raw stats array to named fields.
        DataProject standard layout (20+ fields)
        """
        def get_stat(idx, default=0):
            return raw_stats[idx] if idx < len(raw_stats) else default

        return {
            'pts': get_stat(4),  # Total Points
            'bp': get_stat(5),   # Ball Points
            'serve_total': get_stat(7),
            'serve_err': get_stat(8),
            'serve_ace': get_stat(9),
            'reception_total': get_stat(10),
            'reception_err': get_stat(11),
            'reception_pos_pct': get_stat(12),
            'reception_exc': get_stat(13),
            'attack_total': get_stat(14),
            'attack_err': get_stat(15),
            'attack_blo': get_stat(16),
            'attack_pts': get_stat(17),
            'attack_pts_pct': get_stat(18),
            'block_pts': get_stat(19)
        }

    def extract(self, pdf_path):
        """
        Extract match data from PDF and return structured JSON.
        """
        self.extraction_log = []
        self.log(f"Starting extraction from: {pdf_path}")

        # Validate file exists
        if not os.path.exists(pdf_path):
            self.log(f"ERROR: File not found: {pdf_path}")
            return {"error": f"File not found", "log": self.extraction_log}

        # Convert PDF to images
        try:
            images = convert_from_path(pdf_path, dpi=self.dpi)
            self.log(f"Successfully converted PDF to {len(images)} image(s)")
        except Exception as e:
            error_msg = f"PDF Conversion Error: {str(e)}"
            self.log(f"ERROR: {error_msg}")
            return {"error": error_msg, "log": self.extraction_log}

        # Initialize data structure
        data = {
            "file": os.path.basename(pdf_path),
            "teams": [],
            "total_players": 0,
            "extraction_status": "processing"
        }

        current_team = None
        player_pattern = re.compile(r'^(\d+)\s+(?:L\s+)?([A-Za-z\s\.\-\']+)\s+(.*)')

        # Process each page
        for page_num, image in enumerate(images, 1):
            self.log(f"\n--- Processing Page {page_num} ---")

            try:
                # Extract text using OCR
                custom_config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(image, config=custom_config)
                self.log(f"OCR extracted {len(text)} characters from page {page_num}")

                lines = text.split('\n')

                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if not line or len(line) < 3:
                        continue

                    # Detect team headers
                    if not player_pattern.match(line) and any(kw in line for kw in self.team_indicators):
                        # Extract team name
                        name_match = re.match(r'^([A-Za-z\s]+)', line)
                        if name_match:
                            team_name = name_match.group(1).strip()
                            if len(team_name) > 3 and team_name.lower() not in self.skip_keywords:
                                # Check for duplicates
                                if not any(t['name'] == team_name for t in data['teams']):
                                    current_team = {
                                        "name": team_name,
                                        "players": [],
                                        "page": page_num
                                    }
                                    data['teams'].append(current_team)
                                    self.log(f"Detected team: {team_name}")
                        continue

                    # Parse player records
                    player_data = self.parse_line_as_player(line)
                    if player_data and current_team:
                        # Map stats to named fields
                        stats = self.map_stats(player_data['raw_stats'])

                        player_record = {
                            "number": player_data['number'],
                            "name": player_data['name'],
                            "stats": stats,
                            "page": page_num
                        }
                        current_team['players'].append(player_record)
                        data['total_players'] += 1
                        self.log(f"Extracted player: #{player_data['number']} {player_data['name']} (pts={stats['pts']})")

            except Exception as e:
                self.log(f"ERROR processing page {page_num}: {str(e)}")
                continue

        # Final validation
        data['extraction_status'] = 'success' if data['teams'] else 'no_data'
        self.log(f"\n=== EXTRACTION COMPLETE ===")
        self.log(f"Teams found: {len(data['teams'])}")
        self.log(f"Total players: {data['total_players']}")
        data['log'] = self.extraction_log

        return data

    def save_json(self, data, output_path):
        """Save extracted data to JSON file"""
        try:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            self.log(f"JSON saved to: {output_path}")
            return True
        except Exception as e:
            self.log(f"ERROR saving JSON: {str(e)}")
            return False


def extract_pdf_to_json(pdf_path, output_json_path=None, dpi=400):
    """
    Convenience function to extract PDF and optionally save to JSON.

    Args:
        pdf_path: Path to PDF file
        output_json_path: Optional path to save JSON output
        dpi: DPI for PDF conversion (higher = better quality, slower)

    Returns:
        dict with extracted data and log
    """
    extractor = VolleyballPDFExtractor(dpi=dpi)
    data = extractor.extract(pdf_path)

    if output_json_path and 'error' not in data:
        extractor.save_json(data, output_json_path)

    return data
