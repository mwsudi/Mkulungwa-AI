import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from io import StringIO
from math import exp, factorial

# ==============================
# APP CONFIG
# ==============================
st.set_page_config(page_title="MKULUNGWA AI MASTER", layout="wide")

# ==============================
# STYLE
# ==============================
st.markdown("""
<style>
.main {background:#0E1117; color:white;}

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

.big{font-size:30px; font-weight:900; color:#00ff66;}
.small{color:#cfcfcf;}

.advice{
    background:#101820;
    border-left:5px solid #00ff66;
    padding:15px;
    margin-top:10px;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# LEAGUES
# ==============================
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

# ==============================
# REFRESH DATA
# ==============================
with st.sidebar:
    st.title("🌍 DATABASE")

    if st.button("🔄 REFRESH"):
        for name, code in LEAGUE_MAP.items():
            try:
                url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    with open(f"{code}.csv", "wb") as f:
                        f.write(r.content)
            except:
                pass
        st.success("UPDATED!")

# ==============================
# TITLE
# ==============================
st.markdown("<h1 style='text-align:center;color:#00ff66;'>MKULUNGWA AI MASTER V FINAL</h1>", unsafe_allow_html=True)

league = st.selectbox("SELECT LEAGUE", list(LEAGUE_MAP.keys()))
code = LEAGUE_MAP[league]

# ==============================
# LOAD DATA
# ==============================
if os.path.exists(f"{code}.csv"):

    df = pd.read_csv(f"{code}.csv")

    teams = sorted(df["HomeTeam"].dropna().unique())

    home = st.selectbox("HOME TEAM", teams)
    away = st.selectbox("AWAY TEAM", [t for t in teams if t != home])

    # ==============================
    # ANALYSIS
    # ==============================
    if st.button("RUN ANALYSIS"):

        h = df[df["HomeTeam"] == home].tail(8)
        a = df[df["AwayTeam"] == away].tail(8)

        weights = np.array([1,2,3,4,5,6,7,8])

        h_scored = np.average(h["FTHG"], weights=weights[-len(h):])
        h_conceded = np.average(h["FTAG"], weights=weights[-len(h):])

        a_scored = np.average(a["FTAG"], weights=weights[-len(a):])
        a_conceded = np.average(a["FTHG"], weights=weights[-len(a):])

        home_xg = (h_scored + a_conceded) / 2
        away_xg = (a_scored + h_conceded) / 2

        total_xg = home_xg + away_xg

        # ==============================
        # SIMPLE PROBABILITY MODEL
        # ==============================
        def poisson(lam, k):
            return (lam**k * exp(-lam)) / factorial(k)

        prob_under25 = 0
        for i in range(3):
            for j in range(3):
                if i + j < 3:
                    prob_under25 += poisson(home_xg, i) * poisson(away_xg, j)

        prob_over25 = 1 - prob_under25

        prob_btts = (1 - poisson(home_xg,0)) * (1 - poisson(away_xg,0))

        avg_hc = h["HC"].mean() if "HC" in h.columns else 5
        avg_ac = a["AC"].mean() if "AC" in a.columns else 4

        total_corners = avg_hc + avg_ac

        # ==============================
        # PICK LOGIC
        # ==============================

        # GOALS
        if prob_over25 >= 0.65:
            goal_pick = "OVER 2.5 (STRONG)"
            goal_status = "SAFE"
        elif prob_over25 >= 0.55:
            goal_pick = "OVER 1.5 (MEDIUM)"
            goal_status = "MEDIUM"
        else:
            goal_pick = "UNDER / SKIP"
            goal_status = "AVOID"

        # BTTS
        if prob_btts >= 0.65:
            btts_pick = "BTTS YES"
            btts_status = "SAFE"
        elif prob_btts >= 0.55:
            btts_pick = "BTTS MAYBE"
            btts_status = "MEDIUM"
        else:
            btts_pick = "BTTS NO / SKIP"
            btts_status = "AVOID"

        # CORNERS
        if total_corners >= 9:
            corner_pick = "OVER 8.5 / 9.5"
            corner_status = "SAFE"
        else:
            corner_pick = "UNDER 9.5"
            corner_status = "AVOID"

        # DOUBLE CHANCE
        if home_xg > away_xg + 0.4:
            dc = "1X"
        elif away_xg > home_xg + 0.4:
            dc = "X2"
        else:
            dc = "SKIP"

        # ==============================
        # DISPLAY RESULTS
        # ==============================
        st.markdown("---")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"""
            <div class='card'>
            <h3>⚽ GOALS</h3>
            <div class='big'>{goal_pick}</div>
            <div class='small'>{round(prob_over25*100,1)}%</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class='card'>
            <h3>BTTS</h3>
            <div class='big'>{btts_pick}</div>
            <div class='small'>{round(prob_btts*100,1)}%</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class='card'>
            <h3>CORNERS</h3>
            <div class='big'>{corner_pick}</div>
            <div class='small'>{total_corners:.1f}</div>
            </div>
            """, unsafe_allow_html=True)

        # ==============================
        # FINAL BET RECOMMENDATION
        # ==============================
        st.markdown("## 🧠 FINAL AI BET RECOMMENDATION")

        if goal_status == "SAFE" and btts_status == "SAFE":
            st.success(f"""
            🟢 SAFE BETS:
            - {goal_pick}
            - {btts_pick}
            - {corner_pick}
            - Double Chance: {dc}
            """)
        elif goal_status == "MEDIUM":
            st.warning(f"""
            🟡 MEDIUM BETS:
            - {goal_pick}
            - {btts_pick}
            - {corner_pick}
            """)
        else:
            st.error("🔴 AVOID THIS MATCH (LOW QUALITY SIGNAL)")

else:
    st.warning("Refresh database kwanza.")
