import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
from io import StringIO
from scipy.stats import poisson

# --- 1. THE TRUTH UI ---
st.set_page_config(page_title="MKULUNGWA V19.0 THE TRUTH", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(135deg, #00FF00, #004400); 
        color: white; border-radius: 12px; height: 3.5em; width: 100%; border: 1px solid #00FF00; font-weight: 900;
    }
    .metric-card { 
        background: #1A1C24; padding: 25px; border-radius: 15px; border-top: 4px solid #00FF00;
        text-align: center; box-shadow: 0px 10px 20px rgba(0,0,0,0.4);
    }
    .warning-card {
        background: #2D1B1B; padding: 15px; border-radius: 10px; border: 1px solid #FF4B4B; color: #FF4B4B; text-align: center;
    }
    h1 { color: #00FF00; text-align: center; font-weight: 900; text-transform: uppercase; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LEAGUE MAPPING ---
LEAGUE_MAP = {
    "ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", 
    "FRANCE": "F1", "NETHERLANDS": "N1", "PORTUGAL": "P1", "TURKEY": "T1"
}

# --- 3. SIDEBAR SYNC ---
with st.sidebar:
    st.header("🛰️ REAL-TIME SYNC")
    if st.button("🚀 FETCH LIVE CSV DATA"):
        with st.spinner("Connecting to Football-Data.co.uk..."):
            for name, code in LEAGUE_MAP.items():
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                    else: # Fallback to 2425 if current season is empty
                        url = f"https://www.football-data.co.uk/mmz4281/2425/{code}.csv"
                        r = requests.get(url, timeout=10)
                        with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                except: st.error(f"Failed to sync {name}")
        st.success("DATA SYNC COMPLETE!")

# --- 4. ENGINE ---
st.markdown("<h1>MKULUNGWA V19.0 THE TRUTH</h1>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    nation = st.selectbox("🌍 SELECT NATION", list(LEAGUE_MAP.keys()))
    l_code = LEAGUE_MAP[nation]
with c2:
    if os.path.exists(f"{l_code}.csv"):
        df = pd.read_csv(f"{l_code}.csv")
        teams = sorted(df['HomeTeam'].dropna().unique())
        h_t = st.selectbox("🏠 HOME TEAM", teams)
        a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

if st.button("🧠 EXECUTE POISSON ANALYSIS"):
    # Filter Only HOME matches for HomeTeam and AWAY matches for AwayTeam (The Truth)
    h_form = df[df['HomeTeam'] == h_t].tail(8)
    a_form = df[df['AwayTeam'] == a_t].tail(8)
    
    if len(h_form) < 3 or len(a_form) < 3:
        st.markdown("<div class='warning-card'>⚠️ DATA INSUFFICIENT: Timu hizi hazina rekodi za kutosha msimu huu kutoa utabiri wa kweli.</div>", unsafe_allow_html=True)
    else:
        # Mahesabu ya Kweli
        avg_h_scored = h_form['FTHG'].mean()
        avg_h_conceded = h_form['FTAG'].mean()
        avg_a_scored = a_form['FTAG'].mean()
        avg_a_conceded = a_form['FTHG'].mean()
        
        # Expected Goals (Lambda)
        exp_h = (avg_h_scored + avg_a_conceded) / 2
        exp_a = (avg_a_scored + avg_h_conceded) / 2
        total_exp = exp_h + exp_a
        
        # Corner Estimation based on pressure (Goal attempts)
        corner_base = (total_exp * 2.8) + 3.5
        
        st.markdown("---")
        res1, res2 = st.columns(2)
        
        with res1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.subheader("⚽ GOAL PROJECTION")
            # Strict logic based on Poisson average
            if total_exp > 3.1: g_pick = "OVER 2.5"
            elif total_exp > 2.0: g_pick = "OVER 1.5"
            elif total_exp > 1.2: g_pick = "OVER 0.5"
            else: g_pick = "UNDER 3.5 (SAFE)"
            
            st.write(f"Confidence Rate: **{(total_exp/4)*100:.1f}%**")
            st.markdown(f"<h1 style='color: #00FF00;'>{g_pick}</h1>", unsafe_allow_html=True)
            st.write(f"Expected: {total_exp:.2f} Goals")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with res2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.subheader("🚩 CORNER PROJECTION")
            if corner_base > 10.5: c_pick = "OVER 9.5"
            elif corner_base > 8.8: c_pick = "OVER 8.5"
            elif corner_base > 7.5: c_pick = "OVER 7.5"
            else: c_pick = "OVER 6.5"
            
            st.write(f"Intensity: **Low-Medium**" if corner_base < 8 else "Intensity: **High**")
            st.markdown(f"<h1 style='color: #00FF00;'>{c_pick}</h1>", unsafe_allow_html=True)
            st.write(f"Expected: {int(corner_base)} - {int(corner_base)+2} Corners")
            st.markdown("</div>", unsafe_allow_html=True)

        st.info(f"💡 MASTER ADVICE: Hii mechi inasomwa kutokana na fomu ya {h_t} nyumbani na {a_t} ugenini pekee. Hii ndio siri ya data za kweli.")
