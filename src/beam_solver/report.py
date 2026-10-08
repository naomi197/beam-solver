from fpdf import FPDF
import tempfile
import os

class BeamReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Structural Engineering Analysis Report - 2D Beam Solver", align="C")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def generate_pdf_report(beam_params, max_vals, fig):
    pdf = BeamReport()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 8, "1. Beam Properties & Configuration", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    for key, val in beam_params.items():
        pdf.cell(70, 6, f"{key}:")
        pdf.cell(0, 6, f"{val}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 8, "2. Key Structural Results Summary", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    for key, val in max_vals.items():
        pdf.cell(70, 6, f"{key}:")
        pdf.cell(0, 6, f"{val}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 8, "3. Shear, Moment & Deflection Diagrams", ln=True)
    pdf.set_text_color(0, 0, 0)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp_path = tmp.name
        fig.savefig(tmp_path, dpi=200, bbox_inches="tight")
    pdf.image(tmp_path, x=15, w=180)
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    return bytes(pdf.output())
