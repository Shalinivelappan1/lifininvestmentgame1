import streamlit as st
import pandas as pd
import numpy as np
import random

st.set_page_config(page_title="MBA Portfolio War Room", layout="wide")

# ---------------- RESET ----------------
def reset_state():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

# ---------------- INIT ----------------
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.round = 1
    st.session_state.portfolio_value = 1000000
    st.session_state.history = []
    st.session_state.alloc_history = []
    st.session_state.predictions = []
    st.session_state.submitted = False
    st.session_state.scenario_sequence = []
    st.session_state.regime_labels = []

# ---------------- START SCREEN ----------------
st.title("🎓 MBA Portfolio War-Room")

if not st.session_state.initialized:
    cap = st.number_input("Initial capital", value=1000000, step=100000)
    if st.button("Start Simulation"):
        st.session_state.portfolio_value = cap
        st.session_state.initialized = True
        st.rerun()
    st.stop()

# ---------------- HEADER METRICS ----------------
c1,c2 = st.columns(2)
c1.metric("Portfolio Value", f"₹{int(st.session_state.portfolio_value):,}")
c2.metric("Round", st.session_state.round)

if st.button("Reset Simulation"):
    reset_state()
    st.rerun()

rd = st.session_state.round

# =====================================================
# FINAL DASHBOARD
# =====================================================
if rd > 10:

    st.header("🏁 Final Dashboard")

    hist = pd.DataFrame(st.session_state.history)
    alloc_df = pd.DataFrame(st.session_state.alloc_history)

    returns = hist["Value"].pct_change().dropna()

    # -------- SHARPE RATIO --------
    sharpe = returns.mean() / (returns.std()+1e-9) * np.sqrt(10)
    st.metric("Sharpe Ratio", round(sharpe,3))

    # -------- DIVERSIFICATION --------
    div_score = 100 - alloc_df.std(axis=1).mean()
    st.metric("Diversification Score", round(div_score,2))

    # -------- RISK --------
    vol = returns.std()*100
    st.metric("Volatility", round(vol,2))

    # -------- MAX DRAWDOWN --------
    cum = hist["Value"]
    peak = cum.cummax()
    draw = ((cum-peak)/peak).min()*100
    st.metric("Max Drawdown %", round(draw,2))

    # -------- ADAPTIVE SCORE --------
    change = alloc_df.diff().abs().sum(axis=1).mean()

    if change > 120:
        adapt = "Highly Adaptive"
    elif change > 60:
        adapt = "Adaptive"
    elif change > 25:
        adapt = "Slow Adapter"
    else:
        adapt = "Static"

    st.write("Adaptive Behaviour:", adapt)

    # -------- REGIME TABLE --------
    st.subheader("Regime Performance")

    regime_df = pd.DataFrame({
        "Round": range(1,len(st.session_state.regime_labels)+1),
        "Regime": st.session_state.regime_labels,
        "Portfolio Value": hist["Value"]
    })

    st.dataframe(regime_df)

    # -------- HEATMAP --------
    st.subheader("Allocation Heatmap")
    st.dataframe(alloc_df)

    # -------- DATASET EXPORT --------
    st.subheader("Download Teaching Dataset")

    dataset = pd.concat([hist,alloc_df],axis=1)
    dataset["Regime"] = st.session_state.regime_labels
    dataset["Sharpe"] = sharpe
    dataset["Volatility"] = vol

    csv = dataset.to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "teaching_dataset.csv")

    st.stop()

# =====================================================
# CORE ROUNDS 1–5
# =====================================================
fixed_rounds = {
1: ("rate_hike","RBI hikes rates aggressively",
    {"Indian Equity":-0.07,"US Equity":-0.03,"Bonds":0.02,"Gold":0.04,"Crypto":-0.12,"Cash":0.01},
    "Rate hikes hurt equity valuations."),

2: ("tech_rally","AI boom",
    {"Indian Equity":0.06,"US Equity":0.09,"Bonds":-0.02,"Gold":-0.03,"Crypto":0.15,"Cash":0.01},
    "Growth assets outperform."),

3: ("crisis","Geopolitical crisis",
    {"Indian Equity":-0.10,"US Equity":-0.08,"Bonds":0.05,"Gold":0.08,"Crypto":-0.05,"Cash":0.01},
    "Flight to safety."),

4: ("disinflation","Inflation cools",
    {"Indian Equity":0.08,"US Equity":0.06,"Bonds":0.07,"Gold":-0.04,"Crypto":0.05,"Cash":0.01},
    "Risk-on recovery."),

5: ("recession","Recession fears",
    {"Indian Equity":-0.12,"US Equity":-0.15,"Bonds":0.06,"Gold":0.07,"Crypto":-0.20,"Cash":0.01},
    "Diversification matters.")
}

# =====================================================
# RANDOM POOL
# =====================================================
scenario_pool = [
("crisis","Banking crisis",{"Indian Equity":-0.11,"US Equity":-0.13,"Bonds":0.06,"Gold":0.09,"Crypto":-0.18,"Cash":0.01},"System stress"),
("risk_on","Liquidity injection",{"Indian Equity":0.11,"US Equity":0.13,"Bonds":0.03,"Gold":-0.02,"Crypto":0.20,"Cash":0.01},"Liquidity rally"),
("inflation","Oil spike",{"Indian Equity":-0.06,"US Equity":-0.05,"Bonds":-0.03,"Gold":0.07,"Crypto":-0.04,"Cash":0.01},"Inflation shock"),
("mixed","Policy confusion",{"Indian Equity":0.01,"US Equity":0.02,"Bonds":0.00,"Gold":0.01,"Crypto":0.00,"Cash":0.01},"Mixed signals")
]

# Generate sequence
if rd > 5 and not st.session_state.scenario_sequence:
    st.session_state.scenario_sequence = random.sample(scenario_pool,5)

# Select round
if rd <= 5:
    regime,news,ret,concept = fixed_rounds[rd]
else:
    regime,news,ret,concept = st.session_state.scenario_sequence[rd-6]

st.session_state.regime_labels.append(regime)

# =====================================================
# ROUND UI
# =====================================================
st.header(f"Round {rd}")
st.info(news)

pred = st.radio("Best asset?", list(ret.keys()), key=f"p{rd}")

alloc={}
cols=st.columns(3)

for i,a in enumerate(ret.keys()):
    alloc[a]=cols[i%3].slider(a,0,100,0,key=f"{a}{rd}")

total=sum(alloc.values())
st.write("Total allocation:",total)

if total==100 and not st.session_state.submitted:
    if st.button("Submit"):

        pv=st.session_state.portfolio_value
        new_val=0

        for a in ret:
            invest=pv*(alloc[a]/100)
            new_val+=invest*(1+ret[a])

        best=max(ret,key=ret.get)
        st.session_state.predictions.append(pred==best)
        st.session_state.history.append({"Round":rd,"Value":new_val})
        st.session_state.alloc_history.append(alloc)

        st.session_state.portfolio_value=new_val
        st.session_state.submitted=True
        st.rerun()

if st.session_state.submitted:
    st.success("Returns revealed")
    st.write(pd.DataFrame({"Asset":list(ret.keys()),
                           "Return%":[ret[a]*100 for a in ret]}))
    st.info(concept)

    if st.button("Next Round"):
        st.session_state.round+=1
        st.session_state.submitted=False
        st.rerun()
