import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import os
from dotenv import load_dotenv
import markdown

load_dotenv()




# --- Page Config ---
st.set_page_config(
    page_title="Curewell Business Dashboard",
    page_icon="💊",
    layout="wide"
)

# --- Scroll to top on page change ---
# st.components.v1.html renders inside an iframe, so we use window.parent
# to reach the actual Streamlit page and scroll its containers.
def scroll_to_top():
    st.components.v1.html(
        """
        <script>
            (function() {
                const doScroll = () => {
                    try {
                        const win = window.parent;
                        const doc = win.document;
                        win.scrollTo(0, 0);
                        doc.documentElement.scrollTop = 0;
                        doc.body.scrollTop = 0;
                        const selectors = [
                            '[data-testid="stAppViewBlockContainer"]',
                            '[data-testid="stMain"]',
                            '[data-testid="stAppViewContainer"]',
                            '.main',
                            '.block-container',
                        ];
                        selectors.forEach(s => {
                            const node = doc.querySelector(s);
                            if (node) { node.scrollTop = 0; }
                        });
                    } catch(e) {}
                };
                doScroll();
                setTimeout(doScroll, 80);
                setTimeout(doScroll, 300);
            })();
        </script>
        """,
        height=0,
    )

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=swap');

    /* Section separator */
    hr.section-sep {
        border: none;
        border-top: 2px solid #e2e8f0;
        margin: 32px 0 26px 0;
    }
    /* Sidebar section headers */
    .sidebar-section-header {
        font-size: 0.78rem;
        font-weight: 700;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 8px;
        margin-bottom: 2px;
    }
</style>
""", unsafe_allow_html=True)


# --- Color map for KPI banners ---
_KPI_COLORS = {
    "kpi-blue":   ("linear-gradient(135deg,#2563eb,#1d4ed8)", "#1e3a8a"),
    "kpi-teal":   ("linear-gradient(135deg,#0891b2,#0e7490)", "#164e63"),
    "kpi-green":  ("linear-gradient(135deg,#059669,#047857)", "#064e3b"),
    "kpi-purple": ("linear-gradient(135deg,#7c3aed,#6d28d9)", "#4c1d95"),
    "kpi-orange": ("linear-gradient(135deg,#ea580c,#c2410c)", "#7c2d12"),
    "kpi-pink":   ("linear-gradient(135deg,#db2777,#be185d)", "#831843"),
    "kpi-slate":  ("linear-gradient(135deg,#475569,#334155)", "#1e293b"),
    "kpi-red":    ("linear-gradient(135deg,#dc2626,#b91c1c)", "#7f1d1d"),
}

# --- Helper: KPI Banner Card (inline styles — Streamlit-safe) ---
def kpi_banner(icon: str, label: str, value: str, color: str = "kpi-blue", delta: str = ""):
    grad, _ = _KPI_COLORS.get(color, _KPI_COLORS["kpi-blue"])
    delta_span = (
        f'<span style="display:inline-block;margin-top:6px;padding:2px 10px;'
        f'border-radius:20px;background:rgba(255,255,255,0.22);'
        f'color:#fff;font-size:0.70rem;font-weight:600;">{delta}</span>'
        if delta else ""
    )
    html = (
        f'<div style="background:{grad};border-radius:14px;padding:20px 22px 18px 22px;'
        f'min-height:115px;position:relative;overflow:hidden;margin-bottom:4px;">'
        f'<div style="font-size:1.5rem;margin-bottom:6px;">{icon}</div>'
        f'<div style="font-size:0.70rem;font-weight:700;letter-spacing:0.10em;'
        f'text-transform:uppercase;color:rgba(255,255,255,0.85);margin-bottom:3px;">{label}</div>'
        f'<div style="font-size:1.55rem;font-weight:700;color:#ffffff;line-height:1.2;'
        f'letter-spacing:-0.01em;">{value}</div>'
        f'{delta_span}'
        f'<div style="position:absolute;top:-18px;right:-18px;width:80px;height:80px;'
        f'border-radius:50%;background:rgba(255,255,255,0.10);"></div>'
        f'<div style="position:absolute;bottom:-28px;right:12px;width:110px;height:110px;'
        f'border-radius:50%;background:rgba(255,255,255,0.07);"></div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

# --- Helper: Section Heading Banner ---
_BANNER_THEMES = {
    "blue":   {"bg": "linear-gradient(90deg,#1e3a8a 0%,#2563eb 60%,#3b82f6 100%)", "accent": "#60a5fa"},
    "teal":   {"bg": "linear-gradient(90deg,#134e4a 0%,#0891b2 60%,#22d3ee 100%)", "accent": "#67e8f9"},
    "green":  {"bg": "linear-gradient(90deg,#064e3b 0%,#059669 60%,#34d399 100%)", "accent": "#6ee7b7"},
    "purple": {"bg": "linear-gradient(90deg,#3b0764 0%,#7c3aed 60%,#a78bfa 100%)", "accent": "#c4b5fd"},
    "orange": {"bg": "linear-gradient(90deg,#7c2d12 0%,#ea580c 60%,#fb923c 100%)", "accent": "#fdba74"},
    "red":    {"bg": "linear-gradient(90deg,#7f1d1d 0%,#dc2626 60%,#f87171 100%)", "accent": "#fca5a5"},
    "slate":  {"bg": "linear-gradient(90deg,#0f172a 0%,#334155 60%,#64748b 100%)", "accent": "#94a3b8"},
    "pink":   {"bg": "linear-gradient(90deg,#500724 0%,#be185d 60%,#f472b6 100%)", "accent": "#f9a8d4"},
}

def section_banner(icon: str, title: str, subtitle: str = "", theme: str = "blue"):
    t = _BANNER_THEMES.get(theme, _BANNER_THEMES["blue"])
    sub_html = (
        f'<div style="font-size:0.80rem;color:{t["accent"]};margin-top:4px;'
        f'font-weight:500;letter-spacing:0.02em;">{subtitle}</div>'
        if subtitle else ""
    )
    st.markdown(
        f'<div style="background:{t["bg"]};border-radius:12px;padding:16px 24px;'
        f'margin-bottom:18px;position:relative;overflow:hidden;">'
        f'<div style="position:absolute;right:-20px;top:-20px;width:100px;height:100px;'
        f'border-radius:50%;background:rgba(255,255,255,0.06);"></div>'
        f'<div style="position:absolute;right:40px;bottom:-30px;width:140px;height:140px;'
        f'border-radius:50%;background:rgba(255,255,255,0.04);"></div>'
        f'<div style="display:flex;align-items:center;gap:12px;">'
        f'<span style="font-size:1.6rem;">{icon}</span>'
        f'<div>'
        f'<div style="font-size:1.15rem;font-weight:700;color:#ffffff;'
        f'letter-spacing:-0.01em;line-height:1.2;">{title}</div>'
        f'{sub_html}'
        f'</div></div></div>',
        unsafe_allow_html=True
    )

def section_sep():
    st.markdown('<hr class="section-sep">', unsafe_allow_html=True)

# --- Helper: render a compact detail table below a chart ---
def detail_table(df_table: pd.DataFrame, title: str = "📋 Data Behind the Chart"):
    with st.expander(title, expanded=True):
        st.dataframe(
            df_table.reset_index(drop=True),
            use_container_width=True,
            height=min(40 + 38 * len(df_table), 380),
        )

# --- Helper: Call Groq API ---
def call_groq(api_key: str, messages: list, model: str = "llama-3.3-70b-versatile") -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        return f"❌ API Error: {resp.status_code} — {resp.text}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# --- Helper: Build data summary string for AI context ---
def build_data_summary(df: pd.DataFrame) -> str:
    total_rev = df["Revenue_INR"].sum()
    total_profit = df["Estimated_Profit_INR"].sum()
    total_units = df["Units_Sold"].sum()
    total_customers = df["Customer_ID"].nunique()
    profit_margin = (total_profit / total_rev * 100) if total_rev > 0 else 0
    profitable_orders = (df["Profit_Status"] == "Profitable").sum()
    loss_orders = (df["Profit_Status"] == "Loss").sum()

    top_product = df.groupby("Product")["Revenue_INR"].sum().idxmax()
    top_region = df.groupby("Region")["Revenue_INR"].sum().idxmax()
    top_brand = df.groupby("Brand")["Revenue_INR"].sum().idxmax()
    top_vendor = df.groupby("Vendor")["Revenue_INR"].sum().idxmax()
    top_lead = df.groupby("Lead_Source")["Revenue_INR"].sum().idxmax()

    brand_summary = df.groupby("Brand").agg(
        Revenue=("Revenue_INR","sum"),
        Units=("Units_Sold","sum"),
        Profit=("Estimated_Profit_INR","sum")
    ).reset_index().to_string(index=False)

    region_summary = df.groupby("Region").agg(
        Revenue=("Revenue_INR","sum"),
        Profit=("Estimated_Profit_INR","sum")
    ).reset_index().to_string(index=False)

    product_summary = df.groupby("Product").agg(
        Revenue=("Revenue_INR","sum"),
        Units=("Units_Sold","sum"),
        Profit=("Estimated_Profit_INR","sum")
    ).reset_index().sort_values("Revenue", ascending=False).head(10).to_string(index=False)

    return f"""
