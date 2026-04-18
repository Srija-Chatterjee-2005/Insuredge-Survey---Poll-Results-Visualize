import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Insuredge Analytics Dashboard", layout="wide")

# -----------------------------
# HELPERS
# -----------------------------
def load_csv(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv("data/OIMS(gform_responses).csv")
    df.columns = df.columns.str.strip()
    return df

def find_column(columns, keywords):
    for col in columns:
        col_lower = col.lower()
        if all(keyword in col_lower for keyword in keywords):
            return col
    return None

def find_columns_any(columns, keywords):
    return [col for col in columns if any(k in col.lower() for k in keywords)]

def calculate_nps(series):
    series = pd.to_numeric(series, errors="coerce")
    total = series.notna().sum()
    if total == 0:
        return 0
    promoters = (series >= 4).sum()
    detractors = (series <= 2).sum()
    return ((promoters - detractors) / total) * 100

def classify_nps_group(score):
    if pd.isna(score):
        return "Unknown"
    if score >= 4:
        return "Promoter"
    elif score == 3:
        return "Passive"
    else:
        return "Detractor"

def classify_satisfaction(score):
    if pd.isna(score):
        return "Unknown"
    if score >= 4:
        return "High"
    elif score == 3:
        return "Medium"
    else:
        return "Low"

def fig_to_download(fig, filename, label):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    st.download_button(
        label=label,
        data=buf,
        file_name=filename,
        mime="image/png"
    )

def generate_insights(filtered_df, rating_cols, recommend_col, usage_col):
    insights = []

    if usage_col and usage_col in filtered_df.columns:
        usage_counts = filtered_df[usage_col].value_counts()
        if not usage_counts.empty:
            insights.append(f"Most common usage pattern: **{usage_counts.idxmax()}**.")

    if rating_cols:
        avg_ratings = filtered_df[rating_cols].mean().sort_values(ascending=False)
        if not avg_ratings.empty:
            insights.append(f"Highest rated area: **{avg_ratings.idxmax()}** ({avg_ratings.max():.2f}).")
            insights.append(f"Lowest rated area: **{avg_ratings.idxmin()}** ({avg_ratings.min():.2f}).")

    if recommend_col and recommend_col in filtered_df.columns:
        nps_score = calculate_nps(filtered_df[recommend_col])
        if nps_score > 50:
            insights.append(f"NPS-style score is **{nps_score:.2f}**, showing strong loyalty.")
        elif nps_score > 0:
            insights.append(f"NPS-style score is **{nps_score:.2f}**, showing moderate loyalty.")
        else:
            insights.append(f"NPS-style score is **{nps_score:.2f}**, showing poor loyalty and improvement need.")

    return insights

# -----------------------------
# DATA INPUT
# -----------------------------
st.sidebar.title("Data Input")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
st.sidebar.caption("You can upload a CSV exported from Google Forms.")

df = load_csv(uploaded_file)

st.title("📊 Insuredge Survey Analytics Dashboard")
st.markdown("Interactive dashboard for survey response analysis, satisfaction tracking, and user feedback insights.")

# -----------------------------
# AUTO-DETECT COLUMNS
# -----------------------------
columns = df.columns.tolist()

age_col = next((col for col in columns if col.lower() == "age"), None)

usage_col = next(
    (
        col for col in columns
        if "how often do you use" in col.lower()
        or "use our online insurance management system" in col.lower()
    ),
    None
)

recommend_col = next((col for col in columns if "recommend" in col.lower()), None)

payment_col = next(
    (
        col for col in columns
        if "premium payments" in col.lower() or "payment" in col.lower()
    ),
    None
)

claim_col = next(
    (
        col for col in columns
        if "claim settlement" in col.lower() or "claims" in col.lower()
    ),
    None
)

rating_cols = [
    col for col in columns
    if ("rate" in col.lower() or "satisfied" in col.lower() or "recommend" in col.lower())
]

feedback_col = next(
    (
        col for col in columns
        if "feedback" in col.lower() or "suggest" in col.lower() or "improvement" in col.lower()
    ),
    None
)

# Convert numeric columns
for col in rating_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -----------------------------
# DERIVED COLUMNS
# -----------------------------
if recommend_col and recommend_col in df.columns:
    df["NPS Group"] = df[recommend_col].apply(classify_nps_group)

if recommend_col and recommend_col in df.columns:
    df["Satisfaction Segment"] = df[recommend_col].apply(classify_satisfaction)

# -----------------------------
# FILTERS
# -----------------------------
st.sidebar.title("Filters")
filtered_df = df.copy()

if age_col and age_col in filtered_df.columns:
    age_values = sorted(filtered_df[age_col].dropna().astype(str).unique().tolist())
    selected_age = st.sidebar.multiselect("Filter by Age", age_values, default=age_values)
    filtered_df = filtered_df[filtered_df[age_col].astype(str).isin(selected_age)]

if usage_col and usage_col in filtered_df.columns:
    usage_values = filtered_df[usage_col].dropna().astype(str).unique().tolist()
    selected_usage = st.sidebar.multiselect("Filter by Usage Frequency", usage_values, default=usage_values)
    filtered_df = filtered_df[filtered_df[usage_col].astype(str).isin(selected_usage)]

if recommend_col and recommend_col in filtered_df.columns:
    rec_series = pd.to_numeric(filtered_df[recommend_col], errors="coerce")
    rec_min = int(rec_series.min()) if rec_series.notna().any() else 1
    rec_max = int(rec_series.max()) if rec_series.notna().any() else 5
    selected_range = st.sidebar.slider(
        "Recommendation Score Range",
        min_value=rec_min,
        max_value=rec_max,
        value=(rec_min, rec_max)
    )
    filtered_df = filtered_df[
        pd.to_numeric(filtered_df[recommend_col], errors="coerce").between(selected_range[0], selected_range[1], inclusive="both")
    ]

if payment_col and payment_col in filtered_df.columns:
    payment_values = sorted(filtered_df[payment_col].dropna().astype(str).unique().tolist())
    selected_payment = st.sidebar.multiselect("Filter by Payment Experience", payment_values, default=payment_values)
    filtered_df = filtered_df[filtered_df[payment_col].astype(str).isin(selected_payment)]

if claim_col and claim_col in filtered_df.columns:
    claim_values = sorted(filtered_df[claim_col].dropna().astype(str).unique().tolist())
    selected_claim = st.sidebar.multiselect("Filter by Claim Settlement Experience", claim_values, default=claim_values)
    filtered_df = filtered_df[filtered_df[claim_col].astype(str).isin(selected_claim)]

if "Satisfaction Segment" in filtered_df.columns:
    seg_values = ["Low", "Medium", "High", "Unknown"]
    selected_seg = st.sidebar.multiselect("Filter by Satisfaction Segment", seg_values, default=seg_values)
    filtered_df = filtered_df[filtered_df["Satisfaction Segment"].isin(selected_seg)]

if "NPS Group" in filtered_df.columns:
    nps_values = ["Promoter", "Passive", "Detractor", "Unknown"]
    selected_nps_group = st.sidebar.multiselect("Filter by NPS Group", nps_values, default=nps_values)
    filtered_df = filtered_df[filtered_df["NPS Group"].isin(selected_nps_group)]

# -----------------------------
# KPI SECTION
# -----------------------------
st.subheader("Overview")
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Responses", len(filtered_df))

if rating_cols:
    overall_avg = filtered_df[rating_cols].mean().mean()
    k2.metric("Average Rating", f"{overall_avg:.2f}")
else:
    k2.metric("Average Rating", "N/A")

if recommend_col and recommend_col in filtered_df.columns:
    nps_score = calculate_nps(filtered_df[recommend_col])
    k3.metric("NPS-Style Score", f"{nps_score:.2f}")
else:
    k3.metric("NPS-Style Score", "N/A")

if usage_col and usage_col in filtered_df.columns and not filtered_df[usage_col].dropna().empty:
    k4.metric("Top Usage Group", filtered_df[usage_col].value_counts().idxmax())
else:
    k4.metric("Top Usage Group", "N/A")

# -----------------------------
# CHARTS
# -----------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Usage Frequency")
    if usage_col and usage_col in filtered_df.columns:
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        filtered_df[usage_col].value_counts().plot(kind="bar", ax=ax1)
        ax1.set_ylabel("Count")
        ax1.set_xlabel("Usage Frequency")
        st.pyplot(fig1)
        fig_to_download(fig1, "usage_frequency.png", "Download Usage Chart")
    else:
        st.warning("Usage column not found")

with c2:
    st.subheader("Age Distribution")
    if age_col and age_col in filtered_df.columns:
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        filtered_df[age_col].value_counts().plot(kind="bar", ax=ax2)
        ax2.set_ylabel("Count")
        ax2.set_xlabel("Age Group")
        st.pyplot(fig2)
        fig_to_download(fig2, "age_distribution.png", "Download Age Chart")
    else:
        st.warning("Age column not found")

st.subheader("Recommendation Distribution")
if recommend_col and recommend_col in filtered_df.columns:
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    filtered_df[recommend_col].value_counts().sort_index().plot(kind="bar", ax=ax3)
    ax3.set_ylabel("Count")
    ax3.set_xlabel("Recommendation Score")
    st.pyplot(fig3)
    fig_to_download(fig3, "recommendation_distribution.png", "Download Recommendation Chart")
else:
    st.warning("Recommendation column not found")

st.subheader("Average Ratings Comparison")
if rating_cols:
    avg_ratings = filtered_df[rating_cols].mean().sort_values(ascending=False)
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    avg_ratings.plot(kind="bar", ax=ax4)
    ax4.set_ylabel("Average Score")
    ax4.set_xlabel("Question")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig4)
    fig_to_download(fig4, "average_ratings_comparison.png", "Download Ratings Chart")

    st.dataframe(
        avg_ratings.reset_index().rename(columns={"index": "Question", 0: "Average Score"}),
        use_container_width=True
    )
