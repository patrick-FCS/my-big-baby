import math
from datetime import date

import altair as alt
import pandas as pd
import streamlit as st


def build_who_reference() -> pd.DataFrame:
    # Simplified WHO-style curves for demo purposes.
    ages = [0, 1, 2, 3, 4, 5, 6, 9, 12, 18, 24, 36, 48, 60]
    percentiles = ["P3", "P15", "P50", "P85", "P97"]

    def rows_for(metric, gender, values_by_percentile):
        rows = []
        for p in percentiles:
            for age, value in zip(ages, values_by_percentile[p]):
                rows.append(
                    {
                        "metric": metric,
                        "gender": gender,
                        "percentile": p,
                        "age_months": age,
                        "value": value,
                    }
                )
        return rows

    weight_boys = {
        "P3": [2.5, 3.1, 3.8, 4.4, 4.9, 5.4, 5.8, 6.8, 7.7, 8.9, 10.1, 12.1, 13.9, 15.7],
        "P15": [2.9, 3.6, 4.3, 4.9, 5.4, 5.9, 6.4, 7.5, 8.5, 9.8, 11.1, 13.4, 15.2, 17.0],
        "P50": [3.4, 4.2, 5.0, 5.7, 6.2, 6.7, 7.2, 8.4, 9.5, 10.9, 12.2, 14.3, 16.3, 18.2],
        "P85": [4.1, 4.9, 5.8, 6.5, 7.0, 7.6, 8.1, 9.4, 10.7, 12.2, 13.6, 15.8, 18.0, 20.2],
        "P97": [4.6, 5.5, 6.4, 7.1, 7.7, 8.3, 8.9, 10.3, 11.6, 13.2, 14.8, 17.1, 19.6, 22.2],
    }
    weight_girls = {
        "P3": [2.4, 3.0, 3.6, 4.1, 4.6, 5.0, 5.4, 6.3, 7.1, 8.1, 9.2, 11.1, 12.8, 14.5],
        "P15": [2.8, 3.4, 4.1, 4.6, 5.0, 5.5, 5.9, 6.9, 7.8, 8.9, 10.1, 12.1, 13.9, 15.7],
        "P50": [3.2, 3.9, 4.6, 5.1, 5.6, 6.1, 6.5, 7.6, 8.6, 9.8, 11.0, 13.0, 14.9, 16.8],
        "P85": [3.8, 4.6, 5.3, 5.9, 6.4, 6.9, 7.4, 8.6, 9.7, 11.1, 12.4, 14.6, 16.7, 18.9],
        "P97": [4.3, 5.1, 5.9, 6.5, 7.0, 7.6, 8.1, 9.4, 10.6, 12.2, 13.6, 16.0, 18.5, 21.0],
    }
    length_boys = {
        "P3": [46.5, 50.2, 53.2, 55.6, 57.6, 59.2, 60.7, 65.2, 69.3, 76.0, 81.5, 90.7, 98.5, 105.6],
        "P15": [48.2, 51.9, 54.9, 57.3, 59.3, 61.0, 62.6, 67.3, 71.6, 78.5, 84.2, 93.8, 101.9, 109.2],
        "P50": [49.9, 53.7, 56.7, 59.2, 61.3, 63.0, 64.7, 69.1, 73.4, 80.5, 86.4, 96.1, 104.2, 111.5],
        "P85": [51.8, 55.6, 58.8, 61.4, 63.6, 65.4, 67.2, 71.9, 76.2, 83.5, 89.7, 100.0, 108.4, 115.8],
        "P97": [53.1, 57.1, 60.3, 62.9, 65.1, 66.9, 68.8, 73.8, 78.1, 85.6, 92.1, 102.8, 111.3, 118.9],
    }
    length_girls = {
        "P3": [45.6, 49.3, 52.2, 54.7, 56.7, 58.4, 60.0, 64.5, 68.9, 75.6, 81.3, 90.2, 98.0, 105.2],
        "P15": [47.3, 51.0, 54.0, 56.5, 58.6, 60.3, 62.0, 66.8, 71.3, 78.4, 84.3, 93.6, 101.6, 109.0],
        "P50": [49.1, 52.9, 55.8, 58.4, 60.6, 62.4, 64.0, 68.7, 73.2, 80.7, 86.9, 96.8, 105.0, 112.6],
        "P85": [51.0, 54.9, 57.9, 60.6, 62.8, 64.7, 66.4, 71.6, 76.2, 84.1, 90.6, 101.0, 109.6, 117.5],
        "P97": [52.4, 56.3, 59.5, 62.1, 64.4, 66.3, 68.1, 73.7, 78.4, 86.6, 93.4, 104.3, 113.1, 121.3],
    }
    head_boys = {
        "P3": [32.1, 33.9, 35.1, 36.0, 36.8, 37.4, 38.0, 39.5, 40.9, 42.7, 44.0, 46.0, 47.5, 48.8],
        "P15": [33.1, 34.8, 36.0, 36.9, 37.7, 38.3, 38.9, 40.4, 41.8, 43.6, 44.9, 46.8, 48.2, 49.5],
        "P50": [34.5, 36.1, 37.3, 38.2, 39.0, 39.6, 40.2, 41.7, 43.0, 44.8, 46.1, 47.9, 49.3, 50.5],
        "P85": [35.8, 37.5, 38.7, 39.6, 40.4, 41.0, 41.6, 43.1, 44.4, 46.2, 47.5, 49.2, 50.5, 51.7],
        "P97": [36.7, 38.4, 39.6, 40.5, 41.3, 41.9, 42.5, 44.0, 45.3, 47.0, 48.3, 50.0, 51.2, 52.4],
    }
    head_girls = {
        "P3": [31.5, 33.3, 34.5, 35.4, 36.2, 36.8, 37.4, 38.9, 40.3, 42.1, 43.4, 45.5, 47.0, 48.2],
        "P15": [32.4, 34.1, 35.3, 36.2, 37.0, 37.6, 38.2, 39.7, 41.1, 42.9, 44.2, 46.2, 47.6, 48.8],
        "P50": [33.7, 35.4, 36.6, 37.5, 38.3, 38.9, 39.5, 41.0, 42.4, 44.1, 45.4, 47.3, 48.7, 49.9],
        "P85": [35.0, 36.7, 37.9, 38.8, 39.6, 40.2, 40.8, 42.3, 43.7, 45.4, 46.7, 48.6, 49.9, 51.1],
        "P97": [35.9, 37.6, 38.8, 39.7, 40.5, 41.1, 41.7, 43.2, 44.6, 46.2, 47.5, 49.3, 50.6, 51.8],
    }

    rows = []
    rows += rows_for("weight", "Boys", weight_boys)
    rows += rows_for("weight", "Girls", weight_girls)
    rows += rows_for("length_height", "Boys", length_boys)
    rows += rows_for("length_height", "Girls", length_girls)
    rows += rows_for("head", "Boys", head_boys)
    rows += rows_for("head", "Girls", head_girls)
    return pd.DataFrame(rows)


