import streamlit as st

def solve_diesel_cycle(r=None, V1_L=None, P1=None, T1=None, Qin=None, P3=None, T3=None):
    k = 1.4
    R = 0.2871  # kJ/kg.K
    cv, cp = 0.718, 1.005 # kJ/kg.K
    results = {}

    try:
        V1_m3 = V1_L / 1000 if V1_L else None
        v1 = (R * T1) / P1 if T1 and P1 else V1_m3
        if r and T1 and T3:
            T2 = T1 * r**(k - 1)
            P2 = P1 * r**k if P1 else P3
            P3 = P2
            v2 = v1 / r
            v3 = (R * T3) / P3
            rc = v3 / v2

            T4 = T3 * (v3 / v1)**(k - 1)
            P4 = P3 * (v3 / v1)**k

            q_in = cp * (T3 - T2)
            q_out = cv * (T4 - T1)
            w_net = q_in - q_out
            eff = w_net / q_in if q_in else 0

            results.update({
                "T2 [K]": T2, "T3 [K]": T3, "T4 [K]": T4,
                "P2 [kPa]": P2, "P3 [kPa]": P3, "P4 [kPa]": P4,
                "Heat Added [kJ/kg]": q_in, "Heat Rejected [kJ/kg]": q_out,
                "Net Work [kJ/kg]": w_net, "Efficiency [%]": eff * 100,
            })

        elif P3 and T3 and P1 and T1:
            r = (P3 / P1)**(1 / k)
            return solve_diesel_cycle(r=r, V1_L=V1_L, P1=P1, T1=T1, P3=P3, T3=T3)

        elif Qin and r and P1 and T1:
            v1 = (R * T1) / P1
            v2 = v1 / r
            T2 = T1 * r**(k - 1)
            P2 = P1 * r**k
            T3 = T2 + Qin / cp
            v3 = (R * T3) / P2
            rc = v3 / v2
            T4 = T3 * (v3 / v1)**(k - 1)
            P4 = P2 * (v3 / v1)**k
            q_out = cv * (T4 - T1)
            w_net = Qin - q_out
            eff = w_net / Qin

            results.update({
                "T2 [K]": T2, "T3 [K]": T3, "T4 [K]": T4,
                "P2 [kPa]": P2, "P3 [kPa]": P2, "P4 [kPa]": P4,
                "Heat Rejected [kJ/kg]": q_out,
                "Net Work [kJ/kg]": w_net,
                "Efficiency [%]": eff * 100,
                "Heat Added [kJ/kg]": Qin
            })

        return results if results else {"Error": "Insufficient or inconsistent inputs."}

    except Exception as e:
        return {"Error": str(e)}

# ---------- STREAMLIT UI ----------
st.set_page_config("Diesel Cycle Solver", layout="centered")
st.title("🔧 Diesel Cycle Solver")

st.markdown("Enter known values. Leave others blank. The solver adapts accordingly.")

col1, col2, col3 = st.columns(3)
with col1:
    r = st.number_input("Compression Ratio (r)", min_value=0.0, format="%.1f")
    V1 = st.number_input("Initial Volume V1 [L]", min_value=0.0, format="%.1f")
    Qin = st.number_input("Heat Added Q_in [kJ/kg]", min_value=0.0, format="%.1f")

with col2:
    P1 = st.number_input("Initial Pressure P1 [kPa]", min_value=0.0, format="%.1f")
    P3 = st.number_input("Max Pressure P3 [kPa]", min_value=0.0, format="%.1f")

with col3:
    T1 = st.number_input("Initial Temperature T1 [K]", min_value=0.0, format="%.1f")
    T3 = st.number_input("Max Temperature T3 [K]", min_value=0.0, format="%.1f")

if st.button("Solve"):
    result = solve_diesel_cycle(
        r=r or None, V1_L=V1 or None, Qin=Qin or None,
        P1=P1 or None, P3=P3 or None, T1=T1 or None, T3=T3 or None
    )

    if "Error" in result:
        st.error(f"❌ {result['Error']}")
    else:
        st.success("✔️ Results")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if P1: st.metric("P1 [kPa]", f"{P1:.2f}")
            if T1: st.metric("T1 [K]", f"{T1:.2f}")
            if "Heat Added [kJ/kg]" in result:
                st.metric("Heat Added [kJ/kg]", f"{result['Heat Added [kJ/kg]']:.3f}")

        with col2:
            if "P2 [kPa]" in result:
                st.metric("P2 [kPa]", f"{result['P2 [kPa]']:.3f}")
            if "T2 [K]" in result:
                st.metric("T2 [K]", f"{result['T2 [K]']:.3f}")
            if "Heat Rejected [kJ/kg]" in result:
                st.metric("Heat Rejected [kJ/kg]", f"{result['Heat Rejected [kJ/kg]']:.3f}")

        with col3:
            if "P3 [kPa]" in result:
                st.metric("P3 [kPa]", f"{result['P3 [kPa]']:.3f}")
            if "T3 [K]" in result:
                st.metric("T3 [K]", f"{result['T3 [K]']:.3f}")
            if "Efficiency [%]" in result:
                st.metric("Efficiency [%]", f"{result['Efficiency [%]']:.2f} %")

        with col4:
            if "P4 [kPa]" in result:
                st.metric("P4 [kPa]", f"{result['P4 [kPa]']:.3f}")
            if "T4 [K]" in result:
                st.metric("T4 [K]", f"{result['T4 [K]']:.3f}")
            if "Net Work [kJ/kg]" in result:
                st.metric("Net Work [kJ/kg]", f"{result['Net Work [kJ/kg]']:.3f}")
