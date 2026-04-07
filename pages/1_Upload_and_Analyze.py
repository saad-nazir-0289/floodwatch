from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

from utils.image_processing import (
    analyze_change,
    analyze_single_image,
    mask_to_rgb,
    read_image,
    to_png_bytes,
)
from utils.visualization import metrics_dataframe, render_metric_grid


st.set_page_config(page_title="FloodWatch Pakistan", page_icon="🌊", layout="wide")

ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"

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

st.title("FloodWatch Pakistan")
st.caption("Upload satellite, drone, or aerial imagery only. Ground-level photos are intentionally not supported.")

with st.sidebar:
    st.header("Analysis Controls")
    mode = st.radio("Mode", ["Single Image Analysis", "Before/After Comparison"])
    sensitivity = st.slider("Detection sensitivity", min_value=0.1, max_value=0.9, value=0.5, step=0.05)
    overlay_opacity = st.slider("Overlay opacity", min_value=0.15, max_value=0.80, value=0.42, step=0.05)
    st.markdown("---")
    st.markdown(
        "**Tips**\n\n"
        "- Use nadir or near-nadir overhead images\n"
        "- Keep before/after views roughly aligned\n"
        "- Visible rivers, roads, roofs, and terrain improve results"
    )


def load_local_image(path: Path) -> np.ndarray:
    return np.array(Image.open(path).convert("RGB"))


def sample_image_panel() -> None:
    samples = [
        ASSET_DIR / "demo_delta_before.png",
        ASSET_DIR / "demo_delta_after.png",
        ASSET_DIR / "demo_coast_before.png",
        ASSET_DIR / "demo_coast_after.png",
        ASSET_DIR / "demo_flood_single.png",
    ]
    samples = [sample for sample in samples if sample.exists()]
    if not samples:
        return
    st.subheader("Sample imagery")
    cols = st.columns(min(5, len(samples)))
    for col, sample in zip(cols, samples):
        col.image(str(sample), caption=sample.stem.replace("_", " "), use_container_width=True)


sample_image_panel()

if mode == "Single Image Analysis":
    source = st.radio("Image source", ["Upload your own image", "Use built-in demo image"], horizontal=True)
    image = None

    if source == "Use built-in demo image":
        selected_demo = st.selectbox("Choose a demo image", list(SINGLE_DEMOS.keys()))
        image = load_local_image(SINGLE_DEMOS[selected_demo])
        st.image(image, caption=selected_demo, use_container_width=True)

    uploaded = st.file_uploader(
        "Upload one overhead image",
        type=["png", "jpg", "jpeg", "tif", "tiff", "webp"],
        accept_multiple_files=False,
    )

    if source == "Upload your own image" and uploaded is not None:
        image = read_image(uploaded)

    if image is not None:
        result = analyze_single_image(image, sensitivity=sensitivity, alpha=overlay_opacity)

        st.success(result.confidence_note)
        render_metric_grid(result.metrics)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["Original", "Flood Mask", "Urban Overlay", "Combined Map", "Downloads"]
        )
        with tab1:
            c1, c2 = st.columns(2)
            c1.image(result.original, caption="Original", use_container_width=True)
            c2.image(result.enhanced, caption="Enhanced", use_container_width=True)
        with tab2:
            c1, c2 = st.columns(2)
            c1.image(mask_to_rgb(result.water_mask, (35, 195, 230)), caption="Water mask", use_container_width=True)
            c2.image(result.water_overlay, caption="Flood / water overlay", use_container_width=True)
        with tab3:
            c1, c2 = st.columns(2)
            c1.image(mask_to_rgb(result.urban_mask, (255, 156, 70)), caption="Built-up proxy mask", use_container_width=True)
            c2.image(result.urban_overlay, caption="Urban overlay", use_container_width=True)
        with tab4:
            st.image(result.combined_overlay, caption="Combined thematic map", use_container_width=True)
            st.dataframe(metrics_dataframe(result.metrics), use_container_width=True, hide_index=True)
        with tab5:
            st.download_button(
                "Download combined map (PNG)",
                data=to_png_bytes(result.combined_overlay),
                file_name="floodwatch_combined_map.png",
                mime="image/png",
            )
            st.download_button(
                "Download water mask (PNG)",
                data=to_png_bytes(mask_to_rgb(result.water_mask, (35, 195, 230))),
                file_name="floodwatch_water_mask.png",
                mime="image/png",
            )
            st.download_button(
                "Download urban mask (PNG)",
                data=to_png_bytes(mask_to_rgb(result.urban_mask, (255, 156, 70))),
                file_name="floodwatch_urban_mask.png",
                mime="image/png",
            )
    else:
        st.info("Upload one satellite, drone, or aerial image, or choose a built-in demo image.")
else:
    source = st.radio("Comparison source", ["Upload your own pair", "Use built-in demo pair"], horizontal=True)
    before = None
    after = None

    if source == "Use built-in demo pair":
        selected_pair = st.selectbox("Choose a demo pair", list(PAIR_DEMOS.keys()))
        before_path, after_path = PAIR_DEMOS[selected_pair]
        before = load_local_image(before_path)
        after = load_local_image(after_path)
        c1, c2 = st.columns(2)
        c1.image(before, caption=f"{selected_pair} - before", use_container_width=True)
        c2.image(after, caption=f"{selected_pair} - after", use_container_width=True)

    before_file = st.file_uploader(
        "Upload the BEFORE image",
        type=["png", "jpg", "jpeg", "tif", "tiff", "webp"],
        key="before",
    )
    after_file = st.file_uploader(
        "Upload the AFTER image",
        type=["png", "jpg", "jpeg", "tif", "tiff", "webp"],
        key="after",
    )

    if source == "Upload your own pair" and before_file is not None and after_file is not None:
        before = read_image(before_file)
        after = read_image(after_file)

    if before is not None and after is not None:
        result = analyze_change(before, after, sensitivity=sensitivity, alpha=overlay_opacity)

        render_metric_grid(result.metrics)
        tab1, tab2, tab3, tab4 = st.tabs(["Before vs After", "Change Map", "Masks", "Downloads"])
        with tab1:
            c1, c2 = st.columns(2)
            c1.image(result.before, caption="Before", use_container_width=True)
            c2.image(result.after, caption="After", use_container_width=True)
        with tab2:
            st.image(result.change_overlay, caption="Change overlay", use_container_width=True)
            st.dataframe(metrics_dataframe(result.metrics), use_container_width=True, hide_index=True)
        with tab3:
            c1, c2 = st.columns(2)
            c1.image(mask_to_rgb(result.flood_gain_mask, (35, 195, 230)), caption="New water / flood gain", use_container_width=True)
            c2.image(mask_to_rgb(result.urban_change_mask, (255, 156, 70)), caption="Urban proxy change", use_container_width=True)
        with tab4:
            st.download_button(
                "Download change overlay (PNG)",
                data=to_png_bytes(result.change_overlay),
                file_name="floodwatch_change_overlay.png",
                mime="image/png",
            )
            st.download_button(
                "Download flood gain mask (PNG)",
                data=to_png_bytes(mask_to_rgb(result.flood_gain_mask, (35, 195, 230))),
                file_name="floodwatch_flood_gain.png",
                mime="image/png",
            )
            st.download_button(
                "Download urban change mask (PNG)",
                data=to_png_bytes(mask_to_rgb(result.urban_change_mask, (255, 156, 70))),
                file_name="floodwatch_urban_change.png",
                mime="image/png",
            )
    else:
        st.info("Upload both overhead images or choose a built-in demo pair to compare flood spread or urban change.")
