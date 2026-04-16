import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import random
from io import StringIO

# --- 1. UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V25.0 - THE ORACLE", layout="wide")

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

# --- 2. GLOBAL LEAGUE MAPPING (NOW WITH GREECE) ---
LEAGUE_MAP = {
    "ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", "FRANCE": "F1", 
    "NETHERLANDS": "N1", "PORTUGAL": "P1", "BELGIUM": "B1", "SCOTLAND": "SC0", 
    "TURKEY": "T1", "UKRAINE": "U1", 
    "GREECE": "G1", # Ugiriki Imeongezwa Hapa
    "UEFA LITE (CL/EL/ECL)": "UEFA_ALL"
}

# --- 3. MASTER SYNC ENGINE ---
with st.sidebar:
    st.header("🛰️ GLOBAL SATELLITE")
    if st.button("🔄 REFRESH ALL LEAGUES"):
        all_dfs = []
        with st.spinner("Fetching Data for 12 Nations..."):
            for name, code in LEAGUE_MAP.items():
                if code == "UEFA_ALL": continue
                try:
                    # Kujaribu kuvuta msimu mpya (25/26) au uliopita (24/25)
                    url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                    r = requests.get(url, timeout=10)
                    if r.status_code != 200:
                        url = f"https://www.football-data.co.uk/mmz4281/2425/{code}.csv"
                        r = requests.get(url, timeout=10)
                    
                    if r.status_code == 200:
                        with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                        all_dfs.append(pd.read_csv(StringIO(r.text)))
                except: continue
            
            if all_dfs:
                pd.concat(all_dfs, ignore_index=True).to_csv("UEFA_ALL.csv", index=False)
        st.success("DATABASE READY: GREECE INCLUDED!")

# --- 4. MAIN ENGINE ---
st.markdown("<h1>MKULUNGWA AI V25.0</h1>", unsafe_allow_html=True)

nation = st.selectbox("🌍 SELECT LEAGUE", list(LEAGUE_MAP.keys()))
l_code = LEAGUE_MAP[nation]

if os.path.exists(f"{l_code}.csv"):
    df = pd.read_csv(f"{l_code}.csv")
    teams = sorted(df['HomeTeam'].dropna().unique())
    h_t = st.selectbox("🏠 HOME TEAM", teams)
    a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

    if st.button("🎯 EXECUTE MASTER ANALYSIS"):
        # Technical Isolation
        h_f = df[df['HomeTeam'] == h_t].tail(8)
        a_f = df[df['AwayTeam'] == a_t].tail(8)
        
        if len(h_f) < 2: h_f = df.tail(15) # Safety fallback
            
        # Mathematical IQ
        xh = h_f['FTHG'].mean(); xh_c = h_f['FTAG'].mean()
        xa = a_f['FTAG'].mean(); xa_c = a_f['FTHG'].mean()
        total_exp = ((xh + xa_c)/2) + ((xa + xh_c)/2)
        
        avg_hc = h_f['HC'].mean() if 'HC' in h_f.columns else 4.4
        avg_ac = a_f['AC'].mean() if 'AC' in a_f.columns else 3.9
        total_corners = avg_hc + avg_ac

        # Dynamic Picks
        if total_exp > 3.0: g_p = "OVER 2.5"
        elif total_exp > 1.95: g_p = "OVER 1.5"
        else: g_p = "OVER 0.5"

        if total_corners > 10.4: c_p = "OVER 9.5"
        elif total_corners > 8.9: c_p = "OVER 8.5"
        elif total_corners > 7.6: c_p = "OVER 7.5"
        else: c_p = "OVER 6.5"

        # Multi-Advice Output
        st.markdown("---")
        r1, r2 = st.columns(2)
        with r1: st.markdown(f"<div class='metric-card'><h3>⚽ GOALS</h3><h1>{g_p}</h1><p>Exp: {total_exp:.2f}</p></div>", unsafe_allow_html=True)
        with r2: st.markdown(f"<div class='metric-card'><h3>🚩 CORNERS</h3><h1>{c_p}</h1><p>Exp: {total_corners:.1f}</p></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='advice-section'>", unsafe_allow_html=True)
        st.markdown(f"<div class='advice-text'>✅ CHAGUO SALAMA: Namba zinaashiria {g_p} ni 'Banker' ya leo.</div>", unsafe_allow_html=True)
        
        if xh > (xa + 0.7):
            st.markdown(f"<div class='advice-text'>🏆 MSIMAMO: {h_t} ana nguvu ya Oracle nyumbani. Mpe 1X.</div>", unsafe_allow_html=True)
        elif xa > (xh + 0.7):
            st.markdown(f"<div class='advice-text'>🏆 MSIMAMO: {a_t} ana uwezo wa kuvuna matokeo ugenini. Mpe X2.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='advice-text'>🏆 MSIMAMO: Mechi ngumu, timu zote zina kaba vizuri.</div>", unsafe_allow_html=True)
            
        st.markdown(f"<div class='advice-text'>🚩 KONA: Ugiriki mara nyingi hutoa kona nyingi kutokana na kaba. {c_p} ni uhakika.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Tumia Sidebar na ubonyeze REFRESH ALL LEAGUES kuingiza Ugiriki na ligi nyingine.")
