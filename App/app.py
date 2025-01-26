import sys
import math
import traceback
import re

from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)
from PySide2.QtCore import Qt

# Matplotlib imports
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# We will use sympy for symbolic parsing and solving
import sympy
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)


class MplCanvas(FigureCanvasQTAgg):
    """
    A custom canvas to display matplotlib plots within a PySide2 widget.
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        self.setParent(parent)


class MainWindow(QMainWindow):
    """
    Main window of the application. Contains:
    - Two QLineEdits for user input of functions.
    - A button to solve and plot.
    - An embedded Matplotlib canvas for plotting.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Geowagdy")

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Layout for function inputs
        input_layout = QHBoxLayout()
        self.label_f1 = QLabel("f1(x):")
        self.edit_f1 = QLineEdit()
        self.edit_f1.setPlaceholderText("e.g. 5x + 3 or 5*x + 3")

        self.label_f2 = QLabel("f2(x):")
        self.edit_f2 = QLineEdit()
        self.edit_f2.setPlaceholderText("e.g. 2x or 2*x")

        # Add widgets to input layout
        input_layout.addWidget(self.label_f1)
        input_layout.addWidget(self.edit_f1)
        input_layout.addWidget(self.label_f2)
        input_layout.addWidget(self.edit_f2)

        # Solve button
        self.solve_button = QPushButton("Solve + Plot")
        self.solve_button.clicked.connect(self.on_solve_clicked)

        # Plot canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Add sub-layouts to main layout
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.solve_button)
        main_layout.addWidget(self.canvas)

        self.setCentralWidget(main_widget)
        self.setMinimumSize(800, 600)


    def on_solve_clicked(self):
        """
        Slot triggered when the user clicks the "Solve & Plot" button.
        Attempts to parse the two functions, solve for all real intersections,
        and plot the functions along with the solution points if they exist.
        """
        f1_str = self.edit_f1.text().strip()
        f2_str = self.edit_f2.text().strip()

        # Validate non-empty input
        if not f1_str or not f2_str:
            self.show_error_message("Both function fields must be filled.")
            self.clear_plot()
            return

        try:
            # Convert input strings to Sympy expressions
            expr_f1 = self.string_to_sympy_expr(f1_str)
            expr_f2 = self.string_to_sympy_expr(f2_str)

            # Define a symbol for x
            x = sympy.Symbol('x', real=True)

            # Solve the equation f1(x) = f2(x) -> f1(x) - f2(x) = 0
            solutions = sympy.solve(sympy.Eq(expr_f1, expr_f2), x, dict=True)

            # Filter real solutions
            real_solutions = []
            for sol in solutions:
                val = sol[x]
                if val.is_real:
                    real_solutions.append(val)

            if not real_solutions:
                # No real intersection
                self.show_info_message("No real intersection found. Plotting both functions anyway.")
                self.plot_functions(expr_f1, expr_f2, intersections=[])
            else:
                # Convert each solution to float x and float y
                intersections = []
                for val in real_solutions:
                    float_x = float(val)
                    float_y = float(expr_f1.subs(x, float_x))
                    intersections.append((float_x, float_y))

                # Plot the functions and all intersection points
                self.plot_functions(expr_f1, expr_f2, intersections=intersections)

        except Exception as e:
            # Show error message if any exception occurs
            err_msg = f"An error occurred:\n{traceback.format_exc()}"
            self.show_error_message(err_msg)

    def plot_functions(self, expr_f1, expr_f2, intersections):
        """
        Clears the canvas and plots the two functions over a chosen range.
        Marks and annotates all intersection points in `intersections` if not empty.

        :param expr_f1: Sympy expression for f1(x)
        :param expr_f2: Sympy expression for f2(x)
        :param intersections: list of (x, y) real intersection points. May be empty.
        """
        self.canvas.axes.clear()
        import numpy as np
        x_sym = sympy.Symbol('x', real=True)

        # Decide the x-range for plotting
        if intersections:
            # If we have intersections, pick range from min_x - 2 to max_x + 2
            xs = [pt[0] for pt in intersections]
            min_sol_x, max_sol_x = min(xs), max(xs)
            x_min = min_sol_x - 5
            x_max = max_sol_x + 5
        else:
            # Default range if no intersection
            x_min, x_max = -10, 10

        x_vals = np.linspace(x_min, x_max, 400)

        # Evaluate the functions, skipping complex results
        f1_vals = []
        f2_vals = []
        for val in x_vals:
            y1 = expr_f1.subs(x_sym, val)
            y2 = expr_f2.subs(x_sym, val)

            # Convert y1 to float if real, otherwise NaN
            if y1.is_real:
                f1_vals.append(float(y1))
            else:
                f1_vals.append(np.nan)

            # Convert y2 to float if real, otherwise NaN
            if y2.is_real:
                f2_vals.append(float(y2))
            else:
                f2_vals.append(np.nan)

        # Plot the two functions
        self.canvas.axes.plot(x_vals, f1_vals, label="f1(x)")
        self.canvas.axes.plot(x_vals, f2_vals, label="f2(x)")

        # Draw x=0 and y=0 lines to represent axes
        self.canvas.axes.axhline(0, color='black', linewidth=0.8)
        self.canvas.axes.axvline(0, color='black', linewidth=0.8)

        # If we have intersection points, mark them all
        from adjustText import adjust_text

        texts = []
        for i, (sol_x, sol_y) in enumerate(intersections, start=1):
            self.canvas.axes.plot(sol_x, sol_y, 'ro')
            annotation_text = f"Solution {i}: x={sol_x:.4f}, y={sol_y:.4f}"
            txt = self.canvas.axes.text(sol_x, sol_y, annotation_text)
            texts.append(txt)
        
        # After plotting all text, call:
        adjust_text(texts, ax=self.canvas.axes)



        self.canvas.axes.set_xlabel("x")
        self.canvas.axes.set_ylabel("y")
        self.canvas.axes.set_title("Intersection of f1(x) and f2(x)")
        self.canvas.axes.legend()
        self.canvas.draw()


    def clear_plot(self):
        """Clears the plot area."""
        self.canvas.axes.clear()
        self.canvas.draw()

    def show_error_message(self, message):
        """Display an error message box."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.exec_()
        

    def show_info_message(self, message):
        """Display an informational message box."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle("Information")
        msg_box.exec_()
        

    def string_to_sympy_expr(self, expr_str):
        """
        Safely converts the user-entered string into a Sympy expression.
        Supports +, -, *, /, ^, log10(), sqrt(), and implicit multiplication
        (e.g., "5x" -> "5*x").

        1) Replace '^' with '**'.
        2) Perform basic validation that only allowed characters are present.
        3) Parse with Sympy's parse_expr and implicit multiplication.
        """
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

        # 1) Replace '^' with '**'
        expr_str = expr_str.replace('^', '**')

        # 2) Basic validation (optional but recommended to prevent malicious input).
        #    For example, we allow digits, x, log10, sqrt, and typical math symbols.
        safe_chars_regex = r"[0-9x\+\-\*/\(\)\.\s\*]"
        temp = expr_str.replace("log10", "").replace("sqrt", "")
        for char in temp:
            if not re.match(safe_chars_regex, char):
                raise ValueError(f"Illegal character detected: '{char}' in {expr_str}")

        # 3) Parse the string with implicit multiplication
        transformations = standard_transformations + (implicit_multiplication_application,)

        x = sympy.Symbol('x', real=True)
        local_dict = {
            "x": x,
            "log10": lambda arg: sympy.log(arg, 10),
            "sqrt": sympy.sqrt
        }

        expr_sympy = parse_expr(expr_str, local_dict=local_dict, transformations=transformations)
        return expr_sympy


def main():
    """
    Main entry point for the application.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
