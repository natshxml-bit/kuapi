# app/watch.py
from bs4 import BeautifulSoup
from app.config import fetch_html, BASE_URL
import re

def get_watch_url(slug, episode_num):
    url = f"{BASE_URL}/anime/{slug}/episode/{episode_num}"
    html = fetch_html(url)
    
    if not html or "Just a moment..." in html:
        return {"error": "Gagal mengambil halaman watch (Cloudflare/Timeout)"}

    soup = BeautifulSoup(html, 'html.parser')
    
    # Cari iframe player
    iframe = soup.find('iframe')
    streaming_url = None
    if iframe and iframe.get('src'):
        streaming_url = iframe['src']
        if streaming_url.startswith('//'):
            streaming_url = 'https:' + streaming_url
            
    # Judul & Navigasi
    ep_title = soup.find('h3', class_='anime__video__title') or soup.find('h2')
    
    next_ep = soup.find('a', string=re.compile("Next", re.I)) or soup.find('a', class_='next')
    prev_ep = soup.find('a', string=re.compile("Prev", re.I)) or soup.find('a', class_='prev')

    return {
        'slug': slug,
        'episode_ke': episode_num,
        'judul_episode': ep_title.get_text(strip=True) if ep_title else f"Episode {episode_num}",
        'streaming_iframe_url': streaming_url,
        'next_episode': BASE_URL + next_ep['href'] if next_ep and next_ep.get('href') else None,
        'prev_episode': BASE_URL + prev_ep['href'] if prev_ep and prev_ep.get('href') else None,
        'note': "Gunakan URL iframe ini di WebView atau Iframe HTML5 untuk memutar video."
    }