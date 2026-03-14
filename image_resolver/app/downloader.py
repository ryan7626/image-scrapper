"""
Downloader and verifier for target images.
"""
import io
import requests
from typing import Tuple, Optional
from PIL import Image, UnidentifiedImageError

from . import config

def fetch_image_info(url: str) -> Tuple[bool, Optional[bytes], str]:
    """
    Fetches image data from the given URL and validates the HTTP response.
    
    Returns:
        A tuple of (success, bytes_content, reason)
    """
    headers = {"User-Agent": config.USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
        
        if resp.status_code == 404:
            return False, None, "http_404"
        elif resp.status_code == 403:
            return False, None, "http_403"
        elif resp.status_code != 200:
            return False, None, f"http_{resp.status_code}"
            
        content_type = resp.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            return False, None, "not_image"
            
        return True, resp.content, "success"
    except requests.RequestException as e:
        return False, None, "request_error"

def get_dimensions(raw_bytes: bytes) -> Tuple[bool, Optional[Tuple[int, int]], str]:
    """
    Verifies that the bytes represent a valid image that can be opened by Pillow,
    and returns its dimensions.
    """
    try:
        with Image.open(io.BytesIO(raw_bytes)) as img:
            return True, img.size, "success"
    except UnidentifiedImageError:
        return False, None, "invalid_image"
    except Exception:
        return False, None, "image_open_failed"

def verify_and_download(url: str, dest_path: str) -> Tuple[bool, str]:
    """
    Downloads an image, verifies it, and saves it.
    
    Returns:
        A tuple of (success, reason code)
    """
    success, raw_bytes, reason = fetch_image_info(url)
    if not success or not raw_bytes:
        return False, reason
        
    valid, dimensions, dim_reason = get_dimensions(raw_bytes)
    if not valid:
        return False, dim_reason
        
    try:
        with open(dest_path, "wb") as f:
            f.write(raw_bytes)
    except Exception as e:
        return False, "save_failed"
        
    if dimensions:
        return True, f"downloaded_{dimensions[0]}x{dimensions[1]}"
    return True, "downloaded"
