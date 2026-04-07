import streamlit as st


st.set_page_config(page_title="Methodology", page_icon="🛰️", layout="wide")

st.title("Methodology")
st.caption("Demo-grade visual analytics inspired by the FloodWatch presentation narrative.")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Water / Flood Detection")
    st.markdown(
        """
        - RGB images are enhanced for contrast and tonal separation.
        - Water-like regions are estimated using hue, saturation, brightness, Lab color cues, and low-texture smoothing.
        - Morphological cleanup removes tiny noisy regions and keeps coherent flood-like blobs.
        - Connected components are used to summarize possible flood regions.
        """
    )

    st.subheader("Urban / Built-up Proxy")
    st.markdown(
        """
        - The app estimates an urban footprint proxy rather than a cadastral land-cover classification.
        - Bright surfaces, edge density, local variance, and structural gradients act as signals for built-up presence.
        - This is useful for demo storytelling around exposure and urban expansion.
        """
    )

with col2:
    st.subheader("Before / After Change Logic")
    st.markdown(
        """
        - Images are resized to a common frame.
        - Absolute grayscale differencing and structural similarity cues highlight changed regions.
        - Additional water and urban masks estimate where flood gain or built-up proxy change may have occurred.
        - Results are intended for fast visual interpretation, not formal geospatial registration workflows.
        """
    )

    st.subheader("Why this works for a Streamlit demo")
    st.markdown(
        """
        - CPU-first and lightweight
        - no GPU required
        - no paid APIs required
        - explainable outputs for judges, mentors, and stakeholders
        - suitable for Streamlit Community Cloud deployment
        """
    )

st.subheader("Limitations")
st.warning(
    "Best results come from overhead satellite, drone, or aerial images with visible water boundaries and built structures. "
    "The app is not a calibrated hydrology model, a GIS-grade land-cover classifier, or a replacement for field validation."
)
