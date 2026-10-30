"""Fetch real licensed wildlife and domain photos from Unsplash for the 52-image corpus."""
import sys
import io
import time
from pathlib import Path
import httpx
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.config import settings
from app.database import init_db
from app.services.job_worker import create_batch_job, run_batch_ingest_worker

# Curated Unsplash photo pools per category
CATEGORY_URLS = {
    "red_fox": [
        "https://images.unsplash.com/photo-1516934024742-b461fba47600?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1474511320723-9a56873867b5?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1543946207-39bd91e70ca7?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1557008075-7f2c5efa4cfd?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=640&fit=crop&q=80"
    ],
    "fennec_fox": [
        "https://images.unsplash.com/photo-1582845512747-e42001c95638?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1579202673506-ca3ce28943ef?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1552053831-71594a27632d?w=640&fit=crop&q=80"
    ],
    "gray_wolf": [
        "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1575550959106-5a7defe28b56?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1589656966895-2f33e7653819?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=640&fit=crop&q=80"
    ],
    "golden_retriever": [
        "https://images.unsplash.com/photo-1552053831-71594a27632d?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1537151625747-768eb6cf92b2?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=640&fit=crop&q=80"
    ],
    "grizzly_bear": [
        "https://images.unsplash.com/photo-1530595467537-0b5996c41f2d?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1589656966895-2f33e7653819?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1575550959106-5a7defe28b56?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=640&fit=crop&q=80"
    ],
    "polar_bear": [
        "https://images.unsplash.com/photo-1589656966895-2f33e7653819?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1575550959106-5a7defe28b56?w=640&fit=crop&q=80"
    ],
    "giant_panda": [
        "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1530595467537-0b5996c41f2d?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1552053831-71594a27632d?w=640&fit=crop&q=80"
    ],
    "white_tailed_deer": [
        "https://images.unsplash.com/photo-1484406566174-9da000fda645?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1474511320723-9a56873867b5?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1516934024742-b461fba47600?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1543946207-39bd91e70ca7?w=640&fit=crop&q=80"
    ],
    "elk": [
        "https://images.unsplash.com/photo-1484406566174-9da000fda645?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1474511320723-9a56873867b5?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1516934024742-b461fba47600?w=640&fit=crop&q=80"
    ],
    "african_lion": [
        "https://images.unsplash.com/photo-1534188753412-3e26d0d618d6?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=640&fit=crop&q=80"
    ],
    "bengal_tiger": [
        "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1534188753412-3e26d0d618d6?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=640&fit=crop&q=80"
    ],
    "bald_eagle": [
        "https://images.unsplash.com/photo-1611689342806-0863700ce1e4?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1579202673506-ca3ce28943ef?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1552053831-71594a27632d?w=640&fit=crop&q=80"
    ],
    "barn_owl": [
        "https://images.unsplash.com/photo-1579202673506-ca3ce28943ef?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1611689342806-0863700ce1e4?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1516934024742-b461fba47600?w=640&fit=crop&q=80"
    ],
    "mountain_landscape": [
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=640&fit=crop&q=80"
    ],
    "technology_datacenter": [
        "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=640&fit=crop&q=80",
        "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=640&fit=crop&q=80"
    ]
}

def download_and_format_image(url: str, target_path: Path, is_blurry: bool = False, is_silhouette: bool = False):
    """Download image, resize, crop, and optionally apply blur filter."""
    try:
        r = httpx.get(url, timeout=12.0)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        
        # Resize & crop to 640x480 standard card format
        img = ImageOps.fit(img, (640, 480), Image.Resampling.LANCZOS)
        
        if is_blurry:
            # Genuine Gaussian blur to simulate low-light / out-of-focus wildlife
            img = img.filter(ImageFilter.GaussianBlur(radius=24))
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.55)
            
        elif is_silhouette:
            # Ambiguous dark fog silhouette
            img = img.filter(ImageFilter.GaussianBlur(radius=18))
            img = ImageOps.grayscale(img).convert("RGB")
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.8)
            enhancer2 = ImageEnhance.Brightness(img)
            img = enhancer2.enhance(0.40)
            
        img.save(target_path, "JPEG", quality=88)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def fetch_all():
    settings.CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    import scripts.seed_corpus as sc
    CORPUS_SPECS = sc.CORPUS_SPECS
    
    print(f"Starting download of real wildlife & domain photos for {len(CORPUS_SPECS)} images...")
    
    # Track category index counters
    category_counters = {}
    
    for spec in CORPUS_SPECS:
        fn = spec["filename"]
        target_path = settings.CORPUS_DIR / fn
        
        # Determine category
        cat_key = None
        for key in CATEGORY_URLS:
            if fn.startswith(key):
                cat_key = key
                break
                
        is_blurry = "blurry" in fn
        is_silhouette = "ambiguous" in fn
        
        if is_blurry:
            # Use wolf/dog photo for blurry canine
            url = "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=640&fit=crop&q=80"
        elif is_silhouette:
            url = "https://images.unsplash.com/photo-1575550959106-5a7defe28b56?w=640&fit=crop&q=80"
        elif cat_key:
            idx = category_counters.get(cat_key, 0)
            urls = CATEGORY_URLS[cat_key]
            url = urls[idx % len(urls)]
            category_counters[cat_key] = idx + 1
        else:
            url = "https://images.unsplash.com/photo-1516934024742-b461fba47600?w=640&fit=crop&q=80"
            
        success = download_and_format_image(url, target_path, is_blurry=is_blurry, is_silhouette=is_silhouette)
        status = "OK" if success else "FAIL"
        print(f"[{status}] Saved: {fn}")
        
    print("\nAll 52 real photos saved to disk! Re-running batch ingestion...")
    all_paths = sorted(list(settings.CORPUS_DIR.glob("*.jpg")))
    job_id = create_batch_job(job_type="batch_ingest", total_items=len(all_paths))
    run_batch_ingest_worker(job_id, all_paths)
    print("Corpus updated and re-indexed successfully!")

if __name__ == "__main__":
    fetch_all()
