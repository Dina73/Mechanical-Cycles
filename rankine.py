import streamlit as st
from iapws import IAPWS97
import pandas as pd

st.set_page_config(page_title="Rankine Cycle Solver", layout="wide")
st.title("🔁 Rankine Cycle Solver (Ideal & Actual)")

# --- Sidebar Inputs ---
st.sidebar.header("Inputs")
P1 = st.sidebar.number_input("Boiler Pressure (MPa)", 8.0, step=0.1)
T1_C = st.sidebar.number_input("Turbine Inlet Temp (°C)", 480.0, step=1.0)
P2 = st.sidebar.number_input("Condenser Pressure (MPa)", 0.008, step=0.001, format="%.4f")
eta_t = st.sidebar.slider("Turbine η (0-1)", 0.0, 1.0, 1.0)
eta_p = st.sidebar.slider("Pump η (0-1)", 0.0, 1.0, 1.0)
net_power = st.sidebar.number_input("Net Power Output (MW)", 0.0, step=1.0)

# --- State 1: Turbine Inlet ---
st1 = IAPWS97(P=P1, T=T1_C + 273.15)
h1, s1 = st1.h, st1.s

# --- State 2: Turbine Outlet ---
h2s = IAPWS97(P=P2, s=s1).h
h2 = h1 - eta_t * (h1 - h2s)
st2 = IAPWS97(P=P2, h=h2)

# --- State 3: Pump Inlet ---
st3 = IAPWS97(P=P2, x=0)
h3, v3 = st3.h, st3.v

# --- State 4: Pump Outlet ---
h4s = h3 + v3 * (P1 - P2) * 1000  # MPa to kPa → kJ/kg
h4 = h3 + (h4s - h3) / eta_p
st4 = IAPWS97(P=P1, h=h4)

# --- Energetics ---
wt = h1 - h2
wp = h4 - h3
wnet = wt - wp
qin = h1 - h4
eff = wnet / qin * 100
m_dot = (net_power * 1e3 / wnet) if net_power > 0 else None

# --- Results Table ---
df = pd.DataFrame({
    "State": [1, 2, 3, 4],
    "P (MPa)": [P1, P2, P2, P1],
    "T (°C)": [st1.T-273.15, st2.T-273.15, st3.T-273.15, st4.T-273.15],
    "h (kJ/kg)": [h1, h2, h3, h4],
    "s (kJ/kg.K)": [s1, st2.s, st3.s, st4.s]
})
st.dataframe(df.set_index("State").round(3))

# --- Performance ---
st.subheader("Performance")
st.write(f"Thermal Efficiency: **{eff:.2f}%**")
st.write(f"Net Specific Work: **{wnet:.2f} kJ/kg**")
if m_dot:
    st.write(f"Mass Flow Rate: **{m_dot:.2f} kg/s**")
