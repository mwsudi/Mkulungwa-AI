import streamlit as st
import pandas as pd
import numpy as np
import requests, joblib, os
from io import StringIO
from scipy.stats import poisson
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV

# ---------------- UI SETUP ----------------
st.set_page_config(page_title="ELITE TRADING DESK AI", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070A; color: #E0E0E0; }
    .stMetric { background: #10141D; padding: 15px; border-radius: 10px; border: 1px solid #00FF00; }
    .elite-card { 
        background: #0A0F14; padding: 25px; border-radius: 15px; 
        border: 1px solid #00FF00; margin-bottom: 20px;
        box-shadow: 0px 4px 20px rgba(0, 255, 0, 0.2);
    }
    h1, h2, h3 { color: #00FF00; text-transform: uppercase; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🔥 FINAL TRADING DESK SYSTEM</h1>", unsafe_allow_html=True)

# ---------------- DATA ENGINE ----------------
@st.cache_data(ttl=3600) # Inakaa saa moja kisha inajifuta kuitafuta mpya
def load_data():
    leagues = ["E0","SP1","I1","D1","F1","T1","G1"] # T1=Turkey, G1=Greece
    seasons = ["2526","2425","2324"]
    dfs = []

    status = st.empty()
    status.text("🛰️ Inavuta data za misimu 3 ya dunia...")

    for s in seasons:
        for l in leagues:
            try:
                url = f"https://www.football-data.co.uk/mmz4281/{s}/{l}.csv"
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    temp_df = pd.read_csv(StringIO(r.text))
                    dfs.append(temp_df)
            except:
                continue

    full_df = pd.concat(dfs, ignore_index=True)
    # Hakikisha tunachukua vigezo muhimu pekee
    needed = ['HomeTeam','AwayTeam','FTHG','FTAG','HC','AC']
    full_df = full_df[needed].dropna()
    full_df['total'] = full_df['FTHG'] + full_df['FTAG']
    full_df['over25'] = (full_df['total'] >= 3).astype(int)
    
    status.empty()
    return full_df

df_raw = load_data()

# ---------------- FEATURE ENGINEERING ----------------
def process_features(df):
    # Rolling mean ya mechi 10 za mwisho kwa kila timu
    df = df.copy()
    df['hg'] = df.groupby('HomeTeam')['FTHG'].transform(lambda x: x.rolling(10, min_periods=1).mean())
    df['ag'] = df.groupby('AwayTeam')['FTAG'].transform(lambda x: x.rolling(10, min_periods=1).mean())
    df['hc'] = df.groupby('HomeTeam')['HC'].transform(lambda x: x.rolling(10, min_periods=1).mean())
    df['ac'] = df.groupby('AwayTeam')['AC'].transform(lambda x: x.rolling(10, min_periods=1).mean())
    return df.dropna()

df_processed = process_features(df_raw)

# ---------------- AI MODEL CORE ----------------
FEATS = ['hg','ag','hc','ac']
X = df_processed[FEATS]
y = df_processed['over25']

model_path = "desk_model.pkl"

if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    with st.spinner("🧠 Inafunza AI Model (Calibration Mode)..."):
        rf = RandomForestClassifier(n_estimators=300, random_state=42)
        lr = LogisticRegression(max_iter=1000)

        # Calibrated models ni bora kwa betting probability
        clf_rf = CalibratedClassifierCV(rf, cv=3).fit(X, y)
        clf_lr = CalibratedClassifierCV(lr, cv=3).fit(X, y)

        model = {"rf": clf_rf, "lr": clf_lr}
        joblib.dump(model, model_path)

# ---------------- MATH ENGINES ----------------
def predict_proba(x_input):
    p1 = model["rf"].predict_proba(x_input)[0][1]
    p2 = model["lr"].predict_proba(x_input)[0][1]
    return (p1 + p2) / 2

def poisson_prob(h_exp, a_exp):
    p = 0
    for i in range(6):
        for j in range(6):
            pr = poisson.pmf(i, h_exp) * poisson.pmf(j, a_exp)
            if i + j >= 3:
                p += pr
    return p

def kelly_criterion(p, odds):
    b = odds - 1
    if b <= 0: return 0
    q = 1 - p
    f = (b * p - q) / b
    return max(0, f) * 0.5  # Fractional Kelly for safety

# ---------------- APP INTERFACE ----------------
st.subheader("🎯 Match Trading Analyzer")

teams = sorted(df_raw['HomeTeam'].unique())
col_a, col_b, col_c = st.columns([2,2,1])

with col_a: home = st.selectbox("Home Team", teams)
with col_b: away = st.selectbox("Away Team", [t for t in teams if t != home])
with col_c: odds = st.number_input("Odds (Over 2.5)", value=2.0, step=0.01)

# Get current stats for prediction
h_stats = df_processed[df_processed['HomeTeam'] == home].tail(1)
a_stats = df_processed[df_processed['AwayTeam'] == away].tail(1)

if not h_stats.empty and not a_stats.empty:
    hg, ag = h_stats['hg'].values[0], a_stats['ag'].values[0]
    hc, ac = h_stats['hc'].values[0], a_stats['ac'].values[0]
    
    x_input = np.array([[hg, ag, hc, ac]])

    # Calculation
    p_ml = predict_proba(x_input)
    p_po = poisson_prob(hg, ag)
    
    # Final Weighted Prob
    final_p = (0.5 * p_ml) + (0.5 * p_po)
    value = (final_p * odds) - 1
    stake_fraction = kelly_criterion(final_p, odds)

    # --- OUTPUT ---
    st.markdown("<div class='elite-card'>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ML PROB", f"{p_ml*100:.1f}%")
    c2.metric("POISSON", f"{p_po*100:.1f}%")
    c3.metric("FINAL PROB", f"{final_p*100:.1f}%")
    c4.metric("VALUE", f"{value:.2f}", delta=f"{value*100:.1f}%")

    st.markdown("---")
    
    if final_p > 0.70 and value > 0.1:
        signal, color = "🔥 ELITE TRADE", "#00FF00"
    elif final_p > 0.62:
        signal, color = "⚡ HIGH TRADE", "#CCFF00"
    elif final_p > 0.55:
        signal, color = "⚠️ MEDIUM RISK", "#FFFF00"
    else:
        signal, color = "❌ NO TRADE", "#FF4B4B"

    st.markdown(f"<h2 style='color:{color}; text-align:center;'>SIGNAL: {signal}</h2>", unsafe_allow_html=True)
    st.write(f"**Recommended Stake:** {stake_fraction*100:.1f}% of Bankroll")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- PORTFOLIO TRACKER ----------------
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = []

    if st.button("➕ Add to My Trades"):
        st.session_state.portfolio.append({
            "Match": f"{home} vs {away}",
            "Stake": f"{stake_fraction*100:.1f}%",
            "Prob": f"{final_p*100:.1f}%",
            "Odds": odds
        })
        st.success("Trade imerekodiwa!")

    if st.session_state.portfolio:
        st.subheader("📦 My Active Portfolio")
        st.table(st.session_state.portfolio)

else:
    st.warning("⚠️ Data haitoshi kwa timu hizi. Chagua timu nyingine.")
