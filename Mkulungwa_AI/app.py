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

# --- 0. DATABASE ENGINE (Kwa ajili ya Admin & Login) ---
DB_NAME = "mkulungwa_sys.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (username TEXT, action TEXT, timestamp TEXT)''')
    # Admin wa kwanza
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", ("admin", admin_pw, "admin", "active"))
    conn.commit()
    conn.close()

def log_user(u, action):
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("INSERT INTO logs VALUES (?, ?, ?)", (u, action, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit(); conn.close()

# --- 1. ULTIMATE UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V17.7", layout="wide")
init_db()

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(90deg, #00FF00, #008000); 
        color: white; border-radius: 15px; height: 4em; width: 100%; border: none; font-weight: bold; font-size: 20px;
        box-shadow: 0px 5px 15px rgba(0, 255, 0, 0.4); transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0px 8px 20px rgba(0, 255, 0, 0.6); }
    .result-card-green { background: #1A1C24; padding: 30px; border-radius: 20px; border-left: 10px solid #00FF00; box-shadow: 5px 5px 15px rgba(0,0,0,0.5); }
    .result-card-yellow { background: #1A1C24; padding: 30px; border-radius: 20px; border-left: 10px solid #FFD700; box-shadow: 5px 5px 15px rgba(0,0,0,0.5); }
    .result-card-red { background: #1A1C24; padding: 30px; border-radius: 20px; border-left: 10px solid #FF4B4B; box-shadow: 5px 5px 15px rgba(0,0,0,0.5); }
    .advice-box { 
        background: linear-gradient(135deg, rgba(0,255,0,0.1), rgba(0,0,0,0.5)); 
        border: 2px solid #00FF00; padding: 25px; border-radius: 15px; margin-top: 25px;
        color: #00FF00; font-size: 18px; line-height: 1.6;
    }
    h1 { color: #00FF00; text-align: center; font-size: 60px; font-weight: 900; letter-spacing: -2px; }
    .login-container { max-width: 450px; margin: 0 auto; padding: 40px; background: #1A1C24; border-radius: 20px; border: 1px solid #00FF00; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN LOGIC
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.markdown("<h1>🛡️ ACCESS</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["LOGIN", "CREATE ACCOUNT"])
        
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
                        st.session_state.auth = True
                        st.session_state.user = u
                        st.session_state.role = user[0]
                        st.rerun()
                    else: st.error("❌ AKAUNTI IMEFUNGWA. LIPIA ACCESS!")
                else: st.error("🚨 Username/Password siyo sahihi.")
        
        with tab2:
            nu = st.text_input("New Username", key="r_u")
            np = st.text_input("New Password", type="password", key="r_p")
            if st.button("CREATE MASTER ACCOUNT"):
                hashed_np = hashlib.sha256(np.encode()).hexdigest()
                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                try:
                    c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (nu, hashed_np, "user", "active"))
                    conn.commit(); st.success("✅ Karibu! Sasa Login."); conn.close()
                except: st.error("❌ Jina hili limeshachukuliwa.")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- ADMIN DASHBOARD ---
    if st.session_state.role == "admin":
        with st.sidebar:
            st.markdown("### 🛠️ ADMIN COMMANDS")
            if st.checkbox("OPEN CONTROL PANEL"):
                st.markdown("---")
                conn = sqlite3.connect(DB_NAME)
                users_df = pd.read_sql_query("SELECT username, role, status FROM users", conn)
                for i, row in users_df.iterrows():
                    if row['username'] != 'admin':
                        c1, c2 = st.columns([2, 1])
                        c1.write(f"👤 {row['username']} ({row['status']})")
                        if row['status'] == 'active':
                            if c2.button("BLOCK", key=f"bl_{row['username']}"):
                                conn.execute("UPDATE users SET status='blocked' WHERE username=?", (row['username'],))
                                conn.commit(); st.rerun()
                        else:
                            if c2.button("ACTIVATE", key=f"ac_{row['username']}"):
                                conn.execute("UPDATE users SET status='active' WHERE username=?", (row['username'],))
                                conn.commit(); st.rerun()
                        if st.button("DELETE USER", key=f"del_{row['username']}"):
                            conn.execute("DELETE FROM users WHERE username=?", (row['username'],))
                            conn.commit(); st.rerun()
                conn.close()

    # --- 3. ORIGINAL CODE STARTS HERE (V17.7) ---
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

    with st.sidebar:
        st.markdown(f"### 🛡️ ACTIVE: {st.session_state.user.upper()}")
        if st.button("🚪 LOGOUT"): st.session_state.auth = False; st.rerun()
        st.markdown("---")
        if st.button("🔄 REFRESH GLOBAL DATABASE"):
            all_dfs = []
            p_bar = st.progress(0, text="Establishing Neural Links...")
            leagues = []
            for cat, sub in LEAGUE_MAP.items():
                if cat != "UEFA / EUROPA / CONFERENCE":
                    for n, c in sub.items(): leagues.append((n, c))
            for i, (n, c) in enumerate(leagues):
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/2526/{c}.csv"
                    r = requests.get(url, timeout=12)
                    if r.status_code == 200:
                        with open(f"{c}.csv", 'wb') as f: f.write(r.content)
                        all_dfs.append(pd.read_csv(StringIO(r.text)))
                    p_bar.progress((i+1)/len(leagues), text=f"Processing {n} Analytics...")
                except: continue
            if all_dfs:
                pd.concat(all_dfs, ignore_index=True).to_csv("UEFA_ALL.csv", index=False)
                st.success("DATABASE FULLY SYNCED!")

    st.markdown("<h1>MKULUNGWA AI V17.7</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:20px; color:#888;'>THE ULTIMATE FINAL AUTHORITY</p>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: cat = st.selectbox("📂 CATEGORY", list(LEAGUE_MAP.keys()))
    with c2:
        if cat == "UEFA / EUROPA / CONFERENCE": l_code = "UEFA_ALL"
        else:
            l_name = st.selectbox("🏆 ACTIVE LEAGUE", list(LEAGUE_MAP[cat].keys()))
            l_code = LEAGUE_MAP[cat][l_name]

    df = pd.DataFrame()
    if os.path.exists(f"{l_code}.csv"): df = pd.read_csv(f"{l_code}.csv")

    if not df.empty and 'HomeTeam' in df.columns:
        teams = sorted(df['HomeTeam'].dropna().unique())
        col1, col2 = st.columns(2)
        h_t = col1.selectbox("🏠 HOME SIDE", teams)
        a_t = col2.selectbox("🚀 AWAY SIDE", [t for t in teams if t != h_t])

        if st.button("🎯 RUN FINAL MASTER ANALYSIS"):
            # Original Neural Logic Unchanged
            m_key = f"{h_t}{a_t}{l_code}_FINAL_V17"
            seed = int(hashlib.md5(m_key.encode()).hexdigest(), 16) % (10**6)
            np.random.seed(seed); random.seed(seed)

            st.write("🔍 *Analyzing Match Patterns...*")
            p_bar_an = st.progress(0)
            for i in range(101):
                time.sleep(0.005); p_bar_an.progress(i)

            h_data = df[df['HomeTeam'] == h_t].tail(10)
            a_data = df[df['AwayTeam'] == a_t].tail(10)
            xh = h_data['FTHG'].mean() if not h_data.empty else 1.5
            xa = a_data['FTAG'].mean() if not a_data.empty else 1.2
            total_exp = xh + xa
            conf = 96.8 + (seed % 21) / 10
            if conf > 98.9: conf = 98.9

            if xh > (xa + 0.15): dc_pick = "1X (HOME/DRAW)"
            elif xa > (xh + 0.15): dc_pick = "X2 (AWAY/DRAW)"
            else: dc_pick = "12 (NO DRAW)"

            goal_pick = "OVER 2.5" if total_exp > 2.6 else "OVER 1.5" if total_exp > 1.5 else "UNDER 3.5"
            corner_calc = total_exp * 3.8 + (seed % 2)
            corner_pick = "OVER 9.5" if corner_calc > 9.0 else "OVER 8.5" if corner_calc > 7.5 else "OVER 6.5"

            advice_pool = {
                "goals": [f"🔥 MKULUNGWA FINAL ADVICE: Mechi hii ina harufu ya magoli. Wastani wa {total_exp:.2f} unatoa picha ya mchezo wa wazi."],
                "safety": ["⚖️ MKULUNGWA FINAL ADVICE: Huu ni mchezo wa kimkakati. Double Chance ndio usalama wako."],
                "corners": ["🚩 MKULUNGWA FINAL ADVICE: Takwimu zinaonyesha mechi itapigwa sana pembeni. Corners ni chaguo imara."]
            }
            advice = random.choice(advice_pool["goals" if total_exp > 2.75 else "corners" if corner_calc > 9.2 else "safety"])

            style = "result-card-green" if conf >= 97.8 else "result-card-yellow"
            st.markdown(f"<h2 style='text-align:center; color:#00FF00;'>🛡️ IQ CONFIDENCE: {conf:.1f}%</h2>", unsafe_allow_html=True)
            r1, r2, r3 = st.columns(3)
            r1.markdown(f"<div class='{style}'><h3>🏆 DC</h3><h2>{dc_pick}</h2></div>", unsafe_allow_html=True)
            r2.markdown(f"<div class='{style}'><h3>🚩 CORNERS</h3><h2>{corner_pick}</h2></div>", unsafe_allow_html=True)
            r3.markdown(f"<div class='{style}'><h3>⚽ GOALS</h3><h2>{goal_pick}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='advice-box'>{advice}</div>", unsafe_allow_html=True)
    else:
        st.info("💡 DATABASE OFFLINE: Please run 'REFRESH GLOBAL DATABASE' to activate.")
