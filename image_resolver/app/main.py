"""
Main orchestration logic for the batch pipeline.
"""
import time
from typing import List

from . import config
from .parser import parse_local_images
from .crawler import extract_page_images
from .resolver import build_target_urls
from .downloader import verify_and_download
from .utils import write_csv_results
from .models import ResolveResult

def run_pipeline() -> None:
    """
    Executes the main pipeline:
    1. Parse local filenames.
    2. Group by gallery ID and fetch pages.
    3. Generate candidate URLs and verify/download.
    4. Log results.
    """
    print(f"Scanning input directory: {config.INPUT_DIR}")
    grouped_records = parse_local_images(config.INPUT_DIR)
    
    if not grouped_records:
        print("No valid local images found. Exiting.")
        return
        
    results: List[ResolveResult] = []
    
    for galid, local_imgs in grouped_records.items():
        print(f"\nProcessing Gallery: {galid} ({len(local_imgs)} images)")
        
        # 1. Fetch gallery page and extract its image mappings
        page_url = config.BASE_GALLERY_URL_TEMPLATE.format(galid=galid)
        print(f"  Fetching gallery: {page_url}")
        
        page_images = extract_page_images(page_url, galid)
        if not page_images:
            print("  Failed to extract valid images from gallery. Recording failures.")
            for img in local_imgs:
                results.append(ResolveResult(
                    galid=galid,
                    filename=img.filename,
                    page_url=page_url,
                    preview_url=None,
                    target_url=None,
                    downloaded_path=None,
                    success=False,
                    reason="gallery_fetch_failed_or_invalid"
                ))
            continue
            
        # 2. Process each local image
        for local_img in local_imgs:
            page_record = page_images.get(local_img.filename)
            
            if not page_record:
                results.append(ResolveResult(
                    galid=galid,
                    filename=local_img.filename,
                    page_url=page_url,
                    preview_url=None,
                    target_url=None,
                    downloaded_path=None,
                    success=False,
                    reason="filename_not_found_on_page"
                ))
                continue
                
            # 3. Resolve target URLs
            candidates = build_target_urls(page_record, config.TARGET_RESIDS)
            if not candidates:
                results.append(ResolveResult(
                    galid=galid,
                    filename=local_img.filename,
                    page_url=page_url,
                    preview_url=page_record.preview_url,
                    target_url=None,
                    downloaded_path=None,
                    success=False,
                    reason="target_url_build_failed"
                ))
                continue
                
            # 4. Try candidate URLs in order
            success = False
            final_reason = "no_valid_target_resid"
            final_target_url = None
            final_dest_path = None
            
            dest_dir = config.OUTPUT_DIR / galid
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / local_img.filename
            
            for candidate_url in candidates:
                print(f"    Trying {candidate_url} ...")
                is_valid, reason = verify_and_download(candidate_url, str(dest_path))
                if is_valid:
                    success = True
                    final_reason = reason
                    final_target_url = candidate_url
                    final_dest_path = str(dest_path)
                    break
                else:
                    final_reason = reason
                    
            results.append(ResolveResult(
                galid=galid,
                filename=local_img.filename,
                page_url=page_url,
                preview_url=page_record.preview_url,
                target_url=final_target_url,
                downloaded_path=final_dest_path,
                success=success,
                reason=final_reason
            ))

            time.sleep(config.RETRY_BACKOFF_SECONDS)  # Polite crawling
            
    # 5. Write logs
    logs_path = config.LOGS_DIR / "results.csv"
    write_csv_results(results, logs_path)
    print(f"\nPipeline finished. Wrote results to {logs_path}")

if __name__ == "__main__":
    run_pipeline()
