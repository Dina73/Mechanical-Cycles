import streamlit as st
from iapws import IAPWS97

# --- Global page configuration for the entire app ---
st.set_page_config(page_title="Thermodynamic Cycle Solver", layout="centered")
st.title("⚙️ Combined Thermodynamic Cycle Solver")

# --- Function to handle the Brayton Cycle logic and UI ---
def brayton_cycle_app():
    # Brayton Cycle Solver logic (user's code)
    def brayton(cycle, rp, T1, T3, T4=None, eta_c=None, eta_t=None, P_MW=None, m_kgph=None):
        r = {}
        # Use given efficiencies or assume ideal (1)
        e_c = eta_c / 100 if (cycle == "Actual" and eta_c not in (None, 0)) else 1
        e_t = eta_t / 100 if (cycle == "Actual" and eta_t not in (None, 0)) else 1
        k = 1.4
        cp = 1.005

        T2s = T1 * rp ** ((k - 1) / k)
        T4s = T3 / rp ** ((k - 1) / k)
        T2a = T1 + (T2s - T1) / e_c
        T4a = T3 - (T3 - T4s) * e_t if T4 is None else T4

        wc, wt = cp * (T2a - T1), cp * (T3 - T4a)
        wnet = wt - wc
        qin = cp * (T3 - T2a)
        qout = cp * (T4a - T1)
        eff = (wnet / qin) * 100 if qin else 0

        r.update(T1=T1, T3=T3, rp=rp, T2s=T2s, T4s=T4s, T2a=T2a, T4a=T4a,
                  w_c=wc, w_t=wt, w_net=wnet, q_in=qin, q_out=qout, eff=eff)

        if P_MW or m_kgph:
            wnet = (P_MW * 1000) / (m_kgph / 3600)
            wc = wt - wnet
            T2a = (wc / cp) + T1
            eta_c = ((cp * (T2s - T1)) / wc) * 100
            qin = cp * (T3 - T2a)
            r.update(w_net=wnet, w_c=wc, q_in=qin, T2a=T2a)

        if cycle == "Actual":
            r['eta_c'] = eta_c if eta_c not in (None, 0) else (T2s - T1) / (T2a - T1) * 100
            r['eta_t'] = eta_t if eta_t not in (None, 0) else (T3 - T4a) / (T3 - T4s) * 100
        return r

    st.subheader("Brayton Cycle Solver")
    cycle = st.selectbox("Cycle Type", ["Ideal", "Actual"])
    col1, col2 = st.columns(2)
    with col1:
        T1 = st.number_input("T1 [K]", value=0.0)
        T3 = st.number_input("T3 [K]", value=0.0)
        T4 = st.number_input("T4 [K]", value=0.0) or None
    with col2:
        rp = st.number_input("Pressure Ratio", value=0.0)
        P_MW = st.number_input("Net Power [MW]", value=0.0) or None
        m_kgph = st.number_input("Mass Flow [kg/hr]", value=0.0) or None
        eta_c = eta_t = None

    if cycle == "Actual":
        eta_c_input = st.number_input("Compressor η [%]", value=0.0)
        eta_t_input = st.number_input("Turbine η [%]", value=0.0)
        eta_c = eta_c_input if eta_c_input > 0 else None
        eta_t = eta_t_input if eta_t_input > 0 else None

    if st.button("Calculate", key="brayton_calc"):
        r = brayton(cycle, rp, T1, T3, T4, eta_c, eta_t, P_MW, m_kgph)

        c1, c2, c3 = st.columns(3)

        if cycle == "Ideal":
            c1.metric("T1 [K]", f"{r['T1']:.2f}")
            c2.metric("T2s [K]", f"{r['T2s']:.2f}")
            c3.metric("T3 [K]", f"{r['T3']:.2f}")
            c1.metric("T4s [K]", f"{r['T4s']:.2f}")
            c2.metric("w_c [kJ/kg]", f"{r['w_c']:.2f}")
            c3.metric("w_t [kJ/kg]", f"{r['w_t']:.2f}")
            c1.metric("w_net [kJ/kg]", f"{r['w_net']:.2f}")
            c2.metric("q_in [kJ/kg]", f"{r['q_in']:.2f}")
            c3.metric("q_out [kJ/kg]", f"{r['q_out']:.2f}")
            c1.metric("Efficiency [%]", f"{r['eff']:.2f}")

        if cycle == "Actual":
            c1.metric("T1 [K]", f"{r['T1']:.2f}")
            c2.metric("T2s [K]", f"{r['T2s']:.2f}")
            c3.metric("T2a [K]", f"{r['T2a']:.2f}")
            c1.metric("T3 [K]", f"{r['T3']:.2f}")
            c2.metric("T4s [K]", f"{r['T4s']:.2f}")
            c3.metric("T4a [K]", f"{r['T4a']:.2f}")
            c1.metric("w_c [kJ/kg]", f"{r['w_c']:.2f}")
            c2.metric("w_t [kJ/kg]", f"{r['w_t']:.2f}")
            c3.metric("w_net [kJ/kg]", f"{r['w_net']:.2f}")
            c1.metric("q_in [kJ/kg]", f"{r['q_in']:.2f}")
            c2.metric("q_out [kJ/kg]", f"{r['q_out']:.2f}")
            c3.metric("Efficiency [%]", f"{r['eff']:.2f}")
            c1.metric("Compressor η [%]", f"{r['eta_c']:.2f}")
            c2.metric("Turbine η [%]", f"{r['eta_t']:.2f}")

