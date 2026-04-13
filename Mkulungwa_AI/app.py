import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time

# 1. THEME & APP CONFIGURATION
st.set_page_config(page_title="MKULUNGWA AI V13.1", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    .stButton>button { 
        background-image: linear-gradient(to right, #00FF00 , #008000); 
        color: white; border-radius: 20px; border: none; font-weight: bold; width: 100%;
    }
    .stMetric { background-color: #1A1C24; padding: 15px; border-radius: 15px; border: 1px solid #00FF00; }
    .report-card { border: 2px solid #00FF00; padding: 20px; border-radius: 20px; background: #000; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

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
    "Scotland (Premiership)": "https://www.football-data.co.uk/mmz4281/2526/SC0.csv"
}

# --- SIDEBAR: NEURAL SYNC ---
with st.sidebar:
    st.markdown("### 🧬 PREDATOR NEURAL LINK")
    if st.button("🚀 SYNC GLOBAL DATABASE"):
        with st.status("Initializing Neural Sync...", expanded=True) as status:
            p_bar = st.progress(0)
            for i, (name, url) in enumerate(DATA_URLS.items()):
                try:
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        with open(url.split('/')[-1], 'wb') as f:
                            f.write(r.content)
                except:
                    st.warning(f"Failed to sync: {name}")
                p_bar.progress((i + 1) / len(DATA_URLS))
            status.update(label="✅ SYSTEM CALIBRATED!", state="complete", expanded=False)

# --- HEADER ---
st.markdown("<h1 style='text-align: center; color: #00FF00;'>🛡️ MKULUNGWA AI: THE FINAL PREDATOR V13.1 🛡️</h1>", unsafe_allow_html=True)

nchi = st.selectbox("🌍 CHAGUA MASHINDANO", list(DATA_URLS.keys()))

# --- DATA LOADING ---
df_final = pd.DataFrame()
f_path = DATA_URLS[nchi].split('/')[-1]

if os.path.exists(f_path):
    try:
        df_final = pd.read_csv(f_path)
    except Exception as e:
        st.error(f"Error reading data: {e}")

if not df_final.empty:
    teams = sorted(df_final['HomeTeam'].dropna().unique())
    col_t1, col_t2 = st.columns(2)
    h_t = col_t1.selectbox("🏠 HOME TEAM", teams)
    a_t = col_t2.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

    st.markdown("---")
    st.write("📊 **BOOKIE ODDS (Input values to enable EV+ Radar)**")
    o_col1, o_col2 = st.columns(2)
    b_h_odds = o_col1.number_input(f"Odds za {h_t}", value=2.00, step=0.01)
    b_a_odds = o_col2.number_input(f"Odds za {a_t}", value=2.00, step=0.01)

    if st.button("RUN DEEP PREDATOR COMPUTATION"):
        try:
            # Stats & Monte Carlo
            h_p = df_final[df_final['HomeTeam'] == h_t].tail(10)
            a_p = df_final[df_final['AwayTeam'] == a_t].tail(10)
            
            avg_h, avg_a = df_final['FTHG'].mean(), df_final['FTAG'].mean()
            
            # Poisson Means (Expected Goals)
            xh = (h_p['FTHG'].mean() / avg_h) * (a_p['FTAG'].mean() / avg_a) * avg_h
            xa = (a_p['FTAG'].mean() / avg_a) * (h_p['FTHG'].mean() / avg_h) * avg_a
            
            # Simulations
            sh = np.random.poisson(xh, 10000)
            sa = np.random.poisson(xa, 10000)
            
            ph = (np.sum(sh > sa) / 10000) * 100
            pa = (np.sum(sa > sh) / 10000) * 100
            
            # EV+ & Kelly Criterion
            ev_h = (b_h_odds * (ph/100)) - (1 - (ph/100))
            b_kelly = b_h_odds - 1
            kelly_h = ((b_kelly * (ph/100)) - (1 - (ph/100))) / b_kelly if b_kelly > 0 else 0
            
            # Dynamic Corner Flex IQ
            if 'HC' in df_final.columns and 'AC' in df_final.columns:
                hc_avg = h_p['HC'].mean() if not h_p['HC'].empty else 4.5
                ac_avg = a_p['AC'].mean() if not a_p['AC'].empty else 4.0
                total_c = hc_avg + ac_avg
                c_market = "KONA 7.5 OVER" if total_c > 8.8 else "KONA 6.5 OVER"
                c_conf = min(total_c * 10.5, 98.0)
            else:
                c_market = "KONA DATA N/A"
                c_conf = 0

            # Dashboard Display
            r1, r2, r3, r4 = st.columns(4)
            r1.metric(f"🏠 {h_t}", f"{ph:.1f}%")
            r2.metric(f"🚀 {a_t}", f"{pa:.1f}%")
            r3.metric("📈 Expected Value", f"{ev_h:.2f}")
            r4.metric(f"🚩 {c_market}", f"{c_conf:.1f}%" if c_conf > 0 else "N/A")

            # Final Verdict
            st.markdown(f"""
                <div class='report-card'>
                    <h2 style='color: #00FF00; text-align: center;'>🧠 THE FINAL SNIPER VERDICT</h2>
                    <p style='font-size: 18px;'><b>Primary Selection:</b> {h_t if ph > pa else a_t} Win / Double Chance</p>
                    <p style='font-size: 18px;'><b>Corner Strategy:</b> {c_market}</p>
                    <p style='font-size: 18px;'><b>Kelly Stake Advice:</b> Weka {max(0, kelly_h*100):.1f}% ya mtaji wako.</p>
                </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Uchambuzi umeshindwa: Hakikisha umedownload data kwanza (Sidebar). Error: {e}")
else:
    st.info("Fungua Sidebar kisha bonyeza 'SYNC GLOBAL DATA' kuanza safari.")
