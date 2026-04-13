import streamlit as st
import pandas as pd
import os
import numpy as np
import requests

# 1. MPANGILIO MKUU (Design Safi)
st.set_page_config(page_title="PREDATOR V12.1", layout="wide")

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

# --- SIDEBAR & SYNC ---
with st.sidebar:
    st.header("🧠 PREDATOR CORE")
    if st.button("🔄 UPDATE DATABASE"):
        for name, url in DATA_URLS.items():
            if url.startswith("http"):
                try:
                    r = requests.get(url, timeout=5)
                    with open(url.split('/')[-1], 'wb') as f: f.write(r.content)
                except: pass
        st.success("DATA UPDATED!")

# --- UI HEADER ---
st.markdown("<h2 style='text-align: center; color: #00FF00;'>🛡️ PREDATOR V12.1: SLIM ENGINE</h2>", unsafe_allow_html=True)

nchi = st.selectbox("🌍 LIGI", list(DATA_URLS.keys()))

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
    c1, c2 = st.columns(2)
    h_t = c1.selectbox("🏠 HOME", teams)
    a_t = c2.selectbox("🚀 AWAY", [t for t in teams if t != h_t])
    
    # Odds za Hiari
    st.markdown("---")
    b_h = st.number_input(f"Odds za {h_t} (Weka 0 kama huna)", value=0.00)

    if st.button("EXECUTE ANALYSIS"):
        try:
            # Leta Takwimu
            l_h, l_a = df_final['FTHG'].mean(), df_final['FTAG'].mean()
            h_p = df_final[df_final['HomeTeam'] == h_t].tail(8)
            a_p = df_final[df_final['AwayTeam'] == a_t].tail(8)
            
            # Poisson & Simulation
            xh = (h_p['FTHG'].mean() / l_h) * (a_p['FTHG'].mean() / l_h) * l_h
            xa = (a_p['FTAG'].mean() / l_a) * (h_p['FTAG'].mean() / l_a) * l_a
            sh = np.random.poisson(xh, 10000)
            sa = np.random.poisson(xa, 10000)
            
            ph = (np.sum(sh > sa) / 10000) * 100
            pa = (np.sum(sa > sh) / 10000) * 100
            po15 = (np.sum((sh + sa) >= 2) / 10000) * 100
            fair_h = 100 / ph if ph > 0 else 0
            
            # Volatility (Risk)
            vix = np.std(sh) + np.std(sa)
            risk_lbl = "LOW" if vix < 1.6 else "HIGH"
            
            # --- DISPLAY MATOKEO (SLIM VERSION) ---
            st.markdown(f"#### 🎯 Verdict: {h_t} vs {a_t}")
            
            # Row ya kwanza ya matokeo
            m1, m2, m3 = st.columns(3)
            m1.metric(f"💎 {h_t}", f"{ph:.1f}%", f"Fair: {fair_h:.2f}")
            m2.metric(f"💎 {a_t}", f"{pa:.1f}%", f"Fair: {100/pa:.2f}")
            m3.metric("⚽ Over 1.5", f"{po15:.1f}%")

            # Mtego wa Odds (Trap Radar)
            if b_h > 0 and b_h > (fair_h + 1.1):
                st.error(f"⚠️ TRAP ALERT: Odds za kampuni ({b_h}) ni kubwa mno. Kuna kitu kimefichwa!")
            
            # Final Summary
            st.markdown("---")
            if risk_lbl == "HIGH":
                st.warning("🛡️ UAMUZI: Mechi ina hatari. Pendekezo: Over 1.5 au Kona.")
            elif ph > 70 or pa > 70:
                win_t = h_t if ph > pa else a_t
                st.success(f"🔥 SNIPER: {win_t} Win / Double Chance. Confidence: HIGH.")
            else:
                st.info("📊 UAMUZI: Mechi imebalance. Double Chance ndio salama zaidi.")

        except: st.error("Tafadhali Refresh data kwanza.")
else:
    st.warning("Fungua Sidebar kisha bonyeza 'UPDATE DATABASE' kuanza.")