CUREWELL PHARMA — FILTERED DATASET SUMMARY
===========================================
Records: {len(df):,}
Total Revenue: ₹{total_rev:,.0f}
Total Profit: ₹{total_profit:,.0f}
Profit Margin: {profit_margin:.1f}%
Total Units Sold: {total_units:,}
Unique Customers: {total_customers:,}
Profitable Orders: {profitable_orders:,}
Loss Orders: {loss_orders:,}

Top Performing Product: {top_product}
Top Region: {top_region}
Top Brand: {top_brand}
Top Vendor: {top_vendor}
Best Lead Source: {top_lead}

BRAND BREAKDOWN:
{brand_summary}

REGION BREAKDOWN:
{region_summary}

TOP 10 PRODUCTS BY REVENUE:
{product_summary}
"""

@st.cache_data
def load_data():
    df = pd.read_csv("data/curewell_business_full_dataset.csv")
    df["Profit_Status"] = df["Estimated_Profit_INR"].apply(
        lambda x: "Profitable" if x > 0 else "Loss"
    )
    return df

df = load_data()

# --- Sidebar ---
st.sidebar.title("💊 Curewell")
st.sidebar.markdown("---")

# --- Navigation ---
st.sidebar.markdown("### 🗂️ Navigation")

# Track previous page to detect navigation changes
if "current_page" not in st.session_state:
    st.session_state.current_page = "📊 Overview"

page = st.sidebar.radio("Go to", [
    "📊 Overview",
    "🏷️ Brand & Product",
    "🌍 Region Analysis",
    "📞 Sales & Leads",
    "💰 Profit Analysis",
    "📁 Raw Data",
    "🤖 AI Insights"
])

# Detect page change and trigger scroll to top
if page != st.session_state.current_page:
    st.session_state.current_page = page
    st.session_state["_scroll_to_top"] = True

st.sidebar.markdown("---")

# --- Filters ---
st.sidebar.markdown("### 🔽 Filters")

all_brands = sorted(df["Brand"].unique().tolist())
selected_brands = st.sidebar.multiselect("Brand", all_brands, default=all_brands)

all_regions = sorted(df["Region"].unique().tolist())
selected_regions = st.sidebar.multiselect("Region", all_regions, default=all_regions)

# --- Split Product Filter by Brand ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 📦 Products by Brand")

brand_product_selections = []
for brand in all_brands:
    brand_products = sorted(df[df["Brand"] == brand]["Product"].unique().tolist())
    st.sidebar.markdown(
        f'<p class="sidebar-section-header">🏷️ {brand}</p>',
        unsafe_allow_html=True
    )
    sel = st.sidebar.multiselect(
        f"Products — {brand}",
        brand_products,
        default=brand_products,
        key=f"products_{brand}",
        label_visibility="collapsed"
    )
    brand_product_selections.extend(sel)

selected_products = brand_product_selections

st.sidebar.markdown("---")

all_vendors = sorted(df["Vendor"].unique().tolist())
selected_vendors = st.sidebar.multiselect("Vendor", all_vendors, default=all_vendors)

all_lead_sources = sorted(df["Lead_Source"].unique().tolist())
selected_leads = st.sidebar.multiselect("Lead Source", all_lead_sources, default=all_lead_sources)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Groq AI")

# Load API key from .env first, allow sidebar override
env_groq_key = os.getenv("GROQ_API_KEY", "")

groq_api_key = st.sidebar.text_input(
    "Groq API Key",
    value=env_groq_key,
    type="password",
    placeholder="gsk_...",
    help="Get your free key at console.groq.com — or set GROQ_API_KEY in your .env file"
)
if groq_api_key:
    st.sidebar.success("✅ API Key set")
else:
    st.sidebar.caption("🔑 Enter key to enable AI Insights")

st.sidebar.markdown("---")

# --- Apply Filters ---
filtered_df = df[
    (df["Brand"].isin(selected_brands)) &
    (df["Region"].isin(selected_regions)) &
    (df["Product"].isin(selected_products)) &
    (df["Vendor"].isin(selected_vendors)) &
    (df["Lead_Source"].isin(selected_leads))
].copy()

# --- Scroll to top if page just changed ---
if st.session_state.get("_scroll_to_top"):
    scroll_to_top()
    st.session_state["_scroll_to_top"] = False

# ============================================================
# PAGE 1 — OVERVIEW
# ============================================================
if page == "📊 Overview":

    section_banner("📊", "Curewell Business Overview", f"Showing {len(filtered_df):,} records out of {len(df):,} total", "blue")

    # --- KPI Banner Cards Row 1 ---
    total_profit = filtered_df['Estimated_Profit_INR'].sum()
    profitable = (filtered_df["Profit_Status"] == "Profitable").sum()
    loss = (filtered_df["Profit_Status"] == "Loss").sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_banner("💰", "Total Revenue", f"₹{filtered_df['Revenue_INR'].sum():,.0f}", "kpi-blue")
    with col2:
        kpi_banner("📦", "Total Units Sold", f"{filtered_df['Units_Sold'].sum():,}", "kpi-teal")
    with col3:
        kpi_banner("📈", "Total Profit", f"₹{total_profit:,.0f}", "kpi-green",
                   delta="✅ Profitable" if total_profit > 0 else "⚠️ Loss")
    with col4:
        kpi_banner("👥", "Total Customers", f"{filtered_df['Customer_ID'].nunique():,}", "kpi-purple")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # --- KPI Banner Cards Row 2 ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_banner("🏷️", "Brands", f"{filtered_df['Brand'].nunique()}", "kpi-orange")
    with col2:
        kpi_banner("🛒", "Products", f"{filtered_df['Product'].nunique()}", "kpi-slate")
    with col3:
        kpi_banner("✅", "Profitable Orders", f"{profitable:,}", "kpi-green")
    with col4:
        kpi_banner("❌", "Loss Orders", f"{loss:,}", "kpi-red")

    section_sep()

    # --- Row 1: Revenue by Brand + Revenue by Region ---
    col1, col2 = st.columns(2)
    with col1:
        section_banner("💰", "Revenue by Brand", "Share of total revenue across brands", "blue")
        rev_brand = filtered_df.groupby("Brand")["Revenue_INR"].sum().reset_index()
        rev_brand.columns = ["Brand", "Total Revenue (₹)"]
        fig1 = px.pie(
            rev_brand, names="Brand", values="Total Revenue (₹)",
            title="Revenue Share by Brand",
            color_discrete_sequence=["#636EFA", "#EF553B"]
        )
        st.plotly_chart(fig1, use_container_width=True)
        detail_table(
            rev_brand.sort_values("Total Revenue (₹)", ascending=False)
            .assign(**{"Total Revenue (₹)": lambda x: x["Total Revenue (₹)"].map("₹{:,.0f}".format)}),
            "📋 Revenue by Brand"
        )

    with col2:
        section_banner("🌍", "Revenue by Region", "Total revenue breakdown across all regions", "teal")
        rev_region = filtered_df.groupby("Region")["Revenue_INR"].sum().reset_index().sort_values("Revenue_INR", ascending=False)
        rev_region.columns = ["Region", "Total Revenue (₹)"]
        fig2 = px.bar(
            rev_region, x="Region", y="Total Revenue (₹)", color="Region",
            title="Total Revenue (₹) by Region"
        )
        st.plotly_chart(fig2, use_container_width=True)
        detail_table(
            rev_region.assign(**{"Total Revenue (₹)": lambda x: x["Total Revenue (₹)"].map("₹{:,.0f}".format)}),
            "📋 Revenue by Region"
        )

    section_sep()

    # --- Row 2: Top Products + Profit vs Loss ---
    col1, col2 = st.columns(2)
    with col1:
        section_banner("🏆", "Top 10 Products by Revenue", "Highest revenue-generating products", "orange")
        top_products = (
            filtered_df.groupby("Product")["Revenue_INR"].sum()
            .reset_index()
            .sort_values("Revenue_INR", ascending=False)
            .head(10)
        )
        top_products.columns = ["Product", "Revenue (₹)"]
        fig3 = px.bar(
            top_products, x="Revenue (₹)", y="Product",
            orientation="h", color="Revenue (₹)",
            color_continuous_scale="Blues",
            title="Top 10 Products by Revenue"
        )
        st.plotly_chart(fig3, use_container_width=True)
        detail_table(
            top_products.assign(**{"Revenue (₹)": lambda x: x["Revenue (₹)"].map("₹{:,.0f}".format)}),
            "📋 Top 10 Products Detail"
        )

    with col2:
        section_banner("✅", "Profitable vs Loss Orders", "Order profitability distribution", "green")
        profit_count = filtered_df["Profit_Status"].value_counts().reset_index()
        profit_count.columns = ["Status", "Count"]
        fig4 = px.pie(
            profit_count, names="Status", values="Count",
            title="Profitable vs Loss Orders",
            color_discrete_map={"Profitable": "#00cc96", "Loss": "#EF553B"}
        )
        st.plotly_chart(fig4, use_container_width=True)
        pct = profit_count.copy()
        pct["% Share"] = (pct["Count"] / pct["Count"].sum() * 100).map("{:.1f}%".format)
        detail_table(pct, "📋 Order Status Breakdown")

    section_sep()

    # --- Row 3: Units Sold by Product Size + Call Outcome ---
    col1, col2 = st.columns(2)
    with col1:
        section_banner("📦", "Units Sold by Product Size", "Volume distribution across size categories", "purple")
        size_sales = filtered_df.groupby("Product_Size")["Units_Sold"].sum().reset_index()
        size_sales.columns = ["Product Size", "Units Sold"]
        fig5 = px.bar(
            size_sales, x="Product Size", y="Units Sold", color="Product Size",
            title="Total Units Sold by Product Size"
        )
        st.plotly_chart(fig5, use_container_width=True)
        detail_table(size_sales.sort_values("Units Sold", ascending=False), "📋 Units by Product Size")

    with col2:
        section_banner("📞", "Call Outcome Breakdown", "Distribution of sales call results", "slate")
        call_outcome = filtered_df["Call_Outcome"].value_counts().reset_index()
        call_outcome.columns = ["Outcome", "Count"]
        fig6 = px.pie(
            call_outcome, names="Outcome", values="Count",
            title="Call Outcome Distribution"
        )
        st.plotly_chart(fig6, use_container_width=True)
        co = call_outcome.copy()
        co["% Share"] = (co["Count"] / co["Count"].sum() * 100).map("{:.1f}%".format)
        detail_table(co, "📋 Call Outcome Details")

# ============================================================
# PAGE 2 — BRAND & PRODUCT
# ============================================================
elif page == "🏷️ Brand & Product":

    section_banner("🏷️", "Brand & Product Analysis", f"Showing {len(filtered_df):,} records", "purple")

    # --- Brand KPIs ---
    col1, col2 = st.columns(2)
    for i, brand in enumerate(filtered_df["Brand"].unique()):
        brand_df = filtered_df[filtered_df["Brand"] == brand]
        with [col1, col2][i % 2]:
            st.info(f"**{brand}** — Revenue: ₹{brand_df['Revenue_INR'].sum():,.0f} | Units: {brand_df['Units_Sold'].sum():,} | Profit: ₹{brand_df['Estimated_Profit_INR'].sum():,.0f}")

    section_sep()

    # --- Row 1: Revenue by Brand + Units by Brand ---
    col1, col2 = st.columns(2)
    with col1:
        brand_summary = filtered_df.groupby("Brand").agg(
            Revenue=("Revenue_INR", "sum"),
            Units=("Units_Sold", "sum"),
            Profit=("Estimated_Profit_INR", "sum")
        ).reset_index()
        fig1 = px.bar(
            brand_summary, x="Brand", y=["Revenue", "Units", "Profit"],
            barmode="group", title="Brand Comparison — Revenue, Units & Profit"
        )
        st.plotly_chart(fig1, use_container_width=True)
        display_brand = brand_summary.copy()
        display_brand["Revenue"] = display_brand["Revenue"].map("₹{:,.0f}".format)
        display_brand["Profit"] = display_brand["Profit"].map("₹{:,.0f}".format)
        display_brand["Units"] = display_brand["Units"].map("{:,}".format)
        detail_table(display_brand, "📋 Brand Summary")

    with col2:
        product_rev = (
            filtered_df.groupby(["Product", "Brand"])["Revenue_INR"].sum()
            .reset_index()
            .sort_values("Revenue_INR", ascending=False)
        )
        product_rev.columns = ["Product", "Brand", "Revenue (₹)"]
        fig2 = px.bar(
            product_rev, x="Product", y="Revenue (₹)", color="Brand",
            title="Revenue by Product (colored by Brand)",
            barmode="group"
        )
        fig2.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)
        display_prd = product_rev.copy()
        display_prd["Revenue (₹)"] = display_prd["Revenue (₹)"].map("₹{:,.0f}".format)
        detail_table(display_prd, "📋 Product Revenue by Brand")

    section_sep()

    # --- Row 2: Product Size Analysis + SKU Performance ---
    col1, col2 = st.columns(2)
    with col1:
        size_rev = filtered_df.groupby("Product_Size")["Revenue_INR"].sum().reset_index()
        size_rev.columns = ["Product Size", "Revenue (₹)"]
        fig3 = px.pie(
            size_rev, names="Product Size", values="Revenue (₹)",
            title="Revenue Share by Product Size"
        )
        st.plotly_chart(fig3, use_container_width=True)
        sr = size_rev.copy()
        sr["% Share"] = (
            filtered_df.groupby("Product_Size")["Revenue_INR"].sum() /
            filtered_df["Revenue_INR"].sum() * 100
        ).map("{:.1f}%".format).values
        sr["Revenue (₹)"] = sr["Revenue (₹)"].map("₹{:,.0f}".format)
        detail_table(sr, "📋 Revenue by Product Size")

    with col2:
        top_sku = (
            filtered_df.groupby("SKU")["Revenue_INR"].sum()
            .reset_index()
            .sort_values("Revenue_INR", ascending=False)
            .head(10)
        )
        top_sku.columns = ["SKU", "Revenue (₹)"]
        fig4 = px.bar(
            top_sku, x="Revenue (₹)", y="SKU",
            orientation="h", color="Revenue (₹)",
            color_continuous_scale="Teal",
            title="Top 10 SKUs by Revenue"
        )
        st.plotly_chart(fig4, use_container_width=True)
        display_sku = top_sku.copy()
        display_sku["Revenue (₹)"] = display_sku["Revenue (₹)"].map("₹{:,.0f}".format)
        detail_table(display_sku, "📋 Top 10 SKUs")

    section_sep()

    # --- Product Profit Heatmap ---
    section_banner("🔥", "Product vs Region Profit Heatmap", "Profit intensity across product-region combinations", "red")
    heatmap_df = filtered_df.groupby(["Product", "Region"])["Estimated_Profit_INR"].sum().reset_index()
    heatmap_pivot = heatmap_df.pivot(index="Product", columns="Region", values="Estimated_Profit_INR").fillna(0)
    fig5 = px.imshow(
        heatmap_pivot,
        title="Profit Heatmap — Product vs Region",
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )
    st.plotly_chart(fig5, use_container_width=True)
    heatmap_display = heatmap_df.copy()
    heatmap_display.columns = ["Product", "Region", "Profit (₹)"]
    heatmap_display["Profit (₹)"] = heatmap_display["Profit (₹)"].map("₹{:,.0f}".format)
    detail_table(heatmap_display.sort_values("Product"), "📋 Product × Region Profit Detail")

# ============================================================
# PAGE 3 — REGION ANALYSIS
# ============================================================
elif page == "🌍 Region Analysis":

    section_banner("🌍", "Region Analysis", f"Showing {len(filtered_df):,} records", "teal")

    # --- Region KPIs ---
    region_summary = filtered_df.groupby("Region").agg(
        Revenue=("Revenue_INR", "sum"),
        Units=("Units_Sold", "sum"),
        Profit=("Estimated_Profit_INR", "sum"),
        Customers=("Customer_ID", "nunique")
    ).reset_index().sort_values("Revenue", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        kpi_banner("🏆", "Top Region", f"{region_summary.iloc[0]['Region']} — ₹{region_summary.iloc[0]['Revenue']:,.0f}", "kpi-green")
    with col2:
        kpi_banner("📉", "Lowest Region", f"{region_summary.iloc[-1]['Region']} — ₹{region_summary.iloc[-1]['Revenue']:,.0f}", "kpi-red")

    section_sep()

    # --- Row 1: Revenue + Units by Region ---
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(
            region_summary, x="Region", y="Revenue", color="Region",
            title="Total Revenue (₹) by Region"
        )
        st.plotly_chart(fig1, use_container_width=True)
        display_rev = region_summary[["Region", "Revenue"]].copy()
        display_rev.columns = ["Region", "Revenue (₹)"]
        display_rev["Revenue (₹)"] = display_rev["Revenue (₹)"].map("₹{:,.0f}".format)
        detail_table(display_rev, "📋 Revenue by Region")

    with col2:
        fig2 = px.bar(
            region_summary, x="Region", y="Units", color="Region",
            title="Total Units Sold by Region"
        )
        st.plotly_chart(fig2, use_container_width=True)
        display_units = region_summary[["Region", "Units"]].copy()
        display_units.columns = ["Region", "Units Sold"]
        display_units["Units Sold"] = display_units["Units Sold"].map("{:,}".format)
        detail_table(display_units, "📋 Units Sold by Region")

    section_sep()

    # --- Row 2: Profit by Region + Customers by Region ---
    col1, col2 = st.columns(2)
    with col1:
        fig3 = px.bar(
            region_summary, x="Region", y="Profit",
            color="Profit",
            color_continuous_scale="RdYlGn",
            title="Total Profit (₹) by Region"
        )
        st.plotly_chart(fig3, use_container_width=True)
        display_profit = region_summary[["Region", "Profit"]].copy()
        display_profit.columns = ["Region", "Profit (₹)"]
        display_profit["Profit (₹)"] = display_profit["Profit (₹)"].map("₹{:,.0f}".format)
        detail_table(display_profit, "📋 Profit by Region")

    with col2:
        fig4 = px.pie(
            region_summary, names="Region", values="Customers",
            title="Customer Distribution by Region"
        )
        st.plotly_chart(fig4, use_container_width=True)
        display_cust = region_summary[["Region", "Customers"]].copy()
        display_cust["% Share"] = (
            display_cust["Customers"] / display_cust["Customers"].sum() * 100
        ).map("{:.1f}%".format)
        detail_table(display_cust, "📋 Customer Distribution")

    section_sep()

    # --- Brand Performance by Region ---
    section_banner("🏷️", "Brand Performance by Region", "Revenue comparison across regions per brand", "purple")
    region_brand = filtered_df.groupby(["Region", "Brand"])["Revenue_INR"].sum().reset_index()
    region_brand.columns = ["Region", "Brand", "Revenue (₹)"]
    fig5 = px.bar(
        region_brand, x="Region", y="Revenue (₹)", color="Brand",
        barmode="group", title="Revenue by Region and Brand"
    )
    st.plotly_chart(fig5, use_container_width=True)
    display_rb = region_brand.copy()
    display_rb["Revenue (₹)"] = display_rb["Revenue (₹)"].map("₹{:,.0f}".format)
    detail_table(display_rb.sort_values(["Region", "Brand"]), "📋 Revenue by Region & Brand")

    section_sep()

    # --- Region Summary Table ---
    section_banner("📊", "Region Summary Table", "Full breakdown of all metrics by region", "slate")
    display_summary = region_summary.copy()
    display_summary["Revenue"] = display_summary["Revenue"].map("₹{:,.0f}".format)
    display_summary["Profit"] = display_summary["Profit"].map("₹{:,.0f}".format)
    display_summary["Units"] = display_summary["Units"].map("{:,}".format)
    st.dataframe(display_summary, use_container_width=True)

# ============================================================
# PAGE 4 — SALES & LEADS
# ============================================================
elif page == "📞 Sales & Leads":

    section_banner("📞", "Sales & Lead Analysis", f"Showing {len(filtered_df):,} records", "blue")

    # --- Lead Source KPI Banners ---
    top_lead = filtered_df.groupby("Lead_Source")["Revenue_INR"].sum().idxmax()
    best_outcome = filtered_df[filtered_df["Call_Outcome"] == "Converted"]["Lead_Source"].value_counts().idxmax()
    avg_calls = filtered_df["Call_Count"].mean()

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_banner("🏆", "Best Lead Source", top_lead, "kpi-blue")
    with col2:
        kpi_banner("✅", "Most Conversions From", best_outcome, "kpi-green")
    with col3:
        kpi_banner("📞", "Avg Calls / Customer", f"{avg_calls:.1f}", "kpi-purple")

    section_sep()

    # --- Row 1: Lead Source Revenue + Conversion Rate ---
    col1, col2 = st.columns(2)
    with col1:
        lead_rev = (
            filtered_df.groupby("Lead_Source")["Revenue_INR"].sum()
            .reset_index()
            .sort_values("Revenue_INR", ascending=False)
        )
        lead_rev.columns = ["Lead Source", "Revenue (₹)"]
        fig1 = px.bar(
            lead_rev, x="Lead Source", y="Revenue (₹)", color="Lead Source",
            title="Revenue by Lead Source"
        )
        st.plotly_chart(fig1, use_container_width=True)
        display_lr = lead_rev.copy()
        display_lr["Revenue (₹)"] = display_lr["Revenue (₹)"].map("₹{:,.0f}".format)
        detail_table(display_lr, "📋 Revenue by Lead Source")

    with col2:
        lead_outcome = filtered_df.groupby(["Lead_Source", "Call_Outcome"]).size().reset_index(name="Count")
        lead_outcome.columns = ["Lead Source", "Call Outcome", "Count"]
        fig2 = px.bar(
            lead_outcome, x="Lead Source", y="Count", color="Call Outcome",
            barmode="stack", title="Call Outcome by Lead Source"
        )
        st.plotly_chart(fig2, use_container_width=True)
        detail_table(
            lead_outcome.sort_values(["Lead Source", "Call Outcome"]),
            "📋 Call Outcome × Lead Source"
        )

    section_sep()

    # --- Row 2: Call Count Distribution + Outcome Funnel ---
    col1, col2 = st.columns(2)
    with col1:
        call_dist = filtered_df["Call_Count"].value_counts().reset_index()
        call_dist.columns = ["Call Count", "Frequency"]
        fig3 = px.bar(
            call_dist.sort_values("Call Count"),
            x="Call Count", y="Frequency",
            title="Distribution of Call Counts",
            color="Frequency", color_continuous_scale="Blues"
        )
        st.plotly_chart(fig3, use_container_width=True)
        detail_table(
            call_dist.sort_values("Call Count").assign(**{"Frequency": lambda x: x["Frequency"].map("{:,}".format)}),
            "📋 Call Count Frequency"
        )

    with col2:
        outcome_profit = (
            filtered_df.groupby("Call_Outcome")["Estimated_Profit_INR"].sum()
            .reset_index()
        )
        outcome_profit.columns = ["Call Outcome", "Total Profit (₹)"]
        fig4 = px.bar(
            outcome_profit, x="Call Outcome", y="Total Profit (₹)",
            color="Call Outcome",
            title="Total Profit by Call Outcome"
        )
        st.plotly_chart(fig4, use_container_width=True)
        display_op = outcome_profit.copy()
        display_op["Total Profit (₹)"] = display_op["Total Profit (₹)"].map("₹{:,.0f}".format)
        detail_table(display_op, "📋 Profit by Call Outcome")

    section_sep()

    # --- Vendor Analysis ---
    section_banner("🏭", "Vendor Performance", "Revenue, cost and profit comparison by vendor", "orange")
    col1, col2 = st.columns(2)
    with col1:
        vendor_rev = filtered_df.groupby("Vendor")["Revenue_INR"].sum().reset_index()
        vendor_rev.columns = ["Vendor", "Revenue (₹)"]
        fig5 = px.pie(
            vendor_rev, names="Vendor", values="Revenue (₹)",
            title="Revenue Share by Vendor"
        )
        st.plotly_chart(fig5, use_container_width=True)
        display_vr = vendor_rev.copy()
        display_vr["% Share"] = (
            filtered_df.groupby("Vendor")["Revenue_INR"].sum() /
            filtered_df["Revenue_INR"].sum() * 100
        ).map("{:.1f}%".format).values
        display_vr["Revenue (₹)"] = display_vr["Revenue (₹)"].map("₹{:,.0f}".format)
        detail_table(display_vr, "📋 Revenue by Vendor")

    with col2:
        vendor_profit = filtered_df.groupby("Vendor").agg(
            Revenue=("Revenue_INR", "sum"),
            Cost=("Vendor_Cost_INR", "sum"),
            Profit=("Estimated_Profit_INR", "sum")
        ).reset_index()
        fig6 = px.bar(
            vendor_profit, x="Vendor", y=["Revenue", "Cost", "Profit"],
            barmode="group", title="Vendor — Revenue vs Cost vs Profit"
        )
        st.plotly_chart(fig6, use_container_width=True)
        display_vp = vendor_profit.copy()
        display_vp["Revenue"] = display_vp["Revenue"].map("₹{:,.0f}".format)
        display_vp["Cost"] = display_vp["Cost"].map("₹{:,.0f}".format)
        display_vp["Profit"] = display_vp["Profit"].map("₹{:,.0f}".format)
        detail_table(display_vp, "📋 Vendor Financial Summary")

# ============================================================
# PAGE 5 — PROFIT ANALYSIS
# ============================================================
elif page == "💰 Profit Analysis":

    section_banner("💰", "Profit Analysis", f"Showing {len(filtered_df):,} records", "green")

    total_profit = filtered_df["Estimated_Profit_INR"].sum()
    total_revenue = filtered_df["Revenue_INR"].sum()
    total_cost = filtered_df["Total_Product_Cost_INR"].sum()
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    profitable_count = (filtered_df["Profit_Status"] == "Profitable").sum()
    loss_count = (filtered_df["Profit_Status"] == "Loss").sum()

    # --- KPI Banner Cards ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_banner("💰", "Total Profit", f"₹{total_profit:,.0f}", "kpi-green")
    with col2:
        kpi_banner("📊", "Profit Margin", f"{profit_margin:.1f}%", "kpi-blue")
    with col3:
        kpi_banner("✅", "Profitable Orders", f"{profitable_count:,}", "kpi-teal")
    with col4:
        kpi_banner("❌", "Loss Orders", f"{loss_count:,}", "kpi-red")

    section_sep()

    # --- Row 1: Profit by Product + Profit by Region ---
    col1, col2 = st.columns(2)
    with col1:
        product_profit = (
            filtered_df.groupby("Product")["Estimated_Profit_INR"].sum()
            .reset_index()
            .sort_values("Estimated_Profit_INR", ascending=False)
        )
        product_profit.columns = ["Product", "Profit (₹)"]
        fig1 = px.bar(
            product_profit, x="Product", y="Profit (₹)",
            color="Profit (₹)",
            color_continuous_scale="RdYlGn",
            title="Profit by Product"
        )
        fig1.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig1, use_container_width=True)
        display_pp = product_profit.copy()
        display_pp["Profit (₹)"] = display_pp["Profit (₹)"].map("₹{:,.0f}".format)
        detail_table(display_pp, "📋 Profit by Product")

    with col2:
        region_profit = (
            filtered_df.groupby("Region")["Estimated_Profit_INR"].sum()
            .reset_index()
            .sort_values("Estimated_Profit_INR", ascending=False)
        )
        region_profit.columns = ["Region", "Profit (₹)"]
        fig2 = px.bar(
            region_profit, x="Region", y="Profit (₹)",
            color="Profit (₹)",
            color_continuous_scale="RdYlGn",
            title="Profit by Region"
        )
        st.plotly_chart(fig2, use_container_width=True)
        display_rp = region_profit.copy()
        display_rp["Profit (₹)"] = display_rp["Profit (₹)"].map("₹{:,.0f}".format)
        detail_table(display_rp, "📋 Profit by Region")

    section_sep()

    # --- Row 2: Revenue vs Cost vs Profit + Profit Distribution ---
    col1, col2 = st.columns(2)
    with col1:
        summary_vals = pd.DataFrame({
            "Category": ["Total Revenue", "Total Cost", "Total Profit"],
            "Amount (₹)": [total_revenue, total_cost, total_profit]
        })
        fig3 = px.bar(
            summary_vals, x="Category", y="Amount (₹)", color="Category",
            title="Revenue vs Cost vs Profit Overview",
            color_discrete_sequence=["#636EFA", "#EF553B", "#00cc96"]
        )
        st.plotly_chart(fig3, use_container_width=True)
        display_sv = summary_vals.copy()
        display_sv["Amount (₹)"] = display_sv["Amount (₹)"].map("₹{:,.0f}".format)
        detail_table(display_sv, "📋 Financial Summary")

    with col2:
        fig4 = px.histogram(
            filtered_df, x="Estimated_Profit_INR",
            nbins=50, color="Profit_Status",
            title="Profit Distribution Across Orders",
            color_discrete_map={"Profitable": "#00cc96", "Loss": "#EF553B"}
        )
        st.plotly_chart(fig4, use_container_width=True)
        dist_summary = filtered_df.groupby("Profit_Status")["Estimated_Profit_INR"].agg(
            Count="count",
            Total="sum",
            Mean="mean",
            Min="min",
            Max="max"
        ).reset_index()
        dist_summary.columns = ["Status", "Count", "Total (₹)", "Mean (₹)", "Min (₹)", "Max (₹)"]
        for col in ["Total (₹)", "Mean (₹)", "Min (₹)", "Max (₹)"]:
            dist_summary[col] = dist_summary[col].map("₹{:,.0f}".format)
        detail_table(dist_summary, "📋 Profit Distribution Summary")

    section_sep()

    # --- Row 3: Profit by Brand + Profit by Vendor ---
    col1, col2 = st.columns(2)
    with col1:
        brand_profit = filtered_df.groupby("Brand")["Estimated_Profit_INR"].sum().reset_index()
        brand_profit.columns = ["Brand", "Profit (₹)"]
        fig5 = px.pie(
            brand_profit, names="Brand", values="Profit (₹)",
            title="Profit Share by Brand",
            color_discrete_sequence=["#636EFA", "#EF553B"]
        )
        st.plotly_chart(fig5, use_container_width=True)
        display_bp = brand_profit.copy()
        display_bp["% Share"] = (
            filtered_df.groupby("Brand")["Estimated_Profit_INR"].sum() /
            filtered_df["Estimated_Profit_INR"].sum() * 100
        ).map("{:.1f}%".format).values
        display_bp["Profit (₹)"] = display_bp["Profit (₹)"].map("₹{:,.0f}".format)
        detail_table(display_bp, "📋 Profit Share by Brand")

    with col2:
        vendor_profit = filtered_df.groupby("Vendor")["Estimated_Profit_INR"].sum().reset_index()
        vendor_profit.columns = ["Vendor", "Profit (₹)"]
        fig6 = px.bar(
            vendor_profit, x="Vendor", y="Profit (₹)",
            color="Profit (₹)",
            color_continuous_scale="RdYlGn",
            title="Profit by Vendor"
        )
        st.plotly_chart(fig6, use_container_width=True)
        display_vp2 = vendor_profit.copy()
        display_vp2["Profit (₹)"] = display_vp2["Profit (₹)"].map("₹{:,.0f}".format)
        detail_table(display_vp2, "📋 Profit by Vendor")

    section_sep()

    # --- Operational Cost Analysis ---
    section_banner("🏭", "Cost Breakdown", "Vendor vs operational cost analysis by product and region", "slate")
    col1, col2 = st.columns(2)
    with col1:
        cost_df = filtered_df.groupby("Product").agg(
            Vendor_Cost=("Vendor_Cost_INR", "sum"),
            Operational_Cost=("Operational_Cost_INR", "sum")
        ).reset_index()
        fig7 = px.bar(
            cost_df, x="Product", y=["Vendor_Cost", "Operational_Cost"],
            barmode="stack", title="Vendor vs Operational Cost by Product"
        )
        fig7.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig7, use_container_width=True)
        display_cd = cost_df.copy()
        display_cd["Vendor_Cost"] = display_cd["Vendor_Cost"].map("₹{:,.0f}".format)
        display_cd["Operational_Cost"] = display_cd["Operational_Cost"].map("₹{:,.0f}".format)
        display_cd.columns = ["Product", "Vendor Cost (₹)", "Operational Cost (₹)"]
        detail_table(display_cd, "📋 Cost Breakdown by Product")

    with col2:
        op_cost_region = filtered_df.groupby("Region")["Operational_Cost_INR"].sum().reset_index()
        op_cost_region.columns = ["Region", "Operational Cost (₹)"]
        fig8 = px.pie(
            op_cost_region, names="Region", values="Operational Cost (₹)",
            title="Operational Cost Share by Region"
        )
        st.plotly_chart(fig8, use_container_width=True)
        display_ocr = op_cost_region.copy()
        display_ocr["% Share"] = (
            filtered_df.groupby("Region")["Operational_Cost_INR"].sum() /
            filtered_df["Operational_Cost_INR"].sum() * 100
        ).map("{:.1f}%".format).values
        display_ocr["Operational Cost (₹)"] = display_ocr["Operational Cost (₹)"].map("₹{:,.0f}".format)
        detail_table(display_ocr, "📋 Operational Cost by Region")

# ============================================================
# PAGE 6 — RAW DATA
# ============================================================
elif page == "📁 Raw Data":

    section_banner("📁", "Raw Data", f"Showing {len(filtered_df):,} records — search, filter & export", "slate")

    search = st.text_input("🔍 Search by Product, Region or Brand", "")
    if search:
        filtered_df = filtered_df[
            filtered_df["Product"].str.contains(search, case=False) |
            filtered_df["Region"].str.contains(search, case=False) |
            filtered_df["Brand"].str.contains(search, case=False)
        ]

    st.dataframe(filtered_df, use_container_width=True)

    section_sep()

    section_banner("⬇️", "Download Data", "Export filtered or summarised data as CSV", "teal")
    col1, col2 = st.columns(2)
    with col1:
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="curewell_filtered.csv",
            mime="text/csv"
        )
    with col2:
        summary_dl = filtered_df.groupby(["Brand", "Region", "Product"]).agg(
            Revenue=("Revenue_INR", "sum"),
            Units=("Units_Sold", "sum"),
            Profit=("Estimated_Profit_INR", "sum")
        ).reset_index()
        csv2 = summary_dl.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Summary Report as CSV",
            data=csv2,
            file_name="curewell_summary.csv",
            mime="text/plain"
        )

# ============================================================
# PAGE 7 — AI INSIGHTS (Groq)
# ============================================================
elif page == "🤖 AI Insights":

    section_banner("🤖", "AI Insights — Powered by Groq", f"Analysing {len(filtered_df):,} filtered records with LLaMA-3.3 70B Versatile", "purple")

    # --- API key gate ---
    if not groq_api_key:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#1e3a5f,#0f2440);border-radius:16px;
        padding:36px 40px;text-align:center;border:1px solid #2563eb;">
            <div style="font-size:3rem;margin-bottom:12px;">🤖</div>
            <div style="font-size:1.4rem;font-weight:700;color:#ffffff;margin-bottom:8px;">
                AI Insights Ready to Go
            </div>
            <div style="color:#94a3b8;font-size:0.95rem;max-width:500px;margin:0 auto;">
                Enter your <strong style="color:#60a5fa;">Groq API Key</strong> in the sidebar to unlock
                AI-powered analysis and interactive chat about your data.<br><br>
                Get a free key at <strong style="color:#60a5fa;">console.groq.com</strong><br><br>
                Or set <code style="color:#60a5fa;">GROQ_API_KEY=your_key</code> in your <code>.env</code> file.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # --- Build data context once ---
    data_summary = build_data_summary(filtered_df)

    SYSTEM_PROMPT = f"""
