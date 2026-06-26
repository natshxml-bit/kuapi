# app/home.py
from bs4 import BeautifulSoup
from app.config import session, BASE_URL

def get_homepage():
    url = f"{BASE_URL}/"
    
    # Request pakai curl_cffi
    response = session.get(url, timeout=15)
    
    # 🕵️‍♂️ DEBUGGING: Cek apakah kena blok Cloudflare
    if response.status_code != 200 or "Just a moment..." in response.text or "Checking your browser" in response.text:
        return [], {
            "status": "BLOCKED_CLOUDFLARE",
            "status_code": response.status_code,
            "pesan": "IP Railway terdeteksi bot oleh Cloudflare.",
            "html_bukti": response.text[:300] # Potongan HTML buat buktiin
        }

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    sections = soup.find_all('section')
    
    for section in sections:
        title_tag = section.find('h4')
        if not title_tag: continue
            
        section_name = title_tag.get_text(strip=True)
        anime_items = section.select('a[href*="/anime/"]')
        
        for item in anime_items:
            div = item.find('div', class_='product__sidebar__view__item')
            if not div: continue
            
            ep_tag = div.find('div', class_='ep')
            quality_tag = div.find('div', class_='view')
            title_h5 = div.find('h5', class_='sidebar-title-h5')
            
            results.append({
                'kategori': section_name,
                'judul': title_h5.get_text(strip=True) if title_h5 else '-',
                'episode': ep_tag.get_text(strip=True) if ep_tag else '-',
                'kualitas': quality_tag.get_text(strip=True) if quality_tag else '-',
                'thumbnail': div.get('data-setbg', ''),
                'link': BASE_URL + item.get('href', '')
            })
            
    # 🕵️‍♂️ DEBUGGING: Kalau HTML berhasil dibuka tapi parsing gagal (Kuramanime ganti class)
    if not results:
        return [], {
            "status": "PARSING_ERROR",
            "status_code": response.status_code,
            "pesan": "HTML berhasil diambil, tapi struktur class HTML Kuramanime mungkin berubah.",
            "html_bukti": response.text[:500]
        }
        
    return results, None