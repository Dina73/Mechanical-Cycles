import streamlit as st

def solve_dual_cycle(r=None, rp=None, rc=None, V1_L=None, P1=None, T1=None, Qin=None):
    k = 1.4
    R = 0.2871  # kJ/kg.K
    cv, cp = 0.718, 1.005  # kJ/kg.K
    results = {}

    try:
        V1_m3 = V1_L / 1000 if V1_L else None
        v1 = (R * T1) / P1 if T1 and P1 else V1_m3

        if r and rc and rp and T1:
            v2 = v1 / r
            T2 = T1 * r**(k - 1)
            P2 = P1 * r**k

            # Isentropic compression: 1 -> 2
            # Constant volume heat addition: 2 -> 3
            T3 = T2 * rp
            P3 = P2 * rp

            # Constant pressure heat addition: 3 -> 4
            v3 = v2
            v4 = rc * v3
            T4 = T3 * rc
            P4 = P3

            # Isentropic expansion: 4 -> 5
            T5 = T4 * (v4 / v1)**(1 - k)
            P5 = P4 * (v4 / v1)**(-k)

            # Heat and work calculations
            q_in = cv * (T3 - T2) + cp * (T4 - T3)
            q_out = cv * (T5 - T1)
            w_net = q_in - q_out
            eff = w_net / q_in if q_in else 0

            results.update({
                "T2 [K]": T2, "T3 [K]": T3, "T4 [K]": T4, "T5 [K]": T5,
                "P2 [kPa]": P2, "P3 [kPa]": P3, "P4 [kPa]": P4, "P5 [kPa]": P5,
                "Heat Added [kJ/kg]": q_in, "Heat Rejected [kJ/kg]": q_out,
                "Net Work [kJ/kg]": w_net, "Efficiency [%]": eff * 100,
            })

        return results if results else {"Error": "Insufficient or inconsistent inputs."}

    except Exception as e:
        return {"Error": str(e)}

# ---------- STREAMLIT UI ----------
st.set_page_config("Dual Cycle Solver", layout="centered")
st.title("⚙️ Dual Cycle Solver")

st.markdown("Enter known values below. Leave blank if unknown.")

col1, col2, col3 = st.columns(3)
with col1:
    r = st.number_input("Compression Ratio (r)", min_value=0.0, format="%.2f")
    rc = st.number_input("Cut-off Ratio (rc)", min_value=0.0, format="%.2f")
    V1 = st.number_input("Initial Volume V1 [L]", min_value=0.0, format="%.1f")

with col2:
    P1 = st.number_input("Initial Pressure P1 [kPa]", min_value=0.0, format="%.1f")
    rp = st.number_input("Pressure Ratio (rp = P3/P2)", min_value=0.0, format="%.2f")
    Qin = st.number_input("Total Heat Added Q_in [kJ/kg]", min_value=0.0, format="%.1f")

with col3:
    T1 = st.number_input("Initial Temperature T1 [K]", min_value=0.0, format="%.1f")

if st.button("Solve"):
    result = solve_dual_cycle(
        r=r or None, rc=rc or None, rp=rp or None, V1_L=V1 or None,
        P1=P1 or None, T1=T1 or None, Qin=Qin or None
    )

    if "Error" in result:
        st.error(f"❌ {result['Error']}")
    else:
        st.success("✔️ Results")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("P1 [kPa]", f"{P1:.2f}")
            st.metric("T1 [K]", f"{T1:.2f}")
            st.metric("T2 [K]", f"{result['T2 [K]']:.2f}")

        with col2:
            st.metric("P2 [kPa]", f"{result['P2 [kPa]']:.2f}")
            st.metric("T3 [K]", f"{result['T3 [K]']:.2f}")
            st.metric("P3 [kPa]", f"{result['P3 [kPa]']:.2f}")

        with col3:
            st.metric("T4 [K]", f"{result['T4 [K]']:.2f}")
            st.metric("P4 [kPa]", f"{result['P4 [kPa]']:.2f}")
            st.metric("T5 [K]", f"{result['T5 [K]']:.2f}")

        with col4:
            st.metric("P5 [kPa]", f"{result['P5 [kPa]']:.2f}")
            st.metric("Net Work [kJ/kg]", f"{result['Net Work [kJ/kg]']:.2f}")
            st.metric("Efficiency [%]", f"{result['Efficiency [%]']:.2f}")
