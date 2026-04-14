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
    
    # Create Default Admin
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
    
    /* Box la Logo ya Mkulungwa */
    .logo-box {
        border: 3px solid #00FF00; border-radius: 30px; padding: 15px; text-align: center;
        margin: 0 auto 20px auto; max-width: 450px; background: rgba(0, 255, 0, 0.05);
        box-shadow: 0px 0px 20px rgba(0, 255, 0, 0.2);
    }
    
    .stButton>button { 
        background: linear-gradient(90deg, #00FF00, #008000); 
        color: white; border-radius: 15px; height: 3.5em; width: 100%; border: none; font-weight: bold;
    }
    .login-container { 
        max-width: 500px; margin: 0 auto; padding: 30px; background: #1A1C24; 
        border-radius: 25px; border: 1px solid rgba(0, 255, 0, 0.3);
    }
    .result-card-green { background: #1A1C24; padding: 25px; border-radius: 20px; border-left: 10px solid #00FF00; box-shadow: 5px 5px 15px rgba(0,0,0,0.5); }
    .advice-box { border: 2px solid #00FF00; padding: 20px; border-radius: 15px; color: #00FF00; background: rgba(0,255,0,0.05); font-size: 18px; }
    
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

# --- 3. LOGIN / SIGNUP LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Picha ya Mkulungwa ndani ya Box
        st.markdown("<div class='logo-box'>", unsafe_allow_html=True)
        if os.path.exists("mkulungwa_png.png"):
            st.image("mkulungwa_png.png", use_container_width=True)
        else:
            st.markdown("<h1 style='color:#00FF00;'>WELCOME MKULUNGWA IQ AI 2026</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["🔐 LOGIN", "✍️ REGISTER", "🔄 PASS RECOVERY"])
        
        with t1:
            u = st.text_input("Username", key="login_u")
            p = st.text_input("Password", type="password", key="login_p")
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
                else: st.error("🚨 Username au Password si sahihi!")

        with t2:
            f_n = st.text_input("First Name", key="reg_f")
            m_n = st.text_input("Middle Name", key="reg_m")
            p_n = st.text_input("Phone Number", key="reg_ph")
            n_u = st.text_input("Desired Username", key="reg_u")
            n_p = st.text_input("Strong Password (@#$%!^ + Numbers)", key="reg_p", type="password")
            if st.button("TENGENEZA AKAUNTI"):
                if f_n and m_n and n_u and n_p:
                    if check_password(n_p):
                        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                        try:
                            c.execute("INSERT INTO users (username, password, role, status, firstname, middlename, phone) VALUES (?,?,?,?,?,?,?)", 
                                      (n_u, hashlib.sha256(n_p.encode()).hexdigest(), "user", "active", f_n, m_n, p_n))
                            conn.commit(); st.success("✅ Umesajiliwa! Karibu IQ AI.")
                        except: st.error("❌ Username tayari ipo!")
                        conn.close()
                    else: st.warning("⚠️ Tumia herufi, namba na alama moja kati ya @#$%!^")
                else: st.warning("⚠️ Jaza sehemu zote!")

        with t3:
            c_u = st.text_input("Confirm Username", key="rec_u")
            o_p = st.text_input("Old Password", type="password", key="rec_op")
            new_p = st.text_input("New Strong Password", type="password", key="rec_np")
            if st.button("UPDATE PASSWORD"):
                if check_password(new_p):
                    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                    if c.execute("SELECT * FROM users WHERE username=? AND password=?", (c_u, hashlib.sha256(o_p.encode()).hexdigest())).fetchone():
                        c.execute("UPDATE users SET password=? WHERE username=?", (hashlib.sha256(new_p.encode()).hexdigest(), c_u))
                        conn.commit(); st.success("✅ Password Imesasishwa!")
                    else: st.error("❌ Data hazilingani!")
                    conn.close()
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- 4. APP INTERFACE (IQ MASTER LOGIC) ---
    update_last_seen(st.session_state.user)
    
    with st.sidebar:
        if os.path.exists("mkulungwa_png.png"): st.image("mkulungwa_png.png", width=150)
        st.markdown(f"### 👤 {st.session_state.user.upper()}")
        if st.button("🚪 LOGOUT"): st.session_state.auth = False; st.rerun()

        if st.session_state.role == "admin":
            st.markdown("---")
            st.markdown("### 🛠️ ADMIN CONTROL")
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
                if all_dfs: pd.concat(all_dfs, ignore_index=True).to_csv("UEFA_ALL.csv", index=False); st.success("DATABASE UPDATED!")

            if st.checkbox("👥 MANAGE USERS"):
                conn = sqlite3.connect(DB_NAME)
                users_df = pd.read_sql_query("SELECT username, firstname, status, last_seen FROM users WHERE role='user'", conn)
                now = datetime.now()
                online_count = sum(1 for ls in users_df['last_seen'] if ls and (now - datetime.strptime(ls, '%Y-%m-%d %H:%M:%S.%f')).total_seconds() < 300)
                st.metric("🟢 ONLINE", online_count); st.metric("🔴 OFFLINE", len(users_df) - online_count)
                for i, row in users_df.iterrows():
                    col_u, col_b, col_d = st.columns([2, 1, 1])
                    col_u.write(f"@{row['username']}")
                    if col_b.button("BL/UN", key=f"blk_{row['username']}"):
                        ns = 'inactive' if row['status']=='active' else 'active'
                        conn.execute("UPDATE users SET status=? WHERE username=?", (ns, row['username']))
                        conn.commit(); st.rerun()
                    if col_d.button("🗑️", key=f"del_{row['username']}"):
                        conn.execute("DELETE FROM users WHERE username=?", (row['username'],)); conn.commit(); st.rerun()
                conn.close()

    st.markdown("<h1 style='text-align:center; color:#00FF00; font-size:60px; font-weight:900;'>MKULUNGWA IQ MASTER V18.9</h1>", unsafe_allow_html=True)
    
    cat = st.selectbox("📂 CATEGORY", list(LEAGUE_MAP.keys()))
    l_code = "UEFA_ALL" if cat == "UEFA / EUROPA / CONFERENCE" else LEAGUE_MAP[cat][st.selectbox("🏆 LEAGUE", list(LEAGUE_MAP[cat].keys()))]

    if os.path.exists(f"{l_code}.csv"):
        df = pd.read_csv(f"{l_code}.csv")
        teams = sorted(df['HomeTeam'].dropna().unique())
        h_t, a_t = st.selectbox("🏠 HOME TEAM", teams), st.selectbox("🚀 AWAY TEAM", [t for t in teams if t != st.session_state.get('h_t', teams[0])])
        
        if st.button("🎯 EXECUTE DEEP ANALYSIS"):
            m_key = f"{h_t}{a_t}{l_code}_V18.9"
            seed = int(hashlib.md5(m_key.encode()).hexdigest(), 16) % (10**6)
            np.random.seed(seed); random.seed(seed)
            
            p_bar_an = st.progress(0, text="Analyzing Neural Patterns...")
            for i in range(101): time.sleep(0.005); p_bar_an.progress(i)

            h_rec, a_rec = df[df['HomeTeam'] == h_t].tail(10), df[df['AwayTeam'] == a_t].tail(10)
            xh, xa = (h_rec['FTHG'].mean() if not h_rec.empty else 1.4), (a_rec['FTAG'].mean() if not a_rec.empty else 1.1)
            
            # Corner IQ Logic
            h_shots = h_rec['HS'].mean() if 'HS' in h_rec.columns else 10
            a_shots = a_rec['AS'].mean() if 'AS' in a_rec.columns else 9
            c_index = (h_shots + a_shots) * 0.45 + (seed % 3)
            c_pick = "OVER 10.5" if c_index > 10.5 else "OVER 9.5" if c_index > 9.2 else "OVER 8.5"

            dc_pick = "1X (HOME/DRAW)" if xh > (xa + 0.2) else "X2 (AWAY/DRAW)" if xa > (xh + 0.2) else "12 (NO DRAW)"
            goal_pick = "OVER 2.5" if (xh+xa) > 2.7 else "OVER 1.5" if (xh+xa) > 1.6 else "UNDER 3.5"
            conf = min(98.9, 96.5 + (seed % 24) / 10)

            st.markdown(f"<h2 style='text-align:center; color:#00FF00;'>🛡️ IQ CONFIDENCE: {conf:.1f}%</h2>", unsafe_allow_html=True)
            r1, r2, r3 = st.columns(3)
            r1.markdown(f"<div class='result-card-green'><h3>🏆 DOUBLE CHANCE</h3><h2>{dc_pick}</h2></div>", unsafe_allow_html=True)
            r2.markdown(f"<div class='result-card-green'><h3>🚩 CORNERS</h3><h2>{c_pick}</h2></div>", unsafe_allow_html=True)
            r3.markdown(f"<div class='result-card-green'><h3>⚽ GOALS</h3><h2>{goal_pick}</h2></div>", unsafe_allow_html=True)
            
            advice = f"🔥 MASTER IQ ALERT: Mechi ya {h_t} vs {a_t} kulingana na data, " + \
                     (f"ina mashambulizi mengi ({c_index:.1f} corner index), kimbilia soko la Kona." if c_index > 9.5 else "ni ya kimkakati, Double Chance ni usalama wako.")
            st.markdown(f"<div class='advice-box'>{advice}</div>", unsafe_allow_html=True)
    else:
        st.info("💡 DATABASE OFFLINE: Admin, tafadhali bonyeza 'REFRESH GLOBAL DATABASE' kwenye sidebar.")
