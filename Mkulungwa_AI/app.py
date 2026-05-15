import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
from math import exp, factorial

# =========================================
# BIST WAPAMBANAJI AI - ELITE 2026 v9.0 PRO
# =========================================

st.set_page_config(
    page_title="BIST WAPAMBANAJI AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# FOOTBALL-DATA.ORG API CONFIG
# =========================================

API_KEY = "2493de184054414dae83d3a909d012d0"
HEADERS = {"X-Auth-Token": API_KEY}

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
.warning-box{
    background:#2d1b00; padding:15px; border-radius:10px;
    border-left:5px solid orange; margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# DYNAMIC LEAGUE MAP (CSV vs API)
# =========================================

LEAGUE_MAP = {
    "ENGLAND": {
        "Premier League": {"csv": "E0", "api": "PL"},
        "Championship": {"csv": "E1", "api": "ELC"}
    },
    "SPAIN": {
        "La Liga": {"csv": "SP1", "api": "PD"}
    },
    "ITALY": {
        "Serie A": {"csv": "I1", "api": "SA"}
    },
    "GERMANY": {
        "Bundesliga": {"csv": "D1", "api": "BL1"}
    },
    "FRANCE": {
        "Ligue 1": {"csv": "F1", "api": "FL1"}
    }
}

# =========================================
# DATA FUNCTIONS
# =========================================

@st.cache_data(ttl=3600)
def load_league_data(code):
    for season in ["2526", "2425"]:
        try:
            url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return pd.read_csv(StringIO(r.text))
        except: continue
    return None

def test_api():
    try:
        url = "https://api.football-data.org/v4/competitions/PL"
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.status_code == 200
    except: return False

@st.cache_data(ttl=1800)
def get_standings(league_api_code):
    try:
        url = f"https://api.football-data.org/v4/competitions/{league_api_code}/standings"
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        if "standings" in data:
            return data["standings"][0]["table"]
        return []
    except: return []

# =========================================
# HEADER
# =========================================

st.markdown("<h1 style='text-align:center;color:#ffd700;'>BIST WAPAMBANAJI AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#8b949e;'>ELITE FOOTBALL AI ENGINE v9.0 PRO</p>", unsafe_allow_html=True)

# =========================================
# SELECTORS (Must be before Sidebar Table)
# =========================================

c1, c2 = st.columns(2)
with c1:
    nation = st.selectbox("🌍 CHAGUA NCHI", list(LEAGUE_MAP.keys()))
with c2:
    league_name = st.selectbox("🏆 CHAGUA LIGI", list(LEAGUE_MAP[nation].keys()))

# Get codes based on selection
csv_code = LEAGUE_MAP[nation][league_name]["csv"]
api_code = LEAGUE_MAP[nation][league_name]["api"]

# =========================================
# SIDEBAR & LIVE TABLE
# =========================================

with st.sidebar:
    st.markdown(f"## 📊 {league_name.upper()} TABLE")
    table = get_standings(api_code)
    if table:
        for team in table[:10]: # Top 10 teams
            st.write(f"{team['position']}. {team['team']['shortName']} ({team['points']} pts)")
    else:
        st.write("Msimamo haupatikani.")

    st.markdown("---")
    st.markdown("## 💰 BANKROLL PROTECTOR")
    daily_limit = st.sidebar.slider("Daily Risk Limit", 10000, 500000, 50000, 5000)
    today_loss = st.sidebar.number_input("Today's Current Loss", min_value=0, value=0, step=5000)

if today_loss >= daily_limit:
    st.error("⛔ MASTER, KAA MBALI NA SIMU! PUMZIKA LEO.")
    st.stop()

# =========================================
# MAIN ENGINE
# =========================================

df = load_league_data(csv_code)

if df is not None:
    teams = sorted(df["HomeTeam"].dropna().unique())
    s1, s2, s3 = st.columns([2,2,1])
    
    with s1: home = st.selectbox("🏠 HOME TEAM", teams)
    with s2: away = st.selectbox("🚀 AWAY TEAM", [x for x in teams if x != home])
    with s3: market_odds = st.number_input("💰 O2.5 ODDS", min_value=1.10, value=1.85, step=0.01)

    if st.button("🎯 RUN AI ANALYSIS"):
        h_data = df[df["HomeTeam"] == home].tail(8)
        a_data = df[df["AwayTeam"] == away].tail(8)

        if len(h_data) < 5 or len(a_data) < 5:
            st.error("⚠️ Data haitoshi.")
            st.stop()

        # Weighted Averages
        w = np.arange(1, len(h_data)+1)
        h_sc = np.average(h_data["FTHG"], weights=w)
        h_con = np.average(h_data["FTAG"], weights=w)
        a_sc = np.average(a_data["FTAG"], weights=w)
        a_con = np.average(a_data["FTHG"], weights=w)

        # Expected Goals
        home_xg = (h_sc + a_con) / 2
        away_xg = (a_sc + h_con) / 2
        total_xg = home_xg + away_xg

        # Poisson Model
        def poisson(lam, k):
            if lam <= 0: return 0
            return ((lam ** k) * exp(-lam)) / factorial(k)

        prob_u25 = sum(poisson(home_xg, i) * poisson(away_xg, j) for i in range(3) for j in range(3) if i + j < 3)
        prob_o25 = 1 - prob_u25
        prob_btts = (1 - poisson(home_xg, 0)) * (1 - poisson(away_xg, 0))

        # Filters
        revenge = True if h_data["FTAG"].iloc[-1] >= 3 or a_data["FTHG"].iloc[-1] >= 3 else False
        if (h_data["FTAG"] == 0).mean() > 0.45: prob_btts -= 0.08
        if (a_data["FTHG"] == 0).mean() > 0.45: prob_btts -= 0.08

        # Intensity (Shots)
        h_shots = h_data["HS"].mean() if "HS" in h_data.columns else 10
        a_shots = a_data["AS"].mean() if "AS" in a_data.columns else 8
        intensity = h_shots + a_shots

        # Form & Volatility
        volatility = (np.std(h_data["FTHG"]) + np.std(a_data["FTAG"])) / 2
        
        # Display Analysis
        st.markdown("<div class='section-title'>📊 MATCH ANALYSIS</div>", unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4)
        r1.markdown(f"<div class='card'><p class='small'>OVER 2.5</p><div class='big-val'>{prob_o25*100:.1f}%</div></div>", unsafe_allow_html=True)
        r2.markdown(f"<div class='card'><p class='small'>BTTS</p><div class='big-val'>{prob_btts*100:.1f}%</div></div>", unsafe_allow_html=True)
        r3.markdown(f"<div class='card'><p class='small'>VOLATILITY</p><div class='big-val'>{volatility:.2f}</div></div>", unsafe_allow_html=True)
        r4.markdown(f"<div class='card'><p class='small'>INTENSITY</p><div class='big-val'>{intensity:.1f}</div></div>", unsafe_allow_html=True)

        # Score & Quality
        score = (2 if prob_o25 > .72 else 0) + (1 if prob_btts > .65 else 0) + (2 if total_xg > 3.1 else 0)
        quality = round((prob_o25*45 + prob_btts*25 + min(total_xg/4,1)*20 + min(intensity/30,1)*10), 1)

        # Final Verdict Display
        st.markdown("<div class='section-title'>🧠 FINAL AI VERDICT</div>", unsafe_allow_html=True)
        if score >= 6 and quality >= 75: col, verdict = "#00ff66", "🔥 GREEN ELITE"
        elif score >= 4: col, verdict = "#ffd700", "⚖️ YELLOW RISK"
        else: col, verdict = "#ff4d4d", "⛔ RED AVOID"

        st.markdown(f"""
            <div class='signal-box' style='border:3px solid {col}; color:{col};'>
            {verdict}<br><br>
            ⭐ QUALITY: {quality}/100<br>
            📈 SCORE: {score}/8
            </div>
        """, unsafe_allow_html=True)

        # Bet Engine Logic
        edge = round((prob_o25 - (1/market_odds))*100, 1)
        if score >= 6 and edge > 5: final_bet = "🔥 FINAL AI BET: OVER 2.5"
        elif prob_btts >= 0.62: final_bet = "⚽ FINAL AI BET: BTTS YES"
        else: final_bet = "⛔ FINAL AI BET: SKIP MATCH"
        
        st.success(final_bet)
        st.info(f"📈 EDGE: {edge}% | 💰 RECOM. STAKE: {min(max(0, edge/2), 10):.1f}%")

else:
    st.error("❌ FAILED TO LOAD FOOTBALL DATA")
