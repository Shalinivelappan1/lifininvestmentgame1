import streamlit as st
import pandas as pd
import numpy as np
import random

st.set_page_config(page_title="Portfolio War-Room", layout="wide")

# =====================================================
# SESSION INIT
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
# REGIME AI
# =====================================================
def regime_ai_allocation(regime):

    if regime in ["Crisis", "Recession", "Credit"]:
        return {
            "Indian Equity":0.10,"US Equity":0.10,"Bonds":0.35,
            "Gold":0.30,"Crypto":0.05,"Cash":0.10
        }

    elif regime in ["Rate Hike","Inflation"]:
        return {
            "Indian Equity":0.15,"US Equity":0.15,"Bonds":0.25,
            "Gold":0.30,"Crypto":0.05,"Cash":0.10
        }

    elif regime in ["Growth Rally","Liquidity"]:
        return {
            "Indian Equity":0.30,"US Equity":0.30,"Bonds":0.10,
            "Gold":0.05,"Crypto":0.20,"Cash":0.05
        }

    else:
        return {
            "Indian Equity":0.20,"US Equity":0.20,"Bonds":0.20,
            "Gold":0.20,"Crypto":0.10,"Cash":0.10
        }

# =====================================================
# LEARNING INSIGHTS
# =====================================================
learning_insights = {

"Rate Hike": """
Central banks raised rates → equity valuations fall.  
Defensive assets and gold usually hold better.
""",

"Growth Rally": """
Risk appetite rises → equities & crypto rally.  
Cash becomes a drag.
""",

"Crisis": """
Risk-off environment.  
Gold & bonds protect capital.  
Diversification matters most.
""",

"Disinflation": """
Inflation falls → bonds rally.  
Balanced portfolios perform well.
""",

"Recession": """
Growth slows → defensive allocation helps.  
High-beta assets suffer.
""",

"Liquidity": """
Liquidity injection boosts risk assets broadly.
""",

"Inflation": """
Inflation hurts bonds and growth stocks.  
Gold becomes hedge.
""",

"Credit": """
Financial stress → rotate defensive.
""",

"Mixed": """
Conflicting signals → diversification helps.
"""
}

# =====================================================
# TITLE
# =====================================================
st.title("🎓 Portfolio War-Room Simulation")
st.caption("Designed by Prof. Shalini Velappan | IIM Tiruchirappalli")

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
# SCENARIOS
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

# =====================================================
# SUBMIT
# =====================================================
if total==100 and not st.session_state.submitted:
    if st.button("Submit Allocation"):

        pv = st.session_state.portfolio_value
        new_val = sum(pv*(alloc[a]/100)*(1+returns[a]) for a in returns)

        bpv = st.session_state.bench_value
        w = 1/len(returns)
        bench_new = sum(bpv*w*(1+returns[a]) for a in returns)

        spv = st.session_state.smart_value
        smart_alloc = regime_ai_allocation(regime)
        smart_new = sum(spv*smart_alloc[a]*(1+returns[a]) for a in returns)

        st.session_state.portfolio_value = new_val
        st.session_state.bench_value = bench_new
        st.session_state.smart_value = smart_new

        st.session_state.history.append({"Round":rd,"Value":new_val})
        st.session_state.bench_history.append({"Round":rd,"Value":bench_new})
        st.session_state.smart_history.append({"Round":rd,"Value":smart_new})
        st.session_state.alloc_history.append(alloc)

        st.session_state.submitted=True
        st.rerun()

# =====================================================
# REVEAL
# =====================================================
if st.session_state.submitted:
    st.success("Returns Revealed")

    st.write(pd.DataFrame({
        "Asset": list(returns.keys()),
        "Return %":[returns[a]*100 for a in returns]
    }))

    st.markdown("### 🧠 Market Insight")
    st.info(learning_insights.get(regime,""))

    if st.button("Next Round"):
        st.session_state.round += 1
        st.session_state.submitted=False
        st.rerun()

# =====================================================
# FINAL DASHBOARD
# =====================================================
if rd > 10:

    st.header("🏁 Final Performance Dashboard")

    hist = pd.DataFrame(st.session_state.history)
    bench_hist = pd.DataFrame(st.session_state.bench_history)
    smart_hist = pd.DataFrame(st.session_state.smart_history)

    r = hist["Value"].pct_change().dropna()
    br = bench_hist["Value"].pct_change().dropna()
    sr = smart_hist["Value"].pct_change().dropna()

    sharpe = r.mean()/(r.std()+1e-9)*np.sqrt(10)
    bsharpe = br.mean()/(br.std()+1e-9)*np.sqrt(10)
    ssharpe = sr.mean()/(sr.std()+1e-9)*np.sqrt(10)

    st.metric("Your Sharpe", round(sharpe,3))
    st.metric("Benchmark Sharpe", round(bsharpe,3))
    st.metric("Regime AI Sharpe", round(ssharpe,3))

    compare = pd.DataFrame({
        "Student": hist["Value"],
        "Benchmark": bench_hist["Value"],
        "Regime AI": smart_hist["Value"]
    })

    st.line_chart(compare)

    st.subheader("🎓 Final Reflection")
    st.write("""
- Did you adapt to regimes?  
- Did diversification help?  
- Did you chase winners?  
- Did AI outperform you? Why?  
""")

    st.stop()
