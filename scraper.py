import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import config

class DzriTVScraper:
    """
    DzriTV ওয়েবসাইট থেকে স্লাগ URL নিয়ে কাস্টম CSS এর মাধ্যমে শুধুমাত্র ভিডিও প্লেয়ার ভিউ রেন্ডার করার স্ক্র্যাপার
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

    def generate_cropped_embed(self, match_slug_url: str) -> Dict[str, str]:
        """
        স্লাগ URL টি আইফ্রেমের ভেতর রেখে CSS Margin/Crop এর মাধ্যমে 
        সাইটের হেডার-ফুটার লুকিয়ে শুধু ভিডিও প্লেয়ারটুকু ডিসপ্লে করাবে।
        """
        # CSS ট্রিকস দিয়ে সাইটের ওপরের অংশ (Header/Nav) কেটে বাদ দিয়ে প্লেয়ার ফোকাস করা
        embed_code = (
            f'<div style="position: relative; width: 100%; height: 0; padding-bottom: 56.25%; overflow: hidden; background: #000;">'
            f'<iframe src="{match_slug_url}" '
            f'style="position: absolute; top: -140px; left: 0; width: 100%; height: calc(100% + 200px); border: none; scrolling: no;" '
            f'allowfullscreen="true" scrolling="no" allow="autoplay; encrypted-media">'
            f'</iframe>'
            f'</div>'
        )
        
        return {
            "iframe_url": match_slug_url,
            "embed_code": embed_code
        }

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
                player_data = self.generate_cropped_embed(full_slug_url)

                match_list.append({
                    "title": title,
                    "category": category['name'],
                    "slug_url": full_slug_url,
                    "iframe_url": player_data["iframe_url"],
                    "embed_code": player_data["embed_code"]
                })

        return match_list
