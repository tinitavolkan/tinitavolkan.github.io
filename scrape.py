import requests
import re
import json

# ---------------- AYARLAR ----------------
RUMBLE_USER = "tinitavolkan"
URL = f"https://rumble.com/user/{RUMBLE_USER}"
OUTPUT_FILE = "videos.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
# ------------------------------------------

def scrape_rumble_videos():
    print("🌐 Sayfa çekiliyor (Requests - Çok Hızlı)...")
    
    try:
        r = requests.get(URL, headers=HEADERS, timeout=15)
        r.raise_for_status() # Eğer sayfa 404 verirse hata fırlat
        html = r.text

        # 🔥 Regex ile /v... ile başlayan linkleri bul
        matches = re.findall(r'/v([a-z0-9]+)-', html, flags=re.IGNORECASE)
        
        if not matches:
            print("⚠️ Uyarı: Hiç video bulunamadı. Link yapısı değişmiş olabilir.")
            # Yine de boş dosya oluşturalım ki hata vermesin
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)
            return

        # Set ile tekrarları kaldır ve "v" öneki ekleyerek listeye çevir
        unique_ids = sorted(set("v" + m for m in matches))
        print(f"✅ Bulunan benzersiz video sayısı: {len(unique_ids)}")

        videos = [
            {
                "id": vid,
                "embed": f"https://rumble.com/embed/{vid}/"
            }
            for vid in unique_ids
        ]

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(videos, f, indent=4, ensure_ascii=False)

        print(f"💾 {OUTPUT_FILE} başarıyla oluşturuldu.")

    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    scrape_rumble_videos()
