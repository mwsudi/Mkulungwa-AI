import streamlit as st
import pandas as pd
import os
import requests
from io import StringIO

# --- 1. UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V31.0 - TACTICAL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(135deg, #00FF00, #004400); 
        color: white; border-radius: 12px; height: 3.5em; width: 100%; border: 1px solid #00FF00; font-weight: 900;
    }
    .metric-card { background: #1A1C24; padding: 20px; border-radius: 15px; border-top: 5px solid #00FF00; text-align: center; margin-bottom: 10px; }
    .advice-box { background: rgba(0, 255, 0, 0.05); border-left: 5px solid #00FF00; padding: 15px; border-radius: 8px; margin-top: 10px; }
    .signal-text { font-size: 1.2em; font-weight: bold; }
    h1, h2, h3 { color: #00FF00; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA SYNC ---
LEAGUE_MAP = {
    "ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", "FRANCE": "F1", 
    "NETHERLANDS": "N1", "PORTUGAL": "P1", "BELGIUM": "B1", "SCOTLAND": "SC0", 
    "TURKEY": "T1", "UKRAINE": "U1", "GREECE": "G1", "UEFA LITE": "UEFA_ALL"
}

with st.sidebar:
    st.header("🛰️ GLOBAL SATELLITE")
    if st.button("🔄 REFRESH DATA"):
        all_dfs = []
        for name, code in LEAGUE_MAP.items():
            if code == "UEFA_ALL": continue
            for season in ["2526", "2425"]:
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                        temp_df = pd.read_csv(StringIO(r.text))
                        if not temp_df.empty:
                            essential = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HC', 'AC']
                            all_dfs.append(temp_df[[c for c in essential if c in temp_df.columns]])
                            break
                except: continue
        if all_dfs:
            pd.concat(all_dfs, ignore_index=True, sort=False).to_csv("UEFA_ALL.csv", index=False)
            st.success("DATA REFRESHED!")

# --- 3. ANALYZER ENGINE ---
st.markdown("<h1>MKULUNGWA AI V31.0</h1>", unsafe_allow_html=True)
nation = st.selectbox("🌍 SELECT LEAGUE", list(LEAGUE_MAP.keys()))

if os.path.exists(f"{LEAGUE_MAP[nation]}.csv"):
    df = pd.read_csv(f"{LEAGUE_MAP[nation]}.csv")
    teams = sorted([str(t) for t in df['HomeTeam'].dropna().unique()])
    h_t = st.selectbox("🏠 HOME TEAM (WANYUMBANI)", teams)
    a_t = st.selectbox("🚀 AWAY TEAM (WAGENI)", [t for t in teams if t != h_t])

    if st.button("🎯 EXECUTE TACTICAL ANALYSIS"):
        h_f = df[df['HomeTeam'] == h_t].tail(8)
        a_f = df[df['AwayTeam'] == a_t].tail(8)
        
        # 1. Individual Corner Stats
        home_corner_exp = h_f['HC'].mean() if not h_f.empty else 5.0
        away_corner_exp = a_f['AC'].mean() if not a_f.empty else 4.0
        total_exp = home_corner_exp + away_corner_exp

        # 2. Formula Logic for Individual Teams
        def get_team_bet(exp):
            if exp >= 6.5: return f"OVER {int(exp - 1.5)}.5"
            elif exp >= 5.0: return f"OVER {int(exp - 1.5)}.5"
            else: return "BET SALAMA: OVER 2.5"

        st.markdown("---")
        # Displaying Results
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-card'><h4>🏠 {h_t}</h4><h1>{home_corner_exp:.1f}</h1><p>Home Exp</p></div>", unsafe_allow_html=True)
            st.info(f"Bet: {get_team_bet(home_corner_exp)}")
            
        with col2:
            st.markdown(f"<div class='metric-card'><h4>🚀 {a_t}</h4><h1>{away_corner_exp:.1f}</h1><p>Away Exp</p></div>", unsafe_allow_html=True)
            st.info(f"Bet: {get_team_bet(away_corner_exp)}")

        with col3:
            st.markdown(f"<div class='metric-card'><h4>🚩 TOTAL</h4><h1>{total_exp:.1f}</h1><p>Match Exp</p></div>", unsafe_allow_html=True)
            
        # 3. Overall Signal Logic (Our Trusty Formula)
        st.markdown("### 🚦 USHAURI WA JUMLA (OVERALL ADVICE)")
        if total_exp >= 11.0:
            st.markdown(f"<div class='advice-box' style='border-left-color: #00FF00;'><span class='signal-text' style='color: #00FF00;'>🟢 KIJANI (BANKER)</span><br>Formula: Exp ni kubwa ({total_exp:.1f}). Ushauri wa kitalamu: <b>OVER 8.5 au 7.5</b></div>", unsafe_allow_html=True)
        elif total_exp >= 9.0:
            st.markdown(f"<div class='advice-box' style='border-left-color: #FFFF00;'><span class='signal-text' style='color: #FFFF00;'>🟡 NJANO (SAFE)</span><br>Formula: Exp ya wastani ({total_exp:.1f}). Ushauri wa kitalamu: <b>OVER 7.5 au 6.5</b></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='advice-box' style='border-left-color: #FF4B4B;'><span class='signal-text' style='color: #FF4B4B;'>🔴 NYEKUNDU (RISK)</span><br>Formula: Exp ni ndogo sana ({total_exp:.1f}). Epuka soko la kona hapa.</div>", unsafe_allow_html=True)

else:
    st.info("Tafadhali Refresh Data kuanza uchambuzi wa kitalamu.")