def linear_prediction(points, horizon_months=12):
    xs = [p["age_months"] for p in points]
    ys = [p["value"] for p in points]
    n = len(xs)
    if n < 2:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    if sxx == 0:
        return None
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / sxx
    intercept = mean_y - slope * mean_x
    residuals = [y - (intercept + slope * x) for x, y in zip(xs, ys)]
    s_err = math.sqrt(sum(r ** 2 for r in residuals) / max(n - 2, 1))

    x_min = min(xs)
    x_max = max(xs) + horizon_months
    ages = list(range(int(x_min), int(x_max) + 1))
    preds = []
    for age in ages:
        pred = intercept + slope * age
        se_pred = s_err * math.sqrt(1 + (1 / n) + ((age - mean_x) ** 2 / sxx))
        preds.append(
            {
                "age_months": age,
                "prediction": pred,
                "lower": pred - se_pred,
                "upper": pred + se_pred,
            }
        )
    return preds


def chart_for_metric(
    metric,
    gender,
    reference_df,
    measurements_df,
    title,
    unit,
):
    base = reference_df[
        (reference_df["metric"] == metric) & (reference_df["gender"] == gender)
    ]
    percentile_order = ["P3", "P15", "P50", "P85", "P97"]
    color_scale = alt.Scale(
        domain=percentile_order,
        range=["#9fa7b5", "#7d8793", "#3f4854", "#7d8793", "#9fa7b5"],
    )

    lines = (
        alt.Chart(base)
        .mark_line(interpolate="monotone", opacity=0.7)
        .encode(
            x=alt.X("age_months:Q", title="Age (months)"),
            y=alt.Y("value:Q", title=f"{title} ({unit})"),
            color=alt.Color("percentile:N", scale=color_scale, sort=percentile_order),
            strokeWidth=alt.condition(
                alt.datum.percentile == "P50",
                alt.value(2.5),
                alt.value(1.2),
            ),
        )
    )

    overlays = []
    if not measurements_df.empty:
        dots = (
            alt.Chart(measurements_df)
            .mark_point(size=80, color="#d8563f", filled=True)
            .encode(
                x="age_months:Q",
                y=alt.Y("value:Q", title=f"{title} ({unit})"),
                tooltip=["date:T", "age_months:Q", "value:Q"],
            )
        )
        overlays.append(dots)

        if len(measurements_df) >= 2:
            line = (
                alt.Chart(measurements_df)
                .mark_line(color="#d8563f", strokeWidth=2)
                .encode(x="age_months:Q", y="value:Q")
            )
            overlays.append(line)

            preds = linear_prediction(measurements_df.to_dict("records"))
            if preds:
                pred_df = pd.DataFrame(preds)
                band = (
                    alt.Chart(pred_df)
                    .mark_area(opacity=0.15, color="#d8563f")
                    .encode(
                        x="age_months:Q",
                        y="lower:Q",
                        y2="upper:Q",
                    )
                )
                pred_line = (
                    alt.Chart(pred_df)
                    .mark_line(color="#d8563f", strokeDash=[5, 4])
                    .encode(x="age_months:Q", y="prediction:Q")
                )
                overlays.extend([band, pred_line])

    chart = lines
    for overlay in overlays:
        chart = chart + overlay

    chart = (
        chart.properties(height=300)
        .configure_axis(labelFont="Alegreya Sans", titleFont="Alegreya Sans")
        .configure_legend(title=None, labelFont="Alegreya Sans")
    )
    st.altair_chart(chart, use_container_width=True)


