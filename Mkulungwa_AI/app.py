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

# --- 1. DATABASE & SECURITY LAYER ---
DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (username TEXT, action TEXT, timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS system_config 
                 (key TEXT PRIMARY KEY, value TEXT)''')
    
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

def update_user_status(username, new_status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET status = ? WHERE username = ?", (new_status, username))
    conn.commit()
    conn.close()

# --- 2. THE GLOBAL LEAGUE & UEFA MAP ---
LEAGUE_MAP = {
    "UEFA CUPS": {
        "Champions League": "CL",
        "Europa League": "EL",
        "Conference League": "EC"
    },
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

# --- 3. AUTO-SYNC ENGINE (Daily Updates) ---
def auto_sync_data():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM system_config WHERE key = 'last_sync'")
    res = c.fetchone()
    
    # Marekebisho hapa: if na : zimekaa sawa sasa
    if res is None or res[0] != today:
        with st.status("🔄 Neural Sync: Updating Global & UEFA Data...", expanded=False):
            for cat, sub in LEAGUE_MAP.items():
                for name, code in sub.items():
                    try:
                        url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                        r = requests.get(url, timeout=5)
                        if r.status_code == 200:
                            with open(f"{code}.csv", 'wb') as f:
                                f.write(r.content)
                    except:
                        continue
            c.execute("INSERT OR REPLACE INTO system_config VALUES ('last_sync', ?)", (today,))
            conn.commit()
            st.toast("✅ Mkulungwa AI: Data Zote Zipo Updated!")
    conn.close()

# --- 4. THE IQ CORE (Neural Poisson xG Engine) ---
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
    
    return exp_home, exp_away, random.randint(89, 98)

# --- 5. UI BRANDING & PAYMENT FOOTER ---
def display_custom_logo():
    st.markdown(f"<h1 style='text-align:center; color:#00FF00; text-shadow: 0 0 20px #00FF00;'>🛡️ MKULUNGWA AI V20.6</h1>", unsafe_allow_html=True)

def display_footer():
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 2px solid #00FF00; border-radius: 15px; background: rgba(0,255,0,0.07);">
            <h3 style="color: #00FF00;">💰 KUPATA ACCESS / RENEW SUBSCRIPTION</h3>
            <p style="font-size: 16px;">Lipia sasa na tuma ushahidi wa muamala WhatsApp ili kupewa ruhusa ya kudumu.</p>
            <p style="font-size: 24px; font-weight: bold; color: #00FF00;">📞 0699470308</p>
            <a href="https://wa.me/255699470308?text=Habari%20Master,%20nimefanya%20malipo%20ya%20Mkulungwa%20AI,%20naomba%20access." target="_blank">
                <button style="background:#25D366; color:white; padding:12px 25px; border-radius:10px; border:none; font-weight:bold; cursor:pointer; font-size:16px;">💬 TUMA MUAMALA WHATSAPP</button>
            </a>
        </div>
    """, unsafe_allow_html=True)

# --- 6. APP EXECUTION ---
init_db()
st.set_page_config(page_title="MKULUNGWA AI | Master Edition", layout="wide")
st.markdown("<style>.main {background-color:#0E1117; color:#E0E0E0;} .stButton>button {width:100%; background:linear-gradient(90deg,#00FF00,#008000); color:white; font-weight:bold; border-radius:12px; border:none; height:3.5em; box-shadow: 0 4px 15px rgba(0,255,0,0.3);}</style>", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    display_custom_logo()
    t1, t2 = st.tabs(["🔒 SECURE LOGIN", "📝 NEW REGISTRATION"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("AUTHORIZE ENTRANCE"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT status, role FROM users WHERE username=? AND password=?", (u, hashlib.sha256(p.encode()).hexdigest()))
            res = c.fetchone()
            conn.close()
            if res:
                if res[0] == 'active':
                    st.session_state.logged_in, st.session_state.username, st.session_state.user_role = True, u, res[1]
                    log_action(u, "System Access Granted")
                    st.rerun()
                else:
                    st.error("❌ Akaunti imefungwa. Lipia kupitia namba hapo chini.")
            else:
                st.error("🚨 Username au Password siyo sahihi.")
    with t2:
        nu = st.text_input("Choose Username", key="r_u")
        np = st.text_input("Choose Password", type="password", key="r_p")
        if st.button("CREATE MASTER ACCOUNT"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users VALUES (?,?,?,?)", (nu, hashlib.sha256(np.encode()).hexdigest(), "user", "active"))
                conn.commit()
                st.success("✅ Karibu! Sasa tumia Login kuingia ndani.")
            except:
                st.error("❌ Jina hili tayari lipo.")
            conn.close()
    display_footer()

else:
    auto_sync_data
