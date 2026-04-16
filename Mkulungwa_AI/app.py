import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import random

# --- 1. UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V21.0 - MASTER ADVICE", layout="wide")

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
    .advice-box { 
        background: rgba(0, 255, 0, 0.1); border: 2px dashed #00FF00; padding: 20px; 
        border-radius: 15px; margin-top: 25px; color: #00FF00; font-size: 18px; font-weight: bold;
    }
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
st.markdown("<h1>MKULUNGWA AI V21.0</h1>", unsafe_allow_html=True)

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
        
        # Mahesabu
        xh = h_form['FTHG'].mean(); xh_c = h_form['FTAG'].mean()
        xa = a_form['FTAG'].mean(); xa_c = a_form['FTHG'].mean()
        total_exp = ((xh + xa_c)/2) + ((xa + xh_c)/2)
        
        avg_hc = h_form['HC'].mean() if 'HC' in h_form.columns else 5.0
        avg_ac = a_form['AC'].mean() if 'AC' in a_form.columns else 4.0
        total_corners = avg_hc + avg_ac

        # Picks
        if total_exp > 3.0: g_pick = "OVER 2.5"
        elif total_exp > 1.9: g_pick = "OVER 1.5"
        else: g_pick = "OVER 0.5"

        if total_corners > 10.3: c_pick = "OVER 9.5"
        elif total_corners > 8.9: c_pick = "OVER 8.5"
        elif total_corners > 7.6: c_pick = "OVER 7.5"
        else: c_pick = "OVER 6.5"

        # --- REKEBISHO LA USHAURI (THE FIX) ---
        advices = []
        if total_exp > 3.2:
            advices.append(f"🔥 USHAURI: Timu hizi zina funguka sana. {g_pick} ni uhakika wa 90%.")
        elif total_exp < 1.8:
            advices.append(f"🛡️ USHAURI: Mechi ya ulinzi mkali sana. Usiguse magoli mengi, baki na {g_pick}.")
        
        if total_corners > 10.0:
            advices.append(f"🚩 USHAURI: Hapa kuna fujo ya krosi. Weka mzigo kwenye {c_pick}.")
        
        if not advices:
            # Hapa nimeongeza 'f' mwanzo ili kodi isomeke
            final_advice = f"⚖️ USHAURI: Mechi imekaa katikati. Chaguo salama zaidi ni {g_pick} au {c_pick}."
        else:
            final_advice = random.choice(advices)

        # Output Display
        st.markdown("---")
        r1, r2 = st.columns(2)
        with r1: st.markdown(f"<div class='metric-card'><h3>⚽ GOALS</h3><h1>{g_pick}</h1><p>Exp: {total_exp:.2f}</p></div>", unsafe_allow_html=True)
        with r2: st.markdown(f"<div class='metric-card'><h3>🚩 CORNERS</h3><h1>{c_pick}</h1><p>Exp: {total_corners:.1f}</p></div>", unsafe_allow_html=True)
        
        st.markdown(f"<div class='advice-box'>{final_advice}</div>", unsafe_allow_html=True)
