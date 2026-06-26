# app/detail.py
from bs4 import BeautifulSoup
from app.config import fetch_html, BASE_URL

def get_detail(slug):
    url = f"{BASE_URL}/anime/{slug}"
    html = fetch_html(url)
    
    if not html or "Just a moment..." in html:
        return {"error": "Gagal mengambil detail (Cloudflare/Timeout)"}

    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Info Dasar
    title = soup.find('h2', class_='anime__details__title')
    synopsis = soup.find('div', class_='anime__details__text')
    cover = soup.find('div', class_='anime__details__pic')
    
    # 2. Metadata
    metadata = {}
    widget = soup.find('div', class_='anime__details__widget')
    if widget:
        for li in widget.find_all('li'):
            span = li.find('span')
            p = li.find('p')
            if span and p:
                metadata[span.get_text(strip=True)] = p.get_text(strip=True)

    # 3. List Episode
    episodes = []
    ep_list = soup.find('select', class_='select-episode') or soup.find('div', class_='anime__details__episodes') or soup.find('ul', class_='listing')
    
    if ep_list:
        # Kalau bentuknya dropdown select
        if ep_list.name == 'select':
            for option in ep_list.find_all('option'):
                ep_name = option.get_text(strip=True)
                ep_link = option.get('value', '')
                if ep_link and ep_link != '#':
                    full_link = BASE_URL + ep_link if ep_link.startswith('/') else ep_link
                    episodes.append({'nama_episode': ep_name, 'link': full_link})
        # Kalau bentuknya list <a>
        else:
            for a in ep_list.find_all('a'):
                ep_name = a.get_text(strip=True)
                ep_link = a.get('href', '')
                if ep_link:
                    full_link = BASE_URL + ep_link if ep_link.startswith('/') else ep_link
                    episodes.append({'nama_episode': ep_name, 'link': full_link})

    return {
        'slug': slug,
        'judul': title.get_text(strip=True) if title else '-',
        'sinopsis': synopsis.get_text(strip=True) if synopsis else '-',
        'thumbnail': cover.find('img').get('src') if cover and cover.find('img') else '',
        'metadata': metadata,
        'daftar_episode': episodes
    }