import streamlit as st


st.set_page_config(page_title="Project Background", page_icon="📘", layout="wide")

st.title("Project Background")
st.caption("A condensed version of the deck narrative used to frame the demo.")

st.subheader("Pakistan-wide problem framing")
st.markdown(
    """
    - Pakistan faces recurring flood shocks alongside rapid urban expansion [1][2][3].
    - The 2022 floods affected 33 million people and caused more than US$14.9B in damages [1].
    - Urban population reached 98.4 million in 2024, increasing exposure in dense and low-service settlements [2][3][4].
    - Monitoring is often delayed, fragmented, or too coarse for neighborhood-scale decisions.
    """
)

st.subheader("Why fusion-inspired monitoring")
st.markdown(
    """
    - High-resolution imagery gives better visual detail, but not always daily continuity.
    - High-frequency imagery covers large areas often, but can be too coarse for local response.
    - A fusion mindset helps bridge the spatial-temporal gap and supports response plus planning.
    """
)

st.subheader("Selected references")
refs = [
    "[1] Pakistan Floods 2022: Post-Disaster Needs Assessment (PDNA), 2022.",
    "[2] World Bank urban population data for Pakistan.",
    "[3] World Bank urban population share data for Pakistan.",
    "[4] World Bank slum population data for Pakistan.",
    "[5] F. Gao et al., STARFM, Remote Sensing of Environment, 2006.",
    "[6] X. Zhu et al., ESTARFM, Remote Sensing of Environment, 2010.",
    "[7] Z. Lian et al., Deep learning-based spatiotemporal fusion review, Sensors, 2025.",
    "[8] C. Wang et al., Sentinel-1 and Sentinel-2 flood inundation mapping, ISPRS JPRS, 2021.",
]
for ref in refs:
    st.markdown(f"- {ref}")
