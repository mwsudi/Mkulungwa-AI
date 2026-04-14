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
    
    # Auto-migration kwa ajili ya majina
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
st.set_page_config(page_title="MKULUNGWA AI V18.6", layout="wide")
init_db()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@700&display=swap');
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(90deg, #00FF00, #008000); 
        color: white; border-radius: 15px; height: 3.5em; width: 100%; border: none; font-weight: bold;
    }
    .brand-box {
        border: 2px solid #00FF00; border-radius: 50px; padding: 15px; text-align: center;
        margin-bottom: 20px; background: rgba(0, 255, 0, 0.03);
    }
    .brand-text {
        font-family: 'Courier Prime', monospace; color: #00FF00; font-size: 40px;
        font-weight: 900; letter-spacing: 3px; text-shadow: 2px 2px 8px rgba(0, 255, 0, 0.4);
    }
    .result-card-green { background: #1A1C24; padding: 25px; border-radius: 20px; border-left: 10px solid #00FF00; }
    .login-container { max-width: 450px; margin: 0 auto; padding: 30px; background: #1A1C24; border-radius: 20px; border: 1px solid #00FF00; }
    /* Delete button style */
    div[data-testid="column"]:nth-child(3) button {
        background: linear-gradient(90deg, #FF4B4B, #8B0000) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN LOGIC
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='brand-box'><p class='brand-text'>🛡️ MKULUNGWA AI</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["LOGIN", "REGISTER", "CHANGE PASS"])
        
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
    # 3. APP LOGIC
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user.upper()}")
        if st.button("🚪 LOGOUT"): st.session_state.auth = False; st.rerun()
        
        if st.session_state.role == "admin":
            st.markdown("---")
            st.markdown("### 🛠️ ADMIN PANEL")
            # Manage Users Section
            if st.checkbox("👥 MANAGE USERS"):
                conn = sqlite3.connect(DB_NAME)
                users = pd.read_sql_query("SELECT username, firstname, lastname, status FROM users WHERE role='user'", conn)
                for i, row in users.iterrows():
                    # Safu 3: Jina, Block, Delete
                    c1, c2, c3 = st.columns([2, 1, 1])
                    f_name = row['firstname'] if row['firstname'] else "N/A"
                    c1.write(f"**{f_name}** (@{row['username']})")
                    
                    # Kitufe cha Block
                    if c2.button("UNBLOCK" if row['status']=='inactive' else "BLOCK", key=f"blk_{row['username']}"):
                        new_s = 'inactive' if row['status']=='active' else 'active'
                        conn.execute("UPDATE users SET status=? WHERE username=?", (new_s, row['username']))
                        conn.commit(); st.rerun()
                    
                    # Kitufe cha Delete (Kipya)
                    if c3.button("🗑️", key=f"del_{row['username']}", help="Futa kabisa huyu user"):
                        conn.execute("DELETE FROM users WHERE username=?", (row['username'],))
                        conn.commit(); st.success(f"Umfuta {row['username']}"); time.sleep(1); st.rerun()
                conn.close()

    # --- 4. DASHBOARD ---
    st.markdown("<h1>MKULUNGWA AI V18.6</h1>", unsafe_allow_html=True)
    # ... (Hapa inaendelea ile League Config na Analysis kama awali) ...
    # Nimefupisha hapa ili kodi isizidi urefu wa kurasa, lakini logic ya Analysis ibaki ile ile.
