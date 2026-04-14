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
    
    cursor = conn.execute('PRAGMA table_info(users)')
    columns = [column[1] for column in cursor.fetchall()]
    if 'firstname' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN firstname TEXT DEFAULT ''")
    if 'lastname' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN lastname TEXT DEFAULT ''")
    
    c.execute('''CREATE TABLE IF NOT EXISTS system_config 
                 (key TEXT PRIMARY KEY, value TEXT)''')
    
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, role, status) VALUES (?, ?, ?, ?)", 
              ("admin", admin_pw, "admin", "active"))
    conn.commit()
    conn.close()

# --- 1. UI SETUP ---
st.set_page_config(page_title="MKULUNGWA AI V18.7", layout="wide")
init_db()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@700&display=swap');
    
    .main { background-color: #0E1117; color: #E0E0E0; }
    
    /* Box la Logo - Sasa limeboreshwa ili picha ikae ndani */
    .logo-box {
        border: 2px solid #00FF00;
        border-radius: 30px;
        padding: 10px;
        text-align: center;
        margin: 0 auto 20px auto;
        max-width: 400px;
        background: rgba(0, 255, 0, 0.05);
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 120px;
    }

    .stButton>button { 
        background: linear-gradient(90deg, #00FF00, #008000); 
        color: white; border-radius: 15px; height: 3.5em; width: 100%; border: none; font-weight: bold;
    }
    
    .login-container { 
        max-width: 480px; 
        margin: 0 auto; 
        padding: 30px; 
        background: #1A1C24; 
        border-radius: 25px; 
        border: 1px solid rgba(0, 255, 0, 0.2);
        box-shadow: 0px 15px 35px rgba(0,0,0,0.5);
    }
    
    button[key^="del_"] {
        background: linear-gradient(90deg, #FF4B4B, #8B0000) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN LOGIC
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    # Safu ya kati kwa ajili ya Logo na Login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # HAPA NDIPO PICHA INAPOINGIZWA NDANI YA BOX
        st.markdown("<div class='logo-box'>", unsafe_allow_html=True)
        if os.path.exists("mkulungwa_png.png"):
            # Tunatumia st.image ndani ya lile box la kijani
            st.image("mkulungwa_png.png", width=300)
        else:
            st.markdown("<h1 style='color:#00FF00; font-family:Courier Prime; margin:0;'>MKULUNGWA AI</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["🔐 LOGIN", "✍️ REGISTER", "🔄 CHANGE PASS"])
        
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
            fname = st.text_input("First Name")
            lname = st.text_input("Last Name")
            nu = st.text_input("New Username", key="r_u")
            np = st.text_input("New Pass", type="password", key="r_p")
            if st.button("CREATE ACCOUNT"):
                if fname and lname and nu and np:
                    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                    try:
                        c.execute("INSERT INTO users (username, password, role, status, firstname, lastname) VALUES (?, ?, ?, ?, ?, ?)", 
                                  (nu, hashlib.sha256(np.encode()).hexdigest(), "user", "active", fname, lname))
                        conn.commit(); st.success("✅ Karibu! Sasa Login.")
                    except: st.error("❌ Username lipo.")
                    conn.close()
                else: st.warning("⚠️ Jaza majina yako yote mawili!")

        with tab3:
            cu = st.text_input("Username Verification")
            old_p = st.text_input("Old Password", type="password")
            new_p = st.text_input("New Password", type="password")
            if st.button("UPDATE PASSWORD"):
                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                h_old = hashlib.sha256(old_p.encode()).hexdigest()
                c.execute("SELECT * FROM users WHERE username=? AND password=?", (cu, h_old))
                if c.fetchone():
                    h_new = hashlib.sha256(new_p.encode()).hexdigest()
                    c.execute("UPDATE users SET password=? WHERE username=?", (h_new, cu))
                    conn.commit(); st.success("✅ Password updated!")
                else: st.error("❌ Data hazilingani.")
                conn.close()
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # 3. LEAGUE CONFIG & DASHBOARD (Inabaki vile vile Master)
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
        if os.path.exists("mkulungwa_png.png"):
            st.image("mkulungwa_png.png", width=150)
        st.markdown(f"### 👤 {st.session_state.user.upper()}")
        if st.button("🚪 LOGOUT"): st.session_state.auth = False; st.rerun()
        
        if st.session_state.role == "admin":
            st.markdown("---")
            if st.button("🚀 BROADCAST GLOBAL SYNC"):
                # ... (Logic ya sync)
                st.success("✅ SYNC COMPLETE!")

            if st.checkbox("👥 MANAGE USERS"):
                conn = sqlite3.connect(DB_NAME)
                users = pd.read_sql_query("SELECT username, firstname, lastname, status FROM users WHERE role='user'", conn)
                for i, row in users.iterrows():
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.write(f"@{row['username']}")
                    if c2.button("BLOCK/UNBL", key=f"blk_{row['username']}"):
                        # Logic hapa
                        st.rerun()
                    if c3.button("🗑️", key=f"del_{row['username']}"):
                        conn.execute("DELETE FROM users WHERE username=?", (row['username'],))
                        conn.commit(); st.rerun()
                conn.close()

    st.markdown("<h1>MKULUNGWA AI V18.7</h1>", unsafe_allow_html=True)
    # ... (Sehemu ya Analysis inaendelea kama kawaida)
