import streamlit as st
import pandas as pd
import numpy as np
import random

st.set_page_config(page_title="MBA Portfolio War-Room", layout="wide")

# =====================================================
# RESET FUNCTION
# =====================================================
def reset_state():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

# =====================================================
# INITIAL STATE
# =====================================================
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

# =====================================================
# START SCREEN
# =====================================================
st.title("🎓 MBA Portfolio War-Room Simulation")

if not st.session_state.initialized:
    capital = st.number_input("Initial Capital (₹)", value=1000000, step=100000)
    if st.button("Start Simulation"):
        st.session_state.portfolio_value = capital
        st.session_state.initialized = True
        st.rerun()
    st.stop()

# =====================================================
# HEADER METRICS
# =====================================================
col1, col2 = st.columns(2)
col1.metric("Portfolio Value", f"₹{int(st.session_state.portfolio_value):,}")
col2.metric("Round", st.session_state.round)

if st.button("🔄 Reset Simulation"):
    reset_state()
    st.rerun()

rd = st.session_state.round

# =====================================================
# FINAL DASHBOARD
# =====================================================
if rd > 10:

    st.header("🏁 Final Performance Dashboard")

    hist = pd.DataFrame(st.session_state.history)
    alloc_df = pd.DataFrame(st.session_state.alloc_history)

    returns = hist["Value"].pct_change().dropna()

    # Sharpe
    sharpe = returns.mean() / (returns.std() + 1e-9) * np.sqrt(10)
    st.metric("Sharpe Ratio (10 rounds)", round(sharpe, 3))

    # Volatility
    volatility = returns.std() * 100
    st.metric("Volatility (%)", round(volatility, 2))

    # Max Drawdown
    cum = hist["Value"]
    peak = cum.cummax()
    drawdown = ((cum - peak) / peak).min() * 100
    st.metric("Max Drawdown (%)", round(drawdown, 2))

    # Diversification
    div_score = 100 - alloc_df.std(axis=1).mean()
    st.metric("Diversification Score", round(div_score, 2))

    # Adaptive Behaviour
    change = alloc_df.diff().abs().sum(axis=1).mean()

    if change > 120:
        adapt = "Highly Adaptive Strategist"
    elif change > 60:
        adapt = "Moderately Adaptive"
    elif change > 25:
        adapt = "Slow Adapter"
    else:
        adapt = "Static Allocator"

    st.subheader("Adaptive Behaviour Profile")
    st.write(adapt)

    # Behaviour Type
    avg_equity = alloc_df["Indian Equity"].mean()

    if avg_equity > 70:
        behaviour = "Momentum Chaser (High Equity Bias)"
    elif avg_equity < 20:
        behaviour = "Fearful / Defensive Allocator"
    else:
        behaviour = "Balanced Strategic Allocator"

    st.subheader("Behavioural Classification")
    st.write(behaviour)

    # Regime Performance Table
    st.subheader("Regime Performance Table")

    regime_df = pd.DataFrame({
        "Round": range(1, len(st.session_state.regime_labels)+1),
        "Regime": st.session_state.regime_labels,
        "Portfolio Value": hist["Value"]
    })

    st.dataframe(regime_df)

    # Allocation Heatmap
    st.subheader("Allocation Heatmap (Strategy Persistence)")
    st.dataframe(alloc_df)

    # Learning Reflection
    st.subheader("Strategic Reflection")
    st.write("""
    • Did you increase risk after positive shocks?  
    • Did you reduce exposure after crises?  
    • Did diversification reduce drawdowns?  
    • Did you adapt to regime changes or remain static?  
    • Was your Sharpe driven by skill or luck?  
    """)

    # Dataset export
    dataset = pd.concat([hist, alloc_df], axis=1)
    dataset["Regime"] = st.session_state.regime_labels
    dataset["Sharpe"] = sharpe
    dataset["Volatility"] = volatility

    csv = dataset.to_csv(index=False).encode()
    st.download_button("Download Teaching Dataset", csv, "mba_simulation_dataset.csv")

    st.stop()

