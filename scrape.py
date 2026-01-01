import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# AYARLAR
RUMBLE_USER = "tinitavolkan"
URL = f"https://rumble.com/user/{RUMBLE_USER}"
OUTPUT_FILE = "videos.json"

def scrape_videos():
    print("🚀 Tarayıcı (Selenium) başlatılıyor...")
    
    # Chrome Ayarları (GitHub Actions üzerinde çalışması için kritik)
    options = Options()
    options.add_argument("--headless")  # Arayüzü açma (arka planda çalış)
    options.add_argument("--no-sandbox") # Güvenlik modunu kapat
    options.add_argument("--disable-dev-shm-usage") # Bellek hatası önleme
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None
    
    try:
        # Tarayıcıyı başlat
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        print(f"🌐 Sayfa yükleniyor: {URL}")
        driver.get(URL)

        # Sayfanın tam yüklenmesini ve videoların gelmesini beklemek için zaman tanı
        # WebDriverWait ile bir video linki görünene kadar bekleyebiliriz ama 5-10 saniye yeterli
        time.sleep(5) 

        # Tüm linkleri bul
        video_links = set()
        
        # 1. Yöntem: Tüm <a> tag'lerini tara
        elements = driver.find_elements(By.TAG_NAME, "a")
        
        for elem in elements:
            href = elem.get_attribute("href")
            if href:
                # Linkin Rumble video ID'si içerip içermediğini kontrol et
                # Örnek: rumble.com/v73qci0-...
                if "rumble.com/v" in href:
                    # ID'yi çek: rumble.com/ID'den sonraki kısmı al
                    # regex: rumble.com/(v......)
                    match = re.search(r'rumble\.com\/(v[a-z0-9\-]+)(?=\?|\.|$)', href, re.IGNORECASE)
                    if match:
                        video_id = match.group(1)
                        # Sadece başında 'v' olanları al, tireli uzun ID'leri temizle (opsiyonel ama güvenli)
                        if video_id.startswith('v'):
                            video_links.add(video_id)

        # Set'i listeye çevir
        unique_ids = list(video_links)
        print(f"✅ Tarayıcıda {len(unique_ids)} video bulundu.")

        # JSON oluşturma
        videos_data = []
        for vid in unique_ids:
            videos_data.append({
                "id": vid,
                "embed": f"https://rumble.com/embed/{vid}/"
            })

        # Kaydet
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(videos_data, f, indent=4, ensure_ascii=False)

        print(f"💾 {OUTPUT_FILE} başarıyla güncellendi.")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        # Ekran görüntüsü alıp debug edebilirdik ama şimdilik log yeterli
    finally:
        if driver:
            driver.quit()
            print("🔚 Tarayıcı kapatıldı.")

if __name__ == "__main__":
    scrape_videos()
