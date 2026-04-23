import streamlit as st
import pandas as pd
import numpy as np
import requests
from scipy.stats import poisson
from sklearn.ensemble import RandomForestClassifier

# ================= UI =================
st.set_page_config(page_title="AI BETTING ENGINE", layout="wide")
st.title("🧠 AI BETTING DECISION ENGINE")

# ================= SAMPLE HISTORICAL DATA =================
@st.cache_data
def load_data():
    data = pd.DataFrame({
        "home_goals": np.random.randint(0,3,200),
        "away_goals": np.random.randint(0,3,200),
        "home_corners": np.random.randint(2,10,200),
        "away_corners": np.random.randint(2,10,200),
    })
    data["total_goals"] = data["home_goals"] + data["away_goals"]
    data["over25"] = (data["total_goals"] >= 3).astype(int)
    return data

df = load_data()

# ================= FEATURES =================
X = df[["home_goals","away_goals","home_corners","away_corners"]]
y = df["over25"]

model = RandomForestClassifier(n_estimators=200)
model.fit(X, y)

# ================= FUNCTIONS =================
def poisson_model(h,a):
    return min(0.9, (h+a)/3)

def market_prob(odds):
    return 1/odds

def edge(p_ai, p_market, odds):
    return (p_ai - p_market) * odds

# ================= INPUT =================
st.subheader("🎯 Analyze Match")

home = st.number_input("Home Avg Goals", 0.0, 5.0, 1.2)
away = st.number_input("Away Avg Goals", 0.0, 5.0, 1.0)
home_c = st.number_input("Home Corners", 0.0, 15.0, 5.0)
away_c = st.number_input("Away Corners", 0.0, 15.0, 4.0)
odds = st.number_input("Odds Over 2.5", 1.2, 5.0, 2.0)

# ================= AI ENGINE =================
x_input = np.array([[home, away, home_c, away_c]])

ml_prob = model.predict_proba(x_input)[0][1]
poisson_prob = poisson_model(home, away)

p_ai = (ml_prob + poisson_prob) / 2
p_market = market_prob(odds)

e = edge(p_ai, p_market, odds)

# ================= DECISION =================
if e > 0.1:
    decision = "🟢 STRONG BET"
elif e > 0:
    decision = "🟡 WEAK BET"
else:
    decision = "🔴 SKIP"

# ================= OUTPUT =================
col1, col2, col3 = st.columns(3)

col1.metric("AI Probability", f"{p_ai:.2f}")
col2.metric("Market Probability", f"{p_market:.2f}")
col3.metric("Edge", f"{e:.3f}")

st.subheader("📌 Decision")
st.success(decision)

# ================= EXPLANATION =================
st.write("""
### 🧠 How AI thinks:
- Combines ML + Poisson model
- Compares with bookmaker odds
- Only selects value bets (positive edge)
""")
