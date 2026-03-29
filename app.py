import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="TN Agri-Satellite Intelligence", layout="wide", initial_sidebar_state="collapsed")

# 2. CREATIVE STYLING (Animated Background & Glass UI)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #021a02, #072b07, #001f3f, #000000);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #e0ffe0;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    [data-testid="stSidebar"] { display: none; }
    .main .block-container { padding: 1rem 3rem; max-width: 100%; }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(0, 255, 0, 0.2);
        margin-bottom: 20px;
    }
    .metric-title { color: #00ff41; font-weight: bold; font-size: 1.1rem; }
    .tn-val { color: #FFD700; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 3. COMPREHENSIVE CROP DATA ENGINE
# Schema: [IndiaPrice, TNPrice, YieldPerAcre, UniqueSuggestion]
CROP_MASTER = {
    "Staple Farming": {
        "Paddy (Rice)": [2183, 2350, 25, "Use SRI (System of Rice Intensification) to save 40% water and increase grain weight."],
        "Ragi (Finger Millet)": [3846, 4100, 12, "Best suited for dry red soil; transplant 20-day old seedlings for maximum tillering."],
        "Bajra (Pearl Millet)": [2500, 2750, 10, "Highly drought resistant; ensure good drainage to prevent ergot disease."],
        "Jowar (Sorghum)": [3180, 3400, 11, "Ideal for rotation with pulses; harvest at physiological maturity for fodder quality."],
        "Maize (Corn)": [2090, 2250, 30, "Apply Nitrogen in 3 split doses (basal, knee-high, and tasseling stages)."],
        "Pulses (Urad/Moong)": [6950, 7400, 4, "Seed treatment with Rhizobium is mandatory for natural nitrogen fixation."]
    },
    "Dry Land Crops": {
        "Groundnut": [6377, 6800, 15, "Apply Gypsum at 400kg/ha during the 45th day to ensure bold nut filling."],
        "Sesame (Gingelly)": [8635, 9200, 3, "Thinning is vital; maintain 15cm spacing between plants for high oil content."],
        "Cotton": [7020, 7500, 12, "Use yellow sticky traps and 'topping' (nipping the terminal bud) at 90 days."],
    },
    "Cash Crops": {
        "Banana": [1800, 2100, 150, "Install drip fertigation and use high-density planting for export-quality 'G9' variety."],
        "Sugarcane": [315, 340, 450, "Adopt 'Sustained Sugarcane Initiative' (SSI) using bud chips to save seed cost."],
        "Coconut": [2500, 2900, 80, "Apply 50kg of farmyard manure and TNAU Coconut Tonic for button-shedding control."],
    },
    "Plantation (South)": {
        "Rubber": [15000, 16500, 8, "Use rain-guards during monsoons in Kanyakumari to ensure year-round tapping."],
        "Tea": [140, 165, 800, "Maintain shade trees like Silver Oak to prevent leaf scorch in the Nilgiris."],
        "Cashew": [8000, 9500, 6, "Prune dead wood after harvest; apply fertilizers in a circular trench around the drip line."]
    },
    "Spices & High Value": {
        "Turmeric": [7500, 8500, 20, "Process in 'Erode Steam Boilers' to retain high curcumin levels."],
        "Chilli": [12000, 14500, 15, "Samba variety needs careful drying on cement floors to prevent fungal growth."],
        "Tamarind": [4500, 5200, 40, "Value-add by de-seeding and brick-packing for 3x profit in urban markets."]
    },
    "Vegetables & Fruits": {
        "Tomato": [1500, 1800, 100, "Use staking (trellis system) for hybrid varieties to prevent fruit rot."],
        "Onion (Small)": [2500, 3200, 60, "TN-specific 'CO' varieties perform best; ensure field curing for 3 days after harvest."],
        "Drumstick": [3000, 4500, 80, "Adopt 'PKM-1' variety; pinch terminal shoots at 3 feet to encourage branching."],
        "Mango": [4000, 5500, 40, "Practice 'High Density Planting' and off-season pruning for Banganapalli/Alphonso."]
    },
    "Flower Farming": {
        "Jasmine (Malli)": [400, 650, 30, "Madurai Malli: Pick buds before 6 AM; use refrigerated transport for Chennai/Dubai exports."],
        "Rose": [200, 350, 40, "Prune in October for Pishanam season flowering; use micronutrient sprays for color."],
    }
}

# 4. TOP INPUT SECTION
st.markdown("<h1 style='text-align: center; color: #00FF41; margin-bottom: 20px;'>🌾 TAMIL NADU PRECISION AGRI-SATELLITE v8.0</h1>", unsafe_allow_html=True)

with st.container():
    c1, c2, c3, c4 = st.columns([2,2,2,3])
    with c1:
        lat = st.number_input("📍 Latitude", value=9.9252, format="%.4f")
    with c2:
        lon = st.number_input("📍 Longitude", value=78.1198, format="%.4f")
    with c3:
        acres = st.number_input("🚜 Total Acres", value=1.0, min_value=0.1)
    with c4:
        category = st.selectbox("📂 Select Crop Category", list(CROP_MASTER.keys()))

# 5. LOCATION IDENTITY & SATELLITE (FULL WIDTH)
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
col_map, col_loc = st.columns([3, 1])

with col_map:
    # Validate Coordinates
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        st.error("Invalid Coordinates. Defaulting to Madurai Region.")
        lat, lon = 9.92, 78.11
        
    m = folium.Map(location=[lat, lon], zoom_start=18)
    google_sat = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
    folium.TileLayer(tiles=google_sat, attr='Google', name='Satellite').add_to(m)
    folium.Marker([lat, lon], popup="Your Field Boundary").add_to(m)
    st_folium(m, width="100%", height=350)

with col_loc:
    st.subheader("🗺️ Exact Location Profile")
    st.write(f"**Coordinates:** {lat}, {lon}")
    # Simple Regional Detection
    if lat < 10.0: zone = "South Tamil Nadu (Pishanam Belt)"
    elif lat > 11.5: zone = "North Tamil Nadu (Cauvery/Palar Belt)"
    else: zone = "Central TN (Madurai/Trichy Region)"
    
    st.info(f"**Zone:** {zone}")
    st.markdown("""
    **Current Season:**  
    🍂 *Pishanam (Nov-Feb)*  
    Targeting post-monsoon harvest.
    """)
st.markdown('</div>', unsafe_allow_html=True)

# 6. FINANCIAL NETWORK & UNIQUE SUGGESTIONS
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader(f"💰 Net Worth Analysis for {category}")

selected_crops = CROP_MASTER[category]
results = []
for name, info in selected_crops.items():
    india_net = info[2] * acres * info[0]
    tn_net = info[2] * acres * info[1]
    results.append({
        "Variety": name,
        "Total Yield (Qtl)": f"{info[2] * acres:.1f}",
        "India Net Worth": f"₹{india_net:,.0f}",
        "TN Net Worth": f"₹{tn_net:,.0f}",
        "Expert Suggestion": info[3]
    })

df_res = pd.DataFrame(results)
st.table(df_res)
st.markdown('</div>', unsafe_allow_html=True)

# 7. HISTORICAL 5-YEAR TREND & FLOWCHART
col_chart, col_flow = st.columns([2, 1])

with col_chart:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📈 5-Year Market Growth (INR/Acre)")
    years = [2020, 2021, 2022, 2023, 2024]
    fig = go.Figure()
    # Trend for top 3 crops in category
    for name in list(selected_crops.keys())[:3]:
        base = selected_crops[name][1] * selected_crops[name][2]
        trend = [base * (1 + (i*0.08) + np.random.uniform(-0.04, 0.04)) for i in range(-2, 3)]
        fig.add_trace(go.Scatter(x=years, y=trend, name=name, mode='lines+markers', line=dict(width=3)))
    
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_flow:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("⚙️ Field Workflow")
    st.markdown("""
    **STAGE 1: ANALYSIS**  
    ➡ Soil Health Mapping  
    ➡ Water Salinity Test  
    
    **STAGE 2: PREPARATION**  
    ➡ Deep Summer Ploughing  
    ➡ Basal Organic Loading  
    
    **STAGE 3: CULTIVATION**  
    ➡ Precision Sowing  
    ➡ Fertigation Scheduling  
    
    **STAGE 4: PROTECTION**  
    ➡ Bio-Pesticide Shield  
    ➡ Weed Management  
    
    **STAGE 5: COMMERCE**  
    ➡ Direct Market Linkage  
    """)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<center style='opacity:0.6;'>Tamil Nadu Integrated Agri-Decision System | Satellite Data v8.2</center>", unsafe_allow_html=True)
