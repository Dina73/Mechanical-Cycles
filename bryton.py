import streamlit as st
import numpy as np

def calculate_brayton_cycle(
    cycle_type,
    r_p=None,
    T1=None,
    T3=None,
    T4_actual=None,
    eta_c_input=None, # Renamed to avoid confusion with calculated
    eta_t_input=None, # Renamed to avoid confusion with calculated
    net_power_MW=None,
    mass_flow_kgph=None,
    cp=1.005, # Default cp for air
    k=1.4 # Default k for air
):
    """
    Calculates Brayton Cycle parameters based on available inputs.
    It attempts to deduce unknowns if enough information is provided.

    Args:
        cycle_type (str): "Ideal" or "Actual".
        r_p (float, optional): Pressure Ratio (P2/P1).
        T1 (float, optional): Compressor Inlet Temperature T1 [K].
        T3 (float, optional): Turbine Inlet Temperature T3 [K].
        T4_actual (float, optional): Actual Turbine Exhaust Temperature T4 [K].
        eta_c_input (float, optional): Compressor Isentropic Efficiency [%].
        eta_t_input (float, optional): Turbine Isentropic Efficiency [%].
        net_power_MW (float, optional): Net power output in MW.
        mass_flow_kgph (float, optional): Mass flow rate in kg/hr.
        cp (float): Specific heat at constant pressure [kJ/kg.K]. Defaults to 1.005 for air.
        k (float): Specific heat ratio. Defaults to 1.4 for air.

    Returns:
        dict: A dictionary containing calculated results and an error message if unsolvable.
    """
    results = {"error": None}

    # Initialize efficiencies for calculations
    eta_c_dec = (eta_c_input / 100.0) if eta_c_input is not None else 1.0
    eta_t_dec = (eta_t_input / 100.0) if eta_t_input is not None else 1.0

    # Ensure efficiencies are 100% for Ideal cycle type
    if cycle_type == "Ideal":
        eta_c_dec = 1.0
        eta_t_dec = 1.0

    # Initialize all calculated parameters to None
    T2s = None
    T4s = None
    T2a = None
    T4a = None
    w_c_s = None # Isentropic compressor work
    w_t_s = None # Isentropic turbine work
    w_c_a = None # Actual compressor work
    w_t_a = None # Actual turbine work
    w_net = None
    q_in = None
    q_out = None
    thermal_efficiency = None
    calculated_eta_c = None
    calculated_eta_t = None
    calculated_mass_flow_kgs = None
    calculated_net_power_kW = None

    # --- Step 1: Calculate Isentropic Temperatures (T2s, T4s) if possible ---
    if T1 is not None and r_p is not None:
        try:
            T2s = T1 * (r_p ** ((k - 1) / k))
            results['T2s'] = T2s
        except Exception as e:
            results['error'] = f"Could not calculate T2s: {e}"
            return results

    if T3 is not None and r_p is not None:
        try:
            T4s = T3 * ((1 / r_p) ** ((k - 1) / k))
            results['T4s'] = T4s
        except Exception as e:
            results['error'] = f"Could not calculate T4s: {e}"
            return results

    # --- Step 2: Determine Actual Temperatures (T2a, T4a) and Efficiencies ---

    # Case 1: Efficiencies are known (or Ideal cycle)
    if cycle_type == "Ideal" or (eta_c_input is not None and eta_t_input is not None):
        if T2s is not None and T1 is not None and eta_c_dec > 0:
            T2a = T1 + (T2s - T1) / eta_c_dec
            results['T2a'] = T2a
        elif T2s is None and T1 is not None and T2a is not None and eta_c_dec > 0:
            # If T2a is somehow known but T2s wasn't, but we have efficiency, reverse
            T2s = T1 + (T2a - T1) * eta_c_dec
            results['T2s'] = T2s

        if T4s is not None and T3 is not None and eta_t_dec > 0:
            T4a = T3 - (T3 - T4s) * eta_t_dec
            results['T4a'] = T4a
        elif T4s is None and T3 is not None and T4a is not None and eta_t_dec > 0:
            # If T4a is somehow known but T4s wasn't, but we have efficiency, reverse
            T4s = T3 - (T3 - T4a) / eta_t_dec
            results['T4s'] = T4s

    # Case 2: T4_actual is known, and eta_t might be unknown
    elif T4_actual is not None:
        T4a = T4_actual
        results['T4a'] = T4a
        if T3 is not None and T4s is not None:
            if (T3 - T4s) != 0:
                calculated_eta_t = (T3 - T4a) / (T3 - T4s) * 100
                results['calculated_eta_t'] = calculated_eta_t
                eta_t_dec = calculated_eta_t / 100.0 # Use calculated for further steps
            else:
                results['error'] = "Cannot calculate turbine efficiency: (T3 - T4s) is zero."

    # --- Step 3: Calculate Work Terms (isentropic and actual) ---
    if T1 is not None and T2s is not None:
        w_c_s = cp * (T2s - T1)
        results['w_c_s'] = w_c_s
    if T3 is not None and T4s is not None:
        w_t_s = cp * (T3 - T4s)
        results['w_t_s'] = w_t_s

    # Actual work calculations (using actual temperatures if available, or efficiencies)
    if T1 is not None and T2a is not None:
        w_c_a = cp * (T2a - T1)
        results['w_c_a'] = w_c_a
    elif w_c_s is not None and eta_c_dec > 0:
        w_c_a = w_c_s / eta_c_dec # w_c_a = (h2s - h1) / eta_c = w_c_s / eta_c
        if T1 is not None and cp != 0:
            T2a = T1 + w_c_a / cp
            results['T2a'] = T2a
        results['w_c_a'] = w_c_a

    if T3 is not None and T4a is not None:
        w_t_a = cp * (T3 - T4a)
        results['w_t_a'] = w_t_a
    elif w_t_s is not None and eta_t_dec > 0:
        w_t_a = w_t_s * eta_t_dec # w_t_a = eta_t * (h3 - h4s) = eta_t * w_t_s
        if T3 is not None and cp != 0:
            T4a = T3 - w_t_a / cp
            results['T4a'] = T4a
        results['w_t_a'] = w_t_a

    # Net Work Calculation
    if w_t_a is not None and w_c_a is not None:
        w_net = w_t_a - w_c_a
        results['w_net'] = w_net

    # Heat Transfer Calculations
    if T3 is not None and T2a is not None:
        q_in = cp * (T3 - T2a)
        results['q_in'] = q_in
    if T4a is not None and T1 is not None:
        q_out = cp * (T4a - T1)
        results['q_out'] = q_out

    # Thermal Efficiency Calculation
    if w_net is not None and q_in is not None and q_in != 0:
        thermal_efficiency = (w_net / q_in) * 100
        results['thermal_efficiency'] = thermal_efficiency
    elif q_in is not None and q_out is not None and q_in != 0:
        thermal_efficiency = (1 - (q_out / q_in)) * 100
        results['thermal_efficiency'] = thermal_efficiency

    # --- Step 4: Handle cases where net_power_MW or mass_flow_kgph are given ---
    # These often help find specific work or unknown efficiencies

    # If total power is given, but mass flow is unknown, and specific net work is known
    # Or, if specific net work is unknown, and mass flow and total power are given
    if net_power_MW is not None and mass_flow_kgph is not None:
        calculated_mass_flow_kgs = mass_flow_kgph / 3600 # Convert to kg/s
        calculated_net_power_kW = net_power_MW * 1000 # Convert to kW (kJ/s)
        results['mass_flow_kgs'] = calculated_mass_flow_kgs
        results['net_power_kW'] = calculated_net_power_kW

        if calculated_mass_flow_kgs != 0:
            derived_w_net = calculated_net_power_kW / calculated_mass_flow_kgs
            results['derived_w_net'] = derived_w_net

            # If we calculated w_net from temperatures, compare or use this to derive
            if w_net is None: # If specific work wasn't determined yet
                w_net = derived_w_net
                results['w_net'] = w_net

    # If specific net work is known (either derived or calculated from temps)
    # and total net power is known, calculate mass flow rate
    if w_net is not None and net_power_MW is not None and mass_flow_kgph is None:
        calculated_net_power_kW = net_power_MW * 1000
        if w_net != 0:
            calculated_mass_flow_kgs = calculated_net_power_kW / w_net
            results['mass_flow_kgs'] = calculated_mass_flow_kgs
            results['mass_flow_kgph'] = calculated_mass_flow_kgs * 3600 # Also provide in kg/hr
        else:
            results['error'] = "Cannot calculate mass flow rate: Net work is zero."

    # If specific net work is known (either derived or calculated from temps)
    # and mass flow rate is known, calculate total net power
    if w_net is not None and mass_flow_kgph is not None and net_power_MW is None:
        calculated_mass_flow_kgs = mass_flow_kgph / 3600
        calculated_net_power_kW = w_net * calculated_mass_flow_kgs
        results['net_power_kW'] = calculated_net_power_kW
        results['net_power_MW'] = calculated_net_power_kW / 1000 # Also provide in MW

    # Handle cases where an efficiency might be the unknown
    # This part gets tricky and requires specific input combinations
    # For instance, if T1, T3, T4a, r_p, and net_power_MW/mass_flow are known,
    # we can deduce w_net, then w_c_a, then T2a, then eta_c.
    if cycle_type == "Actual" and T1 is not None and T3 is not None and r_p is not None:
        # Check if eta_c is missing but T2a (or derived w_c_a) can be found
        if eta_c_input is None and T2a is not None and T2s is not None:
            if (T2a - T1) != 0:
                calculated_eta_c = (T2s - T1) / (T2a - T1) * 100
                results['calculated_eta_c'] = calculated_eta_c
            else:
                results['error'] = "Cannot calculate compressor efficiency: (T2a - T1) is zero."

        # Check if eta_t is missing but T4a (or derived w_t_a) can be found
        if eta_t_input is None and T4a is not None and T4s is not None:
            if (T3 - T4s) != 0:
                calculated_eta_t = (T3 - T4a) / (T3 - T4s) * 100
                results['calculated_eta_t'] = calculated_eta_t
            else:
                results['error'] = "Cannot calculate turbine efficiency: (T3 - T4s) is zero."

        # If T1, T3, T4a, r_p, net_power_MW, mass_flow are known (Problem 2 scenario):
        if (T4_actual is not None and net_power_MW is not None and mass_flow_kgph is not None
            and eta_c_input is None and eta_t_input is None):
            # Recalculate based on specific knowns to solve for efficiencies
            if calculated_net_power_kW is not None and calculated_mass_flow_kgs is not None and calculated_mass_flow_kgs != 0:
                derived_w_net_from_power = calculated_net_power_kW / calculated_mass_flow_kgs
                w_t_a_from_T4a = cp * (T3 - T4_actual) # Actual turbine work from given T4a
                w_c_a_derived = w_t_a_from_T4a - derived_w_net_from_power # Derived actual compressor work

                if T1 is not None and cp != 0:
                    derived_T2a = T1 + w_c_a_derived / cp
                    results['derived_T2a'] = derived_T2a # For debugging/display
                    if T2s is not None and (derived_T2a - T1) != 0:
                        calculated_eta_c = (T2s - T1) / (derived_T2a - T1) * 100
                        results['calculated_eta_c'] = calculated_eta_c
                    else:
                        results['error'] = "Cannot calculate compressor efficiency for this scenario."
                else:
                    results['error'] = "Insufficient data to derive T2a for compressor efficiency calculation."


    results['T1'] = T1
    results['T3'] = T3
    results['r_p'] = r_p
    results['cycle_type'] = cycle_type
    results['input_eta_c'] = eta_c_input
    results['input_eta_t'] = eta_t_input

    # Clean up results for display, only include non-None values
    final_results = {k: v for k, v in results.items() if v is not None}
    return final_results

