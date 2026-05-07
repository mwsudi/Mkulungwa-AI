import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
import sqlite3
from math import exp, factorial
from sklearn.ensemble import RandomForestClassifier

# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(page_title="MKULUNGWA AI MASTER", layout="wide")

# ==============================
# DATABASE SAFE SETUP
# ==============================

conn = sqlite3.connect("mkulungwa_ai.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    home TEXT,
    away TEXT,
    league TEXT,
    h_scored REAL,
    a_scored REAL,
    h_conceded REAL,
    a_conceded REAL,
    home_goals INTEGER,
    away_goals INTEGER
)
""")

conn.commit()

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
# LOAD DATA SAFE
# ==============================

def load_data(code):
    path = f"{code}.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

# ==============================
# POISSON
# ==============================

def poisson(lam, k):
    return (lam**k * exp(-lam)) / factorial(k)

# ==============================
# ML MODEL
# ==============================

def train_model():

    df = pd.read_sql("SELECT * FROM matches", conn)

    if len(df) < 20:
        return None

    df["label"] = (df["home_goals"] > df["away_goals"]).astype(int)

    X = df[["h_scored","a_scored","h_conceded","a_conceded"]]
    y = df["label"]

    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X, y)

    return model

# ==============================
# UI
# ==============================

st.title("🧠 MKULUNGWA AI MASTER v50 FIXED")

league = st.selectbox("Select League", list(LEAGUE_MAP.keys()))
code = LEAGUE_MAP[league]

df = load_data(code)

# ==============================
# SAFETY CHECK
# ==============================

if df is None or len(df) == 0:
    st.error("❌ No data found. Please refresh database.")
    st.stop()

teams = sorted(df["HomeTeam"].dropna().unique())

home = st.selectbox("Home Team", teams)
away = st.selectbox("Away Team", [t for t in teams if t != home])

# ==============================
# RUN AI
# ==============================

if st.button("RUN AI PREDICTION"):

    h_form = df[df["HomeTeam"] == home].tail(8)
    a_form = df[df["AwayTeam"] == away].tail(8)

    if len(h_form) == 0 or len(a_form) == 0:
        st.error("Not enough team data")
        st.stop()

    # SAFE FEATURES
    h_scored = h_form["FTHG"].mean()
    h_conceded = h_form["FTAG"].mean()
    a_scored = a_form["FTAG"].mean()
    a_conceded = a_form["FTHG"].mean()

    home_xg = (h_scored + a_conceded) / 2
    away_xg = (a_scored + h_conceded) / 2

    # ==========================
    # GOALS PROB
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

    first_half = "OVER 0.5 HT" if (home_xg+away_xg)*0.45 > 0.8 else "UNDER 1.5 HT"

    confidence = round(((prob_over*100)+(prob_btts*100))/2)

    risk = "🟢 LOW" if confidence > 80 else "🟡 MID" if confidence > 60 else "🔴 HIGH"

    # ==========================
    # SAFE DATABASE INSERT (FIXED)
    # ==========================

    c.execute("""
    INSERT INTO matches (
        home,away,league,
        h_scored,a_scored,
        h_conceded,a_conceded,
        home_goals,away_goals
    )
    VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        home, away, league,
        h_scored, a_scored,
        h_conceded, a_conceded,
        0, 0
    ))

    conn.commit()

    # ==========================
    # DISPLAY
    # ==========================

    st.markdown("---")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.success(f"GOALS: {goal_pick}")

    with c2:
        st.success(f"BTTS: {btts_pick}")

    with c3:
        st.success(f"CORNERS: {corner_pick}")

    st.markdown(f"""
    ### 🏆 DOUBLE CHANCE: {dc_pick}
    ### 🎯 SCORE: {correct_score}
    ### ⏱ FIRST HALF: {first_half}
    ### 📊 CONFIDENCE: {confidence}%
    ### ⚠️ RISK: {risk}
    """)

# ==============================
# ML STATUS
# ==============================

model = train_model()

if model is None:
    st.info("ML Model: Not enough data yet (need 20+ matches)")
else:
    st.success("ML Model: ACTIVE ✔️")
