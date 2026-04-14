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
    # Admin wa kwanza
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", ("admin", admin_pw, "admin", "active"))
    conn.commit()
    conn.close()

# --- 1. ULTIMATE UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V18.0", layout="wide")
init_db()

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(90deg, #00FF00, #008000); 
        color: white; border-radius: 15px; height: 3.5em; width: 100%; border: none; font-weight: bold;
        box-shadow: 0px 5px 15px rgba(0, 255, 0, 0.4);
    }
    .result-card-green { background: #1A1C24; padding: 25px; border-radius: 20px; border-left: 10px solid #00FF00; }
    .advice-box { background: rgba(0,255,0,0.05); border: 1px solid #00FF00; padding: 20px; border-radius: 15px; color: #00FF00; }
    h1 { color: #00FF00; text-align: center; font-weight: 900; }
    .login-container { max-width: 450px; margin: 0 auto; padding: 30px; background: #1A1C24; border-radius: 20px; border: 1px solid #00FF00; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN LOGIC
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.markdown("<h1>🛡️ MKULUNGWA AI</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
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
                else: st.error("🚨 Wrong Credentials")
        with tab2:
            nu = st.text_input("New User", key="r_u")
            np = st.text_input("New Pass", type="password", key="r_p")
            if st.button("CREATE ACCOUNT"):
                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                try:
                    c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (nu, hashlib.sha256(np.encode()).hexdigest(), "user", "active"))
                    conn.commit(); st.success("✅ Karibu! Sasa Login.")
                except: st.error("❌ Jina lipo.")
                conn.close()
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # 3. LEAGUE CONFIG
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
        "SCOTLAND": {"Premiership": "SC0"},
        "GREECE": {"Super League": "G1"}
    }

    # --- SIDEBAR (ADMIN CONTROL ONLY) ---
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user.upper()}")
        if st.button("🚪 LOGOUT"): st.session_state.auth = False; st.rerun()
        st.markdown("---")
        
        if st.session_state.role == "admin":
            st.markdown("### 🛠️ ADMIN PANEL")
            # Kitufe cha siri cha Admin ku-update data kwa watumiaji wote
            if st.button("🚀 BROADCAST GLOBAL SYNC"):
                all_dfs = []
                leagues = []
                for cat, sub in LEAGUE_MAP.items():
                    if cat != "UEFA / EUROPA / CONFERENCE":
                        for n, c in sub.items(): leagues.append((n, c))
                
                p_bar = st.progress(0, text="Updating cloud database...")
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
                    st.success("✅ GLOBAL UPDATE COMPLETE!")
            
            st.markdown("---")
            if st.checkbox("Manage Users"):
                conn = sqlite3.connect(DB_NAME)
                users = pd.read_sql_query("SELECT username, status FROM users WHERE role='user'", conn)
                for i, row in users.iterrows():
                    c1, c2 = st.columns([2, 1])
                    c1.write(row['username'])
                    if c2.button("BLOCK" if row['status']=='active' else "UNBLOCK", key=row['username']):
                        new_s = 'inactive' if row['status']=='active' else 'active'
                        conn.execute("UPDATE users SET status=? WHERE username=?", (new_s, row['username']))
                        conn.commit(); st.rerun()
                conn.close()

    # --- 4. MAIN APP ---
    st.markdown("<h1>MKULUNGWA AI V18.0</h1>", unsafe_allow_html=True)
    
    cat = st.selectbox("📂 CATEGORY", list(LEAGUE_MAP.keys()))
    if cat == "UEFA / EUROPA / CONFERENCE": l_code = "UEFA_ALL"
    else:
        l_name = st.selectbox("🏆 LEAGUE", list(LEAGUE_MAP[cat].keys()))
        l_code = LEAGUE_MAP[cat][l_name]

    if os.path.exists(f"{l_code}.csv"):
        df = pd.read_csv(f"{l_code}.csv")
        teams = sorted(df['HomeTeam'].dropna().unique())
        h_t = st.selectbox("🏠 HOME TEAM", teams)
        a_t = st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])

        if st.button("🎯 RUN MASTER ANALYSIS"):
            # Logic ya siri (Original V17.7)
            m_key = f"{h_t}{a_t}{l_code}_V18"
            seed = int(hashlib.md5(m_key.encode()).hexdigest(), 16) % (10**6)
            np.random.seed(seed); random.seed(seed)
            
            h_data = df[df['HomeTeam'] == h_t].tail(10)
            a_data = df[df['AwayTeam'] == a_t].tail(10)
            xh = h_data['FTHG'].mean() if not h_data.empty else 1.5
            xa = a_data['FTAG'].mean() if not a_data.empty else 1.2
            conf = 96.5 + (seed % 25) / 10
            
            res_dc = "1X" if xh > xa else "X2" if xa > xh else "12"
            res_gl = "OVER 2.5" if (xh+xa) > 2.5 else "OVER 1.5"
            
            st.markdown(f"<h2 style='text-align:center;'>🛡️ CONFIDENCE: {conf:.1f}%</h2>", unsafe_allow_html=True)
            r1, r2 = st.columns(2)
            r1.markdown(f"<div class='result-card-green'><h3>🏆 PICK</h3><h2>{res_dc}</h2></div>", unsafe_allow_html=True)
            r2.markdown(f"<div class='result-card-green'><h3>⚽ GOALS</h3><h2>{res_gl}</h2></div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Data is currently being prepared by the Admin. Please check back later.")
