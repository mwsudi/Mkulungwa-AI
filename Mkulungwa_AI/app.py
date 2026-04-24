import streamlit as st
import pandas as pd
import numpy as np
import requests, os, joblib
from io import StringIO
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import TimeSeriesSplit
from rapidfuzz import process, fuzz

# ---------------- CONFIG ----------------
st.set_page_config(page_title="BET PLANNER PRO+", layout="wide")
st.title("🧠📊 BET PLANNER PRO+ (Calibrated Value Desk)")

MODEL_PATH = "model_pro_plus.pkl"
HISTORY_PATH = "bet_history.csv"
ODDS_API_KEY = st.secrets.get("ODDS_API_KEY", "")

# ---------------- LEAGUES ----------------
COUNTRY_MAP = {
    "ENGLAND": {"Premier": "E0", "Championship": "E1"},
    "SPAIN": {"La Liga": "SP1"},
    "GERMANY": {"Bundesliga": "D1"},
    "ITALY": {"Serie A": "I1"},
    "FRANCE": {"Ligue 1": "F1"},
    "PORTUGAL": {"Liga": "P1"},
    "NETHERLANDS": {"Eredivisie": "N1"},
    "BELGIUM": {"Pro League": "B1"},
    "SCOTLAND": {"Premiership": "SC0"}
}

# ---------------- DATA ----------------
@st.cache_data(ttl=3600)
def load_history():
    seasons = ["2425","2324","2223"]
    dfs = []
    for s in seasons:
        for c in COUNTRY_MAP:
            for lg, code in COUNTRY_MAP[c].items():
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/{s}/{code}.csv"
                    r = requests.get(url, timeout=15)
                    if r.status_code != 200: continue
                    d = pd.read_csv(StringIO(r.text))
                    d["Country"], d["League"] = c, lg
                    d = d[["Date","HomeTeam","AwayTeam","FTHG","FTAG"]].dropna()
                    # parse date if exists
                    if "Date" in d.columns:
                        try:
                            d["Date"] = pd.to_datetime(d["Date"], dayfirst=True, errors="coerce")
                        except:
                            pass
                    dfs.append(d)
                except:
                    continue
    df = pd.concat(dfs, ignore_index=True)
    df = df.sort_values(by="Date") if "Date" in df.columns else df
    df["total"] = df["FTHG"] + df["FTAG"]
    df["over25"] = (df["total"] >= 3).astype(int)
    return df

df_raw = load_history()

# ---------------- FEATURES ----------------
def make_features(df):
    df = df.copy()
    # rolling windows
    for w in [5, 10]:
        df[f"hg_{w}"] = df.groupby("HomeTeam")["FTHG"].transform(lambda x: x.rolling(w, min_periods=1).mean())
        df[f"ag_{w}"] = df.groupby("AwayTeam")["FTAG"].transform(lambda x: x.rolling(w, min_periods=1).mean())
        df[f"hc_{w}"] = df.groupby("HomeTeam")["FTAG"].transform(lambda x: x.rolling(w, min_periods=1).mean())
        df[f"ac_{w}"] = df.groupby("AwayTeam")["FTHG"].transform(lambda x: x.rolling(w, min_periods=1).mean())

    # strength & tempo
    df["hs"] = df["hg_5"] - df["hc_5"]
    df["as_"] = df["ag_5"] - df["ac_5"]
    df["tempo"] = (df["hg_5"] + df["ag_5"]) / 2

    # xG proxy (simple blend)
    df["xg_home"] = 0.6*df["hg_5"] + 0.4*df["ac_5"]
    df["xg_away"] = 0.6*df["ag_5"] + 0.4*df["hc_5"]
    df["xg_total"] = df["xg_home"] + df["xg_away"]

    feats = ["hg_5","ag_5","hc_5","ac_5","hs","as_","tempo","xg_home","xg_away","xg_total"]
    return df.dropna(subset=feats), feats

df, FEATS = make_features(df_raw)
X, y = df[FEATS], df["over25"]

