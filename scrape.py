import requests
import re
import json

# AYARLAR
RUMBLE_USER = "tinitavolkan"
URL = f"https://rumble.com/user/{RUMBLE_USER}"
OUTPUT_FILE = "videos.json"

def scrape_videos():
    # Tarayıcı gibi görün
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"🔍 {URL} adresine bağlanılıyor...")
    
    try:
        response = requests.get(URL, headers=headers)
        
        if response.status_code != 200:
            print(f"Hata: Sayfa bulunamadı. Durum kodu: {response.status_code}")
            return

        html_content = response.text
        
        # DÜZELTİLMİŞ REGEX
        # 1. rumble.com/ ile başlar
        # 2. (v[a-z0-9]+) -> Grubu yakalar (Sadece v ile başlayan sayı/harf dizisi, örn: v73qci0)
        # 3. (?=-|\.|\?|") -> Bakış açısı (Lookahead): Sonra tire, nokta, soru işareti veya tırnak varsa dur.
        # Bu sayede başlık kısmını (egearseven-...) almaz.
        
        # Bu pattern: rumble.com/v73qci0-... veya rumble.com/v73qci0.html... yakalar
        pattern = r'rumble\.com\/(v[a-z0-9]+)(?=-|\.|\?|")'
        
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        
        print(f"🔍 Regex buldu: {len(matches)} adet ID.")

        if not matches:
            print("⚠️ ID bulunamadı. Sayfa kaynağı farklı olabilir.")
            return

        # Listeyi tekilleştir
        unique_ids = list(set(matches))
        print(f"✅ Tekrar edenler temizlendi, kalan: {len(unique_ids)}")

        # JSON formatına çevir
        videos_data = []
        for vid in unique_ids:
            videos_data.append({
                "id": vid,
                "embed": f"https://rumble.com/embed/{vid}/"
            })

        # Dosyaya yaz
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(videos_data, f, indent=4, ensure_ascii=False)

        print(f"✅ {OUTPUT_FILE} dosyasına {len(videos_data)} video yazıldı.")

    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    scrape_videos()
