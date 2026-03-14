"""
Data models for the image resolver.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class LocalImageRecord:
    galid: str
    pid: str
    filename: str
    ext: str
    local_path: Path

@dataclass
class PageImageRecord:
    galid: str
    filename: str
    preview_url: str
    fid: str
    resid: str
    page_url: str

@dataclass
class ResolveResult:
    galid: str
    filename: str
    page_url: str
    preview_url: Optional[str]
    target_url: Optional[str]
    downloaded_path: Optional[str]
    success: bool
    reason: str
