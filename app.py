import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import base64
import os

st.set_page_config(page_title="Satyam Analytics Dashboard", layout="wide")

# Sidebar branding
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
st.sidebar.markdown("<h2 style='text-align: center;'>ANYTHING Analytics</h2>", unsafe_allow_html=True)


def load_data(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    else:
        return None

st.sidebar.header("Upload Data (required)")
inf_file = st.sidebar.file_uploader("Influencers CSV", type="csv")
posts_file = st.sidebar.file_uploader("Posts CSV", type="csv")
track_file = st.sidebar.file_uploader("Tracking Data CSV", type="csv")
payouts_file = st.sidebar.file_uploader("Payouts CSV", type="csv")

influencers = load_data(inf_file)
posts = load_data(posts_file)
tracking_data = load_data(track_file)
payouts = load_data(payouts_file)

st.title("Satyam Analytics Dashboard")

if any(x is None for x in (influencers, posts, tracking_data, payouts)):
    st.warning("Please upload all required CSV files to view the dashboard.")
    st.stop()

required_columns = {'ID', 'name', 'category', 'gender', 'follower_count', 'platform'}
if not required_columns.issubset(set(influencers.columns)):
    st.error(f"Influencers CSV is missing required columns: {required_columns - set(influencers.columns)}")
    st.write("Columns found:", influencers.columns.tolist())
    st.stop()

posts.columns = posts.columns.str.strip()
required_post_columns = {'influencer_id', 'platform', 'date', 'URL', 'caption', 'reach', 'likes', 'comments'}
if not required_post_columns.issubset(set(posts.columns)):
    st.error(f"Posts CSV is missing required columns: {required_post_columns - set(posts.columns)}")
    st.write("Columns found:", posts.columns.tolist())
    st.stop()

tracking_data.columns = tracking_data.columns.str.strip()
required_tracking_columns = {'source', 'campaign', 'influencer_id', 'user_id', 'product', 'date', 'orders', 'revenue'}
if not required_tracking_columns.issubset(set(tracking_data.columns)):
    st.error(f"Tracking Data CSV is missing required columns: {required_tracking_columns - set(tracking_data.columns)}")
    st.write("Columns found:", tracking_data.columns.tolist())
    st.stop()

st.sidebar.header("Data Filters")
brands = tracking_data['product'].unique()
brand_filter = st.sidebar.multiselect("Brand/Product", options=brands, default=list(brands))
categories = influencers['category'].unique()
category_filter = st.sidebar.multiselect("Influencer Type", options=categories, default=list(categories))
platforms = influencers['platform'].unique()
platform_filter = st.sidebar.multiselect("Platform", options=platforms, default=list(platforms))

filtered_influencers = influencers[
    influencers['category'].isin(category_filter) &
    influencers['platform'].isin(platform_filter)
]
filtered_tracking = tracking_data[
    tracking_data['product'].isin(brand_filter) &
    tracking_data['influencer_id'].isin(filtered_influencers['ID'])
]

# --- Dashboard Layout ---
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Influencers", len(filtered_influencers))
with col2:
    st.metric("Total Posts", len(posts))
with col3:
    st.metric("Total Revenue", f"₹{filtered_tracking['revenue'].sum():,.0f}")

st.markdown("---")

# Post Performance
st.subheader(":bar_chart: Post Performance")
st.dataframe(posts.groupby('influencer_id')[['reach', 'likes', 'comments']].sum().reset_index(), use_container_width=True)

st.markdown("---")

# Influencer Performance
st.subheader(":trophy: Influencer Performance")
influencer_perf = tracking_data.groupby('influencer_id')[['orders', 'revenue']].sum().reset_index()
st.dataframe(influencer_perf, use_container_width=True)

st.markdown("---")

# ROI & Incremental ROAS
st.subheader(":money_with_wings: ROI & Incremental ROAS")
tracking_data['ad_spend'] = tracking_data['orders'] * 50
tracking_data['ROAS'] = tracking_data['revenue'] / tracking_data['ad_spend']
tracking_data['ROI'] = (tracking_data['revenue'] - tracking_data['ad_spend']) / tracking_data['ad_spend']
st.success("Average ROAS and ROI by Campaign:")
st.dataframe(tracking_data.groupby('campaign')[['ROAS', 'ROI']].mean().reset_index(), use_container_width=True)

st.markdown("---")

# Insights
st.subheader(":bulb: Insights")
top_influencers = filtered_tracking.groupby('influencer_id')['revenue'].sum().sort_values(ascending=False).head(5)
st.markdown("**Top Influencers by Revenue**")
st.table(top_influencers)
best_personas = filtered_tracking.merge(influencers, left_on='influencer_id', right_on='ID')
persona_perf = best_personas.groupby('category')['revenue'].mean().sort_values(ascending=False)
st.markdown("**Best Personas (by Category Revenue)**")
st.table(persona_perf)
if 'ROAS' in filtered_tracking.columns:
    poor_rois = filtered_tracking.groupby('influencer_id')['ROAS'].mean().sort_values().head(5)
    st.markdown("**Influencers with Poor ROAS**")
    st.table(poor_rois)
else:
    poor_rois = None

# PDF Insights Preview
st.markdown("---")
def generate_insights_pdf(top_influencers, persona_perf, poor_rois):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "HealthKart Influencer Campaign Insights Summary", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Top Influencers by Revenue", ln=True)
    pdf.set_font("Arial", size=10)
    for idx, value in top_influencers.items():
        pdf.cell(0, 8, f"Influencer ID: {idx} | Revenue: {value}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Best Personas (by Category Revenue)", ln=True)
    pdf.set_font("Arial", size=10)
    for idx, value in persona_perf.items():
        pdf.cell(0, 8, f"Category: {idx} | Avg Revenue: {value:.2f}", ln=True)
    pdf.ln(5)

    if poor_rois is not None:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Influencers with Poor ROAS", ln=True)
        pdf.set_font("Arial", size=10)
        for idx, value in poor_rois.items():
            pdf.cell(0, 8, f"Influencer ID: {idx} | ROAS: {value:.2f}", ln=True)
        pdf.ln(5)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    temp_file.close()
    return temp_file.name

if st.button("Show Insights Summary as PDF"):
    pdf_path = generate_insights_pdf(top_influencers, persona_perf, poor_rois)
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    os.remove(pdf_path)

st.markdown("---")

st.subheader(":moneybag: Payout Tracking")
st.dataframe(payouts, use_container_width=True)

st.markdown("---")

st.download_button("Export Filtered Tracking Data to CSV", filtered_tracking.to_csv(index=False), "filtered_tracking.csv")

st.info("To run the dashboard, open your terminal and run: streamlit run app.py. Open the local URL provided in your browser.")
