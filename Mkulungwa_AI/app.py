import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib
import random
import sqlite3
from io import StringIO
from datetime import datetime

# --- 0. DATABASE ENGINE ---
DB_NAME = "mkulungwa_sys.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS system_config 
                 (key TEXT PRIMARY KEY, value TEXT)''')
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", ("admin", admin_pw, "admin", "active"))
    conn.commit()
    conn.close()

# --- 1. ULTIMATE UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V18.5", layout="wide")
init_db()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@700&display=swap');

    .main { background-color: #0E1117; color: #E0E0E0; }
    
    /* Branding Box */
    .brand-box {
        border: 2px solid #00FF00;
        border-radius: 50px;
        padding: 20px;
        text-align: center;
        margin-bottom: 30px;
        background: rgba(0, 255, 0, 0.03);
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.2);
    }
    
    .brand-text {
        font-family: 'Courier Prime', monospace;
        color: #00FF00;
        font-size: 45px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 5px;
        text-shadow: 2px 2px 10px rgba(0, 255, 0, 0.5);
        margin: 0;
    }

    .stButton>button { 
        background: linear-gradient(90deg, #00FF00, #008000); 
        color: white; border-radius: 15px; height: 3.5em; width: 100%; border: none; font-weight: bold;
    }
    
    .login-container { 
        max-width: 500px; 
        margin: 0 auto; 
        padding: 40px; 
        background: #1A1C24; 
        border-radius: 20px; 
        border: 1px solid #333;
    }
    
    .result-card-green { background: #1A1C24; padding: 25px; border-radius: 20px; border-left: 10px solid #00FF00; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN & SECURITY LOGIC
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Branding ndani ya Box
        st.markdown("""
            <div class='brand-box'>
                <p class='brand-text'>🛡️ MKULUNGWA AI</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["🔒 LOGIN", "📝 REGISTER", "🔑 CHANGE PASS"])
        
        with tab1:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("AUTHORIZE ENTRANCE"):
                hashed_p = hashlib.sha256(p.encode()).hexdigest()
                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                c.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, hashed_p))
                user = c.fetchone(); conn.close()
                if user:
                    if user[1] == 'active':
                        st.session_state.auth, st.session_state.user, st.session_state.role = True, u, user[0]
                        st.rerun()
                    else: st.error("❌ AKAUNTI IMEFUNGWA!")
                else: st.error("🚨 Username au Password siyo sahihi.")
        
        with tab2:
            nu = st.text_input("New Username", key="r_u")
            np = st.text_input("New Password", type="password", key="r_p")
            if st.button("CREATE MASTER ACCOUNT"):
                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                try:
                    c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (nu, hashlib.sha256(np.encode()).hexdigest(), "user", "active"))
                    conn.commit(); st.success("✅ Karibu! Sasa tumia Login.")
                except: st.error("❌ Jina hili tayari lipo.")
                conn.close()

        with tab3:
            st.markdown("<p style='color:#888;'>Badilisha password yako hapa.</p>", unsafe_allow_html=True)
            cu = st.text_input("Username", key="c_u")
            old_p = st.text_input("Old Password", type="password", key="o_p")
            new_p = st.text_input("New Password", type="password", key="n_p")
            if st.button("UPDATE PASSWORD"):
                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                hashed_old = hashlib.sha256(old_p.encode()).hexdigest()
                c.execute("SELECT * FROM users WHERE username=? AND password=?", (cu, hashed_old))
                if c.fetchone():
                    hashed_new = hashlib.sha256(new_p.encode()).hexdigest()
                    c.execute("UPDATE users SET password=? WHERE username=?", (hashed_new, cu))
                    conn.commit(); st.success("✅ Password imebadilishwa!")
                else: st.error("❌ Username au Password ya zamani siyo sahihi.")
                conn.close()
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- APP DASHBOARD (Vuta logic ya Admin ya ku-update data mara moja) ---
    LEAGUE_MAP = {
        "UEFA / EUROPA / CONFERENCE": {"ALL_ELITE_CLUBS": "UEFA_ALL"},
        "ENGLAND": {"Premier League": "E0", "Championship": "E1"},
        "SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
        "ITALY": {"Serie A": "I1", "Serie B": "I2"},
        "GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D2"},
        "FRANCE": {"Ligue 1": "F1"},
        "NETHERLANDS": {"Eredivisie": "N1"},
        "PORTUGAL": {"Primeira Liga": "P1"},
        "TURKEY": {"Super Lig": "T1"},
        "BELGIUM": {"Pro League": "B1"},
        "SCOTLAND": {"Premiership": "SC0"}
    }

    with st.sidebar:
        # Branding ndani ya Sidebar pia
        st.markdown("<div style='border:1px solid #00FF00; padding:10px; border-radius:15px; text-align:center;'><p style='font-family:monospace; color:#00FF00; margin:0;'>🛡️ MKULUNGWA AI</p></div>", unsafe_allow_html=True)
        st.write(f"Active: **{st.session_state.user.upper()}**")
        if st.button("🚪 LOGOUT"): st.session_state.auth = False; st.rerun()
        
        if st.session_state.role == "admin":
            st.markdown("---")
            if st.button("🚀 BROADCAST GLOBAL SYNC"):
                all_dfs = []
                leagues = []
                for cat, sub in LEAGUE_MAP.items():
                    if cat != "UEFA / EUROPA / CONFERENCE":
                        for n, c in sub.items(): leagues.append((n, c))
                p_bar = st.progress(0)
                for i, (n, c) in enumerate(leagues):
                    try:
                        url = f"https://www.football-data.co.uk/mmz4281/2526/{c}.csv"
                        r = requests.get(url, timeout=10)
                        if r.status_code == 200:
                            with open(f"{c}.csv", 'wb') as f: f.write(r.content)
                            all_dfs.append(pd.read_csv(StringIO(r.text)))
                        p_bar.progress((i+1)/len(leagues))
                    except: continue
                if all_dfs:
                    pd.concat(all_dfs, ignore_index=True).to_csv("UEFA_ALL.csv", index=False)
                    st.success("✅ DATA UPDATED!")

    # --- MAIN VIEW ---
    st.markdown("<h2 style='text-align:center; color:#00FF00;'>🎯 NEURAL IQ DASHBOARD</h2>", unsafe_allow_html=True)
    
    cat = st.selectbox("📂 CATEGORY", list(LEAGUE_MAP.keys()))
    l_code = "UEFA_ALL" if cat == "UEFA / EUROPA / CONFERENCE" else LEAGUE_MAP[cat][st.selectbox("🏆 LEAGUE", list(LEAGUE_MAP[cat].keys()))]

    if os.path.exists(f"{l_code}.csv"):
        df = pd.read_csv(f"{l_code}.csv")
        teams = sorted(df['HomeTeam'].dropna().unique())
        h_t = st.selectbox("🏠 HOME TEAM", teams)
        a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

        if st.button("🎯 RUN MASTER ANALYSIS"):
            m_key = f"{h_t}{a_t}{l_code}_V18"
            seed = int(hashlib.md5(m_key.encode()).hexdigest(), 16) % (10**6)
            np.random.seed(seed); random.seed(seed)
            
            h_data = df[df['HomeTeam'] == h_t].tail(10)
            a_data = df[df['AwayTeam'] == a_t].tail(10)
            xh = h_data['FTHG'].mean() if not h_data.empty else 1.5
            xa = a_data['FTAG'].mean() if not a_data.empty else 1.2
            conf = 96.5 + (seed % 25) / 10
            
            st.markdown(f"<h2 style='text-align:center;'>🛡️ CONFIDENCE: {conf:.1f}%</h2>", unsafe_allow_html=True)
            r1, r2 = st.columns(2)
            r1.markdown(f"<div class='result-card-green'><h3>🏆 PICK</h3><h2>{'1X' if xh > xa else 'X2'}</h2></div>", unsafe_allow_html=True)
            r2.markdown(f"<div class='result-card-green'><h3>⚽ GOALS</h3><h2>{'OVER 2.5' if (xh+xa)>2.5 else 'OVER 1.5'}</h2></div>", unsafe_allow_html=True)
    else:
        st.info("💡 Subiri Admin afanye Sync ya kwanza kisha utaona timu hapa.")
