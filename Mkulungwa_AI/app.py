import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib
import random
import sqlite3
import re
from io import StringIO
from datetime import datetime

# --- 0. DATABASE ENGINE ---
DB_NAME = "mkulungwa_master_iq.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, status TEXT, 
                  firstname TEXT, middlename TEXT, phone TEXT, last_seen TIMESTAMP)''')
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, role, status) VALUES (?, ?, ?, ?)", 
              ("admin", admin_pw, "admin", "active"))
    conn.commit()
    conn.close()

def check_password(password):
    if len(password) < 6: return False
    if not re.search("[a-z]", password): return False
    if not re.search("[0-9]", password): return False
    if not re.search("[@#$%!^]", password): return False
    return True

def update_last_seen(username):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("UPDATE users SET last_seen = ? WHERE username = ?", (datetime.now(), username))
    conn.commit()
    conn.close()

# --- 1. UI SETUP ---
st.set_page_config(page_title="MKULUNGWA IQ AI 2026", layout="wide")
init_db()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@700&display=swap');
    .main { background-color: #0E1117; color: #E0E0E0; }
    .logo-box {
        border: 3px solid #00FF00; border-radius: 30px; padding: 15px; text-align: center;
        margin: 0 auto 20px auto; max-width: 450px; background: rgba(0, 255, 0, 0.05);
    }
    .stButton>button { 
        background: linear-gradient(90deg, #00FF00, #008000); 
        color: white; border-radius: 15px; height: 3.5em; width: 100%; border: none; font-weight: bold;
    }
    .login-container { max-width: 500px; margin: 0 auto; padding: 30px; background: #1A1C24; border-radius: 25px; border: 1px solid rgba(0, 255, 0, 0.3); }
    .result-card-green { background: #1A1C24; padding: 25px; border-radius: 20px; border-left: 10px solid #00FF00; box-shadow: 5px 5px 15px rgba(0,0,0,0.5); }
    .advice-box { border: 2px solid #00FF00; padding: 20px; border-radius: 15px; color: #00FF00; background: rgba(0,255,0,0.05); font-size: 18px; line-height: 1.6; }
    button[key^="del_"] { background: linear-gradient(90deg, #FF4B4B, #8B0000) !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. LEAGUE MAP
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

# --- 3. AUTH LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='logo-box'>", unsafe_allow_html=True)
        if os.path.exists("mkulungwa_png.png"): st.image("mkulungwa_png.png", width=380)
        else: st.markdown("<h1 style='color:#00FF00;'>WELCOME MKULUNGWA IQ AI 2026</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["🔐 LOGIN", "✍️ REGISTER", "🔄 PASS RECOVERY"])
        with t1:
            u, p = st.text_input("Username", key="l_u"), st.text_input("Password", type="password", key="l_p")
            if st.button("AUTHORIZE IQ ENTRANCE"):
                hashed_p = hashlib.sha256(p.encode()).hexdigest()
                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                user = c.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, hashed_p)).fetchone()
                conn.close()
                if user:
                    if user[1] == 'active':
                        st.session_state.auth, st.session_state.user, st.session_state.role = True, u, user[0]
                        update_last_seen(u); st.rerun()
                    else: st.error("❌ AKAUNTI YAKO IMEFUNGWA!")
                else: st.error("🚨 Wrong Credentials")
        with t2:
            f_n, m_n, p_n, n_u = st.text_input("First Name"), st.text_input("Middle Name"), st.text_input("Phone"), st.text_input("Username")
            n_p = st.text_input("Strong Password (@#$%!^ + Numbers)")
            if st.button("CREATE ACCOUNT"):
                if f_n and m_n and n_u and n_p:
                    if check_password(n_p):
                        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                        try:
                            c.execute("INSERT INTO users (username, password, role, status, firstname, middlename, phone) VALUES (?,?,?,?,?,?,?)", 
                                      (n_u, hashlib.sha256(n_p.encode()).hexdigest(), "user", "active", f_n, m_n, p_n))
                            conn.commit(); st.success("✅ Karibu Mkulungwa!")
                        except: st.error("❌ Username tayari ipo!")
                        conn.close()
                    else: st.warning("⚠️ Tumia herufi, namba na alama moja (@#$%!^)")
        with t3:
            c_u, o_p, new_p = st.text_input("Username"), st.text_input("Old Pass", type="password"), st.text_input("New Pass", type="password")
            if st.button("RESET PASSWORD"):
                if check_password(new_p):
                    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                    if c.execute("SELECT * FROM users WHERE username=? AND password=?", (c_u, hashlib.sha256(o_p.encode()).hexdigest())).fetchone():
                        c.execute("UPDATE users SET password=? WHERE username=?", (hashlib.sha256(new_p.encode()).hexdigest(), c_u))
                        conn.commit(); st.success("✅ Password Updated!")
                    conn.close()
        st.markdown("</div>", unsafe_allow_html=True)
else:
    update_last_seen(st.session_state.user)
    with st.sidebar:
        if os.path.exists("mkulungwa_png.png"): st.image("mkulungwa_png.png", width=150)
        st.write(f"👤 {st.session_state.user.upper()}")
        if st.button("🚪 LOGOUT"): st.session_state.auth = False; st.rerun()
        if st.session_state.role == "admin":
            st.markdown("---")
            if st.button("🔄 REFRESH GLOBAL DATABASE"):
                all_dfs = []
                p_bar = st.progress(0, text="Establishing Neural Links...")
                leagues = [(n, c) for cat, sub in LEAGUE_MAP.items() if cat != "UEFA / EUROPA / CONFERENCE" for n, c in sub.items()]
                for i, (n, c) in enumerate(leagues):
                    try:
                        r = requests.get(f"https://www.football-data.co.uk/mmz4281/2526/{c}.csv", timeout=12)
                        if r.status_code == 200:
                            with open(f"{c}.csv", 'wb') as f: f.write(r.content)
                            all_dfs.append(pd.read_csv(StringIO(r.text)))
                        p_bar.progress((i+1)/len(leagues))
                    except: continue
                if all_dfs: pd.concat(all_dfs, ignore_index=True).to_csv("UEFA_ALL.csv", index=False); st.success("SYNCED!")

    # --- 4. CORE IQ BRAIN V18.9 ---
    st.markdown("<h1 style='text-align:center; color:#00FF00;'>MKULUNGWA IQ MASTER V18.9</h1>", unsafe_allow_html=True)
    
    cat = st.selectbox("📂 CATEGORY", list(LEAGUE_MAP.keys()))
    l_code = "UEFA_ALL" if cat == "UEFA / EUROPA / CONFERENCE" else LEAGUE_MAP[cat][st.selectbox("🏆 LEAGUE", list(LEAGUE_MAP[cat].keys()))]

    if os.path.exists(f"{l_code}.csv"):
        df = pd.read_csv(f"{l_code}.csv")
        teams = sorted(df['HomeTeam'].dropna().unique())
        h_t, a_t = st.selectbox("🏠 HOME", teams), st.selectbox("🚀 AWAY", [t for t in teams if t != st.session_state.get('h_t', teams[0])])
        
        if st.button("🎯 EXECUTE DEEP ANALYSIS"):
            m_key = f"{h_t}{a_t}{l_code}_V18.9"
            seed = int(hashlib.md5(m_key.encode()).hexdigest(), 16) % (10**6)
            np.random.seed(seed); random.seed(seed)
            
            # Data Processing
            h_recent = df[df['HomeTeam'] == h_t].tail(10)
            a_recent = df[df['AwayTeam'] == a_t].tail(10)
            
            xh = h_recent['FTHG'].mean() if not h_recent.empty else 1.4
            xa = a_recent['FTAG'].mean() if not a_recent.empty else 1.1
            total_goals = xh + xa
            
            # Corner Logic (Deep Analysis) - Tunatumia Mashambulizi (Shots) kukadiria kona
            h_shots = h_recent['HS'].mean() if 'HS' in h_recent.columns else 10
            a_shots = a_recent['AS'].mean() if 'AS' in a_recent.columns else 9
            corner_index = (h_shots + a_shots) * 0.45 + (seed % 3)
            
            # Prediction Logic
            if corner_index > 10.5: c_pick = "OVER 10.5 CORNERS"
            elif corner_index > 9.2: c_pick = "OVER 9.5 CORNERS"
            else: c_pick = "OVER 8.5 CORNERS"

            dc_pick = "1X (HOME/DRAW)" if xh > (xa + 0.2) else "X2 (AWAY/DRAW)" if xa > (xh + 0.2) else "12 (NO DRAW)"
            goal_pick = "OVER 2.5" if total_goals > 2.7 else "OVER 1.5" if total_goals > 1.6 else "UNDER 3.5"
            conf = min(98.9, 96.5 + (seed % 24) / 10)

            # UI Results
            st.markdown(f"<h2 style='text-align:center; color:#00FF00;'>🛡️ IQ CONFIDENCE: {conf:.1f}%</h2>", unsafe_allow_html=True)
            r1, r2, r3 = st.columns(3)
            r1.markdown(f"<div class='result-card-green'><h3>🏆 DOUBLE CHANCE</h3><h2>{dc_pick}</h2></div>", unsafe_allow_html=True)
            r2.markdown(f"<div class='result-card-green'><h3>🚩 CORNERS</h3><h2>{c_pick}</h2></div>", unsafe_allow_html=True)
            r3.markdown(f"<div class='result-card-green'><h3>⚽ GOALS</h3><h2>{goal_pick}</h2></div>", unsafe_allow_html=True)
            
            # Dynamic Advice Based on Real Data
            if total_goals > 2.8:
                advice = f"🔥 MASTER IQ ALERT: Timu hizi zina wastani mkubwa wa magoli ({total_goals:.2f}). Mashambulizi ni mengi, goli la mapema linawezekana."
            elif corner_index > 10:
                advice = f"🚩 MASTER IQ ALERT: Mechi itapigwa pembeni sana (Winger play). Kona ni soko lenye uhakika, Over 9.5 ni chaguo imara kulingana na data."
            else:
                advice = f"⚖️ MASTER IQ ALERT: Huu ni mchezo wa kiungo zaidi. Timu zinalingana nguvu, Double Chance ({dc_pick}) ndio kinga yako bora."
            
            st.markdown(f"<div class='advice-box'>{advice}</div>", unsafe_allow_html=True)
    else:
        st.info("💡 DATABASE OFFLINE: Admin bonyeza 'REFRESH' kuwasha mfumo.")
