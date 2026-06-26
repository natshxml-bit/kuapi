# app/detail.py
from bs4 import BeautifulSoup
from app.config import scraper, BASE_URL, HEADERS

def get_detail(slug):
    # Contoh slug: "4871/kami-no-shizuku"
    url = f"{BASE_URL}/anime/{slug}"
    response = scraper.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. Ambil Info Dasar (Judul, Sinopsis, Thumbnail)
    title = soup.find('h2', class_='anime__details__title')
    synopsis = soup.find('div', class_='anime__details__text')
    cover = soup.find('div', class_='anime__details__pic')
    
    # 2. Ambil Metadata (Genre, Studio, Season, dll)
    metadata = {}
    widget = soup.find('div', class_='anime__details__widget')
    if widget:
        for li in widget.find_all('li'):
            span = li.find('span')
            p = li.find('p')
            if span and p:
                metadata[span.get_text(strip=True)] = p.get_text(strip=True)

    # 3. Ambil List Episode
    episodes = []
    # Biasanya list episode ada di dalam element dengan class seperti .listing atau .episode-list
    # (Sesuaikan class_ di bawah jika Kuramanime mengubah templatenya)
    ep_list = soup.find('div', class_='anime__details__episodes') or soup.find('ul', class_='listing')
    
    if ep_list:
        for a in ep_list.find_all('a'):
            ep_name = a.get_text(strip=True)
            ep_link = a.get('href', '')
            episodes.append({
                'nama_episode': ep_name,
                'link': BASE_URL + ep_link if ep_link.startswith('/') else ep_link
            })

    return {
        'slug': slug,
        'judul': title.get_text(strip=True) if title else '-',
        'sinopsis': synopsis.get_text(strip=True) if synopsis else '-',
        'thumbnail': cover.find('img').get('src') if cover and cover.find('img') else '',
        'metadata': metadata,
        'daftar_episode': episodes
    }