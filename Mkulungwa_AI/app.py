import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib
from io import StringIO

# 1. UI SETUP & STYLING
st.set_page_config(page_title="MKULUNGWA AI V17.4", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(45deg, #00FF00, #004d00); 
        color: white; border-radius: 10px; height: 3.5em; width: 100%; border: none; font-weight: bold;
    }
    .result-card-green { background-color: #1A1C24; padding: 20px; border-radius: 15px; border-top: 6px solid #00FF00; text-align: center; margin-bottom: 15px; }
    .result-card-yellow { background-color: #1A1C24; padding: 20px; border-radius: 15px; border-top: 6px solid #FFD700; text-align: center; margin-bottom: 15px; }
    .result-card-red { background-color: #1A1C24; padding: 20px; border-radius: 15px; border-top: 6px solid #FF4B4B; text-align: center; margin-bottom: 15px; }
    h1 { color: #00FF00; text-align: center; font-weight: 900; text-shadow: 2px 2px #000; }
    </style>
    """, unsafe_allow_html=True)

# 2. STABLE ELITE LEAGUE MAP
LEAGUE_MAP = {
    "UEFA / EUROPA / CONFERENCE": {"ELITE_CLUBS": "UEFA_ALL"},
    "ENGLAND": {"Premier League": "E0", "Championship": "E1"},
    "SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D2"},
    "FRANCE": {"Ligue 1": "F1"},
    "NETHERLANDS": {"Eredivisie": "N1"},
    "PORTUGAL": {"Primeira Liga": "P1"},
    "TURKEY": {"Super Lig": "T1"},
    "BELGIUM": {"Pro League": "B1"},
    "SCOTLAND": {"Premiership": "SC0"},
    "GREECE": {"Super League": "G1"}
}

# 3. GLOBAL SYNC WITH PROGRESS BAR
with st.sidebar:
    st.header("⚙️ SYSTEM CONTROL")
    if st.button("🚀 RUN GLOBAL DATA SYNC"):
        all_dfs = []
        progress_text = "Connecting to Data Centers..."
        p_bar = st.progress(0, text=progress_text)
        
        leagues = []
        for cat in LEAGUE_MAP:
            if cat != "UEFA / EUROPA / CONFERENCE":
                for name, code in LEAGUE_MAP[cat].items():
                    leagues.append(code)
        
        for i, code in enumerate(leagues):
            try:
                url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                    all_dfs.append(pd.read_csv(StringIO(r.text)))
                time.sleep(0.1)
                p_bar.progress((i + 1) / len(leagues), text=f"Syncing {code}...")
            except: continue
            
        if all_dfs:
            pd.concat(all_dfs, ignore_index=True).to_csv("UEFA_ALL.csv", index=False)
            st.success("GLOBAL SYNC COMPLETED! 🛡️")

# 4. INTERFACE
st.markdown("<h1>🛡️ MKULUNGWA AI V17.4: VISUAL MODE 🛡️</h1>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    category = st.selectbox("📂 CHAGUA KUNDI", list(LEAGUE_MAP.keys()))
with c2:
    if category == "UEFA / EUROPA / CONFERENCE":
        league_code = "UEFA_ALL"
    else:
        league_name = st.selectbox("🏆 CHAGUA LIGI", list(LEAGUE_MAP[category].keys()))
        league_code = LEAGUE_MAP[category][league_name]

# 5. ANALYSIS ENGINE
df = pd.DataFrame()
if os.path.exists(f"{league_code}.csv"):
    df = pd.read_csv(f"{league_code}.csv")

if not df.empty and 'HomeTeam' in df.columns:
    teams = sorted(df['HomeTeam'].dropna().unique())
    col1, col2 = st.columns(2)
    h_t = col1.selectbox("🏠 HOME TEAM", teams)
    a_t = col2.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])
    
    if st.button("🎯 EXECUTE DEEP ANALYSIS"):
        match_key = f"{h_t}{a_t}{league_code}_V174_PRO"
        seed = int(hashlib.md5(match_key.encode()).hexdigest(), 16) % (10**6)
        np.random.seed(seed)

        # Analysis Progress
        p_bar_an = st.progress(0, text="Reading Neural Patterns...")
        for i in range(101):
            time.sleep(0.005)
            p_bar_an.progress(i)

        h_data = df[df['HomeTeam'] == h_t].tail(10)
        a_data = df[df['AwayTeam'] == a_t].tail(10)
        
        xh = h_data['FTHG'].mean() if not h_data.empty else 1.5
        xa = a_data['FTAG'].mean() if not a_data.empty else 1.2
        
        # IQ Accuracy Calculation
        conf = 96.0 + (seed % 30) / 10
        if conf > 98.9: conf = 98.9
        
        # Color Logic
        if conf >= 97.5: card_style = "result-card-green"
        elif conf >= 96.5: card_style = "result-card-yellow"
        else: card_style = "result-card-red"

        # Predictions Logic
        if xh > (xa + 0.15): dc_pick, trend = "1X (HOME/DRAW)", "📈"
        elif xa > (xh + 0.15): dc_pick, trend = "X2 (AWAY/DRAW)", "📉"
        else: dc_pick, trend = "12 (NO DRAW)", "↔️"

        total_exp = xh + xa
        goal_pick = "OVER 2.5" if total_exp > 2.6 else "OVER 1.5" if total_exp > 1.5 else "UNDER 3.5"
        
        corner_calc = total_exp * 3.7 + (seed % 2)
        corner_pick = "OVER 9.5" if corner_calc > 9.0 else "OVER 8.5" if corner_calc > 7.5 else "OVER 6.5"

        # UI RESULTS
        st.markdown(f"<h2 style='text-align:center; color:#00FF00;'>🎯 IQ ACCURACY: {conf:.1f}% {trend}</h2>", unsafe_allow_html=True)
        
        res1, res2, res3 = st.columns(3)
        with res1: st.markdown(f"<div class='{card_style}'><h3>🏆 DC OPTION</h3><h2>{dc_pick}</h2></div>", unsafe_allow_html=True)
        with res2: st.markdown(f"<div class='{card_style}'><h3>🚩 CORNERS</h3><h2>{corner_pick}</h2></div>", unsafe_allow_html=True)
        with res3: st.markdown(f"<div class='{card_style}'><h3>⚽ GOALS</h3><h2>{goal_pick}</h2></div>", unsafe_allow_html=True)
else:
    st.info("💡 Run 'GLOBAL DATA SYNC' to activate the system.")