# ---------------- MODEL (CALIBRATED) ----------------
def train_model():
    # time-aware split (simple)
    tscv = TimeSeriesSplit(n_splits=3)
    # base models
    rf = RandomForestClassifier(n_estimators=500, random_state=42)
    lr = LogisticRegression(max_iter=600)

    # calibrated wrappers (Platt scaling)
    rf_cal = CalibratedClassifierCV(rf, method="sigmoid", cv=tscv)
    lr_cal = CalibratedClassifierCV(lr, method="sigmoid", cv=tscv)

    rf_cal.fit(X, y)
    lr_cal.fit(X, y)

    m = {"rf": rf_cal, "lr": lr_cal}
    joblib.dump(m, MODEL_PATH)
    return m

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
    except:
        model = train_model()
else:
    model = train_model()

# ---------------- POISSON PROXY ----------------
def poisson_prob(xg_h, xg_a):
    return min(0.95, (xg_h + xg_a) / 3.0)

# ---------------- ODDS (LIVE) ----------------
@st.cache_data(ttl=300)
def load_odds():
    if not ODDS_API_KEY:
        return pd.DataFrame()
    url = "https://api.the-odds-api.com/v4/sports/soccer/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "totals",
        "oddsFormat": "decimal"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return pd.DataFrame()
        data = r.json()
    except:
        return pd.DataFrame()

    rows = []
    for ev in data:
        home = ev.get("home_team")
        teams = ev.get("teams", [])
        away = [t for t in teams if t != home]
        away = away[0] if away else None

        best_over25 = 0
        best_under25 = 0

        for bk in ev.get("bookmakers", []):
            for mk in bk.get("markets", []):
                if mk.get("key") == "totals":
                    for o in mk.get("outcomes", []):
                        if float(o.get("point",0)) == 2.5:
                            if o.get("name")=="Over":
                                best_over25 = max(best_over25, o.get("price",0))
                            if o.get("name")=="Under":
                                best_under25 = max(best_under25, o.get("price",0))

        if home and away and best_over25>1:
            rows.append({
                "HomeTeam": home.strip(),
                "AwayTeam": away.strip(),
                "odds_over25": float(best_over25),
                "odds_under25": float(best_under25) if best_under25>1 else np.nan
            })
    return pd.DataFrame(rows)

odds_df = load_odds()

# ---------------- TEAM NAME MATCH (FUZZY) ----------------
def best_match(name, candidates, threshold=80):
    if not candidates:
        return None
    match = process.extractOne(name, candidates, scorer=fuzz.WRatio)
    if match and match[1] >= threshold:
        return match[0]
    return None

home_candidates = sorted(df["HomeTeam"].unique())
away_candidates = sorted(df["AwayTeam"].unique())

def get_vec(h_name, a_name):
    h_match = best_match(h_name, home_candidates)
    a_match = best_match(a_name, away_candidates)
    if not h_match or not a_match:
        return None

    hdf = df[df["HomeTeam"]==h_match].tail(1)
    adf = df[df["AwayTeam"]==a_match].tail(1)
    if hdf.empty or adf.empty:
        return None

    vec = [
        float(hdf["hg_5"]), float(adf["ag_5"]),
        float(hdf["hc_5"]), float(adf["ac_5"]),
        float(hdf["hs"]), float(adf["as_"]),
        float((hdf["tempo"])),
        float(hdf["xg_home"]), float(adf["xg_away"]),
        float(hdf["xg_total"])
    ]
    return vec

# ---------------- PREDICT ----------------
def predict_prob(vec):
    p_rf = model["rf"].predict_proba([vec])[0][1]
    p_lr = model["lr"].predict_proba([vec])[0][1]
    p_ps = poisson_prob(vec[7], vec[8])
    return (0.5*p_rf) + (0.3*p_lr) + (0.2*p_ps)

def kelly_fraction(p, odds, cap=0.1):
    b = odds - 1
    q = 1 - p
    f = (b*p - q) / b if b > 0 else 0
    return max(0, min(f, cap))

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Controls")
    bankroll = st.number_input("Bankroll", value=100.0, step=10.0)
    min_edge = st.slider("Min Edge (%)", 0.0, 20.0, 5.0) / 100
    min_prob = st.slider("Min AI Prob (%)", 0.0, 90.0, 60.0) / 100
    top_k = st.slider("Top Picks", 3, 20, 10)
    acc_size = st.slider("Accumulator Size", 2, 4, 3)
    kelly_cap = st.slider("Kelly Cap (%)", 2, 10, 5) / 100

