# Indus Urban FloodWatch

`FloodWatch Pakistan` is a Streamlit demo for overhead imagery analysis focused on flood extent, water spread, urban footprint proxies, and before/after change detection.

## What it supports

- satellite imagery
- drone imagery
- aerial imagery

The demo intentionally does **not** support ground-level or phone photos.

## Features

- single image flood / water mask generation
- built-up proxy overlay for urban exposure storytelling
- before/after change mapping
- quick metrics for water coverage, built-up proxy coverage, changed area, and connected regions
- downloadable PNG outputs
- built-in demo imagery for instant testing without uploads

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from the repo.
4. Set the main file path to `app.py`.
5. Deploy.

## Notes

- This is a visual decision-support demo, not a calibrated operational flood model.
- Best results come from clear overhead images with visible water, terrain, and built structures.
