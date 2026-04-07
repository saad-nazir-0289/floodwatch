from pathlib import Path

import streamlit as st

from utils.image_processing import (
    analyze_change,
    analyze_single_image,
    mask_to_rgb,
    read_image,
    to_png_bytes,
)
from utils.visualization import metrics_dataframe, render_metric_grid


st.set_page_config(page_title="FloodWatch Pakistan", page_icon="🌊", layout="wide")

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


def sample_image_panel() -> None:
    asset_dir = Path(__file__).resolve().parent.parent / "assets"
    samples = sorted(asset_dir.glob("sample_*.png"))
    if not samples:
        return
    st.subheader("Sample imagery")
    cols = st.columns(len(samples))
    for col, sample in zip(cols, samples):
        col.image(str(sample), caption=sample.stem.replace("_", " "), use_container_width=True)


sample_image_panel()

if mode == "Single Image Analysis":
    uploaded = st.file_uploader(
        "Upload one overhead image",
        type=["png", "jpg", "jpeg", "tif", "tiff", "webp"],
        accept_multiple_files=False,
    )

    if uploaded is not None:
        image = read_image(uploaded)
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
        st.info("Upload one satellite, drone, or aerial image to start analysis.")
else:
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

    if before_file is not None and after_file is not None:
        before = read_image(before_file)
        after = read_image(after_file)
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
        st.info("Upload both overhead images to compare flood spread or urban change.")
