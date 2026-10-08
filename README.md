<div align="center">

# 🏗️ BeamSolver Pro

**A professional 2D Structural Beam Analysis Tool — SFD, BMD & Deflection Curves with Certified PDF Reports**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![NumPy](https://img.shields.io/badge/NumPy-FEM_Engine-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![Tests](https://img.shields.io/badge/Tests-2%20Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](tests/)

</div>

---

## 📖 Overview

**BeamSolver Pro** is an engineering-grade application for the structural analysis of 2D Euler-Bernoulli beams, built on the **Finite Element Method (FEM)** using the direct stiffness approach.

It delivers instant, publication-quality diagrams and exports certified structural analysis reports in PDF format — designed for civil & structural engineers, students, and educators.

## ✨ Features

| | Feature |
|---|---|
| 🧮 | **FEM Physics Engine** — Stiffness-method solver (`solver.py`) verified against closed-form solutions |
| 📊 | **Interactive Diagrams** — Shear Force (SFD), Bending Moment (BMD) & Elastic Deflection Curve |
| 📐 | **Flexible Inputs** — Custom spans, support positions, point loads & uniform distributed loads |
| 📄 | **PDF Reporting** — One-click certified structural report export (`fpdf2`) |
| 🎨 | **Modern Dark Dashboard** — Engineering-grade UI with live KPI metric cards |
| ✅ | **Unit Tested** — `pytest` validated against theory |

## 🧪 Verification

The solver is validated against hand-calculated structural mechanics results:


```
Simply supported beam, L = 6 m, P = 10 kN at mid-span
Theory:    M_max = P*L/4  = 15.00 kN*m
Solver:    M_max          = 15.00 kN*m   (rel. error < 0.1%)
Reactions: R1 = R2 = P/2  =  5.00 kN     (symmetry check)

```

Run the test suite:


```powershell
$env:PYTHONPATH = "src"
uv run pytest tests/test_solver.py -v

```

## 🚀 Quick Start


```powershell
# 1. Clone the repository
git clone https://github.com/naomi197/beam-solver.git
cd beam-solver

# 2. Install dependencies
uv sync

# 3. Launch the dashboard
$env:PYTHONPATH = "src"
uv run streamlit run app.py

```

The app opens automatically at `http://localhost:8501`.

## 📂 Project Structure


```
beam-solver/
├── app.py                      # Streamlit dashboard (UI layer)
├── pyproject.toml              # Project metadata & dependencies
├── src/
│   └── beam_solver/
│       ├── solver.py           # FEM stiffness-method physics engine
│       └── report.py           # PDF report generator (fpdf2)
└── tests/
    └── test_solver.py          # Engineering validation tests (pytest)

```

---

<div align="center">

*Engineered by Alireza Sani*

</div>
