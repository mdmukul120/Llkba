import json
import re
from datetime import datetime
import config
from scraper import DzriTVScraper
from banner_generator import PremiumBannerGenerator

def sanitize_filename(name: str) -> str:
    clean_name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    return re.sub(r'[-\s]+', '_', clean_name)[:30]

def main():
    print("==================================================")
    print("        DzriTV Advanced Scraper Engine            ")
    print("==================================================")

    scraper = DzriTVScraper()
    banner_gen = PremiumBannerGenerator()
    
    all_processed_data = []

    categories = scraper.get_all_categories()
    if not categories:
        categories = [{"name": "Live Sports", "url": config.TARGET_BASE_URL}]

    for cat in categories:
        matches = scraper.scrape_matches_by_category(cat)
        
        for match in matches:
            file_slug = sanitize_filename(match['title'])
            image_filename = f"{file_slug}_{datetime.now().strftime('%H%M%S')}.png"
            image_path = config.IMAGE_OUTPUT_DIR / image_filename

            print(f" [+] [Willow] ব্যানার তৈরি হচ্ছে: {image_filename}")
            generated_img_path = banner_gen.generate_banner(
                match_title=match['title'],
                category=match['category'],
                output_path=str(image_path)
            )

            match_entry = {
                "id": file_slug,
                "title": match['title'],
                "category": match['category'],
                "slug_url": match['slug_url'],
                "iframe_url": match['iframe_url'],
                "embed_code": match['embed_code'],
                "banner_image": str(generated_img_path),
                "timestamp": datetime.now().isoformat()
            }
            
            all_processed_data.append(match_entry)

    print("\n[+] JSON ফাইল সেভ করা হচ্ছে...")
    with open(config.JSON_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_processed_data, f, ensure_ascii=False, indent=4)

    print(f"[✓] প্রসেস সফলভাবে সম্পন্ন হয়েছে! মোট ম্যাচ: {len(all_processed_data)}")
    print("==================================================")

if __name__ == "__main__":
    main()
