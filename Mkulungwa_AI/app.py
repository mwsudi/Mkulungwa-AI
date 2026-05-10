import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
from math import exp, factorial

# =========================================
# BIST WAPAMBANAJI AI - ELITE 2026 v6.1
# =========================================

st.set_page_config(page_title="BIST WAPAMBANAJI AI", layout="wide", initial_sidebar_state="expanded")

# --- STYLE ENGINE ---
st.markdown("""
<style>
    .main { background-color:#0d1117; color:#e6edf3; }
    [data-testid="stSidebar"]{ background:#0b0e14; border-right:2px solid #ffd700; }
    .stButton>button {
        background: linear-gradient(135deg,#ffd700 0%,#b8860b 100%);
        color:black !important; border:none; border-radius:10px;
        height:3.5em; font-weight:900; width:100%; letter-spacing:1px; transition:0.3s;
    }
    .stButton>button:hover { transform:scale(1.02); }
    .card {
        background:#161b22; padding:25px; border-radius:15px;
        border:1px solid #30363d; border-left:5px solid #ffd700;
        text-align:center; margin-bottom:20px;
    }
    .big-val { font-size:30px; font-weight:900; color:#ffd700; }
    .small { color:#8b949e; font-size:14px; }
    .section-title {
        color:#ffd700; font-size:24px; font-weight:bold; margin-top:25px;
        margin-bottom:15px; border-bottom:2px solid #ffd700; padding-bottom:10px;
    }
    .signal-box {
        padding:30px; border-radius:20px; text-align:center;
        font-size:30px; font-weight:900; margin:20px 0; background:#0d1117;
    }
    .h2h-box {
        background:#161b22; padding:12px; border-radius:10px;
        border:1px solid #30363d; margin-bottom:10px; display:flex; justify-content:space-between;
    }
</style>
""", unsafe_allow_html=True)

# --- LEAGUES ---
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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#ffd700;'>🛰️ BIST SYNC</h2>", unsafe_allow_html=True)
    if st.button("🔄 REFRESH DATABASE"):
        loaded = 0
        with st.spinner("Loading football data..."):
            for nation, leagues in LEAGUE_MAP.items():
                for league_name, code in leagues.items():
                    try:
                        for season in ["2526", "2425"]:
                            url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
                            r = requests.get(url, timeout=6)
                            if r.status_code == 200:
                                st.session_state.data_cache[code] = pd.read_csv(StringIO(r.text))
                                loaded += 1
                                break
                    except: pass
        st.success(f"{loaded} leagues synced!")

# --- HEADER ---
st.markdown("<h1 style='text-align:center;color:#ffd700;'>BIST WAPAMBANAJI AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#8b949e;'>ELITE FOOTBALL AI ENGINE v6.1</p>", unsafe_allow_html=True)

# --- SELECTORS ---
c1, c2 = st.columns(2)
with c1: nation = st.selectbox("🌍 CHAGUA NCHI", list(LEAGUE_MAP.keys()))
with c2: league_name = st.selectbox("🏆 CHAGUA LIGI", list(LEAGUE_MAP[nation].keys()))

code = LEAGUE_MAP[nation][league_name]

