from pathlib import Path

import streamlit as st


ASSET_DIR = Path(__file__).parent / "assets"


st.set_page_config(
    page_title="FloodWatch Pakistan",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(54, 153, 255, 0.15), transparent 28%),
                linear-gradient(160deg, #071526 0%, #0d2742 48%, #13385c 100%);
            color: #eaf2ff;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .hero {
            border: 1px solid rgba(120, 180, 255, 0.22);
            background: linear-gradient(135deg, rgba(8, 22, 40, 0.92), rgba(17, 54, 90, 0.88));
            border-radius: 24px;
            padding: 2rem;
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.22);
        }
        .hero h1 {
            font-size: 3rem;
            margin-bottom: 0.5rem;
            color: #f4f8ff;
        }
        .hero p {
            color: #bfd5f2;
            font-size: 1.05rem;
            line-height: 1.6;
        }
        .metric-card {
            border-radius: 18px;
            padding: 1rem 1.1rem;
            background: rgba(8, 22, 40, 0.72);
            border: 1px solid rgba(120, 180, 255, 0.18);
            min-height: 128px;
        }
        .metric-card h3 {
            color: #7dd3fc;
            margin-bottom: 0.35rem;
        }
        .metric-card p {
            color: #dcecff;
            margin: 0;
        }
        .small-note {
            color: #bdd1e8;
            font-size: 0.95rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


load_css()

left, right = st.columns([1.25, 1], gap="large")

with left:
    st.markdown(
        """
        <div class="hero">
            <h1>Indus Urban FloodWatch</h1>
            <p>
                A Streamlit demo for overhead imagery analysis focused on flood extent,
                water spread, urban footprint proxies, and before/after change detection.
                Upload satellite, drone, or aerial imagery to generate explainable overlays
                and quick decision-support metrics.
            </p>
            <p class="small-note">
                Short app label: <strong>FloodWatch Pakistan</strong> · Supported imagery:
                satellite, drone, and aerial views only.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    hero_path = ASSET_DIR / "hero.png"
    if hero_path.exists():
        st.image(str(hero_path), use_container_width=True)
    else:
        st.info("Add `assets/hero.png` for the branded hero visual.")

st.write("")

col1, col2, col3 = st.columns(3, gap="medium")
with col1:
    metric_card("Single Image Analysis", "Estimate water/flood masks and built-up proxies from one overhead image.")
with col2:
    metric_card("Before/After Change", "Compare two overhead images to reveal flood spread or urban expansion signals.")
with col3:
    metric_card("Exportable Outputs", "Download polished overlay maps, masks, and change visuals for presentations and demos.")

st.write("")
st.subheader("What this demo does")

overview_left, overview_right = st.columns([1.15, 1], gap="large")
with overview_left:
    st.markdown(
        """
        - Detects likely water bodies and flood-like regions using color, texture, and morphology.
        - Builds a built-up / urban footprint proxy from brightness, edge density, and structural texture.
        - Creates change maps for before/after imagery using aligned differencing and structural similarity cues.
        - Reports quick metrics such as estimated water coverage, built-up proxy coverage, changed area, and connected flood regions.
        - Produces demo-friendly thematic outputs without requiring GPUs or paid APIs.
        """
    )

with overview_right:
    st.markdown(
        """
        **Use it for**

        - flood response walkthroughs
        - urban exposure storytelling
        - hackathon or capstone demos
        - stakeholder pitches and rapid prototypes

        **Not for**

        - cadastral-grade mapping
        - certified hazard products
        - arbitrary ground-level phone photos
        """
    )

st.subheader("How to use")
steps = st.columns(4)
steps[0].info("1. Go to `Upload & Analyze`.")
steps[1].info("2. Upload one image or a before/after pair.")
steps[2].info("3. Tune sensitivity and overlay settings.")
steps[3].info("4. Review masks, metrics, and downloads.")

st.caption(
    "This demo is designed for satellite, drone, and aerial imagery only. Results are explainable and fast, but still approximate."
)
