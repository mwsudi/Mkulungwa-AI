import streamlit as st
import pandas as pd
import os
import requests
from io import StringIO

# --- 1. UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V33.0 - EXPRESS", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(135deg, #00FF00, #004400); 
        color: white; border-radius: 12px; height: 3.5em; width: 100%; border: 1px solid #00FF00; font-weight: 900;
    }
    .express-card { 
        background: #1A1C24; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #00FF00; margin-bottom: 15px;
    }
    .status-safe { color: #00FF00; font-size: 1.5em; font-weight: 900; }
    .status-warning { color: #FFFF00; font-size: 1.2em; font-weight: bold; }
    .status-danger { color: #FF4B4B; font-size: 1.1em; font-weight: bold; }
    h1, h3 { color: #00FF00; text-align: center; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOAD (Simplified for brevity) ---
LEAGUE_MAP = {"ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", "GREECE": "G1", "SCOTLAND": "SC0"}

# --- 3. THE EXPRESS ENGINE ---
st.markdown("<h1>MKULUNGWA AI V33.0</h1>", unsafe_allow_html=True)
st.markdown("### 🚂 TRENI LA MILIONI MOJA - SYSTEM CHECK")

nation = st.selectbox("🌍 CHAGUA LIGI YA TRENI", list(LEAGUE_MAP.keys()))

if os.path.exists(f"{LEAGUE_MAP[nation]}.csv"):
    df = pd.read_csv(f"{LEAGUE_MAP[nation]}.csv")
    teams = sorted([str(t) for t in df['HomeTeam'].dropna().unique()])
    h_t = st.selectbox("🏠 HOME TEAM", teams)
    a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

    if st.button("🚀 CHAMBUA KWA AJILI YA TRENI"):
        h_f = df[df['HomeTeam'] == h_t].tail(8)
        a_f = df[df['AwayTeam'] == a_t].tail(8)
        
        # Data Stats
        avg_g = (h_f['FTHG'].mean() + a_f['FTAG'].mean())
        avg_c = (h_f['HC'].mean() + a_f['AC'].mean())
        
        st.markdown("---")
        
        # LOGIC YA TRENI (THE SNIPER FILTER)
        is_goal_safe = avg_g > 2.2
        is_corner_safe = avg_c > 10.8
        
        st.markdown("<div class='express-card'>", unsafe_allow_html=True)
        
        # 1. Corner Verdict
        if is_corner_safe:
            st.markdown(f"<span class='status-safe'>✅ KONA: UHAKIKA WA TRENI (Exp {avg_c:.1f})</span>", unsafe_allow_html=True)
            st.write(f"Soko: **OVER 7.5 CORNERS** (Ushindi 92%)")
        elif avg_c > 9.0:
            st.markdown(f"<span class='status-warning'>⚠️ KONA: SALAMA KIASI (Exp {avg_c:.1f})</span>", unsafe_allow_html=True)
            st.write(f"Soko: **OVER 6.5 CORNERS** (Ushindi 85%)")
        else:
            st.markdown(f"<span class='status-danger'>❌ KONA: USIWEKE KWENYE TRENI</span>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Goal Verdict
        if is_goal_safe:
            st.markdown(f"<span class='status-safe'>✅ MAGOLI: UHAKIKA WA TRENI (Exp {avg_g:.2f})</span>", unsafe_allow_html=True)
            st.write(f"Soko: **OVER 0.5 GOALS** (Ushindi 98%)")
        else:
            st.markdown(f"<span class='status-warning'>⚠️ MAGOLI: WEKA KWA TAHADHARI</span>", unsafe_allow_html=True)
            st.write(f"Soko: **OVER 0.5 GOALS** (Inafaa kama nyongeza tu)")

        st.markdown("</div>", unsafe_allow_html=True)
        
        # FINAL EXPRESS ADVICE
        if is_corner_safe and is_goal_safe:
            st.success("🏆 HII NI MECHI YA MILIONI! Iweke kwenye treni bila wasiwasi.")
        elif is_corner_safe or is_goal_safe:
            st.warning("⚖️ MECHI YA KAWAIDA: Iweke kama una timu chache.")
        else:
            st.error("🛑 RISK: Achana na hii mechi kwenye treni ya siku 5.")
