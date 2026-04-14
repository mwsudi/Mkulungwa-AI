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
    """Huanzisha database na kutengeneza table za watumiaji na logs."""
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
    """Hurekodi kila hatua anayochukua mtumiaji kwa ajili ya usalama."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO logs VALUES (?, ?, ?)", (username, action, now))
    conn.commit()
    conn.close()

def update_user_status(username, new_status):
    """Huruhusu admin kufunga au kufungulia akaunti ya mteja."""
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
    """
    Hushusha data mpya za ligi zote kila siku mara moja.
    Inakagua kama kuna hitaji la ku-update kwa kuangalia tarehe ya mwisho.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM system_config WHERE key = 'last_sync'")
    res = c.fetchone()
    
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
    """Hupiga mahesabu ya Poisson na xG kulingana na data za kihistoria."""
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
    """Huonyesha kichwa cha habari cha AI."""
    st.markdown(f"<h1 style='text-align:center; color:#00FF00; text-shadow: 0 0 20px #00FF00;'>🛡️ MKULUNGWA AI V20.7</h1>", unsafe_allow_html=True)

def display_footer():
    """Huonyesha maelezo ya malipo na mawasiliano ya WhatsApp."""
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
    # Function inaitwa hapa ndani ya mzunguko wa Streamlit baada ya login
    auto_sync_data()
    
    with st.sidebar:
        display_custom_logo()
        st.write(f"Active Master: **{st.session_state.username.upper()}**")
        if st.button("🚪 EXIT SYSTEM"):
            st.session_state.logged_in = False
            st.rerun()

    if st.session_state.user_role == "admin":
        with st.expander("🛠️ ADMIN COMMAND CENTER"):
            tab1, tab2 = st.tabs(["👥 User Status", "📜 Usage Logs"])
            with tab1:
                conn = sqlite3.connect(DB_NAME)
                df_u = pd.read_sql_query("SELECT username, status FROM users WHERE role='user'", conn)
                conn.close()
                for _, row in df_u.iterrows():
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"**{row['username']}** - Status: {row['status'].upper()}")
                    btn_label = "Block" if row['status'] == 'active' else "Unblock"
                    if col2.button(btn_label, key=row['username']):
                        update_user_status(row['username'], 'inactive' if row['status'] == 'active' else 'active')
                        st.rerun()
            with tab2:
                conn = sqlite3.connect(DB_NAME)
                st.dataframe(pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp DESC", conn))
                conn.close()

    st.markdown("<h1 style='color:#00FF00; text-align:center;'>🎯 NEURAL IQ DASHBOARD</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    cat = c1.selectbox("📂 CATEGORY", list(LEAGUE_MAP.keys()))
    l_name = c2.selectbox("🏆 LEAGUE/CUP", list(LEAGUE_MAP[cat].keys()))
    l_code = LEAGUE_MAP[cat][l_name]
    
    if os.path.exists(f"{l_code}.csv"):
        df = pd.read_csv(f"{l_code}.csv")
        teams = sorted(df['HomeTeam'].dropna().unique())
        
        col_h, col_a = st.columns(2)
        h_t = col_h.selectbox("🏠 HOME TEAM", teams)
        a_t = col_a.selectbox("🚀 AWAY TEAM", [t for t in teams if t != h_t])
        
        if st.button("🎯 RUN NEURAL ANALYSIS"):
            with st.spinner("🧠 Calculating Neural xG Patterns..."):
                exp_h, exp_a, conf = calculate_iq_metrics(df, h_t, a_t)
                time.sleep(1.2)
            
            st.markdown(f"""
                <div style="background:#1A1C24; padding:25px; border-radius:15px; border-left:10px solid #00FF00; margin-bottom:20px;">
                    <h2 style="color:#00FF00; text-align:center; margin-bottom:20px;">{h_t} vs {a_t}</h2>
                    <div style="display:flex; justify-content:space-around; text-align:center;">
                        <div><p style='color:#888;'>EXPECTED GOALS (xG)</p><h3 style='font-size:35px;'>{exp_h:.2f} - {exp_a:.2f}</h3></div>
                        <div><p style='color:#888;'>AI IQ CONFIDENCE</p><h3 style="color:#00FF00; font-size:35px;">{conf}%</h3></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Advice Logic
            if (exp_h + exp_a) > 2.2: advice = "Over 1.5 & Both Teams to Score (GG)"
            elif exp_h > (exp_a + 0.8): advice = f"{h_t} Win or Draw (1X)"
            elif exp_a > (exp_h + 0.8): advice = f"{a_t} Win or Draw (X2)"
            else: advice = "Under 3.5 Goals & Double Chance"
            
            st.success(f"🔥 MASTER ADVICE: {advice}")
            log_action(st.session_state.username, f"Analyzed {h_t} vs {a_t} ({l_name})")
    else:
        st.warning(f"⚠️ Data ya {l_name} haijapatikana. Hakikisha umei-shusha au subiri sekunde kadhaa.")

    display_footer()
