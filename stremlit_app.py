import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="APL Logistics Dashboard",
    page_icon="📦",
    layout="wide"
)

st.title("APL Logistics Dashboard")
st.caption("Sales, Customer Profitability & Shipping Analysis")

@st.cache_data
def load_data():
    return pd.read_csv("APL_Logistics_small2.csv")

df = load_data()
df.columns = df.columns.str.strip()

st.sidebar.header("Dashboard Filters")

if "Customer Segment" in df.columns:
    segments = df["Customer Segment"].dropna().unique().tolist()
    selected = st.sidebar.multiselect(
        "Customer Segment", segments, default=segments
    )
    df = df[df["Customer Segment"].isin(selected)]

if "Shipping Mode" in df.columns:
    modes = df["Shipping Mode"].dropna().unique().tolist()
    selected_modes = st.sidebar.multiselect(
        "Shipping Mode", modes, default=modes
    )
    df = df[df["Shipping Mode"].isin(selected_modes)]

def find_col(name):
    return next((c for c in df.columns if c.lower() == name.lower()), None)

sales_col = find_col("Sales")
customer_col = find_col("Customer ID")
product_col = find_col("Product Name")
category_col = find_col("Category Name")
quantity_col = find_col("Order Item Quantity")
profit_col = find_col("Benefit per order")

c1, c2, c3, c4 = st.columns(4)

sales = pd.to_numeric(df[sales_col], errors="coerce").sum() if sales_col else 0
customers = df[customer_col].nunique() if customer_col else 0
quantity = pd.to_numeric(df[quantity_col], errors="coerce").sum() if quantity_col else 0
profit = pd.to_numeric(df[profit_col], errors="coerce").sum() if profit_col else 0

c1.metric("Total Sales", f"{sales:,.2f}")
c2.metric("Total Customers", f"{customers:,}")
c3.metric("Total Quantity", f"{quantity:,.0f}")
c4.metric("Benefit per Order", f"{profit:,.2f}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Sales by Product")
    if sales_col and product_col:
        chart = df.copy()
        chart[sales_col] = pd.to_numeric(chart[sales_col], errors="coerce")
        chart = chart.groupby(product_col)[sales_col].sum().nlargest(10)
        st.bar_chart(chart)

with right:
    st.subheader("Sales by Category")
    if sales_col and category_col:
        chart = df.copy()
        chart[sales_col] = pd.to_numeric(chart[sales_col], errors="coerce")
        chart = chart.groupby(category_col)[sales_col].sum()
        st.bar_chart(chart)

st.subheader("Shipping Mode Analysis")
if "Shipping Mode" in df.columns:
    st.bar_chart(df["Shipping Mode"].value_counts())

st.subheader("Customer Data")
st.dataframe(df, use_container_width=True)

st.caption("APL Logistics | Interactive Business Dashboard")

