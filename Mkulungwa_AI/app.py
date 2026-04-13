import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib

# 1. UI SETUP
st.set_page_config(page_title="MKULUNGWA PREDICTION V14.8", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    .stButton>button { 
        background: linear-gradient(45deg, #00FF00, #004d00); 
        color: white; border-radius: 12px; height: 3.5em; width: 100%; border: none; font-weight: bold; font-size: 18px;
    }
    .result-card { 
        background-color: #1A1C24; padding: 20px; border-radius: 20px; 
        border-top: 4px solid #00FF00; margin-bottom: 20px; text-align: center;
    }
    h1 { color: #00FF00; text-align: center; font-size: 40px; }
    </style>
    """, unsafe_allow_html=True)

# 2. COMPLETE LEAGUE DATABASE (Zote ulizotaka Master)
LEAGUE_MAP = {
    "🏆 TOP ELITE MASHINDANO": {"Champions League (UEFA)": "CL", "Europa League (UEFA)": "EL", "Conference League (UEFA)": "EC"},
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENGLAND": {"Premier League": "E0", "Championship": "E1", "League 1": "E2", "League 2": "E3"},
    "🇪🇸 SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
    "🇮🇹 ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "🇩🇪 GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D2"},
    "🇫🇷 FRANCE": {"Ligue 1": "F1", "Ligue 2": "F2"},
    "🇳🇱 NETHERLANDS": {"Eredivisie": "N1"},
    "🇵🇹 PORTUGAL": {"Primeira Liga": "P1"},
    "🇹🇷 TURKEY": {"Süper Lig": "T1"},
    "🇧🇪 BELGIUM": {"Pro League": "B1"},
    "🇦🇹 AUSTRIA": {"Bundesliga": "A1"},
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 SCOTLAND": {"Premiership": "SC0"},
    "🇨🇭 SWITZERLAND": {"Super League": "C1"},
    "🇩🇰 DENMARK": {"Superliga": "D1"},
    "🇳🇴 NORWAY": {"Eliteserien": "N1"},
    "🇸🇪 SWEDEN": {"Allsvenskan": "S1"},
    "🇵🇱 POLAND": {"Ekstraklasa": "P1"},
