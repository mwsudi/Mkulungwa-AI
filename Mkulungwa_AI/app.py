import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
from math import exp, factorial

# =========================================
# MKULUNGWA AI MASTER PRO - ELITE EDITION 2026
# =========================================

st.set_page_config(
    page_title="MKULUNGWA AI MASTER PRO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# ADVANCED GOLDEN STYLE (PRO UI)
# =========================================

st.markdown("""
<style>
    .main { background-color: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    
    .stButton>button {
        background: linear-gradient(135deg, #ffd700, #b8860b);
        color: black !important;
        border: none; border-radius: 10px;
        height: 3.5em; font-weight: bold; width: 100%;
        transition: 0.3s; box-shadow: 0px 4px 15px rgba(255, 215, 0, 0.2);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0px 6px 20px rgba(255, 215, 0, 0.4); }

    .card {
        background: #1c2128; padding: 25px; border-radius: 15px;
        border: 1px solid #30363d; border-top: 4px solid #ffd700;
        text-align: center; margin-bottom: 20px;
    }
    .big-val { font-size: 32px; font-weight: 900; color: #ffd700; margin: 10px 0; }
    .small { color: #8b949e; font-size: 14px; }
    
    .section-title {
        color: #ffd700; font-size: 24px; font-weight: bold;
        border-bottom: 2px solid #30363d; margin: 25px 0 15px 0; padding-bottom: 10px;
    }
    
    .signal-box {
        padding: 25px; border-radius: 15px; text-align: center;
        font-size: 28px; font-weight: bold; margin: 20px 0;
        background: rgba(0,0,0,0.2);
    }
    
    .h2h-box {
        background: #161b22; padding: 12px; border-radius: 8px;
        border: 1px solid #30363d; margin-bottom: 8px;
        display: flex; justify-content: space-between; align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# =========================================
# LEAGUES ENGINE
# =========================================

LEAGUE_MAP = {
    "ENGLAND": {"Premier League": "E0", "Championship": "E1"},
    "SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D2"},
    "FRANCE": {"Ligue 1": "F1", "Ligue 2": "F2"},
    "NETHERLANDS": {"Eredivisie": "N1"},
    "PORTUGAL": {"Liga Portugal": "P1"},
    "TURKEY": {"Super Lig": "T1"}
}

if "data_cache" not in st.session_state:
    st.session_state.data_cache = {}

# =========================================
# SIDEBAR SYNC
# =========================================

with st.sidebar:
    st.title("🛰️ MKULUNGWA SYNC")
    st.info("Boresha data ili AI iwe na usahihi wa 2026.")
    
    if st.button("🔄 REFRESH DATABASE"):
        loaded = 0
        with st.spinner("Fetching Live Match Data..."):
            for nation, leagues in LEAGUE_MAP.items():
                for league_name, code in leagues.items():
                    try:
                        # Hapa inajaribu msimu wa 2526, ikifeli inachukua 2425
                        url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                        r = requests.get(url, timeout=5)
                        if r.status_code != 200:
                            url = f"https://www.football-data.co.uk/mmz4281/2425/{code}.csv"
                            r = requests.get(url, timeout=5)
                        
                        if r.status_code == 200:
                            st.session_state.data_cache[code] = pd.read_csv(StringIO(r.text))
                            loaded += 1
                    except: pass
        st.success(f"Successfully Synced {loaded} Leagues!")

# =========================================
# INTERFACE
# =========================================

st.markdown("<h1 style='text-align:center; color:#ffd700;'>MKULUNGWA AI MASTER PRO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#8b949e;'>Elite Neural Football Prediction Engine v4.2</p>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1: nation = st.selectbox("🌍 SELECT COUNTRY", list(LEAGUE_MAP.keys()))
with c2: league_name = st.selectbox("🏆 SELECT LEAGUE", list(LEAGUE_MAP[nation].keys()))

code = LEAGUE_MAP[nation][league_name]

if code in st.session_state.data_cache:
    df = st.session_state.data_cache[code]
    teams = sorted(df["HomeTeam"].dropna().unique())

    t1, t2, t3 = st.columns([2,2,1])
    with t1: home = st.selectbox("🏠 HOME TEAM", teams)
    with t2: away = st.selectbox("🚀 AWAY TEAM", [x for x in teams if x != home])
    with t3: market_odds = st.number_input("💰 O2.5 MARKET ODDS", min_value=1.10, value=1.85, step=0.01)

    if st.button("🎯 RUN MASTER ANALYSIS"):
        # Data Slicing
        h_data = df[df["HomeTeam"] == home].tail(8)
        a_data = df[df["AwayTeam"] == away].tail(8)

        if len(h_data) < 3 or len(a_data) < 3:
            st.error("⚠️ Data haitoshi kufanya uchambuzi makini.")
            st.stop()

        # Weighting
        w_h = np.arange(1, len(h_data) + 1)
        w_a = np.arange(1, len(a_data) + 1)

        # Intelligence Calculations
        h_adv = 1.12 if nation in ["ENGLAND", "GERMANY"] else 1.07
        h_sc = np.average(h_data["FTHG"], weights=w_h) * h_adv
        h_con = np.average(h_data["FTAG"], weights=w_h)
        a_sc = np.average(a_data["FTAG"], weights=w_a)
        a_con = np.average(a_data["FTHG"], weights=w_a)

        home_xg = (h_sc + a_con) / 2
        away_xg = (a_sc + h_con) / 2
        total_xg = home_xg + away_xg

        def poisson(lam, k):
            return (lam ** k * exp(-lam)) / factorial(k) if lam > 0 else 0

        # Probabilities
        prob_u25 = sum(poisson(home_xg, i) * poisson(away_xg, j) for i in range(3) for j in range(3) if i+j < 3)
        prob_o25 = 1 - prob_u25
        prob_btts = (1 - poisson(home_xg, 0)) * (1 - poisson(away_xg, 0))

        # Intensity Logic
        h_shots = h_data["HS"].mean() if "HS" in h_data.columns else 10
        a_shots = a_data["AS"].mean() if "AS" in a_data.columns else 8
        intensity = h_shots + a_shots

        if intensity > 24: prob_o25 *= 1.08
        elif intensity < 18: prob_o25 *= 0.92
        prob_o25 = max(0.01, min(0.99, prob_o25))

        # Scoring System (0-7)
        score = 0
        if prob_o25 > 0.72: score += 2
        if prob_btts > 0.65: score += 1
        if intensity > 22: score += 1
        if total_xg > 3.1: score += 2
        if (h_data["FTHG"].iloc[-1] + h_data["FTAG"].iloc[-1]) > 2: score += 1

        # Contradiction Logic
        if (prob_o25 > 0.70 and prob_btts < 0.50) or (intensity < 17 and total_xg > 3.2):
            score -= 2

        # Display Metrics
        st.markdown("<div class='section-title'>📊 DETAILED ANALYSIS</div>", unsafe_allow_html=True)
        r1, r2, r3 = st.columns(3)

        goal_pick = "🟢 OVER 2.5" if prob_o25 > 0.70 else ("🟡 OVER 1.5" if prob_o25 > 0.58 else "🔴 SKIP/UNDER")
        btts_pick = "🟢 BTTS YES" if prob_btts > 0.65 else ("🟡 BTTS MAYBE" if prob_btts > 0.55 else "🔴 BTTS NO")
        total_corners = (h_data["HC"].mean() if "HC" in h_data.columns else 5) + (a_data["AC"].mean() if "AC" in a_data.columns else 4)

        with r1: st.markdown(f"<div class='card'><h3>⚽ GOALS</h3><div class='big-val'>{goal_pick}</div><p class='small'>{prob_o25*100:.1f}% Probability</p></div>", unsafe_allow_html=True)
        with r2: st.markdown(f"<div class='card'><h3>🎯 BTTS</h3><div class='big-val'>{btts_pick}</div><p class='small'>{prob_btts*100:.1f}% Probability</p></div>", unsafe_allow_html=True)
        with r3: st.markdown(f"<div class='card'><h3>🚩 CORNERS</h3><div class='big-val'>{'🟢 O9.5' if total_corners > 10 else '🟡 O8.5'}</div><p class='small'>Avg: {total_corners:.1f}</p></div>", unsafe_allow_html=True)

        # Verdict
        st.markdown("<div class='section-title'>🧠 FINAL AI VERDICT</div>", unsafe_allow_html=True)
        sig_col = "#00ff66" if score >= 5 else ("#ffd700" if score >= 3 else "#ff4d4d")
        sig_txt = "🔥 STRONG BUY" if score >= 5 else ("⚖️ NEUTRAL" if score >= 3 else "⚠️ AVOID")
        st.markdown(f"<div class='signal-box' style='border:2px solid {sig_col}; color:{sig_col};'>{sig_txt} (Score: {score}/7)</div>", unsafe_allow_html=True)

        # Financials
        implied = 1 / market_odds
        edge = (prob_o25 - implied) * 100
        val_status = "🔥 HIGH VALUE" if edge > 8 else ("✅ VALUE" if edge > 2 else "❌ NO VALUE")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1: st.success(f"VALUE EDGE: {val_status} ({edge:.1f}%)")
        with col_f2:
            kelly = ((prob_o25 * market_odds) - 1) / (market_odds - 1) if market_odds > 1 else 0
            safe_k = min(max(0, kelly * 100 / 5), 10) # 5 divisor for fractional kelly
            st.warning(f"💰 RECOMMENDED STAKE: {safe_k:.1f}%")

        # H2H
        st.markdown("<div class='section-title'>📜 H2H HISTORY</div>", unsafe_allow_html=True)
        h2h = df[((df["HomeTeam"] == home) & (df["AwayTeam"] == away)) | ((df["HomeTeam"] == away) & (df["AwayTeam"] == home))].tail(5)
        if not h2h.empty:
            for _, r in h2h.iterrows():
                st.markdown(f"<div class='h2h-box'><span>{r['HomeTeam']}</span> <b>{r['FTHG']} - {r['FTAG']}</b> <span>{r['AwayTeam']}</span></div>", unsafe_allow_html=True)
        else: st.write("No recent H2H encounters found.")

else:
    st.warning("⚠️ Database is empty. Click REFRESH DATABASE to start.")
