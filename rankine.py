# A Streamlit application to solve a generic Rankine Cycle problem.
# This app calculates thermal efficiency, specific work, and mass flow rate.

# Import necessary libraries
import streamlit as st
from CoolProp.CoolProp import PropsSI
import pandas as pd

# Set up the Streamlit page
st.set_page_config(layout="wide", page_title="Generic Rankine Cycle Solver")

st.title("👨‍🔬 Generic Rankine Cycle Solver")
st.markdown("""
This application helps you analyze a simple Rankine cycle. Enter the parameters
for the cycle below to get the thermodynamic properties at each state, as well as the
overall cycle performance.
""")

st.markdown("---")

# Use a sidebar for all inputs
with st.sidebar:
    st.header("Cycle Parameters")
    st.markdown("All pressures in MPa, temperatures in °C.")

    # Boiler and Turbine Inlet (State 1)
    st.subheader("Boiler & Turbine Inlet (State 1)")
    p1 = st.number_input("Pressure at Turbine Inlet ($P_1$)", value=10.0, min_value=0.1, step=0.1, format="%.2f")
    t1 = st.number_input("Temperature at Turbine Inlet ($T_1$)", value=500.0, min_value=0.0, step=1.0, format="%.1f")

    st.markdown("---")

    # Condenser & Pump Inlet (State 2 & 3)
    st.subheader("Condenser & Pump Inlet (State 2 & 3)")
    p2 = st.number_input("Condenser Pressure ($P_2=P_3$)", value=0.01, min_value=0.001, step=0.001, format="%.3f")
    turbine_efficiency = st.slider("Turbine Isentropic Efficiency ($\eta_t$)", min_value=0.0, max_value=1.0, value=1.0, step=0.01)
    pump_efficiency = st.slider("Pump Isentropic Efficiency ($\eta_p$)", min_value=0.0, max_value=1.0, value=1.0, step=0.01)

    st.markdown("---")

    # Optional Inputs
    st.subheader("Optional Inputs")
    net_power_output = st.number_input("Net Power Output (MW) - Optional", value=0.0, min_value=0.0, step=1.0)
    
    st.info("Set net power output > 0 to calculate mass flow rate.")

# Convert units for CoolProp (Pa and K)
P1 = p1 * 1e6
T1 = t1 + 273.15
P2 = p2 * 1e6

try:
    # --- State 1: Turbine Inlet (Superheated Steam) ---
    h1 = PropsSI('H', 'P', P1, 'T', T1, 'Water')
    s1 = PropsSI('S', 'P', P1, 'T', T1, 'Water')
    T1_sat = PropsSI('T', 'P', P1, 'Q', 0, 'Water') - 273.15
    h1_units = h1 / 1e3
    s1_units = s1 / 1e3

    # --- State 2: Turbine Outlet (Isentropic expansion) ---
    s2s = s1
    # Check if the turbine outlet is saturated or superheated to get the correct enthalpy.
    try:
        h2s = PropsSI('H', 'P', P2, 'S', s2s, 'Water')
        x2s = PropsSI('Q', 'P', P2, 'S', s2s, 'Water')
    except ValueError:
        # Sometimes CoolProp can't find a valid quality, this is okay.
        x2s = None
    
    h2s_units = h2s / 1e3

    # Actual turbine work
    wt = turbine_efficiency * (h1 - h2s)
    h2 = h1 - wt
    h2_units = h2 / 1e3
    wt_units = wt / 1e3

    # --- State 3: Pump Inlet (Saturated Liquid) ---
    h3 = PropsSI('H', 'P', P2, 'Q', 0, 'Water')
    s3 = PropsSI('S', 'P', P2, 'Q', 0, 'Water')
    v3 = PropsSI('V', 'P', P2, 'Q', 0, 'Water')
    h3_units = h3 / 1e3
    s3_units = s3 / 1e3
    v3_units = v3

    # --- State 4: Pump Outlet (Isentropic Compression) ---
    # Pump work is approximately v3 * (P1 - P2)
    wp_isentropic = v3 * (P1 - P2)
    
    if pump_efficiency > 0:
        wp = wp_isentropic / pump_efficiency
    else:
        wp = wp_isentropic # In case efficiency is 0, we'll assume isentropic
    
    h4 = h3 + wp
    h4_units = h4 / 1e3
    wp_units = wp / 1e3

    # --- Cycle Performance Calculations ---
    # Specific Heat Input (kJ/kg)
    qin = h1 - h4
    qin_units = qin / 1e3

    # Net specific work (kJ/kg)
    wnet = wt - wp
    wnet_units = wnet / 1e3

    # Thermal Efficiency (%)
    thermal_efficiency = (wnet / qin) * 100

    # Mass Flow Rate (kg/s)
    mass_flow_rate = 0
    if net_power_output > 0 and wnet > 0:
        mass_flow_rate = (net_power_output * 1e6) / wnet

    # --- Display Results ---
    st.header("Results")
    
    st.subheader("Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Thermal Efficiency ($\eta_{th}$)", f"{thermal_efficiency:.2f} %")
    with col2:
        st.metric("Net Specific Work ($w_{net}$)", f"{wnet_units:.2f} kJ/kg")
    with col3:
        if mass_flow_rate > 0:
            st.metric("Mass Flow Rate ($\dot{m}$)", f"{mass_flow_rate:.2f} kg/s")
        else:
            st.info("Enter net power to see mass flow rate.")

    st.markdown("---")
    
    st.subheader("Thermodynamic Properties at Each State")
    st.markdown("All enthalpy (h) and entropy (s) values are in kJ/kg and kJ/(kg·K) respectively.")
    
    state_data = {
        "State": ["1: Turbine Inlet", "2: Turbine Outlet", "3: Pump Inlet", "4: Pump Outlet"],
        "Pressure (MPa)": [p1, p2, p2, p1],
        "Temperature (°C)": [t1, (PropsSI('T', 'P', P2, 'H', h2, 'Water') - 273.15), PropsSI('T', 'P', P2, 'Q', 0, 'Water') - 273.15, (PropsSI('T', 'P', P1, 'H', h4, 'Water') - 273.15)],
        "Enthalpy (h)": [h1_units, h2_units, h3_units, h4_units],
        "Entropy (s)": [s1_units, (PropsSI('S', 'P', P2, 'H', h2, 'Water') / 1e3), s3_units, (PropsSI('S', 'P', P1, 'H', h4, 'Water') / 1e3)]
    }
    st.dataframe(pd.DataFrame(state_data).set_index("State"))
    
    st.markdown("---")

    st.subheader("Component Work and Heat Transfer")
    colA, colB, colC = st.columns(3)
    with colA:
        st.metric("Specific Turbine Work ($w_t$)", f"{wt_units:.2f} kJ/kg")
    with colB:
        st.metric("Specific Pump Work ($w_p$)", f"{wp_units:.2f} kJ/kg")
    with colC:
        st.metric("Specific Heat Input ($q_{in}$)", f"{qin_units:.2f} kJ/kg")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.warning("Please ensure your inputs are physically realistic. For example, the turbine inlet temperature must be high enough for the given pressure.")