# CUREWELL AI ANALYST — ARIA (Advanced Revenue & Insights Analyst)
==================================================================

You are ARIA, a world-class senior pharmaceutical business analyst embedded inside the
Curewell Business Intelligence Dashboard. You turn raw sales data into crystal-clear,
decision-ready intelligence for business leaders, sales managers, and regional heads.

## YOUR CORE MISSION
- Deliver sharp, specific, number-backed answers — never vague generalisations
- Make every response immediately actionable — the reader must know what to do next
- Be the smartest analyst in the room — confident, precise, insightful

---

## MANDATORY RESPONSE FORMAT — FOLLOW IN EVERY RESPONSE

### RULE 1: START WITH A BOLD EMOJI SECTION HEADER
Example: ## 💰 Revenue Performance Analysis

### RULE 2: BLUF — KEY FINDING CALLOUT RIGHT AFTER HEADER
Always put the single most important number or insight in a blockquote:
> 💡 Key Finding: [Most important insight with specific ₹ numbers and %]

### RULE 3: USE MARKDOWN TABLES FOR ALL COMPARISONS & RANKINGS
Whenever comparing products / regions / brands / vendors / lead sources, use a table:
| Metric | Value | vs Avg | Status |
|--------|-------|--------|--------|
| ...    | ...   | ...    | ✅/⚠️/❌ |