# =====================================================
# CORE ROUNDS (1–5)
# =====================================================
fixed_rounds = {
1: ("Rate Tightening Regime",
    "RBI raises rates aggressively.",
    {"Indian Equity":-0.07,"US Equity":-0.03,"Bonds":0.02,"Gold":0.04,"Crypto":-0.12,"Cash":0.01},
    "Higher discount rates reduce equity valuations. Defensive assets outperform."),

2: ("Growth Rally",
    "AI technology boom fuels markets.",
    {"Indian Equity":0.06,"US Equity":0.09,"Bonds":-0.02,"Gold":-0.03,"Crypto":0.15,"Cash":0.01},
    "Innovation cycles reward growth and speculative assets."),

3: ("Crisis Regime",
    "Geopolitical conflict escalates.",
    {"Indian Equity":-0.10,"US Equity":-0.08,"Bonds":0.05,"Gold":0.08,"Crypto":-0.05,"Cash":0.01},
    "Flight-to-safety dynamics dominate."),

4: ("Disinflation Recovery",
    "Inflation cools faster than expected.",
    {"Indian Equity":0.08,"US Equity":0.06,"Bonds":0.07,"Gold":-0.04,"Crypto":0.05,"Cash":0.01},
    "Falling inflation boosts both equities and bonds."),

5: ("Recession Fear",
    "Global recession fears intensify.",
    {"Indian Equity":-0.12,"US Equity":-0.15,"Bonds":0.06,"Gold":0.07,"Crypto":-0.20,"Cash":0.01},
    "Diversification protects portfolios during downturns.")
}

# =====================================================
# RANDOM SCENARIO POOL
# =====================================================
scenario_pool = [
("Liquidity Regime","Massive liquidity injection",
 {"Indian Equity":0.11,"US Equity":0.13,"Bonds":0.03,"Gold":-0.02,"Crypto":0.20,"Cash":0.01},
 "Liquidity amplifies asset price inflation."),

("Inflation Shock","Oil price spike resurfaces",
 {"Indian Equity":-0.06,"US Equity":-0.05,"Bonds":-0.03,"Gold":0.07,"Crypto":-0.04,"Cash":0.01},
 "Inflation shocks hurt duration assets."),

("Credit Stress","Global banking stress",
 {"Indian Equity":-0.09,"US Equity":-0.08,"Bonds":0.05,"Gold":0.07,"Crypto":-0.10,"Cash":0.01},
 "Credit tightening increases volatility."),

("Mixed Signals","Rate hike but strong earnings",
 {"Indian Equity":0.02,"US Equity":0.05,"Bonds":-0.02,"Gold":0.01,"Crypto":0.06,"Cash":0.01},
 "Conflicting macro signals test allocation discipline.")
]

# Safe structured sampling
if rd > 5 and not st.session_state.scenario_sequence:

    if len(scenario_pool) >= 5:
        seq = random.sample(scenario_pool, 5)
    else:
        seq = random.choices(scenario_pool, k=5)

    random.shuffle(seq)
    st.session_state.scenario_sequence = seq

# =====================================================
# SELECT ROUND DATA
# =====================================================
if rd <= 5:
    regime, news, returns, concept = fixed_rounds[rd]
else:
    regime, news, returns, concept = st.session_state.scenario_sequence[rd-6]

# prevent duplicate regime labels
if len(st.session_state.regime_labels) < rd:
    st.session_state.regime_labels.append(regime)

# =====================================================
# ROUND UI
# =====================================================
st.header(f"Round {rd}")
st.info(news)

prediction = st.radio("Which asset will perform BEST?", list(returns.keys()), key=f"pred{rd}")

alloc = {}
cols = st.columns(3)

for i, asset in enumerate(returns.keys()):
    alloc[asset] = cols[i%3].slider(asset, 0, 100, 0, key=f"{asset}{rd}")

total = sum(alloc.values())
st.write("Total Allocation:", total)

if total == 100 and not st.session_state.submitted:
    if st.button("Submit Allocation"):

        pv = st.session_state.portfolio_value
        new_val = 0

        for asset in returns:
            invest = pv*(alloc[asset]/100)
            new_val += invest*(1+returns[asset])

        best = max(returns, key=returns.get)
        st.session_state.predictions.append(prediction==best)
        st.session_state.history.append({"Round":rd,"Value":new_val})
        st.session_state.alloc_history.append(alloc)

        st.session_state.portfolio_value = new_val
        st.session_state.submitted = True
        st.rerun()

if st.session_state.submitted:
    st.success("Returns Revealed")
    st.write(pd.DataFrame({"Asset":list(returns.keys()),
                           "Return %":[returns[a]*100 for a in returns]}))
    st.info(concept)

    if st.button("Next Round"):
        st.session_state.round += 1
        st.session_state.submitted = False
        st.rerun()
