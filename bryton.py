import streamlit as st

def main():
    st.set_page_config(page_title="Brayton Cycle Efficiency Simulator", layout="centered")
    st.title("🔥 Brayton Cycle Simulator (Ideal & Actual)")

    k = 1.4
    cp = 1.005  # kJ/kg.K
    R = 0.2871  # kJ/kg.K

    st.markdown("### Input Parameters")

    col1, col2 = st.columns(2)
    with col1:
        r_p = st.number_input("Pressure Ratio (P2/P1)", min_value=1.0)
        T1 = st.number_input("Inlet Temperature T1 [K]", min_value=200.0, value=300.0)
        P1 = st.number_input("Inlet Pressure P1 [bar]", min_value=0.1, value=1.0)
    with col2:
        T3 = st.number_input("Max Temperature T3 [K]", min_value=500.0, value=1200.0)
        eta_c = st.slider("Compressor Efficiency [%]", 50.0, 100.0, 100.0)
        eta_t = st.slider("Turbine Efficiency [%]", 50.0, 100.0, 100.0)

    if st.button("Solve"):
        # ---------- Ideal Brayton Cycle ----------
        # 1 → 2s: Isentropic Compression
        T2s = T1 * r_p ** ((k - 1) / k)
        # 2 → 3: Constant Pressure Heat Addition
        # 3 → 4s: Isentropic Expansion
        T4s = T3 * (1 / r_p) ** ((k - 1) / k)

        # Efficiency (Ideal)
        eff_ideal = 1 - (1 / (r_p ** ((k - 1) / k)))
        w_t_ideal = cp * (T3 - T4s)
        w_c_ideal = cp * (T2s - T1)
        w_net_ideal = w_t_ideal - w_c_ideal
        q_in_ideal = cp * (T3 - T2s)

        # ---------- Actual Brayton Cycle ----------
        T2 = T1 + (T2s - T1) / (eta_c / 100)
        T4 = T3 - (T3 - T4s) * (eta_t / 100)

        w_c_actual = cp * (T2 - T1)
        w_t_actual = cp * (T3 - T4)
        w_net_actual = w_t_actual - w_c_actual
        q_in_actual = cp * (T3 - T2)
        q_out_actual = cp * (T4 - T1)
        eff_actual = (w_net_actual / q_in_actual) * 100 if q_in_actual else 0

        # ---------- Display Results ----------
        st.subheader("✅ Results")

        st.markdown("#### 🔹 Ideal Brayton Cycle")
        col1, col2, col3 = st.columns(3)
        col1.metric("T2s [K]", f"{T2s:.2f}")
        col2.metric("T4s [K]", f"{T4s:.2f}")
        col3.metric("Efficiency [%]", f"{eff_ideal * 100:.2f}")

        st.markdown("#### 🔹 Actual Brayton Cycle")
        col4, col5, col6, col7 = st.columns(4)
        col4.metric("T2 [K]", f"{T2:.2f}")
        col5.metric("T4 [K]", f"{T4:.2f}")
        col6.metric("Efficiency [%]", f"{eff_actual:.2f}")
        col7.metric("Net Work [kJ/kg]", f"{w_net_actual:.2f}")

        st.markdown("#### 🔹 Heat and Work")
        col8, col9, col10 = st.columns(3)
        col8.metric("Heat Added [kJ/kg]", f"{q_in_actual:.2f}")
        col9.metric("Heat Rejected [kJ/kg]", f"{q_out_actual:.2f}")
        col10.metric("Compressor Work [kJ/kg]", f"{w_c_actual:.2f}")
    else:
        st.info("Enter the values and click **Solve** to simulate the Brayton cycle.")

main()
