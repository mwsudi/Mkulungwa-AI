import streamlit as st
import pandas as pd
import numpy as np
import requests, joblib, os
from io import StringIO
from scipy.stats import poisson
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

# ---------------- 1. UI SETUP ----------------
st.set_page_config(page_title="MKULUNGWA GLOBAL V46", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070A; color: #E0E0E0; }
    .stMetric { background: #10141D; padding: 15px; border-radius: 12px; border: 1px solid #00FF00; }
    .elite-card { 
        background: #0A0F14; padding: 25px; border-radius: 15px; 
        border: 1px solid #00FF00; margin-bottom: 20px;
        box-shadow: 0px 4px 20px rgba(0, 255, 0, 0.2);
    }
    h1, h2, h3 { color: #00FF00; text-transform: uppercase; letter-spacing: 2px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌍 GLOBAL TRADING DESK V46</h1>", unsafe_allow_html=True)

# ---------------- 2. COUNTRY & LEAGUE MAPPING ----------------
COUNTRY_MAP = {
    "ENGLAND": {"Premier": "E0", "Championship": "E1", "League 1": "E2"},
    "SPAIN": {"La Liga": "SP1", "Segunda": "SP2"},
    "GERMANY": {"Bundesliga 1": "D1", "Bundesliga 2": "D2"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "FRANCE": {"Ligue 1": "F1", "Ligue 2": "F2"},
    "NETHERLANDS": {"Eredivisie": "N1"},
    "BELGIUM": {"Pro League": "B1"},
    "PORTUGAL": {"Liga I": "P1"},
    "TURKEY": {"Super Lig": "T1"},
    "GREECE": {"Super League": "G1"},
    "SCOTLAND": {"Premiership": "SC0", "Championship": "SC1"}
}

# ---------------- 3. DATA ENGINE (Auto-Update) ----------------
@st.cache_data(ttl=3600)
def load_all_data():
    seasons = ["2526", "2425", "2324"]
    dfs = []
    
    for s in seasons:
        for country, leagues in COUNTRY_MAP.items():
            for league_name, code in leagues.items():
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/{s}/{code}.csv"
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        temp_df = pd.read_csv(StringIO(r.text))
                        temp_df['CountryName'] = country
                        temp_df['LeagueName'] = league_name
                        cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'CountryName', 'LeagueName']
                        available_cols = [c for c in cols if c in temp_df.columns]
                        dfs.append(temp_df[available_cols].dropna())
                except:
                    continue
            
    full_df = pd.concat(dfs, ignore_index=True)
    full_df['total'] = full_df['FTHG'] + full_df['FTAG']
    full_df['over25'] = (full_df['total'] >= 3).astype(int)
    return full_df

df_raw = load_all_data()

# ---------------- 4. FEATURE ENGINEERING ----------------
def process_features(df):
    df = df.copy()
    df['hg'] = df.groupby('HomeTeam')['FTHG'].transform(lambda x: x.rolling(10, min_periods=1).mean())
    df['ag'] = df.groupby('AwayTeam')['FTAG'].transform(lambda x: x.rolling(10, min_periods=1).mean())
    return df.dropna(subset=['hg', 'ag'])

df_processed = process_features(df_raw)

# ---------------- 5. AI MODEL (With Error Protection) ----------------
FEATS = ['hg', 'ag']
X = df_processed[FEATS]
y = df_processed['over25']

# Tumeulipa jina jipya kabisa ili tuepuke mgongano
model_path = "v46_ultimate_global.pkl"

def train_new_model():
    rf = RandomForestClassifier(n_estimators=300).fit(X, y)
    lr = LogisticRegression().fit(X, y)
    model_obj = {"rf": rf, "lr": lr}
    joblib.dump(model_obj, model_path)
    return model_obj

if os.path.exists(model_path):
    try:
        model = joblib.load(model_path)
    except:
        # Hapa ndipo ulinzi ulipo: Kama ikigoma, inafuta na kufundisha upya
        os.remove(model_path)
        model = train_new_model()
else:
    model = train_new_model()

# ---------------- 6. MAIN INTERFACE ----------------
st.subheader("🎯 Global Sniper Analyzer")

c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 2, 2, 1])

with c1:
    country_choice = st.selectbox("MATAFA", sorted(list(COUNTRY_MAP.keys())))

with c2:
    available_leagues = list(COUNTRY_MAP[country_choice].keys())
    league_choice = st.selectbox("LIGI", available_leagues)

# Filter timu
mask = (df_raw['CountryName'] == country_choice) & (df_raw['LeagueName'] == league_choice)
teams_list = sorted(df_raw[mask]['HomeTeam'].unique())

with c3: home = st.selectbox("HOME TEAM", teams_list)
with c4: away = st.selectbox("AWAY TEAM", [t for t in teams_list if t != home])
with c5: odds = st.number_input("ODDS (O2.5)", value=1.90, step=0.01)

# --- PREDICTION ENGINE ---
h_stats = df_processed[df_processed['HomeTeam'] == home].tail(1)
a_stats = df_processed[df_processed['AwayTeam'] == away].tail(1)

if not h_stats.empty and not a_stats.empty:
    hg, ag = h_stats['hg'].values[0], a_stats['ag'].values[0]
    
    # Probability calculations
    p_rf = model["rf"].predict_proba([[hg, ag]])[0][1]
    p_lr = model["lr"].predict_proba([[hg, ag]])[0][1]
    prob = (p_rf + p_lr) / 2
    value = (prob * odds) - 1

    st.markdown("<div class='elite-card'>", unsafe_allow_html=True)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("AI PROBABILITY", f"{prob*100:.1f}%")
    m2.metric("EXPECTED VALUE", f"{value:.2f}", delta=f"{value*100:.1f}%")
    
    if prob > 0.70 and value > 0.05:
        signal, color = "🔥 ELITE TRADE", "#00FF00"
    elif prob > 0.60:
        signal, color = "⚡ HIGH TRADE", "#CCFF00"
    else:
        signal, color = "❌ NO TRADE", "#FF4B4B"
        
    st.markdown(f"<h2 style='color:{color};'>SIGNAL: {signal}</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Portfolio Tracking
    if st.button("➕ Add to Train"):
        if "picks" not in st.session_state: st.session_state.picks = []
        st.session_state.picks.append({"Match": f"{home} vs {away}", "Prob": f"{prob*100:.1f}%", "Odds": odds})
        st.success("Imewekwa kwenye mkeka!")

    if "picks" in st.session_state and st.session_state.picks:
        st.table(st.session_state.picks)

else:
    st.info("Chagua timu kuanza uchambuzi.")
