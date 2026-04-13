import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time

# 1. SETTINGS ZA KISASA
st.set_page_config(page_title="PREDATOR V12.4: CORNER MASTER", layout="wide")

DATA_URLS = {
    "England (Premier League)": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "Spain (La Liga)": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
    "Germany (Bundesliga)": "https://www.football-data.co.uk/mmz4281/2526/D1.csv",
    "Italy (Serie A)": "https://www.football-data.co.uk/mmz4281/2526/I1.csv",
    "France (Ligue 1)": "https://www.football-data.co.uk/mmz4281/2526/F1.csv",
    "Netherlands (Eredivisie)": "https://www.football-data.co.uk/mmz4281/2526/N1.csv",
    "Belgium (Pro League)": "https://www.football-data.co.uk/mmz4281/2526/B1.csv",
    "Portugal (Primeira Liga)": "https://www.football-data.co.uk/mmz4281/2526/P1.csv",
    "Turkey (Super Lig)": "https://www.football-data.co.uk/mmz4281/2526/T1.csv",
    "Scotland (Premiership)": "https://www.football-data.co.uk/mmz4281/2526/SC0.csv",
    "UEFA Champions/Europa/Conf": "GLOBAL_EUROPE"
}

# --- SIDEBAR: MATRIX UPDATE BAR ---
with st.sidebar:
    st.markdown("### 🧬 PREDATOR NEURAL LINK")
    if st.button("🚀 LAUNCH DATABASE UPDATE"):
        with st.status("Inapakia Data za Dunia...", expanded=True) as status:
            progress_bar = st.progress(0)
            for i, (name, url) in enumerate(DATA_URLS.items()):
                if url.startswith("http"):
                    try:
                        r = requests.get(url, timeout=7)
                        with open(url.split('/')[-1], 'wb') as f: f.write(r.content)
                    except: pass
                progress_bar.progress((i + 1) / len(DATA_URLS))
            status.update(label="✅ DATA UPDATED & LIVE!", state="complete", expanded=False)

# --- UI HEADER ---
st.markdown("<h1 style='text-align: center; color: #00FF00;'>🛡️ PREDATOR V12.4: CORNER MASTER 🛡️</h1>", unsafe_allow_html=True)

nchi = st.selectbox("🌍 CHAGUA MASHINDANO", list(DATA_URLS.keys()))

# --- DATA LOADING ---
df_final = pd.DataFrame()
if nchi == "UEFA Champions/Europa/Conf":
    files = ["E0.csv", "SP1.csv", "D1.csv", "I1.csv", "F1.csv"]
    all_d = [pd.read_csv(f) for f in files if os.path.exists(f)]
    if all_d: df_final = pd.concat(all_d)
else:
    fname = DATA_URLS[nchi].split('/')[-1]
    if os.path.exists(fname): df_final = pd.read_csv(fname)

if not df_final.empty:
    teams = sorted(df_final['HomeTeam'].unique())
    col1, col2 = st.columns(2)
    h_t = col1.selectbox("🏠 HOME TEAM", teams)
    a_t = col2.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

    if st.button("EXECUTE TURBO ANALYSIS"):
        # 1. Stats Baseline
        l_h, l_a = df_final['FTHG'].mean(), df_final['FTAG'].mean()
        h_p = df_final[df_final['HomeTeam'] == h_t].tail(10)
        a_p = df_final[df_final['AwayTeam'] == a_t].tail(10)
        
        # 2. Monte Carlo (10,000 Rounds)
        xh = (h_p['FTHG'].mean() / l_h) * (a_p['FTHG'].mean() / l_h) * l_h
        xa = (a_p['FTAG'].mean() / l_a) * (h_p['FTAG'].mean() / l_a) * l_a
        sh, sa = np.random.poisson(xh, 10000), np.random.poisson(xa, 10000)
        
        ph, pa = (np.sum(sh > sa)/100), (np.sum(sa > sh)/100)
        po15 = np.sum((sh + sa) >= 2) / 100

        # 3. CORNER INTELLIGENCE (IQ: 6.5 vs 7.5 Decision)
        # HC = Home Corners, AC = Away Corners
        h_c = h_p['HC'].mean() if 'HC' in h_p.columns else 4.0
        a_c = a_p['AC'].mean() if 'AC' in a_p.columns else 3.5
        total_corners = h_c + a_c
        
        # Logic: Data ndiyo inaamua soko lipi liandikwe
        if total_corners >= 8.5:
            corner_market = "KONA 7.5 OVER"
            corner_conf = min(total_corners * 10, 96.2)
        else:
            corner_market = "KONA 6.5 OVER"
            corner_conf = min(total_corners * 12, 94.8)

        # Volatility
        vix = np.std(sh) + np.std(sa)

        # --- DISPLAY RESULTS ---
        st.markdown(f"### 🎯 Battle Report: {h_t} vs {a_t}")
        res1, res2, res3, res4 = st.columns(4)
        res1.metric(f"🏠 {h_t}", f"{ph:.1f}%")
        res2.metric(f"🚀 {a_t}", f"{pa:.1f}%")
        res3.metric("⚽ Magoli 1.5+", f"{po15:.1f}%")
        res4.metric(f"🚩 {corner_market}", f"{corner_conf:.1f}%")

        st.markdown("---")
        
        # --- FINAL PREDATOR VERDICT ---
        st.subheader("🧠 PREDATOR FINAL VERDICT")
        if vix > 2.3:
            st.error(f"⚠️ HIGH VOLATILITY: Mechi haitabiriki kwa mshindi (1X2). PIGA {corner_market} KWA USALAMA.")
        elif ph > 78 or pa > 78:
            winner = h_t if ph > pa else a_t
            st.success(f"🔥 SNIPER SELECTION: {winner} Kushinda. Pendekezo la ziada: {corner_market}.")
        elif po15 > 90:
            st.info(f"📊 GOAL PREDATOR: Uwezekano wa magoli ni mkubwa. Tumia soko la Over 1.5 au {corner_market}.")
        else:
            st.warning(f"📊 BALANCED MATCH: Timu zote zimepishana kidogo. Soko bora: {corner_market}.")

        with st.expander("🔬 View Data Breakdown"):
            st.write(f"Wastani wa Kona (Total Expected): {total_corners:.2f}")
            st.write(f"Hatari (Risk Score): {vix:.2f}")

else:
    st.info("Fungua Sidebar kisha bonyeza 'LAUNCH DATABASE UPDATE' ili kuanza safari.")
