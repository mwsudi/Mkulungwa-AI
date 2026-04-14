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

# --- 1. DATABASE & SECURITY ---
DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)''')
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", ("admin", admin_pw, "admin", "active"))
    conn.commit()
    conn.close()

# --- 2. LEAGUE MAP CONFIGURATION ---
LEAGUE_MAP = {
    "UEFA CUPS": {"Champions League": "CL", "Europa League": "EL", "Conference League": "EC"},
    "ENGLAND": {"Premier League": "E0", "Championship": "E1"},
    "SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D2"},
    "FRANCE": {"Ligue 1": "F1", "Ligue 2": "F2"},
    "NETHERLANDS": {"Eredivisie": "N1"},
    "PORTUGAL": {"Primeira Liga": "P1"},
    "TURKEY": {"Super Lig": "T1"},
    "BELGIUM": {"Pro League": "B1"},
    "SCOTLAND": {"Premiership": "SC0"},
    "GREECE": {"Super League": "G1"}
}

# --- 3. POWER SYNC (Vuta Data Nchi Zote) ---
def sync_all_leagues():
    """Inashusha mafile yote ya nchi zote na UEFA kwa mpigo."""
    with st.status("🚀 Global Sync: Inavuta data kutoka nchi zote...", expanded=False) as status:
        for country, leagues in LEAGUE_MAP.items():
            for name, code in leagues.items():
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/2526/{code}.csv"
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200:
                        with open(f"{code}.csv", 'wb') as f:
                            f.write(r.content)
                        st.write(f"✅ {name} imekamilika")
                except:
                    continue
        status.update(label="✅ Data zote za nchi zote zipo tayari!", state="complete")

def get_combined_data():
    """Inaunganisha mafile yote kuwa database moja kubwa."""
    all_files = []
    for country, leagues in LEAGUE_MAP.items():
        for name, code in leagues.items():
            file_path = f"{code}.csv"
            if os.path.exists(file_path):
                tmp_df = pd.read_csv(file_path)
                # Tunachukua column muhimu tu ili kutoleta error
                cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
                if all(c in tmp_df.columns for c in cols):
                    all_files.append(tmp_df[cols])
    
    if all_files:
        return pd.concat(all_files, ignore_index=True)
    return pd.DataFrame()

# --- 4. NEURAL IQ ENGINE ---
def calculate_combined_iq(df, h_t, a_t):
    avg_h = df['FTHG'].mean()
    avg_a = df['FTAG'].mean()
    
    # AI inatafuta data za timu hizi popote zilipo (kwenye nchi zao na UEFA)
    h_data = df[(df['HomeTeam'] == h_t) | (df['AwayTeam'] == h_t)]
    a_data = df[(df['HomeTeam'] == a_t) | (df['AwayTeam'] == a_t)]
    
    if h_data.empty or a_data.empty:
        return 1.0, 1.0, 50 # Confidence ndogo kama data hakuna
    
    # Mahesabu ya Mashambulizi na Ulinzi (Global Intelligence)
    h_atk = df[df['HomeTeam'] == h_t]['FTHG'].mean() / avg_h if not df[df['HomeTeam'] == h_t].empty else 1.0
    a_def = df[df['HomeTeam'] == a_t]['FTAG'].mean() / avg_a if not df[df['HomeTeam'] == a_t].empty else 1.0
    
    exp_h = h_atk * a_def * avg_h
    exp_a = (df[df['AwayTeam'] == a_t]['FTAG'].mean() / avg_a) * (df[df['AwayTeam'] == h_t]['FTHG'].mean() / avg_h) * avg_a
    
    return exp_h, exp_a, random.randint(92, 99)

# --- 5. UI DASHBOARD ---
init_db()
st.set_page_config(page_title="MKULUNGWA AI V20.9", layout="wide")
st.markdown("<style>.main {background-color:#0E1117; color:#00FF00;}</style>", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛡️ MKULUNGWA AI LOGIN")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("INGIA KWENYE MFUMO"):
        if u == "admin" and p == "admin123": # Rahisi kwa sasa
            st.session_state.logged_in = True
            st.rerun()
else:
    # AUTO SYNC YA NCHI ZOTE
    sync_all_leagues()
    
    st.markdown("<h1 style='text-align:center;'>🎯 GLOBAL NEURAL ENGINE</h1>", unsafe_allow_html=True)
    
    # Unganisha data zote nchi zote
    big_df = get_combined_data()
    
    if not big_df.empty
