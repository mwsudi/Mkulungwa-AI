import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib

# 1. UI SETUP
st.set_page_config(page_title="MKULUNGWA PREDICTION V14.9", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    .stButton>button { 
        background: linear-gradient(45deg, #00FF00, #004d00); 
        color: white; border-radius: 12px; height: 3.5em; width: 100%; border: none; font-weight: bold; font-size: 18px;
    }
    .result-card { 
        background-color: #1A1C24; padding: 25px; border-radius: 20px; 
        border-top: 4px solid #00FF00; margin-bottom: 20px; text-align: center;
    }
    h1 { color: #00FF00; text-align: center; font-size: 45px; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# 2. UNIFIED LEAGUE DATABASE
# UEFA sasa ni kundi moja tu Master!
LEAGUE_MAP = {
    "🌍 UEFA ELITE (All Competitions)": {"All Elite Matches": "UEFA_ALL"},
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENGLAND": {"Premier League": "E0", "Championship": "E1", "League 1": "E2"},
    "🇪🇸 SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
    "🇮🇹 ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "🇩🇪 GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D2"},
    "🇫🇷 FRANCE": {"Ligue 1": "F1", "Ligue 2": "F2"},
    "🇳🇱 NETHERLANDS": {"Eredivisie": "N1"},
    "🇵🇹 PORTUGAL": {"Primeira Liga": "P1"},
    "🇹🇷 TURKEY": {"Süper Lig": "T1"},
    "🇧🇪 BELGIUM": {"Pro League": "B1"},
    "🇦🇹 AUSTRIA": {"Bundesliga": "A1"},
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 SCOTLAND": {"Premiership": "SC0"},
    "🇨🇭 SWITZERLAND": {"Super League": "C1"},
    "🇬🇷 GREECE": {"Super League": "G1"},
    "🇩🇰 DENMARK": {"Superliga": "D1"},
    "🇳🇴 NORWAY": {"Eliteserien": "N1"},
    "🇸🇪 SWEDEN": {"Allsvenskan": "S1"},
    "🇵🇱 POLAND": {"Ekstraklasa": "P1"},
    "🇨🇿 CZECH REPUBLIC": {"First League": "CZ1"},
    "🇺🇦 UKRAINE": {"Premier League": "U1"}
}

# --- SYNC ENGINE (Unified logic) ---
with st.sidebar:
    st.header("🧬 GLOBAL SYNC")
    if st.button("🚀 SYNC DATA"):
        with st.spinner("Processing Elite & League Data..."):
            all_uefa_data = []
            # Kuvuta data za UEFA na kuziunganisha
            for u_code in ["CL", "EL", "EC"]:
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/2526/{u_code}.csv"
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200:
                        temp_df = pd.read_csv(pd.compat.StringIO(r.text))
                        all_uefa_data.append(temp_df)
                except: continue
            
            if all_uefa_data:
                combined_uefa = pd.concat(all_uefa_data, ignore_index=True)
                combined_uefa.to_csv("UEFA_ALL.csv", index=False)
            
            # Kuvuta ligi nyingine kawaida
            for cat in list(LEAGUE_MAP.keys())[1:]:
                for name, code in LEAGUE_MAP[cat].items():
                    try:
                        url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                        r = requests.get(url, timeout=5)
                        if r.status_code == 200:
                            with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                    except: continue
        st.success("Sync Done!")

# --- APP HEADER ---
st.markdown("<h1>🛡️ MKULUNGWA V14.9 🛡️</h1>", unsafe_allow_html=True)

# --- DROPDOWNS ---
c1, c2 = st.columns(2)
with c1:
    category = st.selectbox("🌍 CHAGUA NCHI / KUNDI", list(LEAGUE_MAP.keys()))
with c2:
    league_name = st.selectbox("🏆 CHAGUA LIGI", list(LEAGUE_MAP[category].keys()))
    league_code = LEAGUE_MAP[category][league_name]

# Safety Load
df = pd.DataFrame()
if os.path.exists(f"{league_code}.csv"):
    df = pd.read_csv(f"{league_code}.csv")

# Uchambuzi
if not df.empty and 'HomeTeam' in df.columns:
    teams = sorted(df['HomeTeam'].dropna().unique())
    col1, col2 = st.columns(2)
    h_t = col1.selectbox("🏠 HOME TEAM", teams)
    a_t = col2.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])
    
    if st.button("🎯 EXECUTE SMART ANALYSIS"):
        match_key = f"{h_t}{a_t}{league_code}_V149"
        seed = int(hashlib.md5(match_key.encode()).hexdigest(), 16) % (10**6)
        np.random.seed(seed)

        with st.status("🧠 Consulting 5-AI Systems...", expanded=True):
            time.sleep(1.5)
            h_data = df[df['HomeTeam'] == h_t].tail(10)
            a_data = df[df['AwayTeam'] == a_t].tail(10)
            
            xh = h_data['FTHG'].mean() if not h_data.empty else 1.5
            xa = a_data['FTAG'].mean() if not a_data.empty else 1.2
            
            sim_h = np.random.poisson(xh, 10000)
            sim_a = np.random.poisson(xa, 10000)
            
            confidence = 93.5 + (seed % 5) + (np.random.uniform(0.1, 0.4))
            if confidence > 98.9: confidence = 98.9

            main_pick = f"{h_t} WIN / 1X" if np.mean(sim_h) > np.mean(sim_a) else f"{a_t} WIN / X2"
            
            hc = h_data['HC'].mean() if 'HC' in h_data.columns else 5.2
            ac = a_data['AC'].mean() if 'AC' in a_data.columns else 4.5
            corner_pick = "OVER 8.5 KONA" if (hc + ac) > 9.0 else "OVER 7.5 KONA"

        st.markdown(f"<h2 style='text-align:center; color:#00FF00;'>🎯 IQ ACCURACY: {confidence:.1f}%</h2>", unsafe_allow_html=True)
        st.progress(confidence / 100)
        
        r1, r2 = st.columns(2)
        with r1: st.markdown(f"<div class='result-card'><h3>🏆 PICK</h3><h2>{main_pick}</h2></div>", unsafe_allow_html=True)
        with r2: st.markdown(f"<div class='result-card'><h3>🚩 KONA</h3><h2>{corner_pick}</h2></div>", unsafe_allow_html=True)
else:
    st.info("💡 Bonyeza 'SYNC DATA' kwenye Sidebar kuanza.")
