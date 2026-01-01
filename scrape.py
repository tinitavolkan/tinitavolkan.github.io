import requests
import re
import json

# AYARLAR
RUMBLE_USER = "tinitavolkan"
URL = f"https://rumble.com/user/{RUMBLE_USER}"
OUTPUT_FILE = "videos.json"

def scrape_videos():
    # Başlığı ayarlayalım (Tarayıcı gibi görünmesi için)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"🔍 {URL} adresine bağlanılıyor...")
    
    try:
        # Başlık (Header) ile istek gönderiyoruz
        response = requests.get(URL, headers=headers)
        
        if response.status_code != 200:
            print(f"Hata: Sayfa bulunamadı. Durum kodu: {response.status_code}")
            print("HTML İçeriği (ilk 500 karakter):", response.text[:500])
            return

        html_content = response.text
        
        # Daha geniş Regex:
        # 1. rumble.com/vID.html yakalar
        # 2. Sadece /vID.html (bağıl link) yakalar
        # 3. JSON yapısı içindeki "url":"..." yakalar
        
        # Önce standart linkleri dene
        video_matches = re.findall(r'rumble\.com\/(v[a-zA-Z0-9\-]+)\.html', html_content)
        
        # Eğer bulamazsa, sadece başına / işareti olanları dene
        if not video_matches:
            video_matches = re.findall(r'\/(v[a-zA-Z0-9\-]+)\.html', html_content)

        # Hala yoksa, ID'yi basitçe yakalamayı dene (v ile başlayan her şey)
        if not video_matches:
            video_matches = re.findall(r'[^a-z](v[a-z0-9]+)', html_content)

        print(f"🔍 Regex buldu: {len(video_matches)} adet ham ID.")

        if not video_matches:
            print("⚠️ Video bulunamadı.")
            print("SAYFANIN İLK 1000 KARAKTERİNE BAK:")
            print(html_content[:1000])
            return

        # Aynı videoları temizle (Set kullanarak)
        # Rumble'da ID'ler 'v' ile başlar. Eğer yanlış yakaladıysak 'v' ile başlayanları filtreleyelim.
        valid_videos = [v for v in video_matches if v.startswith('v')]
        unique_ids = list(set(valid_videos))
        
        print(f"✅ Temizlenmiş benzersiz video sayısı: {len(unique_ids)}")

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

        print(f"✅ {OUTPUT_FILE} dosyasına {len(videos_data)} video kaydedildi.")

    except Exception as e:
        print(f"❌ Bir hata oluştu: {e}")

if __name__ == "__main__":
    scrape_videos()