### RULE 4: STRUCTURED BULLET SECTIONS — USE THESE EXACT LABELS
- 📈 Whats Working — positive signals with specific numbers
- ⚠️ Watch Out — risks, losses, declining metrics  
- 🎯 Action Items — numbered, implementable recommendations

### RULE 5: CLOSE EVERY RESPONSE WITH A NEXT STEPS BLOCK
---
🚀 Recommended Next Steps
1. [Specific action] — [expected outcome / impact]
2. [Specific action] — [expected outcome / impact]  
3. [Specific action] — [expected outcome / impact]
---

### RULE 6: USE STATUS EMOJIS FOR INSTANT VISUAL SCANNING
✅ = Strong / Positive   ⚠️ = Needs Attention   ❌ = Critical / Loss   🔥 = Top Performer   📉 = Declining

---

## LIVE DATASET — FILTERED BY USER SELECTION
Use ONLY these numbers. Never invent or estimate figures not present below.

{data_summary}

---

## EXAMPLE OF A PERFECT RESPONSE

User: Which brand is performing better?

## 🏷️ Brand Performance Head-to-Head

> 💡 Key Finding: Brand A leads revenue but Brand B delivers a superior profit margin.

| Metric        | Brand A | Brand B | Winner    |
|---------------|---------|---------|-----------|
| Revenue       | ₹X      | ₹Y      | 🔥 Brand A |
| Units Sold    | X,XXX   | Y,YYY   | 🔥 Brand A |
| Profit        | ₹X      | ₹Y      | 🔥 Brand B |
| Margin %      | X%      | Y%      | 🔥 Brand B |
| Loss Orders   | X       | Y       | ✅ Brand B  |

