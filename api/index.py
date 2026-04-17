from __future__ import annotations

import base64
from pathlib import Path

import numpy as np
from flask import Flask, render_template, request
from PIL import Image

from utils.image_processing import (
    analyze_change,
    analyze_single_image,
    mask_to_rgb,
    to_png_bytes,
)


ROOT_DIR = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT_DIR / "assets"

app = Flask(
    __name__,
    template_folder=str(ROOT_DIR / "templates"),
    static_folder=str(ASSET_DIR),
    static_url_path="/assets",
)

FAQS = [
    {
        "question": "What kind of images should I use?",
        "answer": "Use overhead satellite, drone, or aerial imagery with visible water boundaries and built structures.",
    },
    {
        "question": "Can I upload phone photos?",
        "answer": "No. The demo is intentionally limited to overhead imagery because the segmentation logic is designed for map-like views.",
    },
    {
        "question": "Is this a production flood model?",
        "answer": "No. It is a fast, explainable demo for visual analysis and storytelling.",
    },
    {
        "question": "What does the built-up layer mean?",
        "answer": "It is a built-up proxy, not a parcel-accurate land-cover classification.",
    },
    {
        "question": "Why do built-in demo images exist?",
        "answer": "They let anyone test the app instantly, even if they do not have imagery ready.",
    },
]

BACKGROUND_POINTS = [
    "Pakistan faces recurring flood shocks alongside rapid urban expansion.",
    "The 2022 floods affected 33 million people and caused more than US$14.9B in damages.",
    "Urban population growth increases exposure in dense and low-service settlements.",
    "Monitoring is often delayed, fragmented, or too coarse for neighborhood-scale decisions.",
]

FUSION_POINTS = [
    "High-resolution imagery gives better visual detail, but not always daily continuity.",
    "High-frequency imagery covers large areas often, but can be too coarse for local response.",
    "A fusion mindset helps bridge the spatial-temporal gap and supports response plus planning.",
]

REFERENCES = [
    "[1] Pakistan Floods 2022: Post-Disaster Needs Assessment (PDNA), 2022.",
    "[2] World Bank urban population data for Pakistan.",
    "[3] World Bank urban population share data for Pakistan.",
    "[4] World Bank slum population data for Pakistan.",
    "[5] F. Gao et al., STARFM, Remote Sensing of Environment, 2006.",
    "[6] X. Zhu et al., ESTARFM, Remote Sensing of Environment, 2010.",
    "[7] Z. Lian et al., Deep learning-based spatiotemporal fusion review, Sensors, 2025.",
    "[8] C. Wang et al., Sentinel-1 and Sentinel-2 flood inundation mapping, ISPRS JPRS, 2021.",
]

SINGLE_DEMOS = {
    "Demo Set C - Single Flood Scene": ASSET_DIR / "demo_flood_single.png",
    "Demo Set A - Before": ASSET_DIR / "demo_delta_before.png",
    "Demo Set B - Before": ASSET_DIR / "demo_coast_before.png",
}

PAIR_DEMOS = {
    "Demo Set A - River Flood Expansion": (
        ASSET_DIR / "demo_delta_before.png",
        ASSET_DIR / "demo_delta_after.png",
    ),
    "Demo Set B - Coastal Flood + Urban Pressure": (
        ASSET_DIR / "demo_coast_before.png",
        ASSET_DIR / "demo_coast_after.png",
    ),
}

SAMPLE_IMAGES = [
    "demo_delta_before.png",
    "demo_delta_after.png",
    "demo_coast_before.png",
    "demo_coast_after.png",
    "demo_flood_single.png",
]


def load_local_image(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("RGB"))


def file_to_image(file_storage) -> np.ndarray:
    return np.array(Image.open(file_storage.stream).convert("RGB"))


def png_data_uri(image: np.ndarray) -> str:
    encoded = base64.b64encode(to_png_bytes(image)).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def metrics_list(metrics: dict[str, object]) -> list[dict[str, object]]:
    return [{"label": label, "value": value} for label, value in metrics.items()]


