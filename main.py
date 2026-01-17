import math
from datetime import date
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


WEEKS_PER_MONTH = 4.348


@st.cache_data(show_spinner=False)
def build_who_reference() -> pd.DataFrame:
    percentiles = ["P3", "P15", "P50", "P85", "P97"]
    data_dir = Path("data/csv")
    datasets = [
        {
            "metric": "weight",
            "gender": "Boys",
            "path": data_dir
            / "boys_weight_0-13_weeks_pctl_tab_wfa_boys_p_0_13.csv",
            "age_col": "Week",
            "age_unit": "week",
        },
        {
            "metric": "weight",
            "gender": "Girls",
            "path": data_dir
            / "girls_weight_0-13_weeks_pctl_tab_wfa_girls_p_0_13.csv",
            "age_col": "Week",
            "age_unit": "week",
        },
        {
            "metric": "weight",
            "gender": "Boys",
            "path": data_dir / "boys_weight_0-5_years_pctl_tab_wfa_boys_p_0_5.csv",
            "age_col": "Month",
            "age_unit": "month",
            "min_age_months": 3.0,
        },
        {
            "metric": "weight",
            "gender": "Girls",
            "path": data_dir / "girls_weight_0-5_years_pctl_tab_wfa_girls_p_0_5.csv",
            "age_col": "Month",
            "age_unit": "month",
            "min_age_months": 3.0,
        },
        {
            "metric": "length_height",
            "gender": "Boys",
            "path": data_dir
            / "boys_length_0-13_weeks_pctl_tab_lhfa_boys_p_0_13.csv",
            "age_col": "Week",
            "age_unit": "week",
        },
        {
            "metric": "length_height",
            "gender": "Girls",
            "path": data_dir
            / "girls_length_0-13_weeks_pctl_tab_lhfa_girls_p_0_13.csv",
            "age_col": "Week",
            "age_unit": "week",
        },
        {
            "metric": "length_height",
            "gender": "Boys",
            "path": data_dir / "boys_length_0-2_years_pctl_tab_lhfa_boys_p_0_2.csv",
            "age_col": "Month",
            "age_unit": "month",
            "min_age_months": 3.0,
            "max_age_months": 23.999,
        },
        {
            "metric": "length_height",
            "gender": "Girls",
            "path": data_dir / "girls_length_0-2_years_pctl_tab_lhfa_girls_p_0_2.csv",
            "age_col": "Month",
            "age_unit": "month",
            "min_age_months": 3.0,
            "max_age_months": 23.999,
        },
        {
            "metric": "length_height",
            "gender": "Boys",
            "path": data_dir / "boys_height_2-5_years_pctl_tab_lhfa_boys_p_2_5.csv",
            "age_col": "Month",
            "min_age_months": 24.0,
        },
        {
            "metric": "length_height",
            "gender": "Girls",
            "path": data_dir / "girls_height_2-5_years_pctl_tab_lhfa_girls_p_2_5.csv",
            "age_col": "Month",
            "min_age_months": 24.0,
        },
    ]

    frames = []
    for dataset in datasets:
        df = pd.read_csv(dataset["path"])
        if dataset["age_unit"] == "week":
            df["age_months"] = df[dataset["age_col"]] / WEEKS_PER_MONTH
        else:
            df = df.rename(columns={dataset["age_col"]: "age_months"})
        if "min_age_months" in dataset:
            df = df[df["age_months"] >= dataset["min_age_months"]]
        if "max_age_months" in dataset:
            df = df[df["age_months"] <= dataset["max_age_months"]]
        df = df[["age_months"] + percentiles]
        melted = df.melt(
            id_vars="age_months",
            var_name="percentile",
            value_name="value",
        )
        melted["metric"] = dataset["metric"]
        melted["gender"] = dataset["gender"]
        frames.append(melted)

    return pd.concat(frames, ignore_index=True)


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
    if base.empty:
        st.info("Reference data for this chart is not available yet.")
        return
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
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
  --ink-900: #1f2328;
  --ink-700: #353b44;
  --ink-500: #59606b;
  --peach-50: #fff4e5;
  --peach-100: #fde3c7;
  --citrus-300: #f9b35d;
  --citrus-500: #f08a2b;
  --sage-100: #eaf1ea;
  --card: #fffdf8;
  --card-border: #e8dfd2;
  --shadow: 0 18px 36px rgba(42, 34, 18, 0.12);
}

