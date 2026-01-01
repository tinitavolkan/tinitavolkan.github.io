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
    print("🚀 Tarayıcı başlatılıyor...")
    
    options = Options()
    # GitHub Actions için Headless ZORUNLU (Arayüz açılmaz)
    # Yerel test yaparken burayı yorum satırı yapabilirsin: # options.add_argument("--headless")
    options.add_argument("--headless") 
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None
    
    try:
        # Driver Başlatma
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        except:
            driver = webdriver.Chrome(options=options)

        print(f"🌐 Sayfa yükleniyor: {URL}")
        driver.get(URL)

        # Sayfanın yüklenmesini bekle
        time.sleep(5)

        # --- DEBUG: EKRAN GÖRÜNTÜSÜ AL (Video yoksa görmek için) ---
        try:
            driver.save_screenshot("rumble_debug.png")
            print("📸 Ekran görüntüsü kaydedildi: rumble_debug.png")
        except Exception as e:
            print("⚠️ Ekran görüntüsü alınamadı (Headless sunucu hatası olabilir).")
        # ---------------------------------------------------------

        # Sonsuz Kaydırma
        print("📜 Sayfayı kaydırarak daha fazla video yüklüyorum...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 10

        while scroll_attempts < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_attempts += 1

        # --- EN GARANTİ SEÇİCİ (KESİN ÇÖZÜM) ---
        # Class veya data-id'ye bakmıyoruz. Doğrudan href="/v" ile başlayan linkleri topluyoruz.
        links = driver.find_elements(By.CSS_SELECTOR, "a[href^='/v']")
        
        print(f"🔍 Bulunan '/v' ile başlayan link sayısı: {len(links)}")

        video_ids = set()

        for link in links:
            href = link.get_attribute("href")
            if href:
                # Örnek: /v73qn5i-prensesperver...
                # Regex: /v ile başlayan, tire işaretine kadar olan kısmı al.
                match = re.search(r'/v([a-z0-9]+)-', href, re.IGNORECASE)
                if match:
                    video_ids.add("v" + match.group(1))

        unique_ids = list(video_ids)
        print(f"✅ İşlenen benzersiz video sayısı: {len(unique_ids)}")

        # JSON Oluşturma
        videos_data = []
        for vid in unique_ids:
            videos_data.append({
                "id": vid,
                "embed": f"https://rumble.com/embed/{vid}/"
            })

        # Kaydetme
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(videos_data, f, indent=4, ensure_ascii=False)

        print(f"💾 {OUTPUT_FILE} güncellendi.")

    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    scrape_videos()
