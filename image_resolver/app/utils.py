"""
Utility functions for file/dir operations and logging.
"""
import csv
from pathlib import Path
from typing import List

from .models import ResolveResult

def write_csv_results(results: List[ResolveResult], dest_path: Path) -> None:
    """
    Writes the list of ResolveResults to a CSV file.
    """
    if not results:
        return
        
    headers = [
        "galid", 
        "filename", 
        "page_url", 
        "preview_url", 
        "target_url", 
        "downloaded_path", 
        "success", 
        "reason"
    ]
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(dest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for res in results:
            writer.writerow({
                "galid": res.galid,
                "filename": res.filename,
                "page_url": res.page_url,
                "preview_url": res.preview_url,
                "target_url": res.target_url,
                "downloaded_path": res.downloaded_path,
                "success": res.success,
                "reason": res.reason
            })