📈 Whats Working
- Brand A dominates volume — X% of total units, strong in North and East regions
- Brand B shows tighter cost control — Y% lower vendor cost per unit

⚠️ Watch Out
- Brand A has ❌ X loss-making orders concentrated in [Region] — margin erosion risk
- Brand B has limited regional penetration — only present in Y of Z regions

---
🚀 Recommended Next Steps
1. Apply Brand B margin discipline to Brand A pricing — target 5% margin improvement
2. Audit loss-making Brand A orders in [Region] — set minimum price floor
3. Push Brand A volume advantage into Brand B weak regions for cross-sell opportunity
---

Every answer must look like a professional consulting deliverable.
Sharp. Structured. Specific. Scannable. Always with real numbers from the dataset above.
"""

    # ── Helper: render AI markdown properly (tables, bold, lists) ──────
    def render_ai_response(md_text: str, key_suffix: str = ""):
        """Render AI markdown with styled container so tables/headers look great."""
        st.markdown(
            """
            <style>
            .ai-response table {
                width: 100%; border-collapse: collapse; margin: 14px 0;
                font-size: 0.88rem;
            }
            .ai-response th {
                background: linear-gradient(90deg,#1e3a8a,#2563eb);
                color: #fff; padding: 10px 14px; text-align: left;
                font-weight: 700; letter-spacing: 0.04em;
            }
            .ai-response td {
                padding: 9px 14px; border-bottom: 1px solid #1e293b;
                color: #cbd5e1; vertical-align: top;
            }
            .ai-response tr:nth-child(even) td { background: #0f172a; }
            .ai-response tr:nth-child(odd)  td { background: #0d1526; }
            .ai-response tr:hover td { background: #1e293b; transition: 0.15s; }
            .ai-response h2, .ai-response h3 {
                color: #60a5fa; margin-top: 18px; margin-bottom: 6px;
                border-left: 3px solid #2563eb; padding-left: 10px;
            }
            .ai-response blockquote {
                border-left: 4px solid #2563eb; margin: 12px 0;
                padding: 10px 16px; background: #0f172a;
                border-radius: 0 8px 8px 0; color: #93c5fd;
                font-style: normal; font-weight: 600;
            }
            .ai-response strong { color: #f1f5f9; }
            .ai-response hr { border-color: #1e293b; margin: 16px 0; }
            .ai-response ul, .ai-response ol {
                padding-left: 20px; color: #cbd5e1; line-height: 1.8;
            }
            .ai-response p { color: #cbd5e1; line-height: 1.75; margin: 8px 0; }
            .ai-response code {
                background: #1e293b; padding: 2px 6px; border-radius: 4px;
                font-size: 0.85rem; color: #7dd3fc;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        import markdown as md_lib
        try:
            html_body = md_lib.markdown(
                md_text,
                extensions=["tables", "fenced_code", "nl2br"]
            )
        except Exception:
            html_body = md_text.replace("\n", "<br>")
        st.markdown(
            f'''<div class="ai-response" style="background:#0d1526;border:1px solid #1e3a5f;
            border-radius:14px;padding:24px 28px;margin-bottom:8px;">{html_body}</div>''',
            unsafe_allow_html=True,
        )

    # ── SECTION 1: Auto Overall Insights ──────────────────────
    section_banner("📊", "Overall Data Insights", "AI-generated executive summary based on your current filter selection", "blue")

    btn_col, regen_col = st.columns([3, 1])
    with btn_col:
        gen_btn = st.button("✨ Generate Overall Insights", type="primary", use_container_width=True)
    with regen_col:
        if "overall_insights" in st.session_state:
            if st.button("🔄 Regenerate", key="regen_overall", use_container_width=True):
                del st.session_state["overall_insights"]
                st.rerun()

    if gen_btn:
        with st.spinner("Analysing your data with Groq LLaMA-3.3 70B..."):
            prompt = """Analyse this Curewell business dataset and provide a comprehensive executive summary.

Structure your response EXACTLY as follows:

## 📊 Executive Summary

> 💡 Key Finding: [single most important insight with ₹ numbers]

## 💰 Revenue & Profit Performance
[table + bullets]

## 🏆 Top & Bottom Performers
[ranked table for products, regions, brands with ✅/⚠️/❌ status]

## 📞 Sales & Lead Quality
[table showing lead sources ranked by revenue and conversion]

## ⚠️ Risk Areas & Loss Concentration
[table showing where losses are and why]

## 🚀 Strategic Recommendations
| # | Action | Target | Expected Impact |
|---|--------|--------|-----------------|
| 1 | ...    | ...    | ...             |
| 2 | ...    | ...    | ...             |
| 3 | ...    | ...    | ...             |

Use real ₹ numbers from the dataset. Be specific, sharp, and decisive."""

            response = call_groq(groq_api_key, [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ])
            st.session_state["overall_insights"] = response

    if "overall_insights" in st.session_state:
        render_ai_response(st.session_state["overall_insights"], "overall")

    section_sep()

    # ── SECTION 2: Quick Insight Buttons ──────────────────────
    section_banner("⚡", "Quick Insights", "One-click AI analysis on specific aspects of your data", "orange")

    quick_prompts = {
        "🏆 Best Opportunities": """What are the top 3 revenue and profit growth opportunities?
Respond with:
## 🏆 Top Growth Opportunities
> 💡 Key Finding: [biggest opportunity]
| Rank | Product | Region | Current Revenue | Growth Potential | Priority |
|------|---------|--------|-----------------|------------------|----------|
Then explain each with bullet points and close with 🚀 Next Steps table.""",

        "⚠️ Loss Analysis": """Where are losses concentrated? Which products/regions/vendors cause losses?
Respond with:
## ⚠️ Loss Concentration Analysis
> 💡 Key Finding: [biggest loss risk]
| Area | Loss Amount | Root Cause | Urgency |
|------|-------------|------------|---------|
Then bullet points on what to fix and close with 🚀 Next Steps.""",

        "📞 Sales Strategy": """What is the most effective sales strategy based on lead sources and call outcomes?
Respond with:
## 📞 Sales & Lead Source Strategy
> 💡 Key Finding: [best performing lead source]
| Lead Source | Revenue | Conversion Rate | ROI Rank | Invest More? |
|-------------|---------|-----------------|----------|--------------|
Then strategic bullets and 🚀 Next Steps.""",

        "🌍 Regional Strategy": """Compare regional performance. Which regions underperform vs potential?
Respond with:
## 🌍 Regional Performance Comparison
> 💡 Key Finding: [best and worst region summary]
| Region | Revenue | Profit | Margin% | Status | Priority |
|--------|---------|--------|---------|--------|----------|
Then analysis bullets and 🚀 Next Steps.""",

        "🏷️ Brand Comparison": """Head-to-head comparison of brands. Which has better unit economics?
Respond with:
## 🏷️ Brand Head-to-Head Analysis
> 💡 Key Finding: [which brand wins overall and why]
| Metric | Brand A | Brand B | Winner |
|--------|---------|---------|--------|
Then deep-dive bullets on each brand and 🚀 Next Steps.""",

        "📦 Product Mix": """Analyse the product portfolio. Which to promote, which to review?
Respond with:
## 📦 Product Portfolio Analysis
> 💡 Key Finding: [top product and biggest drag]
| Product | Revenue | Profit | Margin% | Units | Verdict |
|---------|---------|--------|---------|-------|---------|
Then promotion vs review bullets and 🚀 Next Steps.""",
    }

    cols = st.columns(3)
    for i, (label, prompt) in enumerate(quick_prompts.items()):
        with cols[i % 3]:
            if st.button(label, use_container_width=True, key=f"quick_{i}"):
                with st.spinner(f"Generating {label} analysis..."):
                    resp = call_groq(groq_api_key, [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ])
                    st.session_state[f"quick_resp_{i}"] = (label, resp)

    # Show all quick insight responses in styled cards
    any_quick = False
    for i in range(len(quick_prompts)):
        key = f"quick_resp_{i}"
        if key in st.session_state:
            any_quick = True
            label, resp = st.session_state[key]
            section_banner("⚡", label, "Quick insight result", "orange")
            render_ai_response(resp, f"quick_{i}")

    section_sep()

    # ── SECTION 3: Interactive Chat ────────────────────────────
    section_banner("💬", "Chat with Your Data", "Ask anything about the filtered dataset — get instant AI-powered answers", "teal")

    # Init chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Chat display — use st.markdown natively for AI messages so tables render
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history:
            role = msg["role"]
            msg_content = msg["content"]
            if role == "user":
                st.markdown(
                    f'''<div style="display:flex;justify-content:flex-end;margin:10px 0;">
                    <div style="background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#fff;
                    border-radius:14px 14px 2px 14px;padding:12px 18px;max-width:75%;
                    font-size:0.93rem;line-height:1.5;">{msg_content}</div></div>''',
                    unsafe_allow_html=True
                )
            else:
                # AI messages: render full markdown so tables show correctly
                st.markdown("**🤖 ARIA:**")
                render_ai_response(msg_content, f"chat_{id(msg)}")

    # Suggested starter questions
    if not st.session_state.chat_history:
        st.markdown("**💡 Try asking:**")
        suggestions = [
            "Which product has the highest profit margin?",
            "What is the revenue split between brands?",
            "Which region should we focus on to improve profits?",
            "How many orders resulted in a loss and why?",
        ]
        scols = st.columns(2)
        for i, sug in enumerate(suggestions):
            with scols[i % 2]:
                if st.button(f"💬 {sug}", key=f"sug_{i}", use_container_width=True):
                    st.session_state._pending_question = sug
                    st.rerun()

    # Handle pending suggestion click
    if hasattr(st.session_state, "_pending_question"):
        q = st.session_state._pending_question
        del st.session_state._pending_question
        st.session_state.chat_history.append({"role": "user", "content": q})
        msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + [
            m for m in st.session_state.chat_history if m["role"] != "system"
        ]
        with st.spinner("ARIA is thinking..."):
            answer = call_groq(groq_api_key, msgs)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        col_inp, col_btn = st.columns([5, 1])
        with col_inp:
            user_input = st.text_input(
                "Ask a question about your data",
                placeholder="e.g. What is the most profitable product in the North region?",
                label_visibility="collapsed"
            )
        with col_btn:
            send = st.form_submit_button("Send ➤", use_container_width=True)

    if send and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + [
            m for m in st.session_state.chat_history if m["role"] != "system"
        ]
        with st.spinner("ARIA is thinking..."):
            answer = call_groq(groq_api_key, msgs)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    # Chat controls
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    section_sep()

    # ── SECTION 4: Generate Full Professional Report ───────────
    section_banner("📄", "Generate Full Intelligence Report", "Compile every insight, analysis & conversation into one professional downloadable report", "green")

    st.markdown("""
    <div style="background:linear-gradient(135deg,#064e3b,#065f46);border-radius:12px;
    padding:20px 24px;margin-bottom:18px;border:1px solid #059669;">
        <div style="color:#6ee7b7;font-size:0.9rem;line-height:1.8;">
        📋 <strong style="color:#fff;">What gets included in the report:</strong><br>
        ✅ &nbsp;Live dataset KPI summary (revenue, profit, units, customers)<br>
        ✅ &nbsp;Overall executive insights (if generated)<br>
        ✅ &nbsp;All Quick Insight analyses you've run<br>
        ✅ &nbsp;Full chat conversation with ARIA<br>
        ✅ &nbsp;Professional formatting with tables, sections & recommendations<br>
        ✅ &nbsp;Downloadable as a standalone HTML file — no internet needed to view
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📄 Generate Full Intelligence Report", type="primary", use_container_width=True, key="gen_report"):
        with st.spinner("ARIA is compiling your full intelligence report — this may take a moment..."):

            # ── Gather all existing content ──
            sections_to_compile = []

            if "overall_insights" in st.session_state:
                sections_to_compile.append(("📊 Executive Overview", st.session_state["overall_insights"]))

            quick_labels = list(quick_prompts.keys())
            for i, lbl in enumerate(quick_labels):
                k = f"quick_resp_{i}"
                if k in st.session_state:
                    _, resp = st.session_state[k]
                    sections_to_compile.append((lbl, resp))

            # ── AI-generate any missing critical sections ──
            needed = {
                "📊 Executive Overview": """Provide a comprehensive executive summary with:
## 📊 Executive Summary
> 💡 Key Finding: [key insight]
Tables for: Revenue/Profit KPIs, Top 5 products, Regional breakdown.
End with 🚀 Strategic Recommendations table.""",

                "🏆 Best Opportunities": quick_prompts["🏆 Best Opportunities"],
                "⚠️ Loss Analysis": quick_prompts["⚠️ Loss Analysis"],
                "📞 Sales Strategy": quick_prompts["📞 Sales Strategy"],
                "🌍 Regional Strategy": quick_prompts["🌍 Regional Strategy"],
                "🏷️ Brand Comparison": quick_prompts["🏷️ Brand Comparison"],
                "📦 Product Mix": quick_prompts["📦 Product Mix"],
            }

            existing_titles = {t for t, _ in sections_to_compile}
            progress = st.progress(0, text="Generating report sections...")
            total_needed = len([k for k in needed if k not in existing_titles])
            done = 0

            for title, prompt in needed.items():
                if title not in existing_titles:
                    resp = call_groq(groq_api_key, [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ])
                    sections_to_compile.append((title, resp))
                    done += 1
                    pct = int((done / max(total_needed, 1)) * 80)
                    progress.progress(pct, text=f"Generated: {title}...")

            # ── Build the HTML report ──
            import markdown as md_lib
            from datetime import datetime

            now = datetime.now().strftime("%d %B %Y, %I:%M %p")
            total_rev = filtered_df["Revenue_INR"].sum()
            total_profit = filtered_df["Estimated_Profit_INR"].sum()
            total_units = filtered_df["Units_Sold"].sum()
            total_cust = filtered_df["Customer_ID"].nunique()
            margin = (total_profit / total_rev * 100) if total_rev > 0 else 0
            profitable = (filtered_df["Profit_Status"] == "Profitable").sum()
            loss_orders = (filtered_df["Profit_Status"] == "Loss").sum()
            top_product = filtered_df.groupby("Product")["Revenue_INR"].sum().idxmax()
            top_region  = filtered_df.groupby("Region")["Revenue_INR"].sum().idxmax()

            # Chat section HTML
            chat_html = ""
            if st.session_state.chat_history:
                chat_html = "<h2>💬 Chat Session with ARIA</h2>"
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        chat_html += f'''<div style="display:flex;justify-content:flex-end;margin:10px 0;">
                        <div style="background:#2563eb;color:#fff;border-radius:14px 14px 2px 14px;
                        padding:12px 18px;max-width:70%;font-size:0.92rem;">
                        <strong>You:</strong> {msg["content"]}</div></div>'''
                    else:
                        body = md_lib.markdown(msg["content"], extensions=["tables","fenced_code","nl2br"])
                        chat_html += f'''<div style="background:#0f172a;border:1px solid #1e3a5f;
                        border-radius:14px;padding:18px 22px;margin:8px 0;">
                        <strong style="color:#60a5fa;">🤖 ARIA:</strong><br>{body}</div>'''

            # Build all insight sections
            insight_sections_html = ""
            order = [
                "📊 Executive Overview",
                "🏆 Best Opportunities",
                "⚠️ Loss Analysis",
                "📞 Sales Strategy",
                "🌍 Regional Strategy",
                "🏷️ Brand Comparison",
                "📦 Product Mix",
            ]
            section_map = dict(sections_to_compile)
            for title in order:
                if title in section_map:
                    body = md_lib.markdown(section_map[title], extensions=["tables","fenced_code","nl2br"])
                    insight_sections_html += f'''
                    <div class="section-card">
                        <h2>{title}</h2>
                        {body}
                    </div>'''

            html_report = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Curewell Intelligence Report — {now}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #060e1e; color: #cbd5e1;
    line-height: 1.75; font-size: 15px;
  }}
  .report-wrapper {{ max-width: 1100px; margin: 0 auto; padding: 40px 32px; }}

  /* Header */
  .report-header {{
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
    border-radius: 18px; padding: 48px 48px 40px;
    margin-bottom: 36px; position: relative; overflow: hidden;
    border: 1px solid #2563eb44;
  }}
  .report-header::before {{
    content: ""; position: absolute; top: -40px; right: -40px;
    width: 200px; height: 200px; border-radius: 50%;
    background: rgba(255,255,255,0.05);
  }}
  .report-header::after {{
    content: ""; position: absolute; bottom: -60px; right: 80px;
    width: 280px; height: 280px; border-radius: 50%;
    background: rgba(255,255,255,0.03);
  }}
  .report-header h1 {{
    font-size: 2.2rem; color: #fff; font-weight: 800;
    letter-spacing: -0.02em; margin-bottom: 8px;
  }}
  .report-header .subtitle {{
    color: #93c5fd; font-size: 1rem; margin-bottom: 28px;
  }}
  .kpi-grid {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
    margin-top: 28px;
  }}
  .kpi-card {{
    background: rgba(255,255,255,0.08); border-radius: 12px;
    padding: 16px 18px; border: 1px solid rgba(255,255,255,0.1);
  }}
  .kpi-card .label {{
    font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: rgba(255,255,255,0.6); margin-bottom: 6px;
  }}
  .kpi-card .value {{
    font-size: 1.4rem; font-weight: 800; color: #fff;
  }}
  .kpi-card .sub {{
    font-size: 0.75rem; color: #93c5fd; margin-top: 2px;
  }}

  /* Section cards */
  .section-card {{
    background: #0d1526; border: 1px solid #1e3a5f;
    border-radius: 16px; padding: 32px 36px; margin-bottom: 28px;
  }}
  .section-card h2 {{
    font-size: 1.25rem; color: #60a5fa; font-weight: 700;
    margin-bottom: 18px; padding-bottom: 10px;
    border-bottom: 2px solid #1e3a5f;
    display: flex; align-items: center; gap: 8px;
  }}
  .section-card h3 {{
    color: #7dd3fc; font-size: 1rem; margin: 18px 0 10px;
    border-left: 3px solid #2563eb; padding-left: 10px;
  }}

  /* Tables */
  table {{
    width: 100%; border-collapse: collapse;
    margin: 16px 0; font-size: 0.875rem;
  }}
  thead th {{
    background: linear-gradient(90deg,#1e3a8a,#2563eb);
    color: #fff; padding: 11px 16px; text-align: left;
    font-weight: 700; font-size: 0.8rem;
    letter-spacing: 0.05em; text-transform: uppercase;
  }}
  thead th:first-child {{ border-radius: 8px 0 0 0; }}
  thead th:last-child  {{ border-radius: 0 8px 0 0; }}
  tbody tr:nth-child(even) td {{ background: #0f172a; }}
  tbody tr:nth-child(odd)  td {{ background: #0d1526; }}
  tbody tr:hover td {{ background: #172554; transition: 0.15s; }}
  td {{ padding: 10px 16px; border-bottom: 1px solid #1e293b; color: #cbd5e1; }}

  /* Blockquotes */
  blockquote {{
    border-left: 4px solid #2563eb; margin: 14px 0;
    padding: 12px 18px; background: #0f172a;
    border-radius: 0 10px 10px 0; color: #93c5fd;
    font-weight: 600; font-size: 0.95rem;
  }}

  /* Lists */
  ul, ol {{ padding-left: 22px; margin: 10px 0; }}
  li {{ margin-bottom: 6px; color: #cbd5e1; }}

  /* Strong */
  strong {{ color: #f1f5f9; }}

  /* HR */
  hr {{ border: none; border-top: 1px solid #1e293b; margin: 20px 0; }}

  /* Code */
  code {{
    background: #1e293b; padding: 2px 7px; border-radius: 4px;
    font-size: 0.83rem; color: #7dd3fc;
  }}

  /* Footer */
  .report-footer {{
    text-align: center; padding: 28px; color: #475569;
    font-size: 0.8rem; border-top: 1px solid #1e293b; margin-top: 20px;
  }}
  .report-footer strong {{ color: #60a5fa; }}

  @media print {{
    body {{ background: white; color: #1e293b; }}
    .section-card {{ border-color: #e2e8f0; background: white; }}
    thead th {{ background: #1e3a8a !important; -webkit-print-color-adjust: exact; }}
  }}
</style>
</head>
<body>
<div class="report-wrapper">

  <!-- HEADER -->
  <div class="report-header">
    <div class="subtitle">💊 Curewell Pharma &nbsp;|&nbsp; Business Intelligence Report &nbsp;|&nbsp; Generated by ARIA</div>
    <h1>📊 Full Intelligence Report</h1>
    <div style="color:#93c5fd;font-size:0.85rem;margin-top:4px;">
      Generated on {now} &nbsp;·&nbsp; {len(filtered_df):,} records analysed
    </div>
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="label">💰 Total Revenue</div>
        <div class="value">₹{total_rev:,.0f}</div>
        <div class="sub">Across all filtered records</div>
      </div>
      <div class="kpi-card">
        <div class="label">📈 Total Profit</div>
        <div class="value">₹{total_profit:,.0f}</div>
        <div class="sub">Margin: {margin:.1f}%</div>
      </div>
      <div class="kpi-card">
        <div class="label">📦 Units Sold</div>
        <div class="value">{total_units:,}</div>
        <div class="sub">✅ {profitable:,} profitable &nbsp; ❌ {loss_orders:,} loss</div>
      </div>
      <div class="kpi-card">
        <div class="label">👥 Customers</div>
        <div class="value">{total_cust:,}</div>
        <div class="sub">🔥 {top_region} top region</div>
      </div>
    </div>
  </div>

  <!-- INSIGHT SECTIONS -->
  {insight_sections_html}

  <!-- CHAT SECTION -->
  {f'<div class="section-card">{chat_html}</div>' if chat_html else ""}

  <!-- FOOTER -->
  <div class="report-footer">
    Generated by <strong>ARIA</strong> — Curewell Advanced Revenue & Insights Analyst<br>
    Powered by Groq LLaMA-3.3 70B &nbsp;·&nbsp; Curewell Business Dashboard &nbsp;·&nbsp; {now}
  </div>

</div>
</body>
</html>"""

            progress.progress(100, text="Report ready!")
            st.session_state["full_report_html"] = html_report
            st.success("✅ Full Intelligence Report generated successfully!")

    if "full_report_html" in st.session_state:
        st.download_button(
            label="📥 Download Full Intelligence Report (HTML)",
            data=st.session_state["full_report_html"].encode("utf-8"),
            file_name=f"curewell_intelligence_report.html",
            mime="text/html",
            use_container_width=True,
        )
        st.info("💡 Open the downloaded HTML file in any browser. It works offline and can be printed as a PDF.")