.stApp {
  background:
    radial-gradient(circle at 12% 18%, #fff6e8 0%, #f7ead6 42%, #e7eef6 100%),
    linear-gradient(135deg, #fff7ec 0%, #f6efe3 50%, #eef2f6 100%);
  color: var(--ink-900);
}

h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
  font-family: "Fraunces", serif;
  letter-spacing: 0.2px;
  color: var(--ink-900);
}

h1, .stMarkdown h1 {
  font-size: 3.1rem;
  margin-bottom: 0.2rem;
}

h2, .stMarkdown h2 {
  font-size: 1.9rem;
}

h3, .stMarkdown h3 {
  font-size: 1.45rem;
}

body, p, label, div, .stMarkdown, .stTextInput, .stNumberInput, .stDateInput {
  font-family: "IBM Plex Sans", sans-serif;
  color: var(--ink-700);
}

.section-card {
  padding: 1.4rem 1.8rem;
  background: var(--card);
  border: 1px solid var(--card-border);
  border-radius: 22px;
  box-shadow: var(--shadow);
}

.stMarkdown p {
  font-size: 1.02rem;
}

.stCaption {
  color: var(--ink-500);
}

.stRadio label {
  color: var(--ink-700);
  font-weight: 500;
}

div[data-baseweb="input"] input,
div[data-baseweb="input"] input:focus,
div[data-baseweb="input"] input:hover,
div[data-baseweb="select"] input {
  background: #ffffff;
  color: var(--ink-900);
  border: 1px solid #d6cbbb;
  box-shadow: inset 0 1px 2px rgba(24, 20, 12, 0.08);
}

div[data-baseweb="input"] input:focus,
div[data-baseweb="select"] input:focus {
  border-color: var(--citrus-500);
  box-shadow: 0 0 0 3px rgba(240, 138, 43, 0.2);
}

.stButton > button {
  background: linear-gradient(135deg, #f2a444, #f07b2d);
  color: #1f2328;
  border: none;
  border-radius: 14px;
  font-weight: 600;
  padding: 0.55rem 1.4rem;
  box-shadow: 0 10px 20px rgba(240, 138, 43, 0.25);
}

.stButton > button:hover {
  filter: brightness(1.03);
  transform: translateY(-1px);
}

.stDataFrame {
  border: 1px solid #e5d8c8;
  border-radius: 16px;
  overflow: hidden;
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
        if "date_of_birth" not in st.session_state:
            st.session_state.date_of_birth = date.today()
        date_of_birth = st.date_input(
            "Date of birth", value=st.session_state.date_of_birth
        )
        st.session_state.date_of_birth = date_of_birth
        st.caption("Charts adapt to selected gender.")
        st.markdown("---")
        st.markdown("**Note**: Curves use WHO reference data from the CSVs in `data/csv`.")

    with col_entry:
        st.subheader("Add a measurement")
        if "measurements" not in st.session_state:
            st.session_state.measurements = []

        with st.form("measurement-form", clear_on_submit=True):
            entry_date = st.date_input("Measurement date", value=date.today())
            weight = st.number_input("Weight (kg)", min_value=0.0, max_value=40.0, step=0.1)
            age_days = (entry_date - st.session_state.date_of_birth).days
            age_months = max(age_days / 30.4375, 0)
            st.caption(f"Age at measurement: {age_months:.1f} months")
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
            if entry_date < st.session_state.date_of_birth:
                st.error("Measurement date cannot be before date of birth.")
            else:
                st.session_state.measurements.append(
                    {
                        "date": entry_date,
                        "age_months": round(age_months, 2),
                        "weight": weight,
                        "length_height": length_height,
                        "head": head,
                    }
                )
                st.success("Measurement added.")

    st.markdown("</div>", unsafe_allow_html=True)


measurements_df = pd.DataFrame(st.session_state.measurements)

st.markdown("### Measurement log")
if measurements_df.empty:
    empty_df = pd.DataFrame(
        [
            {"date": "", "age_months": "", "weight": "", "length_height": "", "head": ""}
            for _ in range(3)
        ]
    )
    st.dataframe(empty_df, use_container_width=True, hide_index=True)
else:
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
