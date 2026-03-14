"""
Configuration settings for the image resolver.
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
CACHE_DIR = DATA_DIR / "cache"
LOGS_DIR = DATA_DIR / "logs"

# Ensure directories exist
for d in [INPUT_DIR, OUTPUT_DIR, CACHE_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Gallery Settings
# Use placeholder safe domains
BASE_GALLERY_URL_TEMPLATE = os.getenv("BASE_GALLERY_URL_TEMPLATE", "https://example.com/galleries/{galid}")

# Target Resolution IDs (Ordered by preference)
TARGET_RESIDS = os.getenv("TARGET_RESIDS", "1280,960,1600").split(",")

# Network Settings
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ImageResolver/1.0")

# Fetch behavior
ENABLE_HTML_CACHE = os.getenv("ENABLE_HTML_CACHE", "true").lower() == "true"
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_BACKOFF_SECONDS = int(os.getenv("RETRY_BACKOFF_SECONDS", "2"))
