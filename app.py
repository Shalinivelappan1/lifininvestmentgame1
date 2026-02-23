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
# ENRICHED LEARNING INSIGHTS
# =====================================================
learning_insights = {

"Rate Hike": """
### 🔍 What Happened?
Central banks raised policy rates → discount rates increase → equity valuations compress.

### 📊 Asset Reaction Logic
• Growth equities suffer  
• Bonds stabilise after initial shock  
• Gold benefits from uncertainty  

### 🎓 Strategic Reflection
Did you reduce risk exposure?  
Did you overweight equities despite tightening?
""",

"Growth Rally": """
### 🔍 What Happened?
Technology optimism and growth expansion increased risk appetite.

### 📊 Asset Reaction Logic
• Equities and crypto rally  
• Bonds underperform  
• Cash becomes drag  

### 🎓 Strategic Reflection
Did you capture upside?  
Or stay too defensive?
""",

"Crisis": """
### 🔍 What Happened?
Geopolitical stress triggered risk-off behaviour.

### 📊 Asset Reaction Logic
• Gold and bonds outperform  
• Equities fall  
• Diversification matters most  

### 🎓 Strategic Reflection
Did you hedge downside?  
Or panic?
""",

"Disinflation": """
### 🔍 What Happened?
Falling inflation reduces uncertainty.

### 📊 Asset Reaction Logic
• Bonds rally  
• Equities recover  
• Balanced allocation benefits  

### 🎓 Strategic Reflection
Did you increase risk at the right time?
""",

"Recession": """
### 🔍 What Happened?
Recession fears drove defensive capital rotation.

### 📊 Asset Reaction Logic
• Bonds + gold protect  
• High-beta assets fall  

### 🎓 Strategic Reflection
Was your portfolio concentrated?
""",

"Liquidity": """
### 🔍 What Happened?
Liquidity injection boosted asset prices broadly.

### 📊 Asset Reaction Logic
• Equities surge  
• Crypto rallies  
• Cash underperforms  

### 🎓 Strategic Reflection
Did you position for expansion?
""",

"Inflation": """
### 🔍 What Happened?
Inflation shock hurt duration assets.

### 📊 Asset Reaction Logic
• Gold hedges inflation  
• Bonds fall  
• Equities pressured  

### 🎓 Strategic Reflection
Did you hedge inflation risk?
""",

"Credit": """
### 🔍 What Happened?
Credit tightening increased financial stress.

### 📊 Asset Reaction Logic
• Defensive assets outperform  
• Risk appetite falls  

### 🎓 Strategic Reflection
Did you rotate defensively?
""",

"Mixed": """
### 🔍 What Happened?
Conflicting signals created uncertainty.

### 📊 Asset Reaction Logic
• Balanced allocation reduces regret  
• Overconfidence hurts  

### 🎓 Strategic Reflection
Did you stay disciplined?
"""
}

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

    sharpe = returns.mean()/(returns.std()+1e-9)*np.sqrt(10)
    bench_sharpe = bench_returns.mean()/(bench_returns.std()+1e-9)*np.sqrt(10)
    smart_sharpe = smart_returns.mean()/(smart_returns.std()+1e-9)*np.sqrt(10)

    st.subheader("Performance Comparison")
    st.metric("Your Sharpe", round(sharpe,3))
    st.metric("Benchmark Sharpe", round(bench_sharpe,3))
    st.metric("Smart Model Sharpe", round(smart_sharpe,3))

    compare = pd.DataFrame({
        "Student": hist["Value"],
        "Benchmark": bench_hist["Value"],
        "Smart": smart_hist["Value"]
    })
    st.line_chart(compare)

    st.subheader("🎓 Final Strategic Reflection")
    st.write("""
• Did you adapt across regimes?  
• Did you chase recent winners?  
• Did diversification protect you?  
• Did the smart model outperform you? Why?  
• Were your decisions emotional or systematic?
""")

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

        pv = st.session_state.portfolio_value
        new_val = sum(pv*(alloc[a]/100)*(1+returns[a]) for a in returns)

        bpv = st.session_state.bench_value
        bench_new = sum(bpv*(0.2)*(1+returns[a]) for a in returns)

        spv = st.session_state.smart_value
        smart_new = sum(spv*(0.2)*(1+returns[a]) for a in returns)

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

    st.markdown("### 🧠 What Just Happened in Markets?")
    st.info(learning_insights.get(regime,""))

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
