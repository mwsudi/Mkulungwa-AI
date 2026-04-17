import streamlit as st
import pandas as pd
import os
import requests
from io import StringIO

# --- 1. UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V30.0 - SIGNAL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(135deg, #00FF00, #004400); 
        color: white; border-radius: 12px; height: 3.5em; width: 100%; border: 1px solid #00FF00; font-weight: 900;
    }
    .signal-banker { background: #00FF00; color: black; padding: 10px; border-radius: 10px; font-weight: bold; text-align: center; }
    .signal-safe { background: #FFFF00; color: black; padding: 10px; border-radius: 10px; font-weight: bold; text-align: center; }
    .signal-risk { background: #FF4B4B; color: white; padding: 10px; border-radius: 10px; font-weight: bold; text-align: center; }
    .metric-card { background: #1A1C24; padding: 25px; border-radius: 15px; border-top: 5px solid #00FF00; text-align: center; }
    h1 { color: #00FF00; text-align: center; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LEAGUE MAPPING ---
LEAGUE_MAP = {
    "ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", "FRANCE": "F1", 
    "NETHERLANDS": "N1", "PORTUGAL": "P1", "BELGIUM": "B1", "SCOTLAND": "SC0", 
    "TURKEY": "T1", "UKRAINE": "U1", "GREECE": "G1", "UEFA LITE": "UEFA_ALL"
}

# --- 3. SYNC ENGINE ---
with st.sidebar:
    st.header("🛰️ GLOBAL SATELLITE")
    if st.button("🔄 REFRESH ALL LEAGUES"):
        all_dfs = []
        for name, code in LEAGUE_MAP.items():
            if code == "UEFA_ALL": continue
            for season in ["2526", "2425"]:
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                        temp_df = pd.read_csv(StringIO(r.text))
                        if not temp_df.empty:
                            essential = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HC', 'AC']
                            all_dfs.append(temp_df[[c for c in essential if c in temp_df.columns]])
                            break
                except: continue
        if all_dfs:
            pd.concat(all_dfs, ignore_index=True, sort=False).to_csv("UEFA_ALL.csv", index=False)
            st.success("DATABASE UPDATED!")

# --- 4. ANALYZER ---
st.markdown("<h1>MKULUNGWA AI V30.0</h1>", unsafe_allow_html=True)
nation = st.selectbox("🌍 SELECT LEAGUE", list(LEAGUE_MAP.keys()))

if os.path.exists(f"{LEAGUE_MAP[nation]}.csv"):
    df = pd.read_csv(f"{LEAGUE_MAP[nation]}.csv")
    teams = sorted([str(t) for t in df['HomeTeam'].dropna().unique()])
    h_t = st.selectbox("🏠 HOME TEAM", teams)
    a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

    if st.button("🎯 RUN ANALYSIS"):
        h_f = df[df['HomeTeam'] == h_t].tail(8)
        a_f = df[df['AwayTeam'] == a_t].tail(8)
        
        # Calculations
        total_exp_g = ((h_f['FTHG'].mean() + a_f['FTHG'].mean())/2) + ((h_f['FTAG'].mean() + a_f['FTAG'].mean())/2)
        total_exp_c = h_f['HC'].mean() + a_f['AC'].mean() if 'HC' in h_f.columns else 9.0

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1: st.markdown(f"<div class='metric-card'><h3>⚽ GOALS</h3><h1>Exp: {total_exp_g:.2f}</h1></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><h3>🚩 CORNERS</h3><h1>Exp: {total_exp_c:.1f}</h1></div>", unsafe_allow_html=True)

        # --- SIGNAL LOGIC (KAMA UNAVYOTAKA MASTER) ---
        st.markdown("### 🚦 SIGNAL YA KONA (CORNER SIGNAL)")
        if total_exp_c >= 11.0:
            st.markdown(f"<div class='signal-banker'>🔥 BANKER: {total_exp_c:.1f} - BET: Over 8.5 au 7.5</div>", unsafe_allow_html=True)
        elif 9.0 <= total_exp_c < 11.0:
            st.markdown(f"<div class='signal-safe'>✅ SAFE: {total_exp_c:.1f} - BET: Over 7.5 au 6.5</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='signal-risk'>⚠️ RISK: {total_exp_c:.1f} - ACHANA NAYO!</div>", unsafe_allow_html=True)
else:
    st.info("Bonyeza Refresh Sidebar kuanza.")
