import requests
import re
import json

# ---------------- AYARLAR ----------------
RUMBLE_USER = "tinitavolkan"

# ✅ KESİN ÇÖZÜM: Mobil alt alan adını kullanıyoruz
# Böylece GitHub Actions IP'leri engellenmez ve linkler çıplak gelir.
URL = f"https://m.rumble.com/user/{RUMBLE_USER}"

OUTPUT_FILE = "videos.json"

HEADERS = {
    # Mobil User-Agent kullanıyoruz (daha doğal görünür)
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    )
}
# ------------------------------------------

def scrape_rumble_videos():
    print("🌐 Mobil site bağlantısı kuruluyor (requests)...")
    
    try:
        r = requests.get(URL, headers=HEADERS, timeout=15)
        r.raise_for_status()
        html = r.text

        # Mobil sitede link yapısı genellikle /v... şeklindedir.
        # Regex araması yap.
        matches = re.findall(r'/v([a-z0-9]+)-', html, flags=re.IGNORECASE)
        
        if not matches:
            print("⚠️ Uyarı: Mobil sitede bile video bulunamadı.")
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)
            return

        # ID'leri temizle ve listeye ekle
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
