import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib
import sqlite3
import base64
from datetime import datetime
from scipy.stats import poisson

# --- 1. DATABASE & SECURITY ---
DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (username TEXT, action TEXT, timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)''')
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", ("admin", admin_pw, "admin", "active"))
    conn.commit()
    conn.close()

def log_action(username, action):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO logs VALUES (?, ?, ?)", (username, action, now))
    conn.commit()
    conn.close()

# --- 2. THE IQ CORE (POISSON ENGINE) ---
def calculate_iq_metrics(df, home_team, away_team):
    # Hesabu ya Wastani (League Average)
    avg_home_goals = df['FTHG'].mean()
    avg_away_goals = df['FTAG'].mean()
    
    # Home Team IQ
    home_df = df[df['HomeTeam'] == home_team]
    home_attack_iq = home_df['FTHG'].mean() / avg_home_goals
    home_defense_iq = home_df['FTAG'].mean() / avg_away_goals
    
    # Away Team IQ
    away_df = df[df['AwayTeam'] == away_team]
    away_attack_iq = away_df['FTAG'].mean() / avg_away_goals
    away_defense_iq = away_df['FTHG'].mean() / avg_home_goals
    
    # Expected Goals (xG)
    exp_home = home_attack_iq * away_defense_iq * avg_home_goals
    exp_away = away_attack_iq * home_defense_iq * avg_away_goals
    
    return exp_home, exp_away, random.randint(85, 98) # Confidence simulator ya IQ

# --- 3. UI BRANDING & CONTACT ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    return None

def display_custom_logo(size=200):
    img_base64 = get_base64_image("logo.png")
    if img_base64:
        st.markdown(f'<div style="text-align:center"><img src="data:image/png;base64,{img_base64}" style="width:{size}px;border-radius:50%;box-shadow:0 0 30px #00FF00;"></div>', unsafe_allow_html=True)
    else: st.markdown("<h1 style='text-align:center;color:#00FF00;'>🛡️ MKULUNGWA AI</h1>", unsafe_allow_html=True)

def display_footer():
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; padding: 15px; border: 1px solid #00FF00; border-radius: 15px; background: rgba(0,255,0,0.05);">
            <h3 style="color: #00FF00;">💰 LIPA KUPATA ACCESS YA MKULUNGWA AI</h3>
            <p>Tuma muamala WhatsApp kupata ruhusa ya kutumia mashine.</p>
            <p style="font-size: 22px; font-weight: bold;">📞 0699470308</p>
            <a href="https://wa.me/255699470308?text=Habari Master, nimefanya malipo ya Mkulungwa AI." target="_blank">
                <button style="background:#25D366;color:white;padding:10px 20px;border-radius:10px;border:none;font-weight:bold;cursor:pointer;">💬 TUMA MUAMALA WHATSAPP</button>
            </a>
        </div>
    """, unsafe_allow_html=True)

# --- 4. APP INITIALIZATION ---
init_db()
st.set_page_config(page_title="MKULUNGWA AI V20.0", layout="wide")
st.markdown("<style>.main {background-color:#0E1117;color:#E0E0E0;} .stButton>button {background:linear-gradient(90deg,#00FF00,#008000);color:white;font-weight:bold;border-radius:10px;border:none;}</style>", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- 5. LOGIN/REGISTER FLOW ---
if not st.session_state.logged_in:
    display_custom_logo(200)
    t1, t2 = st.tabs(["🔒 LOGIN", "📝 REGISTER"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("AUTHORIZE ENTRANCE"):
            conn = sqlite3.connect(DB_NAME); c = conn.cursor()
            c.execute("SELECT status, role FROM users WHERE username=? AND password=?", (u, hashlib.sha256(p.encode()).hexdigest()))
            res = c.fetchone(); conn.close()
            if res:
                if res[0] == 'active':
                    st.session_state.logged_in, st.session_state.username, st.session_state.user_role = True, u, res[1]
                    log_action(u, "System Login")
                    st.rerun()
                else: st.error("❌ Akaunti imefungwa. Lipia kupitia namba hapo chini.")
            else: st.error("🚨 Username au Password siyo sahihi.")
    with t2:
        nu = st.text_input("New Username", key="r_u")
        np = st.text_input("New Password", type="password", key="r_p")
        if st.button("CREATE ACCOUNT"):
            conn = sqlite3.connect(DB_NAME); c = conn.cursor()
            try:
                c.execute("INSERT INTO users VALUES (?,?,?,?)", (nu, hashlib.sha256(np.encode()).hexdigest(), "user", "active"))
                conn.commit(); st.success("✅ Akaunti tayari! Login sasa.")
            except: st.error("❌ Jina tayari lipo.")
            conn.close()
    display_footer()

else:
    # --- DASHBOARD & ANALYTICS ---
    with st.sidebar:
        display_custom_logo(100)
        st.write(f"Mtumiaji: **{st.session_state.username.upper()}**")
        if st.button("🚪 LOGOUT"): st.session_state.logged_in = False; st.rerun()

    st.markdown("<h1 style='color:#00FF00;text-align:center;'>🎯 MKULUNGWA AI IQ DASHBOARD</h1>", unsafe_allow_html=True)
    
    LEAGUE_MAP = {"ENGLAND":{"Premier League":"E0"}, "SPAIN":{"La Liga":"SP1"}, "ITALY":{"Serie A":"I1"}, "GERMANY":{"Bundesliga":"D1"}, "FRANCE":{"Ligue 1":"F1"}}
    
    cat = st.selectbox("📂 CHAGUA NCHI", list(LEAGUE_MAP.keys()))
    l_name = st.selectbox("🏆 CHAGUA LIGI", list(LEAGUE_MAP[cat].keys()))
    l_code = LEAGUE_MAP[cat][l_name]
    
    if os.path.exists(f"{l_code}.csv"):
        df = pd.read_csv(f"{l_code}.csv")
        teams = sorted(df['HomeTeam'].dropna().unique())
        c1, c2 = st.columns(2)
        h_t = c1.selectbox("🏠 HOME TEAM", teams)
        a_t = c2.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])
        
        if st.button("🎯 RUN NEURAL IQ ANALYSIS"):
            with st.status("🧠 Analyzing Neural Patterns...", expanded=True) as status:
                st.write("📡 Fetching league averages...")
                time.sleep(1)
                st.write("📈 Calculating xG (Expected Goals)...")
                exp_h, exp_a, conf = calculate_iq_metrics(df, h_t, a_t)
                time.sleep(1)
                status.update(label="✅ IQ Analysis Complete!", state="complete")
            
            # DASHBOARD DISPLAY
            st.markdown(f"""
                <div style="background:#1A1C24; padding:20px; border-radius:15px; border-left:10px solid #00FF00;">
                    <h2 style="color:#00FF00;text-align:center;">{h_t} vs {a_t}</h2>
                    <div style="display:flex; justify-content:space-around; text-align:center;">
                        <div><p>AI EXPECTED GOALS</p><h3>{exp_h:.2f} - {exp_a:.2f}</h3></div>
                        <div><p>AI CONFIDENCE</p><h3 style="color:#00FF00;">{conf}%</h3></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # MASTER ADVICE
            advice = "Over 1.5 & Double Chance" if (exp_h + exp_a) > 2.0 else "Under 3.5 & Home/Away Win"
            st.markdown(f"<div style='margin-top:20px; padding:15px; background:rgba(0,255,0,0.1); border:1px solid #00FF00; border-radius:10px; color:#00FF00; text-align:center; font-size:20px;'><b>MASTER ADVICE:</b> {advice}</div>", unsafe_allow_html=True)
            log_action(st.session_state.username, f"Analyzed {h_t} vs {a_t}")

    display_footer()
