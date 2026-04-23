import streamlit as st
import pandas as pd
import numpy as np
import requests, os, joblib
from io import StringIO
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MKULUNGWA GOD MODE", layout="wide")
st.title("🧠⚡ MKULUNGWA – AI BETTING ENGINE")

MODEL_PATH = "god_mode_model.pkl"
ODDS_API_KEY = st.secrets.get("ODDS_API_KEY", "")

# ---------------- LEAGUES ----------------
COUNTRY_MAP = {
    "ENGLAND": {"Premier": "E0", "Championship": "E1"},
    "SPAIN": {"La Liga": "SP1"},
    "GERMANY": {"Bundesliga": "D1"},
    "ITALY": {"Serie A": "I1"},
    "FRANCE": {"Ligue 1": "F1"}
}

# ---------------- LOAD DATA ----------------
@st.cache_data(ttl=3600)
def load_data():
    seasons = ["2425","2324"]
    dfs = []
    for s in seasons:
        for c in COUNTRY_MAP:
            for lg, code in COUNTRY_MAP[c].items():
                try:
                    url = f"https://www.football-data.co.uk/mmz4281/{s}/{code}.csv"
                    r = requests.get(url, timeout=10)
                    df = pd.read_csv(StringIO(r.text))
                    df["Country"], df["League"] = c, lg
                    dfs.append(df[['HomeTeam','AwayTeam','FTHG','FTAG','Country','League']])
                except:
                    pass
    df = pd.concat(dfs)
    df['total'] = df['FTHG'] + df['FTAG']
    df['over25'] = (df['total'] >= 3).astype(int)
    return df

df = load_data()

# ---------------- FEATURES ----------------
def features(df):
    df = df.copy()
    df['hg'] = df.groupby('HomeTeam')['FTHG'].transform(lambda x: x.rolling(5).mean())
    df['ag'] = df.groupby('AwayTeam')['FTAG'].transform(lambda x: x.rolling(5).mean())
    df['hc'] = df.groupby('HomeTeam')['FTAG'].transform(lambda x: x.rolling(5).mean())
    df['ac'] = df.groupby('AwayTeam')['FTHG'].transform(lambda x: x.rolling(5).mean())
    df['hs'] = df['hg'] - df['hc']
    df['as_'] = df['ag'] - df['ac']
    return df.dropna()

df = features(df)

FEATS = ['hg','ag','hc','ac','hs','as_']
X = df[FEATS]
y = df['over25']

# ---------------- MODEL ----------------
def train():
    rf = RandomForestClassifier(n_estimators=300).fit(X,y)
    lr = LogisticRegression(max_iter=500).fit(X,y)
    m = {"rf":rf,"lr":lr}
    joblib.dump(m, MODEL_PATH)
    return m

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
    except:
        model = train()
else:
    model = train()

# ---------------- POISSON ----------------
def poisson(h,a):
    return min(0.95,(h+a)/3)

# ---------------- ODDS ----------------
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
        r = requests.get(url, params=params)
        data = r.json()
    except:
        return pd.DataFrame()

    rows=[]
    for ev in data:
        home = ev.get("home_team")
        away = [t for t in ev.get("teams",[]) if t!=home]
        away = away[0] if away else None

        best=None
        for bk in ev.get("bookmakers",[]):
            for mk in bk.get("markets",[]):
                if mk.get("key")=="totals":
                    for o in mk.get("outcomes",[]):
                        if o.get("name")=="Over" and float(o.get("point",0))==2.5:
                            price=o.get("price")
                            if price:
                                best=max(best or 0,price)
        if home and away and best:
            rows.append({"HomeTeam":home,"AwayTeam":away,"odds":best})
    return pd.DataFrame(rows)

odds_df = load_odds()

# ---------------- PREDICT ----------------
def predict(h,a):
    h_row = df[df['HomeTeam']==h].tail(1)
    a_row = df[df['AwayTeam']==a].tail(1)
    if h_row.empty or a_row.empty:
        return None

    hg=h_row['hg'].values[0]
    ag=a_row['ag'].values[0]
    hc=h_row['hc'].values[0]
    ac=a_row['ac'].values[0]
    hs=h_row['hs'].values[0]
    as_=a_row['as_'].values[0]

    f=[[hg,ag,hc,ac,hs,as_]]

    p1=model["rf"].predict_proba(f)[0][1]
    p2=model["lr"].predict_proba(f)[0][1]
    p3=poisson(hg,ag)

    return (0.5*p1+0.3*p2+0.2*p3)

# ---------------- UI ----------------
st.subheader("📡 LIVE SIGNALS")

if odds_df.empty:
    st.warning("Hakuna odds (weka API baadaye)")
else:
    results=[]
    for _,r in odds_df.iterrows():
        p=predict(r['HomeTeam'],r['AwayTeam'])
        if p is None: continue

        odds=r['odds']
        mp=1/odds
        edge=p-mp
        value=(p*odds)-1

        results.append({
            "Match":f"{r['HomeTeam']} vs {r['AwayTeam']}",
            "Odds":odds,
            "AI%":round(p*100,1),
            "Edge%":round(edge*100,1),
            "Value":round(value,2)
        })

    table=pd.DataFrame(results).sort_values(by="Edge%",ascending=False)
    st.dataframe(table)

# ---------------- MANUAL ----------------
st.subheader("🎯 MANUAL ANALYSIS")

teams=sorted(df['HomeTeam'].unique())
c1,c2,c3=st.columns(3)

with c1: home=st.selectbox("HOME",teams)
with c2: away=st.selectbox("AWAY",[t for t in teams if t!=home])
with c3: odds=st.number_input("ODDS",value=1.9)

p=predict(home,away)
if p:
    mp=1/odds
    edge=p-mp
    val=(p*odds)-1

    st.metric("AI%",f"{p*100:.1f}")
    st.metric("EDGE%",f"{edge*100:.1f}")
    st.metric("VALUE",f"{val:.2f}")
