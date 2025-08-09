import streamlit as st
from iapws import IAPWS97

st.set_page_config(page_title="Rankine Cycle Solver", layout="centered")
st.title("🔧 Rankine Cycle Solver (Ideal & Actual)")

# --- Inputs ---
P1 = st.number_input("Condenser Pressure (MPa)",  min_value=0.0)
P2 = st.number_input("Boiler Pressure (MPa)",  min_value=0.0)
T3 = st.number_input("Turbine Inlet Temperature (°C)",  min_value=0.0)
eta_t = st.number_input("Turbine Isentropic Efficiency (%)", min_value=0.0, max_value=100) / 100
eta_p = st.number_input("Pump Isentropic Efficiency (%)", min_value=0.0, max_value=100) / 100
power = st.number_input("Net Power Output (MW)",  min_value=0.0)
m_dot = st.number_input("Mass Flow Rate (kg/s)",  min_value=0.0)

# --- Calculate button ---
if st.button("Solve"):
    # --- State 1: Condenser outlet (saturated liquid) ---
    st1 = IAPWS97(P=P1, x=0)
    h1, s1 = st1.h, st1.s

    # --- Pump (1→2) ---
    st2s = IAPWS97(P=P2, s=s1)
    h2s = st2s.h
    h2 = h1 + (h2s - h1) / (eta_p if eta_p else 1)
    st2 = IAPWS97(P=P2, h=h2)

    # --- State 3: Turbine inlet ---
    st3 = IAPWS97(P=P2, T=T3 + 273.15)
    h3, s3 = st3.h, st3.s

    # --- Turbine (3→4) ---
    st4s = IAPWS97(P=P1, s=s3)
    h4s = st4s.h
    h4 = h3 - eta_t * (h3 - h4s) if eta_t else h4s
    st4 = IAPWS97(P=P1, h=h4)

    # --- Work & efficiency ---
    wp = h2 - h1
    wt = h3 - h4
    wnet = wt - wp
    q_in = h3 - h2
    eff = wnet / q_in

    # --- Mass flow or power ---
    if m_dot == 0 and power > 0:
        m_dot = power * 1000 / wnet
    elif power == 0 and m_dot > 0:
        power = m_dot * wnet / 1000

    # --- Results ---
    st.subheader("Results")
    st.write(f"Thermal Efficiency: {eff*100:.2f} %")
    st.write(f"Specific Work Output: {wnet:.2f} kJ/kg")
    st.write(f"Mass Flow Rate: {m_dot:.2f} kg/s")
    st.write(f"Net Power Output: {power:.2f} MW")

    st.subheader("State Points")
    for i, (P, T, h, s) in enumerate([
        (st1.P, st1.T - 273.15, h1, s1),
        (st2.P, st2.T - 273.15, h2, st2.s),
        (st3.P, st3.T - 273.15, h3, s3),
        (st4.P, st4.T - 273.15, h4, st4.s),
    ], start=1):
        st.write(f"State {i}: P={P:.2f} MPa, T={T:.2f} °C, h={h:.2f} kJ/kg, s={s:.4f} kJ/kg.K")






