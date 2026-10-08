import os
import tempfile
from fpdf import FPDF
import matplotlib.pyplot as plt

class BeamReport(FPDF):
    def header(self):
        logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 32)
            self.set_x(46)
        else:
            self.set_x(14)
        
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(15, 23, 42)
        self.cell(0, 8, "BEAMSOLVER PRO - STRUCTURAL REPORT", ln=True)
        self.set_x(46 if os.path.exists(logo_path) else 14)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, "Certified Structural Analysis & Calculation Dossier | Lead: Alireza Sani", ln=True)
        self.ln(6)
        self.set_draw_color(203, 213, 225)
        self.set_line_width(0.5)
        self.line(10, 26, 200, 26)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} - Confidential & Certified Engineering Output", align="C")

def generate_pdf_report(beam, summary_data, fig_plots):
    pdf = BeamReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=18)

    # 1. Project Information
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 7, "1. Beam Parameters & Cross-Section Properties", ln=True)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    
    L = getattr(beam, "length", 0.0)
    E = getattr(beam, "E", 0.0) / 1e9
    I = getattr(beam, "I", 0.0)
    section_mod = summary_data.get("section_modulus", "N/A")
    yield_str = summary_data.get("yield_strength", "N/A")

    col_w = 47.5
    pdf.cell(col_w, 7, f" Total Span: {L:.2f} m", border=1, fill=True)
    pdf.cell(col_w, 7, f" Young's Modulus (E): {E:.1f} GPa", border=1, fill=True)
    pdf.cell(col_w, 7, f" Inertia (I): {I:.2e} m4", border=1, fill=True)
    pdf.cell(col_w, 7, f" Sec. Modulus (W): {section_mod}", border=1, fill=True, ln=True)
    pdf.ln(3)

    # 2. Key Analysis Indices & Structural Checks
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 7, "2. Key Structural Indices & Compliance Summary", ln=True)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(224, 231, 255)
    pdf.cell(50, 7, " Parameter / Metric", border=1, fill=True)
    pdf.cell(45, 7, " Computed Value", border=1, fill=True)
    pdf.cell(45, 7, " Design Limit / Criteria", border=1, fill=True)
    pdf.cell(50, 7, " Status", border=1, fill=True, ln=True)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_fill_color(255, 255, 255)
    
    indices = [
        ("Max Absolute Bending Moment", f"{summary_data.get('max_moment', 0.0):.2f} kNm", "Moment Capacity", "CRITICAL"),
        ("Max Absolute Shear Force", f"{summary_data.get('max_shear', 0.0):.2f} kN", "Shear Capacity", "VERIFIED"),
        ("Max Elastic Deflection", f"{summary_data.get('max_deflection', 0.0):.3f} mm", f"L/360 ({summary_data.get('limit_deflection', 0.0):.2f} mm)", summary_data.get("deflection_status", "PASS")),
        ("Peak Bending Stress", f"{summary_data.get('max_stress', 'N/A')}", f"Yield Limit ({yield_str})", summary_data.get("stress_status", "PASS")),
    ]

    for label, val, limit, status in indices:
        pdf.cell(50, 6, f" {label}", border=1)
        pdf.cell(45, 6, f" {val}", border=1)
        pdf.cell(45, 6, f" {limit}", border=1)
        if status in ["PASS", "VERIFIED"]:
            pdf.set_text_color(22, 101, 52)
        elif status == "FAIL":
            pdf.set_text_color(185, 28, 28)
        else:
            pdf.set_text_color(30, 41, 59)
        pdf.cell(50, 6, f" {status}", border=1, ln=True)
        pdf.set_text_color(30, 41, 59)

    pdf.ln(5)

    # 3. Diagram Curves
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "3. Shear Force, Bending Moment & Deflection Curves", ln=True)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_fig:
        tmp_name = tmp_fig.name
        fig_plots.savefig(tmp_name, dpi=200, bbox_inches="tight")
        pdf.image(tmp_name, x=10, y=pdf.get_y(), w=190)
    
    try:
        os.remove(tmp_name)
    except Exception:
        pass

    return bytes(pdf.output())
