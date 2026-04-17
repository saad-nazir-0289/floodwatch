from __future__ import annotations

import streamlit as st


def render_metric_grid(metrics: dict) -> None:
    items = list(metrics.items())
    cols = st.columns(min(4, max(1, len(items))))
    for idx, (label, value) in enumerate(items):
        cols[idx % len(cols)].metric(label, value)


def metrics_dataframe(metrics: dict) -> list[dict[str, object]]:
    return [{"Metric": label, "Value": value} for label, value in metrics.items()]
