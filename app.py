import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import google.generativeai as genai
from datetime import datetime

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(page_title="AgriIntelligence Pro | Precision ERP", layout="wide")

# API KEYS (Replace with yours)
GEMINI_API_KEY = "YOUR_GEMINI_KEY"
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# Professional Agri-Tech Theme
st.markdown("""
    <style>
    .stApp { background: #040d04; color: #e8f5e9; }
    .card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid #2e7d32; margin-bottom: 20px; }
    .status-box { border-left: 5px solid #FFD700; padding-left: 15px; background: rgba(255, 215, 0, 0.05); }
    </style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR: THE 20-PARAMETER ENGINE ---
st.sidebar.title("🌿 Farm Control System")
st.sidebar.info("Click the Map to start analysis")

with st.sidebar.expander("📍 Land & Soil (Parameters 1-3)", expanded=True):
    soil_suitability = st.selectbox("Suitable Soil Type", ["Alluvial", "Clay", "Black", "Sandy"])
    soil_condition = st.select_slider("Soil Condition", ["Poor", "Average", "Excellent"])
    ph = st.slider("Soil pH Level", 0.0, 14.0, 6.5)

with st.sidebar.expander("🌱 Seeds & Growth (Parameters 4, 11, 14)"):
    seed_quality = st.selectbox("Seed Quality", ["Certified Elite", "Standard", "Damaged/Discolored"])
    climate = st.selectbox("Climate/Weather", ["Optimal", "Dry", "Heavy Rain"])
    fert_plan = st.text_area("Fertilizer Plan", "Standard NPK Cycle")

with st.sidebar.expander("⚙️ Operations (Parameters 5-10, 16)"):
    water_lvl = st.select_slider("Water Source Level", ["Dry", "Low", "Full"])
    irrigation = st.selectbox("Irrigation System", ["Drip", "Sprinkler", "Surface"])
    labor = st.number_input("Labor Count", 1, 100, 10)
    tools = st.multiselect("Equipment", ["Tractor", "Seeder", "Harvester"], ["Tractor"])

with st.sidebar.expander("🛡️ Protection (Parameters 12-13, 15)"):
    weed = st.checkbox("Weed Control Required")
    pest = st.checkbox("Pest Activity")
    disease = st.checkbox("Disease Symptoms")
    monitoring = st.selectbox("Field Monitoring", ["Manual", "Sensor", "Drone"])

with st.sidebar.expander("📈 Logistics (Parameters 17-20)"):
    storage = st.selectbox("Storage Facility", ["Cold Storage", "Silo", "Warehouse"])
    transport = st.selectbox("Transportation", ["Truck", "Freight"])
    # Measurement and Record Keeping handled in graphs below

# --- 3. INTERACTIVE MAP: CLICK TO ANALYZE ---
st.title("🗺️ Satellite Land Intelligence")
col_map, col_diag = st.columns([2, 1])

with col_map:
    # Use Google Satellite Hybrid (lyrs=y)
    m = folium.Map(location=[13.0827, 80.2707], zoom_start=16)
    google_satellite = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
    folium.TileLayer(tiles=google_satellite, attr='Google', name='Google Satellite').add_to(m)
    
    map_data = st_folium(m, width=850, height=450)
    clicked = map_data.get("last_clicked") if map_data else None

with col_diag:
    if clicked:
        st.markdown('<div class="card status-box">', unsafe_allow_html=True)
        st.success(f"📍 Analysis Locked: {clicked['lat']:.4f}, {clicked['lng']:.4f}")
        
        # CHATBOT AI SUPPORT
        st.subheader("🤖 AI Diagnostic Expert")
        user_msg = st.text_input("Report a problem (e.g. 'Seeds are damaged'):")
        if st.button("Consult AI"):
            context = f"Soil: {ph} pH, Seed Quality: {seed_quality}, Pests: {pest}. Problem: {user_msg}"
            with st.spinner("AI analyzing site..."):
                response = ai_model.generate_content(context)
                st.write(response.text)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👆 Click on a green agricultural field on the map to start.")

# --- 4. PREDICTIVE ANALYTICS & HISTORICAL COMPARISON ---
if clicked:
    st.divider()
    st.header("📊 Multi-Year Yield & Input Analysis")
    
    # CALCULATE CURRENT YIELD (Based on your parameters)
    current_yield = 15.0 # Base yield
    if soil_condition == "Excellent": current_yield += 3.5
    if seed_quality == "Certified Elite": current_yield += 4.0
    if seed_quality == "Damaged/Discolored": current_yield -= 6.0
    if pest: current_yield -= 5.0

    # DATA FOR GRAPH 1: Historical Comparison
    # Simulate a "Set of Years"
    years = ['2021', '2022', '2023', '2024', '2025 (Current Prediction)']
    historical_yields = [12.4, 14.1, 13.5, 15.8, current_yield]
    
    # DATA FOR GRAPH 2: Input vs Output (Sensitivity Analysis)
    # How yield changes as you increase 'Fertilizer/Labor'
    inputs_range = np.linspace(0, 100, 10)
    output_yield = [current_yield * (1 + (x/200)) for x in inputs_range] # Simulated growth

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📅 Year-on-Year Yield Growth")
        fig1 = px.line(x=years, y=historical_yields, markers=True, 
                      title="Historical vs. Current Year Yield (Q/acre)")
        fig1.update_traces(line_color='#2e7d32', line_width=4)
        # Highlight current year point in Gold
        fig1.add_trace(go.Scatter(x=[years[-1]], y=[historical_yields[-1]], 
                                 mode='markers', marker=dict(size=15, color='Gold'), name='Current Prediction'))
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_g2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📈 Input vs Output Correlation")
        fig2 = px.area(x=inputs_range, y=output_yield, 
                      title="Predicted Yield Response to Input Intensity",
                      labels={'x': 'Input Level (Fertilizer/Labor %)', 'y': 'Yield Output (Q)'})
        fig2.update_traces(fillcolor='rgba(46, 125, 50, 0.3)', line_color='#2e7d32')
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