else:
    st.warning("No rating columns found")

# -----------------------------
# SEGMENTATION PANELS
# -----------------------------
s1, s2 = st.columns(2)

with s1:
    st.subheader("Satisfaction Segmentation")
    if "Satisfaction Segment" in filtered_df.columns:
        seg_counts = filtered_df["Satisfaction Segment"].value_counts()
        st.bar_chart(seg_counts)
    else:
        st.info("Satisfaction segmentation unavailable.")

with s2:
    st.subheader("Promoter / Passive / Detractor Grouping")
    if "NPS Group" in filtered_df.columns:
        nps_counts = filtered_df["NPS Group"].value_counts()
        st.bar_chart(nps_counts)
    else:
        st.info("NPS grouping unavailable.")

# -----------------------------
# WORD CLOUD
# -----------------------------
st.subheader("Feedback Word Cloud")
if feedback_col and feedback_col in filtered_df.columns:
    text = " ".join(filtered_df[feedback_col].dropna().astype(str).tolist()).strip()
    if text:
        wc = WordCloud(width=900, height=400, background_color="white").generate(text)
        fig5, ax5 = plt.subplots(figsize=(12, 5))
        ax5.imshow(wc, interpolation="bilinear")
        ax5.axis("off")
        st.pyplot(fig5)
        fig_to_download(fig5, "feedback_wordcloud.png", "Download Word Cloud")
    else:
        st.info("No text available for word cloud after filtering.")
else:
    st.info("No feedback or suggestion column detected.")

# -----------------------------
# INSIGHTS
# -----------------------------
st.subheader("Auto-Generated Insights")
insights = generate_insights(filtered_df, rating_cols, recommend_col, usage_col)

if insights:
    for insight in insights:
        st.markdown(f"- {insight}")
else:
    st.info("Not enough data to generate insights.")

# -----------------------------
# RAW DATA
# -----------------------------
st.subheader("Filtered Data Preview")
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# COLUMN DEBUG
# -----------------------------
with st.expander("Show detected columns"):
    st.write("Age column:", age_col)
    st.write("Usage column:", usage_col)
    st.write("Recommendation column:", recommend_col)
    st.write("Payment column:", payment_col)
    st.write("Claim column:", claim_col)
    st.write("Rating columns:", rating_cols)
    st.write("Feedback column:", feedback_col)