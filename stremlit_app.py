import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="APL Logistics Dashboard",
    page_icon="📦",
    layout="wide"
)

# ---------- Load CSV ----------
st.title("📦 APL Logistics Dashboard")
st.caption("Sales | Customer | Product | Shipping Analysis")

@st.cache_data
def load_data():
    return pd.read_csv("APL_Logistics_small2.csv")

try:
    df = load_data()
except Exception as e:
    st.error("CSV file load nahi hui. GitHub par CSV ka exact filename check karein.")
    st.stop()

df.columns = df.columns.str.strip()

# ---------- Find columns flexibly ----------
def find_col(*names):
    normalized = {
        str(c).strip().lower().replace("_", " "): c
        for c in df.columns
    }
    for name in names:
        key = name.strip().lower().replace("_", " ")
        if key in normalized:
            return normalized[key]
    return None

customer_id = find_col("Customer Id", "Customer ID", "CustomerId")
customer_name = find_col("Customer Name", "CustomerName")
city = find_col("Customer City", "City")
country = find_col("Customer Country", "Country")
category = find_col("Category Name", "Category")
product = find_col("Product Name", "ProductName")
sales_col = find_col("Sales", "Order Item Total")
quantity = find_col("Order Item Quantity", "Order Item Quantity ")
shipping = find_col("Shipping Mode", "ShippingMode")
profit = find_col("Order Profit Per Order", "Order Profit per Order")
profit_ratio = find_col("Order Item Profit Ratio", "Benefit per order")
state = find_col("Order State", "Customer State", "State")
region = find_col("Order Region", "Region")

# Convert numerical fields safely
for col in [sales_col, quantity, profit, profit_ratio]:
    if col:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------- Sidebar filters ----------
st.sidebar.header("Dashboard Filters")

filtered = df.copy()

if category:
    options = sorted(filtered[category].dropna().astype(str).unique())
    chosen = st.sidebar.multiselect(
        "Category", options, default=options
    )
    filtered = filtered[
        filtered[category].astype(str).isin(chosen)
    ]

if shipping:
    options = sorted(filtered[shipping].dropna().astype(str).unique())
    chosen = st.sidebar.multiselect(
        "Shipping Mode", options, default=options
    )
    filtered = filtered[
        filtered[shipping].astype(str).isin(chosen)
    ]

if region:
    options = sorted(filtered[region].dropna().astype(str).unique())
    chosen = st.sidebar.multiselect(
        "Region", options, default=options
    )
    filtered = filtered[
        filtered[region].astype(str).isin(chosen)
    ]

# ---------- KPI cards ----------
total_sales = filtered[sales_col].sum() if sales_col else 0
total_profit = filtered[profit].sum() if profit else 0
total_quantity = filtered[quantity].sum() if quantity else 0
total_customers = (
    filtered[customer_id].nunique()
    if customer_id else
    filtered[customer_name].nunique()
    if customer_name else 0
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"{total_sales:,.2f}")
c2.metric("Total Profit", f"{total_profit:,.2f}")
c3.metric("Total Customers", f"{total_customers:,}")
c4.metric("Total Quantity", f"{total_quantity:,.0f}")

st.divider()

# ---------- Sales analysis ----------
left, right = st.columns(2)

with left:
    st.subheader("📊 Sales by Product")
    if sales_col and product:
        chart_data = (
            filtered.groupby(product)[sales_col]
            .sum().nlargest(10).sort_values()
        )
        st.bar_chart(chart_data)
    else:
        st.info("Product Name ya Sales column nahi mila.")

with right:
    st.subheader("📂 Sales by Category")
    if sales_col and category:
        chart_data = (
            filtered.groupby(category)[sales_col]
            .sum().sort_values(ascending=False)
        )
        st.bar_chart(chart_data)
    else:
        st.info("Category Name ya Sales column nahi mila.")

# ---------- Customer analysis ----------
st.divider()
st.subheader("👥 Customer Analysis")

left, right = st.columns(2)

with left:
    st.write("**Sales by Customer City**")
    if sales_col and city:
        st.bar_chart(
            filtered.groupby(city)[sales_col]
            .sum().nlargest(10).sort_values()
        )
    else:
        st.info("Customer City ya Sales column nahi mila.")

with right:
    st.write("**Sales by Country**")
    if sales_col and country:
        st.bar_chart(
            filtered.groupby(country)[sales_col]
            .sum().nlargest(10).sort_values()
        )
    else:
        st.info("Country ya Sales column nahi mila.")

# ---------- Shipping analysis ----------
st.divider()
st.subheader("🚚 Shipping Analysis")

left, right = st.columns(2)

with left:
    if shipping:
        st.write("**Orders by Shipping Mode**")
        st.bar_chart(filtered[shipping].value_counts())
    else:
        st.info("Shipping Mode column nahi mila.")

with right:
    if profit and shipping:
        st.write("**Profit by Shipping Mode**")
        st.bar_chart(filtered.groupby(shipping)[profit].sum())
    elif profit:
        st.write("**Profit Distribution**")
        st.bar_chart(filtered[profit].dropna().reset_index(drop=True))
    else:
        st.info("Order Profit Per Order column nahi mila.")

# ---------- Region analysis ----------
st.divider()
st.subheader("🌍 Regional Analysis")

left, right = st.columns(2)

with left:
    if sales_col and state:
        st.write("**Sales by State — Top 10**")
        st.bar_chart(
            filtered.groupby(state)[sales_col]
            .sum().nlargest(10).sort_values()
        )
    else:
        st.info("State ya Sales column nahi mila.")

with right:
    if sales_col and region:
        st.write("**Sales by Region**")
        st.bar_chart(filtered.groupby(region)[sales_col].sum())
    else:
        st.info("Region ya Sales column nahi mila.")

# ---------- Raw data ----------
st.divider()
st.subheader("📋 Complete Dataset")
st.write(f"Showing {len(filtered):,} rows and {len(filtered.columns)} columns.")
st.dataframe(filtered, use_container_width=True, height=450)

st.download_button(
    "⬇️ Download Filtered Data",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="APL_Logistics_Filtered.csv",
    mime="text/csv"
)

with st.expander("Check CSV Column Names"):
    st.write(df.columns.tolist())

st.caption("APL Logistics | Interactive Business Dashboard")
