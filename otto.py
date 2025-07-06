import streamlit as st
import math

def main():
    st.title("Otto Cycle Calculator")

    # Constant
    gamma = 1.4

    # Get user input
    compression_ratio = st.number_input("Enter compression ratio (r): ", min_value=1.0, value=8.0)
    heat_added = st.number_input("Enter heat added (Qh) in kJ/kg: ", min_value=0.0, value=1000.0)
    T1 = st.number_input("Enter initial temperature (T1) in K: ", value=300.0, min_value=0.0)

    if st.button("Calculate"):
        # Calculate efficiency
        efficiency = 1 - (1 / (compression_ratio ** (gamma - 1)))

        # Calculate temperatures
        T2 = T1 * (compression_ratio ** (gamma - 1))
        T3 = T2 + heat_added / 0.718  # Assume specific heat capacity at constant volume
        T4 = T3 / (compression_ratio ** (gamma - 1))

        # Calculate work output
        work_output = heat_added * efficiency

        # Calculate heat rejected
        heat_rejected = heat_added - work_output

        # Print results
        st.write("Results:")
        col1, col2 = st.columns(2)
        col1.metric("Efficiency", f"{efficiency:.2f}")
        col2.metric("Work Output", f"{work_output:.2f} kJ/kg")
        col1.metric("Heat Rejected", f"{heat_rejected:.2f} kJ/kg")
        col2.metric("Temperature 1", f"{T1} K")
        col1.metric("Temperature 2", f"{T2:.2f} K")
        col2.metric("Temperature 3", f"{T3:.2f} K")
        col1.metric("Temperature 4", f"{T4:.2f} K")

streamlit run app.py