st.set_page_config(page_title="My big baby", page_icon="🍼", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Alegreya+Sans:wght@400;600&family=Fraunces:opsz,wght@9..144,600&display=swap');

.stApp {
  background: radial-gradient(circle at 15% 20%, #fff7e8 0%, #f4efe6 45%, #e9f0f6 100%);
  color: #2c2f36;
}

h1, h2, h3, .stMarkdown h1, .stMarkdown h2 {
  font-family: "Fraunces", serif;
  letter-spacing: 0.3px;
}

body, p, label, div {
  font-family: "Alegreya Sans", sans-serif;
}

.section-card {
  padding: 1.2rem 1.6rem;
  background: #ffffffcc;
  border: 1px solid #e3dfd7;
  border-radius: 18px;
  box-shadow: 0 12px 28px rgba(36, 35, 30, 0.08);
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("My big baby")
st.markdown(
    "Track your child's growth over time and see measurements compared to WHO-style charts. "
    "Add points to get a trend line and a simple future projection."
)

with st.container():
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    col_profile, col_entry = st.columns([1, 2], gap="large")

    with col_profile:
        st.subheader("Child profile")
        gender = st.radio("Gender", ["Girls", "Boys"], horizontal=True)
        st.caption("Charts adapt to selected gender.")
        st.markdown("---")
        st.markdown("**Note**: Curves are simplified WHO-style references for demo use.")

    with col_entry:
        st.subheader("Add a measurement")
        if "measurements" not in st.session_state:
            st.session_state.measurements = []

        with st.form("measurement-form", clear_on_submit=True):
            entry_date = st.date_input("Measurement date", value=date.today())
            age_months = st.number_input("Age (months)", min_value=0, max_value=60, value=6)
            weight = st.number_input("Weight (kg)", min_value=0.0, max_value=40.0, step=0.1)
            if age_months <= 24:
                length_height = st.number_input(
                    "Length (cm)", min_value=30.0, max_value=120.0, step=0.1
                )
            else:
                length_height = st.number_input(
                    "Height (cm)", min_value=60.0, max_value=140.0, step=0.1
                )
            head = st.number_input(
                "Head circumference (cm)", min_value=25.0, max_value=60.0, step=0.1
            )
            submitted = st.form_submit_button("Add measurement")

        if submitted:
            st.session_state.measurements.append(
                {
                    "date": entry_date,
                    "age_months": age_months,
                    "weight": weight,
                    "length_height": length_height,
                    "head": head,
                }
            )
            st.success("Measurement added.")

    st.markdown("</div>", unsafe_allow_html=True)


measurements_df = pd.DataFrame(st.session_state.measurements)

if not measurements_df.empty:
    st.markdown("### Measurement log")
    st.dataframe(measurements_df, use_container_width=True, hide_index=True)

st.markdown("### WHO-style growth charts")
reference_df = build_who_reference()

cols = st.columns(3, gap="large")
with cols[0]:
    st.markdown("#### Weight-for-age")
    weight_df = (
        measurements_df[["date", "age_months", "weight"]]
        .rename(columns={"weight": "value"})
        .dropna()
        if not measurements_df.empty
        else pd.DataFrame(columns=["date", "age_months", "value"])
    )
    chart_for_metric(
        "weight",
        gender,
        reference_df,
        weight_df,
        "Weight",
        "kg",
    )

with cols[1]:
    st.markdown("#### Length/height-for-age")
    length_df = (
        measurements_df[["date", "age_months", "length_height"]]
        .rename(columns={"length_height": "value"})
        .dropna()
        if not measurements_df.empty
        else pd.DataFrame(columns=["date", "age_months", "value"])
    )
    chart_for_metric(
        "length_height",
        gender,
        reference_df,
        length_df,
        "Length/Height",
        "cm",
    )

with cols[2]:
    st.markdown("#### Head circumference-for-age")
    head_df = (
        measurements_df[["date", "age_months", "head"]]
        .rename(columns={"head": "value"})
        .dropna()
        if not measurements_df.empty
        else pd.DataFrame(columns=["date", "age_months", "value"])
    )
    chart_for_metric(
        "head",
        gender,
        reference_df,
        head_df,
        "Head circumference",
        "cm",
    )

st.markdown(
    """
**Projection guidance**: The dashed line is a simple linear forecast with a light uncertainty band.
It is not a medical prediction and should not replace professional advice.
"""
)
