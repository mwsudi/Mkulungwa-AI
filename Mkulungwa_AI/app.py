import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import random
from io import StringIO

# --- 1. UI SETUP (DARK THEME) ---
st.set_page_config(page_title="MKULUNGWA AI V23.0 - GLOBAL BEAST", layout="wide")

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

# --- 2. EXTENDED LEAGUE MAPPING ---
LEAGUE_MAP = {
    "ENGLAND": "E0", 
    "SPAIN": "SP1", 
    "ITALY": "I1", 
    "GERMANY": "D1", 
    "FRANCE": "F1", 
    "NETHERLANDS (Uholanzi)": "N1",
    "PORTUGAL": "P1",
    "BELGIUM": "B1",
    "SCOTLAND": "SC0",
    "TURKEY": "T1",
    "UEFA LITE (CL/EL/ECL)": "UEFA_ALL"
}

# --- 3. GLOBAL SYNC ENGINE ---
with st.sidebar:
    st.header("🛰️ GLOBAL SYNC")
    if st.button("🔄 REFRESH ALL LEAGUES"):
        all_dfs = []
        with st.spinner("Connecting to Global Databases..."):
            for name, code in LEAGUE_MAP.items():
                if code == "UEFA_ALL": continue # Tutaishughulikia chini
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                        all_dfs.append(pd.read_csv(StringIO(r.text)))
                except: continue
            
            # Kutengeneza UEFA LITE kwa kuunganisha ligi zote kubwa
            if all_dfs:
                combined_df = pd.concat(all_dfs, ignore_index=True)
                combined_df.to_csv("UEFA_ALL.csv", index=False)
        st.success("DATABASE FULLY LOADED!")

# --- 4. MAIN ENGINE ---
st.markdown("<h1>MKULUNGWA AI V23.0</h1>", unsafe_allow_html=True)

nation = st.selectbox("🌍 SELECT LEAGUE / REGION", list(LEAGUE_MAP.keys()))
l_code = LEAGUE_MAP[nation]

if os.path.exists(f"{l_code}.csv"):
    df = pd.read_csv(f"{l_code}.csv")
    teams = sorted(df['HomeTeam'].dropna().unique())
    h_t = st.selectbox("🏠 HOME TEAM", teams)
    a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

    if st.button("🎯 RUN MASTER ANALYSIS"):
        # Isolation Logic
        h_form = df[df['HomeTeam'] == h_t].tail(8)
        a_form = df[df['AwayTeam'] == a_t].tail(8)
        
        if len(h_form) < 2:
            st.warning("Data ni chache, inatumia wastani wa ligi.")
            h_form = df.tail(20) # Fallback
            
        # Mahesabu
        xh = h_form['FTHG'].mean(); xh_c = h_form['FTAG'].mean()
        xa = a_form['FTAG'].mean(); xa_c = a_form['FTHG'].mean()
        total_exp = ((xh + xa_c)/2) + ((xa + xh_c)/2)
        
        avg_hc = h_form['HC'].mean() if 'HC' in h_form.columns else 4.5
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

        # Multi-Advice Engine
        safe_bet = f"✅ UHAKIKA: Namba zinaashiria {g_pick} ni salama zaidi."
        
        if xh > (xa + 0.5): win_adv = f"🏆 MSIMAMO: {h_t} ana faida ya nyumbani. Mpe 1X."
        elif xa > (xh + 0.5): win_adv = f"🏆 MSIMAMO: {a_t} ana uwezo wa kushinda ugenini. Mpe X2."
        else: win_adv = "🏆 MSIMAMO: Timu zinalingana nguvu sana (Tight Match)."

        corn_adv = f"🚩 KONA: Tarajia kona {int(total_corners)} hivi. {c_pick} inatosha."

        # Display
        st.markdown("---")
        r1, r2 = st.columns(2)
        with r1: st.markdown(f"<div class='metric-card'><h3>⚽ GOALS</h3><h1>{g_pick}</h1><p>Exp: {total_exp:.2f}</p></div>", unsafe_allow_html=True)
        with r2: st.markdown(f"<div class='metric-card'><h3>🚩 CORNERS</h3><h1>{c_pick}</h1><p>Exp: {total_corners:.1f}</p></div>", unsafe_allow_html=True)
        
        st.markdown("<div class='advice-section'>", unsafe_allow_html=True)
        st.markdown(f"<div class='advice-text'>{safe_bet}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='advice-text'>{win_adv}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='advice-text'>{corn_adv}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Tafadhali Refresh Database kwenye Sidebar kuanza.")

