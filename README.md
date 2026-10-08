# BeamSolver Pro

Free and open-source 2D structural beam analysis application built with Python, NumPy, Matplotlib, FPDF2, and Streamlit.

## Features

- Shear force and bending moment diagrams
- Elastic deflection curve for the supported beam model
- Point loads
- Uniform, triangular, and trapezoidal distributed loads
- Bending stress verification
- PDF calculation report export
- Dark Streamlit interface with project logo
- Input validation for beam, support, point-load, and distributed-load data
- MIT licensed and free to use

## Project Scope

BeamSolver currently targets a simply supported beam model with two supports. Deflection is calculated in the application by numerical double integration of the bending moment with supported-beam boundary conditions.

The calculation results are intended for preliminary engineering analysis and educational use. Always have structural calculations independently reviewed by a qualified engineer before using them for construction or safety-critical decisions.

## Requirements

- Python 3.10 or newer
- Windows, macOS, or Linux

## Installation

```powershell
git clone https://github.com/naomi197/beam-solver.git
cd beam-solver
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## Run the Application

```powershell
streamlit run app.py
```

The application opens locally at http://localhost:8501.

## Run Tests

```powershell
python -m pytest -q
```

The test suite covers:

- Point-load beam behavior
- Uniform, triangular, and trapezoidal distributed loads
- Static equilibrium
- Invalid physical values
- Out-of-range support and load positions
- Invalid support configurations
- `n_points` validation

## Repository Structure

```text
app.py
assets/
  logo.png
src/
  beam_solver/
    __init__.py
    solver.py
    report.py
tests/
  test_solver.py
  test_input_validation.py
docs/
.github/
  workflows/
    ci.yml
pyproject.toml
requirements.txt
```

## Limitations

- The current solver supports a simply supported beam with two supports.
- Native deflection calculation is not implemented inside the solver package; the Streamlit application performs numerical integration.
- The application is not a general-purpose finite-element analysis package.
- Results should be independently reviewed by a qualified structural engineer before safety-critical use.

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE) for the full text.

## Author

Developed by Alireza Fazeli.
