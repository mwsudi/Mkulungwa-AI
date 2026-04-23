import streamlit as st
import pandas as pd
import numpy as np
import requests, os, joblib
from io import StringIO
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MKULUNGWA GOD MODE 2026", layout="wide")
st.title("🧠⚡ MKULUNGWA AI – VERSION 2026 (OVER 1.5)")

MODEL_PATH = "mkulungwa_2026_model.pkl"

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

# ---------------- LOAD DATA (4 SEASONS: 22/23 - 25/26) ----------------
@st.cache_data(ttl=3600)
def load_data():
    # Tumeshajumuisha msimu wa sasa 25/26
    seasons = ["2223", "2324", "2425", "2526"] 
    dfs = []
    
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    total_leagues = sum(len(v) for v in COUNTRY_MAP.values())
    total_steps = len(seasons) * total_leagues
    current_step = 0

    for s in seasons:
        for c in COUNTRY_MAP:
            for lg, code in COUNTRY_MAP[c].items():
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/{s}/{code}.csv"
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        df_tmp = pd.read_csv(StringIO(r.text))
                        df_tmp["Country"], df_tmp["League"] = c, lg
                        # Tunachukua column muhimu tu kupunguza mzigo wa RAM
                        dfs.append(df_tmp[['HomeTeam','AwayTeam','FTHG','FTAG','Country','League']])
                except:
                    continue
                current_step += 1
                progress_bar.progress(min(current_step / total_steps, 1.0))
                status_text.text(f"Inapakia Data: Msimu {s} - {lg}...")
    
    status_text.empty()
    df = pd.concat(dfs).dropna()
    df['total'] = df['FTHG'] + df['FTAG']
    # LENGO: OVER 1.5 (Goli 2 au zaidi)
    df['over15'] = (df['total'] >= 2).astype(int)
    return df

df = load_data()

# ---------------- FEATURE ENGINEERING (LAST 8 MATCHES) ----------------
def get_features(df):
    df = df.copy()
    # Mahesabu ya fomu kwa kutumia mechi 8 za mwisho (kwa uhakika zaidi)
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

# ---------------- AI MODEL ----------------
@st.cache_resource
def train_model():
    # RF 500 kwa ajili ya accuracy ya juu zaidi
    rf = RandomForestClassifier(n_estimators=500, random_state=42).fit(X, y)
    lr = LogisticRegression(max_iter=1000).fit(X, y)
    return {"rf": rf, "lr": lr}

model = train_model()

# ---------------- POISSON LOGIC ----------------
def poisson_prob(h, a):
    lamb = h + a
    prob_0 = np.exp(-lamb)
    prob_1 = lamb * np.exp(-lamb)
    return 1 - (prob_0 + prob_1)

# ---------------- PREDICT ----------------
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

    return (0.4 * p1 + 0.3 * p2 + 0.3 * p3)

# ---------------- UI ----------------
st.sidebar.title("SETTINGS")
st.sidebar.success("DATA: 2022 - 2026")
st.sidebar.info("MODE: OVER 1.5 SAFE")

st.subheader("🎯 MANUAL SNIPER (OVER 1.5)")

c1, c2, c3 = st.columns(3)

with c1:
    lg_list = sorted(df['League'].unique())
    lg = st.selectbox("CHAGUA LIGI", lg_list)
    teams = sorted(df[df['League'] == lg]['HomeTeam'].unique())
with c2:
    home = st.selectbox("HOME TEAM", teams)
with c3:
    away = st.selectbox("AWAY TEAM", [t for t in teams if t != home])

odds = st.number_input("ODDS ZA MUHINDI", value=1.25, step=0.01)

if st.button("PIGA ANALYSES"):
    p = predict_over15(home, away)
    if p:
        mp = 1 / odds
        edge = p - mp
        val = (p * odds) - 1
        
        st.divider()
        
        # Hukumu ya mwisho
        if p >= 0.85:
            st.success(f"🔥 UHAKIKA WA NAULI! (AI: {p*100:.1f}%)")
            st.balloons()
        elif p >= 0.70:
            st.warning(f"⚖️ INAFAA KWA MKEKA (AI: {p*100:.1f}%)")
        else:
            st.error(f"❌ RISK - ACHANA NAYO (AI: {p*100:.1f}%)")

        res1, res2, res3 = st.columns(3)
        res1.metric("AI%", f"{p*100:.1f}%")
        res2.metric("EDGE%", f"{edge*100:.1f}%")
        res3.metric("VALUE", f"{val:.2f}")
    else:
        st.warning("Data hazitoshi kwa mechi hii (Huenda timu imepanda daraja hivi karibuni).")

st.markdown("---")
st.caption("Mkulungwa AI v2026 | Bagamoyo Edition 🚢")
