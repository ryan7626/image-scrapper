"""
HTML crawler and parser for gallery pages.
"""
import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from typing import Dict, Optional
from pathlib import Path

from . import config
from .models import PageImageRecord

# Preview URL pattern: .../{resid}/{fid}/{galid}/{filename}
# E.g. https://cdni.example.com/460/7/822/24748699/24748699_246_8d64.jpg
IMAGE_URL_PATTERN = re.compile(r"/(?P<resid>[0-9a-zA-Z_-]+)/(?P<fid>[0-9a-zA-Z_/]+)/(?P<galid>\d+)/(?P<filename>[^/?#]+)$")

def fetch_html(page_url: str, galid: str) -> Optional[str]:
    """
    Fetches HTML for a given gallery page. Uses caching if enabled.
    
    Args:
        page_url: The full URL to the gallery page.
        galid: The gallery ID, used for caching.
        
    Returns:
        The HTML content as a string, or None if the fetch failed.
    """
    if config.ENABLE_HTML_CACHE:
        cache_path = config.CACHE_DIR / f"{galid}.html"
        if cache_path.exists():
            return cache_path.read_text(encoding="utf-8")
            
    headers = {"User-Agent": config.USER_AGENT}
    try:
        resp = requests.get(page_url, headers=headers, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
        html = resp.text
        
        if config.ENABLE_HTML_CACHE:
            config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache_path = config.CACHE_DIR / f"{galid}.html"
            cache_path.write_text(html, encoding="utf-8")
            
        return html
    except Exception as e:
        print(f"Error fetching {page_url}: {e}")
        return None

def extract_image_urls_from_element(img_tag, page_url: str) -> list[str]:
    """
    Extracts potential image URLs from an img tag (src, srcset, data attrs).
    """
    urls = []
    
    # Check standard src
    if img_tag.has_attr("src"):
        urls.append(urljoin(page_url, img_tag["src"]))
        
    # Check srcset
    if img_tag.has_attr("srcset"):
        srcset = img_tag["srcset"]
        for entry in srcset.split(","):
            url = entry.strip().split(" ")[0]
            if url:
                urls.append(urljoin(page_url, url))
                
    # Check common lazy-load attributes
    for attr in ["data-src", "data-lazy", "data-original", "data-srcset"]:
        if img_tag.has_attr(attr):
            val = img_tag[attr]
            # Simple heuristic if it's a srcset-like string vs single URL
            if "," in val:
                for entry in val.split(","):
                    url = entry.strip().split(" ")[0]
                    if url:
                        urls.append(urljoin(page_url, url))
            else:
                urls.append(urljoin(page_url, val))
                
    return list(dict.fromkeys(urls)) # Remove duplicates while preserving order

def extract_page_images(page_url: str, galid: str) -> Dict[str, PageImageRecord]:
    """
    Fetches a gallery page and parses it for images that match the target gallery ID.
    
    Returns:
        A dictionary mapping exact filename to PageImageRecord.
    """
    html = fetch_html(page_url, galid)
    if not html:
        return {}
        
    soup = BeautifulSoup(html, "html.parser")
    records: Dict[str, PageImageRecord] = {}
    
    for img in soup.find_all("img"):
        candidate_urls = extract_image_urls_from_element(img, page_url)
        for url in candidate_urls:
            parsed = urlparse(url)
            match = IMAGE_URL_PATTERN.search(parsed.path)
            if match:
                url_galid = match.group("galid")
                # Only keep URLs that match our target gallery ID
                if url_galid == galid:
                    filename = match.group("filename")
                    # If multiple candidates exist, we take the first valid one we see (usually 'src' or most direct)
                    if filename not in records:
                        records[filename] = PageImageRecord(
                            galid=galid,
                            filename=filename,
                            preview_url=url,
                            fid=match.group("fid"),
                            resid=match.group("resid"),
                            page_url=page_url
                        )
                        
    return records
