import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from math import exp, factorial

# ======================================
# MKULUNGWA AI MASTER V40 PRO
# ======================================

st.set_page_config(
    page_title="MKULUNGWA AI MASTER",
    layout="wide"
)

# ======================================
# STYLE
# ======================================

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
    font-weight:bold;
    width:100%;
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
    font-size:32px;
    font-weight:900;
    color:#00ff66;
}

.small{
    color:#cfcfcf;
}

.advice{
    background:#101820;
    border-left:5px solid #00ff66;
    padding:15px;
    margin-top:10px;
    border-radius:10px;
}

.high{
    color:#00ff66;
    font-weight:bold;
}

.mid{
    color:orange;
    font-weight:bold;
}

.low{
    color:red;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ======================================
# LEAGUES
# ======================================

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

# ======================================
# LEAGUE FACTORS
# ======================================

LEAGUE_GOAL_FACTOR = {
    "ENGLAND": 1.10,
    "SPAIN": 1.00,
    "ITALY": 0.92,
    "GERMANY": 1.15,
    "FRANCE": 0.96,
    "NETHERLANDS": 1.18,
    "PORTUGAL": 0.95,
    "BELGIUM": 1.08,
    "SCOTLAND": 1.05,
    "TURKEY": 1.04
}

# ======================================
# SIDEBAR
# ======================================

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

        st.success("DATABASE UPDATED!")

# ======================================
# TITLE
# ======================================

st.markdown("""
<h1 style='text-align:center;color:#00ff66;'>
MKULUNGWA AI MASTER V40 PRO
</h1>
""", unsafe_allow_html=True)

# ======================================
# SELECT LEAGUE
# ======================================

league = st.selectbox(
    "🌍 SELECT LEAGUE",
    list(LEAGUE_MAP.keys())
)

code = LEAGUE_MAP[league]

# ======================================
# LOAD DATA
# ======================================

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

    # ======================================
    # RUN AI
    # ======================================

    if st.button("🎯 RUN MASTER AI"):

        try:

            # ======================================
            # MATCHES
            # ======================================

            h_home = df[df["HomeTeam"] == home_team].tail(8)
            a_away = df[df["AwayTeam"] == away_team].tail(8)

            if h_home.empty or a_away.empty:
                st.error("Not enough data.")
                st.stop()

            # ======================================
            # H2H
            # ======================================

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

            # ======================================
            # WEIGHTS
            # ======================================

            weights = np.array([1,2,3,4,5,6,7,8])

            # ======================================
            # ATTACK & DEFENSE
            # ======================================

            h_scored = np.average(
                h_home["FTHG"],
                weights=weights[-len(h_home):]
            )

            h_conceded = np.average(
                h_home["FTAG"],
                weights=weights[-len(h_home):]
            )

            a_scored = np.average(
                a_away["FTAG"],
                weights=weights[-len(a_away):]
            )

            a_conceded = np.average(
                a_away["FTHG"],
                weights=weights[-len(a_away):]
            )

            # ======================================
            # FORM INDEX
            # ======================================

            def get_form(matches, home=True):

                points = 0

                for _, row in matches.iterrows():

                    if home:

                        if row["FTHG"] > row["FTAG"]:
                            points += 3

                        elif row["FTHG"] == row["FTAG"]:
                            points += 1

                    else:

                        if row["FTAG"] > row["FTHG"]:
                            points += 3

                        elif row["FTAG"] == row["FTHG"]:
                            points += 1

                return points / (len(matches) * 3)

            home_form = get_form(h_home, True)
            away_form = get_form(a_away, False)

            # ======================================
            # EXPECTED GOALS
            # ======================================

            home_xg = (h_scored + a_conceded) / 2
            away_xg = (a_scored + h_conceded) / 2

            # HOME ADVANTAGE
            home_xg += 0.25

            # LEAGUE FACTOR
            factor = LEAGUE_GOAL_FACTOR.get(league, 1)

            home_xg *= factor
            away_xg *= factor

            # SHOTS ON TARGET BOOST
            if "HST" in h_home.columns:
                home_xg += h_home["HST"].mean() * 0.05

            if "AST" in a_away.columns:
                away_xg += a_away["AST"].mean() * 0.05

            total_xg = home_xg + away_xg

            # ======================================
            # POISSON
            # ======================================

            def poisson(lam, k):
                return (lam**k * exp(-lam)) / factorial(k)

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

            # ======================================
            # BTTS
            # ======================================

            prob_btts = (
                (1 - poisson(home_xg,0))
                *
                (1 - poisson(away_xg,0))
            )

            # ======================================
            # H2H FACTOR
            # ======================================

            if not h2h.empty:

                h2h_goals = (
                    h2h["FTHG"] + h2h["FTAG"]
                ).mean()

            else:
                h2h_goals = 2.5

            # ======================================
            # CORNERS
            # ======================================

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

            # ======================================
            # PICKS
            # ======================================

            if prob_over25 > 0.72:
                goal_pick = "OVER 2.5"

            elif prob_over25 > 0.52:
                goal_pick = "OVER 1.5"

            else:
                goal_pick = "UNDER 3.5"

            # BTTS
            btts_pick = (
                "YES"
                if prob_btts > 0.58
                else "NO"
            )

            # CORNERS
            if total_corners > 10:
                corner_pick = "OVER 9.5"

            elif total_corners > 8:
                corner_pick = "OVER 8.5"

            else:
                corner_pick = "OVER 7.5"

            # WIN SIDE
            if home_xg > away_xg + 0.45:
                win_pick = f"{home_team} 1X"

            elif away_xg > home_xg + 0.45:
                win_pick = f"{away_team} X2"

            else:
                win_pick = "DRAW / TIGHT MATCH"

            # ======================================
            # CORRECT SCORE
            # ======================================

            score_home = round(home_xg)
            score_away = round(away_xg)

            correct_score = f"{score_home}-{score_away}"

            # ======================================
            # FIRST HALF
            # ======================================

            if total_xg * 0.45 > 1:
                first_half = "OVER 0.5 HT"

            else:
                first_half = "UNDER 1.5 HT"

            # ======================================
            # CONFIDENCE
            # ======================================

            h2h_factor = min(h2h_goals / 5, 1)

            confidence = round(
                (
                    prob_over25 * 40
                    +
                    prob_btts * 30
                    +
                    home_form * 20
                    +
                    h2h_factor * 10
                )
            )

            # ======================================
            # RISK LEVEL
            # ======================================

            if confidence >= 75:
                risk = "🟢 LOW RISK"
                risk_class = "high"

            elif confidence >= 60:
                risk = "🟠 MEDIUM RISK"
                risk_class = "mid"

            else:
                risk = "🔴 HIGH RISK"
                risk_class = "low"

            # ======================================
            # DISPLAY
            # ======================================

            st.markdown("---")

            c1, c2, c3 = st.columns(3)

            with c1:

                st.markdown(f"""
                <div class='card'>
                <h3>⚽ GOALS</h3>
                <div class='big'>{goal_pick}</div>
                <div class='small'>
                Over Probability:
                {prob_over25*100:.1f}%
                </div>
                </div>
                """, unsafe_allow_html=True)

            with c2:

                st.markdown(f"""
                <div class='card'>
                <h3>🔥 BTTS</h3>
                <div class='big'>{btts_pick}</div>
                <div class='small'>
                BTTS Probability:
                {prob_btts*100:.1f}%
                </div>
                </div>
                """, unsafe_allow_html=True)

            with c3:

                st.markdown(f"""
                <div class='card'>
                <h3>🚩 CORNERS</h3>
                <div class='big'>{corner_pick}</div>
                <div class='small'>
                Expected:
                {total_corners:.1f}
                </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class='advice'>

            🏆 MATCH SIDE:
            <b>{win_pick}</b><br><br>

            🎯 CORRECT SCORE:
            <b>{correct_score}</b><br><br>

            ⏱ FIRST HALF:
            <b>{first_half}</b><br><br>

            📊 CONFIDENCE:
            <b>{confidence}%</b><br><br>

            ⚠️ RISK:
            <span class='{risk_class}'>{risk}</span>

            </div>
            """, unsafe_allow_html=True)

        except Exception as e:

            st.error(f"ERROR: {e}")

else:

    st.warning("⚠️ Refresh database kwanza.")