def main():
    st.set_page_config(page_title="Generic Brayton Cycle Solver", layout="centered")
    st.title("🔧 Generic Brayton Cycle Solver")
    st.markdown("Enter the known parameters below. The solver will calculate the rest.")

    # User selects cycle type
    cycle_type = st.selectbox("Cycle Type", ["Ideal", "Actual"], help="Select 'Ideal' for 100% efficient components.")

    st.markdown("### Primary Inputs")
    col1, col2, col3 = st.columns(3)
    with col1:
        T1 = st.number_input("Compressor Inlet Temp T1 [K]", min_value=0.0, format="%.2f", help="Temperature at state 1 (compressor inlet)", value=None if cycle_type == "Actual" else 300.0)
    with col2:
        T3 = st.number_input("Turbine Inlet Temp T3 [K]", min_value=0.0, format="%.2f", help="Temperature at state 3 (turbine inlet)", value=None if cycle_type == "Actual" else 1200.0)
    with col3:
        r_p = st.number_input("Pressure Ratio (P2/P1)", min_value=1.0, format="%.2f", help="Ratio of high to low pressure in the cycle", value=10.0)

    st.markdown("### Secondary Inputs (Optional - provide if known)")
    col4, col5 = st.columns(2)
    with col4:
        T4_actual = st.number_input("Actual Turbine Exhaust Temp T4 [K]", min_value=0.0, format="%.2f", help="Temperature at state 4 (turbine exhaust). Leave empty if unknown.", value=None)
    with col5:
        net_power_MW = st.number_input("Net Power Output [MW]", min_value=0.0, format="%.2f", help="Total net power produced by the cycle. Leave empty if unknown.", value=None)

    col6, col7 = st.columns(2)
    with col6:
        mass_flow_kgph = st.number_input("Mass Flow Rate [kg/hr]", min_value=0.0, format="%.2f", help="Mass flow rate of air through the cycle. Leave empty if unknown.", value=None)

    # Efficiencies only for Actual cycle
    eta_c_input = None
    eta_t_input = None
    if cycle_type == "Actual":
        st.markdown("### Efficiencies (for Actual Cycle)")
        st.write("Provide these if known. If left empty and sufficient other data is given, they might be calculated.")
        col_eff1, col_eff2 = st.columns(2)
        with col_eff1:
            eta_c_input = st.number_input("Compressor Efficiency [%]", min_value=0.0, max_value=100.0, format="%.2f", help="Isentropic efficiency of the compressor. Enter 100 for ideal compressor.", value=None)
        with col_eff2:
            eta_t_input = st.number_input("Turbine Efficiency [%]", min_value=0.0, max_value=100.0, format="%.2f", help="Isentropic efficiency of the turbine. Enter 100 for ideal turbine.", value=None)

    st.markdown("### Fluid Properties")
    col_prop1, col_prop2 = st.columns(2)
    with col_prop1:
        cp_val = st.number_input("Specific Heat Cp [kJ/kg.K]", value=1.005, format="%.3f", help="Specific heat at constant pressure for the working fluid (air).")
    with col_prop2:
        k_val = st.number_input("Specific Heat Ratio k (gamma)", value=1.4, format="%.2f", help="Ratio of specific heats for the working fluid (air).")

    if st.button("Calculate Brayton Cycle"):
        if T1 is None or T3 is None or r_p is None:
            st.warning("Please provide at least Compressor Inlet Temp (T1), Turbine Inlet Temp (T3), and Pressure Ratio (P2/P1) for basic calculations.")
        else:
            with st.spinner("Calculating..."):
                results = calculate_brayton_cycle(
                    cycle_type=cycle_type,
                    r_p=r_p,
                    T1=T1,
                    T3=T3,
                    T4_actual=T4_actual,
                    eta_c_input=eta_c_input,
                    eta_t_input=eta_t_input,
                    net_power_MW=net_power_MW,
                    mass_flow_kgph=mass_flow_kgph,
                    cp=cp_val,
                    k=k_val
                )

            if results.get("error"):
                st.error(f"Calculation Error: {results['error']}")
            else:
                st.subheader("✅ Calculation Results")

                # Input Parameters Summary
                st.markdown("#### Input Parameters Summary")
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                col_sum1.metric("Cycle Type", results.get('cycle_type', 'N/A'))
                col_sum2.metric("T1 [K]", f"{results['T1']:.2f}")
                col_sum3.metric("T3 [K]", f"{results['T3']:.2f}")

                col_sum4, col_sum5, col_sum6 = st.columns(3)
                col_sum4.metric("Pressure Ratio (rp)", f"{results['r_p']:.2f}")
                if 'input_eta_c' in results and results['input_eta_c'] is not None:
                    col_sum5.metric("Input $\\eta_c$ [%]", f"{results['input_eta_c']:.2f}")
                if 'input_eta_t' in results and results['input_eta_t'] is not None:
                    col_sum6.metric("Input $\\eta_t$ [%]", f"{results['input_eta_t']:.2f}")

                # Display Results
                st.markdown("#### Temperatures")
                col_t1, col_t2, col_t3, col_t4 = st.columns(4)
                if 'T2s' in results: col_t1.metric("T2s [K]", f"{results['T2s']:.2f}")
                if 'T2a' in results: col_t2.metric("T2a [K]", f"{results['T2a']:.2f}")
                if 'T4s' in results: col_t3.metric("T4s [K]", f"{results['T4s']:.2f}")
                if 'T4a' in results: col_t4.metric("T4a [K]", f"{results['T4a']:.2f}")

                st.markdown("#### Specific Work & Heat (per unit mass)")
                col_wh1, col_wh2, col_wh3 = st.columns(3)
                if 'w_c_a' in results: col_wh1.metric("Compressor Work ($w_c$) [kJ/kg]", f"{results['w_c_a']:.2f}")
                if 'w_t_a' in results: col_wh2.metric("Turbine Work ($w_t$) [kJ/kg]", f"{results['w_t_a']:.2f}")
                if 'w_net' in results: col_wh3.metric("Net Work ($w_{net}$) [kJ/kg]", f"{results['w_net']:.2f}")

                col_wh4, col_wh5 = st.columns(2)
                if 'q_in' in results: col_wh4.metric("Heat Added ($q_{in}$) [kJ/kg]", f"{results['q_in']:.2f}")
                if 'q_out' in results: col_wh5.metric("Heat Rejected ($q_{out}$) [kJ/kg]", f"{results['q_out']:.2f}")

                st.markdown("#### Efficiencies & Performance")
                col_eff_out1, col_eff_out2, col_eff_out3 = st.columns(3)
                if 'calculated_eta_c' in results:
                    col_eff_out1.metric("Calculated $\\eta_c$ [%]", f"{results['calculated_eta_c']:.2f}")
                elif results.get('input_eta_c') is not None: # Display input if not calculated
                    col_eff_out1.metric("Input $\\eta_c$ [%]", f"{results['input_eta_c']:.2f}")
                elif cycle_type == "Ideal":
                    col_eff_out1.metric("$\\eta_c$ (Ideal)", "100.00%")


                if 'calculated_eta_t' in results:
                    col_eff_out2.metric("Calculated $\\eta_t$ [%]", f"{results['calculated_eta_t']:.2f}")
                elif results.get('input_eta_t') is not None: # Display input if not calculated
                    col_eff_out2.metric("Input $\\eta_t$ [%]", f"{results['input_eta_t']:.2f}")
                elif cycle_type == "Ideal":
                    col_eff_out2.metric("$\\eta_t$ (Ideal)", "100.00%")

                if 'thermal_efficiency' in results:
                    col_eff_out3.metric("Thermal Efficiency [%]", f"{results['thermal_efficiency']:.2f}")

                st.markdown("#### Total Power & Mass Flow")
                col_power1, col_power2 = st.columns(2)
                if 'mass_flow_kgs' in results:
                    col_power1.metric("Mass Flow Rate [kg/s]", f"{results['mass_flow_kgs']:.2f}")
                if 'mass_flow_kgph' in results: # Display if it was calculated from kg/s
                     col_power1.metric("Mass Flow Rate [kg/hr]", f"{results['mass_flow_kgph']:.2f}")

                if 'net_power_kW' in results:
                    col_power2.metric("Net Power Output [kW]", f"{results['net_power_kW']:.2f}")
                if 'net_power_MW' in results: # Display if it was calculated from kW
                    col_power2.metric("Net Power Output [MW]", f"{results['net_power_MW']:.2f}")


    st.info("💡 **How it works:** Provide the values you know. The solver will attempt to calculate the unknown parameters. For an 'Actual' cycle, if efficiencies are not provided, but the actual exhaust temperature (T4) and/or net power/mass flow are known, the solver may be able to deduce the efficiencies. If you only provide T1, T3, and pressure ratio, it will give you the ideal cycle results or require efficiencies for an actual cycle.")


if __name__ == "__main__":
    main()
