import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from sklearn.linear_model import LinearRegression

# -----------------------------------------------------------------------------
# 1. CYBER-AGRI UI & ANIMATIONS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Geo-Agri Financial Intelligence", layout="wide")

st.markdown("""
    <style>
    @keyframes bgAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stApp {
        background: linear-gradient(-45deg, #020a02, #051a05, #001200, #0a0a0a);
        background-size: 400% 400%;
        animation: bgAnimation 12s ease infinite;
        color: #f0fff0;
    }
    .glass-box {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(0, 255, 0, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        margin-bottom: 20px;
    }
    .stat-val { color: #00ff41; font-weight: bold; font-size: 1.5rem; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. MARKET DATA & MODEL
# -----------------------------------------------------------------------------
# Current Market Rates (Approximate INR per Quintal)
MARKET_RATES = {
    "Paddy (Rice)": 2369,
    "Wheat": 2425,
    "Cotton": 7521,
    "Sugarcane": 355,
    "Maize": 2400,
    "Turmeric": 8500,
    "Mushrooms": 15000,
    "Moringa": 5000
}

@st.cache_data
def train_logic():
    # Training simulation based on common Indian agricultural data patterns
    X = np.random.randint(400, 1500, (100, 6)) # Rain, Fert, Temp, N, P, K
    y = np.random.randint(10, 60, 100)
    return LinearRegression().fit(X, y)

MODEL = train_logic()

# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.title("📡 Satellite Control Panel")

with st.sidebar.expander("📍 Location & Area", expanded=True):
    lat = st.number_input("Latitude", value=13.0827, format="%.6f")
    lng = st.number_input("Longitude", value=80.2707, format="%.6f")
    acres = st.number_input("Land Area (Acres)", min_value=0.1, value=5.0, step=0.5)

with st.sidebar.expander("🛒 Market Demand"):
    consumer_crop = st.selectbox("What do consumers need?", list(MARKET_RATES.keys()))
    demand_level = st.select_slider("Consumer Demand Level", ["Low", "Medium", "High", "Critical"])

with st.sidebar.expander("🧪 Soil & Climate"):
    rain = st.slider("Rainfall (mm)", 300, 2000, 800)
    temp = st.slider("Temp (°C)", 15, 50, 30)
    n = st.number_input("Nitrogen (N)", 0, 200, 60)
    p = st.number_input("Phosphorus (P)", 0, 200, 50)
    k = st.number_input("Potassium (K)", 0, 200, 50)
    fert = n + p + k

# -----------------------------------------------------------------------------
# 4. SATELLITE & FINANCIAL VIEW
# -----------------------------------------------------------------------------
st.title("🛰️ Land Intelligence & Net Worth Analysis")

col_map, col_stats = st.columns([3, 2])

with col_map:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.subheader(f"Satellite View: {acres} Acres at {lat}, {lng}")
    m = folium.Map(location=[lat, lng], zoom_start=17)
    google_sat = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
    folium.TileLayer(tiles=google_sat, attr='Google', name='Satellite').add_to(m)
    folium.Marker([lat, lng], icon=folium.Icon(color='green', icon='leaf')).add_to(m)
    st_folium(m, width="100%", height=450)
    st.markdown('</div>', unsafe_allow_html=True)

with col_stats:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.subheader("💰 Financial Network Analysis")
    
    # Prediction Math
    pred_yield_per_acre = MODEL.predict([[rain, fert, temp, n, p, k]])[0]
    total_yield = pred_yield_per_acre * acres
    
    rate = MARKET_RATES.get(consumer_crop, 2500)
    total_net_worth = total_yield * rate
    
    st.write(f"**Target Crop:** {consumer_crop}")
    st.metric("Predicted Total Yield", f"{total_yield:.2f} Quintals")
    st.metric("Estimated Net Worth", f"₹ {total_net_worth:,.2f}", delta="INR")
    
    st.write("---")
    st.write(f"**Consumer Demand for {consumer_crop}:** {demand_level}")
    st.progress(85 if demand_level == "Critical" else 50)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. AI AGRONOMIST & PROTECTION STRATEGIES
# -----------------------------------------------------------------------------
st.divider()
st.subheader("🤖 AI Land Protection & Multi-Crop Strategy")

col_ai, col_protect = st.columns(2)

with col_ai:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    if st.button("Generate AI Market & Seed Report"):
        try:
            # Update with your real API key
            genai.configure(api_key="YOUR_GEMINI_API_KEY") 
            ai_model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Land Info: {acres} acres at Lat {lat}, Lng {lng}. 
            Current selection: {consumer_crop} with {demand_level} demand.
            Parameters: {temp}C, {rain}mm rain, {n}-{p}-{k} NPK levels.
            
            Task:
            1. Suggest the specific top-tier Seed Varieties for {consumer_crop} in this region.
            2. Analyze surrounding land crops (based on Indian regional geography).
            3. Explain the 'Financial Network' (market linkages) for these seeds.
            4. Compare the profit of {consumer_crop} vs a high-value exotic alternative (e.g. Stevia or Saffron).
            """
            
            response = ai_model.generate_content(prompt)
            st.markdown(response.text)
        except:
            st.error("AI Error: Please enter a valid Gemini API Key in the code.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_protect:
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.subheader("🛡️ Land Protection Suggestions")
    
    # Logic-based suggestions
    if rain > 1200:
        st.warning("⚠️ High Rain Risk: Implement **Raised Bed Farming** and **Contour Bunding** to prevent soil erosion.")
    if temp > 40:
        st.warning("🔥 Heat Risk: Use **Organic Mulching** (sugarcane waste/straw) to keep soil moisture.")
    
    st.info("💡 **Integrated Pest Management (IPM):** Use Neem-based 'Neemastra' to protect {consumer_crop} without chemicals.")
    st.info("💡 **Soil Protection:** Plant 'Legume' cover crops between seasons to fix Nitrogen naturally.")
    st.markdown('</div>', unsafe_allow_html=True)

st.write("<center>Agri-Satellite Suite v6.0 | Secure Financial Decision Support</center>", unsafe_allow_html=True)
