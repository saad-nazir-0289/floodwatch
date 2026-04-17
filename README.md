# Indus Urban FloodWatch

`FloodWatch Pakistan` now includes a Vercel-ready Flask frontend for overhead imagery analysis focused on flood extent, water spread, urban footprint proxies, and before/after change detection.

## Overview

This repo packages a presentation-friendly demo for the `Indus Urban FloodWatch` concept. It is optimized for fast exploration, visual storytelling, and overhead image walkthroughs rather than formal geospatial operations.

## Supported imagery

- satellite imagery
- drone imagery
- aerial imagery

The demo intentionally does **not** support ground-level or phone photos.

## What the app can generate

- single-image flood / water masks
- built-up proxy overlays for urban exposure storytelling
- before/after change maps
- summary metrics for water share, built-up proxy share, changed area, and connected flood regions
- downloadable PNG outputs for reports and presentations
- built-in demo imagery so users can test the app instantly without uploading anything

## Demo image sets included

- `Demo Set A`: river floodplain before/after pair
- `Demo Set B`: coastal flood and urban pressure before/after pair
- `Demo Set C`: single-image flood scene

## Vercel deploy

1. Import the repo into Vercel.
2. Let Vercel build the Python app from `api/index.py`.
3. Deploy.

## Local run (Vercel app)

```bash
pip install -r requirements.txt
flask --app api/index.py run
```

## Local run (legacy Streamlit app)

```bash
pip install -r requirements-streamlit.txt
streamlit run app.py
```

## Streamlit Community Cloud deploy

1. Push this repo to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from the repo.
4. Set the main file path to `app.py`.
5. Deploy.

## Repo structure

```text
app.py
api/
pages/
templates/
utils/
assets/
.streamlit/
requirements.txt
requirements-streamlit.txt
```

## Notes

- This is a visual decision-support demo, not a calibrated operational flood model.
- Best results come from clear overhead images with visible water, terrain, and built structures.
- Outputs should be reviewed before being used in formal reports.
- Vercel uses the Flask app; the original Streamlit app remains available for local or Streamlit Cloud use.
