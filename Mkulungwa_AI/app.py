import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from io import StringIO

# --- 1. UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V23.4 - GLOBAL BEAST", layout="wide")

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

# --- 2. THE COMPLETE LEAGUE MAP (HAIJAPUNGUA KITU!) ---
NATIONS_MAP = {
    "ENGLAND": {
        "Premier League": "E0",
        "Championship": "E1",
        "League One": "E2",
        "League Two": "E3"
    },
    "FRANCE": {
        "Ligue 1": "F1",
        "Ligue 2": "F2",
        "National": "F3"
    },
    "SPAIN": {
        "La Liga 1": "SP1",
        "La Liga 2": "SP2"
    },
    "ITALY": {
        "Serie A": "I1",
        "Serie B": "I2"
    },
    "GERMANY": {
        "Bundesliga 1": "D1",
        "Bundesliga 2": "D2"
    },
    "NETHERLANDS": {"Eredivisie": "N1"},
    "PORTUGAL": {"Liga I": "P1"},
    "TURKEY": {"Super Lig": "T1"},
    "BELGIUM": {"Jupiler League": "B1"},
    "SCOTLAND": {"Premiership": "SC0"},
    "GREECE": {"Super League": "G1"},
    "AUSTRIA": {"Bundesliga": "AUT"}
}

# Session State for Data
if 'all_data' not in st.session_state:
    st.session_state['all_data'] = {}

# --- 3. GLOBAL SYNC ENGINE ---
with st.sidebar:
    st.header("🛰️ GLOBAL SYNC")
    if st.button("🔄 REFRESH ALL LEAGUES"):
        with st.spinner("Connecting to Global Databases..."):
            for nation, leagues in NATIONS_MAP.items():
                for name, code in leagues.items():
                    try:
                        # Msimu wa sasa
                        url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                        r = requests.get(url, timeout=5)
                        if r.status_code == 200:
                            st.session_state['all_data'][code] = pd.read_csv(StringIO(r.text))
                    except:
                        continue
        st.success(f"DATABASE LOADED: {len(st.session_state['all_data'])} Leagues Active!")

# --- 4. MAIN ENGINE ---
st.markdown("<h1>MKULUNGWA AI V23.4</h1>", unsafe_allow_html=True)

# Selection Dropdowns
selected_nation = st.selectbox("🌍 SELECT NATION", list(NATIONS_MAP.keys()))
league_options = NATIONS_MAP[selected_nation]
selected_league_name = st.selectbox("🏆 SELECT LEAGUE", list(league_options.keys()))
l_code = league_options[selected_league_name]

if l_code in st.session_state['all_data']:
    df = st.session_state['all_data'][l_code]
    teams = sorted(df['HomeTeam'].dropna().unique())
    
    col1, col2 = st.columns(2)
    with col1:
        h_t = st.selectbox("🏠 HOME TEAM", teams)
    with col2:
        a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

    if st.button("🎯 RUN MASTER ANALYSIS"):
        h_form = df[df['HomeTeam'] == h_t].tail(8)
        a_form = df[df['AwayTeam'] == a_t].tail(8)
        
        if not h_form.empty and not a_form.empty:
            # Goals Calculation
            xh = h_form['FTHG'].mean(); xh_c = h_form['FTAG'].mean()
            xa = a_form['FTAG'].mean(); xa_c = a_form['FTHG'].mean()
            total_exp = ((xh + xa_c)/2) + ((xa + xh_c)/2)
            
            # Corners Safety Logic (For leagues like National)
            avg_hc = h_form['HC'].mean() if 'HC' in h_form.columns else 4.5
            avg_ac = a_form['AC'].mean() if 'AC' in a_form.columns else 4.0
            total_corners = avg_hc + avg_ac

            # Picks
            g_pick = "OVER 2.5" if total_exp > 2.8 else ("OVER 1.5" if total_exp > 1.8 else "OVER 0.5")
            
            # Corner Pick (Supports your Under 6.5 - 7.5 logic)
            if total_corners > 10.3: c_pick = "OVER 9.5"
            elif total_corners > 8.9: c_pick = "OVER 8.5"
            elif total_corners > 7.6: c_pick = "OVER 7.5"
            else: c_pick = "OVER 6.5"

            # Results Display
            st.markdown("---")
            r1, r2 = st.columns(2)
            with r1: st.markdown(f"<div class='metric-card'><h3>⚽ GOALS</h3><h1>{g_pick}</h1><p>Exp: {total_exp:.2f}</p></div>", unsafe_allow_html=True)
            with r2: st.markdown(f"<div class='metric-card'><h3>🚩 CORNERS</h3><h1>{c_pick}</h1><p>Exp: {total_corners:.1f}</p></div>", unsafe_allow_html=True)
            
            st.markdown("<div class='advice-section'>", unsafe_allow_html=True)
            st.markdown(f"<div class='advice-text'>✅ UHAKIKA: Uchambuzi wa {selected_league_name} umekamilika.</div>", unsafe_allow_html=True)
            win_adv = f"🏆 MSIMAMO: {'1X (Home Win/Draw)' if xh > xa else 'X2 (Away Win/Draw)'}"
            st.markdown(f"<div class='advice-text'>{win_adv}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='advice-text'>🚩 KONA: Tarajia mchezo wa kona {int(total_corners)}. Chagua {c_pick}.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Data za timu hizi bado hazijatosha kwenye database yetu.")
else:
    st.warning(f"⚠️ Data za {selected_league_name} hazijapakiwa. Bonyeza REFRESH DATABASE kwenye sidebar.")
