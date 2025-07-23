import streamlit as st

def main():
    st.set_page_config(page_title="Brayton Cycle Efficiency Simulator", layout="centered")
    st.title("🔧 Brayton Cycle Solver")

    k = 1.4
    cp = 1.005  # kJ/kg.K

    st.markdown("### Input Parameters")

    # Selection: Ideal or Actual
    cycle_type = st.selectbox("Cycle Type", ["Ideal", "Actual"])

    col1, col2 = st.columns(2)
    with col1:
        r_p = st.number_input("Pressure Ratio (P2/P1)", min_value=1.0)
        T1 = st.number_input("Inlet Temperature T1 [K]", min_value=0.0)
    with col2:
        T3 = st.number_input("Max Temperature T3 [K]", min_value=0.0)

        if cycle_type == "Actual":
            eta_c = st.slider("Compressor Efficiency [%]", 0.0, 100.0)
            eta_t = st.slider("Turbine Efficiency [%]", 0.0, 100.0)

    if st.button("Solve"):
        
        if cycle_type == "Ideal":
            # Efficiency (Ideal)
            T2 = T1 * r_p ** ((k - 1) / k)
            T4 = T3 * (1 / r_p) ** ((k - 1) / k)
            eff_ideal = 1 - (1 / (r_p ** ((k - 1) / k)))
            w_t = cp * (T3 - T4)
            w_c = cp * (T2 - T1)
            w_net = w_t - w_c
            q_in = cp * (T3 - T2)
            efficiency = eff_ideal * 100
            q_out = cp * (T4 - T1)

            # Results display
            st.subheader("✅ Ideal Brayton Cycle Results")
            col1, col2, col3 = st.columns(3)
            col1.metric("T2 [K]", f"{T2:.2f}")
            col2.metric("T4 [K]", f"{T4:.2f}")
            col3.metric("Efficiency [%]", f"{efficiency:.2f}")
            col1.metric("Net Work [kJ/kg]", f"{w_net:.2f}")
            col2.metric("Heat Added [kJ/kg]", f"{q_in:.2f}")
            col3.metric("Heat Rejected [kJ/kg]", f"{q_out:.2f}")

        elif cycle_type == "Actual":
            
            # ---------- Isentropic Temperatures ----------
            T2s = T1 * r_p ** ((k - 1) / k)
            T4s = T3 * (1 / r_p) ** ((k - 1) / k)
            
            # Actual Temperatures using efficiencies
            T2a = T1 + (T2s - T1) / (eta_c / 100)
            T4a = T3 - (T3 - T4s) * (eta_t / 100)

            # Actual work and heat
            w_c = cp * (T2a - T1)
            w_t = cp * (T3 - T4a)
            w_net = w_t - w_c
            q_in = cp * (T3 - T2a)
            q_out = cp * (T4a - T1)
            efficiency = (w_net / q_in) * 100 if q_in else 0

            # Results display
            st.subheader("✅ Actual Brayton Cycle Results")
            col1, col2, col3 = st.columns(3)
            col1.metric("T2a [K]", f"{T2a:.2f}")
            col2.metric("T4a [K]", f"{T4a:.2f}")
            col3.metric("Efficiency [%]", f"{efficiency:.2f}")
            col1.metric("Net Work [kJ/kg]", f"{w_net:.2f}")
            col2.metric("Heat Added [kJ/kg]", f"{q_in:.2f}")
            col3.metric("Heat Rejected [kJ/kg]", f"{q_out:.2f}")

    else:
        st.info("Select cycle type, enter inputs, then click **Solve** to simulate the cycle.")

main()

