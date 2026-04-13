import streamlit as st
import pandas as pd
import os
import numpy as np
import requests
import time
import hashlib

# 1. UI SETUP - ELITE GLOBAL DESIGN
st.set_page_config(page_title="MKULUNGWA PREDICTION V14.7", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    .stSelectbox div[data-baseweb="select"] { background-color: #1A1C24; color: white; border-radius: 12px; }
    .stButton>button { 
        background: linear-gradient(45deg, #00FF00, #004d00); 
        color: white; border-radius: 15px; height: 4em; width: 100%; border: none; font-weight: bold; font-size: 20px;
        box-shadow: 0px 6px 20px rgba(0, 255, 0, 0.3); transition: 0.3s;
    }
    .result-card { 
        background-color: #1A1C24; padding: 30px; border-radius: 25px; 
        border-top: 4px solid #00FF00; box-shadow: 0px 10px 30