# ---------------- BUILD TABLE ----------------
rows = []
for _, r in odds_df.iterrows():
    vec = get_vec(r["HomeTeam"], r["AwayTeam"])
    if vec is None:
        continue

    p = predict_prob(vec)
    odds = float(r["odds_over25"])
    market_p = 1.0 / odds
    edge = p - market_p
    value = (p * odds) - 1

    # simple overround sanity if under odds exist
    if not np.isnan(r.get("odds_under25", np.nan)):
        overround = (1.0/odds) + (1.0/float(r["odds_under25"]))
        if overround > 1.12:  # skip very high margins
            continue

    kelly = kelly_fraction(p, odds, cap=kelly_cap)
    stake = bankroll * kelly

    rows.append({
        "Match": f'{r["HomeTeam"]} vs {r["AwayTeam"]}',
        "Odds": odds,
        "AI_Prob": p,
        "Market_Prob": market_p,
        "Edge": edge,
        "Value": value,
        "Kelly%": kelly,
        "Stake": stake
    })

table = pd.DataFrame(rows)

# ---------------- FILTER & SORT ----------------
if not table.empty:
    table = table[(table["Edge"] >= min_edge) & (table["AI_Prob"] >= min_prob)]
    table = table.sort_values(by=["Edge","Value","AI_Prob"], ascending=False).head(top_k)

# ---------------- OUTPUT ----------------
st.subheader("📊 TOP PICKS (Filtered)")
if table.empty:
    st.info("Hakuna picks zinazokidhi filters zako kwa sasa.")
else:
    show = table.copy()
    show["AI_Prob"] = (show["AI_Prob"]*100).round(1).astype(str) + "%"
    show["Market_Prob"] = (show["Market_Prob"]*100).round(1).astype(str) + "%"
    show["Edge"] = (show["Edge"]*100).round(1).astype(str) + "%"
    show["Kelly%"] = (show["Kelly%"]*100).round(1).astype(str) + "%"
    show["Stake"] = show["Stake"].round(2)
    st.dataframe(show, use_container_width=True)

    # ---------------- ACCUMULATOR ----------------
    if len(table) >= acc_size:
        acc = table.head(acc_size)
        acc_odds = np.prod(acc["Odds"])
        st.subheader("🔗 ACCUMULATOR (Controlled)")
        st.write(acc[["Match","Odds"]])
        st.success(f"TOTAL ODDS: {acc_odds:.2f}")

    # ---------------- PLAN ----------------
    st.subheader("📌 DAILY PLAN (Singles First)")
    for _, r in table.head(5).iterrows():
        tier = "🔥 ELITE" if r["Edge"]>0.10 and r["AI_Prob"]>0.70 else ("⚡ STRONG" if r["Edge"]>0.05 else "🟡 SMALL")
        st.write(f"{r['Match']} | Odds {r['Odds']:.2f} | AI {r['AI_Prob']*100:.1f}% | Edge {r['Edge']*100:.1f}% | {tier} | Stake {r['Stake']:.2f}")

# ---------------- QUICK BACKTEST (SNAPSHOT) ----------------
st.subheader("📈 QUICK BACKTEST (Snapshot)")
if not df.empty:
    # simple last 500 rows split
    dft = df.tail(500).copy()
    # naive: use current model to score
    probs = model["rf"].predict_proba(dft[FEATS])[:,1]
    # combine with LR + poisson proxy
    probs_lr = model["lr"].predict_proba(dft[FEATS])[:,1]
    probs_ps = np.minimum(0.95, (dft["xg_home"]+dft["xg_away"])/3.0)
    p = 0.5*probs + 0.3*probs_lr + 0.2*probs_ps

    # assume constant odds 1.90 for illustration
    odds = 1.90
    market_p = 1/odds
    edge = p - market_p

    mask = (p >= min_prob) & (edge >= min_edge)
    sel = dft[mask]
    if len(sel) > 0:
        wins = (sel["over25"]==1).sum()
        total = len(sel)
        hit = wins/total
        # ROI approx
        profit = (wins*(odds-1)) - (total-wins)*1
        roi = profit/total
        c1, c2, c3 = st.columns(3)
        c1.metric("Bets", total)
        c2.metric("Hit Rate", f"{hit*100:.1f}%")
        c3.metric("ROI (approx)", f"{roi*100:.1f}%")
    else:
        st.info("Hakuna samples zinazokidhi filters kwenye snapshot.")
