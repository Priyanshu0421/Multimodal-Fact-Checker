import requests
from typing import Dict, Any, List, Optional
import re
import os
import urllib3
import certifi

class CredibilityChecker:
    def __init__(self):
        self.wikipedia_api_url = "https://en.wikipedia.org/w/api.php"
        self.session = requests.Session()
        
        cert_paths = [
            certifi.where(),
            '/etc/ssl/cert.pem',
            '/usr/local/etc/openssl/cert.pem',
        ]
        
        valid_cert_path = None
        for path in cert_paths:
            if os.path.exists(path):
                valid_cert_path = path
                break
        
        if valid_cert_path:
            self.session.verify = valid_cert_path
        else:
            self.session.verify = False
        
        retry_strategy = urllib3.Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    async def check_claim(self, claim: str) -> Dict[str, Any]:
        search_results = await self._search_wikipedia(claim)
        matches = []
        for result in search_results:
            page_info = await self._get_page_info(result['title'])
            if page_info:
                matches.append(page_info)
        score = self._calculate_score(matches, claim)
        
        return {
            'claim': claim,
            'matches': matches,
            'score': score,
            'sources': [m['url'] for m in matches]
        }
    
    async def _search_wikipedia(self, query: str) -> List[Dict[str, str]]:
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'format': 'json',
            'srlimit': 5
        }
        try:
            response = self.session.get(self.wikipedia_api_url, params=params)
            response.raise_for_status()
            data = response.json()
            results = []
            for item in data['query']['search']:
                results.append({
                    'title': item['title'],
                    'snippet': item['snippet']
                })
            return results
        except Exception as e:
            print(f"Error searching Wikipedia: {str(e)}")
            return []
    
    async def _get_page_info(self, title: str) -> Optional[Dict[str, Any]]:
        params = {
            'action': 'query',
            'prop': 'extracts|info',
            'titles': title,
            'format': 'json',
            'exintro': True,
            'inprop': 'url'
        }
        try:
            response = self.session.get(self.wikipedia_api_url, params=params)
            response.raise_for_status()
            data = response.json()
            pages = data['query']['pages']
            page_id = list(pages.keys())[0]
            page = pages[page_id]
            extract = re.sub(r'<[^>]+>', '', page.get('extract', ''))
            return {
                'title': page['title'],
                'url': page['fullurl'],
                'extract': extract,
                'last_modified': page.get('touched', '')
            }
        except Exception as e:
            print(f"Error getting page info: {str(e)}")
            return None
    
    def _calculate_score(self, matches: List[Dict[str, Any]], claim: str) -> int:
        if not matches:
            return 0
        score = min(len(matches) * 20, 60)
        claim_words = set(claim.lower().split())
        for match in matches:
            extract_words = set(match['extract'].lower().split())
            if claim_words.issubset(extract_words):
                score += 40
                break
        return score