if code in st.session_state.data_cache:
    df = st.session_state.data_cache[code]
    teams = sorted(df["HomeTeam"].dropna().unique())
    s1, s2, s3 = st.columns([2,2,1])
    with s1: home = st.selectbox("🏠 HOME TEAM", teams)
    with s2: away = st.selectbox("🚀 AWAY TEAM", [x for x in teams if x != home])
    with s3: market_odds = st.number_input("💰 O2.5 ODDS", min_value=1.10, value=1.85, step=0.01)

    if st.button("🎯 RUN AI ANALYSIS"):
        h_data = df[df["HomeTeam"] == home].tail(8)
        a_data = df[df["AwayTeam"] == away].tail(8)
        if len(h_data) < 5 or len(a_data) < 5:
            st.error("⚠️ Data haitoshi kuchambua Wapambanaji.")
            st.stop()

        # Calculation Engine
        w_h = np.arange(1, len(h_data)+1)
        w_a = np.arange(1, len(a_data)+1)
        h_adv = 1.10 if nation in ["ENGLAND", "GERMANY"] else 1.05
        
        h_sc = np.average(h_data["FTHG"], weights=w_h) * h_adv
        h_con = np.average(h_data["FTAG"], weights=w_h)
        a_sc = np.average(a_data["FTAG"], weights=w_a)
        a_con = np.average(a_data["FTHG"], weights=w_a)

        home_xg, away_xg = (h_sc + a_con) / 2, (a_sc + h_con) / 2
        total_xg = home_xg + away_xg

        def poisson(lam, k): return ((lam**k * exp(-lam)) / factorial(k)) if lam > 0 else 0

        prob_u25 = sum(poisson(home_xg, i) * poisson(away_xg, j) for i in range(3) for j in range(3) if i + j < 3)
        prob_o25, prob_btts = (1 - prob_u25), (1 - poisson(home_xg, 0)) * (1 - poisson(away_xg, 0))

        # Balanced Intensity
        intensity = (h_data["HS"].mean() if "HS" in h_data.columns else 10) + (a_data["AS"].mean() if "AS" in a_data.columns else 8)
        if intensity > 25: prob_o25 += 0.04
        elif intensity < 18: prob_o25 -= 0.04
        
        prob_o25, prob_btts = min(max(prob_o25, 0.05), 0.95), min(max(prob_btts, 0.05), 0.95)

        # Form Consistency
        form_consistency = (1 if h_data["FTHG"].tail(5).mean() >= 1.5 else 0) + (1 if a_data["FTAG"].tail(5).mean() >= 1.2 else 0)
        t_corners = (h_data["HC"].mean() if "HC" in h_data.columns else 5) + (a_data["AC"].mean() if "AC" in a_data.columns else 4)

        # Score Engine
        score = 0
        if prob_o25 > 0.72: score += 2
        if prob_btts > 0.65: score += 1
        if intensity > 22: score += 1
        if total_xg > 3.1: score += 2
        if (h_data["FTHG"].iloc[-1] + h_data["FTAG"].iloc[-1]) > 2: score += 1
        score += form_consistency

        # Quality & Confidence
        quality = round((prob_o25 * 45 + prob_btts * 25 + min(total_xg / 4, 1) * 20 + min(intensity / 30, 1) * 10), 1)
        
        # Display Picks
        st.markdown("<div class='section-title'>📊 MATCH ANALYSIS</div>", unsafe_allow_html=True)
        r1, r2, r3 = st.columns(3)
        with r1: st.markdown(f"<div class='card'><p class='small'>GOALS</p><div class='big-val'>{'🟢 OVER 2.5' if prob_o25 > 0.70 else ('🟡 OVER 1.5' if prob_o25 > 0.58 else '🔴 SKIP')}</div><p class='small'>{prob_o25*100:.1f}% Prob</p></div>", unsafe_allow_html=True)
        with r2: st.markdown(f"<div class='card'><p class='small'>BTTS</p><div class='big-val'>{'🟢 YES' if prob_btts > 0.65 else ('🟡 MAYBE' if prob_btts > 0.55 else '🔴 NO')}</div><p class='small'>{prob_btts*100:.1f}% Prob</p></div>", unsafe_allow_html=True)
        with r3: st.markdown(f"<div class='card'><p class='small'>CORNERS</p><div class='big-val'>{'🟢 O9.5' if t_corners > 10 else '🟡 O8.5'}</div><p class='small'>Avg: {t_corners:.1f}</p></div>", unsafe_allow_html=True)

        # Verdict
        st.markdown("<div class='section-title'>🧠 FINAL AI VERDICT</div>", unsafe_allow_html=True)
        col = "#00ff66" if score >= 6 and quality >= 75 else ("#90ee90" if score >= 5 and quality >= 65 else ("#ffd700" if score >= 3 else "#ff4d4d"))
        txt = "🔥 GREEN ELITE" if score >= 6 and quality >= 75 else ("✅ GREEN SAFE" if score >= 5 and quality >= 65 else ("⚖️ YELLOW RISK" if score >= 3 else "⛔ RED AVOID"))
        st.markdown(f"<div class='signal-box' style='border:3px solid {col};color:{col};'>{txt}<br><span style='font-size:18px;color:#8b949e;'>Battle Score: {score}/9</span></div>", unsafe_allow_html=True)

        # Final Bet Suggestion Logic
        final_bet = "🔥 FINAL AI BET: OVER 2.5" if prob_o25 >= 0.78 else ("✅ FINAL AI BET: OVER 1.5" if prob_o25 >= 0.65 else ("⚽ FINAL AI BET: BTTS YES" if prob_btts >= 0.62 else "⛔ FINAL AI BET: SKIP MATCH"))
        st.success(final_bet)

        # Side Pick & Kelly
        side_pick = "🏠 HOME 1X" if home_xg > away_xg + 0.4 else ("🚀 AWAY X2" if away_xg > home_xg + 0.4 else "🤝 DRAW / TIGHT")
        kelly = (((prob_o25 * market_odds) - 1) / (market_odds - 1)) if market_odds > 1 else 0
        safe_k = min(max(0, kelly * 100 / 5), 10)

        st.info(f"🏆 SIDE PICK: {side_pick} | ⭐ QUALITY: {quality}/100")
        st.warning(f"💰 VALUE EDGE: {((prob_o25 - 1/market_odds)*100):.1f}% | 💵 RECOMMENDED STAKE: {safe_k:.1f}%")

        # H2H History
        st.markdown("<div class='section-title'>📜 H2H HISTORY</div>", unsafe_allow_html=True)
        h2h = df[((df["HomeTeam"] == home) & (df["AwayTeam"] == away)) | ((df["HomeTeam"] == away) & (df["AwayTeam"] == home))].tail(5)
        if not h2h.empty:
            for _, r in h2h.iterrows():
                st.markdown(f"<div class='h2h-box'><span>{r['HomeTeam']}</span><b style='color:#ffd700;'>{r['FTHG']} - {r['FTAG']}</b><span>{r['AwayTeam']}</span></div>", unsafe_allow_html=True)
        else: st.write("No recent H2H encounters found.")
else:
    st.warning("⚠️ Database empty. Click REFRESH DATABASE in Sidebar.")
