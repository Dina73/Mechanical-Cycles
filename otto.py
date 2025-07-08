import streamlit as st

def main():
    st.set_page_config(page_title="Otto Cycle Efficiency Simulator", layout="centered")
    st.title("🔧 Otto Cycle Efficiency Simulator")

    k = 1.4
    cv = 0.718  # kJ/kg.K
    cp= 1.005   # kJ/kg.K
    R= 0.2871   # kJ/kg.K

    st.sidebar.header("Input Parameters")
    compression_ratio = st.sidebar.number_input("Compression Ratio (r)", min_value=1.0, value=8.0)
    heat_added = st.sidebar.number_input("Heat Added (Qin) [kJ/kg]", min_value=0.0, value=1000.0)
    T1 = st.sidebar.number_input("Initial Temperature T1 [K]", min_value=0.0)
    P1 = st.sidebar.number_input("Initial Pressure P1 [kPa]", min_value=0.0)

    if st.button("Calculate"):
        V1=(R*T1)/P1
        V2=V1/ compression_ratio
        P2=P1/((1/ compression_ratio)**k)
        T2 = T1 * (compression_ratio ** (k - 1))
        V3=V2
        T3 = T2 +( heat_added / cv)
        P3=(R*T3)/V3
        V4=V1
        T4 = T3 / (compression_ratio ** (k - 1))
        P4=(R*T4)/V4
        heat_rejected=cv*(T4-T1)
        work_output = heat_added -heat_rejected
        efficiency = (work_output/heat_added)*100

        st.subheader("📊 Simulation Results")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("T1", f"{T1:.2f} K")
        col1.metric("P1", f"{P1:.2f} kPa")
        col2.metric("T2", f"{T2:.2f} K")
        col2.metric("P2", f"{P2:.2f} kPa")
        col3.metric("T3", f"{T3:.2f} K")
        col3.metric("P3", f"{P3:.2f} kPa")
        col4.metric("T4", f"{T4:.2f} K")
        col4.metric("P4", f"{P4:.2f} kPa")
        col1.metric("Efficiency", f"{efficiency:.4f} %")
        col2.metric("Work Output", f"{work_output:.2f} kJ/kg")
        col3.metric("Heat Rejected", f"{heat_rejected:.2f} kJ/kg")
    else:
        st.info("Enter values in the sidebar and click **Calculate** to simulate the cycle.")

# ✅ Ensure Streamlit Cloud runs the app
main()

