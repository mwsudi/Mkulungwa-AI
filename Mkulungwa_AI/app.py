import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
from sklearn.ensemble import RandomForestClassifier

# --- UI SETUP ---
st.set_page_config(page_title="MKULUNGWA ML BEAST", layout="wide")
st.title("🧠 MKULUNGWA AI - REAL MACHINE LEARNING")

# Data Storage
if 'ml_brain' not in st.session_state:
    st.session_state['ml_brain'] = None
    st.session_state['leagues_data'] = {}

# --- LEAGUE MAPPING ---
NATIONS = {
    "ENGLAND": {"E0": "EPL", "E1": "Championship", "E2": "League 1"},
    "FRANCE": {"F1": "Ligue 1", "F2": "Ligue 2", "F3": "National"},
    "SPAIN": {"SP1": "La Liga 1", "SP2": "La Liga 2"},
    "ITALY": {"I1": "Serie A", "I2": "Serie B"}
}

# --- ML ENGINE ---
def train_ai(df):
    # Tunatengeneza 'Features' (Data za kujifunzia)
    df = df.copy().dropna(subset=['HC', 'AC', 'FTHG', 'FTAG'])
    if len(df) < 10: return None
    
    # Feature Engineering
    df['total_goals'] = df['FTHG'] + df['FTAG']
    df['total_corners'] = df['HC'] + df['AC']
    
    # Target: 1 kama ni Over 2.5, 0 kama ni Under
    df['target_goals'] = (df['total_goals'] > 2.5).astype(int)
    # Target: 1 kama ni Under 8.5 (Kona chache), 0 kama ni Over
    df['target_corners'] = (df['total_corners'] < 8.5).astype(int)
    
    X = df[['HS', 'AS', 'HST', 'AST', 'HC', 'AC']].tail(100) # Mashuti na Kona
    y_g = df['target_goals'].tail(100)
    y_c = df['target_corners'].tail(100)
    
    model_g = RandomForestClassifier(n_estimators=50).fit(X, y_g)
    model_c = RandomForestClassifier(n_estimators=50).fit(X, y_c)
    
    return model_g, model_c

# --- SIDEBAR SYNC ---
with st.sidebar:
    if st.button("🔄 TRAIN MACHINE LEARNING"):
        with st.spinner("AI inajifunza patterns za ligi zote..."):
            all_dfs = []
            for n_name, leagues in NATIONS.items():
                for code, name in leagues.items():
                    try:
                        url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                        r = requests.get(url, timeout=5)
                        if r.status_code == 200:
                            ldf = pd.read_csv(StringIO(r.text))
                            st.session_state['leagues_data'][code] = ldf
                            all_dfs.append(ldf)
                    except: continue
            
            if all_dfs:
                big_df = pd.concat(all_dfs, ignore_index=True)
                st.session_state['ml_brain'] = train_ai(big_df)
                st.success("Ubongo wa AI umekamilika!")

# --- MAIN INTERFACE ---
selected_nation = st.selectbox("🌍 TAIFA", list(NATIONS.keys()))
selected_league = st.selectbox("🏆 LIGI", list(NATIONS[selected_nation].values()))
l_code = [k for k, v in NATIONS[selected_nation].items() if v == selected_league][0]

if l_code in st.session_state['leagues_data'] and st.session_state['ml_brain']:
    df = st.session_state['leagues_data'][l_code]
    teams = sorted(df['HomeTeam'].dropna().unique())
    h_t = st.selectbox("🏠 HOME", teams)
    a_t = st.selectbox("🚀 AWAY", [t for t in teams if t != h_t])
    
    if st.button("🎯 ML PREDICTION"):
        # Kuchukua data za hivi karibuni za timu husika kama Features
        h_stats = df[df['HomeTeam'] == h_t].tail(1)
        a_stats = df[df['AwayTeam'] == a_t].tail(1)
        
        if not h_stats.empty and not a_stats.empty:
            # Kutengeneza vector ya utabiri
            test_data = [[
                h_stats['HS'].values[0], a_stats['AS'].values[0],
                h_stats['HST'].values[0], a_stats['AST'].values[0],
                h_stats['HC'].values[0], a_stats['AC'].values[0]
            ]]
            
            model_g, model_c = st.session_state['ml_brain']
            prob_g = model_g.predict_proba(test_data)[0][1]
            prob_c = model_c.predict_proba(test_data)[0][1] # Uwezekano wa Under 8.5
            
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Probability Over 2.5", f"{prob_g*100:.1f}%")
                st.write("🔥🔥 HIGH" if prob_g > 0.6 else "❄️ LOW")
            with c2:
                st.metric("Probability Under 8.5 Corners", f"{prob_c*100:.1f}%")
                st.write("🎯 SNIPER (Under)" if prob_c > 0.65 else "⚠️ Risky")
        else:
            st.error("Timu hizi hazina data za kutosha za mashuti (HS/AS).")
else:
    st.info("Tafadhali 'Train Machine Learning' kwenye sidebar kwanza.")
