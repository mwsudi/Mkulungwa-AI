import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib

# 1. UI SETUP
st.set_page_config(page_title="MKULUNGWA AI V15.9", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stButton>button { 
        background: linear-gradient(45deg, #00FF00, #004d00); 
        color: white; border-radius: 10px; height: 3.5em; width: 100%; border: none; font-weight: bold;
    }
    .result-card { 
        background-color: #1A1C24; padding: 25px; border-radius: 20px; 
        border-top: 5px solid #00FF00; text-align: center; margin-bottom: 20px;
    }
    h1 { color: #00FF00; text-align: center; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# 2. MASTER DATABASE STRUCTURE - FIXED & CLOSED PROPERLY
LEAGUE_MAP = {
    "UEFA / EUROPA / CONFERENCE": {"ALL_EUROPE": "UEFA_ALL"},
    "ENGLAND": {"Premier League": "E0", "Championship": "E1"},
    "SPAIN": {"La Liga": "SP1", "La Liga 2": "SP2"},
    "ITALY": {"Serie A": "I1", "Serie B": "I2"},
    "GERMANY": {"Bundesliga": "D1", "Bundesliga 2": "D
