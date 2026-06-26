# app/properties.py
from bs4 import BeautifulSoup
from app.config import fetch_html, BASE_URL
import re
import html

def _is_blocked(html_text):
    """Cek apakah HTML hasil fetch itu halaman blokiran Cloudflare"""
    if not html_text:
        return True
    block_signs = [
        "Just a moment...", 
        "Checking your browser", 
        "Attention Required!",
        "Enable JavaScript",
        "DDoS protection"
    ]
    return any(sign in html_text for sign in block_signs)

def get_properties():
    """
    Mengambil daftar kategori properti (Genre, Musim, Studio, dll)
    dari halaman /properties/genre
    """
    url = f"{BASE_URL}/properties/genre"
    html_text = fetch_html(url)
    
    # 🕵️‍♂️ DEBUG: Kalau gagal total / kena blok
    if _is_blocked(html_text):
        return {
            "error": "Halaman /properties/genre diblokir Cloudflare atau timeout.",
            "debug_html": (html_text or "")[:500]
        }

    soup = BeautifulSoup(html_text, 'html.parser')
    
    # 1. Ambil Kategori Filter (Dropdown)
    categories = []
    select_filter = soup.find('select', id='filterAnime')
    if select_filter:
        for option in select_filter.find_all('option'):
            val = html.unescape(option.get('value', '')) # Decode &amp;
            categories.append({
                'nama': option.get_text(strip=True),
                'tipe': option.get('type', 'general'),
                'url': val,
                'title': option.get('title', '')
            })
            
    # 2. Ambil List Detail Properti (A-Z Genre / Musim / dll)
    items = []
    list_container = (
        soup.find('div', class_='kuramanime__genres') or 
        soup.find('div', id='animeList')
    )
    if list_container:
        for li in list_container.find_all('li'):
            a_tag = li.find('a')
            if a_tag:
                span = a_tag.find('span')
                href = html.unescape(a_tag.get('href', '')).strip()
                items.append({
                    'nama': span.get_text(strip=True) if span else a_tag.get_text(strip=True),
                    'url': href
                })
                
    return {
        'halaman_saat_ini': 'Daftar Properti Anime',
        'kategori_filter': categories,
        'daftar_properti': items
    }


def get_anime_list(url_path, page=1):
    """
    Mengambil daftar anime dari halaman list / genre dan mengekstrak SLUG-nya.
    
    Contoh url_path: 
    - /quick/ongoing (Sedang Tayang)
    - /quick/finished (Selesai Tayang)
    - /quick/movie (Film Layar Lebar)
    - /properties/genre/action (Anime berdasarkan genre)
    """
    url = f"{BASE_URL}{url_path}"
    if page > 1:
        separator = "&" if "?" in url else "?"
        url += f"{separator}page={page}"
        
    html_text = fetch_html(url)
    
    # 🕵️‍♂️ DEBUG: Kalau gagal total / kena blok
    if _is_blocked(html_text):
        return {
            "error": f"Gagal mengambil list anime di {url_path}. Diblokir/Timeout.",
            "debug_html": (html_text or "")[:500]
        }

    soup = BeautifulSoup(html_text, 'html.parser')
    animes = []
    seen_slugs = set() # Cegah anime duplikat
    
    # Regex untuk cari link dengan pola /anime/{id}/{slug}
    pattern = re.compile(r'/anime/(\d+/[a-z0-9\-]+)')
    links = soup.find_all('a', href=pattern)
    
    for a in links:
        href = a.get('href', '')
        match = pattern.search(href)
        if match:
            slug = match.group(1)
            if slug not in seen_slugs:
                seen_slugs.add(slug)
                
                # Cari Judul & Thumbnail dari div pembungkus
                item_div = a.find('div', class_=re.compile(r'product__.*item|anime__card|set-bg'))
                judul = '-'
                thumbnail = ''
                episode = '-'
                kualitas = '-'
                
                if item_div:
                    thumbnail = item_div.get('data-setbg', '')
                    title_tag = item_div.find('h5') or item_div.find('h4') or item_div.find('h3')
                    if title_tag:
                        judul = title_tag.get_text(strip=True)
                    
                    # Ambil info episode & kualitas (kalau ada di card)
                    ep_tag = item_div.find('div', class_='ep')
                    if ep_tag:
                        episode = ep_tag.get_text(strip=True)
                        
                    quality_tag = item_div.find('div', class_='view')
                    if quality_tag:
                        kualitas = quality_tag.get_text(strip=True)
                
                # Fallback judul
                if judul == '-':
                    judul = a.get('title', '') or a.get_text(strip=True)
                        
                animes.append({
                    'slug': slug,
                    'judul': judul,
                    'episode': episode,
                    'kualitas': kualitas,
                    'thumbnail': thumbnail,
                    'detail_url': f"{BASE_URL}/anime/{slug}"
                })
                
    return {
        'url_path': url_path,
        'page': page,
        'total': len(animes),
        'data': animes
    }