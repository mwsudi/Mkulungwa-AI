import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
from math import exp, factorial

# =========================================
# BIST WAPAMBANAJI AI - ELITE 2026 v5.3
# =========================================

st.set_page_config(
    page_title="BIST WAPAMBANAJI AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# STYLE - WAPAMBANAJI THEME
# =========================================

st.markdown("""
<style>
    .main { background-color:#0d1117; color:#e6edf3; }
    [data-testid="stSidebar"]{ background:#0b0e14; border-right:2px solid #ffd700; }
    
    .stButton>button {
        background: linear-gradient(135deg, #ffd700 0%, #b8860b 100%);
        color: black !important; border: none; border-radius: 8px;
        height: 3.5em; font-weight: 900; width: 100%; letter-spacing: 1px;
        transition: 0.4s; box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0px 0px 20px rgba(255, 215, 0, 0.4); }

    .card {
        background:#161b22; padding:25px; border-radius:15px;
        border: 1px solid #30363d; border-left: 5px solid #ffd700;
        text-align:center; margin-bottom:20px;
    }
    .big-val { font-size:32px; font-weight:900; color:#ffd700; text-shadow: 2px 2px #000; }
    .small { color:#8b949e; font-size:14px; text-transform: uppercase; }
    
    .section-title {
        color:#ffd700; font-size:26px; font-weight:bold;
        margin-top:25px; margin-bottom:15px; border-bottom:3px solid #ffd700;
        padding-bottom:10px; width: fit-content;
    }
    .signal-box {
        padding:30px; border-radius:20px; text-align:center;
        font-size:32px; font-weight:900; margin:25px 0;
        background: #0d1117; box-shadow: inset 0 0 15px rgba(255,255,255,0.05);
    }
    .h2h-box {
        background:#0d1117; padding:15px; border-radius:10px;
        border:1px solid #30363d; margin-bottom:10px;
        display:flex; justify-content:space-between; align-items: center;
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
# SIDEBAR - BIST SYNC
# =========================================

with st.sidebar:
    st.markdown("<h2 style='color:#ffd700;'>🛰️ BIST SYNC</h2>", unsafe_allow_html=True)
    st.write("---")
    st.info("Wapambanaji, bofya hapa kupata data mpya ya masoko.")
    
    if st.button("🔄 REFRESH BIST DATA"):
        loaded = 0
        with st.spinner("Kupata Data za Wapambanaji..."):
            for nation, leagues in LEAGUE_MAP.items():
                for league_name, code in leagues.items():
                    try:
                        for season in ["2526", "2425"]:
                            url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
                            r = requests.get(url, timeout=5)
                            if r.status_code == 200:
                                st.session_state.data_cache[code] = pd.read_csv(StringIO(r.text))
                                loaded += 1
                                break
                    except: pass
        st.success(f"Ligi {loaded} zimesawazishwa!")

# =========================================
# MAIN HEADER
# =========================================

st.markdown("<h1 style='text-align:center;color:#ffd700; font-size: 50px;'>BIST WAPAMBANAJI AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#8b949e; letter-spacing: 2px;'>ULTIMATE BATTLEFIELD PREDICTION ENGINE v5.3</p>", unsafe_allow_html=True)

# =========================================
# SELECTORS
# =========================================

c1, c2 = st.columns(2)
with c1: nation = st.selectbox("🌍 CHAGUA NCHI", list(LEAGUE_MAP.keys()))
with c2: league_name = st.selectbox("🏆 CHAGUA LIGI", list(LEAGUE_MAP[nation].keys()))

code = LEAGUE_MAP[nation][league_name]

if code in st.session_state.data_cache:
    df = st.session_state.data_cache[code]
    teams = sorted(df["HomeTeam"].dropna().unique())

    s1, s2, s3 = st.columns([2,2,1])
    with s1: home = st.selectbox("🏠 TIMU YA NYUMBANI", teams)
    with s2: away = st.selectbox("🚀 TIMU YA UGENINI", [x for x in teams if x != home])
    with s3: market_odds = st.number_input("💰 O2.5 MARKET ODDS", min_value=1.10, value=1.85, step=0.01)

    if st.button("🎯 ANZA UCHAMBUZI WA WAPAMBANAJI"):
        h_data = df[df["HomeTeam"] == home].tail(8)
        a_data = df[df["AwayTeam"] == away].tail(8)

        if len(h_data) < 3 or len(a_data) < 3:
            st.error("⚠️ Wapambanaji, data haitoshi kwenye hii mechi!")
            st.stop()

        # 1. FIXED HOME ADVANTAGE (LESS AGGRESSIVE)
        h_adv = 1.10 if nation in ["ENGLAND", "GERMANY"] else 1.05

        # Calculation Engine
        w_h = np.arange(1, len(h_data)+1)
        w_a = np.arange(1, len(a_data)+1)

        h_sc = np.average(h_data["FTHG"], weights=w_h) * h_adv
        h_con = np.average(h_data["FTAG"], weights=w_h)
        a_sc = np.average(a_data["FTAG"], weights=w_a)
        a_con = np.average(a_data["FTHG"], weights=w_a)

        home_xg = (h_sc + a_con) / 2
        away_xg = (a_sc + h_con) / 2
        total_xg = home_xg + away_xg

        def poisson(lam, k):
            return (lam**k * exp(-lam)) / factorial(k) if lam > 0 else 0

        prob_u25 = sum(poisson(home_xg, i) * poisson(away_xg, j) for i in range(3) for j in range(3) if i+j < 3)
        prob_o25 = 1 - prob_u25
        prob_btts = (1 - poisson(home_xg, 0)) * (1 - poisson(away_xg, 0))

        # 2. BALANCED INTENSITY ADJUSTMENT
        h_s = h_data["HS"].mean() if "HS" in h_data.columns else 10
        a_s = a_data["AS"].mean() if "AS" in a_data.columns else 8
        intensity = h_s + a_s

        if intensity > 25:
            prob_o25 += 0.04
        elif intensity < 18:
            prob_o25 -= 0.04

        # 3. SAFE LIMIT PROBABILITY (REALISM FILTER)
        prob_o25 = min(max(prob_o25, 0.05), 0.95)
        prob_btts = min(max(prob_btts, 0.05), 0.95)

        # 4. FORM CONSISTENCY FILTER
        home_recent_goals = h_data["FTHG"].tail(5).mean()
        away_recent_goals = a_data["FTAG"].tail(5).mean()
        form_consistency = 0
        if home_recent_goals >= 1.5: form_consistency += 1
        if away_recent_goals >= 1.2: form_consistency += 1

        # Corners
        t_corners = (h_data["HC"].mean() if "HC" in h_data.columns else 5) + (a_data["AC"].mean() if "AC" in a_data.columns else 4)

        # Signal Scoring
        score = 0
        if prob_o25 > 0.72: score += 2
        if prob_btts > 0.65: score += 1
        if intensity > 22: score += 1
        if total_xg > 3.1: score += 2
        if (h_data["FTHG"].iloc[-1] + h_data["FTAG"].iloc[-1]) > 2: score += 1
        
        # Add Form Consistency to final score
        score += form_consistency

        # Contradiction Check
        if prob_o25 > 0.72 and prob_btts < 0.50: score -= 2

        quality = round((prob_o25*40 + prob_btts*25 + min(total_xg/4, 1)*20 + min(intensity/25, 1)*15), 1)

        # UI Results
        st.markdown("<div class='section-title'>📊 DATA ZA MAPAMBANO</div>", unsafe_allow_html=True)
        r1, r2, r3 = st.columns(3)
        
        g_pick = "🟢 OVER 2.5" if prob_o25 > 0.70 else ("🟡 OVER 1.5" if prob_o25 > 0.58 else "🔴 SKIP")
        b_pick = "🟢 BTTS YES" if prob_btts > 0.65 else ("🟡 BTTS MAYBE" if prob_btts > 0.55 else "🔴 BTTS NO")

        with r1: st.markdown(f"<div class='card'><p class='small'>Magoli</p><div class='big-val'>{g_pick}</div><p class='small'>{prob_o25*100:.1f}%</p></div>", unsafe_allow_html=True)
        with r2: st.markdown(f"<div class='card'><p class='small'>BTTS</p><div class='big-val'>{b_pick}</div><p class='small'>{prob_btts*100:.1f}%</p></div>", unsafe_allow_html=True)
        with r3: st.markdown(f"<div class='card'><p class='small'>Kona</p><div class='big-val'>{'🟢 O9.5' if t_corners > 10 else '🟡 O8.5'}</div><p class='small'>Avg: {t_corners:.1f}</p></div>", unsafe_allow_html=True)

        # FINAL VERDICT & 5. AI BET SUGGESTION
        st.markdown("<div class='section-title'>🧠 MAAMUZI YA BIST</div>", unsafe_allow_html=True)
        if score >= 6 and quality >= 75: 
            col, txt = "#00ff66", "🔥 GREEN ELITE"
            final_bet = "🔥 FINAL AI BET: OVER 2.5"
        elif score >= 5 and quality >= 65: 
            col, txt = "#90ee90", "✅ GREEN SAFE"
            final_bet = "✅ FINAL AI BET: OVER 1.5"
        elif score >= 3: 
            col, txt = "#ffd700", "⚖️ YELLOW RISK"
            final_bet = "⚠️ FINAL AI BET: SMALL STAKE ONLY"
        else: 
            col, txt = "#ff4d4d", "⛔ RED AVOID"
            final_bet = "⛔ FINAL AI BET: SKIP MATCH"

        st.markdown(f"<div class='signal-box' style='border:3px solid {col}; color:{col};'>{txt}<br><span style='font-size:18px; color:#8b949e;'>Battle Score: {score}/9</span></div>", unsafe_allow_html=True)
        
        # Display Final Suggestion with st.success for visibility
        st.success(final_bet)

        st.write(f"**MATCH STRENGTH:** `{quality}/100` | **SIDE PICK:** `{'HOME 1X' if home_xg > away_xg + 0.4 else 'AWAY X2' if away_xg > home_xg + 0.4 else 'DRAW/TIGHT'}`")

        # Money Management
        kelly = (((prob_o25 * market_odds) - 1) / (market_odds - 1)) if market_odds > 1 else 0
        safe_k = min(max(0, kelly * 100 / 5), 10)
        st.warning(f"💰 **USHAURI WA DAU:** Weka **{safe_k:.1f}%** ya mtaji wako.")

        # H2H
        st.markdown("<div class='section-title'>📜 HISTORIA YA MAPAMBANO</div>", unsafe_allow_html=True)
        h2h = df[((df["HomeTeam"] == home) & (df["AwayTeam"] == away)) | ((df["HomeTeam"] == away) & (df["AwayTeam"] == home))].tail(5)
        if not h2h.empty:
            for _, r in h2h.iterrows():
                st.markdown(f"<div class='h2h-box'><span>{r['HomeTeam']}</span><b style='color:#ffd700;'>{r['FTHG']} - {r['FTAG']}</b><span>{r['AwayTeam']}</span></div>", unsafe_allow_html=True)
        else: st.write("Hakuna historia ya karibuni.")

else:
    st.warning("Wapambanaji, Database iko wazi. Bofya REFRESH hapo pembeni!")
