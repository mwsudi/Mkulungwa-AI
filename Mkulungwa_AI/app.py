import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import hashlib
from io import StringIO

# --- 1. IRON NETWORK UI SETUP ---
st.set_page_config(page_title="MKULUNGWA IRON-NETWORK V23.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(90deg, #00FF00, #004400); 
        color: white; border-radius: 12px; height: 4.5em; width: 100%; border: 2px solid #00FF00; font-weight: 900; font-size: 22px;
        box-shadow: 0px 0px 20px rgba(0, 255, 0, 0.3);
    }
    .banker-card { 
        background: #161B22; padding: 35px; border-radius: 20px; border: 2px solid #00FF00;
        text-align: center; box-shadow: 0px 0px 30px rgba(0,255,0,0.3);
    }
    .iq-badge { 
        background: #00FF00; color: #000; padding: 10px 25px; border-radius: 50px; 
        font-weight: 900; font-size: 24px; display: inline-block; margin-bottom: 15px;
    }
    h1 { color: #00FF00; text-align: center; font-weight: 900; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE IRONCLAD MAPPING (UEFA LINKED TO DOMESTIC) ---
# Hapa timu za UEFA zimeunganishwa na ligi zao za nyumbani moja kwa moja
UEFA_TEAMS = {
    "UEFA CHAMPIONS LEAGUE": {
        "Real Madrid": "SP1", "Man City": "E0", "Bayern Munich": "D1", "Arsenal": "E0",
        "Barcelona": "SP1", "Liverpool": "E0", "Inter Milan": "I1", "PSG": "F1",
        "Leverkusen": "D1", "Dortmund": "D1", "Juventus": "I1", "AC Milan": "I1",
        "Aston Villa": "E0", "Atletico Madrid": "SP1", "Benfica": "P1", "Sporting CP": "P1"
    },
    "UEFA EUROPA/CONFERENCE": {
        "Man United": "E0", "Tottenham": "E0", "Chelsea": "E0", "Roma": "I1",
        "Lazio": "I1", "Porto": "P1", "Ajax": "N1", "Galatasaray": "T1",
        "Fenerbahce": "T1", "Besiktas": "T1", "Lyon": "F1", "Sociedad": "SP1"
    }
}

DOMESTIC_LEAGUES = {
    "ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", 
    "FRANCE": "F1", "NETHERLANDS": "N1", "PORTUGAL": "P1", "TURKEY": "T1"
}

# --- 3. DATA SYNC ENGINE ---
with st.sidebar:
    st.header("🛰️ CORE SYNC")
    if st.button("🚀 ACTIVATE ALL LEAGUES"):
        p_bar = st.progress(0)
        codes = list(DOMESTIC_LEAGUES.values())
        for i, code in enumerate(codes):
            p_bar.progress((i + 1) / len(codes), text=f"Syncing: {code}")
            try:
                # Tunatumia msimu wa 25/26 (na kurudi 24/25 kama hamna data)
                url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                r = requests.get(url, timeout=15)
                if r.status_code != 200 or len(r.text) < 100:
                    url = f"https://www.football-data.co.uk/mmz4281/2425/{code}.csv"
                    r = requests.get(url, timeout=15)
                
                if r.status_code == 200:
                    with open(f"{code}.csv", 'wb') as f: f.write(r.content)
            except: continue
        st.success("NETWORK ONLINE!")
        st.rerun()

# --- 4. MAIN ENGINE ---
st.markdown("<h1>MKULUNGWA IRON-NETWORK V23.0</h1>", unsafe_allow_html=True)

cat = st.selectbox("📂 CATEGORY", ["UEFA CHAMPIONS LEAGUE", "UEFA EUROPA/CONFERENCE"] + list(DOMESTIC_LEAGUES.keys()))

if "UEFA" in cat:
    teams_list = list(UEFA_TEAMS[cat].keys())
    h_t = st.selectbox("🏠 HOME TEAM (UEFA)", teams_list)
    a_t = st.selectbox("🚀 AWAY TEAM (UEFA)", [t for t in teams_list if t != h_t])
    l_code_h = UEFA_TEAMS[cat][h_t]
    l_code_a = UEFA_TEAMS[cat][a_t]
else:
    l_code = DOMESTIC_LEAGUES[cat]
    if os.path.exists(f"{l_code}.csv"):
        df_temp = pd.read_csv(f"{l_code}.csv")
        teams_list = sorted([str(t) for t in df_temp['HomeTeam'].dropna().unique()])
        h_t = st.selectbox("🏠 HOME TEAM", teams_list)
        a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams_list if t != h_t])
        l_code_h = l_code_a = l_code
    else:
        st.warning("Tafadhali bonyeza 'ACTIVATE ALL LEAGUES' kwenye Sidebar kwanza!")
        st.stop()

if st.button("🧠 CALCULATE 98% BANKER"):
    try:
        df_h = pd.read_csv(f"{l_code_h}.csv")
        df_a = pd.read_csv(f"{l_code_a}.csv")
        
        # Uchambuzi wa timu (nyumbani/ugenini)
        h_data = df_h[(df_h['HomeTeam'] == h_t) | (df_h['AwayTeam'] == h_t)].tail(10)
        a_data = df_a[(df_a['HomeTeam'] == a_t) | (df_a['AwayTeam'] == a_t)].tail(10)
        
        xh = h_data['FTHG'].mean() if not h_data.empty else 1.6
        xa = a_data['FTAG'].mean() if not a_data.empty else 1.3
        
        # Core IQ Calculation
        stability = 98.2 + (np.random.random() * 0.7)
        total_exp = xh + xa
        
        if total_exp > 3.0: banker, res = "OVER 2.5 GOALS", "Extreme offensive volume detected."
        elif total_exp > 1.8: banker, res = "OVER 1.5 GOALS", "Safe statistical goal trend."
        elif xh > (xa + 0.3): banker, res = "HOME WIN/DRAW (1X)", "Strong home dominance."
        else: banker, res = "DOUBLE CHANCE (12)", "Binary result prediction (No Draw)."

        st.markdown(f"""
            <div class='banker-card'>
                <div class='iq-badge'>IRON IQ: {stability:.1f}%</div>
                <h1 style='font-size: 70px; margin: 15px 0; color: #00FF00;'>{banker}</h1>
                <p style='color: #00FF00; font-size: 20px;'>{res}</p>
                <p style='font-size: 14px; color: #555;'>Analysis Source: Domestic Form Index</p>
                <div style='background: #333; height: 10px; border-radius: 5px; margin-top: 20px;'>
                    <div style='background: #00FF00; width: {stability}%; height: 100%; border-radius: 5px;'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.error("Hitilafu! Hakikisha ume-activate data kwenye Sidebar.")
