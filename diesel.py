import streamlit as st

def solve_diesel_cycle(r=None, V1_input=None, P1=None, T1=None, Qin=None, P3=None, T3=None):
    """
    Solves the Diesel Cycle thermodynamic properties based on provided inputs.

    Args:
        r (float, optional): Compression Ratio. Defaults to None.
        V1_input (float, optional): Initial Volume V1 in Liters (can be total or specific). Defaults to None.
        P1 (float, optional): Initial Pressure P1 in kPa. Defaults to None.
        T1 (float, optional): Initial Temperature T1 in Kelvin. Defaults to None.
        Qin (float, optional): Heat Added Q_in in kJ/kg. Defaults to None.
        P3 (float, optional): Max Pressure P3 in kPa. Defaults to None.
        T3 (float, optional): Max Temperature T3 in Kelvin. Defaults to None.

    Returns:
        dict: A dictionary containing the calculated properties, or an error message.
    """
    k = 1.4
    R = 0.2871  # kJ/kg.K
    cv = 0.718  # kJ/kg.K
    cp = 1.005  # kJ/kg.K
    results = {}
    m = None  # Mass of air, will be calculated if V1 (total), P1, T1 are provided

    try:
        V1_total_m3 = None  # Total volume in m^3 (from V1_input if it's total volume)
        v1_specific_m3_per_kg = None  # Specific volume in m^3/kg

        # Convert V1_input (Liters) to m^3 for internal calculations
        if V1_input is not None:
            V1_total_m3 = V1_input / 1000

        # --- Determine initial state 1 properties and mass ---
        if P1 is not None and T1 is not None:
            # Calculate specific volume at state 1 from P1 and T1
            v1_specific_m3_per_kg = (R * T1) / P1
            results["v1 [L/kg]"] = v1_specific_m3_per_kg * 1000  # Display specific volume in L/kg

            if V1_total_m3 is not None:
                # If V1 (total volume) is also provided, calculate the mass of air
                m = V1_total_m3 / v1_specific_m3_per_kg
                results["Calculated Mass [kg]"] = m
                results["Total Volume V1 [L]"] = V1_input  # Display original V1_input as total volume
        elif V1_total_m3 is not None and (P1 is None or T1 is None):
            # If V1 is provided but P1 or T1 are missing, we must assume V1 is specific volume
            # for the cycle calculations to proceed.
            v1_specific_m3_per_kg = V1_total_m3
            results["Note: V1 treated as specific volume [L/kg]"] = V1_input
            results["v1 [L/kg]"] = V1_input

        # --- Scenario 1: r, T1, T3 are known (and P1, V1 might be known) ---
        if r is not None and T1 is not None and T3 is not None:
            # Calculate T2
            T2 = T1 * r**(k - 1)
            results["T2 [K]"] = T2

            # If P1 is known, calculate P2 and P3
            P2_calc = None
            if P1 is not None:
                P2_calc = P1 * r**k
                results["P2 [kPa]"] = P2_calc
                results["P3 [kPa]"] = P2_calc  # P3 = P2 for Diesel cycle
            elif P3 is not None:  # If P3 is known, then P2 = P3
                P2_calc = P3
                results["P2 [kPa]"] = P2_calc

            # Proceed with specific volume calculations if v1_specific_m3_per_kg is available
            if v1_specific_m3_per_kg is not None:
                v2_specific = v1_specific_m3_per_kg / r
                results["v2 [L/kg]"] = v2_specific * 1000

                v3_specific = None
                if P2_calc is not None:
                    v3_specific = (R * T3) / P2_calc  # Use P2_calc as P3
                    results["v3 [L/kg]"] = v3_specific * 1000
                elif P3 is not None:
                    v3_specific = (R * T3) / P3
                    results["v3 [L/kg]"] = v3_specific * 1000

                if v2_specific is not None and v3_specific is not None and v2_specific != 0:
                    rc = v3_specific / v2_specific
                    results["Cutoff Ratio (rc)"] = rc

                    # Calculate T4
                    T4 = T3 * (v3_specific / v1_specific_m3_per_kg)**(k - 1)
                    results["T4 [K]"] = T4

                    # Calculate P4
                    P4 = (P2_calc if P2_calc is not None else P3) * (v3_specific / v1_specific_m3_per_kg)**k  # P4 = P3 * (v3/v4)^k, v4=v1
                    results["P4 [kPa]"] = P4

                    # Calculate Q_in, Q_out, W_net (specific values)
                    q_in_specific = cp * (T3 - T2)
                    q_out_specific = cv * (T4 - T1)
                    w_net_specific = q_in_specific - q_out_specific
                    eff = w_net_specific / q_in_specific if q_in_specific != 0 else 0

                    results["Heat Added Q_in [kJ/kg]"] = q_in_specific
                    results["Heat Rejected Q_out [kJ/kg]"] = q_out_specific
                    results["Net Work [kJ/kg]"] = w_net_specific
                    results["Efficiency [%]"] = eff * 100

                    # If mass is known, calculate total volumes and total heat/work
                    if m is not None:
                        results["Total Volume V2 [L]"] = v2_specific * m * 1000
                        results["Total Volume V3 [L]"] = v3_specific * m * 1000
                        results["Total Net Work [kJ]"] = w_net_specific * m
                        results["Total Heat Added Q_in [kJ]"] = q_in_specific * m
                        results["Total Heat Rejected Q_out [kJ]"] = q_out_specific * m

        # --- Scenario 2: P3, T3, P1, T1 are known ---
        elif P3 is not None and T3 is not None and P1 is not None and T1 is not None:
            r = (P3 / P1)**(1 / k)  # Calculate r from P1, P3, k
            results["Estimated Compression Ratio (r)"] = r

            T2 = T1 * r**(k - 1)
            results["T2 [K]"] = T2
            results["P2 [kPa]"] = P3  # P2 = P3

            v1_specific_m3_per_kg = (R * T1) / P1
            v2_specific = v1_specific_m3_per_kg / r
            v3_specific = (R * T3) / P3
            rc = v3_specific / v2_specific
            results["v1 [L/kg]"] = v1_specific_m3_per_kg * 1000
            results["v2 [L/kg]"] = v2_specific * 1000
            results["v3 [L/kg]"] = v3_specific * 1000
            results["Cutoff Ratio (rc)"] = rc

            T4 = T3 * (v3_specific / v1_specific_m3_per_kg)**(k - 1)
            P4 = P3 * (v3_specific / v1_specific_m3_per_kg)**k
            results["T4 [K]"] = T4
            results["P4 [kPa]"] = P4

            q_in_specific = cp * (T3 - T2)
            q_out_specific = cv * (T4 - T1)
            w_net_specific = q_in_specific - q_out_specific
            eff = w_net_specific / q_in_specific if q_in_specific != 0 else 0

            results["Heat Added Q_in [kJ/kg]"] = q_in_specific
            results["Heat Rejected Q_out [kJ/kg]"] = q_out_specific
            results["Net Work [kJ/kg]"] = w_net_specific
            results["Efficiency [%]"] = eff * 100

            # If mass is known, calculate total volumes and total heat/work
            if m is not None:
                results["Total Volume V1 [L]"] = v1_specific_m3_per_kg * m * 1000
                results["Total Volume V2 [L]"] = v2_specific * m * 1000
                results["Total Volume V3 [L]"] = v3_specific * m * 1000
                results["Total Net Work [kJ]"] = w_net_specific * m
                results["Total Heat Added Q_in [kJ]"] = q_in_specific * m
                results["Total Heat Rejected Q_out [kJ]"] = q_out_specific * m

        # --- Scenario 3: Qin, r, P1, T1 are known ---
        elif Qin is not None and r is not None and P1 is not None and T1 is not None:
            v1_specific_m3_per_kg = (R * T1) / P1
            v2_specific = v1_specific_m3_per_kg / r
            T2 = T1 * r**(k - 1)
            P2 = P1 * r**k
            P3_calc = P2
            T3 = T2 + Qin / cp
            v3_specific = (R * T3) / P3_calc
            rc = v3_specific / v2_specific
            T4 = T3 * (v3_specific / v1_specific_m3_per_kg)**(k - 1)
            P4 = P3_calc * (v3_specific / v1_specific_m3_per_kg)**k
            q_out_specific = cv * (T4 - T1)
            w_net_specific = Qin - q_out_specific
            eff = w_net_specific / Qin if Qin != 0 else 0

            results["T2 [K]"] = T2
            results["P2 [kPa]"] = P2
            results["T3 [K]"] = T3
            results["P3 [kPa]"] = P3_calc
            results["v1 [L/kg]"] = v1_specific_m3_per_kg * 1000
            results["v2 [L/kg]"] = v2_specific * 1000
            results["v3 [L/kg]"] = v3_specific * 1000
            results["Cutoff Ratio (rc)"] = rc
            results["T4 [K]"] = T4
            results["P4 [kPa]"] = P4
            results["Heat Rejected Q_out [kJ/kg]"] = q_out_specific
            results["Net Work [kJ/kg]"] = w_net_specific
            results["Efficiency [%]"] = eff * 100

            # If mass is known, calculate total volumes and total heat/work
            if m is not None:
                results["Total Volume V1 [L]"] = v1_specific_m3_per_kg * m * 1000
                results["Total Volume V2 [L]"] = v2_specific * m * 1000
                results["Total Volume V3 [L]"] = v3_specific * m * 1000
                results["Total Net Work [kJ]"] = w_net_specific * m
                results["Total Heat Added Q_in [kJ]"] = q_in_specific * m
                results["Total Heat Rejected Q_out [kJ]"] = q_out_specific * m

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
    r = st.number_input("Compression Ratio (r)", value=0.0, format="%.2f")
    V1 = st.number_input("Initial Volume V1 [L] (Total or Specific)", value=0.0, format="%.3f")
    Qin = st.number_input("Heat Added Q_in [kJ/kg]", value=0.0, format="%.2f")

with col2:
    P1 = st.number_input("Initial Pressure P1 [kPa]", value=0.0, format="%.2f")
    P3 = st.number_input("Max Pressure P3 [kPa]", value=0.0, format="%.2f")

with col3:
    T1 = st.number_input("Initial Temperature T1 [K]", value=0.0, format="%.2f")
    T3 = st.number_input("Max Temperature T3 [K]", value=0.0, format="%.2f")

if st.button("🧪 Solve"):
    result = solve_diesel_cycle(
        r=r if r > 0 else None,
        V1_input=V1 if V1 > 0 else None,
        P1=P1 if P1 > 0 else None,
        T1=T1 if T1 > 0 else None,
        Qin=Qin if Qin > 0 else None,
        P3=P3 if P3 > 0 else None,
        T3=T3 if T3 > 0 else None
    )

    if result:
        if "Error" in result:
            st.error(f"❌ Calculation Error: {result['Error']}")
        else:
            st.success("✔️ Computed Results")
            for key, val in result.items():
                try:
                    st.metric(label=key, value=f"{float(val):.3f}") # Increased precision
                except (ValueError, TypeError):
                    st.metric(label=key, value=str(val))
    else:
        st.warning("❗ Please provide more complete or valid inputs to solve the cycle.")
