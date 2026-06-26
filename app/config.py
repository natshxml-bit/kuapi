# app/config.py
from curl_cffi import requests

# Menyamar jadi Chrome 124, bypass Cloudflare WAF
session = requests.Session(
    impersonate="chrome124",
    headers={
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://v9.kuramanime.work/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    }
)

BASE_URL = "https://v9.kuramanime.work"