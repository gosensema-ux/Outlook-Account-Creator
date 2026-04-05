import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import os
import json

# --- KULLANICI BİLGİLERİ ---
MAIL_ADRESI = input("Hesap MAIL_ADRESS: ")
SIFRE_METNI = input("Hesap Şifre: ")
AD = input("Hesap AD: ")
SOYAD = input("Hesap SOYAD: ")

HESAP_TXT = "outlook_hesaplar.txt"
HESAP_JSON = "outlook_hesaplar.json"

def hesap_kaydet(email, password, ad, soyad, durum="Başarılı"):
    """Hesabı TXT ve JSON olarak kaydet"""
    
    # TXT kaydı
    with open(HESAP_TXT, "a", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write(f"E-posta: {email}\n")
        f.write(f"Şifre: {password}\n")
        f.write(f"Ad: {ad}\n")
        f.write(f"Soyad: {soyad}\n")
        f.write(f"Durum: {durum}\n")
        f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
    
    # JSON kaydı
    hesap_verisi = {
        "email": email,
        "password": password,
        "first_name": ad,
        "last_name": soyad,
        "status": durum,
        "date": datetime.now().isoformat()
    }
    
    mevcut_hesaplar = []
    if os.path.exists(HESAP_JSON):
        with open(HESAP_JSON, "r", encoding="utf-8") as f:
            try:
                mevcut_hesaplar = json.load(f)
            except:
                mevcut_hesaplar = []
    
    mevcut_hesaplar.append(hesap_verisi)
    
    with open(HESAP_JSON, "w", encoding="utf-8") as f:
        json.dump(mevcut_hesaplar, f, ensure_ascii=False, indent=2)
    
    print(f"\n[✓] Hesap kaydedildi: {HESAP_TXT}")

def click_primary_button(driver, wait):
    """'Sonraki' butonuna tıkla"""
    try:
        btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="primaryButton"]')))
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(2)
        return True
    except:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ms-Button')]//span[contains(text(), 'İleri')]")))
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(2)
            return True
        except:
            return False

def click_tamam_button(driver, wait):
    """'Tamam' butonuna tıkla - Gelişmiş yöntem"""
    time.sleep(5)  # Captcha sonrası bekleme süresini artır
    
    print("[DEBUG] Tamam butonu aranıyor...")
    
    yontemler = [
        (By.XPATH, "//span[text()='Tamam']"),
        (By.XPATH, "//span[contains(text(),'Tamam')]"),
        (By.XPATH, "//button[contains(@class, 'ms-Button')]//span[text()='Tamam']"),
        (By.CSS_SELECTOR, ".ms-Button-label"),
        (By.XPATH, "//*[@role='button']//span[text()='Tamam']"),
        (By.XPATH, "//button[contains(text(),'Tamam')]"),
        (By.ID, "id__0"),
        (By.CSS_SELECTOR, '[data-automationid="primaryButton"]'),
        (By.XPATH, "//*[contains(@class, 'button') and contains(text(),'Tamam')]"),
    ]
    
    for by, selector in yontemler:
        try:
            print(f"[DEBUG] Deneniyor: {selector}")
            btn = wait.until(EC.element_to_be_clickable((by, selector)))
            driver.execute_script("arguments[0].click();", btn)
            print("[✓] Tamam butonuna tıklandı")
            return True
        except Exception as e:
            print(f"[DEBUG] Başarısız: {e}")
            continue
    
    print("[!] Tamam butonu bulunamadı")
    return False

def wait_for_captcha_complete(driver, wait):
    """Captcha'nın tamamlanmasını bekle"""
    print("\n[INFO] Captcha çözülmesi bekleniyor...")
    print("[INFO] Captcha çözüldükten sonra sayfanın otomatik ilerlemesini bekle...")
    
    # 60 saniye boyunca URL değişimini kontrol et
    start_time = time.time()
    current_url = driver.current_url
    
    while time.time() - start_time < 60:
        time.sleep(2)
        new_url = driver.current_url
        
        # URL değiştiyse captcha geçilmiş demektir
        if new_url != current_url:
            print("[✓] Captcha başarıyla geçildi!")
            time.sleep(3)
            return True
        
        # Alternatif: Sayfada "Tamam" butonu göründü mü?
        try:
            tamam = driver.find_element(By.XPATH, "//span[text()='Tamam']")
            if tamam.is_displayed():
                print("[✓] Tamam butonu göründü!")
                return True
        except:
            pass
    
    return False

# --- TARAYICI BAŞLAT (Chrome 146 için) ---
print("\n" + "="*50)
print("CHROME 146 İÇİN TARAYICI BAŞLATILIYOR...")
print("="*50)

options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--remote-debugging-port=9222")

# Chrome 146 için driver başlat
try:
    driver = uc.Chrome(options=options, version_main=146)
    print("[✓] Chrome 146 driver başarıyla başlatıldı!")
except Exception as e:
    print(f"[!] 146 ile hata: {e}")
    print("[!] Otomatik sürüm tespiti deneniyor...")
    driver = uc.Chrome(options=options)

wait = WebDriverWait(driver, 30)

