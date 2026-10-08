import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from beam_solver.solver import Beam, Support, PointLoad, DistributedLoad
from beam_solver.report import generate_pdf_report

st.set_page_config(
    page_title="BeamSolver Pro | Structural Analysis",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Engineering Theme
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric {
        background: linear-gradient(135deg, #1e2530 0%, #151a21 100%);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2d3748;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .metric-title { font-size: 0.9rem; color: #a0aec0; font-weight: 500; }
    .metric-value { font-size: 1.6rem; color: #63b3ed; font-weight: 700; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
        background: linear-gradient(90deg, #3182ce 0%, #2b6cb0 100%);
        border: none;
        box-shadow: 0 4px 12px rgba(49, 130, 206, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/structural.png", width=64)
    st.title("Beam Parameters")
    st.markdown("---")
    
    st.subheader("📐 Geometry & Section")
    length = st.number_input("Span Length $L$ (m)", min_value=1.0, max_value=50.0, value=6.0, step=0.5)
    e_gpa = st.number_input("Modulus of Elasticity $E$ (GPa)", min_value=1.0, value=200.0, step=10.0)
    inertia_cm4 = st.number_input("Moment of Inertia $I$ (cm⁴)", min_value=1.0, value=5000.0, step=50.0)
    
    e_mod = e_gpa * 1e9
    inertia = inertia_cm4 * 1e-8

    st.markdown("---")
    st.subheader("📍 Boundary Conditions")
    sup1_pos = st.number_input("Left Pin Support $x_1$ (m)", min_value=0.0, max_value=length, value=0.0, step=0.5)
    sup2_pos = st.number_input("Right Roller Support $x_2$ (m)", min_value=0.0, max_value=length, value=length, step=0.5)

    st.markdown("---")
    st.subheader("⚡ Applied Loads")
    p_load_kn = st.number_input("Point Load $P$ (kN)", value=10.0, step=1.0)
    p_pos = st.number_input("Point Load Position $x_p$ (m)", min_value=0.0, max_value=length, value=length / 2, step=0.5)
    
    dist_val_kn = st.number_input("Uniform Load $w$ (kN/m)", value=5.0, step=0.5)

    p_load = p_load_kn * 1e3
    dist_val = dist_val_kn * 1e3

# Main Content Area
st.title("🏗️ BeamSolver Pro — 2D Structural Analysis")
st.caption("Euler-Bernoulli Elastic Beam Solver | Instant SFD, BMD & Deflection Curves")

beam = Beam(
    length=length,
    E=e_mod,
    I=inertia,
    supports=[Support(position=sup1_pos), Support(position=sup2_pos)],
    point_loads=[PointLoad(position=p_pos, fz=p_load)] if p_load != 0 else [],
    dist_loads=[DistributedLoad(start=0.0, end=length, w_start=dist_val)] if dist_val != 0 else [],
)

try:
    x, V, M = beam.shear_moment(n_points=400)
    R = beam.reactions()
    
    # Superposition Deflection
    n_pts = 200
    xd = np.linspace(0.0, length, n_pts)
    defl = np.zeros(n_pts)
    equiv_loads = [(pl.position, -pl.fz) for pl in beam.point_loads]
    equiv_loads += [(sup1_pos, -R[0]), (sup2_pos, -R[1])]
    
    for dl in beam.dist_loads:
        n_sub = 40
        xs = np.linspace(dl.start, dl.end, n_sub + 1)
        for i in range(n_sub):
            xa, xb = xs[i], xs[i + 1]
            w = (dl.w_start + (dl.w_end if dl.w_end is not None else dl.w_start)) / 2.0
            equiv_loads.append(((xa + xb) / 2.0, -w * (xb - xa)))
            
    for xi_d in xd:
        for lp, mag in equiv_loads:
            defl[np.where(xd == xi_d)[0][0]] += beam._flex_coeff(xi_d, lp) * mag

    # KPI Top Bar
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Max Shear Force", f"{np.max(np.abs(V))/1e3:.2f} kN", delta=f"R1: {R[0]/1e3:.1f} kN")
    with c2:
        st.metric("Max Bending Moment", f"{np.max(np.abs(M))/1e3:.2f} kNm", delta=f"R2: {R[1]/1e3:.1f} kN")
    with c3:
        st.metric("Max Deflection", f"{np.max(np.abs(defl))*1e3:.2f} mm", delta_color="inverse")
    with c4:
        st.metric("Total Gravity Load", f"{(p_load + dist_val*length)/1e3:.2f} kN")

    st.markdown("<br>", unsafe_allow_html=True)

    # Matplotlib High-End Engineering Plots
    plt.style.use('dark_background')
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11, 8.5), sharex=True)
    fig.patch.set_facecolor('#0e1117')

    # SFD
    ax1.set_facecolor('#161b22')
    ax1.plot(x, V / 1e3, color="#38bdf8", lw=2.2, label="V (kN)")
    ax1.fill_between(x, V / 1e3, color="#38bdf8", alpha=0.25)
    ax1.axhline(0, color="#94a3b8", lw=0.8, linestyle=":")
    ax1.set_ylabel("Shear (kN)", color="#e2e8f0", fontsize=10, weight="bold")
    ax1.grid(True, linestyle="--", alpha=0.3, color="#64748b")
    ax1.set_title("Shear Force Diagram (SFD)", color="#f8fafc", loc="left", fontsize=11, weight="bold")

    # BMD
    ax2.set_facecolor('#161b22')
    ax2.plot(x, -M / 1e3, color="#f87171", lw=2.2, label="M (kNm)")
    ax2.fill_between(x, -M / 1e3, color="#f87171", alpha=0.25)
    ax2.axhline(0, color="#94a3b8", lw=0.8, linestyle=":")
    ax2.set_ylabel("Moment (kNm)", color="#e2e8f0", fontsize=10, weight="bold")
    ax2.grid(True, linestyle="--", alpha=0.3, color="#64748b")
    ax2.set_title("Bending Moment Diagram (BMD)", color="#f8fafc", loc="left", fontsize=11, weight="bold")

    # Deflection
    ax3.set_facecolor('#161b22')
    ax3.plot(xd, -defl * 1e3, color="#4ade80", lw=2.2, label="δ (mm)")
    ax3.fill_between(xd, -defl * 1e3, color="#4ade80", alpha=0.25)
    ax3.axhline(0, color="#94a3b8", lw=0.8, linestyle=":")
    ax3.set_ylabel("Deflection (mm)", color="#e2e8f0", fontsize=10, weight="bold")
    ax3.set_xlabel("Span Location x (m)", color="#e2e8f0", fontsize=11, weight="bold")
    ax3.grid(True, linestyle="--", alpha=0.3, color="#64748b")
    ax3.set_title("Elastic Deflection Curve", color="#f8fafc", loc="left", fontsize=11, weight="bold")

    plt.tight_layout()
    st.pyplot(fig)

    # PDF Download Section
    beam_params = {
        "Beam Length (L)": f"{length} m",
        "Modulus of Elasticity (E)": f"{e_gpa:.1f} GPa",
        "Moment of Inertia (I)": f"{inertia_cm4:.1f} cm4",
        "Support 1 Position": f"{sup1_pos} m (Pin)",
        "Support 2 Position": f"{sup2_pos} m (Roller)",
        "Point Load": f"{p_load_kn:.1f} kN at {p_pos} m",
        "Distributed Load": f"{dist_val_kn:.1f} kN/m (Uniform)",
    }
    max_vals = {
        "Max Shear Force": f"{np.max(np.abs(V))/1e3:.2f} kN",
        "Max Bending Moment": f"{np.max(np.abs(M))/1e3:.2f} kNm",
        "Max Deflection": f"{np.max(np.abs(defl))*1e3:.3f} mm",
        "Left Reaction R1": f"{R[0]/1e3:.2f} kN",
        "Right Reaction R2": f"{R[1]/1e3:.2f} kN",
    }

    st.markdown("---")
    col_dl, col_space = st.columns([1, 2])
    with col_dl:
        pdf_data = generate_pdf_report(beam_params, max_vals, fig)
        st.download_button(
            label="📄 Export Certified Structural Report (PDF)",
            data=pdf_data,
            file_name=f"Beam_Analysis_Report_{length}m.pdf",
            mime="application/pdf",
            use_container_width=True
        )

except Exception as e:
    st.error(f"Computation error: {e}")
