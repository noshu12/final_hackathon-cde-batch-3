import streamlit as st
import snowflake.connector
import pandas as pd
import time

# Page Configuration
st.set_page_config(
    page_title="IoT Analytics & Telemetry Hub",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for attractive UI
st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# Sidebar for controls
st.sidebar.title("🛠️ Control Panel")
st.sidebar.markdown("---")
st.sidebar.info("Connected to Snowflake Data Warehouse\nLayer: **Gold (ANALYTICS)**")
auto_refresh = st.sidebar.checkbox("Auto-Refresh (30s)", value=True)

st.title("🛰️ IoT Device Telemetry & Analytics Hub")
st.markdown("Real-time monitoring dashboard powered by Snowflake Gold Layer (`RAW_ANALYTICS.DEVICE_DAILY`) & Streamlit.")
st.markdown("---")

# Snowflake Connection Function
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        account="POMXEEU-LU82916",
        user="noushadalam45",
        password="Mvc/cn123123123",
        warehouse="COMPUTE_WH",
        database="HACKATHON_IOT",
        schema="RAW",
        role="ACCOUNTADMIN"
    )

conn = init_connection()

def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetch_pandas_all()

# Fetch Data from Gold Layer
try:
    df = run_query("SELECT * FROM HACKATHON_IOT.RAW.DEVICE_DAILY")
    
    if df.empty:
        st.warning("⚠️ No data found in DEVICE_DAILY table yet.")
    else:
        # Top Metrics Row
        total_devices = df['DEVICE_ID'].nunique()
        total_events = df['TOTAL_EVENTS'].sum()
        avg_lat = df['AVG_LATITUDE'].mean()
        avg_lon = df['AVG_LONGITUDE'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Active Devices", f"{total_devices}", delta="Online")
        col2.metric("Total Events", f"{total_events:,}")
        col3.metric("Avg Latitude", f"{avg_lat:.4f}°")
        col4.metric("Avg Longitude", f"{avg_lon:.4f}°")
        
        st.markdown("---")
        
        # Layout: Two columns for charts and tables
        c1, c2 = st.columns([1.2, 1])
        
        with c1:
            st.subheader("📊 Events Distribution per Device")
            # Bar chart using streamlit native chart
            chart_data = df.set_index('DEVICE_ID')[['TOTAL_EVENTS']]
            st.bar_chart(chart_data, color="#2563eb")
            
        with c2:
            st.subheader("📋 Raw Aggregated Data Feed")
            st.dataframe(df, use_container_width=True, height=250)
            
        # Additional Map or Geolocation Section
        st.markdown("---")
        st.subheader("🌍 Device Geolocation Mapping")
        if 'AVG_LATITUDE' in df.columns and 'AVG_LONGITUDE' in df.columns:
            map_df = df.rename(columns={'AVG_LATITUDE': 'lat', 'AVG_LONGITUDE': 'lon'})
            st.map(map_df[['lat', 'lon']])

except Exception as e:
    st.error(f"❌ Error connecting to Snowflake: {e}")

# Auto-refresh mechanism
if auto_refresh:
    time.sleep(30)
    st.rerun()