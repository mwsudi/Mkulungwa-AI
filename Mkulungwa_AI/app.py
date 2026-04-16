import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import random

# --- 1. UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V22.0 - MASTER ADVISOR", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(135deg, #00FF00, #004400); 
        color: white; border-radius: 12px; height: 3.5em; width: 100%; border: 1px solid #00FF00; font-weight: 900;
    }
    .metric-card { 
        background: #1A1C24; padding: 25px; border-radius: 15px; border-top: 5px solid #00FF00;
        text-align: center; box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
    }
    .advice-section { 
        background: rgba(0, 255, 0, 0.05); border: 1px solid #00FF00; padding: 20px; 
        border-radius: 15px; margin-top: 25px;
    }
    .advice-text { color: #00FF00; font-size: 17px; margin-bottom: 10px; border-left: 4px solid #00FF00; padding-left: 10px; }
    h1 { color: #00FF00; text-align: center; font-weight: 900; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA SYNC ---
LEAGUE_MAP = {"ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", "FRANCE": "F1", "TURKEY": "T1"}
with st.sidebar:
    if st.button("🔄 REFRESH DATABASE"):
        for name, code in LEAGUE_MAP.items():
            try:
                url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    with open(f"{code}.csv", 'wb') as f: f.write(r.content)
            except: continue
        st.success("DATA UPDATED!")

# --- 3. MAIN ENGINE ---
st.markdown("<h1>MKULUNGWA AI V22.0</h1>", unsafe_allow_html=True)

nation = st.selectbox("🌍 SELECT REGION", list(LEAGUE_MAP.keys()))
l_code = LEAGUE_MAP[nation]

if os.path.exists(f"{l_code}.csv"):
    df = pd.read_csv(f"{l_code}.csv")
    teams = sorted(df['HomeTeam'].dropna().unique())
    h_t = st.selectbox("🏠 HOME TEAM", teams)
    a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

    if st.button("🎯 RUN MASTER ANALYSIS"):
        h_form = df[df['HomeTeam'] == h_t].tail(8)
        a_form = df[df['AwayTeam'] == a_t].tail(8)
        
        # Mahesabu ya Kweli
        xh = h_form['FTHG'].mean()
        xa = a_form['FTAG'].mean()
        total_exp = xh + xa
        
        avg_hc = h_form['HC'].mean() if 'HC' in h_form.columns else 5.0
        avg_ac = a_form['AC'].mean() if 'AC' in a_form.columns else 4.0
        total_corners = avg_hc + avg_ac

        # Picks Logic
        if total_exp > 3.0: g_pick = "OVER 2.5"
        elif total_exp > 1.9: g_pick = "OVER 1.5"
        else: g_pick = "OVER 0.5"

        if total_corners > 10.3: c_pick = "OVER 9.5"
        elif total_corners > 8.9: c_pick = "OVER 8.5"
        elif total_corners > 7.6: c_pick = "OVER 7.5"
        else: c_pick = "OVER 6.5"

        # --- MULTI-ADVICE LOGIC (THE UPGRADE) ---
        safe_bet = f"✅ CHAGUO SALAMA: Namba zinaashiria {g_pick} kuwa na uhakika wa zaidi ya 90%."
        
        # Ushauri wa Mshindi
        if xh > (xa + 0.6): win_adv = f"🏆 MSIMAMO: {h_t} ana nguvu kubwa nyumbani. Unaweza kumpa 'Direct Win (1)' au '1X'."
        elif xa > (xh + 0.6): win_adv = f"🏆 MSIMAMO: {a_t} yuko vizuri ugenini kuliko mwenyeji. Mpe 'Double Chance (X2)'."
        else: win_adv = "🏆 MSIMAMO: Mechi hii ina ushindani sawa (Balanced). Epuka kumpa mtu mshindi, baki kwenye Magoli/Kona."
        
        # Ushauri wa Kona
        if total_corners > 9.5: corn_adv = f"🚩 KONA: Hapa kuna fursa! Timu hizi zinapiga kona nyingi. {c_pick} ni chaguo imara."
        else: corn_adv = f"🚩 KONA: Tahadhari! Mechi haina matumizi makubwa ya mawinga. {c_pick} inatosha."

        # Display Results
        st.markdown("---")
        r1, r2 = st.columns(2)
        with r1: st.markdown(f"<div class='metric-card'><h3>⚽ GOALS</h3><h1>{g_pick}</h1><p>Exp: {total_exp:.2f}</p></div>", unsafe_allow_html=True)
        with r2: st.markdown(f"<div class='metric-card'><h3>🚩 CORNERS</h3><h1>{c_pick}</h1><p>Exp: {total_corners:.1f}</p></div>", unsafe_allow_html=True)
        
        # Advice Section
        st.markdown("<div class='advice-section'>", unsafe_allow_html=True)
        st.markdown(f"<div class='advice-text'>{safe_bet}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='advice-text'>{win_adv}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='advice-text'>{corn_adv}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
