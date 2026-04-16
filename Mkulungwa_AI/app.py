import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import random
from io import StringIO

# --- 1. UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V28.0 - UKRAINIAN RESCUE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(135deg, #00FF00, #004400); 
        color: white; border-radius: 12px; height: 3.5em; width: 100%; border: 1px solid #00FF00; font-weight: 900;
    }
    .metric-card { 
        background: #1A1C24; padding: 25px; border-radius: 15px; border-top: 5px solid #00FF00;
        text-align: center; box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
    }
    .advice-section { 
        background: rgba(0, 255, 0, 0.05); border: 1px solid #00FF00; padding: 20px; 
        border-radius: 15px; margin-top: 25px;
    }
    .advice-text { color: #00FF00; font-size: 17px; margin-bottom: 10px; border-left: 4px solid #00FF00; padding-left: 10px; }
    h1 { color: #00FF00; text-align: center; font-weight: 900; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBAL LEAGUE MAPPING ---
LEAGUE_MAP = {
    "ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", "FRANCE": "F1", 
    "NETHERLANDS": "N1", "PORTUGAL": "P1", "BELGIUM": "B1", "SCOTLAND": "SC0", 
    "TURKEY": "T1", "UKRAINE": "U1", "GREECE": "G1",
    "UEFA LITE (CL/EL/ECL)": "UEFA_ALL"
}

# --- 3. ADVANCED SYNC ENGINE (WITH DATA CLEANING) ---
with st.sidebar:
    st.header("🛰️ GLOBAL SATELLITE")
    if st.button("🔄 REFRESH ALL LEAGUES"):
        all_dfs = []
        with st.spinner("Locking on all Nations..."):
            for name, code in LEAGUE_MAP.items():
                if code == "UEFA_ALL": continue
                
                # Mbinu ya kuvuta data (Msimu mpya au uliopita)
                for season in ["2526", "2425"]:
                    try:
                        url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
                        r = requests.get(url, timeout=10)
                        if r.status_code == 200:
                            # Hifadhi file la nchi
                            with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                            
                            # Safisha data kabla ya kuziweka kwenye UEFA LITE
                            temp_df = pd.read_csv(StringIO(r.text))
                            if not temp_df.empty:
                                # Tunachukua tu safu (columns) muhimu ili Ukraine na Greece zisi-gome kuungana
                                essential_cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HC', 'AC']
                                # Hakikisha safu hizi zipo kwenye file lililopakuliwa
                                available_cols = [c for c in essential_cols if c in temp_df.columns]
                                clean_df = temp_df[available_cols].copy()
                                all_dfs.append(clean_df)
                                break 
                    except: continue
            
            # UNGANISHA ZOTE (UKRAINE RESCUE MISSION)
            if all_dfs:
                master_df = pd.concat(all_dfs, ignore_index=True, sort=False)
                master_df.to_csv("UEFA_ALL.csv", index=False)
                st.success(f"SUCCESS! {len(master_df)} MATCHES SYNCED.")
                st.info("Ukraine na Greece sasa zimeingizwa kitalamu kwenye UEFA LITE.")
            else:
                st.error("Data imegoma! Angalia internet yako.")

# --- 4. MAIN ENGINE ---
st.markdown("<h1>MKULUNGWA AI V28.0</h1>", unsafe_allow_html=True)

nation = st.selectbox("🌍 SELECT LEAGUE", list(LEAGUE_MAP.keys()))
l_code = LEAGUE_MAP[nation]

if os.path.exists(f"{l_code}.csv"):
    df = pd.read_csv(f"{l_code}.csv")
    # Kusafisha majina ya timu
    teams = sorted([str(t) for t in df['HomeTeam'].dropna().unique() if str(t).strip() != ""])
    h_t = st.selectbox("🏠 HOME TEAM", teams)
    a
