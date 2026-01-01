import cloudscraper
import re
import json

# ---------------- AYARLAR ----------------
RUMBLE_USER = "tinitavolkan"
URL = f"https://rumble.com/user/{RUMBLE_USER}"
OUTPUT_FILE = "videos.json"
# ------------------------------------------

def scrape():
    print("🚀 Cloudscraper ile Rumble bağlantısı başlatılıyor (STABLE MODE)...")

    # Cloudscraper oluştur (Chrome gibi davranacak)
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows"}
    )

    try:
        # İsteği at
        r = scraper.get(URL, timeout=20)
        r.raise_for_status()
        html = r.text

        # DEBUG: Eğer hata alırsan HTML'i kontrol et
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("📸 debug.html oluşturuldu.")

        # Regex ile video ID'lerini yakala
        matches = re.findall(r'/v([a-z0-9]+)-', html, flags=re.IGNORECASE)
        
        if not matches:
            print("⚠️ Video bulunamadı. (Cloudflare koruması aşılabilmiş ama içerik boş olabilir)")
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)
            return

        unique_ids = sorted(set("v" + m for m in matches))
        print(f"✅ Bulunan video sayısı: {len(unique_ids)}")

        videos = [
            {
                "id": vid,
                "embed": f"https://rumble.com/embed/{vid}/"
            }
            for vid in unique_ids
        ]

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(videos, f, indent=4, ensure_ascii=False)

        print(f"💾 {OUTPUT_FILE} oluşturuldu.")

    except Exception as e:
        print(f"❌ Cloudscraper Hatası: {e}")

if __name__ == "__main__":
    scrape()