# --- Function to handle the Diesel Cycle logic and UI ---
def diesel_cycle_app():
    # Diesel Cycle Solver logic (user's code)
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

    # UI for Diesel Cycle
    st.subheader("Diesel Cycle Solver")
    st.markdown("Enter known values. Leave others blank. The solver adapts accordingly.")
    col1, col2, col3 = st.columns(3)
    with col1:
        r = st.number_input("Compression Ratio (r)", min_value=0.0, format="%.1f", key="diesel_r")
        V1 = st.number_input("Initial Volume V1 [L]", min_value=0.0, format="%.1f", key="diesel_V1")
        Qin = st.number_input("Heat Added Q_in [kJ/kg]", min_value=0.0, format="%.1f", key="diesel_Qin")

    with col2:
        P1 = st.number_input("Initial Pressure P1 [kPa]", min_value=0.0, format="%.1f", key="diesel_P1")
        P3 = st.number_input("Max Pressure P3 [kPa]", min_value=0.0, format="%.1f", key="diesel_P3")

    with col3:
        T1 = st.number_input("Initial Temperature T1 [K]", min_value=0.0, format="%.1f", key="diesel_T1")
        T3 = st.number_input("Max Temperature T3 [K]", min_value=0.0, format="%.1f", key="diesel_T3")

    if st.button("Solve", key="diesel_solve"):
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

# --- Function to handle the Dual Cycle logic and UI ---
def dual_cycle_app():
    # Dual Cycle Solver logic (user's code)
    k = 1.4
    cv = 0.718  # kJ/kg.K
    cp = 1.005  # kJ/kg.K
    R = 0.2871  # kJ/kg.K

    st.subheader("Dual Cycle Solver")
    st.markdown("### Input Parameters")

    col1, col2 = st.columns(2)
    with col1:
        r = st.number_input("Compression Ratio (r)", min_value=1.0, key="dual_r")
        P1 = st.number_input("Initial Pressure P1 [bar]", min_value=0.0, key="dual_P1")
    with col2:
        T1 = st.number_input("Initial Temperature T1 [K]", min_value=0.0, key="dual_T1")
        P3 = st.number_input("Max Pressure P3 [bar]", min_value=0.0, key="dual_P3")

    if st.button("Solve", key="dual_solve"):
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

