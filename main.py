import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import config

class DzriTVScraper:
    """
    DzriTV ওয়েবসাইট স্ক্র্যাপ করার এবং আসল ভিডিও লাইভ স্ট্রিম এক্সট্র্যাক্ট করার ক্লাস
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.HTTP_HEADERS)

    def fetch_page_content(self, url: str) -> BeautifulSoup:
        """ যেকোনো ওয়েbaseURL থেকে HTML পেজ ডাউনলোড করে BeautifulSoup অবজেক্ট বানায় """
        for attempt in range(config.MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
                if response.status_code == 200:
                    return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                print(f"[!] রিকোয়েস্ট রিট্রাই করা হচ্ছে ({attempt+1}/{config.MAX_RETRIES}): {url}")
        return None

    def get_all_categories(self) -> List[Dict[str, str]]:
        """ মূল পেজ থেকে সমস্ত খেলার ক্যাটাগরি এবং ক্যাটাগরি স্লাগ লিঙ্ক এক্সট্র্যাক্ট করে """
        print("[+] DzriTV ক্যাটাগরি খুঁজছে...")
        soup = self.fetch_page_content(config.TARGET_BASE_URL)
        categories = []
        
        if not soup:
            print("[-] মূল পেজ লোড করা সম্ভব হয়নি।")
            return categories

        # ক্যাটাগরি লিঙ্ক ফিল্টারিং (মেনু ও নেভিগেশন স্লাগ থেকে)
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
                
        print(f"[✓] মোট {len(categories)} টি ক্যাটাগরি পাওয়া গেছে।")
        return categories

    def extract_stream_source(self, match_slug_url: str) -> Dict[str, Any]:
        """ নির্দিষ্ট ম্যাচের স্লাগ পেজ থেকে Embed Iframe এবং HLS .m3u8 ভিডিও স্ট্রিম এক্সট্র্যাক্ট করে """
        soup = self.fetch_page_content(match_slug_url)
        stream_data = {
            "iframe_url": None,
            "m3u8_url": None,
            "direct_embed": None
        }

        if not soup:
            return stream_data

        page_html = str(soup)

        # ১. Iframe লিঙ্ক সার্চ
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            if src and not 'facebook' in src and not 'google' in src:
                stream_data["iframe_url"] = src if src.startswith('http') else f"https:{src}"
                break

        # ২. HLS (.m3u8) এক্সট্রাকশন (Regex Pattern Matching)
        m3u8_matches = re.findall(r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)', page_html)
        if m3u8_matches:
            stream_data["m3u8_url"] = m3u8_matches[0]

        # ৩. প্লেয়ার ভিডিও সোর্স ট্যাগ এক্সট্রাকশন
        video_source = soup.find('source', type=lambda x: x and ('mpegurl' in x or 'mp4' in x))
        if video_source and video_source.get('src'):
            stream_data["direct_embed"] = video_source.get('src')

        return stream_data

    def scrape_matches_by_category(self, category: Dict[str, str]) -> List[Dict[str, Any]]:
        """ একটি নির্দিষ্ট ক্যাটাগরির সমস্ত ম্যাচ স্লাগ লিঙ্ক স্ক্র্যাপ করে """
        print(f"[+] স্ক্র্যাপ করা হচ্ছে ক্যাটাগরি: {category['name']}")
        soup = self.fetch_page_content(category['url'])
        match_list = []

        if not soup:
            return match_list

        # ম্যাচের আইটেম বা কার্ড ফিল্টার
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
            
            # ম্যাচের টাইটেল এক্সট্রাকশন
            title = link_tag.get('title') or card.text.strip()
            title = re.sub(r'\s+', ' ', title)  # অতিরিক্ত স্পেস রিমুভ

            if len(title) > 5:
                # স্লাগ পেজ এন্টার করে গভীর থেকে ভিডিও লিঙ্ক খোঁজা
                print(f"  └─ ম্যাচ পাওয়া গেছে: {title[:35]}...")
                stream_info = self.extract_stream_source(full_slug_url)

                match_list.append({
                    "title": title,
                    "category": category['name'],
                    "slug_url": full_slug_url,
                    "stream_info": stream_info
                })

        return match_list
