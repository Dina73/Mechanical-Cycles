import streamlit as st
from math import log
from iapws import IAPWS97
from CoolProp.CoolProp import PropsSI

# ================== OTTO ==================
def otto_cycle():
    k = 1.4
    cv = 0.718  # kJ/kg.K
    cp= 1.005   # kJ/kg.K
    R= 0.2871   # kJ/kg.K

    st.subheader("🔧 Otto Cycle Solver")
    col1, col2 = st.columns(2)
    with col1:
        compression_ratio = st.number_input("Compression Ratio (r)", min_value=1.0, key="or")
        heat_added = st.number_input("Heat Added (Qin) [kJ/kg]", min_value=0.0, key="oQ")
    with col2:
        T1 = st.number_input("Initial Temperature T1 [K]", min_value=0.0, key="oT1")
        P1 = st.number_input("Initial Pressure P1 [kPa]", min_value=0.0, key="oP1")

    if st.button("Solve Otto"):
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

        st.subheader("✔️ Otto Results")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Efficiency", f"{efficiency:.2f} %")
        col2.metric("Work Output", f"{work_output:.2f} kJ/kg")
        col3.metric("Heat Rejected", f"{heat_rejected:.2f} kJ/kg")

# ================== DIESEL ==================
def diesel_cycle():
    st.subheader("🔧 Diesel Cycle Solver")

    r = st.number_input("Compression Ratio (r)", min_value=1.0, key="dr")
    rc = st.number_input("Cut-off Ratio (rc)", min_value=1.0, key="drc")
    T1 = st.number_input("Initial Temperature T1 [K]", min_value=0.0, key="dT1")
    P1 = st.number_input("Initial Pressure P1 [kPa]", min_value=0.0, key="dP1")
    Qin = st.number_input("Heat Added (Qin) [kJ/kg]", min_value=0.0, key="dQ")

    if st.button("Solve Diesel"):
        k, cv, cp, R = 1.4, 0.718, 1.005, 0.2871
        V1 = (R*T1)/P1; V2 = V1/r
        P2 = P1*((r)**k); T2 = T1*(r**(k-1))
        V3 = rc*V2; T3 = T2+(Qin/cv); P3 = (R*T3)/V3
        V4 = V1; T4 = T3*((1/rc)**(k-1)); P4=(R*T4)/V4
        Qout = cv*(T4-T1); Wnet=Qin-Qout; eff=(Wnet/Qin)*100

        st.subheader("✔️ Diesel Results")
        st.metric("Efficiency", f"{eff:.2f} %")
        st.metric("Net Work", f"{Wnet:.2f} kJ/kg")

# ================== DUAL ==================
def dual_cycle():
    st.subheader("🔧 Dual Cycle Solver")

    r = st.number_input("Compression Ratio (r)", min_value=1.0, key="ur")
    rc = st.number_input("Cut-off Ratio (rc)", min_value=1.0, key="urc")
    rp = st.number_input("Pressure Ratio (rp)", min_value=1.0, key="urp")
    T1 = st.number_input("Initial Temperature T1 [K]", min_value=0.0, key="uT1")
    P1 = st.number_input("Initial Pressure P1 [kPa]", min_value=0.0, key="uP1")
    Qin = st.number_input("Heat Added (Qin) [kJ/kg]", min_value=0.0, key="uQ")

    if st.button("Solve Dual"):
        k, cv, cp, R = 1.4, 0.718, 1.005, 0.2871
        V1=(R*T1)/P1; V2=V1/r
        P2=P1*((r)**k); T2=T1*(r**(k-1))
        V3=V2; P3=rp*P2; T3=T2*(rp**((k-1)/k))
        V4=rc*V3; T4=T3+(Qin/cv); P4=(R*T4)/V4
        V5=V1; T5=T4*((1/rc)**(k-1)); P5=(R*T5)/V5
        Qout=cv*(T5-T1); Wnet=Qin-Qout; eff=(Wnet/Qin)*100

        st.subheader("✔️ Dual Results")
        st.metric("Efficiency", f"{eff:.2f} %")
        st.metric("Net Work", f"{Wnet:.2f} kJ/kg")

# ================== BRAYTON ==================
def brayton_cycle():
    st.subheader("🔧 Brayton Cycle Solver")
    cycle = st.selectbox("Cycle Type", ["Ideal", "Actual"], key="brtype")
    T1 = st.number_input("T1 [K]", 0.0, key="bT1")
    T3 = st.number_input("T3 [K]", 0.0, key="bT3")
    rp = st.number_input("Pressure Ratio", 0.0, key="brp")

    if st.button("Solve Brayton"):
        k, cp = 1.4, 1.005
        T2s = T1 * rp ** ((k - 1) / k); T4s = T3 / rp ** ((k - 1) / k)
        Wc, Wt = cp * (T2s - T1), cp * (T3 - T4s)
        Wnet, Qin, Qout = Wt - Wc, cp * (T3 - T2s), cp * (T4s - T1)
        eff = (Wnet / Qin) * 100

        st.subheader("✔️ Brayton Results")
        st.metric("Efficiency", f"{eff:.2f} %")
        st.metric("Net Work", f"{Wnet:.2f} kJ/kg")

# ================== RANKINE ==================
def rankine_cycle():
    st.subheader("♨️ Rankine Cycle Solver (Ideal & Actual)")
    P1 = st.number_input("Condenser Pressure (MPa)", 0.01, 1.0, 0.01, key="rP1")
    P2 = st.number_input("Boiler Pressure (MPa)", 1.0, 20.0, 0.1, key="rP2")
    T3 = st.number_input("Turbine Inlet Temp (°C)", 100.0, 600.0, 1.0, key="rT3")

    if st.button("Solve Rankine"):
        # Ideal cycle
        s1 = IAPWS97(P=P1, x=0).s; h1 = IAPWS97(P=P1, x=0).h
        s2s = s1; h2s = IAPWS97(P=P2, s=s1).h
        h2 = h2s; v1 = IAPWS97(P=P1, x=0).v
        wp = v1*(P2-P1)*1000; h2 = h1+wp/1000
        h3 = IAPWS97(P=P2, T=T3+273.15).h
        s3 = IAPWS97(P=P2, T=T3+273.15).s
        s4s = s3; h4s = IAPWS97(P=P1, s=s3).h
        h4 = h4s
        wt = h3-h4; qin = h3-h2; eff = (wt-wp)/qin*100

        st.subheader("✔️ Rankine Results")
        st.metric("Efficiency", f"{eff:.2f} %")
        st.metric("Turbine Work", f"{wt:.2f} kJ/kg")
        st.metric("Pump Work", f"{wp:.2f} kJ/kg")

# ================== MAIN APP ==================
def main():
    st.set_page_config(page_title="Thermodynamic Cycle Simulator", layout="centered")
    st.title("♨️ Thermodynamic Cycle Simulator")

    cycle = st.selectbox("Select Cycle", 
                         ["Otto", "Diesel", "Dual", "Brayton", "Rankine"])

    if cycle == "Otto":
        otto_cycle()
    elif cycle == "Diesel":
        diesel_cycle()
    elif cycle == "Dual":
        dual_cycle()
    elif cycle == "Brayton":
        brayton_cycle()
    elif cycle == "Rankine":
        rankine_cycle()

if __name__ == "__main__":
    main()
