
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# ── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Adidas US Sales Dashboard",
    page_icon="👟",
    layout="wide"
)

st.title("👟 Adidas US Sales Dashboard")
st.markdown("**Interactive business dashboard | 2020–2021 US Sales Data**")
st.markdown("---")

# ── LOAD DATA ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df_raw = pd.read_excel("C:/Users/cayde/Adidas US Sales Datasets.xlsx", header=None)
    header_row = df_raw[df_raw.apply(
        lambda r: r.astype(str).str.contains("Retailer").any(), axis=1
    )].index[0]
    df = pd.read_excel("C:/Users/cayde/Adidas US Sales Datasets.xlsx", header=header_row)
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

# ── SIDEBAR ────────────────────────────────────────────────────────────────
st.sidebar.header("🔍 Filter Data")
st.sidebar.markdown("Select filters to update all charts simultaneously.")

region_options = ["All"] + sorted(df["Region"].unique().tolist())
selected_region = st.sidebar.selectbox("Select Region:", region_options)

year_options = ["Both", "2020", "2021"]
selected_year = st.sidebar.radio("Select Year:", year_options)

if selected_region == "All":
    filtered = df.copy()
else:
    filtered = df[df["Region"] == selected_region].copy()

if selected_year != "Both":
    filtered = filtered[filtered["Year"] == int(selected_year)].copy()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dashboard Summary")
st.sidebar.metric("Total Sales", f"${filtered['Total Sales'].sum():,.0f}")
st.sidebar.metric("Operating Profit", f"${filtered['Operating Profit'].sum():,.0f}")
st.sidebar.metric("Units Sold", f"{filtered['Units Sold'].sum():,.0f}")

# ── ROW 1: VIZ 1 + VIZ 2 ──────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Monthly Sales Trend")

    monthly = filtered.groupby("Month")["Total Sales"].sum().reset_index()
    monthly = monthly.sort_values("Month")
    monthly["Rolling Avg"] = monthly["Total Sales"].rolling(3, min_periods=1).mean()

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Total Sales"],
        mode="lines+markers", name="Monthly Sales",
        line=dict(color="#3B82F6", width=2), marker=dict(size=5)
    ))
    fig1.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Rolling Avg"],
        mode="lines", name="3-Month Avg",
        line=dict(color="#F59E0B", width=2, dash="dash")
    ))
    fig1.update_layout(
        xaxis_title="Month", yaxis_title="Total Sales ($)",
        legend=dict(orientation="h", y=1.1),
        plot_bgcolor="white", height=350,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🏪 Total Sales by Retailer")

    retailer = filtered.groupby("Retailer").agg(
        Total_Sales=("Total Sales","sum"),
        Op_Profit=("Operating Profit","sum")
    ).reset_index().sort_values("Total_Sales", ascending=False)

    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2.add_trace(go.Bar(
        x=retailer["Retailer"], y=retailer["Total_Sales"],
        name="Total Sales", marker_color="#6366F1"
    ), secondary_y=False)
    fig2.add_trace(go.Scatter(
        x=retailer["Retailer"], y=retailer["Op_Profit"],
        mode="lines+markers", name="Operating Profit",
        line=dict(color="#10B981", width=2), marker=dict(size=7)
    ), secondary_y=True)
    avg_sales = retailer["Total_Sales"].mean()
    fig2.add_hline(
        y=avg_sales, line_dash="dot", line_color="red",
        annotation_text=f"Avg: ${avg_sales:,.0f}",
        annotation_position="top right"
    )
    fig2.update_layout(
        plot_bgcolor="white", height=350,
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=20, r=20, t=30, b=20)
    )
    fig2.update_yaxes(title_text="Total Sales ($)", secondary_y=False)
    fig2.update_yaxes(title_text="Operating Profit ($)", secondary_y=True)
    st.plotly_chart(fig2, use_container_width=True)

# ── ROW 2: VIZ 3 + VIZ 4 ──────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("🛍️ Sales by Channel Method")

    method = filtered.groupby("Sales Method")["Total Sales"].sum().reset_index()
    max_idx = method["Total Sales"].idxmax()
    pull_vals = [0.08 if i == max_idx else 0 for i in range(len(method))]

    fig3 = go.Figure(go.Pie(
        labels=method["Sales Method"],
        values=method["Total Sales"],
        hole=0.4,
        pull=pull_vals,
        textinfo="label+percent",
        marker=dict(colors=["#6366F1","#10B981","#F59E0B"])
    ))
    fig3.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("🔵 Units Sold vs. Operating Profit")

    filtered2 = filtered.copy()
    filtered2["Bubble Size"] = (
        (filtered2["Total Sales"] - filtered2["Total Sales"].min()) /
        (filtered2["Total Sales"].max() - filtered2["Total Sales"].min()) * 18 + 4
    )

    fig4 = px.scatter(
        filtered2,
        x="Units Sold", y="Operating Profit",
        color="Product",
        size="Bubble Size", size_max=20,
        hover_data=["Retailer","Region"],
        color_discrete_sequence=px.colors.qualitative.Bold,
        height=350
    )
    for product in filtered2["Product"].unique():
        sub = filtered2[filtered2["Product"] == product]
        if len(sub) > 1:
            z = np.polyfit(sub["Units Sold"], sub["Operating Profit"], 1)
            p = np.poly1d(z)
            xr = np.linspace(sub["Units Sold"].min(), sub["Units Sold"].max(), 50)
            fig4.add_trace(go.Scatter(
                x=xr, y=p(xr), mode="lines",
                line=dict(width=1.5, dash="dash"),
                showlegend=False
            ))
    fig4.update_layout(
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.caption("Adidas US Sales Dashboard | MSBA Group Project | Pepperdine University")
