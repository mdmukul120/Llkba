import os
from io import BytesIO
from PIL import Image as PILImage, ImageDraw, ImageFont
from willow import Image
import config

class PremiumBannerGenerator:
    """
    Willow এবং PIL ব্যবহার করে ডায়নামিক ম্যাচ ব্যানার তৈরির ক্লাস
    """
    
    def __init__(self):
        self.width = config.BANNER_WIDTH
        self.height = config.BANNER_HEIGHT

    def _create_gradient_background(self) -> PILImage.Image:
        base_img = PILImage.new('RGB', (self.width, self.height), config.BG_PRIMARY_COLOR)
        draw = ImageDraw.Draw(base_img)
        
        # প্যানেল বর্ডার ও ডিজাইন
        padding = 30
        draw.rectangle(
            [padding, padding, self.width - padding, self.height - padding],
            outline=config.ACCENT_COLOR,
            width=3
        )
        
        draw.polygon(
            [(self.width - 300, 0), (self.width, 0), (self.width, self.height), (self.width - 450, self.height)],
            fill=config.BG_SECONDARY_COLOR
        )
        
        return base_img

    def generate_banner(self, match_title: str, category: str, output_path: str) -> str:
        try:
            pil_img = self._create_gradient_background()
            draw = ImageDraw.Draw(pil_img)
            
            try:
                title_font = ImageFont.truetype("arial.ttf", 46)
                badge_font = ImageFont.truetype("arial.ttf", 28)
                footer_font = ImageFont.truetype("arial.ttf", 22)
            except IOError:
                title_font = badge_font = footer_font = ImageFont.load_default()

            # ক্যাটাগরি ব্যাজ
            badge_text = f"  {category.upper()} - LIVE MATCH  "
            draw.rectangle([60, 60, 420, 110], fill=config.ACCENT_COLOR)
            draw.text((70, 72), badge_text, fill=(0, 0, 0), font=badge_font)

            # শিরোনাম রেন্ডার করা
            words = match_title.split()
            line1, line2 = "", ""
            for word in words:
                if len(line1 + " " + word) < 25:
                    line1 += " " + word
                else:
                    line2 += " " + word

            draw.text((60, 200), line1.strip(), fill=config.TEXT_WHITE, font=title_font)
            if line2:
                draw.text((60, 260), line2.strip(), fill=config.TEXT_WHITE, font=title_font)

            # ব্র্যান্ডিং ট্যাগ
            draw.ellipse([60, 485, 80, 505], fill=(239, 68, 68))
            draw.text((95, 482), "STREAMING NOW ON DZRITV", fill=config.TEXT_MUTED, font=footer_font)

            # Willow প্রসেসিং
            buffer = BytesIO()
            pil_img.save(buffer, format='PNG')
            buffer.seek(0)

            willow_image = Image.open(buffer)
            willow_image.save_as_png(output_path)
            return output_path

        except Exception as e:
            print(f"[-] ব্যানার তৈরি করতে সমস্যা হয়েছে: {e}")
            return ""
