import streamlit as st

def brayton(cycle, rp, T1, T3, T4=None, eta_c=None, eta_t=None, P_MW=None, m_kgph=None):
    r = {}
    e_c = (eta_c or 100)/100 if cycle == "Actual" else 1
    e_t = (eta_t or 100)/100 if cycle == "Actual" else 1
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
        m = (m_kgph or (P_MW * 1000 / wnet)) / 3600
        P = wnet * m
        r.update(m_kgps=m, P_kW=P, P_MW=P/1000)

    if cycle == "Actual":
        if eta_c is None: r['eta_c'] = (T2s - T1) / (T2a - T1) * 100
        if eta_t is None: r['eta_t'] = (T3 - T4a) / (T3 - T4s) * 100
    return r

def main():
    st.set_page_config(page_title="Brayton Cycle Solver", layout="centered")
    st.title("🔧 Brayton Cycle Solver")

    cycle = st.selectbox("Cycle Type", ["Ideal", "Actual"])
    col1, col2 = st.columns(2)
    with col1:
       T1 = st.number_input("T1 [K]", value=300.0)
       T3 = st.number_input("T3 [K]", value=1200.0)
       rp = st.number_input("Pressure Ratio", value=10.0)
       T4 = st.number_input("T4 [K]", value=0.0) or None
    with col2:
       P_MW = st.number_input("Net Power [MW]", value=0.0) or None
       m_kgph = st.number_input("Mass Flow [kg/hr]", value=0.0) or None
       eta_c = eta_t = None

    if cycle == "Actual":
        eta_c = st.number_input("Compressor η [%]", value=0.0)
        eta_t = st.number_input("Turbine η [%]", value=0.0)

    if st.button("Calculate"):
        r = brayton(cycle, rp, T1, T3, T4, eta_c, eta_t, P_MW, m_kgph)
        for k, v in r.items():
            st.write(f"**{k}**: {v:.2f}")

if __name__ == "__main__":
    main()
