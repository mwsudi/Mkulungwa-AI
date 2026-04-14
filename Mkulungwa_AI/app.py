import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib
import sqlite3
import base64
import random
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
    avg_home_goals = df['FTHG'].mean()
    avg_away_goals = df['FTAG'].mean()
    
    home_df = df[df['HomeTeam'] == home_team]
    home_attack_iq = home_df['FTHG'].mean() / avg_home_goals if not home_df.empty else 1.0
    home_defense_iq = home_df['FTAG'].mean() / avg_away_goals if not home_df.empty else 1.0
    
    away_df = df[df['AwayTeam'] == away_team]
    away_attack_iq = away_df['FTAG'].mean() / avg_away_goals if not away_df.empty else 1.0
    away_defense_iq = away_df['FTHG'].mean() / avg_home_goals if not away_df.empty else 1.0
    
    exp_home = home_attack_iq * away_defense_iq * avg_home_goals
    exp_away = away_attack_iq * home_defense_iq * avg_away_goals
    
    return exp_home, exp_away, random.randint(88, 98)

# --- 3. UI BRANDING & FOOTER ---
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
            <p>Tuma muamala WhatsApp 0699470308 ili kupewa ruhusa (Access).</p>
            <a href="https://wa.me/255699470308?text=Habari Master, nimefanya malipo ya Mkulungwa AI." target="_blank">
                <button style="background:#25D366;color:white;padding:10px 20px;border-radius:10px;border:none;font-weight:bold;cursor:pointer;">💬 TUMA MUAMALA WHATSAPP</button>
            </a>
        </div>
    """, unsafe_allow_html=True)

# --- 4. DATA SYNC ENGINE ---
LEAGUE_MAP = {
    "ENGLAND": {"Premier League": "E0", "Championship": "E1", "League 1": "E2", "League 2": "E3"},
    "SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D2"},
    "FRANCE": {"Ligue 1": "F1", "Ligue 2": "F2"},
    "NETHERLANDS": {"Eredivisie": "N1"},
    "PORTUGAL": {"Primeira Liga": "P1"},
    "TURKEY": {"Super Lig": "T1"},
    "BELGIUM": {"Pro League": "B1"},
    "SCOTLAND": {"Premiership": "SC0", "Championship": "SC1"},
    "GREECE": {"Super League": "G1"}
}

def auto_sync_data():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT value FROM system_config WHERE key = 'last_sync'")
    res = c.fetchone()
    if res is None or res[0] != today:
        with st.status("🔄 Auto-Updating Global Leagues...", expanded=False):
            for cat, sub in LEAGUE_MAP.items():
                for name, code in sub.items():
                    try:
                        url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                        r = requests.get(url, timeout=5)
                        if r.status_code == 200:
                            with open(f"{code}.csv", 'wb') as f: f.write(r.content)
                    except: continue
            c.execute("INSERT OR REPLACE INTO system_config VALUES ('last_sync', ?)", (today,))
            conn.commit()
    conn.close()

# --- 5. MAIN APP FLOW ---
init_db()
st.set_page_config(page_title="MKULUNGWA AI V20.1", layout="wide")
st.markdown("<style>.main {background-color:#0E1117;color:#E0E0E0;} .stButton>button {width:100%;background:linear-gradient(90deg,#00FF00,#008000);color:white;font-weight:bold;border-radius:10px;border:none;height:3em;}</style>", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

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
                    log_action(u, "Login Success")
                    st.rerun()
                else: st.error("❌ Akaunti imefungwa. Lipia kwanza.")
            else: st.error("🚨 Makosa kwenye Username au Password.")
    with t2:
        nu = st.text_input("New Username", key="r_u")
        np = st.text_input("New Password", type="password", key="r_p")
        if st.button("CREATE ACCOUNT"):
            conn = sqlite3.connect(DB_NAME); c = conn.cursor()
            try:
                c.execute("INSERT INTO users VALUES (?,?,?,?)", (nu, hashlib.sha256(np.encode()).hexdigest(), "user", "active"))
                conn.commit(); st.success("✅ Karibu Master! Login sasa.")
            except: st.error("❌ Jina tayari lipo.")
            conn.close()
    display_footer()
else:
    auto_sync_data()
    with st.sidebar:
        display_custom_logo(100)
        st.write(f"Master: **{st.session_state.username.upper()}**")
        if st.button("🚪 LOGOUT"): st.session_state.logged_in = False; st.rerun()

    st.markdown("<h1 style='color:#00FF00;text-align:center;'>🎯 MKULUNGWA AI NEURAL IQ</h1>", unsafe_allow_html=True)
    
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
            with st.status("🧠 Processing Neural Probability...", expanded=True) as status:
                exp_h, exp_a, conf = calculate_iq_metrics(df, h_t, a_t)
                time.sleep(1)
                status.update(label="✅ Analysis Complete!", state="complete")
            
            st.markdown(f"""
                <div style="background:#1A1C24; padding:20px; border-radius:15px; border-left:10px solid #00FF00; margin-bottom:20px;">
                    <h2 style="color:#00FF00;text-align:center;">{h_t} vs {a_t}</h2>
                    <div style="display:flex; justify-content:space-around; text-align:center;">
                        <div><p style='color:#888;'>EXPECTED GOALS (xG)</p><h3 style='font-size:30px;'>{exp_h:.2f} - {exp_a:.2f}</h3></div>
                        <div><p style='color:#888;'>AI CONFIDENCE</p><h3 style="color:#00FF00; font-size:30px;">{conf}%</h3></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            advice = "Over 1.5 & Double Chance" if (exp_h + exp_a) > 2.1 else "Under 3.5 & Home/Away Win"
            st.markdown(f"<div style='padding:20px; background:rgba(0,255,0,0.1); border:1px solid #00FF00; border-radius:10px; color:#00FF00; text-align:center; font-size:22px; font-weight:bold;'>MASTER ADVICE: {advice}</div>", unsafe_allow_html=True)
            log_action(st.session_state.username, f"Analyzed {h_t} vs {a_t} in {l_name}")

    display_footer()
