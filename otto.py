import streamlit as st

st.set_page_config(page_title="Otto Cycle Efficiency Simulator", layout="centered")
st.title("🔧 Otto Cycle Efficiency Simulator")

gamma = 1.4
cv = 0.718  # kJ/kg.K

st.sidebar.header("Input Parameters")
compression_ratio = st.sidebar.number_input("Compression Ratio (r)", min_value=1.0, value=8.0)
heat_added = st.sidebar.number_input("Heat Added (Qh) [kJ/kg]", min_value=0.0, value=1000.0)
T1 = st.sidebar.number_input("Initial Temperature T1 [K]", min_value=0.0, value=300.0)

if st.button("Calculate"):
    efficiency = 1 - (1 / (compression_ratio ** (gamma - 1)))
    T2 = T1 * (compression_ratio ** (gamma - 1))
    T3 = T2 + heat_added / cv
    T4 = T3 / (compression_ratio ** (gamma - 1))
    work_output = heat_added * efficiency
    heat_rejected = heat_added - work_output

    st.subheader("📊 Simulation Results")
    col1, col2 = st.columns(2)
    col1.metric("Efficiency", f"{efficiency:.4f}")
    col2.metric("Work Output", f"{work_output:.2f} kJ/kg")
    col1.metric("Heat Rejected", f"{heat_rejected:.2f} kJ/kg")
    col2.metric("T1", f"{T1:.2f} K")
    col1.metric("T2", f"{T2:.2f} K")
    col2.metric("T3", f"{T3:.2f} K")
    col1.metric("T4", f"{T4:.2f} K")
else:
    st.info("Enter values in the sidebar and click **Calculate** to simulate the cycle.")

