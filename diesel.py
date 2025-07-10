import streamlit as st

def solve_diesel_cycle(r=None, V1_L=None, P1=None, T1=None, Qin=None, P3=None, T3=None):
    k = 1.4
    R = 0.2871  # kJ/kg.K
    cv, cp = 0.718, 1.005
    results = {}

    try:
        m = None
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
            })

        return results if results else {"Error": "Insufficient or inconsistent inputs."}

    except Exception as e:
        return {"Error": str(e)}

# ---------- STREAMLIT UI ----------
st.set_page_config("Diesel Cycle Solver", layout="centered")
st.title("🧠 Diesel Cycle Smart Solver")

st.markdown("Enter known values. Leave others blank. The solver adapts accordingly.")

col1, col2, col3 = st.columns(3)
with col1:
    r = st.number_input("Compression Ratio (r)", min_value=0.0, format="%.2f")
    V1 = st.number_input("Initial Volume V1 [L]", min_value=0.0, format="%.3f")
    Qin = st.number_input("Heat Added Q_in [kJ/kg]", min_value=0.0, format="%.2f")

with col2:
    P1 = st.number_input("Initial Pressure P1 [kPa]", min_value=0.0, format="%.2f")
    P3 = st.number_input("Max Pressure P3 [kPa]", min_value=0.0, format="%.2f")

with col3:
    T1 = st.number_input("Initial Temperature T1 [K]", min_value=0.0, format="%.2f")
    T3 = st.number_input("Max Temperature T3 [K]", min_value=0.0, format="%.2f")

if st.button("🧪 Solve"):
    result = solve_diesel_cycle(
        r=r or None, V1_L=V1 or None, Qin=Qin or None,
        P1=P1 or None, P3=P3 or None, T1=T1 or None, T3=T3 or None
    )

    if "Error" in result:
        st.error(f"❌ {result['Error']}")
    else:
        st.success("✔️ Results")
        for key, val in result.items():
            st.metric(label=key, value=f"{val:.3f}")

