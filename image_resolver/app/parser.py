"""
Parser for local image filenames.
"""
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

from .models import LocalImageRecord

# Regex pattern: ^(?P<galid>\d+)_(?P<pid>.+)\.(?P<ext>jpg|jpeg|png|webp)$
FILENAME_PATTERN = re.compile(r"^(?P<galid>\d+)_(?P<pid>.+)\.(?P<ext>jpg|jpeg|png|webp)$", re.IGNORECASE)

def parse_local_images(input_dir: Path) -> Dict[str, List[LocalImageRecord]]:
    """
    Scans the input directory and parses local filenames using the expected pattern.
    Groups the parsed records by gallery ID (galid).

    Args:
        input_dir: Path to the directory containing local input images.
        
    Returns:
        A dictionary mapping galid to a list of LocalImageRecord instances.
    """
    grouped_records: Dict[str, List[LocalImageRecord]] = defaultdict(list)
    
    if not input_dir.exists() or not input_dir.is_dir():
        return dict(grouped_records)
        
    for file_path in input_dir.iterdir():
        if not file_path.is_file():
            continue
            
        match = FILENAME_PATTERN.match(file_path.name)
        if match:
            record = LocalImageRecord(
                galid=match.group("galid"),
                pid=match.group("pid"),
                filename=file_path.name,
                ext=match.group("ext"),
                local_path=file_path
            )
            grouped_records[record.galid].append(record)
            
    return dict(grouped_records)
