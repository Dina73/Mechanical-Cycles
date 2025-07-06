import streamlit as st
import math

def otto_cycle():
    print("Otto Cycle Calculator")
    print("------------------------")

    # Get user input
    compression_ratio = st.number_input("Enter compression ratio (r): "))
    heat_added =st.number_input("Enter heat added (Qh) in kJ/kg: ")
    gamma = st.number_input("Enter adiabatic index (γ) (default=1.4): ")
    T1 = st.number_input("Enter initial temperature (T1) in K (default=300): ")

    # Calculate efficiency
    efficiency = 1 - (1 / (compression_ratio ** (gamma - 1)))

    # Calculate temperatures
    T2 = T1 * (compression_ratio ** (gamma - 1))
    T3 = T2 + heat_added / (0.718 * 1000)  # Assume specific heat capacity at constant volume
    T4 = T3 / (compression_ratio ** (gamma - 1))

    # Calculate work output
    work_output = heat_added * efficiency

    # Calculate heat rejected
    heat_rejected = heat_added - work_output

    # Print results
    print("\nResults:")
    st.write(f"Efficiency: {efficiency:.2f}")
    st.write(f"Work output: {work_output:.2f} kJ/kg")
    st.write(f"Heat rejected: {heat_rejected:.2f} kJ/kg")
    st.write(f"Temperature 1: {T1} K")
    st.write(f"Temperature 2: {T2:.2f} K")
    st.write(f"Temperature 3: {T3:.2f} K")
    st.write(f"Temperature 4: {T4:.2f} K")

otto_cycle()
