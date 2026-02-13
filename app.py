import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import google.generativeai as genai
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. API CONFIGURATION
# -----------------------------------------------------------------------------
# Get your Gemini API Key: https://aistudio.google.com/
# Get your Google Maps Key: https://console.cloud.google.com/
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY" 

genai.configure(api_key=GEMINI_API_KEY)
model_ai = genai.GenerativeModel('gemini-1.5-flash')

# -----------------------------------------------------------------------------
# 2. PAGE CONFIG & THEME
# -----------------------------------------------------------------------------
st.set_page_config(page_title="AgriLifecycle AI Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #051405; color: #e8f5e9; }
    .card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid #2e7d32; margin-bottom: 20px; }
    .stChatFloatingInputContainer { background-color: #051405 !important; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. SIDEBAR: INTEGRATING ALL 20 PARAMETERS
# -----------------------------------------------------------------------------
st.sidebar.title("🌿 Farm Control Panel")

with st.sidebar.expander("📍 1. Site & Soil", expanded=True):
    land_type = st.selectbox("Land Type", ["Flat", "Slope", "Terrace"])
    soil_condition = st.selectbox("Soil Condition", ["Healthy", "Degraded", "Saline"])
    soil_ph = st.slider("Soil pH Level", 0.0, 14.0, 6.5)

with st.sidebar.expander("🌱 2. Inputs & Seeds"):
    seed_status = st.selectbox("Seed Quality", ["Premium", "Average", "Damaged/Discolored", "Aged"])
    manure_type = st.selectbox("Organic Manure", ["Compost", "Vermicompost", "None"])
    fert_plan = st.selectbox("Fertilizer Plan", ["Standard NPK", "High Nitrogen", "Micro-nutrient Focus"])

with st.sidebar.expander("⚙️ 3. Operations & Resources"):
    water_src = st.selectbox("Water Source", ["Borewell", "River", "Rainwater Harvest"])
    water_lvl = st.select_slider("Water Level", ["Dry", "Low", "Full"])
    irrigation = st.selectbox("Irrigation System", ["Drip", "Sprinkler", "Surface"])
    labor = st.number_input("Labor Personnel", 1, 100, 10)
    tools = st.multiselect("Equipment", ["Tractor", "Seeder", "Power Tiller"], ["Tractor"])

with st.sidebar.expander("🛡️ 4. Protection & Weather"):
    climate = st.selectbox("Current Weather", ["Sunny", "Cloudy", "Heavy Rain", "Drought-like"])
    weed_ctrl = st.selectbox("Weed Control", ["Manual", "Chemical", "Mulching"])
    pest_obs = st.checkbox("Pest Activity Observed")
    disease_obs = st.checkbox("Disease Symptoms Observed")
    monitoring = st.selectbox("Field Monitoring", ["Daily Manual", "Drone Assisted", "Sensor Based"])

with st.sidebar.expander("📈 5. Post-Harvest & Records"):
    harv_tools = st.selectbox("Harvesting Tools", ["Manual Sickle", "Mechanical Harvester"])
    storage = st.selectbox("Storage Facility", ["Cold Storage", "Dry Silo", "Warehouse"])
    transport = st.selectbox("Transportation", ["Truck", "Freight Train", "Local Cart"])
    yield_metric = st.number_input("Yield Record (Q/acre)", 0.0, 100.0, 12.0)

# -----------------------------------------------------------------------------
# 4. MAIN INTERFACE: GOOGLE MAPS & LIVE LOCATION
# -----------------------------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.title("📍 Live Crop Location")
    # Manual location input or Geocoding placeholder
    lat = st.number_input("Latitude", value=13.0827, format="%.4f") # Default Chennai
    lon = st.number_input("Longitude", value=80.2707, format="%.4f")
    
    # Folium Map with Google Maps Layer
    m = folium.Map(location=[lat, lon], zoom_start=16)
    google_tiles = f"https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}&key={GOOGLE_MAPS_API_KEY}"
    folium.TileLayer(tiles=google_tiles, attr='Google', name='Google Satellite', overlay=False, control=True).add_to(m)
    folium.Marker([lat, lon], popup="Current Crop Yield Site").add_to(m)
    st_folium(m, width=900, height=450)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Diagnostic Summary")
    st.write(f"**Land Status:** {land_type} / {soil_condition}")
    st.write(f"**Seed Quality:** {seed_status}")
    st.write(f"**Water Security:** {water_lvl}")
    if pest_obs or disease_obs or seed_status == "Damaged/Discolored":
        st.error("🚨 Critical Issues Detected. Consult AI Assistant below.")
    else:
        st.success("✅ Field Status: Stable")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. GEN-AI DIAGNOSTIC CHATBOT
# -----------------------------------------------------------------------------
st.divider()
st.header("🤖 AI Agronomist Diagnostic Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask about seed damage, pests, or fertilizer plans..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Context Injection for the AI
    farm_context = f"""
    Context:
    - Location: Lat {lat}, Lon {lon}
    - Soil PH: {soil_ph}, Status: {soil_condition}
    - Seed Quality: {seed_status}
    - Weather: {climate}
    - Problems: Pests={pest_obs}, Disease={disease_obs}
    User Question: {prompt}
    
    Task: Diagnose the problem specifically mentioning if the seeds are damaged or if there are other issues based on the context. Suggest a professional agricultural solution.
    """

    with st.chat_message("assistant"):
        with st.spinner("AI is analyzing your farm data..."):
            response = model_ai.generate_content(farm_context)
            full_response = response.text
            st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
