import streamlit as st


st.set_page_config(page_title="FAQ", page_icon="❓", layout="wide")

st.title("FAQ")
st.caption("Quick answers for demo users and reviewers.")

questions = {
    "What kind of images should I use?": "Use overhead satellite, drone, or aerial imagery with visible water boundaries and built structures.",
    "Can I upload phone photos?": "No. The demo is intentionally limited to overhead imagery because the segmentation logic is designed for map-like views.",
    "Is this a production flood model?": "No. It is a fast, explainable demo for visual analysis and storytelling.",
    "What does the built-up layer mean?": "It is a built-up proxy, not a parcel-accurate land-cover classification.",
    "Why do built-in demo images exist?": "They let anyone test the app instantly, even if they do not have imagery ready.",
}

for question, answer in questions.items():
    with st.expander(question):
        st.write(answer)
