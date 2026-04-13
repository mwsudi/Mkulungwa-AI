import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
from scipy.stats import poisson

# 1. THEME & APP CONFIGURATION (MODERN LOOK)
st.set_page_config(page_title="MKULUNGWA AI V13", layout="wide")

# Custom CSS kwa ajili ya muonekano wa kuvutia (Neon Design)
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stButton>button { 
        background-image: linear-gradient(to right, #00FF00 , #008000); 
        color: white; border-radius: 20px; border: none; font-weight: bold; width: 100%;
    }
    .stMetric { background-color: #1A1C24; padding: 15px; border-radius: 15px; border: 1px solid #00FF00; }
    .report-card { border: 2px solid #00FF00; padding: 20px; border-radius: 20px; background: #000; }
    </style>
    """, unsafe_allow_html=True)

DATA_URLS = {
    "England (Premier League)": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "Spain (La Liga)": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    "Germany (Bundesliga)": "https://www.football-data.co.uk/mmz4281/2526/D1.csv",
    "Italy (Serie A)": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "France (Ligue 1)": "https://www.football-data.co.uk/mmz4281/2526/F1.csv",
    "Netherlands (Eredivisie)": "https://www.football-data.co.uk/mmz4281/2526/N1.csv",
    "Belgium (Pro League)": "https://www.football-data.co.uk/mmz4281/2526/B1.csv",
    "Portugal (Primeira Liga)": "https://www.football-data.co.uk/mmz4281/2526/P1.csv",
    "Turkey (Super Lig)": "https://www.football-data.co.uk/mmz4281/2526/T1.csv",
    "Scotland (Premiership)": "https://www.football-data.co.uk/mmz4281/2526/SC0.csv",
    "UEFA Champions/Europa/Conf": "GLOBAL_EUROPE"
}

# --- SIDEBAR: NEURAL SYNC ENGINE ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/64/artificial-intelligence.png")
    st.markdown("### 🧠 PREDATOR NEURAL LINK")
    if st.button("🚀 SYNC GLOBAL DATABASE"):
        with st.status("Initializing Neural Sync...", expanded=True) as status:
            p_bar = st.progress(0)
            for i, (name, url) in enumerate(DATA_URLS.items()):
                st.write(f"🔄 Injecting IQ into: {name}...")
                if url.startswith("http"):
                    try:
                        r = requests.get(url, timeout=7)
                        with open(url.split('/')[-1], 'wb') as f: f.write(r.content)
                    except: pass
                p_bar.progress((i + 1) / len(DATA_URLS))
            status.update(label="✅ SYSTEM CALIBRATED!", state="complete", expanded=False)

# --- HEADER SECTION ---
st.markdown("<h1 style='text-align: center; color: #00FF00;'>🛡️ MKULUNGWA AI: THE FINAL PREDATOR V13 🛡️</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Kelly Criterion | EV+ Radar | Corner Flex IQ | Monte Carlo V3</p>", unsafe_allow_html=True)

# --- SELECTION & INPUTS ---
nchi = st.selectbox("🌍 CHAGUA MASHINDANO", list(DATA_URLS.keys()))

df_final = pd.DataFrame()
fname = DATA_URLS[nchi].split('/')[-1]
if os.path.exists(fname): 
    df_final = pd.read_csv(fname)

if not df_final.empty:
    teams = sorted(df_final['HomeTeam'].unique())
    col_t1, col_t2 = st.columns(2)
    h_t = col_t1.selectbox("🏠 HOME TEAM", teams)
    a_t = col_t2.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

    # Sehemu ya Odds za kampuni kwa ajili ya EV+ Radar
    st.markdown("---")
    st.write("📊 **BOOKIE ODDS (Betpawa / Sportbet)**")
    o_col1, o_col2 = st.columns(2)
    b_h_odds = o_col1.number_input(f"Odds za {h_t}", value=2.00, step=0.01)
    b_a_odds = o_col2.number_input(f"Odds za {a_t}", value=2.00, step=0.01)

    if st.button("RUN DEEP PREDATOR COMPUTATION"):
        # 1. IQ LAYER: DATA PREPROCESSING
        h_p = df_final[df_final['HomeTeam'] == h_t].tail(10)
        a_p = df_final[df_final['AwayTeam'] == a_t].tail(10)
        
        # 2. IQ LAYER: MONTE CARLO PROBABILITY
        avg_h, avg_a = df_final['FTHG'].mean(), df_final['FTAG'].mean()
        xh = (h_p['FTHG'].mean() / avg_h) * (a_p['FTHG'].mean() / avg_h) * avg_h
        xa = (a_p['FTAG'].mean() / avg_a) * (h_p['FTAG'].mean() / avg_a) * avg_a
        sh, sa = np.random.poisson(xh, 10000), np.random.poisson(xa, 10000)
        ph, pa = (np.sum(sh > sa)/100), (np.sum(sa > sh)/100)
        
        # 3. IQ LAYER: EV+ RADAR (The Bookie Killer)
        true_odds_h = 100 / ph if ph > 0 else 100
        ev_h = (b_h_odds * (ph/100)) - (1 - (ph/100))
        
        # 4. IQ LAYER: KELLY CRITERION (Money Management)
        # Formula: K% = (bp - q) / b
        b = b_h_odds - 1
        kelly_h = ((b * (ph/100)) - (1 - (ph/100))) / b if b > 0 else 0
        
        # 5. IQ LAYER: DYNAMIC CORNER FLEX (6.5 vs 7.5)
        hc_avg = h_p['HC'].mean() if 'HC' in h_p.columns else 4.5
        ac_avg = a_p['AC'].mean() if 'AC' in a_p.columns else 4.0
        total_corners = hc_avg + ac_avg
        c_market = "KONA 7.5 OVER" if total_corners > 8.8 else "KONA 6.5 OVER"
        c_conf = min(total_corners * 10, 98.2)

        # --- THE MASTER DASHBOARD ---
        st.markdown(f"### 🎯 Battle Analysis: {h_t} vs {a_t}")
        r1, r2, r3, r4 = st.columns(4
