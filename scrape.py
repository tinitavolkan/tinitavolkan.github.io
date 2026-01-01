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
    print("🚀 Selenium Başlatılıyor...")
    
    options = Options()
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

        print(f"🌐 Sayfa Yükleniyor: {URL}")
        driver.get(URL)

        # 1. Önce biraz bekle (JS yüklenmesi için)
        time.sleep(5)

        # 2. "Accept Cookies" (Çerez) varsa tıkla (Rumble bazen bunu gösteriyor)
        try:
            # Yaygın çerez butonu seçicileri
            driver.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'I Agree') or contains(@class, 'accept')]").click()
            print("🍪 Çerez butonu bulundu ve tıklandı.")
            time.sleep(2)
        except:
            print("ℹ️ Çerez ekranı görünmüyor veya gerekli değil.")

        # 3. Sonsuz Kaydırma (Scroll) - Videoları yükle
        print("📜 Sayfa kaydırılıyor (Videolar yükleniyor)...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        scroll_attempts = 0
        max_scrolls = 10 # 10 kere aşağı in (yaklaşık 30-50 video)

        while scroll_attempts < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) # Yükleme süresi
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("✅ Sayfa sonuna gelindi.")
                break
            last_height = new_height
            scroll_attempts += 1
            print(f"   Kaydırma: {scroll_attempts}")

        # 4. VERİ ÇEKME (En Kritik Kısım)
        video_ids = set()

        # Verdiğin HTML'deki "data-video-id" özelliğini hedefliyoruz.
        # Bu yapı sınıf ismi değişse bile çalışır.
        containers = driver.find_elements(By.CSS_SELECTOR, "div[data-video-id]")
        
        print(f"🔍 Toplam video konteyneri bulundu: {len(containers)}")

        for container in containers:
            try:
                # Konteynerin içindeki video linkini bul
                # Verdiğin HTML'de: <a class="videostream__link link" ...>
                link_elem = container.find_element(By.CSS_SELECTOR, "a.videostream__link")
                href = link_elem.get_attribute("href")
                
                if href:
                    # Örnek Link: /v73qn5i-prensesperver...
                    # Regex: /v ile başlayan, tire işaretine kadar olan kısmı al.
                    # Grup (1): v73qn5i
                    match = re.search(r'/v([a-z0-9]+)-', href, re.IGNORECASE)
                    
                    if match:
                        video_id = "v" + match.group(1) # Regex v'yi almazsa, başına koy
                        video_ids.add(video_id)

            except Exception as e:
                # Bazı konteynerlerde link yoksa hata verme, geç
                pass

        unique_ids = list(video_ids)
        print(f"✅ Başarıyla işlenen benzersiz video sayısı: {len(unique_ids)}")

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

        print(f"💾 {OUTPUT_FILE} başarıyla güncellendi.")

    except Exception as e:
        print(f"❌ Kritik Hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    scrape_videos()
