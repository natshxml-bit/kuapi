# app/detail.py
from bs4 import BeautifulSoup
from app.config import fetch_html, BASE_URL
import html

def get_detail(slug):
    url = f"{BASE_URL}/anime/{slug}"
    html_text = fetch_html(url)
    
    if not html_text or "Just a moment..." in html_text:
        return {"error": "Gagal mengambil detail (Cloudflare/Timeout)"}

    soup = BeautifulSoup(html_text, 'html.parser')
    
    # 1. Info Dasar (Judul, Skor, Thumbnail, Sinopsis)
    title_tag = soup.find('div', class_='anime__details__title')
    judul = title_tag.find('h3').get_text(strip=True) if title_tag and title_tag.find('h3') else '-'
    judul_alt = title_tag.find('span').get_text(strip=True) if title_tag and title_tag.find('span') else '-'
    
    synopsis_tag = soup.find('p', id='synopsisField')
    sinopsis = synopsis_tag.get_text(strip=True) if synopsis_tag else '-'
    
    pic_tag = soup.find('div', class_=lambda x: x and 'anime__details__pic' in x)
    thumbnail = pic_tag.get('data-setbg') if pic_tag else ''
    
    score = '-'
    if pic_tag:
        ep_div = pic_tag.find('div', class_='ep')
        if ep_div:
            score = ep_div.get_text(strip=True).replace('\n', ' ').replace('  ', ' ')

    # 2. Metadata (Tipe, Musim, Studio, Genre, dll)
    metadata = {}
    widget = soup.find('div', class_='anime__details__widget')
    if widget:
        for li in widget.find_all('li'):
            label = li.find('span')
            value_div = li.find('div', class_='col-9')
            if label and value_div:
                key = label.get_text(strip=True).replace(':', '')
                values = [a.get_text(strip=True) for a in value_div.find_all('a')]
                val = ', '.join(values) if values else value_div.get_text(strip=True)
                metadata[key] = val

    # 3. Tag Tambahan
    tags = []
    tags_div = soup.find('div', class_='breadcrumb__links__v2__tags')
    if tags_div:
        tags = [a.get_text(strip=True).replace(',', '') for a in tags_div.find_all('a')]

    # 4. 🚀 RAHASIA 100+ EPISODE (Bongkar Popover data-content)
    episodes = []
    ep_button = soup.find('a', id='episodeLists')
    if ep_button and ep_button.get('data-content'):
        raw_ep_html = ep_button.get('data-content')
        decoded_html = html.unescape(raw_ep_html) # Decode HTML Entity
        ep_soup = BeautifulSoup(decoded_html, 'html.parser')
        
        for a in ep_soup.find_all('a'):
            ep_name = a.get_text(strip=True).replace('\n', ' ').replace('  ', ' ')
            ep_link = a.get('href', '')
            if ep_link:
                full_link = ep_link if ep_link.startswith('http') else BASE_URL + ep_link
                episodes.append({
                    'nama_episode': ep_name,
                    'link': full_link
                })
                
    # Fallback untuk Movie / Batch (kalau nggak ada popover episode)
    if not episodes:
        batch_section = soup.find('div', id='episodeBatchListsSection')
        if batch_section:
            for a in batch_section.find_all('a'):
                ep_name = a.get_text(strip=True)
                ep_link = a.get('href', '')
                if ep_link:
                    full_link = ep_link if ep_link.startswith('http') else BASE_URL + ep_link
                    episodes.append({'nama_episode': ep_name, 'link': full_link})

    return {
        'slug': slug,
        'judul': judul,
        'judul_alternatif': judul_alt,
        'skor': score,
        'sinopsis': sinopsis,
        'thumbnail': thumbnail,
        'metadata': metadata,
        'tags': tags,
        'total_episode': len(episodes),
        'daftar_episode': episodes # Semua episode (1 sampai 1000+) masuk sini!
    }