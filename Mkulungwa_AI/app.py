import streamlit as st
import pandas as pd
import numpy as np
import requests, os, joblib
from io import StringIO
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MKULUNGWA GOD MODE v2", layout="wide")
st.title("🧠⚡ MKULUNGWA AI – SAFE MODE (OVER 1.5)")

MODEL_PATH = "mkulungwa_safe_model.pkl"

# ---------------- LEAGUES ----------------
COUNTRY_MAP = {
    "ENGLAND": {"Premier": "E0", "Championship": "E1"},
    "SPAIN": {"La Liga": "SP1", "Segunda": "SP2"},
    "GERMANY": {"Bundesliga": "D1"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "FRANCE": {"Ligue 1": "F1"},
    "NETHERLANDS": {"Eredivisie": "N1"},
    "BELGIUM": {"Jupiler": "B1"}
}

# ---------------- LOAD DATA (3 SEASONS) ----------------
@st.cache_data(ttl=86400) # Inakaa saa 24 kwa uhakika
def load_data():
    seasons = ["2223", "2324", "2425"] # Miaka 3 ya data
    dfs = []
    progress_bar = st.progress(0)
    total_steps = len(seasons) * len(COUNTRY_MAP)
    step = 0

    for s in seasons:
        for c in COUNTRY_MAP:
            for lg, code in COUNTRY_MAP[c].items():
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/{s}/{code}.csv"
                    r = requests.get(url, timeout=15)
                    if r.status_code == 200:
                        df_tmp = pd.read_csv(StringIO(r.text))
                        df_tmp["Country"], df_tmp["League"] = c, lg
                        dfs.append(df_tmp[['HomeTeam','AwayTeam','FTHG','FTAG','Country','League']])
                except:
                    continue
            step += 1
            progress_bar.progress(step / total_steps)
    
    df = pd.concat(dfs).dropna()
    df['total'] = df['FTHG'] + df['FTAG']
    # TUNACHUJA OVER 1.5 (Magoli kuanzia mawili kwenda juu)
    df['over15'] = (df['total'] >= 2).astype(int)
    return df

df = load_data()

# ---------------- FEATURE ENGINEERING ----------------
def get_features(df):
    df = df.copy()
    # Mahesabu ya fomu ya hivi karibuni
    df['hg'] = df.groupby('HomeTeam')['FTHG'].transform(lambda x: x.rolling(8).mean())
    df['ag'] = df.groupby('AwayTeam')['FTAG'].transform(lambda x: x.rolling(8).mean())
    df['hc'] = df.groupby('HomeTeam')['FTAG'].transform(lambda x: x.rolling(8).mean())
    df['ac'] = df.groupby('AwayTeam')['FTHG'].transform(lambda x: x.rolling(8).mean())
    df['hs'] = df['hg'] - df['hc']
    df['as_'] = df['ag'] - df['ac']
    return df.dropna()

df_feats = get_features(df)
FEATS = ['hg','ag','hc','ac','hs','as_']
X = df_feats[FEATS]
y = df_feats['over15']

# ---------------- AI MODEL TRAINING ----------------
@st.cache_resource
def train_model():
    rf = RandomForestClassifier(n_estimators=500, random_state=42).fit(X, y)
    lr = LogisticRegression(max_iter=1000).fit(X, y)
    return {"rf": rf, "lr": lr}

model = train_model()

# ---------------- POISSON CALCULATOR ----------------
def poisson_prob(h, a):
    # Probability ya kufungana magoli kuanzia 2 kwenda juu
    lamb = h + a
    prob_0 = np.exp(-lamb)
    prob_1 = lamb * np.exp(-lamb)
    return 1 - (prob_0 + prob_1)

# ---------------- PREDICTION LOGIC ----------------
def predict_over15(h, a):
    h_data = df_feats[df_feats['HomeTeam'] == h].tail(1)
    a_data = df_feats[df_feats['AwayTeam'] == a].tail(1)
    
    if h_data.empty or a_data.empty:
        return None

    vals = [[h_data['hg'].values[0], a_data['ag'].values[0], 
             h_data['hc'].values[0], a_data['ac'].values[0], 
             h_data['hs'].values[0], a_data['as_'].values[0]]]

    p1 = model["rf"].predict_proba(vals)[0][1]
    p2 = model["lr"].predict_proba(vals)[0][1]
    p3 = poisson_prob(h_data['hg'].values[0], a_data['ag'].values[0])

    # Weighting: RF inapewa uzito zaidi kwa accuracy
    return (0.4 * p1 + 0.3 * p2 + 0.3 * p3)

# ---------------- UI DASHBOARD ----------------
st.header("🎯 SNIPER MANUAL: OVER 1.5 SAFE MODE")

c1, c2, c3 = st.columns(3)

with c1:
    lg = st.selectbox("LIGI", sorted(df['League'].unique()))
    teams = sorted(df[df['League'] == lg]['HomeTeam'].unique())
with c2:
    home = st.selectbox("HOME TEAM", teams)
with c3:
    away = st.selectbox("AWAY TEAM", [t for t in teams if t != home])

odds = st.number_input("ODDS ZA MUHINDI (Over 1.5)", value=1.30, step=0.01)

if st.button("CHAMBUA KITALAMU"):
    p = predict_over15(home, away)
    if p:
        mp = 1 / odds
        edge = p - mp
        val = (p * odds) - 1
        
        st.divider()
        
        # Hukumu ya AI
        if p > 0.85 and val > 0.05:
            st.success(f"🔥 UHAKIKA WA NAULI! (AI: {p*100:.1f}%)")
            st.balloons()
        elif p > 0.75:
            st.warning(f"⚖️ INAFAA KWA MKΕΚΑ (AI: {p*100:.1f}%)")
        else:
            st.error(f"❌ RISK KUBWA (AI: {p*100:.1f}%)")

        col1, col2, col3 = st.columns(3)
        col1.metric("AI PROBABILITY", f"{p*100:.1f}%")
        col2.metric("EDGE", f"{edge*100:.1f}%")
        col3.metric("VALUE SCORE", f"{val:.2f}")
    else:
        st.error("Data hazitoshi kwa timu hizi!")

st.sidebar.markdown("### 📋 MIKAKATI YA MASTER")
st.sidebar.info("""
1. **Single Bet:** Over 1.5 kwenye mechi yenye AI > 85%.
2. **Treni la Nauli:** Unganisha timu 3-4 zenye AI > 80%.
3. **Bagamoyo Prep:** Usibet hela yote ya nauli!
""")
