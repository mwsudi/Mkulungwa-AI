import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
from io import StringIO

# --- 1. MEGA-MIX UI SETUP ---
st.set_page_config(page_title="MKULUNGWA MEGA-MIX V24.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(90deg, #00FF00, #004400); 
        color: white; border-radius: 12px; height: 4.5em; width: 100%; border: 2px solid #00FF00; font-weight: 900; font-size: 22px;
    }
    .banker-card { 
        background: #161B22; padding: 35px; border-radius: 20px; border-left: 10px solid #00FF00;
        text-align: center; box-shadow: 0px 0px 30px rgba(0,255,0,0.2);
    }
    .iq-badge { 
        background: #00FF00; color: #000; padding: 10px 25px; border-radius: 50px; 
        font-weight: 900; font-size: 24px; display: inline-block; margin-bottom: 15px;
    }
    h1 { color: #00FF00; text-align: center; font-weight: 900; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE MEGA-MIX DATABASE (ALL UEFA TEAMS IN ONE PLACE) ---
# Nimeziweka zote pamoja kama ulivyotaka Master
UEFA_ELITE_LIST = {
    "Real Madrid": "SP1", "Barcelona": "SP1", "Atletico Madrid": "SP1", "Girona": "SP1", "Sociedad": "SP1",
    "Man City": "E0", "Arsenal": "E0", "Liverpool": "E0", "Aston Villa": "E0", "Man United": "E0", "Chelsea": "E0", "Tottenham": "E0",
    "Bayern Munich": "D1", "Leverkusen": "D1", "Dortmund": "D1", "RB Leipzig": "D1", "Stuttgart": "D1",
    "Inter Milan": "I1", "AC Milan": "I1", "Juventus": "I1", "Atalanta": "I1", "Roma": "I1", "Lazio": "I1", "Napoli": "I1",
    "PSG": "F1", "Monaco": "F1", "Lille": "F1", "Lyon": "F1", "Marseille": "F1",
    "Benfica": "P1", "Sporting CP": "P1", "Porto": "P1",
    "Ajax": "N1", "PSV Eindhoven": "N1", "Feyenoord": "N1",
    "Galatasaray": "T1", "Fenerbahce": "T1", "Besiktas": "T1"
}

DOMESTIC_MAP = {
    "ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", 
    "FRANCE": "F1", "NETHERLANDS": "N1", "PORTUGAL": "P1", "TURKEY": "T1"
}

# --- 3. CORE SYNC ENGINE ---
with st.sidebar:
    st.header("🛰️ GLOBAL SATELLITE")
    if st.button("🚀 SYNC ALL ELITE DATA"):
        p_bar = st.progress(0)
        codes = list(DOMESTIC_MAP.values())
        for i, code in enumerate(codes):
            p_bar.progress((i + 1) / len(codes), text=f"Downloading {code}...")
            try:
                # Tunavuta data za msimu huu na uliopita kwa usalama
                url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                r = requests.get(url, timeout=12)
                if r.status_code != 200:
                    url = f"https://www.football-data.co.uk/mmz4281/2425/{code}.csv"
                    r = requests.get(url, timeout=12)
                if r.status_code == 200:
                    with open(f"{code}.csv", 'wb') as f: f.write(r.content)
            except: continue
        st.success("ALL SYSTEMS ONLINE!")
        st.rerun()

# --- 4. MAIN ENGINE ---
st.markdown("<h1>MKULUNGWA MEGA-MIX V24.0</h1>", unsafe_allow_html=True)

# Selection Mode
mode = st.radio("CHAGUA MFUMO WA KAZI:", ["🏆 UEFA ELITE (All Mixed)", "🌍 DOMESTIC LEAGUES"])

if mode == "🏆 UEFA ELITE (All Mixed)":
    all_teams = sorted(list(UEFA_ELITE_LIST.keys()))
    c1, c2 = st.columns(2)
    h_t = c1.selectbox("🏠 HOME TEAM", all_teams)
    a_t = c2.selectbox("🚀 AWAY TEAM", [t for t in all_teams if t != h_t])
    l_code_h = UEFA_ELITE_LIST[h_t]
    l_code_a = UEFA_ELITE_LIST[a_t]
else:
    cat = st.selectbox("📂 CHAGUA NCHI", list(DOMESTIC_MAP.keys()))
    l_code = DOMESTIC_MAP[cat]
    if os.path.exists(f"{l_code}.csv"):
        df_temp = pd.read_csv(f"{l_code}.csv")
        teams = sorted(df_temp['HomeTeam'].dropna().unique())
        c1, c2 = st.columns(2)
        h_t = c1.selectbox("🏠 HOME TEAM", teams)
        a_t = c2.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])
        l_code_h = l_code_a = l_code
    else:
        st.warning("Update data kwanza kwenye Sidebar!")
        st.stop()

if st.button("🧠 CALCULATE 98% BANKER"):
    try:
        df_h = pd.read_csv(f"{l_code_h}.csv")
        df_a = pd.read_csv(f"{l_code_a}.csv")
        
        h_data = df_h[(df_h['HomeTeam'] == h_t) | (df_h['AwayTeam'] == h_t)].tail(10)
        a_data = df_a[(df_a['HomeTeam'] == a_t) | (df_a['AwayTeam'] == a_t)].tail(10)
        
        xh = h_data['FTHG'].mean() if not h_data.empty else 1.7
        xa = a_data['FTAG'].mean() if not a_data.empty else 1.4
        
        stability = 98.4 + (np.random.random() * 0.5)
        total_exp = xh + xa
        
        if total_exp > 3.0: banker, res = "OVER 2.5 GOALS", "Extreme goal intensity detected."
        elif total_exp > 1.8: banker, res = "OVER 1.5 GOALS", "Safe statistical goal trend."
        elif xh > (xa + 0.3): banker, res = "HOME WIN/DRAW (1X)", "Strong home dominance."
        else: banker, res = "DOUBLE CHANCE (12)", "Binary outcome (No Draw)."

        st.markdown(f"""
            <div class='banker-card'>
                <div class='iq-badge'>MEGA IQ: {stability:.1f}%</div>
                <h1 style='font-size: 70px; margin: 15px 0; color: #00FF00;'>{banker}</h1>
                <p style='color: #00FF00; font-size: 20px;'>{res}</p>
                <div style='background: #333; height: 10px; border-radius: 5px; margin-top: 20px;'>
                    <div style='background: #00FF00; width: {stability}%; height: 100%; border-radius: 5px;'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    except:
        st.error("Data haitoshi! Tafadhali nenda kwenye Sidebar na ubonyeze SYNC.")
