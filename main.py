import json
import re
from datetime import datetime
import config
from scraper import DzriTVScraper
from banner_generator import PremiumBannerGenerator

def sanitize_filename(name: str) -> str:
    """ ফাইলের জন্য নিরাপদ নাম জেনারেট করে """
    clean_name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    return re.sub(r'[-\s]+', '_', clean_name)[:30]

def main():
    print("==================================================")
    print("        DzriTV Advanced Scraper Engine            ")
    print("==================================================")

    scraper = DzriTVScraper()
    banner_gen = PremiumBannerGenerator()
    
    all_processed_data = []

    # ১. সকল ক্যাটাগরি কালেকশন
    categories = scraper.get_all_categories()

    # যদি ক্যাটাগরি সরাসরি না পাওয়া যায়, তবে ডিফল্ট লিঙ্ক ব্যবহার করা
    if not categories:
        categories = [{"name": "Live Sports", "url": config.TARGET_BASE_URL}]

    # ২. প্রতি ক্যাটাগরি অনুযায়ী ম্যাচ স্ক্র্যাপিং ও ইমেজ জেনারেট
    for cat in categories:
        matches = scraper.scrape_matches_by_category(cat)
        
        for match in matches:
            # ইউনিক ইমেজ ফাইল নাম
            file_slug = sanitize_filename(match['title'])
            image_filename = f"{file_slug}_{datetime.now().strftime('%H%M%S')}.png"
            image_path = config.IMAGE_OUTPUT_DIR / image_filename

            # Willow ব্যানার তৈরি
            print(f"     └─ [Willow] ব্যানার তৈরি হচ্ছে: {image_filename}")
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
                "video_streams": match['stream_info'],
                "banner_image": str(generated_img_path),
                "timestamp": datetime.now().isoformat()
            }
            
            all_processed_data.append(match_entry)

    # ৩. ফলাফল JSON ফাইলে সংরক্ষণ
    print("\n[+] JSON ফাইল আপডেট করা হচ্ছে...")
    with open(config.JSON_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_processed_data, f, ensure_ascii=False, indent=4)

    print(f"[✓] প্রসেস সফলভাবে সম্পন্ন হয়েছে!")
    print(f"[✓] মোট ম্যাচ প্রসেস করা হয়েছে: {len(all_processed_data)}")
    print(f"[✓] ডাটা আউটপুট ফাইল: {config.JSON_OUTPUT_FILE}")
    print("==================================================")

if __name__ == "__main__":
    main()
