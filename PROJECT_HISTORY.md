# BeamSolver Pro - Project History & AI Handoff Notes
# Last updated: 2026-10-08 | Lead Engineer: Alireza Sani

## WHAT THIS PROJECT IS
A professional 2D structural beam analysis web app (Streamlit + Matplotlib + FPDF).
Dark theme, custom logo (assets/logo.png), KPI metric cards, PDF calculation dossier export.

## CRITICAL - DO NOT BREAK THESE (UI RULES)
1. Logo MUST stay: sidebar + header, loaded from "assets/logo.png" (relative path, app runs from project root).
2. Dark theme CSS (.main-header gradient, .metric-card) must be preserved.
3. Contact email is a static HTML <a href="mailto:..."> link - NOT st.button
   (st.button caused NotFoundError: removeChild due to browser translation corrupting Streamlit DOM).
4. Do NOT introduce non-ASCII characters (em-dash, en-dash) into report.py strings -
   FPDF helvetica font cannot encode them (FPDFUnicodeEncodingException). Use plain "-".

## SOLVER API (verified via inspect - the REAL signatures in src/beam_solver/solver.py)
- Beam(length: float, E: float, I: float, supports: list = [], point_loads: list = [], dist_loads: list = [])
  -> supports/loads are passed DIRECTLY in the constructor. There is NO add_support() and NO solve() method!
- Support(position: float, ux: bool = False, uy: bool = True, rz: bool = False)
- PointLoad(position: float, fz: float)
- IMPORTANT: the load class is "DistributedLoad" in solver.py (NOT "DistLoad").
  app.py imports it with a try/except fallback (DistributedLoad as DistLoad) - keep that pattern.
- Beam methods: reactions(), shear_moment(n_points=500). There is NO native deflection method.
- Deflection is computed in app.py by numerical double integration of M(x)/EI
  with simple-support boundary conditions (linear correction at supports).

## BUGS FIXED (do not reintroduce)
1. ImportError DistLoad -> fixed with try/except import fallback.
2. AttributeError add_support/solve -> fixed by using constructor-based Beam API (verified with inspect).
3. Peak stress showed 305,025,705 MPa -> missing Pa->MPa conversion; corrected to
   max_stress_mpa = (max_m * 1e3) / W_m3 / 1e6.
4. PDF crashed on unicode em-dash in report.py -> all em/en-dashes replaced with "-".
5. Logo disappeared during patches -> fixed with os.path.exists("assets/logo.png") relative path checks.

## CURRENT STATE (working, verified on localhost:8501)
- KPIs correct: M=169.90 kNm, V=72.50 kN, deflection=63.83 mm (FAIL vs L/360=22.2mm), stress=305.0 MPa (FAIL vs fy=240)
- FAIL statuses are ENGINEERING-correct for default loads (span 8m, q=15kN/m, P=25kN, W=557cm3).
  Do NOT "fix" them - the section is simply undersized for those loads.
- PDF download works. Email link works. Logo and dark theme intact.

## FILE STRUCTURE
- app.py                  : Streamlit UI + numerical deflection integration + PDF export call
- src/beam_solver/solver.py  : Core solver (Beam, Support, PointLoad, DistributedLoad)
- src/beam_solver/report.py  : FPDF report generator (ASCII only!)
- assets/logo.png         : Brand logo (do not delete/move)
- inspect_solver.py       : Debug helper that prints class signatures
- PROJECT_HISTORY.md      : This file

## POSSIBLE NEXT STEPS (not started)
- README.md with badges + screenshots for GitHub (naomi197)
- More accurate deflection (exact support-condition integration)
- Multi-support continuous beam UI
