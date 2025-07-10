import streamlit as st

def solve_diesel_cycle(r=None, V1=None, P1=None, T1=None, Qin=None, P3=None, T3=None):
    k = 1.4
    R = 0.2871  # kJ/kg.K
    cv = 0.718  # kJ/kg.K
    cp = 1.005  # kJ/kg.K
    results = {}

    try:
        # Estimate missing state variables
        if r and T1:
            T2 = T1 * r**(k - 1)
            results["T2 [K]"] = T2
        if r and P1:
            P2 = P1 * r**k
            results["P2 [kPa]"] = P2

        # If T3 and T2 exist → estimate cutoff ratio, etc.
        if r and V1 and T3 and T1:
            P1 = (R * T1) / V1
            V2 = V1 / r
            P2 = P1 *(r**k)
            T2 = T1 * r**(k - 1)
            P3 = P2
            V3 = (R * T3) / P3
            rc = V3 / V2
            q_in = cp * (T3 - T2)
            T4 = T3 * (V3 / V1)**(k - 1)
            P4 = P3 * (V3 / V1)**(k)
            q_out = cv * (T4 - T1)
            w_net = q_in - q_out
            eff = w_net / q_in

            results.update({
                "P2 [kPa]": P2,
                "T3 [K]": T3,
                "P3 [kPa]": P3,
                "T4 [K]": T4,
                "P4 [kPa]": P4,
                "Net Work [kJ/kg]": w_net,
                "Efficiency [%]": eff * 100,
            })

        # If P3, T3, P1, T1 are known → estimate r and efficiency
        elif P3 and T3 and P1 and T1:
            r = (P3 / P1) ** (1 / k)
            v1 = R * T1 / P1
            T2 = T1 * r**(k - 1)
            v2 = v1 / r
            P2 = P3
            V3 = (R * T3) / P3
            rc = V3 / V2
            T4 = T3 * (rc / r)**(k - 1)
            P4 = P3 * ((V3 / V1)**(k))
            q_in = cp * (T3 - T2)
            q_out = cv * (T4 - T1)
            w_net = q_in - q_out
            eff = w_net / q_in

            results.update({
                "Estimated Compression Ratio (r)": r,
                "Efficiency [%]": eff * 100,
            })

        # If Qin, r, P1, T1 are known
        elif Qin and r and P1 and T1:
            V1 = R * T1 / P1
            V2 = V1 / r
            T2 = T1 * r**(k - 1)
            P2 = P1 * r**k
            P3 = P2
            T3 = T2 + Qin / cp
            V3 = (R * T3) / P3
            rc = V3 / V2
            T4 = T3 * (V3 / V1)**(k - 1)
            P4 = P3 * (V3 / V1)**(k)
            q_out = cv * (T4 - T1)
            w_net = Qin - q_out
            eff = w_net / Qin

            results.update({
                "T2 [K]": T2, "P2 [kPa]": P2,
                "T3 [K]": T3, "P3 [kPa]": P3,
                "T4 [K]": T4, "P4 [kPa]": P4,
                "Efficiency [%]": eff * 100,
            })

        return results if results else None

    except Exception as e:
        return {"Error": str(e)}

# ------------- STREAMLIT APP --------------
st.set_page_config("Diesel Cycle Solver", layout="centered")
st.title("🧠 Diesel Cycle Smart Solver")

st.markdown("Enter whatever values you know. The app will solve what it can automatically.")

# 🔢 USER INPUT
col1, col2, col3 = st.columns(3)
with col1:
    r = st.number_input("Compression Ratio (r)", value=0.0)
    V1 = st.number_input("Initial Volume V1 [L]", value=0.0)
    Qin = st.number_input("Heat Added Q_in [kJ/kg]", value=0.0)

with col2:
    P1 = st.number_input("Initial Pressure P1 [kPa]", value=0.0)
    P3 = st.number_input("Max Pressure P3 [kPa]", value=0.0)

with col3:
    T1 = st.number_input("Initial Temperature T1 [K]", value=0.0)
    T3 = st.number_input("Max Temperature T3 [K]", value=0.0)

if st.button("🧪 Solve"):
    result = solve_diesel_cycle(
        r=r if r > 0 else None,
        V1=V1 if V1 > 0 else None,
        P1=P1 if P1 > 0 else None,
        T1=T1 if T1 > 0 else None,
        Qin=Qin if Qin > 0 else None,
        P3=P3 if P3 > 0 else None,
        T3=T3 if T3 > 0 else None
    )

    if result:
        st.success("✔️ Computed Results")
        for key, val in result.items():
            try:
                st.metric(label=key, value=f"{float(val):.2f}")
            except (ValueError, TypeError):
                st.metric(label=key, value=str(val))
    else:
        st.warning("❗ Please provide more complete or valid inputs to solve the cycle.")

