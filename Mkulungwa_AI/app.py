import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
from math import exp, factorial

# ==================================================
# BIST WAPAMBANAJI AI - ELITE 2026 v7.0 ULTRA PRO
# ==================================================

st.set_page_config(
    page_title="BIST WAPAMBANAJI AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# STYLE ENGINE
# ==================================================

st.markdown("""
<style>

.main{
    background-color:#0d1117;
    color:#e6edf3;
}

[data-testid="stSidebar"]{
    background:#0b0e14;
    border-right:2px solid #ffd700;
}

.stButton>button{
    background:linear-gradient(135deg,#ffd700 0%,#b8860b 100%);
    color:black !important;
    border:none;
    border-radius:10px;
    height:3.5em;
    font-weight:900;
    width:100%;
    letter-spacing:1px;
    transition:0.3s;
}

.stButton>button:hover{
    transform:scale(1.02);
    box-shadow:0 0 20px rgba(255,215,0,0.4);
}

.card{
    background:#161b22;
    padding:25px;
    border-radius:15px;
    border:1px solid #30363d;
    border-left:5px solid #ffd700;
    text-align:center;
    margin-bottom:20px;
}

.big-val{
    font-size:30px;
    font-weight:900;
    color:#ffd700;
}

.small{
    color:#8b949e;
    font-size:14px;
}

.section-title{
    color:#ffd700;
    font-size:24px;
    font-weight:bold;
    margin-top:25px;
    margin-bottom:15px;
    border-bottom:2px solid #ffd700;
    padding-bottom:10px;
}

.signal-box{
    padding:30px;
    border-radius:20px;
    text-align:center;
    font-size:30px;
    font-weight:900;
    margin:20px 0;
    background:#0d1117;
}

.h2h-box{
    background:#161b22;
    padding:12px;
    border-radius:10px;
    border:1px solid #30363d;
    margin-bottom:10px;
    display:flex;
    justify-content:space-between;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# LEAGUES
# ==================================================

LEAGUE_MAP = {
    "ENGLAND": {
        "Premier League": "E0",
        "Championship": "E1"
    },

    "SPAIN": {
        "La Liga": "SP1",
        "La Liga 2": "SP2"
    },

    "ITALY": {
        "Serie A": "I1",
        "Serie B": "I2"
    },

    "GERMANY": {
        "Bundesliga": "D1",
        "Bundesliga 2": "D2"
    },

    "FRANCE": {
        "Ligue 1": "F1",
        "Ligue 2": "F2"
    },

    "NETHERLANDS": {
        "Eredivisie": "N1"
    },

    "PORTUGAL": {
        "Liga Portugal": "P1"
    },

    "TURKEY": {
        "Super Lig": "T1"
    }
}

# ==================================================
# CACHE SYSTEM
# ==================================================

@st.cache_data(ttl=3600)
def load_league_data(code):

    for season in ["2526", "2425"]:

        try:
            url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"

            r = requests.get(url, timeout=7)

            if r.status_code == 200:
                return pd.read_csv(StringIO(r.text))

        except:
            continue

    return None

# ==================================================
# SESSION CACHE
# ==================================================

if "data_cache" not in st.session_state:
    st.session_state.data_cache = {}

# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.markdown(
        "<h2 style='color:#ffd700;'>🛰️ BIST SYNC</h2>",
        unsafe_allow_html=True
    )

    st.info("Refresh kupata latest football data.")

    if st.button("🔄 REFRESH DATABASE"):

        loaded = 0

        with st.spinner("Loading football data..."):

            for nation, leagues in LEAGUE_MAP.items():

                for league_name, code in leagues.items():

                    df = load_league_data(code)

                    if df is not None:

                        st.session_state.data_cache[code] = df
                        loaded += 1

        st.success(f"{loaded} leagues synced!")

# ==================================================
# HEADER
# ==================================================

st.markdown(
    "<h1 style='text-align:center;color:#ffd700;'>BIST WAPAMBANAJI AI</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:#8b949e;'>ULTRA PRO FOOTBALL AI ENGINE v7.0</p>",
    unsafe_allow_html=True
)

# ==================================================
# SELECTORS
# ==================================================

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

# ==================================================
# AUTO LOAD
# ==================================================

if code not in st.session_state.data_cache:

    auto_df = load_league_data(code)

    if auto_df is not None:
        st.session_state.data_cache[code] = auto_df

# ==================================================
# MAIN ENGINE
# ==================================================

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

    # ==================================================
    # RUN ANALYSIS
    # ==================================================

    if st.button("🎯 RUN AI ANALYSIS"):

        h_data = df[df["HomeTeam"] == home].tail(8)
        a_data = df[df["AwayTeam"] == away].tail(8)

        if len(h_data) < 5 or len(a_data) < 5:

            st.error("⚠️ Data haitoshi kufanya analysis.")
            st.stop()

        # ==================================================
        # WEIGHT ENGINE
        # ==================================================

        w = np.arange(1, len(h_data) + 1)

        h_adv = 1.10 if nation in ["ENGLAND", "GERMANY"] else 1.05

        h_sc = np.average(h_data["FTHG"], weights=w) * h_adv
        h_con = np.average(h_data["FTAG"], weights=w)

        a_sc = np.average(a_data["FTAG"], weights=w)
        a_con = np.average(a_data["FTHG"], weights=w)

        home_xg = (h_sc + a_con) / 2
        away_xg = (a_sc + h_con) / 2

        total_xg = home_xg + away_xg

        # ==================================================
        # POISSON ENGINE
        # ==================================================

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

        # ==================================================
        # CLEAN SHEET FILTER
        # ==================================================

        if (h_data["FTAG"] == 0).mean() > 0.45:
            prob_btts -= 0.08

        if (a_data["FTHG"] == 0).mean() > 0.45:
            prob_btts -= 0.08

        # ==================================================
        # INTENSITY ENGINE
        # ==================================================

        intensity = (
            (h_data["HS"].mean() if "HS" in h_data.columns else 10)
            +
            (a_data["AS"].mean() if "AS" in a_data.columns else 8)
        )

        if intensity > 25:
            prob_o25 += 0.04

        elif intensity < 18:
            prob_o25 -= 0.04

        # ==================================================
        # SHOT ACCURACY FILTER
        # ==================================================

        try:

            home_accuracy = (
                h_data["HST"].mean() /
                h_data["HS"].mean()
            )

            away_accuracy = (
                a_data["AST"].mean() /
                a_data["AS"].mean()
            )

            accuracy = (home_accuracy + away_accuracy) / 2

            if accuracy < 0.28:
                prob_o25 -= 0.05

        except:
            accuracy = 0.30

        # ==================================================
        # LIMITS
        # ==================================================

        prob_o25 = min(max(prob_o25, 0.05), 0.95)
        prob_btts = min(max(prob_btts, 0.05), 0.95)

        # ==================================================
        # FORM ENGINE
        # ==================================================

        form = 0

        if h_data["FTHG"].tail(5).mean() >= 1.5:
            form += 1

        if a_data["FTAG"].tail(5).mean() >= 1.2:
            form += 1

        # ==================================================
        # SCORE ENGINE
        # ==================================================

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
            h_data["FTHG"].iloc[-1]
            +
            h_data["FTAG"].iloc[-1]
        ) > 2:
            score += 1

        score += form

        # ==================================================
        # H2H FILTER
        # ==================================================

        h2h = df[
            (
                (df["HomeTeam"] == home)
                &
                (df["AwayTeam"] == away)
            )
            |
            (
                (df["HomeTeam"] == away)
                &
                (df["AwayTeam"] == home)
            )
        ].tail(5)

        if not h2h.empty:

            h2h_goals = h2h["FTHG"] + h2h["FTAG"]

            if len(h2h_goals) >= 3:

                if h2h_goals.mean() < 2.2:
                    score -= 1

        # ==================================================
        # QUALITY ENGINE
        # ==================================================

        quality = round(

            (
                prob_o25 * 45
                +
                prob_btts * 25
                +
                min(total_xg / 4, 1) * 20
                +
                min(intensity / 30, 1) * 10
            ),

            1
        )

        # ==================================================
        # RED FLAG FILTER
        # ==================================================

        if (
            (prob_o25 > 0.78 and intensity < 18)
            or
            (total_xg < 2.3)
            or
            (prob_btts < 0.45 and prob_o25 > 0.75)
        ):

            score = max(score - 2, 0)
            quality = max(quality - 10, 0)

        # ==================================================
        # ODDS TRAP FILTER
        # ==================================================

        if prob_o25 > 0.75 and market_odds > 2.20:

            score = max(score - 2, 0)
            quality = max(quality - 12, 0)

        # ==================================================
        # EDGE
        # ==================================================

        edge = round(
            (
                prob_o25 - (1 / market_odds)
            ) * 100,
            1
        )

        # ==================================================
        # UI
        # ==================================================

        st.markdown(
            "<div class='section-title'>📊 MATCH ANALYSIS</div>",
            unsafe_allow_html=True
        )

        r1, r2, r3 = st.columns(3)

        with r1:

            st.markdown(
                f"""
                <div class='card'>
                <p class='small'>GOALS</p>
                <div class='big-val'>
                {'🟢 OVER 2.5' if prob_o25 > 0.70 else ('🟡 OVER 1.5' if prob_o25 > 0.58 else '🔴 SKIP')}
                </div>
                <p class='small'>{prob_o25*100:.1f}% Probability</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with r2:

            st.markdown(
                f"""
                <div class='card'>
                <p class='small'>BTTS</p>
                <div class='big-val'>
                {'🟢 YES' if prob_btts > 0.65 else ('🟡 MAYBE' if prob_btts > 0.55 else '🔴 NO')}
                </div>
                <p class='small'>{prob_btts*100:.1f}% Probability</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        t_corners = (
            (h_data["HC"].mean() if "HC" in h_data.columns else 5)
            +
            (a_data["AC"].mean() if "AC" in a_data.columns else 4)
        )

        with r3:

            st.markdown(
                f"""
                <div class='card'>
                <p class='small'>CORNERS</p>
                <div class='big-val'>
                {'🟢 O9.5' if t_corners > 10 else '🟡 O8.5'}
                </div>
                <p class='small'>Avg: {t_corners:.1f}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ==================================================
        # VERDICT
        # ==================================================

        st.markdown(
            "<div class='section-title'>🧠 FINAL AI VERDICT</div>",
            unsafe_allow_html=True
        )

        if (
            score >= 7
            and quality >= 80
            and prob_o25 >= 0.78
            and intensity >= 21
            and edge >= 4
        ):

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

        st.markdown(
            f"""
            <div class='signal-box'
            style='border:3px solid {col};color:{col};'>

            {verdict}

            <br>

            <span style='font-size:18px;color:#8b949e;'>
            Battle Score: {score}/9
            </span>

            </div>
            """,
            unsafe_allow_html=True
        )

        # ==================================================
        # FINAL BET ENGINE
        # ==================================================

        draw_risk = abs(home_xg - away_xg)

        if draw_risk < 0.22 and total_xg < 2.4:

            final_bet = "🤝 DRAW / UNDER 2.5"

        elif edge < 1:

            final_bet = "⛔ NO VALUE (SKIP)"

        elif score >= 7 and edge > 5:

            final_bet = "🔥 OVER 2.5"

        elif score >= 5 and prob_o25 >= 0.65:

            final_bet = "✅ OVER 1.5"

        elif prob_btts >= 0.62 and intensity >= 20:

            final_bet = "⚽ BTTS YES"

        else:

            final_bet = "⛔ SKIP MATCH"

        st.success(f"FINAL AI BET: {final_bet}")

        # ==================================================
        # FINANCIALS
        # ==================================================

        side = (
            "🏠 HOME 1X"
            if home_xg > away_xg + 0.4
            else
            (
                "🚀 AWAY X2"
                if away_xg > home_xg + 0.4
                else
                "🤝 DRAW / TIGHT"
            )
        )

        kelly = (
            (
                (prob_o25 * market_odds) - 1
            )
            /
            (market_odds - 1)
        ) if market_odds > 1 else 0

        safe_k = min(max(0, kelly * 100 / 5), 10)

        st.info(
            f"""
🏆 SIDE: {side}

⭐ QUALITY: {quality}/100

📈 EDGE: {edge}%

🎯 ACCURACY: {accuracy:.2f}
"""
        )

        st.warning(
            f"💰 RECOMMENDED STAKE: {safe_k:.1f}% of Bankroll"
        )

        # ==================================================
        # H2H DISPLAY
        # ==================================================

        st.markdown(
            "<div class='section-title'>📜 H2H HISTORY</div>",
            unsafe_allow_html=True
        )

        if not h2h.empty:

            for _, r in h2h.iterrows():

                st.markdown(
                    f"""
                    <div class='h2h-box'>

                    <span>{r['HomeTeam']}</span>

                    <b style='color:#ffd700;'>
                    {r['FTHG']} - {r['FTAG']}
                    </b>

                    <span>{r['AwayTeam']}</span>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:
            st.write("No recent H2H records found.")

else:

    st.warning(
        "⚠️ Database empty. Click REFRESH DATABASE."
    )
