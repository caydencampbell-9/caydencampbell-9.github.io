"""
Student Dashboard — Adidas US Sales
MSBA Group Project | Pepperdine University
Written manually by student team as baseline visualizations.
Includes two student-created interactive features:
  1. Year filter toggle (2020 / 2021 / Both)
  2. Product category selector
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Adidas Sales — Student Dashboard",
    page_icon="👟",
    layout="wide"
)

st.title("👟 Adidas US Sales — Student Dashboard")
st.markdown("**Baseline visualizations created by student team**")
st.markdown("---")


@st.cache_data
def load_data():
    """
    Loads and preprocesses the Adidas US Sales dataset from a local Excel file.
    Identifies the correct header row, converts date and numeric columns,
    and extracts year and month fields for time-based filtering.
    Returns a cleaned pandas DataFrame ready for visualization.
    """
    df_raw = pd.read_excel(
        "C:/Users/cayde/Adidas US Sales Datasets.xlsx",
        header=None
    )
    header_row = df_raw[df_raw.apply(
        lambda r: r.astype(str).str.contains("Retailer").any(), axis=1
    )].index[0]
    df = pd.read_excel(
        "C:/Users/cayde/Adidas US Sales Datasets.xlsx",
        header=header_row
    )
    df = df.dropna(subset=["Retailer"])
    df.columns = df.columns.str.strip()
    df["Invoice Date"] = pd.to_datetime(df["Invoice Date"])
    df["Total Sales"] = pd.to_numeric(df["Total Sales"], errors="coerce")
    df["Operating Profit"] = pd.to_numeric(df["Operating Profit"], errors="coerce")
    df["Units Sold"] = pd.to_numeric(df["Units Sold"], errors="coerce")
    df["Month"] = df["Invoice Date"].dt.to_period("M").astype(str)
    df["Year"] = df["Invoice Date"].dt.year
    return df


df = load_data()

# ── STUDENT INTERACTIVE FEATURE 1: Year Toggle ────────────────────────────
st.sidebar.header("🎛️ Filters")
st.sidebar.markdown("Team CJS")

year_option = st.sidebar.radio(
    "Select Year:",
    options=["Both", "2020", "2021"]
)

if year_option == "Both":
    filtered = df.copy()
elif year_option == "2020":
    filtered = df[df["Year"] == 2020].copy()
else:
    filtered = df[df["Year"] == 2021].copy()

# ── STUDENT INTERACTIVE FEATURE 2: Product Selector ──────────────────────
all_products = sorted(df["Product"].unique().tolist())
selected_products = st.sidebar.multiselect(
    "Select Products:",
    options=all_products,
    default=all_products
)

if selected_products:
    filtered = filtered[filtered["Product"].isin(selected_products)]

st.sidebar.markdown("---")
st.sidebar.markdown("### Summary")
st.sidebar.metric("Total Sales", f"${filtered['Total Sales'].sum():,.0f}")
st.sidebar.metric("Units Sold", f"{filtered['Units Sold'].sum():,.0f}")

# ── VIZ 1: Basic Line Chart ───────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Monthly Sales Trend")
    monthly = filtered.groupby("Month")["Total Sales"].sum().reset_index()
    monthly = monthly.sort_values("Month")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Total Sales"],
        mode="lines+markers", name="Monthly Sales",
        line=dict(color="blue", width=2)
    ))
    fig1.update_layout(
        xaxis_title="Month", yaxis_title="Total Sales ($)",
        plot_bgcolor="white", height=350,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig1, use_container_width=True)

# ── VIZ 2: Basic Bar Chart ────────────────────────────────────────────────
with col2:
    st.subheader("🏪 Total Sales by Retailer")
    retailer = filtered.groupby("Retailer")["Total Sales"].sum().reset_index()
    retailer = retailer.sort_values("Total Sales", ascending=False)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=retailer["Retailer"], y=retailer["Total Sales"],
        name="Total Sales", marker_color="purple"
    ))
    fig2.update_layout(
        xaxis_title="Retailer", yaxis_title="Total Sales ($)",
        plot_bgcolor="white", height=350,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

# ── VIZ 3: Basic Donut ────────────────────────────────────────────────────
with col3:
    st.subheader("🛍️ Sales by Channel Method")
    method = filtered.groupby("Sales Method")["Total Sales"].sum().reset_index()
    fig3 = go.Figure(go.Pie(
        labels=method["Sales Method"],
        values=method["Total Sales"],
        hole=0.4
    ))
    fig3.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig3, use_container_width=True)

# ── VIZ 4: Basic Scatter ──────────────────────────────────────────────────
with col4:
    st.subheader("🔵 Units Sold vs. Operating Profit")
    fig4 = px.scatter(
        filtered,
        x="Units Sold", y="Operating Profit",
        color="Product",
        color_discrete_sequence=px.colors.qualitative.Bold,
        height=350
    )
    fig4.update_layout(
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.caption("Student-authored dashboard | MSBA Group Project | Pepperdine University")