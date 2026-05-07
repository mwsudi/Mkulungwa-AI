import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from math import exp, factorial

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(page_title="MKULUNGWA AI STABLE", layout="wide")

# ==========================
# STYLE
# ==========================

st.markdown("""
<style>
.main{background:#0E1117;color:white;}
.card{background:#161B22;padding:20px;border-radius:12px;border-top:4px solid #00ff66;text-align:center;}
.big{font-size:28px;color:#00ff66;font-weight:bold;}
.small{color:#ccc;}
.advice{background:#101820;padding:15px;border-left:4px solid #00ff66;margin-top:10px;border-radius:10px;}
</style>
""", unsafe_allow_html=True)

# ==========================
# LEAGUES
# ==========================

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

# ==========================
# LOAD DATA SAFE
# ==========================

def load_data(code):
    path = f"{code}.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

# ==========================
# POISSON FUNCTION
# ==========================

def poisson(lam, k):
    return (lam**k * exp(-lam)) / factorial(k)

# ==========================
# UI
# ==========================

st.title("🧠 MKULUNGWA AI STABLE v60")

league = st.selectbox("Select League", list(LEAGUE_MAP.keys()))
code = LEAGUE_MAP[league]

df = load_data(code)

# ==========================
# SAFE CHECK
# ==========================

if df is None or len(df) == 0:
    st.error("❌ No data found. Please refresh database.")
    st.stop()

teams = sorted(df["HomeTeam"].dropna().unique())

home = st.selectbox("Home Team", teams)
away = st.selectbox("Away Team", [t for t in teams if t != home])

# ==========================
# RUN AI
# ==========================

if st.button("RUN AI PREDICTION"):

    h_form = df[df["HomeTeam"] == home].tail(8)
    a_form = df[df["AwayTeam"] == away].tail(8)

    if len(h_form) == 0 or len(a_form) == 0:
        st.error("Not enough match data")
        st.stop()

    # SAFE STATS
    h_scored = h_form["FTHG"].mean()
    h_conceded = h_form["FTAG"].mean()
    a_scored = a_form["FTAG"].mean()
    a_conceded = a_form["FTHG"].mean()

    h_scored = 0 if np.isnan(h_scored) else h_scored
    h_conceded = 0 if np.isnan(h_conceded) else h_conceded
    a_scored = 0 if np.isnan(a_scored) else a_scored
    a_conceded = 0 if np.isnan(a_conceded) else a_conceded

    # EXPECTED GOALS
    home_xg = (h_scored + a_conceded) / 2
    away_xg = (a_scored + h_conceded) / 2

    # ==========================
    # GOALS PROBABILITY
    # ==========================

    prob_under = 0

    for i in range(3):
        for j in range(3):
            if i + j < 3:
                prob_under += poisson(home_xg, i) * poisson(away_xg, j)

    prob_over = 1 - prob_under

    # ==========================
    # BTTS
    # ==========================

    prob_btts = (1 - poisson(home_xg,0)) * (1 - poisson(away_xg,0))

    # ==========================
    # CORNERS SAFE
    # ==========================

    hc = h_form["HC"].mean() if "HC" in h_form.columns else 5
    ac = a_form["AC"].mean() if "AC" in a_form.columns else 4

    corners = hc + ac

    # ==========================
    # PICKS
    # ==========================

    goal_pick = "OVER 2.5" if prob_over > 0.6 else "OVER 1.5"
    btts_pick = "YES" if prob_btts > 0.6 else "NO"
    corner_pick = "OVER 8.5" if corners > 8 else "OVER 7.5"
    dc_pick = "1X" if home_xg > away_xg else "X2"

    correct_score = f"{round(home_xg)}-{round(away_xg)}"

    first_half = "OVER 0.5 HT" if (home_xg + away_xg) * 0.45 > 0.8 else "UNDER 1.5 HT"

    confidence = round(((prob_over * 100) + (prob_btts * 100)) / 2)

    risk = "🟢 LOW" if confidence > 80 else "🟡 MID" if confidence > 60 else "🔴 HIGH"

    # ==========================
    # DISPLAY
    # ==========================

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class='card'>
        <h3>⚽ GOALS</h3>
        <div class='big'>{goal_pick}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class='card'>
        <h3>🔥 BTTS</h3>
        <div class='big'>{btts_pick}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class='card'>
        <h3>🚩 CORNERS</h3>
        <div class='big'>{corner_pick}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='advice'>
    🏆 DOUBLE CHANCE: <b>{dc_pick}</b><br>
    🎯 CORRECT SCORE: <b>{correct_score}</b><br>
    ⏱ FIRST HALF: <b>{first_half}</b><br>
    📊 CONFIDENCE: <b>{confidence}%</b><br>
    ⚠️ RISK: <b>{risk}</b>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("Select teams and run AI prediction")
