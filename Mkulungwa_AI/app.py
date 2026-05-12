import streamlit as st

import pandas as pd

import numpy as np

import requests

from io import StringIO

from math import exp, factorial



# =========================================

# BIST WAPAMBANAJI AI - ELITE 2026 v8.0 PRO

# =========================================



st.set_page_config(

    page_title="BIST WAPAMBANAJI AI",

    layout="wide",

    initial_sidebar_state="expanded"

)



# =========================================

# RAPID API CONFIG

# =========================================



API_KEY = "ccc042181cmsh922f2c2406a2e16p15503fjsnd189126344bb"



HEADERS = {

    "x-rapidapi-key": API_KEY,

    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"

}



# =========================================

# STYLE

# =========================================



st.markdown("""

<style>



.main{

    background:#0d1117;

    color:#e6edf3;

}



[data-testid="stSidebar"]{

    background:#0b0e14;

    border-right:2px solid #ffd700;

}



.stButton>button{

    background:linear-gradient(135deg,#ffd700 0%,#b8860b 100%);

    color:black !important;

    border:none;

    border-radius:10px;

    height:3.5em;

    font-weight:900;

    width:100%;

}



.card{

    background:#161b22;

    padding:25px;

    border-radius:15px;

    border-left:5px solid #ffd700;

    text-align:center;

    margin-bottom:20px;

}



.big-val{

    font-size:30px;

    font-weight:900;

    color:#ffd700;

}



.small{

    color:#8b949e;

    font-size:14px;

}



.section-title{

    color:#ffd700;

    font-size:24px;

    font-weight:bold;

    margin-top:25px;

    margin-bottom:15px;

    border-bottom:2px solid #ffd700;

    padding-bottom:10px;

}



.signal-box{

    padding:30px;

    border-radius:20px;

    text-align:center;

    font-size:30px;

    font-weight:900;

    margin:20px 0;

    background:#0d1117;

}



.warning-box{

    background:#2d1b1b;

    padding:15px;

    border-radius:10px;

    border-left:5px solid red;

    margin-bottom:10px;

}



</style>

""", unsafe_allow_html=True)



# =========================================

# LEAGUES

# =========================================



LEAGUE_MAP = {

    "ENGLAND": {

        "Premier League": "E0",

        "Championship": "E1"

    },

    "SPAIN": {

        "La Liga": "SP1"

    },

    "ITALY": {

        "Serie A": "I1"

    },

    "GERMANY": {

        "Bundesliga": "D1"

    },

    "FRANCE": {

        "Ligue 1": "F1"

    }

}



# =========================================

# LOAD DATA

# =========================================



@st.cache_data(ttl=3600)

def load_league_data(code):



    for season in ["2526", "2425"]:



        try:



            url = f"https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"



            r = requests.get(url, timeout=10)



            if r.status_code == 200:



                return pd.read_csv(StringIO(r.text))



        except:

            continue



    return None



# =========================================

# RAPID API TEST

# =========================================



def test_api():



    try:



        url = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-matches-by-league"



        r = requests.get(

            url,

            headers=HEADERS,

            timeout=10

        )



        return r.status_code == 200



    except:



        return False



# =========================================

# SEARCH PLAYERS

# =========================================



def search_players(team):



    try:



        url = "https://free-api-live-football-data.p.rapidapi.com/football-players-search"



        querystring = {

            "search": team

        }



        r = requests.get(

            url,

            headers=HEADERS,

            params=querystring,

            timeout=10

        )



        data = r.json()



        if "response" in data:



            return len(data["response"])



        return 0



    except:



        return 0



# =========================================

# HEADER

# =========================================



st.markdown(

    "<h1 style='text-align:center;color:#ffd700;'>BIST WAPAMBANAJI AI</h1>",

    unsafe_allow_html=True

)



st.markdown(

    "<p style='text-align:center;color:#8b949e;'>ELITE FOOTBALL AI ENGINE v8.0 PRO</p>",

    unsafe_allow_html=True

)



# =========================================

# API STATUS

# =========================================



if test_api():



    st.success("✅ RAPID API CONNECTED")



else:



    st.error("❌ RAPID API FAILED")



# =========================================

# DAILY RISK LIMIT

# =========================================



st.sidebar.markdown("## 💰 BANKROLL PROTECTOR")



daily_loss = st.sidebar.slider(

    "Daily Risk Limit (TSh)",

    10000,

    500000,

    50000,

    step=5000

)



today_loss = st.sidebar.number_input(

    "Today's Current Loss",

    min_value=0,

    value=0,

    step=5000

)



if today_loss >= daily_loss:



    st.error("⛔ MASTER, KAA MBALI NA SIMU! PUMZIKA LEO.")

    st.stop()



# =========================================

# SELECTORS

# =========================================



c1, c2 = st.columns(2)



with c1:



    nation = st.selectbox(

        "🌍 CHAGUA NCHI",

        list(LEAGUE_MAP.keys())

    )



with c2:



    league_name = st.selectbox(

        "🏆 CHAGUA LIGI",

        list(LEAGUE_MAP[nation].keys())

    )



code = LEAGUE_MAP[nation][league_name]



