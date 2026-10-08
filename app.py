import time
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from beam_solver.solver import Beam, Support, PointLoad, DistributedLoad
from beam_solver.report import generate_pdf_report

st.set_page_config(
    page_title="BeamSolver Pro — 2D Structural Analysis",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- استایل دارک مهندسی ---
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 15px;
        color: white;
        text-align: center;
    }
    .metric-val {
        font-size: 24px;
        font-weight: bold;
        color: #38bdf8;
    }
    .metric-lbl {
        font-size: 13px;
        color: #94a3b8;
    }
    .lock-box {
        background: linear-gradient(135deg, #1e1b4b, #311042);
        border: 2px solid #a855f7;
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        color: white;
        margin-top: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- مدیریت زمان آزمایشی (60 ثانیه) و لایسنس ---
TRIAL_DURATION = 60

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "is_unlocked" not in st.session_state:
    st.session_state.is_unlocked = False

elapsed = time.time() - st.session_state.start_time
remaining = max(0, int(TRIAL_DURATION - elapsed))

# نوار کناری (Sidebar)
with st.sidebar:
    st.title("🏗️ BeamSolver Pro")
    st.caption("Engineered by Alireza Sani")
    st.markdown("---")
    
    license_key = st.text_input("🔑 Enter Pro License Key:", type="password")
    if license_key in ["BEAM-PRO-2026", "ALIREZA-VIP"]:
        st.session_state.is_unlocked = True
        st.success("✅ Pro License Activated! Unlimited Access.")
    elif license_key:
        st.error("Invalid license key.")

is_expired = (remaining <= 0) and not st.session_state.is_unlocked

# وضعیت لایسنس در سایدبار
if st.session_state.is_unlocked:
    st.sidebar.markdown("🟢 **Status:** Pro License (Active)")
elif not is_expired:
    st.sidebar.markdown(f"⏳ **Trial Mode:** `{remaining}s` remaining")
else:
    st.sidebar.markdown("🔴 **Trial Expired**")

st.title("🏗️ BeamSolver Pro — 2D Structural Beam Analysis")
st.write("Finite Element Method (FEM) Euler-Bernoulli beam solver with live SFD, BMD and certified PDF export.")

# --- صفحه قفل و پرداخت مستقیم با متاماسک (فقط پس از اتمام ۶۰ ثانیه) ---
if is_expired:
    st.markdown("""
    <div class="lock-box">
        <h2>🔒 Trial Period Ended (1 Minute Expired)</h2>
        <p style="font-size: 16px; color: #cbd5e1;">
            Hope you enjoyed testing <b>BeamSolver Pro</b>! To unlock lifetime unlimited analysis and PDF export, purchase a Pro license below.
        </p>
        <div style="margin: 20px 0;">
            <a href="mailto:alirezafazeli@live.com?subject=Purchase%20BeamSolver%20Pro%20License" style="background-color: #38bdf8; color: #0f172a; padding: 12px 24px; border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 16px;">
                💳 Contact via Email ($49)
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💎 Direct MetaMask / Crypto Payment (USDT on Ethereum)")
    st.write("Send **49 USDT** directly to the address below, then submit your transaction hash to receive your instant license key.")

    with st.container(border=True):
        st.markdown("#### 📬 Receiver Wallet Address (Ethereum / ERC-20)")
        st.code("0xf3ddb743b4f1BD8b59Bf5Bf22905555Fe5c4B7C1", language=None)
        st.markdown("[🔗 Check incoming transactions on Etherscan](https://etherscan.io/address/0xf3ddb743b4f1BD8b59Bf5Bf22905555Fe5c4B7C1)")
        st.warning("⚠️ **Notice:** Send only **USDT** on the **Ethereum (ERC-20)** network to this address.")

    with st.container(border=True):
        st.markdown("#### 🧾 Submit Payment Confirmation")
        txid = st.text_input("Transaction Hash (TxID):", key="txid_field")
        buyer_mail = st.text_input("Your Email Address (for key delivery):", key="mail_field")
        if st.button("🚀 Confirm Payment & Request Key"):
            if txid and buyer_mail:
                st.success("✅ Payment submission recorded! Your activation key will be verified and sent to your email promptly.")
            else:
                st.error("Please enter both TxID and Email address.")

    st.stop()

# --- محیط کاربری و محاسبات اصلی (در طول زمان آزمایشی یا نسخه فعال‌شده) ---
col_in1, col_in2 = st.columns(2)
with col_in1:
    st.subheader("📐 Beam Geometry & Material")
    length = st.number_input("Span Length L (m)", min_value=1.0, max_value=50.0, value=6.0, step=0.5)
    E_val = st.number_input("Elastic Modulus E (GPa)", min_value=1.0, max_value=500.0, value=200.0, step=10.0) * 1e9
    I_val = st.number_input("Moment of Inertia I (cm⁴)", min_value=1.0, max_value=100000.0, value=8340.0, step=100.0) * 1e-8

with col_in2:
    st.subheader("⚙️ Supports & Loads")
    s1_pos = st.number_input("Pin Support 1 (m)", min_value=0.0, max_value=length, value=0.0, step=0.5)
    s2_pos = st.number_input("Roller Support 2 (m)", min_value=0.0, max_value=length, value=length, step=0.5)
    p_load = st.number_input("Point Load P (kN, downward)", value=10.0, step=1.0)
    p_pos = st.number_input("Point Load Position (m)", min_value=0.0, max_value=length, value=length/2, step=0.5)
    q_load = st.number_input("Uniform Load q (kN/m, downward)", value=0.0, step=1.0)

# حل مسئله با موتور تحلیل
supports = [
    Support(position=s1_pos, ux=True, uy=True),
    Support(position=s2_pos, ux=False, uy=True)
]
point_loads = [PointLoad(position=p_pos, fz=p_load * 1000)] if p_load > 0 else []
dist_loads_list = [DistributedLoad(start=0, end=length, w_start=q_load * 1000)] if q_load > 0 else []

beam = Beam(length=length, E=E_val, I=I_val, supports=supports, point_loads=point_loads, dist_loads=dist_loads_list)
results = beam.solve()

# نمایش کارت‌های شاخص
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
max_moment = np.max(np.abs(results['moment'])) / 1000
max_shear = np.max(np.abs(results['shear'])) / 1000
max_defl = np.max(np.abs(results['deflection'])) * 1000
total_load = p_load + (q_load * length)

m1.markdown(f'<div class="metric-card"><div class="metric-val">{max_moment:.2f} kN·m</div><div class="metric-lbl">Max Bending Moment</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-card"><div class="metric-val">{max_shear:.2f} kN</div><div class="metric-lbl">Max Shear Force</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-card"><div class="metric-val">{max_defl:.2f} mm</div><div class="metric-lbl">Max Deflection</div></div>', unsafe_allow_html=True)
m4.markdown(f'<div class="metric-card"><div class="metric-val">{total_load:.2f} kN</div><div class="metric-lbl">Total Applied Load</div></div>', unsafe_allow_html=True)

# رسم نمودارهای مهندسی
st.markdown("---")
st.subheader("📊 Engineering Diagrams")
fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
plt.style.use('dark_background')

axes[0].plot(results['x'], results['shear']/1000, color='#38bdf8', lw=2)
axes[0].fill_between(results['x'], results['shear']/1000, color='#38bdf8', alpha=0.2)
axes[0].set_ylabel("Shear (kN)")
axes[0].grid(True, alpha=0.3)
axes[0].set_title("Shear Force Diagram (SFD)")

axes[1].plot(results['x'], results['moment']/1000, color='#f43f5e', lw=2)
axes[1].fill_between(results['x'], results['moment']/1000, color='#f43f5e', alpha=0.2)
axes[1].set_ylabel("Moment (kN·m)")
axes[1].grid(True, alpha=0.3)
axes[1].set_title("Bending Moment Diagram (BMD)")

axes[2].plot(results['x'], results['deflection']*1000, color='#10b981', lw=2)
axes[2].fill_between(results['x'], results['deflection']*1000, color='#10b981', alpha=0.2)
axes[2].set_xlabel("Span (m)")
axes[2].set_ylabel("Deflection (mm)")
axes[2].grid(True, alpha=0.3)
axes[2].set_title("Elastic Deflection Curve")

plt.tight_layout()
st.pyplot(fig)

# خروجی گزارش PDF
pdf_bytes = generate_pdf_report(beam, results)
st.download_button(
    label="📄 Download Certified Structural Report (PDF)",
    data=pdf_bytes,
    file_name="BeamSolver_Pro_Report.pdf",
    mime="application/pdf"
)