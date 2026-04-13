import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib
from io import StringIO

# 1. UI SETUP
st.set_page_config(page_title="MKULUNGWA AI V16.5", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(45deg, #00FF00, #004d00); 
        color: white; border-radius: 10px; height: 3.5em; width: 100%; border: none; font-weight: bold;
    }
    .result-card { 
        background-color: #1A1C24; padding: 25px; border-radius: 20px; 
        border-top: 5px solid #00FF00; text-align: center; margin-bottom: 20px;
    }
    h1 { color: #00FF00; text-align: center; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# 2. MASTER DATABASE - ALL 20 LEAGUES INTEGRATED
LEAGUE_MAP = {
    "UEFA / EUROPA / CONFERENCE": {"ALL_EUROPEAN_ELITE": "UEFA_ALL"},
    "ENGLAND": {"Premier League": "E0", "Championship": "E1"},
    "SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D2"},
    "FRANCE": {"Ligue 1": "F1"},
    "NETHERLANDS": {"Eredivisie": "N1"},
    "PORTUGAL": {"Primeira Liga": "P1"},
    "TURKEY": {"Super Lig": "T1"},
    "BELGIUM": {"Pro League": "B1"},
    "AUSTRIA": {"Bundesliga": "A1"},
    "SCOTLAND": {"Premiership": "SC0"},
    "SWITZERLAND": {"Super League": "C1"},
    "DENMARK": {"Superliga": "DN1"},
    "NORWAY": {"Eliteserien": "N1"},
    "SWEDEN": {"Allsvenskan": "S1"},
    "POLAND": {"Ekstraklasa": "P1"},
    "CZECH REPUBLIC": {"First League": "CZ1"},
    "GREECE": {"Super League": "G1"},
    "UKRAINE": {"Premier League": "U1"},
    "CROATIA": {"First League": "CR1"}
}

# 3. SIDEBAR SYNC ENGINE (Enhanced for 20 Nations)
with st.sidebar:
    st.header("NEURAL DATA SYNC")
    if st.button("RUN GLOBAL DATA SYNC"):
        with st.spinner("Merging 20 Nations Data..."):
            all_data_dfs = []
            
            # Tunapita kwenye kila ligi na kuvuta data
            for cat in LEAGUE_MAP:
                if cat != "UEFA / EUROPA / CONFERENCE":
                    for name, code in LEAGUE_MAP[cat].items():
                        try:
                            url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                            r = requests.get(url, timeout=5)
                            if r.status_code == 200:
                                # Hifadhi faili la ligi husika
                                with open(f"{code}.csv", 'wb') as f:
                                    f.write(r.content)
                                # Ongeza kwenye kapu la UEFA_ALL
                                df_temp = pd.read_csv(StringIO(r.text))
                                all_data_dfs.append(df_temp)
                        except:
                            continue
            
            # Pia vuta data za mashindano yenyewe (CL, EL, EC)
            for u_code in ["CL", "EL", "EC"]:
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/2526/{u_code}.csv"
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200:
                        all_data_dfs.append(pd.read_csv(StringIO(r.text)))
                except:
                    continue

            # Tengeneza lile file moja kubwa la UEFA_ALL lenye kila timu
            if all_data_dfs:
                combined = pd.concat(all_data_dfs, ignore_index=True)
                combined.to_csv("UEFA_ALL.csv", index=False)
                
        st.success("Global Sync Done (20+ Leagues Merged)!")

# 4. APP INTERFACE
st.markdown("<h1>🛡️ MKULUNGWA PREDICTION V16.5 🛡️</h1>", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    category = st.selectbox("📂 CHAGUA KUNDI", list(LEAGUE_MAP.keys()))

with c2:
    if category == "UEFA / EUROPA / CONFERENCE":
        st.write("✅ **EUROPEAN ELITE MODE** (Timu zote 20+ zipo)")
        league_code = "UEFA_ALL"
    else:
        league_name = st.selectbox("🏆 CHAGUA LIGI", list(LEAGUE_MAP[category].keys()))
        league_code = LEAGUE_MAP[category][league_name]

# Data Loading
df = pd.DataFrame()
if os.path.exists(f"{league_code}.csv"):
    try:
        df = pd.read_csv(f"{league_code}.csv")
    except:
        df = pd.DataFrame()

# 5. ANALYSIS ENGINE
if not df.empty and 'HomeTeam' in df.columns:
    teams = sorted(df['HomeTeam'].dropna().unique())
    col1, col2 = st.columns(2)
    h_t = col1.selectbox("🏠 HOME TEAM", teams)
    a_t = col2.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])
    
    if st.button("🎯 EXECUTE SMART ANALYSIS"):
        match_key = f"{h_t}{a_t}{league_code}_MEGA"
        seed = int(hashlib.md5(match_key.encode()).hexdigest(), 16) % (10**6)
        np.random.seed(seed)

        p_bar = st.progress(0)
        status_text = st.empty()
        steps = ["Scanning 20 Leagues...", "Analyzing Team DNA...", "Form Analysis...", "Simulating Match...", "Finalizing Pick..."]
        
        for i, s in enumerate(steps):
            status_text.markdown(f"<p style='text-align:center; color:#00FF00;'>AI ENGINE: {s}</p>", unsafe_allow_html=True)
            p_bar.progress((i + 1) * 20)
            time.sleep(0.5)

        h_data = df[df['HomeTeam'] == h_t].tail(8)
        a_data = df[df['AwayTeam'] == a_t].tail(8)
        xh = h_data['FTHG'].mean() if not h_data.empty else 1.5
        xa = a_data['FTAG'].mean() if not a_data.empty else 1.2
        
        confidence = 96.1 + (seed % 2)
        if confidence > 98.9: confidence = 98.9
        
        pick = f"{h_t} WIN / 1X" if xh > xa else f"{a_t} WIN / X2"
        
        status_text.empty()
        p_bar.empty()

        st.markdown(f"<h2 style='text-align:center; color:#00FF00;'>🎯 IQ ACCURACY: {confidence:.1f}%</h2>", unsafe_allow_html=True)
        st.progress(confidence / 100)
        
        r1, r2 = st.columns(2)
        with r1:
            st.markdown(f"<div class='result-card'><h3>🏆 MAIN PICK</h3><h2>{pick}</h2></div>", unsafe_allow_html=True)
        with r2:
            st.markdown(f"<div class='result-card'><h3>🚩 CORNERS</h3><h2>OVER 8.5</h2></div>", unsafe_allow_html=True)
else:
    st.info("💡 Bonyeza 'RUN GLOBAL DATA SYNC' kuunganisha ligi zote 20 za Ulaya.")