# --- Function to handle the Otto Cycle logic and UI ---
def otto_cycle_app():
    # Otto Cycle Solver logic (user's code)
    k = 1.4
    cv = 0.718  # kJ/kg.K
    cp = 1.005   # kJ/kg.K
    R = 0.2871   # kJ/kg.K

    st.subheader("Otto Cycle Solver")
    st.markdown("Input Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        compression_ratio = st.number_input("Compression Ratio (r)", min_value=1.0, key="otto_r")
        heat_added = st.number_input("Heat Added (Qin) [kJ/kg]", min_value=0.0, key="otto_heat")
    with col2:
        T1 = st.number_input("Initial Temperature T1 [K]", min_value=0.0, key="otto_T1")
        P1 = st.number_input("Initial Pressure P1 [kPa]", min_value=0.0, key="otto_P1")

    if st.button("Solve", key="otto_solve"):
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

        st.subheader("✔️ Results")
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
        st.info("Enter values and click **Solve** to simulate the cycle.")

# --- Function to handle the Rankine Cycle logic and UI ---
def rankine_cycle_app():
    # Rankine Cycle Solver logic (user's code)
    st.subheader("Rankine Cycle Solver (Ideal & Actual)")

    # --- Inputs ---
    P1 = st.number_input("Condenser Pressure (MPa)",  min_value=0.0, key="rankine_P1")
    P2 = st.number_input("Boiler Pressure (MPa)",  min_value=0.0, key="rankine_P2")
    T3 = st.number_input("Turbine Inlet Temperature (°C)",  min_value=0.0, key="rankine_T3")
    eta_t = st.number_input("Turbine Isentropic Efficiency (%)", value=100, key="rankine_eta_t") / 100
    eta_p = st.number_input("Pump Isentropic Efficiency (%)", value=100, key="rankine_eta_p") / 100
    power = st.number_input("Net Power Output (MW)",  min_value=0.0, key="rankine_power")
    m_dot = st.number_input("Mass Flow Rate (kg/s)",  min_value=0.0, key="rankine_mdot")

    # --- Calculate button ---
    if st.button("Solve", key="rankine_solve"):
        # --- State 1: Condenser outlet (saturated liquid) ---
        st1 = IAPWS97(P=P1, x=0)
        h1, s1 = st1.h, st1.s

        # --- Pump (1→2) ---
        st2s = IAPWS97(P=P2, s=s1)
        h2s = st2s.h
        h2 = h1 + (h2s - h1) / (eta_p if eta_p else 1)
        st2 = IAPWS97(P=P2, h=h2)

        # --- State 3: Turbine inlet ---
        st3 = IAPWS97(P=P2, T=T3 + 273.15)
        h3, s3 = st3.h, st3.s

        # --- Turbine (3→4) ---
        st4s = IAPWS97(P=P1, s=s3)
        h4s = st4s.h
        h4 = h3 - eta_t * (h3 - h4s) if eta_t else h4s
        st4 = IAPWS97(P=P1, h=h4)

        # --- Work & efficiency ---
        wp = h2 - h1
        wt = h3 - h4
        wnet = wt - wp
        q_in = h3 - h2
        eff = wnet / q_in

        # --- Mass flow or power ---
        if m_dot == 0 and power > 0:
            m_dot = power * 1000 / wnet
        elif power == 0 and m_dot > 0:
            power = m_dot * wnet / 1000

        # --- Results ---
        st.subheader("Results")
        st.write(f"Thermal Efficiency: {eff*100:.2f} %")
        st.write(f"Specific Work Output: {wnet:.2f} kJ/kg")
        st.write(f"Mass Flow Rate: {m_dot:.2f} kg/s")
        st.write(f"Net Power Output: {power:.2f} MW")

        st.subheader("State Points")
        for i, (P, T, h, s) in enumerate([
            (st1.P, st1.T - 273.15, h1, s1),
            (st2.P, st2.T - 273.15, h2, st2.s),
            (st3.P, st3.T - 273.15, h3, s3),
            (st4.P, st4.T - 273.15, h4, st4.s),
        ], start=1):
            st.write(f"State {i}: P={P:.2f} MPa, T={T:.2f} °C, h={h:.2f} kJ/kg, s={s:.4f} kJ/kg.K")
    else:
        st.info("Enter values and click **Solve** to simulate the cycle.")


# --- Main application entry point ---
def main():
    # Use a dropdown to select the cycle
    cycle_selection = st.selectbox(
        "Select a Thermodynamic Cycle",
        ["Brayton", "Diesel", "Dual", "Otto", "Rankine"]
    )

    # Conditionally call the appropriate function based on the selection
    if cycle_selection == "Brayton":
        brayton_cycle_app()
    elif cycle_selection == "Diesel":
        diesel_cycle_app()
    elif cycle_selection == "Dual":
        dual_cycle_app()
    elif cycle_selection == "Otto":
        otto_cycle_app()
    elif cycle_selection == "Rankine":
        rankine_cycle_app()

if __name__ == "__main__":
    main()

