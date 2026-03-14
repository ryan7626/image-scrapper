# Image Variant Resolver

A scalable, pure Python batch utility to reconcile downscaled/preview local image files back to full high-resolution variants from a remote gallery web interface.

## Purpose & Scope

This tool is designed specifically for public image datasets. It operates in a stateless batch mode:
1. It analyzes locally existing preview files in an input directory.
2. It constructs a lookup to the remote gallery template URL.
3. It downloads the target website's original HTML.
4. It parses out preview endpoints.
5. It synthesizes full-resolution endpoints by string replacing the target resolution identifier exactly how it appears inside the known valid source path.
6. It downloads verified high-res equivalents locally and records state.

**Safety Note:** This tool is intended only for lawful, public image libraries. It does not engage with adult material, execute evasive headless browsers, or attempt arbitrary file inclusion.

## Structure

```text
image_resolver/
  app/              # Core modules logic
  data/
    cache/          # Optional HTML payload caches
    input/          # Initial local preview files matching `{galid}_{pid}.ext`
    logs/           # CSV tracking success and fail-states
    output/         # Full-resolution destinations by ID folder
  requirements.txt  # Project PIP dependencies
```

## Installation

Requires Python 3.11+.

```bash
cd image_resolver
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Configurations are stored in `app/config.py` and can be supplied via environment variables.

- `BASE_GALLERY_URL_TEMPLATE`: Target base. Make sure to embed `{galid}`. e.g. `https://example.com/galleries/{galid}`.
- `TARGET_RESIDS`: Comma-separated prioritized list of fallback resolutions, e.g. `1280,960,1600`.

## Running the Pipeline

Ensure all prerequisite low-res preview target files are copied into `data/input`.
File expectations assume standard syntax: e.g. `24748699_246_8d64.jpg`.

```bash
python3 -m app.main
```

## CSV Output

Your `data/logs/results.csv` outputs structured records representing target lookup states per file.

Example row segment:
```csv
galid,filename,page_url,preview_url,target_url,downloaded_path,success,reason
24748699,24748699_246_8d64.jpg,https://example.com/galleries/24748699,https://cdni.example.com/460/7/822/24748699...,https://cdni.example.com/1280/7/8...,/data/output/24748699/...,True,downloaded_1280x853
```

## Limitations & Future Scope

* The current variant uses lightweight regex-driven replacement targeting the first instance of a matching node identifier. Very weird URL designs may fail.
* Future upgrades could entail adding perceptual hashing routines to fall back to if metadata tags change between pipeline stages.
