import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
from math import exp, factorial

# =========================================
# BIST WAPAMBANAJI AI - ELITE 2026 v9.0 PRO
# =========================================

st.set_page_config(
    page_title="BIST WAPAMBANAJI AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================
# FOOTBALL-DATA.ORG API CONFIG
# =========================================

API_KEY = "2493de184054414dae83d3a909d012d0"
HEADERS = {"X-Auth-Token": API_KEY}

# =========================================
# STYLE ENGINE
# =========================================

st.markdown("""
<style>
.main{ background:#0d1117; color:#e6edf3; }
[data-testid="stSidebar"]{ background:#0b0e14; border-right:2px solid #ffd700; }
.stButton>button{
    background:linear-gradient(135deg,#ffd700 0%,#b8860b 100%);
    color:black !important; border:none; border-radius:10px;
    height:3.5em; font-weight:900; width:100%;
}
.card{
    background:#161b22; padding:25px; border-radius:15px;
    border-left:5px solid #ffd700; text-align:center; margin-bottom:20px;
}
.big-val{ font-size:30px; font-weight:900; color:#ffd700; }
.small{ color:#8b949e; font-size:14px; }
.section-title{
    color:#ffd700; font-size:24px; font-weight:bold; margin-top:25px;
    margin-bottom:15px; border-bottom:2px solid #ffd700; padding-bottom:10px;
}
.signal-box{
    padding:30px; border-radius:20px; text-align:center;
    font-size:30px; font-weight:900; margin:20px 0; background:#0d1117;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# DATA FUNCTIONS
# =========================================

@st.cache_data(ttl=3600)
def load_league_data(code):
    for season in ["2526", "2425"]:
        try:
            url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return pd.read_csv(StringIO(r.text))
        except: continue
    return None

def test_api_connection():
    try:
        url = "https://api.football-data.org/v4/competitions/PL"
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.status_code == 200
    except: return False

@st.cache_data(ttl=1800)
def get_standings(league_api_code):
    try:
        url = f"https://api.football-data.org/v4/competitions/{league_api_code}/standings"
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        if "standings" in data:
            return data["standings"][0]["table"]
        return []
    except: return []

# =========================================
# LEAGUE MAP
# =========================================

LEAGUE_MAP = {
    "ENGLAND": {
        "Premier League": {"csv": "E0", "api": "PL"},
        "Championship": {"csv": "E1", "api": "ELC"}
    },
    "SPAIN": {
        "La Liga": {"csv": "SP1",
