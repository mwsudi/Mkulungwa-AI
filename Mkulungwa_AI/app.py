import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time

# 1. MPANGILIO WA KISASA (Matrix Theme)
st.set_page_config(page_title="PREDATOR V12.3", layout="wide")

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

# --- SIDEBAR: ADVANCED NEURAL SYNC ---
with st.sidebar:
    st.markdown("### 🧬 PREDATOR NEURAL LINK")
    if st.button("🚀 LAUNCH DATABASE UPDATE"):
        with st.status("Inapakia Data za Dunia...", expanded=True) as status:
            progress_bar = st.progress(0)
            for i, (name, url) in enumerate(DATA_URLS.items()):
                st.write(f"🔄 Inavuta data za: {name}...")
                if url.startswith("http"):
                    try:
                        r = requests.get(url, timeout=7)
                        with open(url.split('/')[-1], 'wb') as f: f.write(r.content)
                    except: st.error(f"Feli kwenye {name}")
                time.sleep(0.1)
                progress_bar.progress((i + 1) / len(DATA_URLS))
            status.update(label="✅ DATABASE IS NOW LIVE!", state="complete", expanded=False)

# --- UI HEADER ---
st.markdown("<h1 style='text-align: center; color: #00FF00;'>🛡️ PREDATOR V12.3: ADVANCED TURBO 🛡️</h1>", unsafe_allow_html=True)

nchi = st.selectbox("🌍 SELECT COMPETITION", list(DATA_URLS.keys()))

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
        # Takwimu Layers
        l_h, l_a = df_final['FTHG'].mean(), df_final['FTAG'].mean()
        h_p = df_final[df_final['HomeTeam'] == h_t].tail(10)
        a_p = df_final[df_final['AwayTeam'] == a_t].tail(10)
        
        # Monte Carlo Simulation (10k Rounds)
        xh = (h_p['FTHG'].mean() / l_h) * (a_p['FTHG'].mean() / l_h) * l_h
        xa = (a_p['FTAG'].mean() / l_a) * (h_p['FTAG'].mean() / l_a) * l_a
        sh, sa = np.random.poisson(xh, 10000), np.random.poisson(xa, 10000)
        
        ph, pa, pd_rate = (np.sum(sh > sa)/100), (np.sum(sa > sh)/100), (np.sum(sh == sa)/100)
        po15 = np.sum((sh + sa) >= 2) / 100

        # Risk & Momentum Logic
        vix = np.std(sh) + np.std(sa)
        momentum = (h_p['FTR'].tolist().count('H') * 10) + (a_p['FTR'].tolist().count('A') * 5)
        
        # Fair Odds Generation
        fh, fa = (100 / ph if ph > 0 else 0), (100 / pa if pa > 0 else 0)

        # --- THE ADVANCED DASHBOARD ---
        st.markdown(f"### 🎯 Battle Report: {h_t} vs {a_t}")
        
        res1, res2, res3 = st.columns(3)
        res1.metric("🏠 Home Domination", f"{ph:.1f}%", f"Odds: {fh:.2f}")
        res2.metric("🚀 Away Pressure", f"{pa:.1f}%", f"Odds: {fa:.2f}")
        res3.metric("⚽ Over 1.5 Chance", f"{po15:.1f}%")

        st.markdown("---")
        
        # Final Advanced Verdict Logic
        conf_score = max(ph, pa)
        if vix > 2.3:
            st.error(f"⚠️ HIGH VOLATILITY DETECTED ({vix:.2f}): Mechi hii ina mtego mkubwa. Takwimu hazijatulia. USHAURI: Epuka 1X2, nenda na Kona au kimbia!")
        elif conf_score > 78:
            winner = h_t if ph > pa else a_t
            st.success(f"🔥 SNIPER EXECUTION: {winner} ana nguvu kubwa sana leo. Confidence Index: {conf_score:.1f}%.")
        elif po15 > 90:
            st.info(f"📊 GOAL PREDATOR: Timu zote zina uwezo wa kufumania nyavu. Soko bora: OVER 1.5 au GG.")
        else:
            st.warning("📊 BALANCED MATCH: Hakuna mbabe wa wazi. Pendekezo: Double Chance au Under 3.5.")

        with st.expander("🔬 View Neural Breakdown"):
            st.write(f"Standard Deviation (Vix): {vix:.2f}")
            st.write(f"Momentum Score: {momentum}")
            st.write(f"Monte Carlo Draw Rate: {pd_rate:.1f}%")
else:
    st.info("Tafadhali fungua Sidebar na ubonyeze 'LAUNCH DATABASE UPDATE' ili kuanza safari.")
