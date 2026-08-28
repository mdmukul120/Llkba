import os
from pathlib import Path

# --- প্রজেক্টের গ্লোবাল পাথ কনফিগারেশন ---
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
IMAGE_OUTPUT_DIR = OUTPUT_DIR / "banners"
JSON_OUTPUT_FILE = OUTPUT_DIR / "live_matches.json"

# ফোল্ডার ডিরেক্টরি স্বয়ংক্রিয়ভাবে তৈরি করা
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- ওয়েব স্ক্র্যাপার কনফিগারেশন ---
TARGET_BASE_URL = "https://dzritv.com"
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3

# প্রিমিয়াম ব্রাউজার রিকোয়েস্ট হেডার
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
    "Referer": TARGET_BASE_URL,
}

# --- ব্যানার ডিজাইন কনফিগারেশন ---
BANNER_WIDTH = 1200
BANNER_HEIGHT = 630
BG_PRIMARY_COLOR = (15, 23, 42)      # ডার্ক ব্লু থিম
BG_SECONDARY_COLOR = (30, 41, 59)    # সেকেন্ডারি শেড
ACCENT_COLOR = (234, 179, 8)         # গোল্ডেন অ্যাকসেন্ট
TEXT_WHITE = (255, 255, 255)         # প্রাইমারি টেক্সট
TEXT_MUTED = (148, 163, 184)        # সেকেন্ডারি টেক্সট
