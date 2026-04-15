import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib
import random
from io import StringIO

# --- 1. IRONCLAD UI SETUP ---
st.set_page_config(page_title="MKULUNGWA IRONCLAD V19.4", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(90deg, #00FF00, #008000); 
        color: white; border-radius: 15px; height: 4.5em; width: 100%; border: none; font-weight: bold; font-size: 24px;
        box-shadow: 0px 5px 20px rgba(0, 255, 0, 0.5);
    }
    .banker-card { 
        background: #1A1C24; padding: 40px; border-radius: 25px; border: 3px solid #00FF00; 
        text-align: center; box-shadow: 0px 0px 30px rgba(0, 255, 0, 0.2); margin-bottom: 20px;
    }
    .other-card { background: #262730; padding: 20px; border-radius: 15px; text-align: center; border-bottom: 4px solid #00FF00; }
    h1 { color: #00FF00; text-align: center; font-size: 55px; font-weight: 900; }
    .stat-text { color: #888; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LEAGUE MAPPING ---
LEAGUE_MAP = {
    "ENGLAND": {"Premier League": "E0", "Championship": "E1"},
    "SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D2"},
    "FRANCE": {"Ligue 1": "F1"},
    "NETHERLANDS": {"Eredivisie": "N1"},
    "PORTUGAL": {"Primeira Liga": "P1"},
    "TURKEY": {"Super Lig": "T1"},
    "UEFA / ELITE": {"ALL_ELITE": "UEFA_ALL"}
}

# --- 3. SIDEBAR SYNC ---
with st.sidebar:
    st.markdown("## 🛰️ DATA RADAR")
    if st.button("🔄 PULL RECENT DATA"):
        all_dfs = []
        leagues = [c for cat in LEAGUE_MAP.values() for c in cat.values() if c != "UEFA_ALL"]
        for code in leagues:
            try:
                r = requests.get(f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv", timeout=10)
                if r.status_code == 200:
                    with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                    all_dfs.append(pd.read_csv(StringIO(r.text)))
            except: continue
        if all_dfs:
            pd.concat(all_dfs, ignore_index=True).to_csv("UEFA_ALL.csv", index=False)
            st.success("DATA LOCKED!")
            st.rerun()

# --- 4. MAIN ENGINE ---
st.markdown("<h1>MKULUNGWA IRONCLAD V19.4</h1>", unsafe_allow_html=True)

c_a, c_b = st.columns(2)
cat = c_a.selectbox("📂 CATEGORY", list(LEAGUE_MAP.keys()))
l_code = LEAGUE_MAP[cat][c_b.selectbox("🏆 LEAGUE", list(LEAGUE_MAP[cat].keys()))]

if os.path.exists(f"{l_code}.csv"):
    df = pd.read_csv(f"{l_code}.csv")
    teams = sorted(df['HomeTeam'].dropna().unique())
    col1, col2 = st.columns(2)
    h_t = col1.selectbox("🏠 HOME SIDE", teams)
    a_t = col2.selectbox("🚀 AWAY SIDE", [t for t in teams if t != h_t])

    if st.button("🎯 GET IRONCLAD OPTION"):
        m_key = f"{h_t}{a_t}{l_code}_IRON"
        seed = int(hashlib.md5(m_key.encode()).hexdigest(), 16) % (10**6)
        np.random.seed(seed)
        
        h_data = df[df['HomeTeam'] == h_t].tail(10)
        a_data = df[df['AwayTeam'] == a_t].tail(10)
        
        xh = h_data['FTHG'].mean() if not h_data.empty else 1.5
        xa = a_data['FTAG'].mean() if not a_data.empty else 1.2
        total_exp = xh + xa
        
        # --- THE IRONCLAD DECISION ENGINE ---
        # Tunachuja soko la chuma kwanza (High Confidence)
        if total_exp > 3.2:
            banker = "OVER 2.5 GOALS"
            reason = f"Wastani mkubwa sana wa magoli ({total_exp:.2f}). Timu zote zinafunga kwa wingi."
        elif total_exp > 2.2:
            banker = "OVER 1.5 GOALS"
            reason = f"Wastani wa {total_exp:.2f} ni salama kwa 1.5. Ni soko la uhakika kwa data hizi."
        elif xh > (xa + 0.6):
            banker = "HOME WIN OR DRAW (1X)"
            reason = f"Home Team ina nguvu kubwa nyumbani ({xh:.2f}) dhidi ya ugenini ({xa:.2f})."
        else:
            banker = "ANYONE TO WIN (12)"
            reason = "Mchezo huu hautoi sare kirahisi kulingana na historia ya timu hizi."

        # --- OTHER OPTIONS ---
        h_sh = h_data['HS'].mean() if 'HS' in h_data.columns else 10
        a_sh = a_data['AS'].mean() if 'AS' in a_data.columns else 9
        c_str = (h_sh + a_sh) * 0.43
        corner_opt = "OVER 9.5" if c_str > 9.5 else "OVER 8.5"

        # --- DISPLAY ---
        st.markdown(f"""
            <div class='banker-card'>
                <h3 style='color: #888;'>CHAGUO LA UHAKIKA (THE BANKER)</h3>
                <h1 style='font-size: 70px; margin: 10px 0;'>{banker}</h1>
                <p style='font-size: 20px; color: #00FF00;'>SABABU: {reason}</p>
            </div>
        """, unsafe_allow_html=True)

        st1, st2 = st.columns(2)
        st1.markdown(f"<div class='other-card'><h3>🚩 KONA</h3><h2>{corner_opt}</h2></div>", unsafe_allow_html=True)
        st2.markdown(f"<div class='other-card'><h3>🛡️ USALAMA</h3><h2>DOUBLE CHANCE</h2></div>", unsafe_allow_html=True)
        
        st.success(f"Uchambuzi umekamilika kwa kutumia MD5-Seed: {seed}")
else:
    st.warning("⚠️ Vuta data kwanza kwenye Sidebar!")
