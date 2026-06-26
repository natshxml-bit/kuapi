# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache
from app import detail, watch, properties # Hapus anime_list

app = FastAPI(title="Kuramanime Unofficial API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
cache = TTLCache(maxsize=100, ttl=300) 

@app.get("/")
def root():
    return {
        "status": "Online", 
        "endpoints": [
            "/api/properties", 
            "/api/anime-list?url_path=/quick/ongoing&page=1", 
            "/api/detail/{slug}", 
            "/api/watch/{slug}/{episode}"
        ]
    }

@app.get("/api/properties")
def api_properties():
    cache_key = "properties_data"
    if cache_key in cache: return {"source": "cache", "data": cache[cache_key]}
    data = properties.get_properties()
    if "error" in data: raise HTTPException(status_code=500, detail=data["error"])
    cache[cache_key] = data
    return {"source": "fresh_scrape", "data": data}

@app.get("/api/anime-list")
def api_anime_list(url_path: str = "/quick/ongoing", page: int = 1):
    """
    Mengambil daftar anime beserta SLUG-nya.
    Contoh url_path: 
    - /quick/ongoing (Sedang Tayang)
    - /quick/finished (Selesai)
    - /quick/movie (Movie)
    - /properties/genre/isekai (Berdasarkan Genre)
    """
    cache_key = f"list_{url_path}_{page}"
    if cache_key in cache: return {"source": "cache", "data": cache[cache_key]}
    
    # Panggil dari properties sekarang
    data = properties.get_anime_list(url_path, page)
    if "error" in data: raise HTTPException(status_code=500, detail=data["error"])
    
    cache[cache_key] = data
    return {"source": "fresh_scrape", "data": data}

@app.get("/api/detail/{slug:path}")
def api_detail(slug: str):
    cache_key = f"detail_{slug}"
    if cache_key in cache: return {"source": "cache", "data": cache[cache_key]}
    data = detail.get_detail(slug)
    if "error" in data: raise HTTPException(status_code=404, detail=data["error"])
    cache[cache_key] = data
    return {"source": "fresh_scrape", "data": data}

@app.get("/api/watch/{slug:path}/{episode}")
def api_watch(slug: str, episode: int):
    try:
        data = watch.get_watch_url(slug, episode)
        if "error" in data: raise HTTPException(status_code=404, detail=data["error"])
        return {"source": "fresh_scrape", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))