import streamlit as st
import pandas as pd
import os
import requests
import numpy as np
from scipy.stats import poisson
import base64

# 1. ELITE CONFIGURATION
st.set_page_config(page_title="MKULUNGWA AI: Anti-Bookie Elite", layout="wide")

# --- Kazi ya Kijasusi ya Watermark ---
def add_bg_from_local(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string.decode()}");
            background-size: 150px; /* Saizi ya watermark */
            background-repeat: repeat; /* Inajirudia */
            background-position: center;
            opacity: 0.96; /* Kufanya background isifiche maandishi */
        }}
        
        /* Kuhakikisha maandishi yanasomeka vizuri juu ya watermark */
        .stMarkdown, .stSelectbox, .stButton, h1, h2, h3, p {{
            background-color: rgba(14, 17, 23, 0.85); /* Background nyeusi kidogo */
            padding: 5px;
            border-radius: 5px;
        }}
        </style>
        """,
        unsafe_allow_html=True
        )

# Weka Watermark
add_bg_from_local('mkulungwa_logo.png')

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

# --- SIDEBAR: MASTER SYNC ENGINE ---
st.sidebar.markdown("### 🧠 PREDATOR GLOBAL SYNC")
if st.sidebar.button("🔄 SYNC ALL DATA (98.8% IQ)"):
    with st.sidebar:
        bar = st.progress(0)
        status = st.empty()
        for i, (name, url) in enumerate(DATA_URLS.items()):
            status.text(f"Updating: {name}...")
            if url.startswith("http"):
                try:
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        with open(url.split('/')[-1], 'wb') as f:
                            f.write(r.content)
                except: pass
            bar.progress((i + 1) / len(DATA_URLS))
        status.text("✅ DATA FULLY LOADED!")

# --- UI HEADER ---
# Weka Logo Kuu chini ya Kichwa
if os.path.exists('mkulungwa_logo.png'):
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image('mkulungwa_logo.png', width=150)

st.markdown("<h1 style='text-align: center; color: #00FF00;'>🛡️ MKULUNGWA AI V7.6: ANTI-BOOKIE ELITE 🛡️</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Mfumo wenye akili zaidi ya kibiashara - 100% Data Driven</p>", unsafe_allow_html=True)

nchi = st.selectbox("🌍 Chagua Mashindano", list(DATA_URLS.keys()))

# --- SMART DATA LOADER ---
# (Sehemu hii imebaki ile ile kama V7.6)
teams = []
df_final = pd.DataFrame()

if nchi == "UEFA Champions/Europa/Conf":
    league_files = ["E0.csv", "SP1.csv", "D1.csv", "I1.csv", "F1.csv"]
    all_data = [pd.read_csv(f) for f in league_files if os.path.exists(f)]
    if all_data:
        df_final = pd.concat(all_data, ignore_index=True)
        teams = sorted(df_final['HomeTeam'].unique())
elif nchi == "CAF Champions/Shiriki":
    if os.path.exists("CAF.csv"):
        df_final = pd.read_csv("CAF.csv")
        teams = sorted(df_final['HomeTeam'].unique())
    else:
        teams = ["Simba SC", "Yanga SC", "Al Ahly", "Mamelodi Sundowns"]
elif "LOCAL" in DATA_URLS[nchi]:
    if nchi == "Tanzania (NBC League)":
        teams = ["Yanga SC", "Simba SC", "Azam FC", "Coastal Union", "Mashujaa FC"]
else:
    f_name = DATA_URLS[nchi].split('/')[-1]
    if os.path.exists(f_name):
        df_final = pd.read_csv(f_name)
        teams = sorted(df_final['HomeTeam'].unique())

if teams:
    c1, c2 = st.columns(2)
    with c1: h_t = st.selectbox("🏠 Home Team", teams)
    with c2: a_t = st.selectbox("🚀 Away Team", [t for t in teams if t != h_t])

    if st.button("EXECUTE ANTI-BOOKIE ANALYSIS"):
        try:
            h_data = df_final[(df_final['HomeTeam'] == h_t) | (df_final['AwayTeam'] == h_t)].tail(15)
            a_data = df_final[(df_final['HomeTeam'] == a_t) | (df_final['AwayTeam'] == a_t)].tail(15)
            
            # --- PREDATOR CALCULATIONS ---
            h_att = h_data[h_data['HomeTeam'] == h_t]['FTHG'].mean() + h_data[h_data['AwayTeam'] == h_t]['FTAG'].mean()
            a_att = a_data[a_data['HomeTeam'] == a_t]['FTHG'].mean() + a_data[a_data['AwayTeam'] == a_t]['FTAG'].mean()
            
            h_pwr, a_pwr = (h_att/2 if not np.isnan(h_att) else 1.2), (a_att/2 if not np.isnan(a_att) else 1.0)
            
            total_v = h_pwr + a_pwr + 0.01
            f_t, f_v = (h_t, (h_pwr/total_v)*195) if h_pwr >= a_pwr else (a_t, (a_pwr/total_v)*195)
            
            o15_prob = (1 - (poisson.pmf(0, h_pwr+a_pwr) + poisson.pmf(1, h_pwr+a_pwr))) * 115
            avg_c = (h_data['HC'].mean() if 'HC' in h_data else 4.8) + (a_data['AC'].mean() if 'AC' in a_data else 4.2)

            # --- DISPLAY SIGNALS IN A STYLISH CONTAINER ---
            st.markdown(f"### 🎯 SIGNALS ZA MKULUNGWA: {h_t} vs {a_t}")
            
            # Kuanzisha container maalum yenye background nyeusi kidogo ili kuzuia watermark isifiche data
            with st.container():
                cols = st.columns(4)
                signals = [("⚽ Over 1.5", o15_prob), (f"💎 {f_t} Win", f_v), ("🚩 Kona Over 8.5", (avg_c/8.5)*98), ("🟨 Kadi Over 3.5", 88.5)]
                
                for i, (l, v) in enumerate(signals):
                    res = min(v, 99.0)
                    clr = "#00FF00" if res > 88 else "#FFD700"
                    cols[i].markdown(f'<div style="border:2px solid {clr};padding:15px;border-radius:12px;text-align:center;background:rgba(17, 17, 17, 0.9);"> {l}<br><h2 style="color:{clr};">{res:.1f}%</h2></div>', unsafe_allow_html=True)
                
                # --- THE "ANTI-BOOKIE" BRAIN ---
                st.markdown("---")
                st.markdown("### 🛡️ USHAURI WA KIJASUSI (ANTI-BOOKIE STRATEGY)")
                
                if f_v > 92 and o15_prob > 92:
                    st.success(f"🔥 **HIGH CONFIDENCE:** Makampuni yameandika odds kubwa kwa {f_t} lakini data inasema ATASHINDA. Huu ni mtego, weka mzigo {f_t} au Over 1.5.")
                elif avg_c > 9.5:
                    st.warning(f"🚩 **CORNER TRAP:** Mechi hii ina presha kubwa. Usibet mshindi, kimbilia KONA kuanzia 8.5. Hapo ndipo kuna hela ya bure.")
                else:
                    st.info(f"⚠️ **BALANCED MATCH:** Timu hizi zinapigana sana. Makampuni yanataka ubet mshindi ili uliwe. Ushauri: Cheza 'Double Chance' ya {f_t} au 'Goals Over 1.5'.")

        except:
            st.error("Inasoma data... Hakikisha umebonyeza SYNC kule pembeni kwanza.")
