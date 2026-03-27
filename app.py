import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
import folium
from streamlit_folium import st_folium
from sklearn.linear_model import LinearRegression
import io

# -----------------------------------------------------------------------------
# 1. INITIAL SETUP & MODEL TRAINING
# -----------------------------------------------------------------------------
st.set_page_config(page_title="GeoAgri & Urban Intelligence", layout="wide")

# Mock/Load Data Logic
@st.cache_data
def load_and_train_model():
    # In a real app, you'd load your Excel file here. 
    # For this demo, I'll create a template based on your provided columns
    # cy = pd.read_excel("crop_yield_data_sheet.xlsx")
    
    # Simulating the dataset structure you provided
    data = {
        "Rain Fall (mm)": np.random.randint(400, 1200, 100),
        "Fertilizer": np.random.randint(50, 200, 100),
        "Temperatue": np.random.randint(20, 40, 100),
        "Nitrogen (N)": np.random.randint(10, 100, 100),
        "Phosphorus (P)": np.random.randint(10, 100, 100),
        "Potassium (K)": np.random.randint(10, 100, 100),
        "Yeild (Q/acre)": np.random.randint(10, 50, 100)
    }
    df = pd.DataFrame(data)
    
    X = df[["Rain Fall (mm)","Fertilizer","Temperatue","Nitrogen (N)","Phosphorus (P)","Potassium (K)"]]
    y = df["Yeild (Q/acre)"]
    
    model = LinearRegression()
    model.fit(X, y)
    return model, df

LR_MODEL, RAW_DATA = load_and_train_model()

# Gemini Config
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY" # Replace with actual key
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# -----------------------------------------------------------------------------
# 2. SIDEBAR - PARAMETER ENGINE
# -----------------------------------------------------------------------------
st.sidebar.title("🌍 Land Intelligence System")

land_mode = st.sidebar.radio("Select Land Purpose:", ["Agriculture & Seeds", "Urban Construction"])

with st.sidebar.expander("📍 Soil & Environment", expanded=True):
    soil_type = st.selectbox("Soil Type", ["Alluvial", "Clay", "Black", "Sandy", "Laterite"])
    soil_ph = st.slider("Soil pH Level", 0.0, 14.0, 6.5)
    rainfall = st.number_input("Rainfall (mm)", 0, 3000, 800)
    temp = st.number_input("Temperature (°C)", 0, 50, 30)

if land_mode == "Agriculture & Seeds":
    with st.sidebar.expander("🧪 Fertilizer (NPK) Levels"):
        nitro = st.number_input("Nitrogen (N)", 0, 200, 50)
        phos = st.number_input("Phosphorus (P)", 0, 200, 50)
        potas = st.number_input("Potassium (K)", 0, 200, 50)
        fert = st.number_input("Total Fertilizer Used", 0, 1000, 150)
else:
    with st.sidebar.expander("🏗️ Structural Params"):
        foundation_depth = st.slider("Planned Foundation Depth (m)", 1, 20, 5)
        load_req = st.selectbox("Building Type", ["Residential", "Commercial", "Industrial"])

# -----------------------------------------------------------------------------
# 3. MAP INTERFACE
# -----------------------------------------------------------------------------
st.title("🛰️ Geo-Spatial Land Analysis")

col_map, col_info = st.columns([2, 1])

with col_map:
    st.subheader("Select Coordinates")
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5) # Default India
    google_satellite = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
    folium.TileLayer(tiles=google_satellite, attr='Google Satellite', name='Google Satellite').add_to(m)
    
    map_data = st_folium(m, width=800, height=400)
    clicked = map_data.get("last_clicked")

if clicked:
    lat, lng = clicked['lat'], clicked['lng']
    st.success(f"Selected Location: Lat {lat:.4f}, Lng {lng:.4f}")

    # -------------------------------------------------------------------------
    # 4. LOGIC ENGINE
    # -------------------------------------------------------------------------
    if land_mode == "Agriculture & Seeds":
        # Predict Yield using the ML Model
        input_data = np.array([[rainfall, fert, temp, nitro, phos, potas]])
        predicted_yield = LR_MODEL.predict(input_data)[0]
        
        # Financial Logic
        market_rate_per_q = 2500 # Avg price in INR
        net_profit = predicted_yield * market_rate_per_q
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Predicted Yield", f"{predicted_yield:.2/acre}")
        c2.metric("Est. Market Value", f"₹{net_profit:,.2f}")
        c3.metric("Soil Health Index", f"{10 - abs(6.5-soil_ph):.1f}/10")

        # AI Recommendations for Seeds & Profit
        st.subheader("🌱 AI Seed & Crop Strategy")
        if st.button("Generate Profit Analysis"):
            prompt = f"""
            Location: Lat {lat}, Lng {lng}. Soil: {soil_type}, pH: {soil_ph}. 
            Temp: {temp}C, Rainfall: {rainfall}mm.
            Task: 
            1. Suggest the top 3 most profitable crops for this specific Indian coordinate.
            2. List seed varieties available in surrounding areas.
            3. Estimate the 'Net Worth' potential per acre in Indian Rupees (INR).
            4. Suggest companion crops for surrounding lands.
            """
            with st.spinner("Analyzing regional market data..."):
                response = ai_model.generate_content(prompt)
                st.info(response.text)

    else:
        # URBAN CONSTRUCTION LOGIC
        st.divider()
        st.subheader("🏗️ Structural Suitability Analysis")
        
        # Basic Structural Logic
        max_floors = 0
        if soil_type == "Black": max_floors = 2  # Poor bearing capacity
        elif soil_type == "Clay": max_floors = 4
        elif soil_type == "Alluvial": max_floors = 10
        else: max_floors = 15 # Sandy/Rock/Laterite
        
        if soil_ph < 5.0: # Acidic soil corrodes foundation
            max_floors -= 1
            
        st.warning(f"Based on soil conditions, the suggested safe limit is {max_floors} floors.")
        
        if st.button("Get Engineering AI Report"):
            prompt = f"""
            Location: Lat {lat}, Lng {lng}. Soil Type: {soil_type}, pH: {soil_ph}.
            The user wants to build a {load_req} building. 
            Analyze the soil stability for this specific region. 
            Suggest foundation types and confirm if {max_floors} floors is feasible.
            """
            response = ai_model.generate_content(prompt)
            st.write(response.text)

# -----------------------------------------------------------------------------
# 5. DATA VISUALIZATION
# -----------------------------------------------------------------------------
st.divider()
st.subheader("📈 Regional Historical Trends")
fig = px.scatter(RAW_DATA, x="Rain Fall (mm)", y="Yeild (Q/acre)", 
                 trendline="ols", title="Rainfall vs Yield Impact")
st.plotly_chart(fig, use_container_width=True)

st.markdown("<center>Agri-Urban Intelligence Suite | v4.0</center>", unsafe_allow_html=True)
