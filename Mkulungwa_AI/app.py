import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
from math import exp, factorial
from datetime import datetime

# =========================================
# BIST WAPAMBANAJI AI - ELITE 2026 v7.0 PRO
# =========================================

st.set_page_config(
    page_title="BIST WAPAMBANAJI AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# STYLE ENGINE
# =========================================

st.markdown("""
<style>
.main {
    background-color:#0d1117;
    color:#e6edf3;
}

[data-testid="stSidebar"]{
    background:#0b0e14;
    border-right:2px solid #ffd700;
}

.stButton>button {
    background: linear-gradient(135deg,#ffd700 0%,#b8860b 100%);
    color:black !important;
    border:none;
    border-radius:10px;
    height:3.5em;
    font-weight:900;
    width:100%;
    letter-spacing:1px;
    transition:0.3s;
}

.stButton>button:hover {
    transform:scale(1.02);
    box-shadow:0 0 20px rgba(255,215,0,0.4);
}

.card {
    background:#161b22;
    padding:25px;
    border-radius:15px;
    border:1px solid #30363d;
    border-left:5px solid #ffd700;
    text-align:center;
    margin-bottom:20px;
}

.big-val {
    font-size:30px;
    font-weight:900;
    color:#ffd700;
}

.small {
    color:#8b949e;
    font-size:14px;
}

.section-title {
    color:#ffd700;
    font-size:24px;
    font-weight:bold;
    margin-top:25px;
    margin-bottom:15px;
    border-bottom:2px solid #ffd700;
    padding-bottom:10px;
}

.signal-box {
    padding:30px;
    border-radius:20px;
    text-align:center;
    font-size:30px;
    font-weight:900;
    margin:20px 0;
    background:#0d1117;
}

.h2h-box {
    background:#161b22;
    padding:12px;
    border-radius:10px;
    border:1px solid #30363d;
    margin-bottom:10px;
    display:flex;
    justify-content:space-between;
}

.metric-box {
    background:#161b22;
    padding:15px;
    border-radius:12px;
    border:1px solid #30363d;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# LEAGUES
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

# =========================================
# LEAGUE PROFILE ENGINE
# =========================================

LEAGUE_STRENGTH = {
    "ENGLAND": 1.05,
    "SPAIN": 1.00,
    "ITALY": 0.96,
    "GERMANY": 1.10,
    "FRANCE": 0.94,
    "NETHERLANDS": 1.15,
    "PORTUGAL": 0.98,
    "TURKEY": 1.03
}

# =========================================
# CACHE SYSTEM
# =========================================

@st.cache_data(ttl=3600)
def load_league_data(code):
    for season in ["2526", "2425"]:
        try:
            url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"

            r = requests.get(url, timeout=8)

            if r.status_code == 200:
                return pd.read_csv(StringIO(r.text))

        except:
            continue

    return None

# =========================================
# SESSION STATE
# =========================================

if "data_cache" not in st.session_state:
    st.session_state.data_cache = {}

if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

# =========================================
# SIDEBAR
# =========================================

with st.sidebar:

    st.markdown(
        "<h2 style='color:#ffd700;'>🛰️ BIST SYNC</h2>",
        unsafe_allow_html=True
    )

    st.info("Refresh kupata football data mpya.")

    if st.button("🔄 REFRESH DATABASE"):

        loaded = 0

        with st.spinner("Loading football data..."):

            for nation, leagues in LEAGUE_MAP.items():

                for name, code in leagues.items():

                    df = load_league_data(code)

                    if df is not None:
                        st.session_state.data_cache[code] = df
                        loaded += 1

        st.success(f"{loaded} leagues synced!")

# =========================================
# HEADER
# =========================================

st.markdown("""
<h1 style='text-align:center;color:#ffd700;'>
BIST WAPAMBANAJI AI
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style='text-align:center;color:#8b949e;'>
ELITE FOOTBALL AI ENGINE v7.0 PRO
</p>
""", unsafe_allow_html=True)

# =========================================
# SELECTORS
# =========================================

c1, c2 = st.columns(2)

with c1:
    nation = st.selectbox(
        "🌍 CHAGUA NCHI",
        list(LEAGUE_MAP.keys())
    )

with c2:
    league_name = st.selectbox(
        "🏆 CHAGUA LIGI",
        list(LEAGUE_MAP[nation].keys())
    )

code = LEAGUE_MAP[nation][league_name]

# =========================================
# AUTO LOAD
# =========================================

if code not in st.session_state.data_cache:

    auto_df = load_league_data(code)

    if auto_df is not None:
        st.session_state.data_cache[code] = auto_df

# =========================================
# MAIN ENGINE
# =========================================

if code in st.session_state.data_cache:

    df = st.session_state.data_cache[code]

    teams = sorted(df["HomeTeam"].dropna().unique())

    s1, s2, s3 = st.columns([2,2,1])

    with s1:
        home = st.selectbox("🏠 HOME TEAM", teams)

    with s2:
        away = st.selectbox(
            "🚀 AWAY TEAM",
            [x for x in teams if x != home]
        )

    with s3:
        market_odds = st.number_input(
            "💰 O2.5 ODDS",
            min_value=1.10,
            value=1.85,
            step=0.01
        )

    if st.button("🎯 RUN AI ANALYSIS"):

        h_data = df[df["HomeTeam"] == home].tail(8)
        a_data = df[df["AwayTeam"] == away].tail(8)

        if len(h_data) < 5 or len(a_data) < 5:
            st.error("⚠️ Data haitoshi.")
            st.stop()

        # =========================================
        # WEIGHTS
        # =========================================

        w_h = np.arange(1, len(h_data)+1)
        w_a = np.arange(1, len(a_data)+1)

        # =========================================
        # HOME ADVANTAGE
        # =========================================

        h_adv = 1.10 if nation in ["ENGLAND", "GERMANY"] else 1.05

        # =========================================
        # ATTACK / DEFENCE
        # =========================================

        h_sc = np.average(
            h_data["FTHG"],
            weights=w_h
        ) * h_adv

        h_con = np.average(
            h_data["FTAG"],
            weights=w_h
        )

        a_sc = np.average(
            a_data["FTAG"],
            weights=w_a
        )

        a_con = np.average(
            a_data["FTHG"],
            weights=w_a
        )

        # =========================================
        # LEAGUE MODIFIER
        # =========================================

        league_mod = LEAGUE_STRENGTH[nation]

        h_sc *= league_mod
        a_sc *= league_mod

        # =========================================
        # EXPECTED GOALS
        # =========================================

        home_xg = (h_sc + a_con) / 2
        away_xg = (a_sc + h_con) / 2

        total_xg = home_xg + away_xg

        # =========================================
        # POISSON
        # =========================================

        def poisson(lam, k):

            if lam <= 0:
                return 0

            return ((lam ** k) * exp(-lam)) / factorial(k)

        prob_u25 = sum(
            poisson(home_xg, i) *
            poisson(away_xg, j)

            for i in range(3)
            for j in range(3)

            if i + j < 3
        )

        prob_o25 = 1 - prob_u25

        prob_btts = (
            (1 - poisson(home_xg, 0)) *
            (1 - poisson(away_xg, 0))
        )

        # =========================================
        # SHOT INTENSITY
        # =========================================

        hs = h_data["HS"].mean() if "HS" in h_data.columns else 10
        ass = a_data["AS"].mean() if "AS" in a_data.columns else 8

        intensity = hs + ass

        if intensity > 25:
            prob_o25 += 0.04

        elif intensity < 18:
            prob_o25 -= 0.04

        # =========================================
        # SHOTS ON TARGET FILTER
        # =========================================

        hst = h_data["HST"].mean() if "HST" in h_data.columns else 4
        ast = a_data["AST"].mean() if "AST" in a_data.columns else 3

        sot = hst + ast

        if sot > 9:
            prob_o25 += 0.05

        elif sot < 6:
            prob_o25 -= 0.05

        # =========================================
        # CLEAN SHEET FILTER
        # =========================================

        home_clean_sheet = (h_data["FTAG"] == 0).mean()
        away_clean_sheet = (a_data["FTHG"] == 0).mean()

        if home_clean_sheet > 0.45:
            prob_btts -= 0.08

        if away_clean_sheet > 0.45:
            prob_btts -= 0.08

        # =========================================
        # CLAMP
        # =========================================

        prob_o25 = min(max(prob_o25, 0.05), 0.95)
        prob_btts = min(max(prob_btts, 0.05), 0.95)

        # =========================================
        # FORM ENGINE
        # =========================================

        home_form = (
            1 if h_data["FTHG"].tail(5).mean() >= 1.5
            else 0
        )

        away_form = (
            1 if a_data["FTAG"].tail(5).mean() >= 1.2
            else 0
        )

        form = home_form + away_form

        # =========================================
        # H2H
        # =========================================

        h2h = df[
            (
                (df["HomeTeam"] == home) &
                (df["AwayTeam"] == away)
            )
            |
            (
                (df["HomeTeam"] == away) &
                (df["AwayTeam"] == home)
            )
        ].tail(5)

        if not h2h.empty:

            h2h_avg = (
                h2h["FTHG"] +
                h2h["FTAG"]
            ).mean()

            if h2h_avg < 2:
                prob_o25 -= 0.05

        # =========================================
        # SCORE ENGINE
        # =========================================

        score = 0

        if prob_o25 > 0.72:
            score += 2

        if prob_btts > 0.65:
            score += 1

        if intensity > 22:
            score += 1

        if total_xg > 3.1:
            score += 2

        if (
            h_data["FTHG"].iloc[-1] +
            h_data["FTAG"].iloc[-1]
        ) > 2:
            score += 1

        score += form

        # =========================================
        # QUALITY ENGINE
        # =========================================

        quality = max(
            0,
            round(
                (prob_o25 * 45) +
                (prob_btts * 25) +
                (min(total_xg/4,1) * 20) +
                (min(intensity/30,1) * 10),
                1
            )
        )

        # =========================================
        # RED FLAGS
        # =========================================

        if (
            (prob_o25 > 0.78 and intensity < 18)
            or
            (total_xg < 2.3)
            or
            (prob_btts < 0.45 and prob_o25 > 0.75)
        ):

            score = max(score - 2, 0)
            quality = max(quality - 10, 0)

        # =========================================
        # VALUE EDGE
        # =========================================

        edge = round(
            (
                prob_o25 -
                (1 / market_odds)
            ) * 100,
            1
        )

        # =========================================
        # FINAL BET ENGINE
        # =========================================

        draw_risk = abs(home_xg - away_xg)

        if score < 3 or quality < 55:
            fb = "⛔ FINAL AI BET: SKIP MATCH"

        elif draw_risk < 0.22 and total_xg < 2.4:
            fb = "🤝 FINAL AI BET: DRAW / UNDER 2.5"

        elif edge < 1:
            fb = "⛔ FINAL AI BET: NO VALUE"

        elif score >= 7 and quality >= 75 and edge > 5:
            fb = "🔥 FINAL AI BET: OVER 2.5"

        elif score >= 5 and prob_o25 >= 0.65:
            fb = "✅ FINAL AI BET: OVER 1.5"

        elif prob_btts >= 0.62 and intensity >= 20:
            fb = "⚽ FINAL AI BET: BTTS YES"

        else:
            fb = "⛔ FINAL AI BET: SKIP MATCH"

        # =========================================
        # VERDICT
        # =========================================

        if score >= 6 and quality >= 75:
            verdict = "🔥 GREEN ELITE"
            col = "#00ff66"

        elif score >= 5 and quality >= 65:
            verdict = "✅ GREEN SAFE"
            col = "#90ee90"

        elif score >= 3:
            verdict = "⚖️ YELLOW RISK"
            col = "#ffd700"

        else:
            verdict = "⛔ RED AVOID"
            col = "#ff4d4d"

        # =========================================
        # CONFIDENCE
        # =========================================

        confidence = (
            "HIGH"
            if quality >= 75
            else (
                "MEDIUM"
                if quality >= 60
                else "LOW"
            )
        )

        # =========================================
        # UI
        # =========================================

        st.markdown(
            "<div class='section-title'>📊 MATCH ANALYSIS</div>",
            unsafe_allow_html=True
        )

        r1, r2, r3, r4 = st.columns(4)

        with r1:

            g_pick = (
                "🟢 OVER 2.5"
                if prob_o25 > 0.70
                else (
                    "🟡 OVER 1.5"
                    if prob_o25 > 0.58
                    else "🔴 SKIP"
                )
            )

            st.markdown(f"""
            <div class='card'>
            <p class='small'>GOALS</p>
            <div class='big-val'>{g_pick}</div>
            <p class='small'>{prob_o25*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

        with r2:

            b_pick = (
                "🟢 YES"
                if prob_btts > 0.65
                else (
                    "🟡 MAYBE"
                    if prob_btts > 0.55
                    else "🔴 NO"
                )
            )

            st.markdown(f"""
            <div class='card'>
            <p class='small'>BTTS</p>
            <div class='big-val'>{b_pick}</div>
            <p class='small'>{prob_btts*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)

        with r3:

            t_corners = (
                (
                    h_data["HC"].mean()
                    if "HC" in h_data.columns
                    else 5
                )
                +
                (
                    a_data["AC"].mean()
                    if "AC" in a_data.columns
                    else 4
                )
            )

            c_pick = (
                "🟢 O9.5"
                if t_corners > 10
                else "🟡 O8.5"
            )

            st.markdown(f"""
            <div class='card'>
            <p class='small'>CORNERS</p>
            <div class='big-val'>{c_pick}</div>
            <p class='small'>{t_corners:.1f}</p>
            </div>
            """, unsafe_allow_html=True)

        with r4:

            st.markdown(f"""
            <div class='card'>
            <p class='small'>CONFIDENCE</p>
            <div class='big-val'>{confidence}</div>
            <p class='small'>{quality}/100</p>
            </div>
            """, unsafe_allow_html=True)

        # =========================================
        # FINAL VERDICT
        # =========================================

        st.markdown(
            "<div class='section-title'>🧠 FINAL AI VERDICT</div>",
            unsafe_allow_html=True
        )

        st.markdown(f"""
        <div class='signal-box'
        style='border:3px solid {col};color:{col};'>

        {verdict}

        <br>

        <span style='font-size:18px;color:#8b949e;'>
        Battle Score: {score}/9
        </span>

        </div>
        """, unsafe_allow_html=True)

        st.success(fb)

        # =========================================
        # SIDE PICK
        # =========================================

        if home_xg > away_xg + 0.4:
            side = "🏠 HOME 1X"

        elif away_xg > home_xg + 0.4:
            side = "🚀 AWAY X2"

        else:
            side = "🤝 DRAW / TIGHT"

        # =========================================
        # KELLY
        # =========================================

        kelly = 0

        if edge > 0 and market_odds > 1:

            kelly = (
                (
                    (prob_o25 * market_odds) - 1
                )
                /
                (market_odds - 1)
            )

        safe_k = min(max(0, kelly * 100 / 5), 10)

        # =========================================
        # INFO BOX
        # =========================================

        st.info(f"""
🏆 SIDE: {side}

⭐ QUALITY: {quality}/100

📈 EDGE: {edge}%

🎯 SHOTS ON TARGET: {sot:.1f}
""")

        st.warning(
            f"💰 RECOMMENDED STAKE: {safe_k:.1f}% of Bankroll"
        )

        # =========================================
        # SAVE PREDICTION
        # =========================================

        st.session_state.prediction_history.append({
            "time": datetime.now().strftime("%H:%M"),
            "match": f"{home} vs {away}",
            "verdict": verdict,
            "bet": fb,
            "quality": quality
        })

        # =========================================
        # PREDICTION HISTORY
        # =========================================

        st.markdown(
            "<div class='section-title'>📁 PREDICTION HISTORY</div>",
            unsafe_allow_html=True
        )

        hist_df = pd.DataFrame(
            st.session_state.prediction_history
        )

        st.dataframe(
            hist_df.tail(10),
            use_container_width=True
        )

        # =========================================
        # H2H
        # =========================================

        st.markdown(
            "<div class='section-title'>📜 H2H HISTORY</div>",
            unsafe_allow_html=True
        )

        if not h2h.empty:

            for _, r in h2h.iterrows():

                st.markdown(f"""
                <div class='h2h-box'>
                <span>{r['HomeTeam']}</span>
                <b style='color:#ffd700;'>
                {r['FTHG']} - {r['FTAG']}
                </b>
                <span>{r['AwayTeam']}</span>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.write("No recent H2H records found.")

else:
    st.warning(
        "⚠️ Database empty. Click REFRESH DATABASE."
    )
