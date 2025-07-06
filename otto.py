import math

def otto_cycle():
    print("Otto Cycle Calculator")
    print("------------------------")

    # Get user input
    compression_ratio = float(input("Enter compression ratio (r): "))
    heat_added = float(input("Enter heat added (Qh) in kJ/kg: "))
    gamma = float(input("Enter adiabatic index (γ) (default=1.4): ") or 1.4)
    T1 = float(input("Enter initial temperature (T1) in K (default=300): ") or 300)

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
    print(f"Efficiency: {efficiency:.2f}")
    print(f"Work output: {work_output:.2f} kJ/kg")
    print(f"Heat rejected: {heat_rejected:.2f} kJ/kg")
    print(f"Temperature 1: {T1} K")
    print(f"Temperature 2: {T2:.2f} K")
    print(f"Temperature 3: {T3:.2f} K")
    print(f"Temperature 4: {T4:.2f} K")

otto_cycle()