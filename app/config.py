# app/config.py
from curl_cffi import requests
import time

BASE_URL = "https://v9.kuramanime.work"

HEADERS = {
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": BASE_URL,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

# Daftar "topeng" browser. Kalau satu ketahuan bot, ganti ke berikutnya!
PROFILES = ["chrome110", "chrome120", "safari15_5", "chrome101"]

def fetch_html(url, retries=2):
    """
    Mencoba beberapa profil browser secara berurutan.
    """
    for profile in PROFILES:
        session = requests.Session(impersonate=profile)
        for attempt in range(retries):
            try:
                response = session.get(url, headers=HEADERS, timeout=20)
                html = response.text
                
                # Deteksi halaman blokiran Cloudflare
                if "Just a moment..." in html or "Checking your browser" in html or "Attention Required!" in html:
                    print(f"[!] CF block ({profile}) pada {url}. Ganti topeng...")
                    time.sleep(2)
                    break # Gagal di profil ini, langsung ganti ke profil berikutnya
                    
                # Jika berhasil dapat HTML bersih
                return html
                
            except Exception as e:
                print(f"Error ({profile}): {e}")
                time.sleep(2)
                
    return None # Gagal total setelah coba semua profil