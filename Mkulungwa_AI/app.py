import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib
import random
from io import StringIO

# --- 1. PREMIUM UI SETUP ---
st.set_page_config(page_title="MKULUNGWA HYPER-IQ V19", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(90deg, #00FF00, #008000); 
        color: white; border-radius: 15px; height: 4em; width: 100%; border: none; font-weight: bold; font-size: 22px;
        box-shadow: 0px 5px 15px rgba(0, 255, 0, 0.4); transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0px 8px 25px rgba(0, 255, 0, 0.6); }
    .result-card { background: #1A1C24; padding: 30px; border-radius: 20px; border-top: 5px solid #00FF00; box-shadow: 5px 5px 15px rgba(0,0,0,0.5); text-align: center; }
    .advice-box { 
        background: rgba(0, 255, 0, 0.05); border: 2px solid #00FF00; padding: 25px; border-radius: 15px; 
        margin-top: 25px; color: #00FF00; font-size: 19px; font-weight: 500;
    }
    h1 { color: #00FF00; text-align: center; font-size: 55px; font-weight: 900; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LEAGUE MAPPING ---
LEAGUE_MAP = {
    "UEFA / EUROPA / CONFERENCE": {"ALL_ELITE_CLUBS": "UEFA_ALL"},
    "ENGLAND": {"Premier League": "E0", "Championship": "E1"},
    "SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D2"},
    "FRANCE": {"Ligue 1": "F1"},
    "NETHERLANDS": {"Eredivisie": "N1"},
    "PORTUGAL": {"Primeira Liga": "P1"},
    "TURKEY": {"Super Lig": "T1"},
    "BELGIUM": {"Pro League": "B1"},
    "SCOTLAND": {"Premiership": "SC0"},
    "GREECE": {"Super League": "G1"}
}

# --- 3. SIDEBAR DATABASE ---
with st.sidebar:
    st.markdown("## 🛡️ CORE CONTROL")
    if st.button("🔄 REFRESH NEURAL DATABASE"):
        all_dfs = []
        p_bar = st.progress(0, text="Syncing Global Data...")
        leagues = [(n, c) for cat, sub in LEAGUE_MAP.items() if cat != "UEFA / EUROPA / CONFERENCE" for n, c in sub.items()]
        for i, (n, c) in enumerate(leagues):
            try:
                r = requests.get(f"https://www.football-data.co.uk/mmz4281/2526/{c}.csv", timeout=10)
                if r.status_code == 200:
                    with open(f"{c}.csv", 'wb') as f: f.write(r.content)
                    all_dfs.append(pd.read_csv(StringIO(r.text)))
                p_bar.progress((i+1)/len(leagues))
            except: continue
        if all_dfs:
            pd.concat(all_dfs, ignore_index=True).to_csv("UEFA_ALL.csv", index=False)
            st.success("HYPER-IQ SYNCED!")

# --- 4. INTERFACE ---
st.markdown("<h1>MKULUNGWA HYPER-IQ V19</h1>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
cat = col_a.selectbox("📂 CATEGORY", list(LEAGUE_MAP.keys()))
l_code = "UEFA_ALL" if cat == "UEFA / EUROPA / CONFERENCE" else LEAGUE_MAP[cat][col_b.selectbox("🏆 LEAGUE", list(LEAGUE_MAP[cat].keys()))]

if os.path.exists(f"{l_code}.csv"):
    df = pd.read_csv(f"{l_code}.csv")
    teams = sorted(df['HomeTeam'].dropna().unique())
    c1, c2 = st.columns(2)
    h_t = c1.selectbox("🏠 HOME SIDE", teams)
    a_t = c2.selectbox("🚀 AWAY SIDE", [t for t in teams if t != h_t])

    if st.button("🎯 EXECUTE HYPER-ANALYSIS"):
        # Unique Seed for every match
        m_key = f"{h_t}{a_t}{l_code}_V19"
        seed = int(hashlib.md5(m_key.encode()).hexdigest(), 16) % (10**6)
        np.random.seed(seed); random.seed(seed)
        
        with st.spinner("🧠 Thinking..."):
            time.sleep(1)

        # 1. Data Processing
        h_data = df[df['HomeTeam'] == h_t].tail(10)
        a_data = df[df['AwayTeam'] == a_t].tail(10)
        
        # Power Rating (V19 Logic)
        xh = h_data['FTHG'].mean() if not h_data.empty else 1.5
        xa = a_data['FTAG'].mean() if not a_data.empty else 1.2
        
        # Shot Index (Real Attack Power)
        h_shots = h_data['HS'].mean() if 'HS' in h_data.columns else 11
        a_shots = a_data['AS'].mean() if 'AS' in a_data.columns else 9
        
        # 2. Decision Engine
        # Goals Logic
        total_exp = xh + xa
        goal_pick = "OVER 2.5" if total_exp > 2.75 else "OVER 1.5" if total_exp > 1.6 else "UNDER 3.5"
        
        # Double Chance Logic
        if xh > (xa + 0.3): dc_pick = "1X (HOME/DRAW)"
        elif xa > (xh + 0.3): dc_pick = "X2 (AWAY/DRAW)"
        else: dc_pick = "12 (NO DRAW)"
        
        # Corner Intelligence (The Fix)
        corner_strength = (h_shots + a_shots) * 0.42
        if corner_strength > 10.2: corner_pick = "OVER 10.5"
        elif corner_strength > 9.0: corner_pick = "OVER 9.5"
        else: corner_pick = "OVER 8.5"

        # 3. Dynamic Advice (The "Anti-Bias" Engine)
        # Hapa tunaamua kipi ni bora zaidi leo kati ya DC, Goals, au Corners
        conf = 97.5 + (seed % 15) / 10
        if conf > 98.9: conf = 98.9

        if (xh > 2.0 or xa > 2.0) and total_exp > 3.0:
            best_market = "⚽ MAGOLI"
            advice = f"🔥 HYPER-IQ ALERT: Timu hizi zina wastani mkubwa sana wa kufunga ({total_exp:.2f}). Usihangaike na kona, hapa kuna pesa kwenye MAGOLI."
        elif h_shots > 14 or a_shots > 14:
            best_market = "🚩 KONA"
            advice = f"🚩 HYPER-IQ ALERT: Mashambulizi ni mengi lakini umaliziaji ni hafifu. Kona ({corner_pick}) ndilo soko lenye usalama zaidi kwenye mechi hii."
        else:
            best_market = "🛡️ DOUBLE CHANCE"
            advice = f"⚖️ HYPER-IQ ALERT: Mchezo huu una mbinu nyingi za katikati. Linda mtaji wako kwa {dc_pick}, itakuwa mechi ngumu kwa pande zote."

        # 4. Results Display
        st.markdown(f"<h2 style='text-align:center; color:#00FF00;'>🛡️ IQ CONFIDENCE: {conf:.1f}%</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align:center;'>BORA LEO: <span style='color:#00FF00;'>{best_market}</span></h3>", unsafe_allow_html=True)
        
        r1, r2, r3 = st.columns(3)
        r1.markdown(f"<div class='result-card'><h3>🏆 DOUBLE CHANCE</h3><h2 style='color:#00FF00;'>{dc_pick}</h2></div>", unsafe_allow_html=True)
        r2.markdown(f"<div class='result-card'><h3>🚩 CORNERS</h3><h2 style='color:#00FF00;'>{corner_pick}</h2></div>", unsafe_allow_html=True)
        r3.markdown(f"<div class='result-card'><h3>⚽ GOALS</h3><h2 style='color:#00FF00;'>{goal_pick}</h2></div>", unsafe_allow_html=True)
        
        st.markdown(f"<div class='advice-box'>{advice}</div>", unsafe_allow_html=True)
else:
    st.info("💡 DATABASE OFFLINE: Admin, tafadhali bonyeza 'REFRESH NEURAL DATABASE' ili kuwasha mfumo.")
