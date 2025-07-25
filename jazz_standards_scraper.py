
#!/usr/bin/env python3
"""
Jazz Standards Data Collector - Full Implementation
Scrapes information about jazz standards from multiple sources
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import logging
from datetime import datetime
import re
import os
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jazz_scraper.log'),
        logging.StreamHandler()
    ]
)

# Rate limiting configuration
DELAYS = {
    'jazzstandards.com': 2.0,
    'wikipedia.org': 0.5,
    'musescore.com': 1.5,
    'musicnotes.com': 1.5,
    'jazzoasis.com': 1.0,
    'default': 1.0
}

class JazzStandardsScraper:
    """Main scraper class for collecting jazz standards data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.results = []
        self.cache = {}
        self.load_cache()
        
        # Data validation constants
        self.valid_keys = [
            'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 
            'A', 'A#', 'Bb', 'B', 'Cm', 'C#m', 'Dbm', 'Dm', 'D#m', 'Ebm', 'Em', 
            'Fm', 'F#m', 'Gbm', 'Gm', 'G#m', 'Abm', 'Am', 'A#m', 'Bbm', 'Bm'
        ]
        
        self.common_forms = [
            'AABA', 'ABAC', 'ABAB', 'Blues', '32-bar', '16-bar', '12-bar',
            'Through-composed', 'AB', 'ABA', 'AABC', 'ABCD'
        ]
        
        # Composer name variations for matching
        self.composer_aliases = {
            'Antonio Carlos Jobim': ['Tom Jobim', 'A.C. Jobim', 'Jobim'],
            'Thelonious Monk': ['Monk', 'T. Monk'],
            'Duke Ellington': ['Ellington', 'D. Ellington', 'Edward Kennedy Ellington'],
            'George Gershwin': ['Gershwin', 'G. Gershwin'],
            'Cole Porter': ['Porter', 'C. Porter'],
            'Jerome Kern': ['Kern', 'J. Kern'],
            'Richard Rodgers': ['Rodgers', 'R. Rodgers'],
            'Irving Berlin': ['Berlin', 'I. Berlin'],
            'Harold Arlen': ['Arlen', 'H. Arlen'],
            'Hoagy Carmichael': ['Carmichael', 'H. Carmichael'],
            'Johnny Mercer': ['Mercer', 'J. Mercer'],
            'Billy Strayhorn': ['Strayhorn', 'B. Strayhorn']
        }
    
    def load_cache(self):
        """Load cached results if they exist"""
        cache_file = 'jazz_scraper_cache.json'
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logging.info(f"Loaded {len(self.cache)} cached entries")
            except Exception as e:
                logging.error(f"Error loading cache: {e}")
                self.cache = {}
    
    def save_cache(self):
        """Save cache to file"""
        try:
            with open('jazz_scraper_cache.json', 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving cache: {e}")
    
    def clean_song_title(self, title: str) -> str:
        """Clean song title for searching"""
        # Remove parenthetical information
        title = re.sub(r'\([^)]*\)', '', title)
        # Remove special characters but keep apostrophes
        title = re.sub(r'[^\w\s\']', ' ', title)
        # Clean up whitespace
        title = ' '.join(title.split())
        return title.strip()
    
    def extract_year_from_text(self, text: str) -> Optional[str]:
        """Extract year from text using various patterns"""
        patterns = [
            r'(?:written|composed|published|recorded|in|from)\s+(?:in\s+)?(\d{4})',
            r'(?:©|copyright)\s*(\d{4})',
            r'\b(19[2-9]\d|20[0-2]\d)\b',  # Years from 1920-2029
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                year = match.group(1)
                if 1920 <= int(year) <= 2024:  # Reasonable range for jazz standards
                    return year
        return None
    
    def extract_composer_from_text(self, text: str) -> Optional[str]:
        """Extract composer from text using various patterns"""
        patterns = [
            r'(?:written|composed|music)\s+by\s+([A-Z][a-zA-Z\s\.\-\']+?)(?:\s+and|\s+with|\s+in|\.|,|$)',
            r'([A-Z][a-zA-Z\s\.\-\']+?)\s+(?:wrote|composed|penned)',
            r'composer[:\s]+([A-Z][a-zA-Z\s\.\-\']+?)(?:\.|,|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Clean up the match
                composer = matches[0].strip()
                # Remove common suffixes
                composer = re.sub(r'\s+(wrote|composed|penned).*$', '', composer)
                return composer
        return None
    
    def search_jazzstandards_com(self, song_title: str) -> Optional[Dict]:
        """Search jazzstandards.com for song information"""
        try:
            clean_title = self.clean_song_title(song_title)
            
            # First, try to search their index
            search_url = "http://www.jazzstandards.com/compositions/index.htm"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for the song in their alphabetical list
            song_link = None
            for link in soup.find_all('a'):
                link_text = link.get_text(strip=True)
                if clean_title.lower() in link_text.lower():
                    song_link = link.get('href')
                    break
            
            if not song_link:
                # Try alternative search by first letter
                first_letter = clean_title[0].lower()
                letter_url = f"http://www.jazzstandards.com/compositions/{first_letter}.htm"
                response = self.session.get(letter_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    for link in soup.find_all('a'):
                        if clean_title.lower() in link.get_text(strip=True).lower():
                            song_link = link.get('href')
                            break
            
            result = {
                "source": "jazzstandards.com",
                "composer": None,
                "year": None,
                "key": None,
                "form": None
            }
            
            if song_link:
                # Get the song page
                if not song_link.startswith('http'):
                    song_link = urljoin("http://www.jazzstandards.com/compositions/", song_link)
                
                song_response = self.session.get(song_link, timeout=10)
                song_soup = BeautifulSoup(song_response.content, 'html.parser')
                
                # Extract information from the page
                page_text = song_soup.get_text()
                
                # Look for composer
                composer_match = re.search(r'Composer[:\s]+([^\n]+)', page_text)
                if composer_match:
                    result["composer"] = composer_match.group(1).strip()
                
                # Look for year
                result["year"] = self.extract_year_from_text(page_text)
                
                # Look for key
                key_match = re.search(r'Key[:\s]+([A-G][#b]?\s*(?:major|minor|maj|min)?)', page_text, re.IGNORECASE)
                if key_match:
                    result["key"] = key_match.group(1).strip()
                
                # Look for form
                form_match = re.search(r'Form[:\s]+([^\n]+)', page_text, re.IGNORECASE)
                if form_match:
                    result["form"] = form_match.group(1).strip()
            
            time.sleep(DELAYS.get('jazzstandards.com', 2.0))
            return result
            
        except Exception as e:
            logging.error(f"Error searching jazzstandards.com for {song_title}: {e}")
            return None
    
    def search_wikipedia(self, song_title: str) -> Optional[Dict]:
        """Enhanced Wikipedia search for song information"""
        try:
            search_url = "https://en.wikipedia.org/w/api.php"
            
            # Clean title for search
            clean_title = self.clean_song_title(song_title)
            
            # Try multiple search strategies
            search_queries = [
                f'"{song_title}" jazz standard',
                f'{clean_title} jazz standard',
                f'"{clean_title}" song',
                clean_title
            ]
            
            for query in search_queries:
                search_params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': query,
                    'srlimit': 3
                }
                
                response = self.session.get(search_url, params=search_params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data['query']['search']:
                    # Check each result
                    for search_result in data['query']['search']:
                        page_title = search_result['title']
                        
                        # Get page content
                        content_params = {
                            'action': 'query',
                            'format': 'json',
                            'titles': page_title,
                            'prop': 'extracts|pageprops|categories',
                            'exintro': False,
                            'explaintext': True,
                            'exsectionformat': 'plain',
                            'cllimit': 50
                        }
                        
                        content_response = self.session.get(search_url, params=content_params, timeout=10)
                        content_response.raise_for_status()
                        content_data = content_response.json()
                        
                        pages = content_data['query']['pages']
                        page_id = list(pages.keys())[0]
                        
                        if page_id != '-1':
                            page = pages[page_id]
                            extract = page.get('extract', '')
                            
                            # Check if this is likely about our song
                            if clean_title.lower() in extract.lower():
                                result = {
                                    "source": "wikipedia",
                                    "composer": None,
                                    "year": None,
                                    "genre": "Jazz Standard"
                                }
                                
                                # Enhanced composer extraction
                                composer_patterns = [
                                    r'(?:written|composed)\s+by\s+([A-Z][a-zA-Z\s\.\-\']+?)(?:\s+and\s+([A-Z][a-zA-Z\s\.\-\']+?))?(?:\s+in|\s+for|\.|,)',
                                    r'([A-Z][a-zA-Z\s\.\-\']+?)\s+wrote\s+(?:the\s+)?(?:song|tune|composition)',
                                    r'composer[s]?\s+([A-Z][a-zA-Z\s\.\-\']+?)(?:\s+and\s+([A-Z][a-zA-Z\s\.\-\']+?))?[\.\,]',
                                    r'music\s+by\s+([A-Z][a-zA-Z\s\.\-\']+)',
                                ]
                                
                                for pattern in composer_patterns:
                                    match = re.search(pattern, extract)
                                    if match:
                                        composers = [match.group(1)]
                                        if len(match.groups()) > 1 and match.group(2):
                                            composers.append(match.group(2))
                                        result["composer"] = " & ".join(c.strip() for c in composers if c)
                                        break
                                
                                # Year extraction
                                result["year"] = self.extract_year_from_text(extract)
                                
                                # Genre detection
                                if any(term in extract.lower() for term in ['bossa nova', 'brazilian']):
                                    result["genre"] = "Bossa Nova"
                                elif any(term in extract.lower() for term in ['bebop', 'be-bop']):
                                    result["genre"] = "Bebop"
                                elif 'blues' in extract.lower():
                                    result["genre"] = "Blues"
                                elif any(term in extract.lower() for term in ['ballad', 'slow']):
                                    result["genre"] = "Ballad"
                                
                                time.sleep(DELAYS.get('wikipedia.org', 0.5))
                                return result
            
            return None
            
        except Exception as e:
            logging.error(f"Error searching Wikipedia for {song_title}: {e}")
            return None
    
    def search_musescore(self, song_title: str) -> Optional[Dict]:
        """Search MuseScore for sheet music information"""
        try:
            clean_title = self.clean_song_title(song_title)
            search_title = quote(clean_title)
            url = f"https://musescore.com/sheetmusic?text={search_title}&type=non-official"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            result = {
                "source": "musescore",
                "key": None,
                "tempo": None,
                "time_signature": None
            }
            
            # Find score links
            score_links = soup.find_all('a', {'class': 'tIwxZ'})  # This class might change
            if not score_links:
                # Try alternative selectors
                score_links = soup.find_all('a', href=re.compile(r'/scores/\d+'))
            
            for link in score_links[:3]:  # Check first 3 results
                if clean_title.lower() in link.get_text(strip=True).lower():
                    score_url = urljoin("https://musescore.com", link.get('href'))
                    
                    # Get the score page
                    score_response = self.session.get(score_url, timeout=10)
                    score_soup = BeautifulSoup(score_response.content, 'html.parser')
                    
                    # Extract metadata
                    metadata_section = score_soup.find('div', {'class': 'ScoreMetadata'})
                    if metadata_section:
                        metadata_text = metadata_section.get_text()
                        
                        # Key extraction
                        key_match = re.search(r'Key[:\s]+([A-G][#b]?\s*(?:major|minor|maj|min)?)', metadata_text, re.IGNORECASE)
                        if key_match:
                            result["key"] = key_match.group(1).strip()
                        
                        # Tempo extraction
                        tempo_match = re.search(r'(?:Tempo|BPM)[:\s]+(\d+)', metadata_text, re.IGNORECASE)
                        if tempo_match:
                            result["tempo"] = tempo_match.group(1)
                        
                        # Time signature
                        time_match = re.search(r'(\d+/\d+)', metadata_text)
                        if time_match:
                            result["time_signature"] = time_match.group(1)
                    
                    break
            
            time.sleep(DELAYS.get('musescore.com', 1.5))
            return result
            
        except Exception as e:
            logging.error(f"Error searching MuseScore for {song_title}: {e}")
            return None
    
    def search_jazzoasis(self, song_title: str) -> Optional[Dict]:
        """Search Jazz Oasis for additional information"""
        try:
            clean_title = self.clean_song_title(song_title)
            
            # Jazz Oasis uses a different URL structure
            base_url = "https://www.jazzoasis.com/songsearch.php"
            params = {'song': clean_title}
            
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            result = {
                "source": "jazzoasis",
                "composer": None,
                "year": None,
                "recordings": []
            }
            
            # Look for song information in the results
            results_table = soup.find('table', {'class': 'results'})
            if results_table:
                rows = results_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        song_name = cells[0].get_text(strip=True)
                        if clean_title.lower() in song_name.lower():
                            result["composer"] = cells[1].get_text(strip=True)
                            # Sometimes year is in the third cell
                            year_text = cells[2].get_text(strip=True)
                            year_match = re.search(r'\d{4}', year_text)
                            if year_match:
                                result["year"] = year_match.group()
                            break
            
            time.sleep(DELAYS.get('jazzoasis.com', 1.0))
            return result
            
        except Exception as e:
            logging.error(f"Error searching Jazz Oasis for {song_title}: {e}")
            return None
    
    def normalize_key(self, key: str) -> str:
        """Normalize key notation"""
        if not key:
            return None
        
        key = key.strip()
        
        # Replace variations
        replacements = {
            'major': '',
            'Major': '',
            'maj': '',
            'minor': 'm',
            'Minor': 'm',
            'min': 'm',
            'flat': 'b',
            'sharp': '#',
            '♭': 'b',
            '♯': '#'
        }
        
        for old, new in replacements.items():
            key = key.replace(old, new)
        
        # Clean up whitespace
        key = ''.join(key.split())
        
        # Ensure proper capitalization
        if key:
            if len(key) > 1 and key[1] in ['#', 'b']:
                key = key[0].upper() + key[1:]
            else:
                key = key[0].upper() + key[1:]
        
        return key if key in self.valid_keys else None
    
    def determine_swing_feel(self, tempo: str, genre: str, title: str) -> str:
        """Enhanced swing feel determination"""
        swing_keywords = ['swing', 'bebop', 'bop', 'blues', 'rhythm changes', 'bird', 'hard bop']
        straight_keywords = ['bossa', 'latin', 'samba', 'waltz', 'ballad', 'even 8ths', 'brazilian', 'afro', 'cuban', 'funk']
        
        title_lower = title.lower()
        genre_lower = genre.lower() if genre else ""
        
        # Strong indicators for straight feel
        for keyword in straight_keywords:
            if keyword in title_lower or keyword in genre_lower:
                if keyword == 'ballad' and tempo:
                    try:
                        if int(tempo) < 70:
                            return "Ballad (Swing or Straight)"
                    except:
                        pass
                return "Straight"
        
        # Strong indicators for swing feel
        for keyword in swing_keywords:
            if keyword in title_lower or keyword in genre_lower:
                return "Swing"
        
        # Tempo-based determination
        if tempo:
            try:
                tempo_int = int(tempo)
                if tempo_int < 60:
                    return "Ballad (Swing or Straight)"
                elif 60 <= tempo_int < 120:
                    return "Swing"  # Medium tempos typically swing
                elif tempo_int >= 180:
                    return "Swing"  # Up-tempo usually swings
            except:
                pass
        
        # Special cases
        if "waltz" in title_lower or "3/4" in str(genre_lower):
            return "Straight (3/4)"
        
        return "Swing"  # Default for jazz standards
    
    def determine_difficulty(self, key: str, tempo: str, form: str, title: str) -> str:
        """Enhanced difficulty determination"""
        difficulty_score = 0
        
        # Key difficulty
        if key:
            difficult_keys = {
                'F#': 2, 'C#': 2, 'G#': 2, 'D#': 2, 
                'Gb': 2, 'Db': 1.5, 'Ab': 1, 'Eb': 1,
                'F#m': 2, 'C#m': 2, 'G#m': 2, 'D#m': 2,
                'Ebm': 1.5, 'Bbm': 1
            }
            difficulty_score += difficult_keys.get(key, 0)
        
        # Tempo difficulty
        if tempo:
            try:
                tempo_int = int(tempo)
                if tempo_int > 200:
                    difficulty_score += 2
                elif tempo_int > 160:
                    difficulty_score += 1
                elif tempo_int < 60:
                    difficulty_score += 0.5  # Very slow can be challenging
            except:
                pass
        
        # Form complexity
        if form:
            if any(term in str(form).lower() for term in ['complex', 'through-composed', 'unusual']):
                difficulty_score += 1.5
            elif 'AABA' in str(form):
                difficulty_score += 0  # Standard form
            else:
                difficulty_score += 0.5
        
        # Known difficult pieces
        difficult_pieces = ['giant steps', 'countdown', 'inner urge', 'moments notice', '26-2']
        if any(piece in title.lower() for piece in difficult_pieces):
            difficulty_score += 2
        
        # Determine level
        if difficulty_score <= 1:
            return "Beginner"
        elif difficulty_score <= 2.5:
            return "Intermediate"
        elif difficulty_score <= 4:
            return "Advanced"
        else:
            return "Expert"
    
    def determine_movement(self, tempo: str) -> str:
        """Determine movement based on tempo"""
        if not tempo:
            return None
        
        try:
            tempo_int = int(tempo)
            if tempo_int < 60:
                return "Ballad"
            elif tempo_int < 80:
                return "Slow"
            elif tempo_int < 108:
                return "Medium-Slow"
            elif tempo_int < 132:
                return "Medium"
            elif tempo_int < 160:
                return "Medium-Up"
            elif tempo_int < 200:
                return "Up"
            elif tempo_int < 250:
                return "Fast"
            else:
                return "Burning"
        except:
            return None
    
    def merge_composer_data(self, *composers) -> Optional[str]:
        """Merge composer data from multiple sources"""
        valid_composers = [c for c in composers if c and c.strip()]
        if not valid_composers:
            return None
        
        # Use the first valid composer, but check for known aliases
        primary = valid_composers[0].strip()
        
        # Check against known aliases
        for full_name, aliases in self.composer_aliases.items():
            if primary in aliases or any(alias in primary for alias in aliases):
                return full_name
        
        return primary
    
    def process_song(self, song_title: str) -> Dict:
        """Process a single song, gathering data from multiple sources"""
        logging.info(f"Processing: {song_title}")
        
        # Check cache first
        cache_key = song_title.lower().strip()
        if cache_key in self.cache:
            logging.info(f"Using cached data for: {song_title}")
            return self.cache[cache_key]
        
        song_data = {
            "Title": song_title,
            "Composer(s)": None,
            "Year": None,
            "Genre": "Jazz Standard",
            "Key": None,
            "Tempo": None,
            "Swing": None,
            "Form": None,
            "Tonality": None,
            "Movement": None,
            "Difficulty": None
        }
        
        # Search each source
        wiki_data = self.search_wikipedia(song_title)
        jazz_data = self.search_jazzstandards_com(song_title)
        score_data = self.search_musescore(song_title)
        oasis_data = self.search_jazzoasis(song_title)
        
        # Merge composer data (prioritize jazzstandards.com)
        composers = []
        if jazz_data and jazz_data.get("composer"):
            composers.append(jazz_data.get("composer"))
        if wiki_data and wiki_data.get("composer"):
            composers.append(wiki_data.get("composer"))
        if oasis_data and oasis_data.get("composer"):
            composers.append(oasis_data.get("composer"))
        
        song_data["Composer(s)"] = self.merge_composer_data(*composers)
        
        # Year (prioritize earliest found)
        years = []
        for data in [wiki_data, jazz_data, oasis_data]:
            if data and data.get("year"):
                years.append(data.get("year"))
        
        if years:
            try:
                song_data["Year"] = str(min(int(y) for y in years if y))
            except:
                song_data["Year"] = years[0]
        
        # Genre
        if wiki_data and wiki_data.get("genre"):
            song_data["Genre"] = wiki_data.get("genre")
        
        # Key (prioritize musescore)
        if score_data and score_data.get("key"):
            song_data["Key"] = self.normalize_key(score_data.get("key"))
        elif jazz_data and jazz_data.get("key"):
            song_data["Key"] = self.normalize_key(jazz_data.get("key"))
        
        # Tempo
        if score_data and score_data.get("tempo"):
            song_data["Tempo"] = score_data.get("tempo")
        
        # Form
        if jazz_data and jazz_data.get("form"):
            song_data["Form"] = jazz_data.get("form")
        
        # Determine derived fields
        song_data["Swing"] = self.determine_swing_feel(
            song_data["Tempo"], 
            song_data["Genre"], 
            song_title
        )
        
        song_data["Difficulty"] = self.determine_difficulty(
            song_data["Key"],
            song_data["Tempo"],
            song_data["Form"],
            song_title
        )
        
        song_data["Movement"] = self.determine_movement(song_data["Tempo"])
        
        # Tonality
        if song_data["Key"]:
            if 'm' in song_data["Key"]:
                song_data["Tonality"] = "Minor"
            else:
                song_data["Tonality"] = "Major"
        
        # Cache the result
        self.cache[cache_key] = song_data
        self.save_cache()
        
        return song_data
    
    def scrape_all_songs(self, song_list: List[str]) -> List[Dict]:
        """Process all songs in the list"""
        total_songs = len(song_list)
        
        for i, song in enumerate(song_list):
            try:
                song_data = self.process_song(song)
                self.results.append(song_data)
                
                # Save progress every 10 songs
                if (i + 1) % 10 == 0:
                    self.save_progress()
                    logging.info(f"Progress: {i + 1}/{total_songs} songs processed ({((i + 1) / total_songs * 100):.1f}%)")
                
                # Longer delay every 25 songs
                if (i + 1) % 25 == 0:
                    logging.info("Taking a 15-second break to avoid rate limiting...")
                    time.sleep(15)
                
            except KeyboardInterrupt:
                logging.info("Scraping interrupted by user. Saving progress...")
                self.save_progress()
                break
                
            except Exception as e:
                logging.error(f"Error processing {song}: {e}")
                # Add empty entry for failed song
                self.results.append({
                    "Title": song,
                    "Composer(s)": None,
                    "Year": None,
                    "Genre": "Jazz Standard",
                    "Key": None,
                    "Tempo": None,
                    "Swing": None,
                    "Form": None,
                    "Tonality": None,
                    "Movement": None,
                    "Difficulty": None,
                    "Error": str(e)
                })
                continue
        
        self.save_progress()
        return self.results
    
    def save_progress(self):
        """Save current results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save main results file
        with open('jazz_standards_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Save timestamped backup
        backup_filename = f'jazz_standards_backup_{timestamp}.json'
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Saved {len(self.results)} songs to jazz_standards_data.json")
        logging.info(f"Backup saved to {backup_filename}")
    
    def generate_summary_report(self):
        """Generate a summary report of the collected data"""
        if not self.results:
            return
        
        total = len(self.results)
        complete = sum(1 for song in self.results if all(
            song.get(field) is not None 
            for field in ["Composer(s)", "Year", "Key", "Tempo"]
        ))
        
        report = f"""
Jazz Standards Data Collection Summary
=====================================
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total songs processed: {total}
Complete entries: {complete} ({complete/total*100:.1f}%)
Songs with errors: {sum(1 for song in self.results if 'Error' in song)}

Field completion rates:
-----------------------
"""
        
        fields = ["Composer(s)", "Year", "Genre", "Key", "Tempo", "Swing", "Form", "Tonality", "Movement", "Difficulty"]
        
        for field in fields:
            count = sum(1 for song in self.results if song.get(field) is not None)
            report += f"  {field:<15}: {count:>4}/{total} ({count/total*100:>5.1f}%)\n"
        
        # Additional statistics
        report += f"\n\nAdditional Statistics:\n"
        report += f"----------------------\n"
        
        # Key distribution
        key_counts = {}
        for song in self.results:
            key = song.get("Key")
            if key:
                key_counts[key] = key_counts.get(key, 0) + 1
        
        report += f"\nMost common keys:\n"
        for key, count in sorted(key_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"  {key:<5}: {count:>3}\n"
        
        # Difficulty distribution
        diff_counts = {}
        for song in self.results:
            diff = song.get("Difficulty")
            if diff:
                diff_counts[diff] = diff_counts.get(diff, 0) + 1
        
        report += f"\nDifficulty distribution:\n"
        for diff in ["Beginner", "Intermediate", "Advanced", "Expert"]:
            count = diff_counts.get(diff, 0)
            report += f"  {diff:<12}: {count:>3} ({count/total*100:>5.1f}%)\n"
        
        # Save report
        with open('collection_report.txt', 'w') as f:
            f.write(report)
        
        print(report)

def main():
    """Main function to run the scraper"""
    
    # Your complete song list
    song_list = [
        "African Flower (Petite Fleur Africaine)",
        "Afro Blue",
        "Afternoon In Paris",
        "Água De Beber (Water To Drink)",
        "Airegin",
        "Alfie",
        "Alice In Wonderland",
        "All Blues",
        "All By Myself",
        "All Of Me",
        "All Of You",
        "All The Things You Are",
        "Alright, Okay, You Win",
        "Always",
        "Ana Maria",
        "Angel Eyes",
        "Anthropology",
        "Apple Honey",
        "April In Paris",
        "April Joy",
        "Arise, Her Eyes",
        "Armageddon",
        "Au Privave",
        "Autumn In New York",
        "Autumn Leaves",
        "Beautiful Love",
        "Beauty And The Beast",
        "Bessie's Blues",
        "Bewitched",
        "Big Nick",
        "Birdlike",
        "Black Coffee",
        "Black Diamond",
        "Black Narcissus",
        "Black Nile",
        "Black Orpheus",
        "Blue Bossa",
        "Blue In Green",
        "Blue Monk",
        "The Blue Room",
        "Blue Train (Blue Trane)",
        "Blues For Alice",
        "Bluesette",
        "Body And Soul",
        "Boplicity (Be Bop Lives)",
        "Bright Size Life",
        "Broad Way Blues",
        "Broadway",
        "But Beautiful",
        "Butterfly",
        "C'est Si Bon",
        "Call Me",
        "Call Me Irresponsible",
        "Can't Help Lovin' Dat Man",
        "Captain Marvel",
        "Central Park West",
        "Ceora",
        "Chega De Saudade (No More Blues)",
        "Chelsea Bells",
        "Chelsea Bridge",
        "Cherokee (Indian Love Song)",
        "Cherry Pink And Apple Blossom White",
        "A Child Is Born",
        "Chippie",
        "Chitlins Con Carne",
        "Come Sunday",
        "Como En Vietnam",
        "Con Alma",
        "Conception",
        "Confirmation",
        "Contemplation",
        "Coral",
        "Cotton Tail",
        "Could It Be You",
        "Countdown",
        "Crescent",
        "Crystal Silence",
        "D Natural Blues",
        "Daahoud",
        "Dancing On The Ceiling",
        "Darn That Dream",
        "Day Waves",
        "Days And Nights Waiting",
        "Dear Old Stockholm",
        "Dearly Beloved",
        "Dedicated To You",
        "Deluge",
        "Desafinado",
        "Desert Air",
        "Detour Ahead",
        "Dexterity",
        "Dizzy Atmosphere",
        "Django",
        "Doin' The Pig",
        "Dolores",
        "Dolphin Dance",
        "Domino Biscuit",
        "Don't Blame Me",
        "Don't Get Around Much Anymore",
        "Donna Lee",
        "Dream A Little Dream Of Me",
        "Dreamsville",
        "Easter Parade",
        "Easy Living",
        "Easy To Love (You'd Be So Easy To Love)",
        "Ecclusiastics",
        "Eighty One",
        "El Gaucho",
        "Epistrophy",
        "Equinox",
        "Equipoise",
        "E.S.P.",
        "Fall",
        "Falling Grace",
        "Falling In Love With Love",
        "Fee-Fi-Fo-Fum",
        "A Fine Romance",
        "500 Miles High",
        "502 Blues",
        "Follow Your Heart",
        "Footprints",
        "For All We Know",
        "For Heaven's Sake",
        "(I Love You) For Sentimental Reasons",
        "Forest Flower",
        "Four",
        "Four On Six",
        "Freddie Freeloader",
        "Freedom Jazz Dance",
        "Full House",
        "Gee Baby, Ain't I Good To You",
        "Gemini",
        "Giant Steps",
        "The Girl From Ipanema (Garôta De Ipanema)",
        "Gloria's Step",
        "God Bless' The Child",
        "Golden Lady",
        "Good Evening Mr. And Mrs. America",
        "Grand Central",
        "The Green Mountains",
        "Groovin' High",
        "Grow Your Own",
        "Guilty",
        "Gypsy In My Soul",
        "Half Nelson",
        "Have You Met Miss Jones?",
        "Heaven",
        "Heebie Jeebies",
        "Hello, Young Lovers",
        "Here's That Rainy Day",
        "Hot Toddy",
        "House Of Jade",
        "How High The Moon",
        "How Insensitive (Insensatez)",
        "How My Heart Sings",
        "Hullo Bolinas",
        "I Can't Get Started",
        "I Can't Give You Anything But Love",
        "I Could Write A Book",
        "I Got It Bad And That Ain't Good",
        "I Let A Song Go Out Of My Heart",
        "I Love Paris",
        "I Love You",
        "I Mean You",
        "I Remember Clifford",
        "I Should Care",
        "I Wish I Knew How It Would Feel To Be Free",
        "I'll Never Smile Again",
        "I'll Remember April",
        "I'm All Smiles",
        "I'm Beginning To See The Light",
        "I'm Your Pal",
        "Icarus",
        "If You Never Come To Me (Inutil Paisagem)",
        "Impressions",
        "In A Mellow Tone",
        "In A Sentimental Mood",
        "In The Mood",
        "In The Wee Small Hours Of The Morning",
        "In Your Quiet Place",
        "The Inch Worm",
        "Indian Lady",
        "Inner Urge",
        "Interplay",
        "The Intrepid Fox",
        "Invitation",
        "Iris",
        "Is You Is, Or Is You Ain't (Ma' Baby)",
        "Isn't It Romantic?",
        "Isotope",
        "Israel",
        "It Don't Mean A Thing (If It Ain't Got That Swing)",
        "It's Easy To Remember",
        "Jelly Roll",
        "Jordu",
        "Journey To Recife",
        "Joy Spring",
        "Juju",
        "Jump Monk",
        "June In January",
        "Just One More Chance",
        "Kelo",
        "Lady Bird",
        "Lady Sings The Blues",
        "Lament",
        "Las Vegas Tango",
        "Lazy Bird",
        "Lazy River",
        "Like Someone In Love",
        "Limehouse Blues",
        "Lines And Spaces",
        "Litha",
        "Little Boat (O Barquinho)",
        "Little Waltz",
        "Long Ago (And Far Away)",
        "Lonnie's Lament",
        "Look To The Sky",
        "Love Is The Sweetest Thing",
        "Lucky Southern",
        "Lullaby Of Birdland",
        "Lush Life",
        "The Magician In You",
        "Mahjong",
        "Maiden Voyage",
        "A Man And A Woman (Un Homme Et Une Femme)",
        "Man In The Green Shirt",
        "Meditation (Meditacao)",
        "Memories Of Tomorrow",
        "Michelle",
        "Midnight Mood",
        "Midwestern Nights Dream",
        "Milano",
        "Minority",
        "Miss Ann",
        "Missouri Uncompromised",
        "Mr. P.C.",
        "Misty",
        "Miyako",
        "Moment's Notice",
        "Mood Indigo",
        "Moonchild",
        "The Most Beautiful Girl In The World",
        "My Buddy",
        "My Favorite Things",
        "My Foolish Heart",
        "My Funny Valentine",
        "My One And Only Love",
        "My Romance",
        "My Shining Hour",
        "My Ship",
        "My Way",
        "Mysterious Traveller",
        "Naima (Niema)",
        "Nardis",
        "Nefertiti",
        "Never Will I Marry",
        "Nica's Dream",
        "Night Dreamer",
        "The Night Has A Thousand Eyes",
        "A Night In Tunisia",
        "Night Train",
        "Nobody Knows You When You're Down And Out",
        "Nostalgia In Times Square",
        "Nuages",
        "(The Old Man From) The Old Country",
        "Oleo",
        "Oliloqui Valley",
        "Once I Loved (Amor Em Paz) (Love In Peace)",
        "Once In Love With Amy",
        "One Finger Snap",
        "One Note Samba (Samba De Uma Nota So)",
        "Only Trust Your Heart",
        "Orbits",
        "Ornithology",
        "Out Of Nowhere",
        "Paper Doll",
        "Passion Dance",
        "Passion Flower",
        "Peace",
        "Peggy's Blue Skylight",
        "Pent Up House",
        "Penthouse Serenade",
        "Peri's Scope",
        "Pfrancing",
        "Pinocchio",
        "Pithecanthropus Erectus",
        "Portsmouth Figurations",
        "Prelude To A Kiss",
        "Prince Of Darkness",
        "P.S. I Love You",
        "Pussy Cat Dues",
        "Quiet Nights Of Quiet Stars (Corcovado)",
        "Quiet Now",
        "Recorda Me",
        "Red Clay",
        "Reflections",
        "Reincarnation Of A Lovebird",
        "Ring Dem Bells",
        "Road Song",
        "'Round Midnight",
        "Ruby, My Dear",
        "Poem For #15 (The Saga Of Harrison Crabfeathers)",
        "Satin Doll",
        "Scotch And Soda",
        "Scrapple From The Apple",
        "Sea Journey",
        "Seven Come Eleven",
        "Seven Steps To Heaven",
        "Sidewinder",
        "Silver Hollow",
        "Sirabhorn",
        "Skating In Central Park",
        "So Nice (Summer Samba)",
        "So What",
        "Solar",
        "Solitude",
        "Some Day My Prince Will Come",
        "Some Other Spring",
        "Some Skunk Funk",
        "Somebody Loves Me",
        "Sometime Ago",
        "Song For My Father",
        "The Song Is You",
        "Sophisticated Lady",
        "The Sorcerer",
        "Speak No Evil",
        "The Sphinx",
        "Standing On The Corner",
        "The Star-Crossed Lovers",
        "Stella By Starlight",
        "Steps",
        "Stolen Moments",
        "Stompin' At The Savoy",
        "Straight No Chaser",
        "A String Of Pearls",
        "Stuff",
        "Sugar",
        "A Sunday Kind Of Love",
        "The Surrey With The Fringe On Top",
        "Swedish Pastry",
        "Sweet Georgia Bright",
        "Sweet Henry",
        "Take Five",
        "Take The \"A\" Train",
        "Tame Thy Pen",
        "Tell Me A Bedtime Story",
        "Thanks For The Memory",
        "That's Amore (That's Love)",
        "(There Is) No Greater Love",
        "There Will Never Be Another You",
        "There'll Be Some Changes Made",
        "They Didn't Believe Me",
        "Think On Me",
        "Thou Swell",
        "Three Flowers",
        "Time Remembered",
        "Tones For Joan's Bones",
        "Topsy",
        "Tour De Force",
        "Triste",
        "Tune Up",
        "Turn Out The Stars",
        "Twisted Blues",
        "Unchain My Heart",
        "Unity Village",
        "Unquity Road",
        "Up Jumped Spring",
        "Upper Manhattan Medical Group (UMMG)",
        "Valse Hot",
        "Very Early",
        "Virgo",
        "Wait Till You See Her",
        "Waltz For Debby",
        "Wave",
        "We'll Be Together Again",
        "Well You Needn't (It's Over Now)",
        "West Coast Blues",
        "What Am I Here For?",
        "What Was",
        "When I Fall In Love",
        "When Sunny Gets Blue",
        "When You Wish Upon A Star",
        "Whispering",
        "Wild Flower",
        "Windows",
        "Witch Hunt",
        "Wives And Lovers (Hey, Little Girl)",
        "Woodchopper's Ball",
        "Woody 'n You",
        "The World Is Waiting For The Sunrise",
        "Yes And No",
        "Yesterday",
        "Yesterdays",
        "You Are The Sunshine Of My Life",
        "You Are Too Beautiful",
        "You Brought A New Kind Of Love To Me",
        "You Don't Know What Love Is",
        "You Took Advantage Of Me",
        "You're Nobody 'til Somebody Loves You",
        "Young At Heart"
    ]
    
    print(f"""
Jazz Standards Data Collector - Full Implementation
==================================================
Ready to scrape data for {len(song_list)} songs from multiple sources.

Sources to be searched:
- Wikipedia
- JazzStandards.com
- MuseScore
- Jazz Oasis

This process will:
1. Search multiple sources for each song
2. Cache results to avoid duplicate searches
3. Save progress every 10 songs
4. Take breaks to avoid rate limiting
5. Generate a detailed report when complete

Estimated time: {len(song_list) * 5 / 60:.1f} - {len(song_list) * 10 / 60:.1f} minutes

Press Ctrl+C at any time to stop and save progress.
""")
    
    response = input("Press Enter to start scraping (or 'q' to quit): ")
    if response.lower() == 'q':
        print("Exiting...")
        return
    
    # Initialize scraper and run
    scraper = JazzStandardsScraper()
    
    # Check if we're resuming
    if os.path.exists('jazz_standards_data.json'):
        response = input("Found existing data. Resume from where you left off? (y/n): ")
        if response.lower() == 'y':
            with open('jazz_standards_data.json', 'r', encoding='utf-8') as f:
                scraper.results = json.load(f)
            
            # Remove already processed songs
            processed_titles = {song['Title'] for song in scraper.results}
            song_list = [song for song in song_list if song not in processed_titles]
            print(f"Resuming with {len(song_list)} remaining songs...")
    
    # Start scraping
    results = scraper.scrape_all_songs(song_list)
    
    # Generate summary report
    scraper.generate_summary_report()
    
    print(f"\nScraping complete! Processed {len(scraper.results)} songs total.")
    print("Results saved to: jazz_standards_data.json")
    print("See collection_report.txt for summary statistics.")

if __name__ == "__main__":
    main()
