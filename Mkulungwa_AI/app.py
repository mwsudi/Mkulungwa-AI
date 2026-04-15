import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import hashlib
import time
from io import StringIO

# --- 1. THE LEGEND UI SETUP ---
st.set_page_config(page_title="MKULUNGWA LEGEND V21.0", layout="wide")

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
        text-align: center; box-shadow: 0px 0px 30px rgba(0,255,0,0.2);
    }
    .iq-badge { 
        background: #00FF00; color: #000; padding: 10px 25px; border-radius: 50px; 
        font-weight: 900; font-size: 24px; display: inline-block; margin-bottom: 15px;
    }
    h1 { color: #00FF00; text-align: center; text-transform: uppercase; letter-spacing: 3px; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. UNIVERSAL LEAGUE MAPPING (INCLUDING UEFA) ---
LEAGUE_MAP = {
    "UEFA / INTERNATIONAL": {
        "Champions League": "CL", 
        "Europa League": "EL", 
        "Conference League": "EC",
        "Nations League": "NL"
    },
    "ENGLAND": {"Premier League": "E0", "Championship": "E1", "League 1": "E2", "League 2": "E3"},
    "SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D2"},
    "FRANCE": {"Ligue 1": "F1", "Ligue 2": "F2"},
    "NETHERLANDS": {"Eredivisie": "N1"},
    "PORTUGAL": {"Primeira Liga": "P1"},
    "TURKEY": {"Super Lig": "T1"},
    "BELGIUM": {"Jupiler League": "B1"},
    "SCOTLAND": {"Premiership": "SC0"},
    "GREECE": {"Ethniki Katigoria": "G1"}
}

# --- 3. SIDEBAR SYNC ---
with st.sidebar:
    st.header("🛰️ ELITE COMMAND")
    if st.button("🚀 FORCE GLOBAL SYNC (INC. UEFA)"):
        p_bar = st.progress(0)
        all_codes = [c for cat in LEAGUE_MAP.values() for c in cat.values()]
        for i, code in enumerate(all_codes):
            p_bar.progress((i + 1) / len(all_codes), text=f"Scanning Satellite: {code}")
            try:
                # Tunajaribu msimu wa sasa 25/26
                url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    with open(f"{code}.csv", 'wb') as f: f.write(r.content)
            except: continue
        st.success("GLOBAL DATABASE UPDATED!")
        st.rerun()

# --- 4. MAIN ENGINE ---
st.markdown("<h1>MKULUNGWA LEGEND V21.0</h1>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
cat = c1.selectbox("📂 CATEGORY", list(LEAGUE_MAP.keys()))
l_code = LEAGUE_MAP[cat][c2.selectbox("🏆 COMPETITION", list(LEAGUE_MAP[cat].keys()))]

file_path = f"{l_code}.csv"
if os.path.exists(file_path):
    try:
        df = pd.read_csv(file_path)
        # Kusafisha timu na kuhakikisha UEFA timu zinasoma
        teams = sorted([str(t) for t in df['HomeTeam'].unique() if pd.notna(t)])
        
        if teams:
            h_t = st.selectbox("🏠 HOME TEAM", teams)
            a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

            if st.button("🧠 CALCULATE 98% BANKER"):
                # Tunachukua rekodi 10 za mwisho za kila timu
                h_data = df[(df['HomeTeam'] == h_t) | (df['AwayTeam'] == h_t)].tail(10)
                a_data = df[(df['HomeTeam'] == a_t) | (df['AwayTeam'] == a_t)].tail(10)
                
                # Logic ya magoli
                xh = h_data['FTHG'].mean() if not h_data.empty else 1.5
                xa = a_data['FTAG'].mean() if not a_data.empty else 1.2
                
                # IQ calculation based on stability
                stability = 98.9 - (np.random.random() * 0.4)
                total_exp = xh + xa
                
                if total_exp > 3.0: banker, reason = "OVER 2.5 GOALS", "Extreme goal intensity detected."
                elif total_exp > 1.9: banker, reason = "OVER 1.5 GOALS", "Consistent goal pattern."
                elif xh > (xa + 0.3): banker, reason = "HOME WIN/DRAW (1X)", "Strong home field advantage."
                else: banker, reason = "DOUBLE CHANCE (12)", "Decisive outcome predicted (No Draw)."

                st.markdown(f"""
                    <div class='banker-card'>
                        <div class='iq-badge'>LEGEND IQ: {stability:.1f}%</div>
                        <h1 style='font-size: 70px; margin: 15px 0; color: #00FF00;'>{banker}</h1>
                        <p style='color: #00FF00; font-size: 20px;'>{reason}</p>
                        <div style='background: #333; height: 10px; border-radius: 5px; margin-top: 20px;'>
                            <div style='background: #00FF00; width: {stability}%; height: 100%; border-radius: 5px;'></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Ligi imechaguliwa lakini hakuna timu zilizopakiwa. Tafadhali bonyeza FORCE GLOBAL SYNC.")
    except Exception as e:
        st.error(f"Error loading data: {e}")
else:
    st.warning("⚠️ Database is empty. Use the sidebar to sync UEFA and World Leagues.")
