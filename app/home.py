# app/home.py
from bs4 import BeautifulSoup
from app.config import fetch_html, BASE_URL

def get_homepage():
    url = f"{BASE_URL}/"
    html = fetch_html(url)
    
    # Kalau fetch_html return None atau masih kena blok CF
    if not html:
        return [], {"status": "FETCH_FAILED", "pesan": "Gagal mengambil HTML (Timeout/Blokir)."}
        
    if "Just a moment..." in html:
        return [], {
            "status": "BLOCKED_CLOUDFLARE",
            "pesan": "Masih diblokir Cloudflare. Solusi: Wajib deploy Flaresolverr di Railway.",
            "html_bukti": html[:200]
        }

    soup = BeautifulSoup(html, 'html.parser')
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
            
            link_href = item.get('href', '')
            full_link = BASE_URL + link_href if link_href.startswith('/') else link_href
            
            results.append({
                'kategori': section_name,
                'judul': title_h5.get_text(strip=True) if title_h5 else '-',
                'episode': ep_tag.get_text(strip=True) if ep_tag else '-',
                'kualitas': quality_tag.get_text(strip=True) if quality_tag else '-',
                'thumbnail': div.get('data-setbg', ''),
                'link': full_link
            })
            
    if not results:
         return [], {
            "status": "PARSING_ERROR",
            "pesan": "HTML berhasil dibuka, tapi struktur class HTML Kuramanime mungkin berubah.",
            "html_bukti": html[:300]
        }
        
    return results, None