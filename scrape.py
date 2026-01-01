import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# AYARLAR
RUMBLE_USER = "tinitavolkan"
URL = f"https://rumble.com/user/{RUMBLE_USER}"
OUTPUT_FILE = "videos.json"

def scrape_videos():
    print("🚀 Tarayıcı (Selenium) başlatılıyor...")
    
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None
    
    try:
        # WebDriver Manager kullanarak driver'ı otomatik indirmeye çalışıyoruz
        # Eğer bu satır hata verirse, alttaki basit yönteme geçeceğiz
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        except Exception:
            # Yöntem 2: Direkt kullan (GitHub Actions'ta zaten yüklü gelebilir)
            driver = webdriver.Chrome(options=options)

        print(f"🌐 Sayfa yükleniyor: {URL}")
        driver.get(URL)

        # Sayfanın yüklenmesini bekle
        time.sleep(5) 

        video_links = set()
        elements = driver.find_elements(By.TAG_NAME, "a")
        
        print(f"🔍 Toplam {len(elements)} adet link tarandı...")

        for elem in elements:
            href = elem.get_attribute("href")
            
            # Eğer href boşsa atla
            if not href:
                continue
            
            # --- KRİTİK DEĞİŞİKLİK ---
            # Link içinde "rumble.com" geçse de geçmese de, 
            # sadece video ID'si (/v...) ile başlayanları yakala.
            # Regex: Bir slash (/), ardından v, ardından harf/rakam. Sonrası önemli değil.
            match = re.search(r'\/(v[a-z0-9]+)', href, re.IGNORECASE)
            
            if match:
                video_id = match.group(1)
                # Eğer ID 'v' ile başlıyorsa listeye ekle
                if video_id.startswith('v'):
                    video_links.add(video_id)

        unique_ids = list(video_links)
        print(f"✅ Toplam {len(unique_ids)} adet benzersiz video ID'si bulundu.")

        # Eğer hala boşsa, debug için sayfa kaynağının ilk 1000 karakterini yazdır
        if not unique_ids:
            print("⚠️ Hiç video bulunamadı. Sayfa kaynağına bakılıyor...")
            page_source = driver.page_source
            print("KAYNAK KOD KISMI:", page_source[:1000])

        videos_data = []
        for vid in unique_ids:
            videos_data.append({
                "id": vid,
                "embed": f"https://rumble.com/embed/{vid}/"
            })

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(videos_data, f, indent=4, ensure_ascii=False)

        print(f"💾 {OUTPUT_FILE} dosyasına {len(videos_data)} video kaydedildi.")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    scrape_videos()
