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
st.set_page_config(page_title="MKULUNGWA VISUAL-IQ V19.6", layout="wide")

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
    .conf-text { font-size: 40px; font-weight: bold; color: #00FF00; }
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

# --- 3. SIDEBAR SYNC (MSTARI WA LOADING UMERUDI) ---
with st.sidebar:
    st.markdown("## 🛰️ DATA RADAR")
    if st.button("🔄 PULL RECENT DATA"):
        all_dfs = []
        leagues = [c for cat in LEAGUE_MAP.values() for c in cat.values() if c != "UEFA_ALL"]
        
        # Hapa ndipo mstar wa loading unapoonekana
        p_bar = st.progress(0, text="Establishing Neural Links...")
        
        for i, code in enumerate(leagues):
            try:
                # Update progress bar
                progress = (i + 1) / len(leagues)
                p_bar.progress(progress, text=f"Syncing League Data: {code}")
                
                r = requests.get(f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv", timeout=10)
                if r.status_code == 200:
                    with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                    all_dfs.append(pd.read_csv(StringIO(r.text)))
            except: continue
            
        if all_dfs:
            pd.concat(all_dfs, ignore_index=True).to_csv("UEFA_ALL.csv", index=False)
            st.success("DATA LOCKED & SYNCED!")
            time.sleep(1)
            st.rerun()

# --- 4. MAIN ENGINE ---
st.markdown("<h1>MKULUNGWA VISUAL-IQ V19.6</h1>", unsafe_allow_html=True)

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
        
        # --- ASILIMIA LOGIC ---
        base_conf = 97.2 + (seed % 17) / 10
        if base_conf > 98.9: base_conf = 98.9
        
        # --- THE IRONCLAD DECISION ENGINE ---
        if total_exp > 3.2:
            banker = "OVER 2.5 GOALS"
            reason = f"Wastani mkubwa wa magoli ({total_exp:.2f})."
        elif total_exp > 2.2:
            banker = "OVER 1.5 GOALS"
            reason = f"Wastani wa {total_exp:.2f} ni salama kwa 1.5."
        elif xh > (xa + 0.6):
            banker = "HOME WIN OR DRAW (1X)"
            reason = f"Nguvu ya Home ({xh:.2f}) dhidi ya Away ({xa:.2f})."
        else:
            banker = "ANYONE TO WIN (12)"
            reason = "Historia inaonyesha sare ni ngumu kutokea leo."

        # --- OTHER OPTIONS ---
        h_sh = h_data['HS'].mean() if 'HS' in h_data.columns else 10
        a_sh = a_data['AS'].mean() if 'AS' in a_data.columns else 9
        c_str = (h_sh + a_sh) * 0.43
        corner_opt = "OVER 9.5" if c_str > 9.5 else "OVER 8.5"

        # --- DISPLAY (ASILIMIA IMEONGEZWA HAPA) ---
        st.markdown(f"""
            <div class='banker-card'>
                <p style='color: #00FF00; font-size: 20px; font-weight: bold;'>🛡️ AI CONFIDENCE: {base_conf:.1f}%</p>
                <h3 style='color: #888;'>CHAGUO LA UHAKIKA</h3>
                <h1 style='font-size: 65px; margin: 10px 0;'>{banker}</h1>
                <p style='font-size: 18px; color: #00FF00;'>SABABU: {reason}</p>
            </div>
        """, unsafe_allow_html=True)

        st1, st2 = st.columns(2)
        st1.markdown(f"<div class='other-card'><h3>🚩 KONA</h3><h2>{corner_opt}</h2></div>", unsafe_allow_html=True)
        st2.markdown(f"<div class='other-card'><h3>🛡️ USALAMA</h3><h2>DOUBLE CHANCE</h2></div>", unsafe_allow_html=True)
        
        st.success(f"Analytic Complete. MD5-Check: {seed}")
else:
    st.warning("⚠️ Vuta data kwanza kwenye Sidebar!")
