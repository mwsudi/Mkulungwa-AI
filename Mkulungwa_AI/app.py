import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
import joblib
from io import StringIO
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import poisson

# ================= UI =================
st.set_page_config(page_title="REAL BETTING AI", layout="wide")
st.title("🧠 REAL DATA BETTING AI ENGINE")

MODEL_PATH = "real_model.pkl"

# ================= LOAD REAL DATA =================
@st.cache_data
def load_data():
    leagues = ["E0","SP1","I1","D1","F1"]
    seasons = ["2324","2223","2122"]

    all_data = []

    for season in seasons:
        for lg in leagues:
            try:
                url = f"https://www.football-data.co.uk/mmz4281/{season}/{lg}.csv"
                r = requests.get(url, timeout=10)
                df = pd.read_csv(StringIO(r.text))

                df = df[['HomeTeam','AwayTeam','FTHG','FTAG']].dropna()
                df["total_goals"] = df["FTHG"] + df["FTAG"]
                df["over25"] = (df["total_goals"] >= 3).astype(int)

                all_data.append(df)
            except:
                pass

    return pd.concat(all_data)

df = load_data()

# ================= FEATURES =================
def feature_engineering(df):
    df = df.copy()

    df["home_form"] = df.groupby("HomeTeam")["FTHG"].transform(lambda x: x.rolling(5).mean())
    df["away_form"] = df.groupby("AwayTeam")["FTAG"].transform(lambda x: x.rolling(5).mean())

    df["home_attack"] = df.groupby("HomeTeam")["FTHG"].transform("mean")
    df["away_attack"] = df.groupby("AwayTeam")["FTAG"].transform("mean")

    df = df.dropna()
    return df

df = feature_engineering(df)

FEATURES = ["home_form","away_form","home_attack","away_attack"]

X = df[FEATURES]
y = df["over25"]

# ================= TRAIN / LOAD MODEL =================
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = RandomForestClassifier(n_estimators=300)
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)

# ================= AI FUNCTIONS =================
def poisson_model(h,a):
    return min(0.95, (h + a) / 3)

def market_prob(odds):
    return 1 / odds

def edge(p_ai, p_market, odds):
    return (p_ai - p_market) * odds - 1

# ================= UI INPUT =================
st.subheader("🎯 Select Match")

teams = sorted(df["HomeTeam"].unique())

home = st.selectbox("Home Team", teams)
away = st.selectbox("Away Team", [t for t in teams if t != home])
odds = st.number_input("Over 2.5 Odds", 1.2, 5.0, 2.0)

# ================= BUILD INPUT =================
h_data = df[df["HomeTeam"] == home].tail(5)
a_data = df[df["AwayTeam"] == away].tail(5)

home_form = h_data["FTHG"].mean()
away_form = a_data["FTAG"].mean()
home_attack = df[df["HomeTeam"] == home]["FTHG"].mean()
away_attack = df[df["AwayTeam"] == away]["FTAG"].mean()

x_input = np.array([[home_form, away_form, home_attack, away_attack]])

# ================= PREDICTIONS =================
p_ml = model.predict_proba(x_input)[0][1]
p_poisson = poisson_model(home_form, away_form)

p_ai = (p_ml + p_poisson) / 2
p_market = market_prob(odds)

e = edge(p_ai, p_market, odds)

# ================= DECISION =================
if e > 0.15:
    decision = "🟢 STRONG VALUE BET"
elif e > 0:
    decision = "🟡 WEAK VALUE BET"
else:
    decision = "🔴 NO BET"

# ================= OUTPUT =================
col1, col2, col3, col4 = st.columns(4)

col1.metric("AI Prob", f"{p_ai:.2f}")
col2.metric("Market Prob", f"{p_market:.2f}")
col3.metric("Edge", f"{e:.3f}")
col4.metric("Model", "REAL DATA")

st.subheader("📌 Decision")
st.success(decision)

# ================= EXPLANATION =================
st.write("""
### 🧠 REAL AI LOGIC:
- Uses real football results (EPL, La Liga, etc.)
- Learns team performance patterns
- Compares AI probability vs bookmaker odds
- Only selects VALUE bets (positive edge)
""")
