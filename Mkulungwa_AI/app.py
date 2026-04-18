import streamlit as st
import pandas as pd
import os
import requests
from io import StringIO

# --- 1. UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V33.5 - MILLIONAIRE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(135deg, #00FF00, #004400); 
        color: white; border-radius: 12px; height: 3.5em; width: 100%; border: 1px solid #00FF00; font-weight: 900;
    }
    .express-card { 
        background: #1A1C24; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #00FF00; margin-bottom: 15px;
    }
    .status-safe { color: #00FF00; font-size: 1.4em; font-weight: 900; }
    .status-warning { color: #FFFF00; font-size: 1.2em; font-weight: bold; }
    .status-danger { color: #FF4B4B; font-size: 1.1em; font-weight: bold; }
    h1, h3 { color: #00FF00; text-align: center; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE GLOBAL UPDATE ENGINE ---
LEAGUE_MAP = {
    "ENGLAND": "E0", "SPAIN": "SP1", "ITALY": "I1", "GERMANY": "D1", "FRANCE": "F1", 
    "GREECE": "G1", "SCOTLAND": "SC0", "TURKEY": "T1", "NETHERLANDS": "N1", "BELGIUM": "B1"
}

with st.sidebar:
    st.header("🛰️ SATELITE CONTROL")
    st.write("Sasisha data za mechi za leo hapa:")
    if st.button("🔄 UPDATE DATA YA DUNIA"):
        with st.spinner("Inavuta data mpya ya dunia..."):
            all_dfs = []
            for name, code in LEAGUE_MAP.items():
                url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                try:
                    r = requests.get(url, timeout=15)
                    if r.status_code == 200:
                        with open(f"{code}.csv", 'wb') as f:
                            f.write(r.content)
                        temp_df = pd.read_csv(StringIO(r.text))
                        if not temp_df.empty:
                            essential = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HC', 'AC']
                            all_dfs.append(temp_df[[c for c in essential if c in temp_df.columns]])
                except:
                    continue
            st.success("✅ DATA IMEKAA SAWA!")

# --- 3. ANALYZER ENGINE ---
st.markdown("<h1>MKULUNGWA AI V33.5</h1>", unsafe_allow_html=True)
st.markdown("### 🚂 MFUMO WA TRENI LA MILIONI MOJA")

nation = st.selectbox("🌍 CHAGUA LIGI", list(LEAGUE_MAP.keys()))

file_path = f"{LEAGUE_MAP[nation]}.csv"
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    teams = sorted([str(t) for t in df['HomeTeam'].dropna().unique()])
    h_t = st.selectbox("🏠 TIMU YA NYUMBANI", teams)
    a_t = st.selectbox("🚀 TIMU YA UGENINI", [t for t in teams if t != h_t])

    if st.button("🎯 ANZA UCHAMBUZI WA KITALAMU"):
        h_f = df[df['HomeTeam'] == h_t].tail(8)
        a_f = df[df['AwayTeam'] == a_t].tail(8)
        
        # Calculations
        avg_g = (h_f['FTHG'].mean() + a_f['FTAG'].mean())
        avg_c = (h_f['HC'].mean() + a_f['AC'].mean())
        
        st.markdown("---")
        st.markdown("<div class='express-card'>", unsafe_allow_html=True)
        
        # --- KONA SECTION ---
        st.markdown("### 🚩 KONA (CORNERS)")
        if avg_c >= 11.0:
            st.markdown(f"<span class='status-safe'>🟢 KIJANI (BANKER): UHAKIKA WA TRENI (Exp {avg_c:.1f})</span>", unsafe_allow_html=True)
            st.write("Mkakati: **BET OVER 8.5** (Kama haipo, weka **OVER 7.5**)")
        elif avg_c >= 9.0:
            st.markdown(f"<span class='status-warning'>🟡 NJANO (SAFE): SALAMA KIASI (Exp {avg_c:.1f})</span>", unsafe_allow_html=True)
            st.write("Mkakati: **BET OVER 7.5** (Kama haipo, weka **OVER 6.5**)")
        else:
            st.markdown(f"<span class='status-danger'>❌ NYEKUNDU: USIWEKE KWENYE TRENI</span>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # --- MAGOLI SECTION (DYNAMIC) ---
        st.markdown("### ⚽ MAGOLI (GOALS)")
        if avg_g >= 3.2:
            st.markdown(f"<span class='status-safe'>🔥 MAGOLI: UHAKIKA WA OVER 2.5 (Exp {avg_g:.2f})</span>", unsafe_allow_html=True)
            st.write("Ushauri: **OVER 2.5 GOALS** (Odds Kubwa)")
        elif avg_g >= 2.2:
            st.markdown(f"<span class='status-safe'>✅ MAGOLI: UHAKIKA WA OVER 1.5 (Exp {avg_g:.2f})</span>", unsafe_allow_html=True)
            st.write("Ushauri: **OVER 1.5 GOALS** (Treni Safe)")
        elif avg_g >= 1.2:
            st.markdown(f"<span class='status-warning'>⚠️ MAGOLI: OVER 0.5 TU (Exp {avg_g:.2f})</span>", unsafe_allow_html=True)
            st.write("Ushauri: **OVER 0.5 GOALS**")
        else:
            st.markdown(f"<span class='status-danger'>🛑 TAHADHARI: MECHI YA UNDER (Exp {avg_g:.2f})</span>", unsafe_allow_html=True)
            st.write("Ushauri: **UNDER 3.5 GOALS**")

        st.markdown("</div>", unsafe_allow_html=True)
        
        # HITIMISHO YA MILIONI
        if avg_c >= 10.8 and avg_g >= 2.2:
            st.success("🏆 HII NI 'MASTERPIECE'! Inafaa kuongeza dau kwenye mkeka wa leo.")
else:
    st.info("Fungua Sidebar (kushoto) na ubonyeze UPDATE DATA YA DUNIA kuanza.")
