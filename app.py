import streamlit as st
import pandas as pd
import numpy as np
import random

st.set_page_config(page_title="MBA Portfolio War-Room", layout="wide")

# =====================================================
# SAFE SESSION INIT
# =====================================================
defaults = {
    "initialized": False,
    "round": 1,
    "portfolio_value": 0,
    "bench_value": 0,
    "smart_value": 0,
    "history": [],
    "bench_history": [],
    "smart_history": [],
    "alloc_history": [],
    "regime_labels": [],
    "scenario_sequence": [],
    "submitted": False
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =====================================================
# RESET
# =====================================================
def reset_all():
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
        st.session_state.bench_value = capital
        st.session_state.smart_value = capital
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
    reset_all()

rd = st.session_state.round

# =====================================================
# FINAL DASHBOARD
# =====================================================
if rd > 10:

    st.header("🏁 Final Performance Dashboard")

    hist = pd.DataFrame(st.session_state.history)
    bench_hist = pd.DataFrame(st.session_state.bench_history)
    smart_hist = pd.DataFrame(st.session_state.smart_history)
    alloc_df = pd.DataFrame(st.session_state.alloc_history)

    returns = hist["Value"].pct_change().dropna()
    bench_returns = bench_hist["Value"].pct_change().dropna()
    smart_returns = smart_hist["Value"].pct_change().dropna()

    # ---------- STUDENT ----------
    sharpe = returns.mean()/(returns.std()+1e-9)*np.sqrt(10)
    vol = returns.std()*100
    cum = hist["Value"]
    peak = cum.cummax()
    drawdown = ((cum-peak)/peak).min()*100
    div = 100 - alloc_df.std(axis=1).mean()

    st.subheader("Your Strategy")
    st.metric("Final", f"₹{int(st.session_state.portfolio_value):,}")
    st.metric("Sharpe", round(sharpe,3))
    st.metric("Volatility %", round(vol,2))
    st.metric("Max Drawdown %", round(drawdown,2))
    st.metric("Diversification", round(div,2))

    # ---------- BENCHMARK ----------
    bench_sharpe = bench_returns.mean()/(bench_returns.std()+1e-9)*np.sqrt(10)
    st.subheader("Benchmark Model")
    st.metric("Final", f"₹{int(st.session_state.bench_value):,}")
    st.metric("Sharpe", round(bench_sharpe,3))

    # ---------- SMART ----------
    smart_sharpe = smart_returns.mean()/(smart_returns.std()+1e-9)*np.sqrt(10)
    st.subheader("Smart Macro Model")
    st.metric("Final", f"₹{int(st.session_state.smart_value):,}")
    st.metric("Sharpe", round(smart_sharpe,3))

    # ---------- CHART ----------
    compare = pd.DataFrame({
        "Student": hist["Value"],
        "Benchmark": bench_hist["Value"],
        "Smart": smart_hist["Value"]
    })
    st.line_chart(compare)

    # ---------- ADAPTIVE ----------
    change = alloc_df.diff().abs().sum(axis=1).mean()
    if change > 120:
        adapt = "Highly Adaptive"
    elif change > 60:
        adapt = "Moderately Adaptive"
    else:
        adapt = "Static"

    st.subheader("Adaptive Behaviour")
    st.write(adapt)

    # ---------- HEATMAP ----------
    st.subheader("Allocation Heatmap")
    st.dataframe(alloc_df)

    # ---------- DATASET ----------
    dataset = pd.concat([hist,alloc_df],axis=1)
    dataset["Regime"] = st.session_state.regime_labels
    csv = dataset.to_csv(index=False).encode()
    st.download_button("Download Dataset", csv, "simulation_data.csv")

    st.stop()

# =====================================================
# FIXED ROUNDS
# =====================================================
fixed_rounds = {
1:("Rate Hike","RBI hikes rates",
   {"Indian Equity":-0.07,"US Equity":-0.03,"Bonds":0.02,"Gold":0.04,"Crypto":-0.12,"Cash":0.01}),
2:("Growth Rally","AI boom",
   {"Indian Equity":0.06,"US Equity":0.09,"Bonds":-0.02,"Gold":-0.03,"Crypto":0.15,"Cash":0.01}),
3:("Crisis","Geopolitical crisis",
   {"Indian Equity":-0.10,"US Equity":-0.08,"Bonds":0.05,"Gold":0.08,"Crypto":-0.05,"Cash":0.01}),
4:("Disinflation","Inflation cools",
   {"Indian Equity":0.08,"US Equity":0.06,"Bonds":0.07,"Gold":-0.04,"Crypto":0.05,"Cash":0.01}),
5:("Recession","Recession fear",
   {"Indian Equity":-0.12,"US Equity":-0.15,"Bonds":0.06,"Gold":0.07,"Crypto":-0.20,"Cash":0.01})
}

scenario_pool = [
("Liquidity","Liquidity injection",
 {"Indian Equity":0.11,"US Equity":0.13,"Bonds":0.03,"Gold":-0.02,"Crypto":0.20,"Cash":0.01}),
("Inflation","Oil spike",
 {"Indian Equity":-0.06,"US Equity":-0.05,"Bonds":-0.03,"Gold":0.07,"Crypto":-0.04,"Cash":0.01}),
("Credit","Bank stress",
 {"Indian Equity":-0.09,"US Equity":-0.08,"Bonds":0.05,"Gold":0.07,"Crypto":-0.10,"Cash":0.01}),
("Mixed","Rate hike + earnings",
 {"Indian Equity":0.02,"US Equity":0.05,"Bonds":-0.02,"Gold":0.01,"Crypto":0.06,"Cash":0.01})
]

if rd > 5 and not st.session_state.scenario_sequence:
    seq = random.choices(scenario_pool, k=5)
    random.shuffle(seq)
    st.session_state.scenario_sequence = seq

if rd <= 5:
    regime,news,returns = fixed_rounds[rd]
else:
    regime,news,returns = st.session_state.scenario_sequence[rd-6]

if len(st.session_state.regime_labels) < rd:
    st.session_state.regime_labels.append(regime)

# =====================================================
# MODEL LOGIC
# =====================================================
benchmark_alloc = {
    "Indian Equity":30,"US Equity":20,"Bonds":25,"Gold":15,"Crypto":5,"Cash":5
}

smart_allocations = {
"Rate Hike":{"Indian Equity":20,"US Equity":10,"Bonds":35,"Gold":25,"Crypto":5,"Cash":5},
"Growth Rally":{"Indian Equity":40,"US Equity":30,"Bonds":10,"Gold":5,"Crypto":10,"Cash":5},
"Crisis":{"Indian Equity":15,"US Equity":10,"Bonds":35,"Gold":30,"Crypto":5,"Cash":5},
"Disinflation":{"Indian Equity":35,"US Equity":25,"Bonds":25,"Gold":5,"Crypto":5,"Cash":5},
"Recession":{"Indian Equity":20,"US Equity":15,"Bonds":35,"Gold":20,"Crypto":5,"Cash":5},
"Liquidity":{"Indian Equity":45,"US Equity":35,"Bonds":5,"Gold":5,"Crypto":5,"Cash":5},
"Inflation":{"Indian Equity":25,"US Equity":15,"Bonds":10,"Gold":40,"Crypto":5,"Cash":5},
"Credit":{"Indian Equity":20,"US Equity":15,"Bonds":35,"Gold":20,"Crypto":5,"Cash":5},
"Mixed":{"Indian Equity":30,"US Equity":20,"Bonds":25,"Gold":15,"Crypto":5,"Cash":5}
}

# =====================================================
# ROUND UI
# =====================================================
st.header(f"Round {rd}")
st.info(news)

alloc={}
cols=st.columns(3)

for i,a in enumerate(returns.keys()):
    alloc[a]=cols[i%3].slider(a,0,100,0,key=f"{a}{rd}")

total=sum(alloc.values())
st.write("Total Allocation:", total)

if total==100 and not st.session_state.submitted:
    if st.button("Submit Allocation"):

        # STUDENT
        pv = st.session_state.portfolio_value
        new_val = sum(pv*(alloc[a]/100)*(1+returns[a]) for a in returns)

        # BENCHMARK
        bpv = st.session_state.bench_value
        bench_new = sum(bpv*(benchmark_alloc[a]/100)*(1+returns[a]) for a in returns)

        # SMART
        smart_alloc = smart_allocations.get(regime, benchmark_alloc)
        spv = st.session_state.smart_value
        smart_new = sum(spv*(smart_alloc[a]/100)*(1+returns[a]) for a in returns)

        st.session_state.portfolio_value = new_val
        st.session_state.bench_value = bench_new
        st.session_state.smart_value = smart_new

        st.session_state.history.append({"Round":rd,"Value":new_val})
        st.session_state.bench_history.append({"Round":rd,"Value":bench_new})
        st.session_state.smart_history.append({"Round":rd,"Value":smart_new})
        st.session_state.alloc_history.append(alloc)

        st.session_state.submitted=True
        st.rerun()

if st.session_state.submitted:
    st.success("Returns Revealed")
    st.write(pd.DataFrame({
        "Asset": list(returns.keys()),
        "Return %":[returns[a]*100 for a in returns]
    }))

    if st.button("Next Round"):
        st.session_state.round += 1
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