try:
    # --- ADIM 1: GOOGLE GİRİŞ (Profil ayarı için) ---
    print("\n" + "="*50)
    print("GOOGLE GİRİŞ EKRANI")
    print("="*50)

    driver.get("https://accounts.google.com/signin")
    print("Daha verimli bir hesap için lütfen giriş yap.")
    input("\nGoogle'a Giriş Yaptıktan Sonra ENTER'a bas...")

    # ---OUTLOOK KAYIT ---
    print("\n" + "="*50)
    print("OUTLOOK KAYIT EKRANI")
    print("="*50)

    driver.get("https://signup.live.com/")
    time.sleep(3)

    # ---  E-POSTA ---
    print("\n[1/5] E-posta giriliyor....")
    try:
        mail_box = wait.until(EC.element_to_be_clickable((By.NAME, "email")))
        mail_box.clear()
        mail_box.send_keys(MAIL_ADRESI)
        time.sleep(1)
        click_primary_button(driver, wait)
        print("[✓] E-posta girildi")
    except Exception as e:
        print(f"[✗] E-posta hatası: {e}")

    # --- ŞİFRE ---
    print("\n[2/5] Şifre giriliyor")
    try:
        pwd_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))
        pwd_box.clear()
        pwd_box.send_keys(SIFRE_METNI)
        time.sleep(1)
        click_primary_button(driver, wait)
        print("[✓] Şifre girildi")
    except Exception as e:
        print(f"[✗] Şifre hatası: {e}")

    # --- DOĞUM TARİHİ ---
    print("\n[3/5] Doğum tarihi giriliyor (1 Ocak 2000)...")
    try:
        # Gün
        gun = wait.until(EC.element_to_be_clickable((By.ID, "BirthDayDropdown")))
        driver.execute_script("arguments[0].click();", gun)
        time.sleep(0.5)
        gun.send_keys(Keys.ENTER)
        time.sleep(0.5)
        
        # Ay
        ay = driver.find_element(By.ID, "BirthMonthDropdown")
        driver.execute_script("arguments[0].click();", ay)
        time.sleep(0.5)
        ay.send_keys(Keys.ENTER)
        time.sleep(0.5)
        
        # Yıl
        yil = driver.find_element(By.NAME, "BirthYear")
        yil.clear()
        yil.send_keys("2000")
        time.sleep(1)
        
        click_primary_button(driver, wait)
        print("[✓] Doğum tarihi girildi")
    except Exception as e:
        print(f"[✗] Doğum tarihi hatası: {e}")

    # ---İSİM SOYİSİM ---
    print("\n[4/5] Ad ve Soyad giriliyor...")
    try:
        first_name = wait.until(EC.presence_of_element_located((By.ID, "firstNameInput")))
        first_name.clear()
        first_name.send_keys(AD)
        time.sleep(0.5)
        
        last_name = driver.find_element(By.ID, "lastNameInput")
        last_name.clear()
        last_name.send_keys(SOYAD)
        time.sleep(1)
        
        click_primary_button(driver, wait)
        print("[✓] Ad ve Soyad girildi")
    except Exception as e:
        print(f"[✗] İsim hatası: {e}")

    # --- CAPTCHA BEKLEME ---
    print("\n" + "="*50)
    print("⚠️ CAPTCHA EKRANI ⚠️")
    print("="*50)
    print("\nLütfen Captcha'yı çöz!")
    print("Captcha çözüldükten sonra sayfa otomatik ilerleyecek")
    print("Eğer 60 saniye içinde ilerlemezse manuel 'Tamam' butonuna tıkla")
    print("="*50)
    
    # Captcha'nın tamamlanmasını bekle
    captcha_passed = wait_for_captcha_complete(driver, wait)
    
    if not captcha_passed:
        print("\n[!] Otomatik ilerleme olmadı, manuel müdahale gerekli")
        input("Captcha çözüldü mü? Çözüldüyse ENTER'a bas...")
    
    # --- TAMAM BUTONU (GARANTİLİ) ---
    print("\n[5/5] 'Tamam' butonu tıklanıyor...")
    
    tamam_clicked = False
    
    # 5 kez dene, her seferinde farklı yöntemlerle
    for deneme in range(5):
        if click_tamam_button(driver, wait):
            tamam_clicked = True
            break
        print(f"[DEBUG] {deneme+1}. deneme başarısız, tekrar deneniyor...")
        time.sleep(2)
    
    if tamam_clicked:
        time.sleep(3)
        print("\n[✓] Hesap oluşturma tamamlandı!")
        hesap_kaydet(MAIL_ADRESI, SIFRE_METNI, AD, SOYAD, "Başarıyla Oluşturuldu")
    else:
        print("\n[!] Otomatik tıklama olmadı!")
        print("Lütfen manuel olarak 'Tamam' butonuna tıkla")
        input("Manuel tıkladıktan sonra ENTER'a bas...")
        hesap_kaydet(MAIL_ADRESI, SIFRE_METNI, AD, SOYAD, "Manuel tamamlandı")
    
    # --- SONUÇ ---
    print("\n" + "🎉"*30)
    print("HESAP BAŞARIYLA OLUŞTURULDU!")
    print(f"📧 E-posta: {MAIL_ADRESI}")
    print(f"🔑 Şifre: {SIFRE_METNI}")
    print(f"📁 Kayıt: {HESAP_TXT}")
    print("🎉"*30)

except Exception as e:
    print(f"\n[!] KRİTİK HATA: {e}")
    import traceback
    traceback.print_exc()
    hesap_kaydet(MAIL_ADRESI, SIFRE_METNI, AD, SOYAD, f"Hata: {str(e)[:50]}")

finally:
    input("\nKapatmak için ENTER'a bas...")
    print("Kapatılıyor...")
    for i in range(5, 0, -1):
        print(f"\r{i}...", end="", flush=True)
        time.sleep(1)
    try:
        driver.quit()
        print("\r✓ Kapatıldı!")
    except:
        print("\r[!] Zaten kapalı")
