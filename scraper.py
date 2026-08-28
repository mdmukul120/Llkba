import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import config

class DzriTVScraper:
    """
    DzriTV ওয়েবসাইট থেকে ক্যাটাগরি এবং ডাইরেক্ট Iframe URL এক্সট্র্যাক্ট করার স্ক্র্যাপার
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.HTTP_HEADERS)

    def fetch_page_content(self, url: str) -> BeautifulSoup:
        for attempt in range(config.MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                if response.status_code == 200:
                    return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException:
                pass
        return None

    def get_all_categories(self) -> List[Dict[str, str]]:
        soup = self.fetch_page_content(config.TARGET_BASE_URL)
        categories = []
        
        if not soup:
            return categories

        nav_links = soup.select('nav a, div.menu a, header a, a[href*="/category/"], a[href*="/sport/"]')
        seen_urls = set()

        for link in nav_links:
            href = link.get('href', '')
            cat_name = link.text.strip()
            
            if href and cat_name and href not in seen_urls:
                full_url = href if href.startswith('http') else f"{config.TARGET_BASE_URL.rstrip('/')}/{href.lstrip('/')}"
                seen_urls.add(href)
                categories.append({
                    "name": cat_name,
                    "url": full_url
                })
                
        return categories

    def extract_direct_iframe(self, match_slug_url: str) -> Dict[str, str]:
        """ ডাইরেক্ট Iframe URL ও HTML কোড এক্সট্র্যাক্ট করে """
        soup = self.fetch_page_content(match_slug_url)
        result = {
            "iframe_url": "",
            "embed_code": ""
        }

        if not soup:
            return result

        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src') or iframe.get('data-src') or iframe.get('lazy-src') or ''
            
            if src and not any(ignored in src for ignored in ['facebook.com', 'google.com', 'analytics', 'disqus', 'ads']):
                if src.startswith('//'):
                    final_iframe_url = f"https:{src}"
                elif src.startswith('http'):
                    final_iframe_url = src
                else:
                    final_iframe_url = f"{config.TARGET_BASE_URL.rstrip('/')}/{src.lstrip('/')}"

                result["iframe_url"] = final_iframe_url
                result["embed_code"] = f'<iframe src="{final_iframe_url}" width="100%" height="100%" frameborder="0" allowfullscreen="true" scrolling="no" allow="encrypted-media; autoplay"></iframe>'
                break

        return result

    def scrape_matches_by_category(self, category: Dict[str, str]) -> List[Dict[str, Any]]:
        soup = self.fetch_page_content(category['url'])
        match_list = []

        if not soup:
            return match_list

        cards = soup.select('.match-card, .event-item, article, .post-item, a[href*="/match/"], a[href*="/live/"]')
        seen_slugs = set()

        for card in cards:
            link_tag = card if card.name == 'a' else card.find('a')
            if not link_tag or not link_tag.get('href'):
                continue

            slug_url = link_tag['href']
            if slug_url in seen_slugs:
                continue
            
            seen_slugs.add(slug_url)
            full_slug_url = slug_url if slug_url.startswith('http') else f"{config.TARGET_BASE_URL.rstrip('/')}/{slug_url.lstrip('/')}"
            
            title = link_tag.get('title') or card.text.strip()
            title = re.sub(r'\s+', ' ', title)

            if len(title) > 3:
                iframe_data = self.extract_direct_iframe(full_slug_url)

                match_list.append({
                    "title": title,
                    "category": category['name'],
                    "slug_url": full_slug_url,
                    "iframe_url": iframe_data["iframe_url"],
                    "embed_code": iframe_data["embed_code"]
                })

        return match_list