def build_single_result(image: np.ndarray, sensitivity: float, overlay_opacity: float) -> dict[str, object]:
    result = analyze_single_image(image, sensitivity=sensitivity, alpha=overlay_opacity)
    water_mask_rgb = mask_to_rgb(result.water_mask, (35, 195, 230))
    urban_mask_rgb = mask_to_rgb(result.urban_mask, (255, 156, 70))

    return {
        "kind": "single",
        "headline": result.confidence_note,
        "metrics": metrics_list(result.metrics),
        "images": [
            {"title": "Original", "src": png_data_uri(result.original)},
            {"title": "Enhanced", "src": png_data_uri(result.enhanced)},
            {"title": "Water Mask", "src": png_data_uri(water_mask_rgb)},
            {"title": "Flood / Water Overlay", "src": png_data_uri(result.water_overlay)},
            {"title": "Built-up Proxy Mask", "src": png_data_uri(urban_mask_rgb)},
            {"title": "Urban Overlay", "src": png_data_uri(result.urban_overlay)},
            {"title": "Combined Thematic Map", "src": png_data_uri(result.combined_overlay)},
        ],
        "downloads": [
            {"label": "Combined map (PNG)", "src": png_data_uri(result.combined_overlay), "filename": "floodwatch_combined_map.png"},
            {"label": "Water mask (PNG)", "src": png_data_uri(water_mask_rgb), "filename": "floodwatch_water_mask.png"},
            {"label": "Urban mask (PNG)", "src": png_data_uri(urban_mask_rgb), "filename": "floodwatch_urban_mask.png"},
        ],
    }


def build_change_result(before: np.ndarray, after: np.ndarray, sensitivity: float, overlay_opacity: float) -> dict[str, object]:
    result = analyze_change(before, after, sensitivity=sensitivity, alpha=overlay_opacity)
    flood_gain_rgb = mask_to_rgb(result.flood_gain_mask, (35, 195, 230))
    urban_change_rgb = mask_to_rgb(result.urban_change_mask, (255, 156, 70))

    return {
        "kind": "change",
        "headline": "Comparison complete. Review the change map, flood gain, and urban proxy shifts.",
        "metrics": metrics_list(result.metrics),
        "images": [
            {"title": "Before", "src": png_data_uri(result.before)},
            {"title": "After", "src": png_data_uri(result.after)},
            {"title": "Change Overlay", "src": png_data_uri(result.change_overlay)},
            {"title": "New Water / Flood Gain", "src": png_data_uri(flood_gain_rgb)},
            {"title": "Urban Proxy Change", "src": png_data_uri(urban_change_rgb)},
        ],
        "downloads": [
            {"label": "Change overlay (PNG)", "src": png_data_uri(result.change_overlay), "filename": "floodwatch_change_overlay.png"},
            {"label": "Flood gain mask (PNG)", "src": png_data_uri(flood_gain_rgb), "filename": "floodwatch_flood_gain.png"},
            {"label": "Urban change mask (PNG)", "src": png_data_uri(urban_change_rgb), "filename": "floodwatch_urban_change.png"},
        ],
    }


@app.route("/")
def home():
    return render_template("index.html", sample_images=SAMPLE_IMAGES)


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    form_state = {
        "mode": request.form.get("mode", "single"),
        "source": request.form.get("source", "demo"),
        "sensitivity": request.form.get("sensitivity", "0.50"),
        "overlay_opacity": request.form.get("overlay_opacity", "0.42"),
        "single_demo": request.form.get("single_demo", next(iter(SINGLE_DEMOS))),
        "pair_demo": request.form.get("pair_demo", next(iter(PAIR_DEMOS))),
    }

    result = None
    error = None

    if request.method == "POST":
        sensitivity = float(form_state["sensitivity"])
        overlay_opacity = float(form_state["overlay_opacity"])
        mode = form_state["mode"]
        source = form_state["source"]

        try:
            if mode == "single":
                if source == "demo":
                    image = load_local_image(SINGLE_DEMOS[form_state["single_demo"]])
                else:
                    uploaded = request.files.get("single_image")
                    if uploaded is None or not uploaded.filename:
                        raise ValueError("Upload one overhead image or switch to a built-in demo image.")
                    image = file_to_image(uploaded)
                result = build_single_result(image, sensitivity, overlay_opacity)
            else:
                if source == "demo":
                    before_path, after_path = PAIR_DEMOS[form_state["pair_demo"]]
                    before = load_local_image(before_path)
                    after = load_local_image(after_path)
                else:
                    before_file = request.files.get("before_image")
                    after_file = request.files.get("after_image")
                    if before_file is None or not before_file.filename or after_file is None or not after_file.filename:
                        raise ValueError("Upload both overhead images or switch to a built-in demo pair.")
                    before = file_to_image(before_file)
                    after = file_to_image(after_file)
                result = build_change_result(before, after, sensitivity, overlay_opacity)
        except Exception as exc:
            error = str(exc)

    return render_template(
        "analyze.html",
        form_state=form_state,
        single_demo_names=list(SINGLE_DEMOS.keys()),
        pair_demo_names=list(PAIR_DEMOS.keys()),
        sample_images=SAMPLE_IMAGES,
        result=result,
        error=error,
    )


@app.route("/faq")
def faq():
    return render_template("faq.html", faqs=FAQS)


@app.route("/project-background")
def project_background():
    return render_template(
        "project_background.html",
        background_points=BACKGROUND_POINTS,
        fusion_points=FUSION_POINTS,
        references=REFERENCES,
    )


if __name__ == "__main__":
    app.run(debug=True)
