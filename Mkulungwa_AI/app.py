import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
from math import exp, factorial

# =========================================
# BIST WAPAMBANAJI AI - ELITE 2026 v8.0 PRO
# =========================================

st.set_page_config(
    page_title="BIST WAPAMBANAJI AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# RAPID API CONFIG
# =========================================

API_KEY = "ccc042181cmsh922f2c2406a2e16p15503fjsnd189126344bb"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}

# =========================================
# STYLE ENGINE
# =========================================

st.markdown("""
<style>
.main{ background:#0d1117; color:#e6edf3; }
[data-testid="stSidebar"]{ background:#0b0e14; border-right:2px solid #ffd700; }
.stButton>button{
    background:linear-gradient(135deg,#ffd700 0%,#b8860b 100%);
    color:black !important; border:none; border-radius:10px;
    height:3.5em; font-weight:900; width:100%;
}
.card{
    background:#161b22; padding:25px; border-radius:15px;
    border-left:5px solid #ffd700; text-align:center; margin-bottom:20px;
}
.big-val{ font-size:30px; font-weight:900; color:#ffd700; }
.small{ color:#8b949e; font-size:14px; }
.section-title{
    color:#ffd700; font-size:24px; font-weight:bold; margin-top:25px;
    margin-bottom:15px; border-bottom:2px solid #ffd700; padding-bottom:10px;
}
.signal-box{
    padding:30px; border-radius:20px; text-align:center;
    font-size:30px; font-weight:900; margin:20px 0; background:#0d1117;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# LEAGUES
# =========================================

LEAGUE_MAP = {
    "ENGLAND": {"Premier League": "E0", "Championship": "E1"},
    "SPAIN": {"La Liga": "SP1"},
    "ITALY": {"Serie A": "I1"},
    "GERMANY": {"Bundesliga": "D1"},
    "FRANCE": {"Ligue 1": "F1"}
}

# =========================================
# API & DATA FUNCTIONS
# =========================================

@st.cache_data(ttl=3600)
def load_league_data(code):
    for season in ["2526", "2425"]:
        try:
            url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
            r = requests.get(url, timeout=10)
            if r.status_code == 200: return pd.read_csv(StringIO(r.text))
        except: continue
    return None

def test_api():
    try:
        url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-leagues"
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.status_code == 200
    except: return False

def search_players(team):
    try:
        url = "https://free-api-live-football-data.p.rapidapi.com/football-players-search"
        r = requests.get(url, headers=HEADERS, params={"search": team}, timeout=10)
        data = r.json()
        return len(data.get("response", []))
    except: return 0

# =========================================
# UI HEADER & STATUS
# =========================================

st.markdown("<h1 style='text-align:center;color:#ffd700;'>BIST WAPAMBANAJI AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#8b949e;'>ELITE FOOTBALL AI ENGINE v8.0 PRO</p>", unsafe_allow_html=True)

if test_api():
    st.success("✅ RAPID API CONNECTED")
else:
    st.error("❌ RAPID API FAILED")

# =========================================
# SIDEBAR
# =========================================

st.sidebar.markdown("## 💰 BANKROLL PROTECTOR")
daily_loss = st.sidebar.slider("Daily Risk Limit (TSh)", 10000, 500000, 50000, 5000)
today_loss = st.sidebar.number_input("Today's Current Loss", min_value=0, value=0, step=5000)

if today_loss >= daily_loss:
    st.error("⛔ MASTER, KAA MBALI NA SIMU! PUMZIKA LEO.")
    st.stop()

# =========================================
# SELECTORS
# =========================================

c1, c2 = st.columns(2)
with c1: nation = st.selectbox("🌍 CHAGUA NCHI", list(LEAGUE_MAP.keys()))
with c2: league_name = st.selectbox("🏆 CHAGUA LIGI", list(LEAGUE_MAP[nation].keys()))

code = LEAGUE_MAP[nation][league_name]
df = load_league_data(code)

if df is not None:
    teams = sorted(df["HomeTeam"].dropna().unique())
    s1, s2, s3 = st.columns([2,2,1])
    with s1: home = st.selectbox("🏠 HOME TEAM", teams)
    with s2: away = st.selectbox("🚀 AWAY TEAM", [x for x in teams if x != home])
    with s3: market_odds = st.number_input("💰 O2.5 ODDS", min_value=1.10, value=1.85, step=0.01)

    if st.button("🎯 RUN AI ANALYSIS"):
        h_data, a_data = df[df["HomeTeam"] == home].tail(8), df[df["AwayTeam"] == away].tail(8)
        if len(h_data) < 5 or len(a_data) < 5:
            st.error("⚠️ Data haitoshi.")
            st.stop()

        w = np.arange(1, len(h_data)+1)
        h_sc = np.average(h_data["FTHG"], weights=w) * (1.10 if nation in ["ENGLAND","GERMANY"] else 1.05)
        h_con = np.average(h_data["FTAG"], weights=w)
        a_sc = np.average(a_data["FTAG"], weights=w)
        a_con = np.average(a_data["FTHG"], weights=w)

        h_xg, a_xg = (h_sc + a_con) / 2, (a_sc + h_con) / 2
        total_xg = h_xg + a_xg

        def poisson(lam, k): return ((lam**k)*exp(-lam))/factorial(k) if lam > 0 else 0
        prob_o25 = 1 - sum(poisson(h_xg, i) * poisson(a_xg, j) for i in range(3) for j in range(3) if i + j < 3)
        prob_btts = (1 - poisson(h_xg, 0)) * (1 - poisson(a_xg, 0))

        # Filters
        if h_data["FTAG"].iloc[-1] >= 3 or a_data["FTHG"].iloc[-1] >= 3: prob_o25 -= 0.05
        if (h_data["FTAG"] == 0).mean() > 0.45: prob_btts -= 0.08
        if (a_data["FTHG"] == 0).mean() > 0.45: prob_btts -= 0.08

        # Momentum
        def pts(row, h_side=True):
            if h_side: return 3 if row["FTR"]=="H" else (1 if row["FTR"]=="D" else 0)
            return 3 if row["FTR"]=="A" else (1 if row["FTR"]=="D" else 0)
        m_diff = sum(pts(r, True) for _,r in h_data.tail(5).iterrows()) - sum(pts(r, False) for _,r in a_data.tail(5).iterrows())
        
        intensity = h_data["HS"].mean() + a_data["AS"].mean()
        if intensity > 25: prob_o25 += 0.04
        elif intensity < 18: prob_o25 -= 0.04

        # API Check
        h_p, a_p = search_players(home), search_players(away)
        total_p = h_p + a_p
        if total_p > 0 and total_p < 5: prob_o25 -= 0.04

        prob_o25, prob_btts = min(max(prob_o25, 0.05), 0.95), min(max(prob_btts, 0.05), 0.95)

        # Score & Quality
        score = (2 if prob_o25 > .72 else 0) + (1 if prob_btts > .65 else 0) + (2 if total_xg > 3.1 else 0) + (1 if intensity > 22 else 0)
        quality = round((prob_o25*45 + prob_btts*25 + min(total_xg/4,1)*20 + min(intensity/30,1)*10), 1)

        # UI DISPLAY
        st.markdown("<div class='section-title'>📊 MATCH ANALYSIS</div>", unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4)
        r1.markdown(f"<div class='card'><p class='small'>OVER 2.5</p><div class='big-val'>{prob_o25*100:.1f}%</div></div>", unsafe_allow_html=True)
        r2.markdown(f"<div class='card'><p class='small'>BTTS</p><div class='big-val'>{prob_btts*100:.1f}%</div></div>", unsafe_allow_html=True)
        vol = (np.std(h_data["FTHG"]) + np.std(a_data["FTAG"])) / 2
        r3.markdown(f"<div class='card'><p class='small'>VOLATILITY</p><div class='big-val'>{vol:.2f}</div></div>", unsafe_allow_html=True)
        r4.markdown(f"<div class='card'><p class='small'>MOMENTUM</p><div class='big-val'>{m_diff}</div></div>", unsafe_allow_html=True)

        # FINAL VERDICT
        st.markdown("<div class='section-title'>🧠 FINAL AI VERDICT</div>", unsafe_allow_html=True)
        if score >= 7 and quality >= 75: col, verdict = "#00ff66", "🔥 GREEN ELITE"
        elif score >= 5: col, verdict = "#ffd700", "⚖️ YELLOW RISK"
        else: col, verdict = "#ff4d4d", "⛔ RED AVOID"

        st.markdown(f"""
            <div class="signal-box" style="border:3px solid {col}; color:{col};">
            {verdict}<br><br>
            ⭐ QUALITY: {quality}/100<br>
            📈 SCORE: {score}/8
            </div>
        """, unsafe_allow_html=True)

        # Bet Engine
        edge = round((prob_o25 - (1/market_odds))*100, 1)
        if score >= 7 and edge > 5: st.success("🔥 FINAL AI BET: OVER 2.5")
        elif prob_btts >= .62 and intensity >= 20: st.success("⚽ FINAL AI BET: BTTS YES")
        else: st.success("⛔ FINAL AI BET: SKIP MATCH")

        kelly = (((prob_o25 * market_odds) - 1) / (market_odds - 1)) if market_odds > 1 else 0
        st.warning(f"💰 RECOMMENDED STAKE: {min(max(0, kelly * 100 / 5), 10):.1f}% | 📈 EDGE: {edge}%")
else:
    st.error("❌ FAILED TO LOAD DATA")
