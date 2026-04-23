import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
from io import StringIO
from sklearn.ensemble import RandomForestClassifier

# --- 1. UI SETUP (V36 PRO STYLE) ---
st.set_page_config(page_title="MKULUNGWA AI V36 PRO - AI DESK", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070A; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(135deg, #00FF00, #008800); 
        color: white; border-radius: 8px; height: 3.5em; width: 100%; border: none; font-weight: 900;
        box-shadow: 0px 4px 15px rgba(0, 255, 0, 0.3);
    }
    .ai-card { 
        background: #10141D; padding: 25px; border-radius: 15px; 
        border: 1px solid #00FF00; margin-bottom: 20px;
    }
    .metric-box { text-align: center; padding: 10px; background: #1A1C24; border-radius: 10px; border: 1px solid #333; }
    .status-ultra { color: #00FF00; font-size: 2em; font-weight: 900; text-shadow: 2px 2px #000; }
    h1 { color: #00FF00; text-align: center; font-family: 'Courier New'; letter-spacing: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
LEAGUE_MAP = {
    "ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", "FRANCE": "F1", 
    "GREECE": "G1", "SCOTLAND": "SC0", "TURKEY": "T1", "NETHERLANDS": "N1", "BELGIUM": "B1"
}

with st.sidebar:
    st.header("🤖 AI CONTROL PANEL")
    if st.button("🔄 RETRAIN AI & UPDATE DATA"):
        with st.spinner("Inavuta Data & Inafunza AI..."):
            for name, code in LEAGUE_MAP.items():
                url = f"https://www.football-data.co.uk/mmz4281/2425/{code}.csv" # Adjusted for current season
                try:
                    r = requests.get(url, timeout=15)
                    if r.status_code == 200:
                        with open(f"{code}.csv", 'wb') as f:
                            f.write(r.content)
                except: continue
            st.success("AI IMESHACHUKUA DATA MPYA!")

# --- 3. ANALYZER & AI MODEL ---
st.markdown("<h1>V36 PRO AI DESK</h1>", unsafe_allow_html=True)

nation = st.selectbox("🌍 CHAGUA LIGI YA KIKAZI", list(LEAGUE_MAP.keys()))
file_path = f"{LEAGUE_MAP[nation]}.csv"

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    
    # --- REAL AI CORE (FEATURE ENGINEERING) ---
    # Tunatengeneza uelewa wa AI hapa
    df['home_form'] = df.groupby('HomeTeam')['FTHG'].transform(lambda x: x.rolling(5, min_periods=1).mean())
    df['away_form'] = df.groupby('AwayTeam')['FTAG'].transform(lambda x: x.rolling(5, min_periods=1).mean())
    df['home_attack'] = df.groupby('HomeTeam')['FTHG'].transform(lambda x: x.expanding().mean())
    df['away_attack'] = df.groupby('AwayTeam')['FTAG'].transform(lambda x: x.expanding().mean())
    
    df_ai = df.dropna(subset=['home_form', 'away_form', 'home_attack', 'away_attack'])
    
    # Feature Selection
    features = ['home_form', 'away_form', 'home_attack', 'away_attack']
    X = df_ai[features]
    y = (df_ai['FTHG'] + df_ai['FTAG'] >= 3).astype(int) # Target: Over 2.5
    
    # Train AI Model (Random Forest)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # UI for Team Selection
    teams = sorted([str(t) for t in df['HomeTeam'].dropna().unique()])
    col1, col2 = st.columns(2)
    with col1: h_t = st.selectbox("🏠 NYUMBANI", teams)
    with col2: a_t = st.selectbox("🚀 UGENINI", [t for t in teams if t != h_t])

    if st.button("🎯 RUN AI PREDICTION (V36)"):
        # Get Latest Data for Prediction
        h_stats = df[df['HomeTeam'] == h_t].iloc[-1]
        a_stats = df[df['AwayTeam'] == a_t].iloc[-1]
        
        input_data = np.array([[h_stats['home_form'], a_stats['away_form'], h_stats['home_attack'], a_stats['away_attack']]])
        
        # AI Probabilities
        ai_prob = model.predict_proba(input_data)[0][1]
        
        # Calculations for Corners (Traditional Stats)
        h_f = df[df['HomeTeam'] == h_t].tail(8)
        a_f = df[df['AwayTeam'] == a_t].tail(8)
        avg_c = (h_f['HC'].mean() + a_f['AC'].mean())

        # --- OUTPUT DISPLAY ---
        st.markdown("<div class='ai-card'>", unsafe_allow_html=True)
        
        # Rank Engine
        if ai_prob > 0.75: rank = "🌟 TOP PICK (TRENI BANKER)"
        elif ai_prob > 0.60: rank = "✅ VALUE BET"
        else: rank = "⚠️ HIGH RISK"
        
        st.write(f"### {rank}")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("AI GOAL PROB", f"{ai_prob*100:.1f}%")
        with c2: st.metric("xG EXPECTANCY", f"{(h_stats['home_form'] + a_stats['away_form'])/2:.2f}")
        with c3: st.metric("CORNER EXP", f"{avg_c:.1f}")

        st.markdown("---")
        
        # Decision Logic
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### ⚽ GOAL SIGNAL")
            if ai_prob > 0.70:
                st.markdown("<span class='status-ultra'>🔥 OVER 2.5</span>", unsafe_allow_html=True)
                st.write("AI Inasema: Milango iko wazi leo!")
            elif ai_prob > 0.50:
                st.markdown("<span class='status-safe'>✅ OVER 1.5</span>", unsafe_allow_html=True)
                st.write("Ushauri: Hii ni ya treni la uhakika.")
            else:
                st.markdown("<span class='status-danger'>🛑 UNDER 3.5</span>", unsafe_allow_html=True)
                st.write("Ushauri: Mechi ngumu, goli ni shida.")

        with col_b:
            st.markdown("#### 🚩 CORNER SIGNAL")
            if avg_c >= 10.5:
                st.markdown("<span class='status-ultra'>🚩 OVER 8.5</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='status-warning'>🟡 OVER 7.5</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        
        # Portfolio Suggestion
        st.info(f"🛡️ **V36 PORTFOLIO:** Kwa mechi hii, weka 5% tu ya mtaji wako kulingana na AI confidence ya {ai_prob*100:.0f}%.")

else:
    st.warning("⚠️ DATA HAIJAPATIKANA. Bonyeza UPDATE kwenye Sidebar kwanza.")
