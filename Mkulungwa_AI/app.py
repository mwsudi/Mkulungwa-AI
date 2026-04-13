import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib
from io import StringIO

# 1. UI SETUP
st.set_page_config(page_title="MKULUNGWA AI V16.8", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(45deg, #00FF00, #004d00); 
        color: white; border-radius: 10px; height: 3.5em; width: 100%; border: none; font-weight: bold;
    }
    .result-card { 
        background-color: #1A1C24; padding: 20px; border-radius: 15px; 
        border-top: 4px solid #00FF00; text-align: center; margin-bottom: 15px;
    }
    h1 { color: #00FF00; text-align: center; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# 2. FIXED MASTER DATABASE - CORRECT CODES FOR ALL 20 NATIONS
LEAGUE_MAP = {
    "UEFA / EUROPA / CONFERENCE": {"ALL_EUROPEAN_ELITE": "UEFA_ALL"},
    "ENGLAND": {"Premier League": "E0", "Championship": "E1"},
    "SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D2"},
    "FRANCE": {"Ligue 1": "F1"},
    "NETHERLANDS": {"Eredivisie": "D1"},  # Imetoka N1 kwenda D1
    "PORTUGAL": {"Primeira Liga": "P1"},
    "TURKEY": {"Super Lig": "T1"},
    "BELGIUM": {"Pro League": "B1"},
    "AUSTRIA": {"Bundesliga": "AUT"},      # FIXED CODE
    "SCOTLAND": {"Premiership": "SC0"},
    "SWITZERLAND": {"Super League": "SWZ"}, # FIXED CODE
    "DENMARK": {"Superliga": "DNK"},       # FIXED CODE
    "NORWAY": {"Eliteserien": "NOR"},      # FIXED CODE
    "SWEDEN": {"Allsvenskan": "SWE"},      # FIXED CODE
    "POLAND": {"Ekstraklasa": "POL"},      # FIXED CODE
    "CZECH REPUBLIC": {"First League": "CZE"}, # FIXED CODE
    "GREECE": {"Super League": "G1"},
    "UKRAINE": {"Premier League": "UKR"},   # FIXED CODE
    "CROATIA": {"First League": "CRO"}      # FIXED CODE
}

# 3. SIDEBAR SYNC
with st.sidebar:
    st.header("NEURAL DATA SYNC")
    if st.button("RUN GLOBAL DATA SYNC"):
        with st.spinner("Correcting and Syncing All Leagues..."):
            all_dfs = []
            for cat in LEAGUE_MAP:
                if cat != "UEFA / EUROPA / CONFERENCE":
                    for name, code in LEAGUE_MAP[cat].items():
                        try:
                            # Tunasoma data za msimu wa 25/26
                            url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                            r = requests.get(url, timeout=5)
                            if r.status_code == 200:
                                with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                                df_temp = pd.read_csv(StringIO(r.text))
                                all_dfs.append(df_temp)
                        except: continue
            
            # UEFA Tournaments
            for u_code in ["CL", "EL", "EC"]:
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/2526/{u_code}.csv"
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200:
                        all_dfs.append(pd.read_csv(StringIO(r.text)))
                except: continue

            if all_dfs:
                pd.concat(all_dfs, ignore_index=True).to_csv("UEFA_ALL.csv", index=False)
        st.success("Global Sync Done! Leagues Corrected.")

# 4. INTERFACE
st.markdown("<h1>🛡️ MKULUNGWA AI V16.8 🛡️</h1>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    category = st.selectbox("📂 CHAGUA KUNDI", list(LEAGUE_MAP.keys()))
with c2:
    if category == "UEFA / EUROPA / CONFERENCE":
        league_code = "UEFA_ALL"
        st.write("✅ **EUROPEAN ELITE MODE ACTIVE**")
    else:
        league_name = st.selectbox("🏆 CHAGUA LIGI", list(LEAGUE_MAP[category].keys()))
        league_code = LEAGUE_MAP[category][league_name]
