# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache
from app import home, detail, watch

app = FastAPI(title="Kuramanime Unofficial API")

# Setup CORS & Cache
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
cache = TTLCache(maxsize=100, ttl=300) # Cache 5 Menit

@app.get("/")
def root():
    return {"status": "Online", "endpoints": ["/api/home", "/api/detail/{slug}", "/api/watch/{slug}/{episode}"]}

@app.get("/api/home")
def api_home():
    if "home_data" in cache:
        return {"source": "cache", "data": cache["home_data"]}
    
    data = home.get_homepage()
    cache["home_data"] = data
    return {"source": "fresh_scrape", "total": len(data), "data": data}

@app.get("/api/detail/{slug:path}")
def api_detail(slug: str):
    # Cache key khusus untuk detail agar tidak menimpa cache home
    cache_key = f"detail_{slug}"
    if cache_key in cache:
        return {"source": "cache", "data": cache[cache_key]}

    try:
        data = detail.get_detail(slug)
        cache[cache_key] = data
        return {"source": "fresh_scrape", "data": data}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Gagal mengambil detail: {str(e)}")

@app.get("/api/watch/{slug:path}/{episode}")
def api_watch(slug: str, episode: int):
    # Data watch TIDAK BOLEH di-cache lama, karena link streaming sering expire/rotate
    try:
        data = watch.get_watch_url(slug, episode)
        if not data['streaming_iframe_url']:
             raise HTTPException(status_code=404, detail="Iframe video tidak ditemukan di halaman.")
        return {"source": "fresh_scrape", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error watch page: {str(e)}")