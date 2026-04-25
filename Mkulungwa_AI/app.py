import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO

st.set_page_config(page_title="MKULUNGWA AI V23.3 - UNSTOPPABLE", layout="wide")

# UI Styling
st.markdown("""<style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { background: linear-gradient(135deg, #00FF00, #004400); color: white; border-radius: 12px; height: 3.5em; width: 100%; border: 1px solid #00FF00; font-weight: 900; }
    .metric-card { background: #1A1C24; padding: 20px; border-radius: 15px; border-top: 4px solid #00FF00; text-align: center; }
</style>""", unsafe_allow_html=True)

# Data Store
if 'all_data' not in st.session_state: st.session_state['all_data'] = {}

# League Map (Imeboreshwa)
NATIONS_MAP = {
    "ENGLAND": {"EPL": "E0", "Championship": "E1", "League 1": "E2"},
    "FRANCE": {"Ligue 1": "F1", "Ligue 2": "F2", "National": "F3"},
    "SPAIN": {"La Liga 1": "SP1", "La Liga 2": "SP2"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"}
}

with st.sidebar:
    st.header("🛰️ DATA SYNC")
    if st.button("🔄 REFRESH DATABASE"):
        progress = st.progress(0)
        i = 0
        for nation, leagues in NATIONS_MAP.items():
            for l_name, code in leagues.items():
                i += 1
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200:
                        st.session_state['all_data'][code] = pd.read_csv(StringIO(r.text))
                    progress.progress(i / 10)
                except: continue
        st.success("SYNC IMETAMALIZIKA!")

st.markdown("<h1>MKULUNGWA AI V23.3</h1>", unsafe_allow_html=True)

# Selection
nation = st.selectbox("🌍 CHAGUA TAIFA", list(NATIONS_MAP.keys()))
league_name = st.selectbox("🏆 CHAGUA LIGI", list(NATIONS_MAP[nation].keys()))
l_code = NATIONS_MAP[nation][league_name]

if l_code in st.session_state['all_data']:
    df = st.session_state['all_data'][l_code]
    teams = sorted(df['HomeTeam'].dropna().unique())
    
    h_t = st.selectbox("🏠 HOME TEAM", teams)
    a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

    if st.button("🎯 RUN ANALYSIS"):
        h_f = df[df['HomeTeam'] == h_t].tail(6)
        a_f = df[df['AwayTeam'] == a_t].tail(6)
        
        if not h_f.empty and not a_f.empty:
            exp = (h_f['FTHG'].mean() + a_f['FTAG'].mean())
            crn = (h_f['HC'].mean() if 'HC' in h_f.columns else 4.5) + (a_f['AC'].mean() if 'AC' in a_f.columns else 4.0)
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            c1.markdown(f"<div class='metric-card'><h3>⚽ GOALS</h3><h1>{'OVER 1.5' if exp > 1.8 else 'UNDER 2.5'}</h1><p>Exp: {exp:.2f}</p></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-card'><h3>🚩 CORNERS</h3><h1>{'OVER 8.5' if crn > 9 else 'UNDER 8.5'}</h1><p>Exp: {crn:.1f}</p></div>", unsafe_allow_html=True)
        else:
            st.error("Data za timu hizi hazijapatikana (Labda ligi hii haijafunguliwa vizuri).")
else:
    st.warning(f"⚠️ Ligi ya {league_name} (Code: {l_code}) haijapakiwa. Tafadhali bonyeza REFRESH DATABASE.")
