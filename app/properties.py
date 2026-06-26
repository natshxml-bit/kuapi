# app/properties.py
from bs4 import BeautifulSoup
from app.config import fetch_html, BASE_URL
import re

def get_properties():
    """Mengambil daftar kategori properti (Genre, Musim, Studio, dll)"""
    url = f"{BASE_URL}/properties/genre"
    html_text = fetch_html(url)
    
    if not html_text or "Just a moment..." in html_text:
        return {"error": "Gagal mengambil halaman properties (Cloudflare/Timeout)"}

    soup = BeautifulSoup(html_text, 'html.parser')
    
    categories = []
    select_filter = soup.find('select', id='filterAnime')
    if select_filter:
        for option in select_filter.find_all('option'):
            val = option.get('value', '').replace('&amp;', '&')
            categories.append({
                'nama': option.get_text(strip=True),
                'tipe': option.get('type', 'general'),
                'url': val,
                'title': option.get('title', '')
            })
            
    items = []
    list_container = soup.find('div', class_='kuramanime__genres') or soup.find('div', id='animeList')
    if list_container:
        for li in list_container.find_all('li'):
            a_tag = li.find('a')
            if a_tag:
                span = a_tag.find('span')
                href = a_tag.get('href', '').strip().replace('&amp;', '&')
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
    Contoh url_path: "/quick/ongoing", "/anime", "/properties/genre/action"
    """
    url = f"{BASE_URL}{url_path}"
    if page > 1:
        separator = "&" if "?" in url else "?"
        url += f"{separator}page={page}"
        
    html_text = fetch_html(url)
    if not html_text or "Just a moment..." in html_text:
        return {"error": "Gagal mengambil list anime (Cloudflare/Timeout)"}

    soup = BeautifulSoup(html_text, 'html.parser')
    animes = []
    seen_slugs = set() # Cegah anime duplikat
    
    # Cari semua link yang polanya /anime/{id}/{slug}
    links = soup.find_all('a', href=re.compile(r'/anime/\d+/[a-z0-9\-]+'))
    
    for a in links:
        href = a.get('href', '')
        # Extract SLUG (Contoh: dari /anime/4862/snowball-earth/episode/1 -> 4862/snowball-earth)
        match = re.search(r'/anime/(\d+/[a-z0-9\-]+)', href)
        if match:
            slug = match.group(1)
            if slug not in seen_slugs:
                seen_slugs.add(slug)
                
                # Cari Judul & Thumbnail
                item_div = a.find('div', class_=re.compile(r'product__.*item|anime__card|set-bg'))
                judul = '-'
                thumbnail = ''
                
                if item_div:
                    thumbnail = item_div.get('data-setbg', '')
                    title_tag = item_div.find('h5') or item_div.find('h4') or item_div.find('h3')
                    if title_tag:
                        judul = title_tag.get_text(strip=True)
                
                # Fallback judul kalau nggak ada di div
                if judul == '-':
                    judul = a.get('title', '') or a.get_text(strip=True)
                        
                animes.append({
                    'slug': slug,
                    'judul': judul,
                    'thumbnail': thumbnail,
                    'detail_url': f"{BASE_URL}/anime/{slug}"
                })
                
    return {
        'url_path': url_path,
        'page': page,
        'total': len(animes),
        'data': animes
    }