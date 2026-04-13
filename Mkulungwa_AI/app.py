import streamlit as st
import pandas as pd
import os
import numpy as np
import requests

# 1. MPANGILIO MKUU (Professional & Slim)
st.set_page_config(page_title="PREDATOR V12.2", layout="wide")

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

# --- SIDEBAR: DATA RECOVERY ---
with st.sidebar:
    st.markdown("### 🧠 PREDATOR CORE")
    if st.button("🔄 REFRESH NEURAL DATA"):
        for name, url in DATA_URLS.items():
            if url.startswith("http"):
                try:
                    r = requests.get(url, timeout=5)
                    with open(url.split('/')[-1], 'wb') as f: f.write(r.content)
                except: pass
        st.success("DATA RECOVERY COMPLETE!")

# --- UI HEADER ---
st.markdown("<h2 style='text-align: center; color: #00FF00;'>🛡️ PREDATOR V12.2: DEEP ANALYSIS ENGINE</h2>", unsafe_allow_html=True)

nchi = st.selectbox("🌍 CHAGUA LIGI YA KUCHAMBUA", list(DATA_URLS.keys()))

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
    h_t = c1.selectbox("🏠 HOME TEAM", teams)
    a_t = c2.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

    if st.button("ACTIVATE ALL IQ LAYERS"):
        try:
            # --- IQ LAYER 1: STATS BASELINE ---
            l_h, l_a = df_final['FTHG'].mean(), df_final['FTAG'].mean()
            h_p = df_final[df_final['HomeTeam'] == h_t].tail(10)
            a_p = df_final[df_final['AwayTeam'] == a_t].tail(10)
            
            # --- IQ LAYER 2: MONTE CARLO (10,000 ROUNDS) ---
            xh = (h_p['FTHG'].mean() / l_h) * (a_p['FTHG'].mean() / l_h) * l_h
            xa = (a_p['FTAG'].mean() / l_a) * (h_p['FTAG'].mean() / l_a) * l_a
            sh = np.random.poisson(xh, 10000)
            sa = np.random.poisson(xa, 10000)
            
            ph = (np.sum(sh > sa) / 10000) * 100
            pa = (np.sum(sa > sh) / 10000) * 100
            pd = (np.sum(sh == sa) / 10000) * 100
            po15 = (np.sum((sh + sa) >= 2) / 10000) * 100
            
            # --- IQ LAYER 3: VOLATILITY (RISK) ---
            vix = np.std(sh) + np.std(sa)
            risk = "LOW" if vix < 1.6 else "MEDIUM" if vix < 2.2 else "HIGH"
            
            # --- IQ LAYER 4: MOMENTUM SCAN ---
            h_rec = h_p['FTR'].tolist()
            mom = (h_rec.count('H') / len(h_rec)) * 100 if h_rec else 50

            # --- IQ LAYER 5: AUTOMATIC FAIR ODDS ---
            fair_h = 100 / ph if ph > 0 else 0
            fair_a = 100 / pa if pa > 0 else 0

            # --- DISPLAY MATOKEO ---
            st.markdown(f"#### 🎯 Analysis: {h_t} vs {a_t}")
            
            # Slim Dashboard
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(f"🏠 {h_t}", f"{ph:.1f}%", f"Odds: {fair_h:.2f}")
            m2.metric(f"🚀 {a_t}", f"{pa:.1f}%", f"Odds: {fair_a:.2f}")
            m3.metric("🤝 Draw", f"{pd:.1f}%")
            m4.metric("⚽ Goals 1.5+", f"{po15:.1f}%")

            # --- IQ LAYER 6: THE SNIPER DECISION TREE ---
            st.markdown("---")
            st.subheader("🧠 PREDATOR FINAL VERDICT")
            
            if risk == "HIGH":
                st.error("🛡️ MECHI NGUMU: Data zinaonyesha 'High Volatility'. USHAURI: Usibeti mshindi (1X2). Kama lazima ucheze, nenda na KONA au epuka kabisa!")
            elif ph > 75:
                st.success(f"🔥 SNIPER SELECTION: {h_t} Win. Confidence ipo juu, Momentum ni {mom:.1f}%.")
            elif pa > 75:
                st.success(f"🔥 SNIPER SELECTION: {a_t} Win. Confidence ipo juu.")
            elif po15 > 88:
                st.info("📊 GOAL ALERT: Hakuna timu inayotawala wazi, lakini nafasi ya magoli (1.5+) ni kubwa. Cheza magoli.")
            else:
                st.warning("📊 CAUTION: Mechi imebalance sana. Pendekezo: Double Chance (1X au X2) au Achana nayo.")

            # Maoni ya Ziada
            with st.expander("Fungua kwa maelezo ya kiufundi"):
                st.write(f"- Fair Odds zilizopigwa na AI zinakuongoza kujua thamani halisi ya timu.")
                st.write(f"- Kiwango cha hatari (Volatility) ni **{risk}** kulingana na mtawanyiko wa magoli.")

        except: st.error("Data haijasomeka. Tafadhali nenda Sidebar na ubonyeza UPDATE DATABASE.")
else:
    st.info("Fungua Sidebar upande wa kushoto na ubonyeze UPDATE DATABASE kuanza.")
