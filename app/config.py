# app/config.py
from curl_cffi import requests
import time

BASE_URL = "https://v9.kuramanime.work"

# Header palsu agar dikira browser Chrome Windows asli
HEADERS = {
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": BASE_URL,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="110", "Chromium";v="110"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

def fetch_html(url, retries=2):
    """
    Fungsi pintar untuk ambil HTML. 
    Pakai chrome110 (lebih stabil bypass CF) dan auto-retry kalau gagal.
    """
    session = requests.Session(impersonate="chrome110")
    
    for attempt in range(retries):
        try:
            response = session.get(url, headers=HEADERS, timeout=20)
            html = response.text
            
            # Cek apakah kena halaman "Just a moment..."
            if "Just a moment..." in html or "Checking your browser" in html:
                print(f"[!] Cloudflare block terdeteksi pada percobaan ke-{attempt+1}. Menunggu 3 detik...")
                time.sleep(3)
                continue # Coba lagi
                
            return html
            
        except Exception as e:
            print(f"Request error: {e}")
            time.sleep(2)
            
    return None # Return None kalau gagal total setelah retry