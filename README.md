# BeamSolver Pro: 2D Structural Beam Analysis

### FEA-Based Structural Analysis & Certified Dossier Generator

BeamSolver Pro is a professional-grade 2D structural analysis application engineered for civil and structural engineering workflows. It delivers high-precision Finite Element Analysis (FEA) diagrams and official engineering dossiers in certified PDF format.

## ðŸ’Úºw! Key Features
- **Finite Element Analysis (FEA):** Real-time computation of Shear Force (SFD), Bending Moment (BMD), and Elastic Deflection curves.
- **Senior Engineer Dossier Export:** One-click PDF generation featuring certified stamps, calculation summaries, and diagram plots.
- **Parametric Inputs:** Quick configuration for pinned/roller supports, point loads, and distributed loads (UDL).
- **Modern Engineering UI:** Streamlit interface with full dark mode optimization.

## ðŸ›ø Tech Stack
- **Core Engine:** Python 3.12, NumPy, Matplotlib
- **Application Framework:** Streamlit
- **Reporting Module:** Custom FPDF2 Engine

## ðŸ“¥ Installation & Local Run
```bash
git clone https://github.com/naomi197/beam-solver.git
cd beam-solver
python -m venv .venv
\.venv\Scripts\Activate.ps1
pip install -e .
streamlit run app.py
```

---
*Developed by Alireza Fazeli | Structural Engineering & Software Automation*
