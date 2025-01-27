# GeoWagdy - Function Intersection Plotter

**GeoWagdy** is a Python desktop application (built with **PySide2**) that helps you:
- Enter two **mathematical functions** of `x`.
- Solve for all **real intersections** (where `f1(x) = f2(x)`).
- Plot both functions on a **cartesian** plane, marking intersection points.
- Export the **plot** to a PNG/JPEG file.
- Create multiple **tabs** to handle multiple sets of functions at once.
- Access a "Help" menu that opens a link in your default browser.

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [How to Run](#how-to-run)
4. [Usage Instructions](#usage-instructions)
5. [Running the Automated Tests](#running-the-automated-tests)
6. [Known Limitations](#known-limitations)
7. [License](#license)

---

## Features
- **GUI** with a **Splash Screen** and **Progress Bar**.
- **Multiple Tabs** (each is an independent plotting environment).
- **Plot** with embedded **Matplotlib**.
- **Accepts** operators: `+`, `-`, `*`, `/`, `^` (as `**`), `log10()`, `sqrt()`, etc.
- **Solves** for real intersections using **Sympy**.
- **Exports** your plot to `png`/`jpeg`.
- **Help** menu to open an external documentation link.
- **Automated Tests** with `pytest` and `pytest-qt`.

---

## Installation
1. **Python 3.9+** is recommended (though 3.6+ may work).
2. Install the required dependencies:
   ```bash
   pip install PySide2 matplotlib sympy adjustText pytest pytest-qt



Depending on your environment, you may need a virtual environment:

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
How to Run
Clone or Download this repository.
Open a terminal in the project folder.
Run:
bash
Copy
Edit
python app.py
Alternatively, if you named your file differently, run python <yourfilename>.py.
The Splash Screen will appear briefly, then the Main Window opens.
Usage Instructions
On startup, you’ll see one tab containing:
Two input fields: f1(x) and f2(x).
A button labeled “Solve + Plot”.
Enter your functions in the text fields (e.g., "x", "2*x", "sqrt(x) + 1", etc.).
Click “Solve + Plot”:
If real intersections exist, they’ll be plotted and annotated.
If no real intersection, a message appears but the functions are still plotted.
Add new tabs: Use File → New Tab to create another tab.
Export your current tab’s plot: File → Export Plot.
Help: The Help menu → “Open Help Link” will open your browser at the specified URL.
Running the Automated Tests
Ensure you have pytest and pytest-qt installed:
bash
Copy
Edit
pip install pytest pytest-qt
In the project directory, run:
bash
Copy
Edit
pytest -v
This will automatically discover test_app.py, start the GUI in a test environment, and run tests.
If all goes well, you’ll see something like:
python
Copy
Edit
================= test session starts =================
...
test_app.py::test_main_window_starts PASSED
test_app.py::test_solve_valid_functions PASSED
...
================= 6 passed in 1.23s ====================
If any test fails, pytest will show a FAIL message with details.