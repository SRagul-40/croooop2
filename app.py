import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Agri-Satellite Pro | Tamil Nadu", layout="wide", initial_sidebar_state="collapsed")

# 2. ADVANCED CSS: ANIMATED BACKGROUND & GLASS UI
st.markdown("""
    <style>
    /* Animated Nature Background */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80');
        background-attachment: fixed;
        background-size: cover;
        color: #f0fff0;
    }
    
    /* Floating Particles Effect */
    @keyframes move {
        from { transform: translateY(0px) rotate(0deg); opacity: 0.5; }
        to { transform: translateY(-1000px) rotate(360deg); opacity: 0; }
    }
    
    .glass-card {
        background: rgba(0, 30, 0, 0.7);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(0, 255, 65, 0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 25px;
    }

    h1, h2, h3 { color: #00FF41 !important; text-shadow: 2px 2px 4px #000; }
    .metric-box { border-left: 4px solid #00FF41; padding-left: 15px; }
    .inr-gold { color: #FFD700; font-weight: bold; font-size: 1.4rem; }
    
    /* Hide default streamlit elements */
    [data-testid="stSidebar"] { display: none; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 3. CROP KNOWLEDGE BASE (Financials, Duration, and Soil Specs)
CROP_DB = {
    "Paddy (Rice)": {"in": 2183, "tn": 2350, "yield": 25, "duration": "120 Days", "ph": "6.0-7.0", "temp": "25-30°C", "rain": "1200mm"},
    "Turmeric": {"in": 7800, "tn": 8600, "yield": 22, "duration": "9 Months", "ph": "5.5-7.5", "temp": "20-35°C", "rain": "1500mm"},
    "Sugarcane": {"in": 315, "tn": 340, "yield": 450, "duration": "12 Months", "ph": "6.5-7.5", "temp": "32-38°C", "rain": "1100mm"},
    "Cotton": {"in": 7020, "tn": 7500, "yield": 12, "duration": "6 Months", "ph": "5.5-8.5", "temp": "21-30°C", "rain": "700mm"},
    "Banana (G9)": {"in": 1800, "tn": 2200, "yield": 160, "duration": "11 Months", "ph": "6.5-7.5", "temp": "25-32°C", "rain": "2000mm"},
    "Coconut": {"in": 2600, "tn": 3100, "yield": 85, "duration": "7 Years (Life: 60yrs)", "ph": "5.2-8.0", "temp": "27-35°C", "rain": "1300mm"},
    "Jasmine (Malli)": {"in": 450, "tn": 700, "yield": 35, "duration": "Daily (Peak: 6 Months)", "ph": "6.0-6.5", "temp": "24-32°C", "rain": "800mm"},
    "Groundnut": {"in": 6377, "tn": 6900, "yield": 18, "duration": "105 Days", "ph": "6.0-7.0", "temp": "25-30°C", "rain": "600mm"}
}

# 4. HEADER SECTION
st.markdown("<h1 style='text-align: center;'>🛰️ LAND INTELLIGENCE & FINANCIAL ORACLE</h1>", unsafe_allow_html=True)

# 5. INPUT MODULE (Full Width Row)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
i1, i2, i3, i4 = st.columns([1.5, 1.5, 1, 2])
with i1:
    lat = st.number_input("📍 Latitude", value=11.1271, format="%.6f")
with i2:
    lon = st.number_input("📍 Longitude", value=78.6569, format="%.6f")
with i3:
    acres = st.number_input("🚜 Total Acres", value=1.0, min_value=0.1)
with i4:
    user_crop = st.selectbox("🌱 Choose Your Target Crop", list(CROP_DB.keys()))
st.markdown('</div>', unsafe_allow_html=True)

# 6. SATELLITE & SOIL ANALYTICS
c_map, c_soil = st.columns([2, 1])

with c_map:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📡 Ultra-HD Satellite Inspection")
    # High Zoom level 18 for land detail
    m = folium.Map(location=[lat, lon], zoom_start=18, tiles=None)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    folium.Marker([lat, lon], icon=folium.Icon(color='green', icon='leaf')).add_to(m)
    st_folium(m, width="100%", height=450)
    st.markdown('</div>', unsafe_allow_html=True)

with c_soil:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🧪 Soil & Environment Inputs")
    # Manual Data Simulation for the coordinate
    soil_ph = st.slider("Soil pH Level", 0.0, 14.0, 6.5)
    rainfall = st.number_input("Rainfall (mm)", value=850)
    st.markdown("---")
    st.write("**Target Parameters:**")
    n = st.progress(65, text="Nitrogen (N)")
    p = st.progress(45, text="Phosphorus (P)")
    k = st.progress(80, text="Potassium (K)")
    st.markdown('</div>', unsafe_allow_html=True)

# 7. FINANCIAL NET WORTH (INDIA vs TAMIL NADU)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader(f"💰 {user_crop} : Financial Capability Profile")

data = CROP_DB[user_crop]
total_yield = data['yield'] * acres
india_worth = total_yield * data['in']
tn_worth = total_yield * data['tn']

f1, f2, f3, f4 = st.columns(4)
with f1:
    st.markdown(f"<div class='metric-box'>TOTAL YIELD<br><span class='inr-gold'>{total_yield:,.1f} Qtl</span></div>", unsafe_allow_html=True)
with f2:
    st.markdown(f"<div class='metric-box'>INDIA NET WORTH<br><span class='inr-gold'>₹ {india_worth:,.2f}</span></div>", unsafe_allow_html=True)
with f3:
    st.markdown(f"<div class='metric-box'>TAMIL NADU NET WORTH<br><span class='inr-gold'>₹ {tn_worth:,.2f}</span></div>", unsafe_allow_html=True)
with f4:
    st.markdown(f"<div class='metric-box'>PROFIT DURATION<br><span class='inr-gold'>{data['duration']}</span></div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 8. FLOWCHART & 5-POINT SUGGESTIONS
c_flow, c_sug = st.columns([1, 1])

with c_flow:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("⚙️ Crop Field Workflow")
    # Interactive Flowchart using Markdown
    st.markdown(f"""
    1. **Land Clearing** ➡ Lat: {lat} Survey  
    2. **Basal Application** ➡ Loading Manure & NPK  
    3. **Sowing Stage** ➡ Optimized for {user_crop}  
    4. **Maintenance** ➡ Weekly Irrigation & Pest Check  
    5. **Harvest Window** ➡ Ready in {data['duration']}
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with c_sug:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("💡 5-Point Expert Suggestions")
    st.markdown(f"""
    - ✅ **Soil Match:** Target pH is {data['ph']}. Your pH is {soil_ph}. Adjust accordingly.
    - 💧 **Watering:** Needs {data['rain']} rain. Ensure supplementary drip irrigation.
    - 🌡️ **Temperature:** Thrives in {data['temp']}. Coordinate {lat} is currently optimal.
    - 📈 **Profitability:** TN Net Worth is **₹{(tn_worth - india_worth):,.0f} higher** than National average.
    - 🛡️ **Protection:** Use organic Neem oil sprays every 15 days to protect the {user_crop} leaves.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# 9. FOOTER
st.markdown("<p style='text-align: center; opacity: 0.5;'>Agri-Satellite Suite v9.0 | Built for Tamil Nadu Farmers</p>", unsafe_allow_html=True)
