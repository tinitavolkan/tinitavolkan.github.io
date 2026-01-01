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
    print("🚀 Tarayıcı başlatılıyor...")
    
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = None
    
    try:
        # Driver Başlat
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        except:
            driver = webdriver.Chrome(options=options)

        print(f"🌐 Sayfa yükleniyor: {URL}")
        driver.get(URL)

        # 1. BEKLEME: Videoların yüklenmesini bekle (sınıfa göre bekle)
        # Senin verdiğin "videostream__link" sınıfının göründüğünü teyit et
        print("⏳ Videoların yüklenmesini bekliyorum...")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "videostream__link"))
            )
        except:
            print("⚠️ Uyarı: 'videostream__link' sınıfı bulunamadı, sayfa yapısı değişmiş olabilir.")

        # 2. SCROLL (Kaydırma): Rumble sonsuz kaydırma kullanır.
        # Sayfayı aşağı indikçe yeni videolar yüklenir.
        print("📜 Sayfayı aşağı kaydırarak daha fazla video yüklüyorum...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        scroll_count = 0
        max_scrolls = 10  # En fazla 10 kez aşağı indir (yaklaşık 30-50 video bulur, Actions limiti için önemli)

        while scroll_count < max_scrolls:
            # En aşağı kaydır
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Yüklemesi için bekle
            time.sleep(2)
            
            # Yeni yüksekliği ölç
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                # Yükseklik değişmediyse, sayfa bitti demektir.
                print("✅ Sayfa sonuna gelindi.")
                break
            
            last_height = new_height
            scroll_count += 1
            print(f"   ...Kaydırma {scroll_count}/{max_scrolls}")

        # 3. TOPLAMA: Artık sadece video linklerini hedefle
        video_links = set()
        
        # "videostream__link" sınıfına sahip tüm elementleri bul
        # (Bunu senin verdiğin elementteki class="videostream__link link" yapısından biliyoruz)
        elements = driver.find_elements(By.CLASS_NAME, "videostream__link")
        
        print(f"🔍 Toplam {len(elements)} adet video linki elementi bulundu.")

        for elem in elements:
            href = elem.get_attribute("href")
            if href:
                # Senin verdiğin link: /v73qn5i-prensesperver...
                # Regex ile /v ile başlayan ID'yi yakala
                match = re.search(r'/v([a-z0-9]+)', href, re.IGNORECASE)
                
                if match:
                    video_id = "v" + match.group(1) # Başına v ekle (regex v'siz alıyor)
                    video_links.add(video_id)

        unique_ids = list(video_links)
        print(f"✅ {len(unique_ids)} adet benzersiz video ID'si işlendi.")

        # JSON'a yaz
        videos_data = []
        for vid in unique_ids:
            videos_data.append({
                "id": vid,
                "embed": f"https://rumble.com/embed/{vid}/"
            })

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(videos_data, f, indent=4, ensure_ascii=False)

        print(f"💾 Başarıyla tamamlandı. {OUTPUT_FILE} güncellendi.")

    except Exception as e:
        print(f"❌ Kritik Hata: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    scrape_videos()
