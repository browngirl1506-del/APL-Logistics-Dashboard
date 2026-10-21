import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="APL Logistics", layout="wide")

st.title("📦 APL Logistics Dashboard")

file = st.sidebar.file_uploader(
    "Upload Dataset", type=["csv", "xlsx"]
)

if file is None:
    st.info("Please upload your Excel or CSV dataset.")
    st.stop()

try:
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
except Exception as e:
    st.error(f"File error: {e}")
    st.stop()

df.columns = df.columns.str.strip()

sales_col = next(
    (c for c in df.columns if c.lower() == "sales"), None
)
profit_col = next(
    (c for c in df.columns
     if c.lower() == "order profit per order"), None
)
order_col = next(
    (c for c in df.columns if c.lower() == "order id"), None
)
region_col = next(
    (c for c in df.columns if c.lower() == "order region"), None
)

if sales_col:
    df[sales_col] = pd.to_numeric(df[sales_col], errors="coerce")

if profit_col:
    df[profit_col] = pd.to_numeric(df[profit_col], errors="coerce")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Total Sales",
    f"{df[sales_col].sum():,.2f}" if sales_col else "N/A"
)
c2.metric(
    "Total Profit",
    f"{df[profit_col].sum():,.2f}" if profit_col else "N/A"
)
c3.metric(
    "Total Orders",
    f"{df[order_col].nunique():,}" if order_col else f"{len(df):,}"
)

if sales_col and region_col:
    chart_data = df.groupby(region_col)[sales_col].sum().reset_index()
    fig = px.bar(
        chart_data,
        x=region_col,
        y=sales_col,
        title="Sales by Region"
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Dataset Preview")
st.dataframe(df.head(100), use_container_width=True)

