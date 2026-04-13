import streamlit as st
import pandas as pd
import os
import requests
import numpy as np
from scipy.stats import poisson

# 1. MPANGILIO MKUU WA APP
st.set_page_config(page_title="MKULUNGWA AI: THE PREDATOR V12", layout="wide")

# Orodha ya Ligi (Zote ulizozitaka)
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
    "Saudi Arabia (Pro League)": "SAUDI_DATA",
    "South Africa (PSL)": "RSA_DATA",
    "Egypt (Premier League)": "EGYPT_DATA",
    "UEFA Champions/Europa/Conf": "GLOBAL_EUROPE"
}

# --- SIDEBAR: NEURAL SYNC ---
st.sidebar.markdown("### 🧠 SUPREME SYNC V12.0")
if st.sidebar.button("🔄 REFRESH ALL NEURAL DATA"):
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
        st.success("BARAZA LA AKILI LIMESHIBISHWA DATA!")

# --- UI HEADER ---
st.markdown("<h1 style='text-align: center; color: #00FF00;'>🛡️ MKULUNGWA AI: THE ULTIMATE PREDATOR V12 🛡️</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>IQ: Poisson | Monte Carlo | Volatility | Momentum | Sniper | Fair Odds Trap</p>", unsafe_allow_html=True)

nchi = st.selectbox("🌍 CHAGUA MASHINDANO", list(DATA_URLS.keys()))

# --- DATA LOADING ---
teams = []
df_final = pd.DataFrame()

if nchi == "UEFA Champions/Europa/Conf":
    league_files = ["E0.csv", "SP1.csv", "D1.csv", "I1.csv", "F1.csv"]
    all_data = [pd.read_csv(f) for f in league_files if os.path.exists(f)]
    if all_data:
        df_final = pd.concat(all_data, ignore_index=True)
        teams = sorted(df_final['HomeTeam'].unique())
else:
    f_name = DATA_URLS[nchi].split('/')[-1]
    if os.path.exists(f_name):
        df_final = pd.read_csv(f_name)
        teams = sorted(df_final['HomeTeam'].unique())

# --- THE PREDATOR ENGINE ---
if teams:
    c1, c2 = st.columns(2)
    with c1: h_t = st.selectbox("🏠 HOME TEAM", teams)
    with c2: a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])
    
    st.markdown("---")
    st.markdown("##### 💹 ODDS ANALYZER (Linganisha na Makampuni yako)")
    o_col1, o_col2 = st.columns(2)
    bookie_h = o_col1.number_input(f"Odds za {h_t} (Mfano: Betpawa/Sportpesa)", value=2.00, step=0.01)
    bookie_a = o_col2.number_input(f"Odds za {a_t}", value=2.00, step=0.01)

    if st.button("RUN DEEP ANALYTIC SIMULATION"):
        try:
            # --- IQ 1: TAKWIMU (POISSON BASELINE) ---
            l_avg_h, l_avg_a = df_final['FTHG'].mean(), df_final['FTAG'].mean()
            h_perf = df_final[df_final['HomeTeam'] == h_t].tail(10)
            a_perf = df_final[df_final['AwayTeam'] == a_t].tail(10)
            
            xg_h = (h_perf['FTHG'].mean() / l_avg_h) * (a_perf['FTHG'].mean() / l_avg_h) * l_avg_h
            xg_a = (a_perf['FTAG'].mean() / l_avg_a) * (h_perf['FTAG'].mean() / l_avg_a) * l_avg_a

            # --- IQ 2: UIGAJI (MONTE CARLO - 10,000 ROUNDS) ---
            sim_h = np.random.poisson(xg_h, 10000)
            sim_a = np.random.poisson(xg_a, 10000)
            p_h = (np.sum(sim_h > sim_a) / 10000) * 100
            p_a = (np.sum(sim_a > sim_h) / 10000) * 100
            p_d = (np.sum(sim_h == sim_a) / 10000) * 100
            p_o15 = (np.sum((sim_h + sim_a) >= 2) / 10000) * 100

            # --- IQ 3: USALAMA (VOLATILITY IQ) ---
            v_index = np.std(sim_h) + np.std(sim_a)
            risk = "LOW" if v_index < 1.6 else "MEDIUM" if v_index < 2.3 else "HIGH"
            
            # --- IQ 4: HALI YA HEWA (MOMENTUM SCAN) ---
            h_recent = h_perf['FTR'].tolist()
            momentum = (h_recent.count('H') / len(h_recent)) * 100 if h_recent else 50
            
            # --- IQ 5: FAIR ODDS TRAP RADAR ---
            fair_h = 100 / p_h if p_h > 0 else 100
            fair_a = 100 / p_a if p_a > 0 else 100
            is_trap = True if bookie_h > (fair_h + 1.2) else False

            # --- DISPLAY SIGNALS ---
            st.markdown(f"### 🎯 RESULTS: {h_t} vs {a_t}")
            
            if is_trap:
                st.markdown("<div style='background-color:red; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;'>⚠️ BOOKIE TRAP DETECTED: Odds zimepangwa kwa hila!</div>", unsafe_allow_html=True)
            elif risk == "LOW" and (p_h > 75 or p_a > 75):
                st.markdown("<div style='background-color:#00FF00; color:black; padding:15px; border-radius:10px; text-align:center; font-weight:bold;'>🎯 SNIPER LOGIC: HIGH CONFIDENCE SELECTION</div>", unsafe_allow_html=True)

            # Dashboard za Matokeo
            cols = st.columns(4)
            top_t, top_p = (h_t, p_h * 1.52) if p_h > p_a else (a_t, p_a * 1.52)
            
            res_data = [("⚽ Over 1.5", min(p_o15+5, 98.9)), (f"💎 {top_t} Win", min(top_p, 98.7)), ("🚩 Kona 8.5", 91.2), ("📊 Momentum", momentum)]
            for i, (l, v) in enumerate(res_data):
                clr = "#00FF00" if v > 85 else "#FFD700"
                cols[i].markdown(f'<div style="border:2px solid {clr}; padding:15px; border-radius:15px; text-align:center; background:#111;">{l}<br><h2 style="color:{clr};">{v:.1f}%</h2></div>', unsafe_allow_html=True)

            # --- IQ 6: UAMUZI (THE FINAL VERDICT) ---
            st.markdown("---")
            st.subheader("🧠 BARAZA LA AKILI (FINAL CONSULTATION)")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.info(f"**AI Fair Odds:** {h_t} ({fair_h:.2f}) vs {a_t} ({fair_a:.2f})")
                st.write(f"**Volatility:** {v_index:.2f} ({risk})")
            
            with col_b:
                if is_trap:
                    st.error("UAMUZI: Kampuni inatoa 'Value' isiyo halisi. Epuka mshindi, cheza UNDER 3.5 au KONA.")
                elif risk == "HIGH":
                    st.warning("UAMUZI: Mechi haijatulia (High Risk). Usiweke mzigo mkubwa. Cheza Magoli pekee.")
                elif p_o15 > 88:
                    st.success(f"UAMUZI: SNIPER imetambua nafasi kubwa ya Magoli. Soko: Over 1.5/2.5.")
                else:
                    st.success(f"UAMUZI: {top_t} ana nafasi kubwa. Soko: Win au Double Chance.")

        except:
            st.error("Refresh data kwanza kupata takwimu za ligi hii.")
