from __future__ import annotations

import pandas as pd
import streamlit as st


def render_metric_grid(metrics: dict) -> None:
    items = list(metrics.items())
    cols = st.columns(min(4, max(1, len(items))))
    for idx, (label, value) in enumerate(items):
        cols[idx % len(cols)].metric(label, value)


def metrics_dataframe(metrics: dict) -> pd.DataFrame:
    return pd.DataFrame({"Metric": list(metrics.keys()), "Value": list(metrics.values())})
