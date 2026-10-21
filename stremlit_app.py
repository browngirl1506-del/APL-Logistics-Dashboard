import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="APL Logistics Dashboard",
    page_icon="📦",
    layout="wide"
)

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: #f1f5f9;
}
[data-testid="stMetric"] {
    background-color: #172338;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #293950;
}
[data-testid="stMetricLabel"] {
    color: #a9bbd0;
}
h1, h2, h3 {
    color: #55d6be;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("📦 APL LOGISTICS ANALYTICS")
st.caption("Sales • Profit • Customers • Products • Shipping")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    file_path = "APL_Logistics_small2.csv"
    data = pd.read_csv(file_path, low_memory=False)
    data.columns = data.columns.astype(str).str.strip()
    return data

try:
    df = load_data()
except Exception as e:
    st.error("CSV फ़ाइल लोड नहीं हो पाई।")
    st.write("जाँचो कि APL_Logistics_small2.csv और streamlit_app.py एक ही GitHub repository में हैं।")
    st.code(str(e))
    st.stop()

if df.empty:
    st.error("CSV फ़ाइल में कोई डेटा नहीं है।")
    st.stop()

# ---------------- HELPERS ----------------
def find_column(possible_names):
    """CSV में उपलब्ध कॉलम के अनुसार सही कॉलम ढूँढें।"""
    normalized = {
        str(col).lower().replace("_", " ").strip(): col
        for col in df.columns
    }

    for name in possible_names:
        key = name.lower().replace("_", " ").strip()
        if key in normalized:
            return normalized[key]

    return None


sales_col = find_column(["Sales", "Order Item Total"])
profit_col = find_column([
    "Order Profit Per Order",
    "Profit",
    "Gross Profit"
])
customer_col = find_column(["Customer Id", "Customer ID"])
product_col = find_column(["Product Name"])
category_col = find_column([
    "Category Name",
    "Customer Category Name"
])
region_col = find_column(["Order Region", "Region"])
shipping_col = find_column(["Shipping Mode"])
segment_col = find_column(["Customer Segment"])
quantity_col = find_column([
    "Order Item Quantity",
    "Quantity"
])
order_col = find_column(["Order Id", "Order ID"])
status_col = find_column(["Order Status"])
date_col = find_column(["Order Date"])

# Convert numeric columns safely
for col in [sales_col, profit_col, quantity_col]:
    if col:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("🔎 Dashboard Filters")

filtered_df = df.copy()

filter_columns = [
    ("Region", region_col),
    ("Category", category_col),
    ("Shipping Mode", shipping_col),
    ("Customer Segment", segment_col),
    ("Order Status", status_col),
]

for label, col in filter_columns:
    if col and col in filtered_df.columns:
        options = sorted(
            filtered_df[col].dropna().astype(str).unique().tolist()
        )
        selected = st.sidebar.multiselect(
            label,
            options,
            default=options
        )

        filtered_df = filtered_df[
            filtered_df[col].astype(str).isin(selected)
        ]

st.sidebar.markdown("---")
st.sidebar.write(f"Filtered rows: {len(filtered_df):,}")

# ---------------- KPI CALCULATIONS ----------------
def total_value(data, col):
    if col and col in data.columns:
        return data[col].sum()
    return None

sales_total = total_value(filtered_df, sales_col)
profit_total = total_value(filtered_df, profit_col)
quantity_total = total_value(filtered_df, quantity_col)

customer_total = (
    filtered_df[customer_col].nunique()
    if customer_col else None
)

order_total = (
    filtered_df[order_col].nunique()
    if order_col else None
)

# ---------------- KPI CARDS ----------------
st.subheader("📊 Business Overview")

kpis = st.columns(5)

kpis[0].metric(
    "Total Sales",
    f"${sales_total:,.2f}" if sales_total is not None else "N/A"
)

kpis[1].metric(
    "Total Profit",
    f"${profit_total:,.2f}" if profit_total is not None else "N/A"
)

kpis[2].metric(
    "Total Customers",
    f"{customer_total:,}" if customer_total is not None else "N/A"
)

kpis[3].metric(
    "Total Orders",
    f"{order_total:,}" if order_total is not None else "N/A"
)

kpis[4].metric(
    "Total Quantity",
    f"{quantity_total:,.0f}"
    if quantity_total is not None else "N/A"
)

st.markdown("---")

# ---------------- SALES BY CATEGORY ----------------
left, right = st
