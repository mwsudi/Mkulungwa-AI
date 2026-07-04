import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
from math import exp, factorial

# ===================================================
# BIST WAPAMBANAJI AI - SAFE HARBOR v11.0 (PROFIT DEFENSE)
# ===================================================

st.set_page_config(
    page_title="BIST WAPAMBANAJI AI v11.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================================================
# FOOTBALL-DATA.ORG API CONFIG
# ===================================================
API_KEY = "2493de184054414dae83d3a909d012d0"
HEADERS = {"X-Auth-Token": API_KEY}

# ===================================================
# PREMIUM SHIELD STYLE ENGINE
# ===================================================
st.markdown("""
<style>
.main { background:#0b0f19; color:#e6edf3; }
[data-testid="stSidebar"] { background:#070a13; border-right:2px solid #00ffcc; }
.stButton>button {
    background:linear-gradient(135deg,#00ffcc 0%,#008b8b 100%);
    color:black !important; border:none; border-radius:10px;
    height:3.5em; font-weight:900; width:100%; box-shadow: 0px 4px 15px rgba(0,255,204,0.2);
}
.card {
    background:#121824; padding:20px; border-radius:15px;
    border-top:3px solid #00ffcc; text-align:center; margin-bottom:15px;
}
.big-val { font-size:28px; font-weight:900; color:#00ffcc; }
.small { color:#8b949e; font-size:13px; text-transform: uppercase; font-weight:bold;}
.section-title {
    color:#00ffcc; font-size:22px; font-weight:bold; margin-top:20px;
    margin-bottom:15px; border-left:4px solid #00ffcc; padding-left:10px;
}
.signal-box {
    padding:25px; border-radius:15px; text-align:center;
    font-size:26px; font-weight:900; margin:20px 0; background:#0e1420;
}
</style>
""", unsafe_allow_html=True)

# ===================================================
# ANTI-LOSS DATA FUNCTIONS
# ===================================================
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

@st.cache_data(ttl=3600)
def load_world_cup_data_api():
    try:
        url = "https://api.football-data.org/v4/competitions/WC/matches?status=FINISHED"
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        
        parsed_matches = []
        if "matches" in data:
            for match in data["matches"]:
                if match.get("score") and match["score"].get("fullTime"):
                    parsed_matches.append({
                        "HomeTeam": match["homeTeam"]["name"],
                        "AwayTeam": match["awayTeam"]["name"],
                        "FTHG": match["score"]["fullTime"]["home"],
                        "FTAG": match["score"]["fullTime"]["away"],
                        "HS": 12, "AS": 10
                    })
        return pd.DataFrame(parsed_matches)
    except: return None

def test_api_connection():
    try:
        url = "https://api.football-data.org/v4/competitions/PL"
        r = requests.get(url, headers=HEADERS, timeout=5)
        return r.status_code == 200
    except: return False

@st.cache_data(ttl=1800)
def get_standings(league_api_code):
    try:
        url = f"https://api.football-data.org/v4/competitions/{league_api_code}/standings"
        r = requests.get(url, headers=HEADERS, timeout=5)
        data = r.json()
        if "standings" in data and len(data["standings"]) > 0:
            return data["standings"][0]["table"]
        return []
    except: return []

# ===================================================
# STRATEGIC MAPPING
# ===================================================
LEAGUE_MAP = {
    "ENGLAND": {
        "Premier League": {"csv": "E0", "api": "PL"},
        "Championship": {"csv": "E1", "api": "ELC"}
    },
    "SPAIN": {"La Liga": {"csv": "SP1", "api": "PD"}},
    "ITALY": {"Serie A": {"csv": "I1", "api": "SA"}},
    "GERMANY": {"Bundesliga": {"csv": "D1", "api": "BL1"}},
    "FRANCE": {"Ligue 1": {"csv": "F1", "api": "FL1"}},
    "INTERNATIONAL": {"World Cup": {"csv": "WC", "api": "WC"}}
}

# ===================================================
# UI HEADER
# ===================================================
st.markdown("<h1 style='text-align:center;color:#00ffcc;margin-bottom:0;'>BIST WAPAMBANAJI AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#8b949e;margin-top:0;font-size:14px;'>REAL-WORLD RISK PROTECTION ENGINE • v11.0 PRO</p>", unsafe_allow_html=True)

# ===================================================
# SELECTORS
# ===================================================
c1, c2 = st.columns(2)
with c1: nation = st.selectbox("🌍 CHAGUA NCHI / BARA", list(LEAGUE_MAP.keys()))
with c2: league_name = st.selectbox("🏆 CHAGUA LIGI", list(LEAGUE_MAP[nation].keys()))

csv_code = LEAGUE_MAP[nation][league_name]["csv"]
api_code = LEAGUE_MAP[nation][league_name]["api"]

# ===================================================
# CRITICAL RISK MANAGEMENT SIDEBAR
# ===================================================
with st.sidebar:
    st.markdown(f"### 📊 LIVE TABLE LEADERS")
    live_table = get_standings(api_code)
    if live_table:
        for team in live_table[:6]:
            t_name = team['team'].get('shortName') or team['team'].get('name', 'Unknown')
            st.write(f"**{team['position']}** | {t_name} — `{team.get('points', 0)} PTS`")
    
    st.markdown("---")
    st.markdown("### 🛡️ MWEKESHANO SALAMA (BANKROLL)")
    total_bankroll = st.number_input("Mtaji Wako Kamili (TZS)", min_value=1000, value=50000, step=2000)
    daily_limit = st.slider("Kikomo cha Hasara ya Leo (TZS)", 2000, 50000, 15000, 1000)
    today_loss = st.number_input("Hasara Uliyopata Leo Tayari (TZS)", min_value=0, value=0, step=500)

if today_loss >= daily_limit:
    st.error("⛔ USIWEKE PESA TENA LEO! Umefikia kikomo ulichojiwekea kulinda mtaji wako. Zima simu, kapumzike.")
    st.stop()

# ===================================================
# ANALYSIS EXECUTION
# ===================================================
if csv_code == "WC":
    df = load_world_cup_data_api()
else:
    df = load_league_data(csv_code)

if df is not None and not df.empty:
    teams = sorted(df["HomeTeam"].dropna().unique())
    s1, s2, s3 = st.columns([2, 2, 1])
    
    with s1: home = st.selectbox("🏠 NYUMBANI (HOME)", teams)
    with s2: away = st.selectbox("🚀 UGENINI (AWAY)", [x for x in teams if x != home])
    with s3: market_odds = st.number_input("💰 ODDS ZA NYUMBA YA BET (O2.5)", min_value=1.10, value=1.85, step=0.01)

    if st.button("🎯 ANZA UCHAMBUZI WA UHAKIKA"):
        # Kuchuja fomu ya nyumbani na ugenini pekee ili kupata uhalisia wa uwanja
        h_data = df[df["HomeTeam"] == home].tail(6)
        a_data = df[df["AwayTeam"] == away].tail(6)
        
        # Mfumo wa dharura kama timu haina mechi za kutosha
        if len(h_data) < 3 or len(a_data) < 3:
            h_data = df[(df["HomeTeam"] == home) | (df["AwayTeam"] == home)].tail(6)
            a_data = df[(df["HomeTeam"] == away) | (df["AwayTeam"] == away)].tail(6)

        if len(h_data) < 3 or len(a_data) < 3:
            st.error("⚠️ DATA HAZITOSHI: Timu hizi hazina rekodi za kutosha msimu huu. Skip mechi hii kwa usalama!")
            st.stop()

        # Uzito wa Mechi (Mechi za hivi karibuni zinapewa uzito mkubwa zaidi)
        w_h = np.arange(1, len(h_data) + 1)
        w_a = np.arange(1, len(a_data) + 1)
        
        h_sc = np.average(h_data["FTHG"], weights=w_h)
        h_con = np.average(h_data["FTAG"], weights=w_h)
        a_sc = np.average(a_data["FTAG"], weights=w_a)
        a_con = np.average(a_data["FTHG"], weights=w_a)

        # Expected Goals Calculations
        home_xg = (h_sc + a_con) / 2
        away_xg = (a_sc + h_con) / 2
        total_xg = home_xg + away_xg

        def poisson(lam, k):
            if lam <= 0: return 0
            return ((lam ** k) * exp(-lam)) / factorial(k)

        prob_u25 = sum(poisson(home_xg, i) * poisson(away_xg, j) for i in range(3) for j in range(3) if i + j < 3)
        prob_o25 = 1 - prob_u25
        prob_btts = (1 - poisson(home_xg, 0)) * (1 - poisson(away_xg, 0))

        # Market Advantage Calculator
        fair_odds_o25 = 1 / prob_o25 if prob_o25 > 0 else 99
        edge = (prob_o25 - (1 / market_odds)) * 100

        # UI Visuals
        st.markdown("<div class='section-title'>📊 VIPIMO VYA RISKI NA HESABU</div>", unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4)
        r1.markdown(f"<div class='card'><p class='small'>Uwezekano wa Over 2.5</p><div class='big-val'>{prob_o25*100:.1f}%</div></div>", unsafe_allow_html=True)
        r2.markdown(f"<div class='card'><p class='small'>Odds Stahiki za AI</p><div class='big-val'>@{fair_odds_o25:.2f}</div></div>", unsafe_allow_html=True)
        r3.markdown(f"<div class='card'><p class='small'>Uwezekano wa BTTS</p><div class='big-val'>{prob_btts*100:.1f}%</div></div>", unsafe_allow_html=True)
        r4.markdown(f"<div class='card'><p class='small'>Faida Yako (Edge)</p><div class='big-val' style='color:{'#00ffcc' if edge > 3.0 else '#ff4d4d'};'>{edge:+.1f}%</div></div>", unsafe_allow_html=True)

        # RIGID VERDICT DEPLOYMENT (Hapa ndio tunalinda hela)
        # Mechi inakubaliwa TU kama asilimia ya AI ipo juu ya 65% NA tuna faida ya zaidi ya 3% dhidi ya kampuni
        if edge > 3.0 and prob_o25 > 0.65:
            col, verdict = "#00ffcc", "✅ MAZINGIRA SALAMA - THAMANI IPO JUU"
            
            # Strict 0.15 Fractional Kelly Criterion
            b = market_odds - 1
            p = prob_o25
            q = 1 - p
            kelly_f = ((b * p) - q) / b
            
            # Tunachukua 15% tu ya Kelly ili kuzuia kupoteza mtaji mkubwa kwa mpigo mmoja
            safe_stake_percent = max(0.0, kelly_f * 0.15) * 100
            suggested_stake = (safe_stake_percent / 100) * total_bankroll
            
            final_action = f"🔥 MKAKATI: WEKA OVER 2.5 GOALS"
            money_action = f"💰 KIWANGO CHA MKINGA: Weka {safe_stake_percent:.1f}% tu ya mtaji wako (= {suggested_stake:,.0f} TZS)"
        else:
            col, verdict = "#ff4d4d", "⛔ HATARI KUBWA - USIWEKE PESA!"
            final_action = "🚨 MKAKATI: SKIP MECHI HII. Makampuni ya bet wameweka mtego kwenye odds."
            money_action = "💰 KIWANGO CHA MKINGA: Weka 0 TZS (Linda mtaji wako kwa ajili ya kesho)"

        st.markdown(f"""
            <div class='signal-box' style='border:3px solid {col}; color:{col};'>
            {verdict}<br><br>
            📉 ODDS ZA KAMPUNI: @{market_odds}<br>
            📈 ODDS ZA AI: @{fair_odds_o25:.2f}
            </div>
        """, unsafe_allow_html=True)

        if edge > 3.0 and prob_o25 > 0.65:
            st.success(final_action)
            st.warning(money_action)
        else:
            st.error(final_action)
            st.info(money_action)

else:
    st.error("❌ IMESHINDWA KUUNGANISHA DATABASE.")
