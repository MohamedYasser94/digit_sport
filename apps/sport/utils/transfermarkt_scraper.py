import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urljoin, urlparse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TransferMarktScraper:
    """
    Complete Transfer Market scraper for player data
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    def extract_player_id(self, url):
        """Extract player ID from Transfer Market URL"""
        match = re.search(r'/spieler/(\d+)', url)
        return match.group(1) if match else None
    
    def parse_market_value(self, value_text):
        """Parse market value from text like €50.00m to numeric value"""
        if not value_text:
            return None
            
        # Remove currency symbols and spaces
        clean_value = re.sub(r'[€$£¥]', '', value_text.strip())
        
        # Handle different formats
        if 'm' in clean_value.lower():
            # Million: €50.00m -> 50000000
            number = float(re.findall(r'[\d.]+', clean_value)[0])
            return int(number * 1000000)
        elif 'k' in clean_value.lower():
            # Thousand: €500k -> 500000
            number = float(re.findall(r'[\d.]+', clean_value)[0])
            return int(number * 1000)
        elif clean_value.replace('.', '').replace(',', '').isdigit():
            # Direct number
            return int(float(clean_value.replace(',', '')))
        
        return None
    
    def scrape_player_profile(self, player_url, options=None):
        """
        Scrape complete player profile from Transfer Market
        """
        if options is None:
            options = {
                'includeMarketValue': True,
                'includeContracts': True,
                'includeTransferHistory': False
            }
        
        try:
            response = self.session.get(player_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            player_data = {
                'url': player_url,
                'transfermarkt_id': self.extract_player_id(player_url),
                'scraped_at': datetime.now().isoformat(),
            }
            
            # Extract basic info
            self._extract_basic_info(soup, player_data)
            
            # Extract market value if requested
            if options.get('includeMarketValue', True):
                self._extract_market_value(soup, player_data)
            
            # Extract contract info if requested
            if options.get('includeContracts', True):
                self._extract_contract_info(soup, player_data)
            
            # Extract transfer history if requested
            if options.get('includeTransferHistory', False):
                self._extract_transfer_history(soup, player_data, player_url)
            
            return player_data
            
        except Exception as e:
            logger.error(f"Error scraping player profile {player_url}: {str(e)}")
            return None
    
    def _extract_basic_info(self, soup, player_data):
        """Extract basic player information"""
        try:
            # Player name
            name_element = soup.find('h1', class_='data-header__headline-wrapper')
            if name_element:
                player_data['name'] = name_element.get_text(strip=True)
            
            # Player image
            img_element = soup.find('img', class_='data-header__profile-image')
            if img_element:
                player_data['image_url'] = img_element.get('src', '')
            
            # Extract data from info table
            info_table = soup.find('table', class_='auflistung')
            if info_table:
                rows = info_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        if 'date of birth' in label or 'age' in label:
                            # Extract age and birth date
                            age_match = re.search(r'\((\d+)\)', value)
                            if age_match:
                                player_data['age'] = int(age_match.group(1))
                            
                            date_match = re.search(r'(\w+\s+\d+,\s+\d+)', value)
                            if date_match:
                                player_data['date_of_birth'] = date_match.group(1)
                        
                        elif 'place of birth' in label:
                            player_data['place_of_birth'] = value
                        
                        elif 'citizenship' in label:
                            player_data['nationality'] = value
                        
                        elif 'height' in label:
                            height_match = re.search(r'(\d+,\d+)', value)
                            if height_match:
                                player_data['height'] = height_match.group(1).replace(',', '.')
                        
                        elif 'position' in label:
                            player_data['position'] = value
                        
                        elif 'foot' in label:
                            player_data['preferred_foot'] = value
                        
                        elif 'player agent' in label:
                            player_data['agent'] = value
                        
                        elif 'current club' in label:
                            player_data['current_club'] = value
        
        except Exception as e:
            logger.error(f"Error extracting basic info: {str(e)}")
    
    def _extract_market_value(self, soup, player_data):
        """Extract market value information"""
        try:
            # Current market value
            mv_element = soup.find('div', class_='marktwert')
            if not mv_element:
                mv_element = soup.find('a', class_='marktwert')
            
            if mv_element:
                mv_text = mv_element.get_text(strip=True)
                player_data['current_market_value'] = mv_text
                player_data['market_value_numeric'] = self.parse_market_value(mv_text)
            
            # Market value development (if available)
            chart_data = soup.find('div', {'id': 'marktwertentwicklung'})
            if chart_data:
                # This would require more complex parsing of chart data
                player_data['has_market_value_chart'] = True
        
        except Exception as e:
            logger.error(f"Error extracting market value: {str(e)}")
    
    def _extract_contract_info(self, soup, player_data):
        """Extract contract and club information"""
        try:
            # Find contract table or info
            contract_info = {}
            
            # Look for contract information in various places
            info_tables = soup.find_all('table', class_='auflistung')
            
            for table in info_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)
                        
                        if 'contract' in label:
                            contract_info['contract_expires'] = value
                        elif 'joined' in label:
                            contract_info['joined_on'] = value
                        elif 'contract option' in label:
                            contract_info['contract_option'] = value
            
            if contract_info:
                player_data['contract_info'] = contract_info
        
        except Exception as e:
            logger.error(f"Error extracting contract info: {str(e)}")
    
    def _extract_transfer_history(self, soup, player_data, base_url):
        """Extract transfer history"""
        try:
            # Look for transfer history section
            transfer_history = []
            
            # Transfer Market usually has transfer history in a specific section
            transfer_table = soup.find('div', class_='transferhistorie')
            if transfer_table:
                rows = transfer_table.find_all('tr')[1:]  # Skip header
                
                for row in rows[:5]:  # Limit to last 5 transfers
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        transfer = {
                            'date': cells[0].get_text(strip=True),
                            'from_club': cells[1].get_text(strip=True),
                            'to_club': cells[2].get_text(strip=True),
                            'fee': cells[3].get_text(strip=True) if len(cells) > 3 else 'Free transfer'
                        }
                        transfer_history.append(transfer)
            
            if transfer_history:
                player_data['transfer_history'] = transfer_history
        
        except Exception as e:
            logger.error(f"Error extracting transfer history: {str(e)}")
    
    def scrape_team_players(self, team_url, limit=None):
        """
        Scrape all players from a team page
        """
        try:
            response = self.session.get(team_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            players = []
            
            # Find player table
            player_table = soup.find('table', class_='items')
            if player_table:
                rows = player_table.find('tbody').find_all('tr')
                
                for row in rows:
                    if limit and len(players) >= limit:
                        break
                    
                    # Extract basic player info from table row
                    player_link = row.find('a', href=re.compile(r'/spieler/'))
                    if player_link:
                        player_url = urljoin(team_url, player_link['href'])
                        player_name = player_link.get_text(strip=True)
                        
                        # Extract other info from row
                        cells = row.find_all('td')
                        player_info = {
                            'name': player_name,
                            'profile_url': player_url,
                            'transfermarkt_id': self.extract_player_id(player_url)
                        }
                        
                        # Try to extract position, age, market value from table
                        if len(cells) > 2:
                            for cell in cells:
                                cell_text = cell.get_text(strip=True)
                                if '€' in cell_text and ('m' in cell_text or 'k' in cell_text):
                                    player_info['current_market_value'] = cell_text
                                    player_info['market_value_numeric'] = self.parse_market_value(cell_text)
                        
                        players.append(player_info)
                    
                    # Add delay to be respectful
                    time.sleep(0.5)
            
            return players
            
        except Exception as e:
            logger.error(f"Error scraping team players {team_url}: {str(e)}")
            return []
    
    def scrape_search_results(self, search_query, limit=10):
        """
        Scrape players from search results
        """
        try:
            search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={search_query}&Spieler_page=1"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            players = []
            
            # Find search results
            results_table = soup.find('table', class_='items')
            if results_table:
                rows = results_table.find('tbody').find_all('tr')
                
                for row in rows[:limit]:
                    player_link = row.find('a', href=re.compile(r'/spieler/'))
                    if player_link:
                        player_url = urljoin(search_url, player_link['href'])
                        player_name = player_link.get_text(strip=True)
                        
                        player_info = {
                            'name': player_name,
                            'profile_url': player_url,
                            'transfermarkt_id': self.extract_player_id(player_url)
                        }
                        
                        players.append(player_info)
                    
                    time.sleep(0.3)
            
            return players
            
        except Exception as e:
            logger.error(f"Error scraping search results: {str(e)}")
            return []


# Convenience functions for the views
def scrape_transfermarkt_player(url, options=None):
    """Convenience function to scrape a single player"""
    scraper = TransferMarktScraper()
    return scraper.scrape_player_profile(url, options)

def scrape_transfermarkt_team(team_url, limit=None):
    """Convenience function to scrape team players"""
    scraper = TransferMarktScraper()
    return scraper.scrape_team_players(team_url, limit)

def search_transfermarkt_players(query, limit=10):
    """Convenience function to search players"""
    scraper = TransferMarktScraper()
    return scraper.scrape_search_results(query, limit)
