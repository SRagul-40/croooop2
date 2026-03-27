import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from sklearn.linear_model import LinearRegression

# -----------------------------------------------------------------------------
# 1. UI CONFIGURATION & ANIMATED BACKGROUND
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Agri-Satellite Intelligence", layout="wide")

# Creative CSS for Animating Gradient Background & Glassmorphism
st.markdown("""
    <style>
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stApp {
        background: linear-gradient(-45deg, #040d04, #0a1f0a, #051a05, #000000);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: #e8f5e9;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #2e7d32, #1b5e20);
        color: white;
        border-radius: 10px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px #4caf50;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. ML MODEL & DATA ENGINE
# -----------------------------------------------------------------------------
@st.cache_data
def train_crop_model():
    # Simulated historical data based on your provided column structure
    data = {
        "Rain Fall (mm)": np.random.randint(400, 1500, 200),
        "Fertilizer": np.random.randint(50, 300, 200),
        "Temperatue": np.random.randint(20, 45, 200),
        "Nitrogen (N)": np.random.randint(10, 150, 200),
        "Phosphorus (P)": np.random.randint(10, 150, 200),
        "Potassium (K)": np.random.randint(10, 150, 200),
        "Yeild (Q/acre)": np.random.randint(5, 60, 200)
    }
    df = pd.DataFrame(data)
    X = df[["Rain Fall (mm)","Fertilizer","Temperatue","Nitrogen (N)","Phosphorus (P)","Potassium (K)"]]
    y = df["Yeild (Q/acre)"]
    model = LinearRegression().fit(X, y)
    return model, df

LR_MODEL, RAW_DATA = train_crop_model()

# -----------------------------------------------------------------------------
# 3. SIDEBAR - SATELLITE CONTROLS & PARAMS
# -----------------------------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/628/628283.png", width=100)
st.sidebar.title("🛰️ Land Controller")

with st.sidebar.expander("📍 Target Coordinates", expanded=True):
    input_lat = st.number_input("Enter Latitude", value=13.0827, format="%.6f")
    input_lng = st.number_input("Enter Longitude", value=80.2707, format="%.6f")
    zoom_lvl = st.slider("Satellite Zoom", 10, 20, 16)

with st.sidebar.expander("🌱 Soil Analysis"):
    soil_type = st.selectbox("Soil Category", ["Black Soil", "Alluvial", "Red Soil", "Clay"])
    ph = st.slider("Soil pH", 0.0, 14.0, 6.5)
    nitro = st.number_input("Nitrogen (N)", 0, 200, 60)
    phos = st.number_input("Phosphorus (P)", 0, 200, 50)
    potas = st.number_input("Potassium (K)", 0, 200, 50)
    rain = st.number_input("Expected Rainfall (mm)", 0, 2000, 800)
    temp = st.number_input("Avg Temperature (°C)", 10, 50, 30)

# -----------------------------------------------------------------------------
# 4. MAIN INTERFACE - GOOGLE SATELLITE MAP
# -----------------------------------------------------------------------------
st.title("🌾 Agri-Satellite & Financial Intelligence")

col_map, col_yield = st.columns([3, 2])

with col_map:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Live Satellite View")
    
    # Create Folium Map with Google Satellite Tiles
    m = folium.Map(location=[input_lat, input_lng], zoom_start=zoom_lvl)
    google_sat = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
    folium.TileLayer(
        tiles=google_sat,
        attr='Google',
        name='Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add a marker for the land
    folium.Marker([input_lat, input_lng], popup="Selected Land", icon=folium.Icon(color='green')).add_to(m)
    
    st_folium(m, width="100%", height=500)
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. CROP PREDICTION & FINANCIALS (INR)
# -----------------------------------------------------------------------------
with col_yield:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 Yield & Financial Outlook")
    
    # Prediction
    # Note: Fertilizer is approximated as sum of NPK for the model
    total_fert = nitro + phos + potas 
    pred_input = np.array([[rain, total_fert, temp, nitro, phos, potas]])
    predicted_yield = LR_MODEL.predict(pred_input)[0]
    
    # FINANCIAL LOGIC (INR)
    # Average Market Price per Quintal (e.g., Rice/Wheat avg)
    avg_price_inr = 2800 
    total_net_worth = predicted_yield * avg_price_inr
    
    st.metric("Estimated Yield", f"{predicted_yield:.2f} Q/acre")
    st.metric("Total Net Worth (INR)", f"₹ {total_net_worth:,.2f}", delta="Per Acre")
    
    st.write(f"**Soil Suitability:** {soil_type}")
    st.progress(min(predicted_yield/60, 1.0))
    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # AI STRATEGY PANEL (GEMINI)
    # -----------------------------------------------------------------------------
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🤖 AI Agronomist")
    
    if st.button("Analyze Surrounding Lands"):
        # Context for AI
        context = f"""
        Location: {input_lat}, {input_lng}. 
        Soil: {soil_type}, pH: {ph}. 
        Climate: {temp}°C, {rain}mm rain.
        Predicted Yield: {predicted_yield} Q/acre.
        Task: 
        1. Suggest the most profitable crop varieties for this specific coordinate.
        2. Identify what crops are likely growing in surrounding lands.
        3. List specific seed varieties available in the Indian market.
        4. Provide a financial breakdown in Indian Rupees (INR).
        """
        
        # IMPORTANT: Replace with your actual Gemini Key
        try:
            genai.configure(api_key="YOUR_GEMINI_API_KEY")
            ai_model = genai.GenerativeModel('gemini-1.5-flash')
            response = ai_model.generate_content(context)
            st.info(response.text)
        except Exception as e:
            st.error("AI Analysis: Please configure a valid Gemini API Key.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. HISTORICAL TRENDS (FIXED PLOTLY ERROR)
# -----------------------------------------------------------------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("📈 Regional Production Trends")

# trendline="ols" requires 'statsmodels' installed
fig = px.scatter(
    RAW_DATA, 
    x="Rain Fall (mm)", 
    y="Yeild (Q/acre)", 
    trendline="ols",
    template="plotly_dark",
    color_discrete_sequence=['#4caf50']
)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center>Developed for Agri-Enterprise | v5.0 | High-Precision Mapping</center>", unsafe_allow_html=True)