df = load_league_data(code)



# =========================================

# MAIN

# =========================================



if df is not None:



    teams = sorted(df["HomeTeam"].dropna().unique())



    s1, s2, s3 = st.columns([2,2,1])



    with s1:



        home = st.selectbox(

            "🏠 HOME TEAM",

            teams

        )



    with s2:



        away = st.selectbox(

            "🚀 AWAY TEAM",

            [x for x in teams if x != home]

        )



    with s3:



        market_odds = st.number_input(

            "💰 O2.5 ODDS",

            min_value=1.10,

            value=1.85,

            step=0.01

        )



    # =========================================

    # RUN ANALYSIS

    # =========================================



    if st.button("🎯 RUN AI ANALYSIS"):



        h_data = df[df["HomeTeam"] == home].tail(8)

        a_data = df[df["AwayTeam"] == away].tail(8)



        if len(h_data) < 5 or len(a_data) < 5:



            st.error("⚠️ Data haitoshi.")



            st.stop()



        # =========================================

        # WEIGHTS

        # =========================================



        w = np.arange(1, len(h_data)+1)



        # =========================================

        # ATTACK / DEFENCE

        # =========================================



        h_sc = np.average(h_data["FTHG"], weights=w)

        h_con = np.average(h_data["FTAG"], weights=w)



        a_sc = np.average(a_data["FTAG"], weights=w)

        a_con = np.average(a_data["FTHG"], weights=w)



        # =========================================

        # HOME ADVANTAGE

        # =========================================



        home_adv = 1.10 if nation in ["ENGLAND","GERMANY"] else 1.05



        h_sc *= home_adv



        # =========================================

        # EXPECTED GOALS

        # =========================================



        home_xg = (h_sc + a_con) / 2

        away_xg = (a_sc + h_con) / 2



        total_xg = home_xg + away_xg



        # =========================================

        # POISSON

        # =========================================



        def poisson(lam, k):



            return ((lam ** k) * exp(-lam)) / factorial(k)



        prob_u25 = sum(

            poisson(home_xg, i) *

            poisson(away_xg, j)

            for i in range(3)

            for j in range(3)

            if i + j < 3

        )



        prob_o25 = 1 - prob_u25



        prob_btts = (

            (1 - poisson(home_xg, 0)) *

            (1 - poisson(away_xg, 0))

        )



        # =========================================

        # REVENGE FILTER

        # =========================================



        revenge = False



        if h_data["FTAG"].iloc[-1] >= 3:



            prob_o25 -= 0.05

            revenge = True



        if a_data["FTHG"].iloc[-1] >= 3:



            prob_o25 -= 0.05

            revenge = True



        # =========================================

        # CLEAN SHEET FILTER

        # =========================================



        if (h_data["FTAG"] == 0).mean() > 0.45:



            prob_btts -= 0.08



        if (a_data["FTHG"] == 0).mean() > 0.45:



            prob_btts -= 0.08



        # =========================================

        # VOLATILITY

        # =========================================



        home_vol = np.std(h_data["FTHG"])

        away_vol = np.std(a_data["FTAG"])



        volatility = (home_vol + away_vol) / 2



        # =========================================

        # MOMENTUM ENGINE

        # =========================================



        def get_points(row, home_side=True):



            if home_side:



                if row["FTR"] == "H":

                    return 3



                elif row["FTR"] == "D":

                    return 1



                return 0



            else:



                if row["FTR"] == "A":

                    return 3



                elif row["FTR"] == "D":

                    return 1



                return 0



        home_points = sum(

            get_points(r, True)

            for _, r in h_data.tail(5).iterrows()

        )



        away_points = sum(

            get_points(r, False)

            for _, r in a_data.tail(5).iterrows()

        )



        momentum_diff = home_points - away_points



        if momentum_diff >= 6:



            prob_o25 += 0.03



        elif momentum_diff <= -6:



            prob_o25 -= 0.03



        # =========================================

        # INTENSITY

        # =========================================



        intensity = (

            h_data["HS"].mean()

            +

            a_data["AS"].mean()

        )



        if intensity > 25:



            prob_o25 += 0.04



        elif intensity < 18:



            prob_o25 -= 0.04



        # =========================================

        # RAPID API PLAYER CHECK

        # =========================================



        home_players = search_players(home)

        away_players = search_players(away)



        total_players_found = (

            home_players + away_players

        )



        if total_players_found < 5:



            prob_o25 -= 0.04

            prob_btts -= 0.03



        # =========================================

        # LIMITS

        # =========================================



        prob_o25 = min(max(prob_o25, 0.05), 0.95)



        prob_btts = min(max(prob_btts, 0.05), 0.95)



        # =========================================

        # SCORE ENGINE

        # =========================================



        score = 0



        if prob_o25 > 0.72:

            score += 2



        if prob_btts > 0.65:

            score += 1



        if total_xg > 3.1:

            score += 2



        if intensity > 22:

            score += 1



        if volatility < 1.5:

            score += 1



        if momentum_diff >= 5:

            score += 1



        # =========================================

        # QUALITY

        # =========================================



        quality = round(

            (

                prob_o25 * 45 +

                prob_btts * 25 +

                min(total_xg / 4, 1) * 20 +

                min(intensity / 30, 1) * 10

            ),

            1

        )



        # =========================================

        # RED FLAGS

        # =========================================



        red_flag = False



        if volatility > 1.8:



            red_flag = True

            quality -= 10



        if total_xg < 2.2:



            red_flag = True

            quality -= 10



        if prob_btts < 0.45 and prob_o25 > 0.75:



            red_flag = True

            quality -= 10



        quality = max(quality, 0)



        # =========================================

        # DISPLAY

        # =========================================



        st.markdown(

            "<div class='section-title'>📊 MATCH ANALYSIS</div>",

            unsafe_allow_html=True

        )



        r1, r2, r3, r4 = st.columns(4)



        with r1:



            st.markdown(

                f"""

                <div class='card'>

                <p class='small'>OVER 2.5</p>

                <div class='big-val'>{prob_o25*100:.1f}%</div>

                </div>

                """,

                unsafe_allow_html=True

            )



        with r2:



            st.markdown(

                f"""

                <div class='card'>

                <p class='small'>BTTS</p>

                <div class='big-val'>{prob_btts*100:.1f}%</div>

                </div>

                """,

                unsafe_allow_html=True

            )



        with r3:



            st.markdown(

                f"""

                <div class='card'>

                <p class='small'>VOLATILITY</p>

                <div class='big-val'>{volatility:.2f}</div>

                </div>

                """,

                unsafe_allow_html=True

            )



        with r4:



            st.markdown(

                f"""

                <div class='card'>

                <p class='small'>MOMENTUM</p>

                <div class='big-val'>{momentum_diff}</div>

                </div>

                """,

                unsafe_allow_html=True

            )



        # =========================================

        # WARNINGS

        # =========================================



        if revenge:



            st.warning(

                "⚠️ REVENGE FILTER ACTIVE"

            )



        if volatility > 1.8:



            st.warning(

                "⚠️ INCONSISTENT TEAM"

            )



        if total_players_found < 5:



            st.warning(

                "⚠️ LOW PLAYER DATA FROM API"

            )



        if red_flag:



            st.error(

                "⛔ RED FLAG DETECTED"

            )



        # =========================================

        # FINAL VERDICT

        # =========================================



        st.markdown(

            "<div class='section-title'>🧠 FINAL AI VERDICT</div>",

            unsafe_allow_html=True

        )



        if score >= 7 and quality >= 75:



            color = "#00ff66"

            verdict = "🔥 GREEN ELITE"



        elif score >= 5:



            color = "#ffd700"

            verdict = "⚖️ YELLOW RISK"



        else:



            color = "#ff4d4d"

            verdict = "⛔ RED AVOID"



        st.markdown(

            f"""

            <div class='signal-box'

            style='border:3px solid {color};

            color:{color};'>



            {verdict}



            <br><br>



            ⭐ QUALITY: {quality}/100



            <br>



            📈 SCORE: {score}/8



            </div>

            """,

            unsafe_allow_html=True

        )



        # =========================================

        # FINAL BET ENGINE

        # =========================================



        edge = round(

            (

                prob_o25 -

                (1 / market_odds)

            ) * 100,

            1

        )



        if score >= 7 and edge > 5:



            final_bet = "🔥 FINAL AI BET: OVER 2.5"



        elif prob_btts >= 0.62 and intensity >= 20:



            final_bet = "⚽ FINAL AI BET: BTTS YES"



        elif total_xg < 2.3:



            final_bet = "🛡️ FINAL AI BET: UNDER 3.5"



        else:



            final_bet = "⛔ FINAL AI BET: SKIP MATCH"



        st.success(final_bet)



        # =========================================

        # BANKROLL

        # =========================================



        kelly = (

            (

                (prob_o25 * market_odds) - 1

            ) / (market_odds - 1)

        )



        safe_k = min(

            max(0, kelly * 100 / 5),

            10

        )



        # =========================================

        # EXTRA INFO

        # =========================================



        st.info(

            f"""

📈 EDGE: {edge}%



⚽ TOTAL xG: {total_xg:.2f}



🔥 INTENSITY: {intensity:.1f}



👥 API PLAYERS FOUND: {total_players_found}

"""

        )



        st.warning(

            f"💰 RECOMMENDED STAKE: {safe_k:.1f}%"

        )



        # =========================================

        # H2H

        # =========================================



        st.markdown(

            "<div class='section-title'>📜 H2H HISTORY</div>",

            unsafe_allow_html=True

        )



        h2h = df[

            (

                (df["HomeTeam"] == home)

                &

                (df["AwayTeam"] == away)

            )

            |

            (

                (df["HomeTeam"] == away)

                &

                (df["AwayTeam"] == home)

            )

        ].tail(5)



        if not h2h.empty:



            for _, r in h2h.iterrows():



                st.write(

                    f"{r['HomeTeam']} {r['FTHG']} - {r['FTAG']} {r['AwayTeam']}"

                )



        else:



            st.write("No H2H records found.")



else:



    st.error("❌ FAILED TO LOAD FOOTBALL DATA")
