import streamlit as st
import pandas as pd
import numpy as np
import random

st.set_page_config(page_title="MBA Portfolio War-Room", layout="wide")

# =====================================================
# SAFE SESSION INITIALIZATION (prevents cloud crashes)
# =====================================================
defaults = {
    "initialized": False,
    "round": 1,
    "portfolio_value": 0,
    "model_value": 0,
    "history": [],
    "model_history": [],
    "alloc_history": [],
    "predictions": [],
    "scenario_sequence": [],
    "regime_labels": [],
    "submitted": False
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =====================================================
# RESET
# =====================================================
def reset_state():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

# =====================================================
# TITLE
# =====================================================
st.title("🎓 MBA Portfolio War-Room Simulation")
st.caption("Designed & Developed by Prof. Shalini Velappan, IIM Tiruchirappalli")

# =====================================================
# START SCREEN
# =====================================================
if not st.session_state.initialized:
    capital = st.number_input("Initial Capital (₹)", value=1000000, step=100000)

    if st.button("Start Simulation"):
        st.session_state.portfolio_value = capital
        st.session_state.model_value = capital
        st.session_state.initialized = True
        st.rerun()

    st.stop()

# =====================================================
# HEADER
# =====================================================
display_round = min(st.session_state.round, 10)

c1,c2 = st.columns(2)
c1.metric("Portfolio Value", f"₹{int(st.session_state.portfolio_value):,}")
c2.metric("Round", display_round)

if st.button("Reset Simulation"):
    reset_state()

rd = st.session_state.round

# =====================================================
# FINAL DASHBOARD
# =====================================================
if rd > 10:

    st.header("🏁 Final Performance Dashboard")

    hist = pd.DataFrame(st.session_state.history)
    alloc_df = pd.DataFrame(st.session_state.alloc_history)
    model_hist = pd.DataFrame(st.session_state.model_history)

    returns = hist["Value"].pct_change().dropna()
    model_returns = model_hist["Value"].pct_change().dropna()

    # Student metrics
    sharpe = returns.mean()/(returns.std()+1e-9)*np.sqrt(10)
    vol = returns.std()*100
    cum = hist["Value"]
    peak = cum.cummax()
    drawdown = ((cum-peak)/peak).min()*100
    div = 100 - alloc_df.std(axis=1).mean()

    st.subheader("Your Strategy")
    st.metric("Final Portfolio", f"₹{int(st.session_state.portfolio_value):,}")
    st.metric("Sharpe", round(sharpe,3))
    st.metric("Volatility %", round(vol,2))
    st.metric("Max Drawdown %", round(drawdown,2))
    st.metric("Diversification", round(div,2))

    # Model metrics
    model_sharpe = model_returns.mean()/(model_returns.std()+1e-9)*np.sqrt(10)

    st.subheader("Model Strategy")
    st.metric("Model Final", f"₹{int(st.session_state.model_value):,}")
    st.metric("Model Sharpe", round(model_sharpe,3))

    diff = st.session_state.portfolio_value - st.session_state.model_value
    if diff > 0:
        st.success(f"You outperformed model by ₹{int(diff):,}")
    else:
        st.warning(f"You underperformed model by ₹{int(abs(diff)):,}")

    compare_df = pd.DataFrame({
        "Student": hist["Value"],
        "Model": model_hist["Value"]
    })
    st.line_chart(compare_df)

    # Behaviour
    change = alloc_df.diff().abs().sum(axis=1).mean()
    if change > 120:
        adapt = "Highly Adaptive"
    elif change > 60:
        adapt = "Moderately Adaptive"
    else:
        adapt = "Static Allocator"

    st.subheader("Adaptive Behaviour")
    st.write(adapt)

    avg_equity = alloc_df["Indian Equity"].mean()
    if avg_equity > 70:
        behaviour = "Momentum Chaser"
    elif avg_equity < 20:
        behaviour = "Defensive"
    else:
        behaviour = "Balanced"

    st.subheader("Behaviour Type")
    st.write(behaviour)

    st.subheader("Allocation Heatmap")
    st.dataframe(alloc_df)

    dataset = pd.concat([hist,alloc_df],axis=1)
    dataset["Regime"] = st.session_state.regime_labels
    dataset["Sharpe"] = sharpe
    dataset["ModelSharpe"] = model_sharpe

    csv = dataset.to_csv(index=False).encode()
    st.download_button("Download Teaching Dataset", csv, "mba_simulation_dataset.csv")

    st.stop()

# =====================================================
# FIXED ROUNDS 1–5
# =====================================================
fixed_rounds = {
1:("Rate Hike","RBI hikes rates",
   {"Indian Equity":-0.07,"US Equity":-0.03,"Bonds":0.02,"Gold":0.04,"Crypto":-0.12,"Cash":0.01},
   "Higher rates hurt equities."),
2:("Growth Rally","AI boom",
   {"Indian Equity":0.06,"US Equity":0.09,"Bonds":-0.02,"Gold":-0.03,"Crypto":0.15,"Cash":0.01},
   "Growth assets rally."),
3:("Crisis","Geopolitical crisis",
   {"Indian Equity":-0.10,"US Equity":-0.08,"Bonds":0.05,"Gold":0.08,"Crypto":-0.05,"Cash":0.01},
   "Flight to safety."),
4:("Disinflation","Inflation cools",
   {"Indian Equity":0.08,"US Equity":0.06,"Bonds":0.07,"Gold":-0.04,"Crypto":0.05,"Cash":0.01},
   "Risk-on."),
5:("Recession","Recession fear",
   {"Indian Equity":-0.12,"US Equity":-0.15,"Bonds":0.06,"Gold":0.07,"Crypto":-0.20,"Cash":0.01},
   "Diversification matters.")
}

scenario_pool = [
("Liquidity","Liquidity injection",
 {"Indian Equity":0.11,"US Equity":0.13,"Bonds":0.03,"Gold":-0.02,"Crypto":0.20,"Cash":0.01},
 "Liquidity boosts assets."),
("Inflation","Oil spike",
 {"Indian Equity":-0.06,"US Equity":-0.05,"Bonds":-0.03,"Gold":0.07,"Crypto":-0.04,"Cash":0.01},
 "Inflation shock."),
("Credit","Bank stress",
 {"Indian Equity":-0.09,"US Equity":-0.08,"Bonds":0.05,"Gold":0.07,"Crypto":-0.10,"Cash":0.01},
 "Credit tightening."),
("Mixed","Rate hike + earnings",
 {"Indian Equity":0.02,"US Equity":0.05,"Bonds":-0.02,"Gold":0.01,"Crypto":0.06,"Cash":0.01},
 "Mixed signals.")
]

# generate random
if rd > 5 and not st.session_state.scenario_sequence:
    if len(scenario_pool)>=5:
        seq=random.sample(scenario_pool,5)
    else:
        seq=random.choices(scenario_pool,k=5)
    random.shuffle(seq)
    st.session_state.scenario_sequence=seq

# select
if rd<=5:
    regime,news,returns,concept=fixed_rounds[rd]
else:
    regime,news,returns,concept=st.session_state.scenario_sequence[rd-6]

if len(st.session_state.regime_labels)<rd:
    st.session_state.regime_labels.append(regime)

# =====================================================
# ROUND UI
# =====================================================
st.header(f"Round {rd}")
st.info(news)

prediction = st.radio("Which asset performs BEST?", list(returns.keys()), key=f"p{rd}")

alloc={}
cols=st.columns(3)

for i,a in enumerate(returns.keys()):
    alloc[a]=cols[i%3].slider(a,0,100,0,key=f"{a}{rd}")

total=sum(alloc.values())
st.write("Total Allocation:",total)

if total==100 and not st.session_state.submitted:
    if st.button("Submit Allocation"):

        pv=st.session_state.portfolio_value
        new_val=0
        for a in returns:
            invest=pv*(alloc[a]/100)
            new_val+=invest*(1+returns[a])

        # model allocation (simple disciplined baseline)
        model_alloc={
            "Indian Equity":30,"US Equity":20,"Bonds":25,"Gold":15,"Crypto":5,"Cash":5
        }

        mpv=st.session_state.model_value
        model_new=0
        for a in returns:
            invest=mpv*(model_alloc[a]/100)
            model_new+=invest*(1+returns[a])

        st.session_state.model_value=model_new
        st.session_state.model_history.append({"Round":rd,"Value":model_new})

        best=max(returns,key=returns.get)
        st.session_state.predictions.append(prediction==best)
        st.session_state.history.append({"Round":rd,"Value":new_val})
        st.session_state.alloc_history.append(alloc)

        st.session_state.portfolio_value=new_val
        st.session_state.submitted=True
        st.rerun()

if st.session_state.submitted:
    st.success("Returns Revealed")
    st.write(pd.DataFrame({"Asset":list(returns.keys()),
                           "Return %":[returns[a]*100 for a in returns]}))
    st.info(concept)

    if st.button("Next Round"):
        st.session_state.round+=1
        st.session_state.submitted=False
        st.rerun()

# =====================================================
# FOOTER
# =====================================================
st.markdown("""
---
<div style='text-align:center; font-size:13px; color:gray'>
MBA Portfolio War-Room Simulation  
Designed by Prof. Shalini Velappan | IIM Tiruchirappalli  
© 2026 Academic Teaching Tool
</div>
""", unsafe_allow_html=True)
