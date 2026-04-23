import streamlit as st
import pandas as pd
import numpy as np
import requests, joblib, os
from io import StringIO
from scipy.stats import poisson
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV

# ---------------- 1. UI SETUP (V45 ELITE STYLE) ----------------
st.set_page_config(page_title="V45 GLOBAL TRADING DESK", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #05070A; color: #E0E0E0; }
    .stMetric { background: #10141D; padding: 15px; border-radius: 12px; border: 1px solid #00FF00; box-shadow: 0px 4px 10px rgba(0, 255, 0, 0.1); }
    .elite-card { 
        background: #0A0F14; padding: 25px; border-radius: 15px; 
        border: 1px solid #00FF00; margin-bottom: 20px;
        box-shadow: 0px 4px 20px rgba(0, 255, 0, 0.2);
    }
    .status-badge { padding: 5px 15px; border-radius: 20px; font-weight: 900; text-transform: uppercase; }
    h1, h2, h3 { color: #00FF00; text-transform: uppercase; letter-spacing: 2px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌍 V45 GLOBAL TRADING DESK AI</h1>", unsafe_allow_html=True)

# ---------------- 2. GLOBAL LEAGUE MAP (Ligi Zote + Ligi Ndogo) ----------------
LEAGUE_MAP = {
    "ENGLAND: Premier": "E0",
    "ENGLAND: Championship": "E1",
    "ENGLAND: League 1": "E2",
    "SPAIN: La Liga": "SP1",
    "SPAIN: Segunda": "SP2",
    "GERMANY: Bundesliga 1": "D1",
    "GERMANY: Bundesliga 2": "D2",
    "ITALY: Serie A": "I1",
    "ITALY: Serie B": "I2",
    "FRANCE: Ligue 1": "F1",
    "FRANCE: Ligue 2": "F2",
    "NETHERLANDS: Eredivisie": "N1",
    "BELGIUM: Pro League": "B1",
    "PORTUGAL: Liga I": "P1",
    "TURKEY: Super Lig": "T1",
    "GREECE: Super League": "G1",
    "SCOTLAND: Premiership": "SC0",
    "SCOTLAND: Championship": "SC1"
}

# ---------------- 3. DATA ENGINE (Misimu 3 + Multi-League) ----------------
@st.cache_data(ttl=3600)
def load_global_data():
    seasons = ["2526", "2425", "2324"]
    dfs = []
    
    progress_bar = st.progress(0)
    total_steps = len(seasons) * len(LEAGUE_MAP)
    current_step = 0

    for s in seasons:
        for name, code in LEAGUE_MAP.items():
            try:
                url = f"https://www.football-data.co.uk/mmz4281/{s}/{code}.csv"
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    temp_df = pd.read_csv(StringIO(r.text))
                    # Tunachukua vigezo vya magoli na kona
                    cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HC', 'AC']
                    # Baadhi ya CSV zinaweza kosa HC/AC, tunahakikisha zipo
                    available_cols = [c for c in cols if c in temp_df.columns]
                    temp_df = temp_df[available_cols].dropna()
                    dfs.append(temp_df)
            except:
                continue
            current_step += 1
            progress_bar.progress(current_step / total_steps)
            
    full_df = pd.concat(dfs, ignore_index=True)
    full_df['total'] = full_df['FTHG'] + full_df['FTAG']
    full_df['over25'] = (full_df['total'] >= 3).astype(int)
    progress_bar.empty()
    return full_df

df_raw = load_global_data()

# ---------------- 4. FEATURE ENGINEERING ----------------
def process_features(df):
    df = df.copy()
    # Mahesabu ya fomu ya timu (Rolling 10 matches)
    for col in ['FTHG', 'FTAG', 'HC', 'AC']:
        if col not in df.columns: df[col] = 0 # Fill missing corners with 0 if any
        
    df['hg'] = df.groupby('HomeTeam')['FTHG'].transform(lambda x: x.rolling(10, min_periods=1).mean())
    df['ag'] = df.groupby('AwayTeam')['FTAG'].transform(lambda x: x.rolling(10, min_periods=1).mean())
    df['hc'] = df.groupby('HomeTeam')['HC'].transform(lambda x: x.rolling(10, min_periods=1).mean())
    df['ac'] = df.groupby('AwayTeam')['AC'].transform(lambda x: x.rolling(10, min_periods=1).mean())
    return df.dropna()

df_processed = process_features(df_raw)

# ---------------- 5. AI MODEL (CALIBRATED ENSEMBLE) ----------------
FEATS = ['hg', 'ag', 'hc', 'ac']
X = df_processed[FEATS]
y = df_processed['over25']

model_path = "global_v45_model.pkl"

if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    with st.spinner("🧠 Training Global AI (Misimu 3 + Ligi zote)..."):
        rf = RandomForestClassifier(n_estimators=300, random_state=42)
        lr = LogisticRegression(max_iter=1000)
        
        clf_rf = CalibratedClassifierCV(rf, cv=3).fit(X, y)
        clf_lr = CalibratedClassifierCV(lr, cv=3).fit(X, y)
        
        model = {"rf": clf_rf, "lr": clf_lr}
        joblib.dump(model, model_path)

# ---------------- 6. ANALYSIS ENGINES ----------------
def predict_proba(x_input):
    p1 = model["rf"].predict_proba(x_input)[0][1]
    p2 = model["lr"].predict_proba(x_input)[0][1]
    return (p1 + p2) / 2

def poisson_prob(h_exp, a_exp):
    p = 0
    for i in range(6):
        for j in range(6):
            pr = poisson.pmf(i, h_exp) * poisson.pmf(j, a_exp)
            if i + j >= 3: p += pr
    return p

def kelly_criterion(p, odds):
    b = odds - 1
    if b <= 0: return 0
    q = 1 - p
    f = (b * p - q) / b
    return max(0, f) * 0.5 # Conservative (Half-Kelly)

# ---------------- 7. MAIN INTERFACE ----------------
st.subheader("🎯 Global Market Analyzer")

col_l, col_h, col_a, col_o = st.columns([2, 2, 2, 1])

with col_l:
    league_choice = st.selectbox("LIGI", list(LEAGUE_MAP.keys()))
    # Filter timu kulingana na ligi iliyochaguliwa
    league_code = LEAGUE_MAP[league_choice]
    # Hapa tunafanya filter ndogo ya timu zilizopo kwenye hiyo ligi (Data ya msimu huu)
    league_teams = sorted(df_raw[df_raw['HomeTeam'].isin(df_raw['HomeTeam'].unique())]['HomeTeam'].unique())

with col_h: home = st.selectbox("HOME", league_teams)
with col_a: away = st.selectbox("AWAY", [t for t in league_teams if t != home])
with col_o: odds = st.number_input("ODDS (O2.5)", value=1.85, step=0.01)

# Analysis Logic
h_stats = df_processed[df_processed['HomeTeam'] == home].tail(1)
a_stats = df_processed[df_processed['AwayTeam'] == away].tail(1)

if not h_stats.empty and not a_stats.empty:
    hg, ag = h_stats['hg'].values[0], a_stats['ag'].values[0]
    hc, ac = h_stats['hc'].values[0], a_stats['ac'].values[0]
    
    x_input = np.array([[hg, ag, hc, ac]])
    
    p_ml = predict_proba(x_input)
    p_po = poisson_prob(hg, ag)
    final_p = (0.5 * p_ml) + (0.5 * p_po)
    value = (final_p * odds) - 1
    stake_pct = kelly_criterion(final_p, odds)

    # --- OUTPUT DISPLAY ---
    st.markdown("<div class='elite-card'>", unsafe_allow_html=True)
    st.write(f"### ANALYSIS: {home} vs {away} ({league_choice})")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("AI PROB", f"{final_p*100:.1f}%")
    m2.metric("POISSON", f"{p_po*100:.1f}%")
    m3.metric("VALUE", f"{value:.2f}", delta=f"{value*100:.1f}%")
    m4.metric("STAKE", f"{stake_pct*100:.1f}%")

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
    
    if final_p > 0.72 and value > 0.08:
        sig, col = "🔥 ELITE TRADE", "#00FF00"
    elif final_p > 0.64:
        sig, col = "⚡ HIGH TRADE", "#CCFF00"
    elif final_p > 0.55:
        sig, col = "⚠️ MEDIUM RISK", "#FFFF00"
    else:
        sig, col = "❌ NO TRADE", "#FF4B4B"

    st.markdown(f"<h2 style='color:{col};'>SIGNAL: {sig}</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- PORTFOLIO ---
    if "my_trades" not in st.session_state: st.session_state.my_trades = []
    
    if st.button("➕ ADD TO MY TRAIN"):
        st.session_state.my_trades.append({
            "League": league_choice,
            "Match": f"{home} vs {away}",
            "Prob": f"{final_p*100:.1f}%",
            "Value": f"{value:.2f}",
            "Stake": f"{stake_pct*100:.1f}%"
        })
        st.success("Imewekwa kwenye Behewa!")

    if st.session_state.my_trades:
        st.subheader("📦 MY CURRENT TRAIN (PORTFOLIO)")
        st.table(st.session_state.my_trades)

else:
    st.warning("Data haitoshi kwa timu hizi kwenye database yetu.")

# --- SIDEBAR TOOLS ---
with st.sidebar:
    st.header("⚙️ SYSTEM TOOLS")
    if st.button("🔄 RETRAIN ENTIRE AI"):
        if os.path.exists(model_path): os.remove(model_path)
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.write("📊 **Vigezo Vinavyotumika:**")
    st.write("- Misimu: 2023 - 2026")
    st.write("- Vyanzo: Football-Data.co.uk")
    st.write("- Logic: Ensemble ML + Poisson")
