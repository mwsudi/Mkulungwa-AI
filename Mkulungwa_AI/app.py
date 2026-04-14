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
    # Users table yenye data zote unazotaka
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, status TEXT, 
                  firstname TEXT, middlename TEXT, phone TEXT, last_seen TIMESTAMP)''')
    
    # Admin default
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, role, status) VALUES (?, ?, ?, ?)", 
              ("admin", admin_pw, "admin", "active"))
    conn.commit()
    conn.close()

# --- 1. UTILITIES ---
def check_password(password):
    # Hakikisha anaweka namba, herufi na walau moja ya @#$%!^
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

# --- 2. UI SETUP ---
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
    .result-card-green { background: #1A1C24; padding: 25px; border-radius: 20px; border-left: 10px solid #00FF00; }
    .advice-box { border: 2px solid #00FF00; padding: 20px; border-radius: 15px; color: #00FF00; }
    
    /* Kitufe cha kufuta user (Nyekundu) */
    button[key^="del_"] { background: linear-gradient(90deg, #FF4B4B, #8B0000) !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN / SIGNUP LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Picha ya Mkulungwa ndani ya Box
        st.markdown("<div class='logo-box'>", unsafe_allow_html=True)
        if os.path.exists("mkulungwa_png.png"):
            st.image("mkulungwa_png.png", width=380)
        else:
            st.markdown("<h1 style='color:#00FF00;'>WELCOME MKULUNGWA IQ AI 2026</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["🔐 LOGIN", "✍️ REGISTER", "🔄 PASS RECOVERY"])
        
        with t1:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("AUTHORIZE IQ ENTRANCE"):
                hashed_p = hashlib.sha256(p.encode()).hexdigest()
                conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                c.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, hashed_p))
                user = c.fetchone(); conn.close()
                if user:
                    if user[1] == 'active':
                        st.session_state.auth, st.session_state.user, st.session_state.role = True, u, user[0]
                        update_last_seen(u)
                        st.rerun()
                    else: st.error("❌ AKAUNTI YAKO IMEFUNGWA NA ADMIN!")
                else: st.error("🚨 Username au Password si sahihi!")

        with t2:
            f_n = st.text_input("Jina la Kwanza")
            m_n = st.text_input("Jina la Kati")
            p_n = st.text_input("Namba ya Simu")
            n_u = st.text_input("Username Mpya")
            n_p = st.text_input("Password (Weka @#$%!^ na Namba)")
            if st.button("TENGENEZA AKAUNTI"):
                if f_n and m_n and n_u and n_p:
                    if check_password(n_p):
                        conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                        try:
                            c.execute("INSERT INTO users (username, password, role, status, firstname, middlename, phone) VALUES (?,?,?,?,?,?,?)", 
                                      (n_u, hashlib.sha256(n_p.encode()).hexdigest(), "user", "active", f_n, m_n, p_n))
                            conn.commit(); st.success("✅ Umesajiliwa! Karibu IQ AI.")
                        except: st.error("❌ Username tayari inatumika!")
                        conn.close()
                    else: st.warning("⚠️ Password iwe na Namba, Herufi na moja ya hizi: @#$%!^")
                else: st.warning("⚠️ Jaza sehemu zote!")

        with t3:
            st.info("Kama umesahau password, wasiliana na Admin.")
            c_u = st.text_input("Username ya Uhakiki")
            o_p = st.text_input("Old Pass", type="password")
            new_p = st.text_input("New Strong Pass", type="password")
            if st.button("BADILI PASSWORD"):
                if check_password(new_p):
                    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
                    h_old = hashlib.sha256(o_p.encode()).hexdigest()
                    c.execute("SELECT * FROM users WHERE username=? AND password=?", (c_u, h_old))
                    if c.fetchone():
                        c.execute("UPDATE users SET password=? WHERE username=?", (hashlib.sha256(new_p.encode()).hexdigest(), c_u))
                        conn.commit(); st.success("✅ Password Imesasishwa!")
                    else: st.error("❌ Data hazilingani!")
                    conn.close()
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- 4. APP INTERFACE (V17.7 IQ KUBWA) ---
    update_last_seen(st.session_state.user)
    
    with st.sidebar:
        if os.path.exists("mkulungwa_png.png"): st.image("mkulungwa_png.png")
        st.markdown(f"### 👤 {st.session_state.user.upper()}")
        if st.button("🚪 LOGOUT"): st.session_state.auth = False; st.rerun()

        if st.session_state.role == "admin":
            st.markdown("---")
            st.markdown("### 🛠️ ADMIN CONTROL")
            
            # Update Database (Wewe tu ndio unaruhusiwa)
            if st.button("🔄 REFRESH GLOBAL DATABASE (ADMIN ONLY)"):
                # ... (Kodi yako ya Sync hapa)
                st.success("DATABASE UPDATED!")

            # User Management & Analytics
            if st.checkbox("👥 MANAGE USERS"):
                conn = sqlite3.connect(DB_NAME)
                users_df = pd.read_sql_query("SELECT username, firstname, status, last_seen FROM users WHERE role='user'", conn)
                
                # Jua walio Online (Walioonekana ndani ya dakika 5 zilizopita)
                now = datetime.now()
                online_count = 0
                for _, u_row in users_df.iterrows():
                    if u_row['last_seen']:
                        ls = datetime.strptime(u_row['last_seen'], '%Y-%m-%d %H:%M:%S.%f')
                        if (now - ls).total_seconds() < 300: online_count += 1
                
                st.metric("🟢 ONLINE USERS", online_count)
                st.metric("🔴 OFFLINE USERS", len(users_df) - online_count)

                for i, row in users_df.iterrows():
                    col_u, col_b, col_d = st.columns([2, 1, 1])
                    col_u.write(f"**{row['firstname']}** (@{row['username']})")
                    if col_b.button("BLOCK" if row['status']=='active' else "UNBL", key=f"b_{row['username']}"):
                        ns = 'inactive' if row['status']=='active' else 'active'
                        conn.execute("UPDATE users SET status=? WHERE username=?", (ns, row['username']))
                        conn.commit(); st.rerun()
                    if col_d.button("🗑️", key=f"del_{row['username']}"):
                        conn.execute("DELETE FROM users WHERE username=?", (row['username'],))
                        conn.commit(); st.rerun()
                conn.close()

    # HAPA NDIPO KODI YAKO YA IQ KUBWA INAENDELEA
    st.markdown("<h1>MKULUNGWA IQ AI V18.8</h1>", unsafe_allow_html=True)
    
    # ... (Hapa weka ile LEAGUE_MAP na Analysis Logic yako yote bila kubadili kitu) ...
    st.info("💡 Mfumo wa IQ uko tayari. Chagua ligi kuanza uchambuzi.")
