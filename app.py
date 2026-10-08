import os
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from beam_solver.solver import Beam, Support, PointLoad
try:
    from beam_solver.solver import DistLoad
except ImportError:
    from beam_solver.solver import DistributedLoad as DistLoad
from beam_solver.report import generate_pdf_report

st.set_page_config(
    page_title="BeamSolver Pro — 2D Structural Analysis",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        display: flex; align-items: center; gap: 20px;
        padding: 15px 20px;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155; border-radius: 12px; margin-bottom: 25px;
    }
    .metric-card {
        background: #1e293b; border: 1px solid #334155; border-radius: 10px;
        padding: 14px; text-align: center;
    }
    .metric-val { font-size: 1.5rem; font-weight: 700; color: #38bdf8; }
    .metric-lbl { font-size: 0.85rem; color: #94a3b8; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

logo_path = os.path.join("assets", "logo.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.title("🏗️ BeamSolver Pro")

st.sidebar.markdown("### Structural Engine Config")
st.sidebar.markdown("---")

col_h1, col_h2 = st.columns([1, 6])
with col_h1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=110)
with col_h2:
    st.markdown("## BeamSolver Pro — 2D Structural FEA Engine")
    st.caption("Professional Continuous Beam Analysis, Stress Verification & Calculation Dossier | Lead: Alireza Sani")

beam_length = st.sidebar.number_input("Total Span L (m)", min_value=1.0, max_value=50.0, value=8.0, step=0.5)
E_gpa = st.sidebar.number_input("Young's Modulus E (GPa)", min_value=1.0, max_value=500.0, value=200.0, step=10.0)
I_cm4 = st.sidebar.number_input("Moment of Inertia I (cm⁴)", min_value=1.0, max_value=500000.0, value=8356.0, step=100.0)
W_cm3 = st.sidebar.number_input("Section Modulus W (cm³)", min_value=1.0, max_value=50000.0, value=557.0, step=10.0)
yield_fy = st.sidebar.number_input("Yield Strength fy (MPa)", min_value=50.0, max_value=1000.0, value=240.0, step=10.0)

E_pa = E_gpa * 1e9
I_m4 = I_cm4 * 1e-8
W_m3 = W_cm3 * 1e-6

st.sidebar.markdown("---")
st.sidebar.subheader("Supports")
s1_pos = st.sidebar.number_input("Support 1 Position (m)", min_value=0.0, max_value=beam_length, value=0.0, step=0.5)
s2_pos = st.sidebar.number_input("Support 2 Position (m)", min_value=0.0, max_value=beam_length, value=float(beam_length), step=0.5)

st.sidebar.markdown("---")
st.sidebar.subheader("Loads")
q_load = st.sidebar.number_input("Uniform Load q (kN/m)", min_value=0.0, max_value=200.0, value=15.0, step=1.0)
p_load = st.sidebar.number_input("Point Load P (kN)", min_value=0.0, max_value=500.0, value=25.0, step=5.0)
p_pos = st.sidebar.number_input("Point Load Position (m)", min_value=0.0, max_value=beam_length, value=beam_length / 2.0, step=0.5)

supports = [
    Support(position=s1_pos, uy=True),
    Support(position=s2_pos, uy=True),
]
point_loads = []
if p_load > 0:
    point_loads.append(PointLoad(position=float(p_pos), fz=p_load * 1e3))
dist_loads = []
if q_load > 0:
    dist_loads.append(DistLoad(start=0.0, end=float(beam_length), w_start=q_load * 1e3, w_end=q_load * 1e3))

beam = Beam(length=float(beam_length), E=E_pa, I=I_m4,
            supports=supports, point_loads=point_loads, dist_loads=dist_loads)

res = beam.shear_moment()
if isinstance(res, dict):
    x_arr = np.asarray(res.get("x", res.get("X", [])))
    shear_arr = np.asarray(res.get("V", res.get("shear", []))) / 1e3
    moment_arr = np.asarray(res.get("M", res.get("moment", []))) / 1e3
elif isinstance(res, (tuple, list)) and len(res) >= 3:
    x_arr = np.asarray(res[0]); shear_arr = np.asarray(res[1]) / 1e3; moment_arr = np.asarray(res[2]) / 1e3
else:
    x_arr = np.linspace(0, beam_length, 500); shear_arr = np.zeros_like(x_arr); moment_arr = np.zeros_like(x_arr)

# Deflection via double integration of M(x) with simple-beam boundary conditions
M_pa = moment_arr * 1e3
EI = E_pa * I_m4
n = len(x_arr)
dx = x_arr[1] - x_arr[0] if n > 1 else 1.0
theta = np.concatenate([[0.0], np.cumsum(0.5 * (M_pa[1:] + M_pa[:-1]) / EI * dx)])
v = np.concatenate([[0.0], np.cumsum(0.5 * (theta[1:] + theta[:-1]) * dx)])
v = v - np.interp(0.0, x_arr, v) - (x_arr - 0.0) / (beam_length - 0.0) * (np.interp(beam_length, x_arr, v) - np.interp(0.0, x_arr, v))
defl_arr = -v * 1e3  # mm (downward positive)

max_v = float(np.max(np.abs(shear_arr))) if n else 0.0
max_m = float(np.max(np.abs(moment_arr))) if n else 0.0
max_d = float(np.max(np.abs(defl_arr))) if n else 0.0
defl_limit = (beam_length * 1000.0) / 360.0
max_stress_mpa = (max_m * 1e3) / W_m3 / 1e6 if W_m3 > 0 else 0.0
stress_status = "PASS" if max_stress_mpa <= yield_fy else "FAIL"
defl_status = "PASS" if max_d <= defl_limit else "FAIL"

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{max_m:.2f} kNm</div><div class="metric-lbl">Max Moment |M|</div></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{max_v:.2f} kN</div><div class="metric-lbl">Max Shear |V|</div></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{max_d:.2f} mm</div><div class="metric-lbl">Max Deflection (Lim: {defl_limit:.1f}) [{defl_status}]</div></div>', unsafe_allow_html=True)
with kpi4:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{max_stress_mpa:.1f} MPa</div><div class="metric-lbl">Peak Stress (fy: {yield_fy:.0f}) [{stress_status}]</div></div>', unsafe_allow_html=True)

st.write("")

tab_diagrams, tab_checks, tab_report = st.tabs(["📊 Force & Deflection Diagrams", "📐 Stress & Limit Checks", "📑 Certified Dossier (PDF)"])

plt.style.use("dark_background")
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
ax1.plot(x_arr, shear_arr, color="#38bdf8", lw=2); ax1.fill_between(x_arr, shear_arr, color="#38bdf8", alpha=0.2)
ax1.set_ylabel("Shear (kN)"); ax1.grid(True, linestyle="--", alpha=0.3); ax1.set_title("Shear Force Diagram (SFD)", fontsize=11)
ax2.plot(x_arr, moment_arr, color="#f59e0b", lw=2); ax2.fill_between(x_arr, moment_arr, color="#f59e0b", alpha=0.2)
ax2.set_ylabel("Moment (kNm)"); ax2.grid(True, linestyle="--", alpha=0.3); ax2.set_title("Bending Moment Diagram (BMD)", fontsize=11)
ax3.plot(x_arr, defl_arr, color="#10b981", lw=2); ax3.fill_between(x_arr, defl_arr, color="#10b981", alpha=0.2)
ax3.set_ylabel("Deflection (mm)"); ax3.set_xlabel("Span Position x (m)")
ax3.grid(True, linestyle="--", alpha=0.3); ax3.set_title("Elastic Deflection Curve", fontsize=11)
plt.tight_layout()

with tab_diagrams:
    st.pyplot(fig)

with tab_checks:
    st.markdown("### Engineering Limit State Checks")
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**Deflection Criterion:** L/360 = **{defl_limit:.2f} mm**\n\nComputed: **{max_d:.2f} mm** — Status: **{defl_status}**")
    with c2:
        st.info(f"**Bending Stress Criterion:** Yield Strength = **{yield_fy:.1f} MPa**\n\nComputed Peak Stress: **{max_stress_mpa:.1f} MPa** — Status: **{stress_status}**")

with tab_report:
    st.markdown("### Official Calculation Dossier Export")
    st.write("Generate a signed, certified PDF calculation dossier including design metrics, stress verification, and diagram curves.")
    summary_dict = {
        "max_moment": max_m, "max_shear": max_v,
        "max_deflection": max_d, "limit_deflection": defl_limit, "deflection_status": defl_status,
        "max_stress": f"{max_stress_mpa:.1f} MPa", "yield_strength": f"{yield_fy:.0f} MPa",
        "stress_status": stress_status, "section_modulus": f"{W_cm3:.0f} cm3",
    }
    plt.style.use("default")
    fig_print, (p1, p2, p3) = plt.subplots(3, 1, figsize=(8, 6), sharex=True)
    p1.plot(x_arr, shear_arr, color="#0284c7", lw=1.5); p1.set_ylabel("V (kN)"); p1.grid(True, linestyle=":", alpha=0.6)
    p2.plot(x_arr, moment_arr, color="#d97706", lw=1.5); p2.set_ylabel("M (kNm)"); p2.grid(True, linestyle=":", alpha=0.6)
    p3.plot(x_arr, defl_arr, color="#059669", lw=1.5); p3.set_ylabel("δ (mm)"); p3.set_xlabel("x (m)"); p3.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    pdf_bytes = generate_pdf_report(beam, summary_dict, fig_print)
    plt.close(fig_print)
    st.download_button(label="📥 Download Certified Engineering PDF Dossier", data=pdf_bytes,
                       file_name="BeamSolver_Pro_Calculation_Dossier.pdf", mime="application/pdf")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 10px;">
    BeamSolver Pro v2.4 © 2026 Alireza Sani Structural Engineering Systems. All rights reserved.<br>
    For commercial licensing:
    <a href="mailto:alirezafazeli@live.com?subject=BeamSolver%20Pro%20Inquiry" style="color: #38bdf8; text-decoration: none; font-weight: 600;">
        Contact via Email (alirezafazeli@live.com)
    </a>
</div>
""", unsafe_allow_html=True)
