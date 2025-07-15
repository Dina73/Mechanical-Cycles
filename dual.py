import streamlit as st

def main():
    st.set_page_config(page_title="Dual Cycle Efficiency Simulator", layout="centered")
    st.title("🔧 Dual Cycle Solver")

    k = 1.4
    cv = 0.718  # kJ/kg.K
    cp = 1.005  # kJ/kg.K
    R = 0.2871  # kJ/kg.K

    st.markdown("### Input Parameters")

    col1, col2 = st.columns(2)
    with col1:
        r = st.number_input("Compression Ratio (r)", min_value=1.0)
        P1 = st.number_input("Initial Pressure P1 [bar]", min_value=0.0)
    with col2:
        T1 = st.number_input("Initial Temperature T1 [K]", min_value=0.0)
        P3 = st.number_input("Max Pressure P3 [bar]", min_value=0.0)

    if st.button("Solve"):
        # State 1
        V1 = (R * T1) / P1

        # 1 → 2: Isentropic Compression
        V2 = V1 / r
        T2 = T1 * (r ** (k - 1))
        P2 = P1 * (r ** k)

        # 2 → 3: Constant Volume Heat Addition
        T3 = (P3 * T2) / P2
        V3 = V2
        q_in1 = cv*(T3 - T2)
        
        # 3 → 4: Constant Pressure Heat Addition
        P4 = P3
        q_in2 = q_in1
        T4=(q_in2 / cp)+ T3
        V4=(R * T4) / P4
        
        # 4 → 5: Isentropic Expansion
        V5 = V1
        T5 = T4 * (V4 / V5) ** (k-1)
        P5 = P4 * (V4 / V5) ** (k)

        # Heat & work
        q_in = q_in1 + q_in2
        q_out = cv * (T5 - T1)
        w_net = q_in - q_out
        efficiency = (w_net / q_in) * 100 if q_in else 0

        # Display results
        st.subheader("✔️ Results")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("T2", f"{T2:.2f} K")
        col1.metric("P2", f"{P2:.2f} bar")
        col2.metric("T3", f"{T3:.2f} K")
        col2.metric("P3", f"{P3:.2f} bar")
        col3.metric("T4", f"{T4:.2f} K")
        col3.metric("P4", f"{P4:.2f} bar")
        col4.metric("T5", f"{T5:.2f} K")
        col4.metric("P5", f"{P5:.2f} bar")
        col1.metric("Efficiency", f"{efficiency:.4f} %")
        col2.metric("Net Work", f"{w_net:.2f} kJ/kg")
        col3.metric("Heat Added", f"{q_in:.2f} kJ/kg")
        col4.metric("Heat Rejected", f"{q_out:.2f} kJ/kg")
    else:
        st.info("Enter values and click **Solve** to simulate the cycle.")

# ✅ Ensure Streamlit runs the app
main()

