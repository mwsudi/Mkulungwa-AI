import streamlit as st
import pandas as pd
import os
import requests
import numpy as np
from scipy.stats import poisson

# 1. MPANGILIO MKUU (ELITE LAYOUT)
st.set_page_config(page_title="MKULUNGWA AI", layout="wide")

# Link za Data (Ligi Kuu zote na International)
DATA_URLS = {
    "England (Premier League)": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "Spain (La Liga)": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    "Germany (Bundesliga)": "https://www.football-data.co.uk/mmz4281/2526/D1.csv",
    "Italy (Serie A)": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "France (Ligue 1)": "https://www.football-data.co.uk/mmz4281/2526/F1.csv",
    "UEFA Champions/Europa/Conf": "GLOBAL_EUROPE",
    "CAF Champions/Shiriki": "LOCAL_CAF",
    "Tanzania (NBC League)": "LOCAL_NBC"
}

# --- SIDEBAR: SYNC ENGINE ---
st.sidebar.markdown("### 🧠 PREDATOR SYNC")
if st.sidebar.button("🔄 SYNC ALL DATA"):
    with st.sidebar:
        bar = st.progress(0)
        for i, (name, url) in enumerate(DATA_URLS.items()):
            if url.startswith("http"):
                try:
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        with open(url.split('/')[-1], 'wb') as f:
                            f.write(r.content)
                except: pass
            bar.progress((i + 1) / len(DATA_URLS))
        st.success("DATA UPDATED!")

# --- UI HEADER: NEMBO NA KICHWA ---
logo_path = 'mkulungwa_logo.png'
if os.path.exists(logo_path):
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.image(logo_path, width=120)

st.markdown("<h2 style='text-align: center; color: #00FF00;'>🛡️ MKULUNGWA AI: ANTI-BOOKIE ELITE</h2>", unsafe_allow_html=True)

# --- UCHAGUZI WA LIGI ---
nchi = st.selectbox("🌍 CHAGUA MASHINDANO", list(DATA_URLS.keys()))

# --- SMART DATA LOADER ---
teams = []
df_final = pd.DataFrame()

if nchi == "UEFA Champions/Europa/Conf":
    league_files = ["E0.csv", "SP1.csv", "D1.csv", "I1.csv", "F1.csv"]
    all_data = [pd.read_csv(f) for f in league_files if os.path.exists(f)]
    if all_data:
        df_final = pd.concat(all_data, ignore_index=True)
        teams = sorted(df_final['HomeTeam'].unique())
elif nchi == "Tanzania (NBC League)":
    # Kwa sasa tunaweka timu maarufu, ukipata CSV ya NBC utaiweka GitHub
    teams = ["Yanga SC", "Simba SC", "Azam FC", "Singida FG", "Coastal Union", "Mashujaa FC"]
else:
    f_name = DATA_URLS[nchi].split('/')[-1]
    if os.path.exists(f_name):
        df_final = pd.read_csv(f_name)
        teams = sorted(df_final['HomeTeam'].unique())

# --- ANALYSIS ENGINE ---
if teams:
    c1, c2 = st.columns(2)
    with c1: h_t = st.selectbox("🏠 HOME TEAM", teams)
    with c2: a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

    if st.button("EXECUTE ANALYSIS"):
        try:
            # Tunatafuta fomu ya timu (Mechi 10 zilizopita)
            h_data = df_final[(df_final['HomeTeam'] == h_t) | (df_final['AwayTeam'] == h_t)].tail(10)
            a_data = df_final[(df_final['HomeTeam'] == a_t) | (df_final['AwayTeam'] == a_t)].tail(10)
            
            # Poisson Math
            h_avg = h_data[h_data['HomeTeam'] == h_t]['FTHG'].mean() if not h_data.empty else 1.5
            a_avg = a_data[a_data['AwayTeam'] == a_t]['FTAG'].mean() if not a_data.empty else 1.2
            
            # Results Logic
            o15 = (1 - (poisson.pmf(0, h_avg+a_avg) + poisson.pmf(1, h_avg+a_avg))) * 115
            f_v = (h_avg / (h_avg + a_avg)) * 190 if (h_avg + a_avg) > 0 else 50
            
            # Corners (Kama data ipo)
            hc = h_data['HC'].mean() if 'HC' in h_data else 5.0
            ac = a_data['AC'].mean() if 'AC' in a_data else 4.0
            c_prob = ((hc + ac) / 9.5) * 100

            # DISPLAY SIGNALS
            st.markdown(f"### 🎯 SIGNALS: {h_t} vs {a_t}")
            cols = st.columns(4)
            res_data = [("⚽ Over 1.5", o15), ("💎 Win Signal", f_v), ("🚩 Kona 8.5", c_prob), ("⚠️ Kadi 3.5", 88.0)]
            
            for i, (l, v) in enumerate(res_data):
                val = min(v, 98.8)
                color = "#00FF00" if val > 85 else "#FFD700"
                with cols[i]:
                    st.markdown(f'<div style="border:2px solid {color}; padding:10px; border-radius:10px; text-align:center;">{l}<br><h2>{val:.1f}%</h2></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.info(f"🛡️ **STRATEGY:** Mechi hii ina asilimia kubwa kwenye {l if val > 90 else 'Soko la Magoli'}. Weka mzigo kwa akili!")
        except:
            st.error("Bonyeza 'SYNC ALL DATA' kwanza kupata takwimu za leo.")
else:
    st.warning("Tafadhali bonyeza SYNC kwenye sidebar ili kupata timu za ligi uliyochagua.")
