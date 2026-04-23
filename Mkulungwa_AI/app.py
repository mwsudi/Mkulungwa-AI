import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
from io import StringIO
from sklearn.ensemble import RandomForestClassifier

# --- 1. UI SETUP (MKULUNGWA PRO STYLE) ---
st.set_page_config(page_title="MKULUNGWA AI V36 PRO - AI DESK", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070A; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(135deg, #00FF00, #008800); 
        color: white; border-radius: 10px; height: 3.8em; width: 100%; border: none; font-weight: 900;
        box-shadow: 0px 4px 15px rgba(0, 255, 0, 0.4);
        cursor: pointer;
    }
    .ai-card { 
        background: #10141D; padding: 25px; border-radius: 15px; 
        border: 1px solid #00FF00; margin-bottom: 20px;
    }
    .status-ultra { color: #00FF00; font-size: 1.8em; font-weight: 900; text-shadow: 1px 1px #000; }
    h1 { color: #00FF00; text-align: center; font-family: 'Arial Black'; letter-spacing: 2px; text-transform: uppercase; }
    h3 { color: #00FF00; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOAD MAP ---
LEAGUE_MAP = {
    "ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", "FRANCE": "F1", 
    "GREECE": "G1", "SCOTLAND": "SC0", "TURKEY": "T1", "NETHERLANDS": "N1", "BELGIUM": "B1"
}

st.markdown("<h1>MKULUNGWA AI V36 PRO</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>🚀 MFUMO WA TRENI LA MILIONI MOJA</h3>", unsafe_allow_html=True)

# --- 3. SIDEBAR CONTROL ---
with st.sidebar:
    st.header("🛰️ AI SYSTEM CONTROL")
    st.write("Sasisha data za dunia hapa:")
    if st.button("🔄 RETRAIN AI (FULL UPDATE)"):
        with st.spinner("Inavuta Data za Dunia..."):
            for name, code in LEAGUE_MAP.items():
                # Tunatumia msimu wa 25/26 kama ilivyo kwenye kodi yako
                url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                try:
                    r = requests.get(url, timeout=15)
                    if r.status_code == 200:
                        with open(f"{code}.csv", 'wb') as f:
                            f.write(r.content)
                except: continue
            st.success("✅ DATA NA AI ZIMEKAA SAWA!")

# --- 4. ANALYZER ENGINE ---
nation = st.selectbox("🌍 CHAGUA LIGI YA KIKAZI", list(LEAGUE_MAP.keys()))
file_path = f"{LEAGUE_MAP[nation]}.csv"

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    
    # --- 5. FEATURE ENGINEERING (REAL AI CORE) ---
    # Rolling forms for AI context
    df['home_form'] = df.groupby('HomeTeam')['FTHG'].transform(lambda x: x.rolling(5, min_periods=1).mean())
    df['away_form'] = df.groupby('AwayTeam')['FTAG'].transform(lambda x: x.rolling(5, min_periods=1).mean())
    df['home_attack'] = df.groupby('HomeTeam')['FTHG'].transform(lambda x: x.expanding().mean())
    df['away_attack'] = df.groupby('AwayTeam')['FTAG'].transform(lambda x: x.expanding().mean())
    
    df_ai = df.dropna(subset=['home_form', 'away_form', 'home_attack', 'away_attack'])
    
    features = ['home_form', 'away_form', 'home_attack', 'away_attack']
    X = df_ai[features]
    y = (df_ai['FTHG'] + df_ai['FTAG'] >= 3).astype(int) # Target: Over 2.5 Goals
    
    # Train Random Forest Model
    model = RandomForestClassifier(n_estimators=300, random_state=42)
    model.fit(X, y)

    # UI for Team Selection
    teams = sorted([str(t) for t in df['HomeTeam'].dropna().unique()])
    col1, col2 = st.columns(2)
    with col1: h_t = st.selectbox("🏠 TIMU YA NYUMBANI", teams)
    with col2: a_t = st.selectbox("🚀 TIMU YA UGENINI", [t for t in teams if t != h_t])

    if st.button("🎯 ANZA UCHAMBUZI WA V36 PRO"):
        # Get Stats for Analysis
        h_stats = df[df['HomeTeam'] == h_t].tail(1)
        a_stats = df[df['AwayTeam'] == a_t].tail(1)
        
        # Historical stats for display
        h_f = df[df['HomeTeam'] == h_t].tail(8)
        a_f = df[df['AwayTeam'] == a_t].tail(8)
        avg_c = (h_f['HC'].mean() + a_f['AC'].mean()) # Corners
        
        # --- AI DECISION LOGIC ---
        input_data = np.array([[
            h_f['FTHG'].mean(), 
            a_f['FTAG'].mean(), 
            df[df['HomeTeam'] == h_t]['FTHG'].mean(), 
            df[df['AwayTeam'] == a_t]['FTAG'].mean()
        ]])
        
        ai_prob = model.predict_proba(input_data)[0][1]

        # --- DISPLAY RESULTS ---
        st.markdown("<div class='ai-card'>", unsafe_allow_html=True)
        
        # Ranking Engine
        if ai_prob > 0.70: rank = "🌟 TOP PICK (MASTERPIECE)"
        elif ai_prob > 0.55: rank = "✅ VALUE BET (SAFE)"
        else: rank = "⚠️ HIGH RISK (CAUTION)"
        
        st.write(f"### {rank}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("AI GOAL PROB", f"{ai_prob*100:.1f}%")
        m2.metric("CORNER EXP", f"{avg_c:.1f}")
        m3.metric("EXPECTED xG", f"{(input_data[0][0] + input_data[0][1]):.2f}")

        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        
        # Decision Signals
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### ⚽ GOAL SIGNAL")
            if ai_prob > 0.70:
                st.markdown("<span class='status-ultra'>🔥 OVER 2.5</span>", unsafe_allow_html=True)
            elif ai_prob > 0.50:
                st.markdown("<span class='status-ultra' style='color:#FFFF00;'>⚡ OVER 1.5</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='status-ultra' style='color:#FF4B4B;'>❌ UNDER 3.5</span>", unsafe_allow_html=True)

        with col_b:
            st.markdown("#### 🚩 CORNER SIGNAL")
            if avg_c >= 10.5:
                st.markdown("<span class='status-ultra'>🚩 OVER 8.5</span>", unsafe_allow_html=True)
            elif avg_c >= 8.5:
                st.markdown("<span class='status-ultra' style='color:#FFFF00;'>🚩 OVER 7.5</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='status-ultra' style='color:#FF4B4B;'>🚩 UNDER RISK</span>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        
        # Staking Plan
        st.info(f"🛡️ **PORTFOLIO ADVICE:** Kulingana na AI confidence ya {ai_prob*100:.0f}%, weka 2% mpaka 5% tu ya mtaji wako hapa.")
else:
    st.info("👋 Karibu Master! Fungua Sidebar (kushoto) na ubonyeze RETRAIN AI ili kupata data mpya ya dunia.")
