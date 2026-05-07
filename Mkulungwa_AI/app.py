import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from io import StringIO
from math import exp, factorial

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="MKULUNGWA AI MASTER",
    layout="wide"
)

# =====================================
# STYLE
# =====================================

st.markdown("""
<style>

.main{
    background:#0E1117;
    color:white;
}

.stButton>button{
    background:linear-gradient(135deg,#00ff66,#004d1a);
    color:white;
    border:none;
    border-radius:12px;
    height:3.2em;
    width:100%;
    font-weight:bold;
}

.card{
    background:#161B22;
    padding:20px;
    border-radius:15px;
    border-top:4px solid #00ff66;
    text-align:center;
    margin-bottom:15px;
}

.big{
    font-size:30px;
    font-weight:900;
    color:#00ff66;
}

.small{
    color:#cccccc;
}

.advice{
    background:#101820;
    border-left:5px solid #00ff66;
    padding:15px;
    margin-top:10px;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# LEAGUES
# =====================================

LEAGUE_MAP = {
    "ENGLAND": "E0",
    "SPAIN": "SP1",
    "ITALY": "I1",
    "GERMANY": "D1",
    "FRANCE": "F1",
    "NETHERLANDS": "N1",
    "PORTUGAL": "P1",
    "BELGIUM": "B1",
    "SCOTLAND": "SC0",
    "TURKEY": "T1"
}

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.title("🌍 GLOBAL DATABASE")

    if st.button("🔄 REFRESH DATABASE"):

        with st.spinner("Loading leagues..."):

            for name, code in LEAGUE_MAP.items():

                try:

                    url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"

                    r = requests.get(url, timeout=15)

                    if r.status_code == 200:

                        with open(f"{code}.csv", "wb") as f:
                            f.write(r.content)

                except:
                    pass

        st.success("ALL LEAGUES UPDATED!")

# =====================================
# TITLE
# =====================================

st.markdown("""
<h1 style='text-align:center;color:#00ff66;'>
MKULUNGWA AI MASTER V30
</h1>
""", unsafe_allow_html=True)

# =====================================
# LEAGUE SELECT
# =====================================

league = st.selectbox(
    "🌍 SELECT LEAGUE",
    list(LEAGUE_MAP.keys())
)

code = LEAGUE_MAP[league]

# =====================================
# LOAD DATA
# =====================================

if os.path.exists(f"{code}.csv"):

    df = pd.read_csv(f"{code}.csv")

    teams = sorted(df["HomeTeam"].dropna().unique())

    home_team = st.selectbox(
        "🏠 HOME TEAM",
        teams
    )

    away_team = st.selectbox(
        "🚀 AWAY TEAM",
        [x for x in teams if x != home_team]
    )

    # =====================================
    # RUN AI
    # =====================================

    if st.button("🎯 RUN MASTER AI"):

        # LAST MATCHES

        h_home = df[df["HomeTeam"] == home_team].tail(8)
        a_away = df[df["AwayTeam"] == away_team].tail(8)

        # H2H

        h2h = df[
            (
                (df["HomeTeam"] == home_team)
                &
                (df["AwayTeam"] == away_team)
            )
            |
            (
                (df["HomeTeam"] == away_team)
                &
                (df["AwayTeam"] == home_team)
            )
        ].tail(5)

        # WEIGHTS

        weights = np.array([1,2,3,4,5,6,7,8])

        # HOME FORM

        h_scored = np.average(
            h_home["FTHG"],
            weights=weights[-len(h_home):]
        )

        h_conceded = np.average(
            h_home["FTAG"],
            weights=weights[-len(h_home):]
        )

        # AWAY FORM

        a_scored = np.average(
            a_away["FTAG"],
            weights=weights[-len(a_away):]
        )

        a_conceded = np.average(
            a_away["FTHG"],
            weights=weights[-len(a_away):]
        )

        # EXPECTED GOALS

        home_xg = (h_scored + a_conceded) / 2
        away_xg = (a_scored + h_conceded) / 2

        total_xg = home_xg + away_xg

        # =====================================
        # POISSON
        # =====================================

        def poisson(lam, k):
            return (lam**k * exp(-lam)) / factorial(k)

        # OVER 2.5

        prob_under25 = 0

        for i in range(3):
            for j in range(3):

                if i + j < 3:

                    prob_under25 += (
                        poisson(home_xg, i)
                        *
                        poisson(away_xg, j)
                    )

        prob_over25 = 1 - prob_under25

        # BTTS

        prob_btts = (
            (1 - poisson(home_xg,0))
            *
            (1 - poisson(away_xg,0))
        )

        # =====================================
        # CORNERS
        # =====================================

        avg_hc = (
            h_home["HC"].mean()
            if "HC" in h_home.columns
            else 5
        )

        avg_ac = (
            a_away["AC"].mean()
            if "AC" in a_away.columns
            else 4
        )

        total_corners = avg_hc + avg_ac

        # =====================================
        # GOAL PICK
        # =====================================

        if prob_over25 > 0.70:
            goal_pick = "OVER 2.5"

        elif prob_over25 > 0.50:
            goal_pick = "OVER 1.5"

        else:
            goal_pick = "UNDER 3.5"

        # =====================================
        # CORNER PICK
        # =====================================

        if total_corners > 10:
            corner_pick = "OVER 9.5"

        elif total_corners > 8:
            corner_pick = "OVER 8.5"

        else:
            corner_pick = "OVER 7.5"

        # =====================================
        # DOUBLE CHANCE
        # =====================================

        if home_xg > away_xg + 0.5:
            dc_pick = "1X"

        elif away_xg > home_xg + 0.5:
            dc_pick = "X2"

        else:
            dc_pick = "12"

        # =====================================
        # BTTS PICK
        # =====================================

        if prob_btts > 0.60:
            btts_pick = "BTTS YES"

        elif prob_btts > 0.45:
            btts_pick = "BTTS RISKY"

        else:
            btts_pick = "BTTS NO"

        # =====================================
        # FIRST HALF
        # =====================================

        first_half_xg = total_xg * 0.45

        if first_half_xg > 1.2:
            fh_pick = "OVER 1.5 HT"

        elif first_half_xg > 0.7:
            fh_pick = "OVER 0.5 HT"

        else:
            fh_pick = "UNDER 1.5 HT"

        # =====================================
        # CORRECT SCORE
        # =====================================

        home_goals = round(home_xg)
        away_goals = round(away_xg)

        correct_score = f"{home_goals}-{away_goals}"

        # =====================================
        # CONFIDENCE
        # =====================================

        confidence = round(
            (
                (prob_over25 * 100)
                +
                (prob_btts * 100)
            ) / 2
        )

        # =====================================
        # RISK LEVEL
        # =====================================

        if confidence >= 80:
            risk_level = "🟢 LOW RISK"

        elif confidence >= 65:
            risk_level = "🟡 MEDIUM RISK"

        else:
            risk_level = "🔴 HIGH RISK"

        # =====================================
        # SAFE COMBO
        # =====================================

        safe_combo = f"""
        ✅ {goal_pick}
        ✅ {dc_pick}
        ✅ {corner_pick}
        """

        # =====================================
        # DISPLAY
        # =====================================

        st.markdown("---")

        c1, c2, c3 = st.columns(3)

        with c1:

            st.markdown(f"""
            <div class='card'>
            <h3>⚽ GOALS</h3>
            <div class='big'>{goal_pick}</div>
            <div class='small'>
            Probability: {prob_over25*100:.1f}%
            </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:

            st.markdown(f"""
            <div class='card'>
            <h3>🚩 CORNERS</h3>
            <div class='big'>{corner_pick}</div>
            <div class='small'>
            Expected: {total_corners:.1f}
            </div>
            </div>
            """, unsafe_allow_html=True)

        with c3:

            st.markdown(f"""
            <div class='card'>
            <h3>🏆 DOUBLE CHANCE</h3>
            <div class='big'>{dc_pick}</div>
            <div class='small'>
            Confidence: {confidence}%
            </div>
            </div>
            """, unsafe_allow_html=True)

        # =====================================
        # EXTRA MARKETS
        # =====================================

        x1, x2, x3 = st.columns(3)

        with x1:

            st.markdown(f"""
            <div class='card'>
            <h3>🔥 BTTS</h3>
            <div class='big'>{btts_pick}</div>
            <div class='small'>
            Probability: {prob_btts*100:.1f}%
            </div>
            </div>
            """, unsafe_allow_html=True)

        with x2:

            st.markdown(f"""
            <div class='card'>
            <h3>⏱ FIRST HALF</h3>
            <div class='big'>{fh_pick}</div>
            <div class='small'>
            HT xG: {first_half_xg:.2f}
            </div>
            </div>
            """, unsafe_allow_html=True)

        with x3:

            st.markdown(f"""
            <div class='card'>
            <h3>🎯 CORRECT SCORE</h3>
            <div class='big'>{correct_score}</div>
            <div class='small'>
            AI Prediction
            </div>
            </div>
            """, unsafe_allow_html=True)

        # =====================================
        # ADVICE
        # =====================================

        st.markdown(f"""
        <div class='advice'>
        ✅ SAFE PICK:
        <b>{goal_pick}</b>
        linaonekana salama zaidi.
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='advice'>
        🤖 AI ANALYSIS:
        Mfumo umechambua:
        form,
        attack,
        defense,
        H2H,
        corners,
        na home advantage.
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='advice'>
        💎 SAFE COMBO:
        <br><br>
        {safe_combo}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class='advice'>
        ⚠️ RISK LEVEL:
        <b>{risk_level}</b>
        </div>
        """, unsafe_allow_html=True)

else:

    st.warning("⚠️ Refresh database kwanza.")
