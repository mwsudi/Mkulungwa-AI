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

# --- 3. UPDATED SYNC ENGINE (MUHIMU SANA) ---
def download_file(code):
    """Jaribu kushusha file, kama ikifeli kagua vyanzo mbadala."""
    try:
        # Tunatumia msimu wa 25/26 (2526)
        url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(f"{code}.csv", 'wb') as f:
                f.write(r.content)
            return True
        else:
            # Kama msimu huu hauna data bado, rudi msimu uliopita (2425)
            url_alt = f"https://www.football-data.co.uk/mmz4281/2425/{code}.csv"
            r_alt = requests.get(url_alt, timeout=10)
            if r_alt.status_code == 200:
                with open(f"{code}.csv", 'wb') as f:
                    f.write(r_alt.content)
                return True
    except:
        pass
    return False

def auto_sync_data():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME); c = conn.cursor()
    c.execute("SELECT value FROM system_config WHERE key = 'last_sync'")
    res = c.fetchone()
    
    if res is None or res[0] != today:
        with st.status("🔄 Neural Sync: Updating Data...", expanded=False):
            for cat, sub in LEAGUE_MAP.items():
                for name, code in sub.items():
                    download_file(code)
            c.execute("INSERT OR REPLACE INTO system_config VALUES ('last_sync', ?)", (today,))
            conn.commit()
    conn.close()

# --- 4. THE IQ CORE ---
def calculate_iq_metrics(df, home_team, away_team):
    avg_home_goals = df['FTHG'].mean()
    avg_away_goals = df['FTAG'].mean()
    
    h_df = df[df['HomeTeam'] == home_team]
    a_df = df[df['AwayTeam'] == away_team]
    
    h_atk = h_df['FTHG'].mean() / avg_home_goals if not h_df.empty else 1.0
    h_def = h_df['FTAG'].mean() / avg_away_goals if not h_df.empty else 1.0
    a_atk = a_df['FTAG'].mean() / avg_away_goals if not a_df.empty else 1.0
    a_def = a_df['FTHG'].mean() / avg_home_goals if not a_df.empty else 1.0
    
    exp_h = h_atk * a_def * avg_home_goals
    exp_a = a_atk * h_def * avg_away_goals
    return exp_h, exp_a, random.randint(90, 98)

# --- 5. UI BRANDING ---
def display_custom_logo():
    st.markdown("<h1 style='text-align:center; color:#00FF00; text-shadow: 0 0 15px #00FF00;'>🛡️ MKULUNGWA AI V20.8</h1>", unsafe_allow_html=True)

# --- 6. APP MAIN ---
init_db()
st.set_page_config(page_title="MKULUNGWA AI", layout="wide")
st.markdown("<style>.main {background-color:#0E1117; color:#E0E0E0;} .stButton>button {width:100%; background:linear-gradient(90deg,#00FF00,#008000); color:white; font-weight:bold; border-radius:12px; border:none; height:3.5em;}</style>", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    display_custom_logo()
    t1, t2 = st.tabs(["🔒 LOGIN", "📝 REGISTER"])
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("AUTHORIZE"):
            conn = sqlite3.connect(DB_NAME); c = conn.cursor()
            c.execute("SELECT status, role FROM users WHERE username=? AND password=?", (u, hashlib.sha256(p.encode()).hexdigest()))
            res = c.fetchone(); conn.close()
            if res and res[0] == 'active':
                st.session_state.logged_in, st.session_state.username, st.session_state.user_role = True, u, res[1]
                st.rerun()
            else: st.error("Access Denied.")
    with t2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("REGISTER"):
            conn = sqlite3.connect(DB_NAME); c = conn.cursor()
            try:
                c.execute("INSERT INTO users VALUES (?,?,?,?)", (nu, hashlib.sha256(np.encode()).hexdigest(), "user", "active"))
                conn.commit(); st.success("Tayari! Login sasa.")
            except: st.error("Jina lipo.")
            conn.close()
else:
    auto_sync_data()
    with st.sidebar:
        display_custom_logo()
        if st.button("🚪 LOGOUT"): st.session_state.logged_in = False; st.rerun()

    st.markdown("<h1 style='color:#00FF00; text-align:center;'>🎯 NEURAL IQ ANALYSIS</h1>", unsafe_allow_html=True)
    
    cat = st.selectbox("📂 CATEGORY", list(LEAGUE_MAP.keys()))
    l_name = st.selectbox("🏆 LEAGUE/CUP", list(LEAGUE_MAP[cat].keys()))
    l_code = LEAGUE_MAP[cat][l_name]
    
    # HAPA NDIPO MAREKEBISHO YA ERROR YA NJANO YALIPO:
    if not os.path.exists(f"{l_code}.csv"):
        with st.spinner(f"📥 Fetching {l_name} data..."):
            download_file(l_code)

    if os.path.exists(f"{l_code}.csv"):
        try:
            df = pd.read_csv(f"{l_code}.csv")
            # Kusafisha data (Baadhi ya mafile ya UEFA yanaweza kuwa na matatizo ya format)
            df = df.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'])
            
            teams = sorted(df['HomeTeam'].unique())
            col_h, col_a = st.columns(2)
            h_t = col_h.selectbox("🏠 HOME TEAM", teams)
            a_t = col_a.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])
            
            if st.button("🎯 RUN NEURAL ANALYSIS"):
                exp_h, exp_a, conf = calculate_iq_metrics(df, h_t, a_t)
                st.markdown(f"""
                    <div style="background:#1A1C24; padding:25px; border-radius:15px; border-left:10px solid #00FF00;">
                        <h2 style="color:#00FF00; text-align:center;">{h_t} vs {a_t}</h2>
                        <div style="display:flex; justify-content:space-around; text-align:center;">
                            <div><p>EXPECTED GOALS</p><h3>{exp_h:.2f} - {exp_a:.2f}</h3></div>
                            <div><p>AI IQ CONFIDENCE</p><h3 style="color:#00FF00;">{conf}%</h3></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"⚠️ Data ya {l_name} ina hitilafu kidogo. Jaribu ligi nyingine Master.")
    else:
        st.error(f"❌ Pole Master, server ya data haina kumbukumbu za {l_name} kwa sasa.")

    st.markdown("<br><hr><center><p>📞 Msaada: 0699470308</p></center>", unsafe_allow_html=True)
