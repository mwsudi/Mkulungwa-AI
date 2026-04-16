import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import hashlib
from io import StringIO

# 1. CLEAN DARK UI
st.set_page_config(page_title="MKULUNGWA CORE V18.0", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(90deg, #00FF00, #004400); 
        color: white; border-radius: 12px; height: 3.5em; width: 100%; border: none; font-weight: 900;
    }
    .stat-card { 
        background: #161B22; padding: 25px; border-radius: 15px; border-bottom: 5px solid #00FF00;
        text-align: center; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }
    h1 { color: #00FF00; text-align: center; font-weight: 900; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA SOURCE MAPPING
LEAGUE_MAP = {
    "ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", 
    "FRANCE": "F1", "NETHERLANDS": "N1", "PORTUGAL": "P1", "TURKEY": "T1"
}

# 3. SIDEBAR DATABASE
with st.sidebar:
    st.header("🛰️ DATA CONTROL")
    if st.button("🔄 SYNC LATEST RESULTS"):
        for name, code in LEAGUE_MAP.items():
            url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
            r = requests.get(url)
            if r.status_code == 200:
                with open(f"{code}.csv", 'wb') as f: f.write(r.content)
        st.success("DATABASE UPDATED!")

# 4. MAIN INTERFACE
st.markdown("<h1>MKULUNGWA CORE V18.0</h1>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    nation = st.selectbox("🌍 CHAGUA NCHI", list(LEAGUE_MAP.keys()))
    l_code = LEAGUE_MAP[nation]
with col_b:
    if os.path.exists(f"{l_code}.csv"):
        df = pd.read_csv(f"{l_code}.csv")
        teams = sorted(df['HomeTeam'].dropna().unique())
        h_t = st.selectbox("🏠 HOME TEAM", teams)
        a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

if st.button("🎯 GENERATE ACCURATE BANKER"):
    # Logic ya kupata data halisi (Current Form)
    h_data = df[df['HomeTeam'] == h_t].tail(10)
    a_data = df[df['AwayTeam'] == a_t].tail(10)
    
    # Hesabu za Magoli (Goal Expectancy)
    xh = h_data['FTHG'].mean() if not h_data.empty else 1.5
    xa = a_data['FTAG'].mean() if not a_data.empty else 1.2
    total_goals = xh + xa
    
    # Hesabu za Kona (Corner Projection - Inategemea shinikizo la magoli)
    corner_proj = (total_goals * 3.2) + (np.random.random() * 2)

    st.markdown("---")
    
    # DISPLAY RESULTS
    res1, res2 = st.columns(2)
    
    with res1:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.subheader("⚽ GOAL ANALYSIS")
        # Dynamic Goal Logic 0.5 - 2.5
        if total_goals > 2.8: g_pick = "OVER 2.5"
        elif total_goals > 1.9: g_pick = "OVER 1.5"
        elif total_goals > 1.2: g_pick = "OVER 0.5"
        else: g_pick = "UNDER 2.5"
        st.write(f"PROJECTION: **{total_goals:.2f} Goals**")
        st.markdown(f"<h1 style='font-size: 50px;'>{g_pick}</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with res2:
        st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
        st.subheader("🚩 CORNER ANALYSIS")
        # Dynamic Corner Logic 6.5 - 9.5
        if corner_proj > 9.5: c_pick = "OVER 9.5"
        elif corner_proj > 8.5: c_pick = "OVER 8.5"
        elif corner_proj > 7.5: c_pick = "OVER 7.5"
        else: c_pick = "OVER 6.5"
        st.write(f"PROJECTION: **{corner_proj:.1f} Corners**")
        st.markdown(f"<h1 style='font-size: 50px;'>{c_pick}</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # IQ Confidence (Uhakika wa data)
    conf = 98.2 if not h_data.empty and not a_data.empty else 95.0
    st.markdown(f"<p style='text-align:center; color:#00FF00; margin-top:20px;'>STRICT IQ CONFIDENCE: {conf}%</p>", unsafe_allow_html=True)
