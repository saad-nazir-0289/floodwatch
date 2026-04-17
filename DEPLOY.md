# Deployment Notes

## Vercel

- Entry point: `api/index.py`
- Routing: `vercel.json`
- Static assets: served from `assets/`
- Main routes: `/`, `/analyze`, `/faq`, `/project-background`

## Recommended checks after Vercel deploy

- homepage loads with hero image and navigation
- `Analyze` opens and demo imagery thumbnails appear
- single-image mode produces overlays and download links
- before/after mode produces change maps and download links
- FAQ and Project Background render correctly

## Streamlit Community Cloud

- Repository: `saad-nazir-0289/floodwatch`
- Branch: `main`
- Main file path: `app.py`
- Install file for local parity: `requirements-streamlit.txt`

## Recommended checks after Streamlit deploy

- homepage loads with hero image
- built-in demo images appear in `Upload & Analyze`
- single-image mode produces overlays
- before/after mode produces change maps
- downloads work for generated PNGs

## App positioning

This app is a demo for overhead imagery interpretation and visual flood storytelling. It should be presented as a lightweight decision-support experience rather than an operational flood intelligence platform.
