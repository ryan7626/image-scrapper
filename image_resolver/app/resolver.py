"""
URL transformation and resolution logic.
"""
from urllib.parse import urlparse, urlunparse
from typing import Optional, List

from .models import PageImageRecord

def build_target_url(preview_url: str, target_resid: str, original_resid: str) -> Optional[str]:
    """
    Build a target candidate URL by replacing ONLY the resolution segment that matches original_resid.
    We split the path by '/' and find the first segment that matches original_resid to replace it.
    This safely avoids replacing e.g., '1080' if it appears elsewhere like the gallery ID.
    """
    parsed = urlparse(preview_url)
    path_segments = parsed.path.split('/')
    
    # We want to replace the first occurrence of original_resid
    # that is part of the path (usually one of the first few segments).
    for i, segment in enumerate(path_segments):
        if segment == original_resid:
            path_segments[i] = target_resid
            new_path = "/".join(path_segments)
            return urlunparse(parsed._replace(path=new_path))
            
    return None

def build_target_urls(page_record: PageImageRecord, target_resids: List[str]) -> List[str]:
    """
    Generates a prioritized list of candidate URLs for the target resolutions.
    """
    candidates = []
    for resid in target_resids:
        # If the original resid is identical to target, no need to replace
        if resid == page_record.resid:
            new_url = page_record.preview_url
        else:
            new_url = build_target_url(page_record.preview_url, resid, page_record.resid)
            
        if new_url and new_url not in candidates:
            candidates.append(new_url)
            
    return candidates
