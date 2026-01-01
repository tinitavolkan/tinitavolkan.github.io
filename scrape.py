import requests
import re
import json

# AYARLAR
RUMBLE_USER = "tinitavolkan"
URL = f"https://rumble.com/user/{RUMBLE_USER}"
OUTPUT_FILE = "videos.json"

def scrape_videos():
    print(f"🔍 {URL} adresine bağlanılıyor...")
    
    try:
        response = requests.get(URL)
        if response.status_code != 200:
            print(f"Hata: Sayfa bulunamadı. Durum kodu: {response.status_code}")
            return

        html_content = response.text
        
        # Rumble video linklerini yakalamak için Regex
        # Örnek Link: https://rumble.com/v4abc123-baslik.html
        # Grup (1) sadece ID kısmını alır: v4abc123
        video_matches = re.findall(r'rumble\.com\/(v[a-zA-Z0-9\-]+)', html_content)
        
        if not video_matches:
            print("⚠️ Video bulunamadı. Rumble HTML yapısı değişmiş olabilir veya JS ile yüklüyor.")
            return

        # Aynı videoları tekrar etmekten kaçınmak için (Set kullanımı)
        unique_ids = list(set(video_matches))
        
        # JSON formatına çevirme
        videos_data = []
        for vid in unique_ids:
            videos_data.append({
                "id": vid,
                "embed": f"https://rumble.com/embed/{vid}/"
            })

        # Dosyaya yazma
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(videos_data, f, indent=4, ensure_ascii=False)

        print(f"✅ Başarılı! {len(videos_data)} adet video {OUTPUT_FILE} dosyasına kaydedildi.")

    except Exception as e:
        print(f"❌ Bir hata oluştu: {e}")

if __name__ == "__main__":
    scrape_videos()
