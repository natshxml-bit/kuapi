# app/config.py
import cloudscraper

# Gunakan cloudscraper untuk bypass Cloudflare dasar
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)

BASE_URL = "https://v9.kuramanime.work"
HEADERS = {
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": BASE_URL
}