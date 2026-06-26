# app/home.py
from bs4 import BeautifulSoup
from app.config import scraper, BASE_URL, HEADERS

def get_homepage():
    url = f"{BASE_URL}/"
    response = scraper.get(url, headers=HEADERS)
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
    return results