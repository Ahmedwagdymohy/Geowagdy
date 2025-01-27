import sys
import math
import traceback
import re

from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QFont, QPixmap
from PySide2.QtWidgets import (
    QApplication,
    QSplashScreen,
    QProgressBar,
    QDesktopWidget,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QTabWidget,
    QTabBar,
    QMenuBar,
    QAction
)

import sympy
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

##############################################################################
# 1) A reusable PlotWidget class (replacing your old MainWindow code).
#    Inherits from QWidget, so we can embed it in a tab.
##############################################################################
class MplCanvas(FigureCanvasQTAgg):
    """A custom canvas to display matplotlib plots within a PySide2 widget."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        self.setParent(parent)


class PlotWidget(QWidget):
    """
    A widget for:
      - Two QLineEdits to input functions.
      - A "Solve + Plot" button.
      - An embedded Matplotlib canvas.
    
    This was refactored from your old MainWindow code so it can be used as a tab.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Main vertical layout
        main_layout = QVBoxLayout(self)

        # Row for function inputs
        input_layout = QHBoxLayout()
        self.label_f1 = QLabel("f1(x):")
        self.edit_f1 = QLineEdit()
        self.edit_f1.setPlaceholderText("e.g. 5x + 3 or 5*x + 3")

        self.label_f2 = QLabel("f2(x):")
        self.edit_f2 = QLineEdit()
        self.edit_f2.setPlaceholderText("e.g. 2x or 2*x")

        input_layout.addWidget(self.label_f1)
        input_layout.addWidget(self.edit_f1)
        input_layout.addWidget(self.label_f2)
        input_layout.addWidget(self.edit_f2)

        # Solve button
        self.solve_button = QPushButton("Solve + Plot")
        # Example button styling
        self.solve_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px;")

        # Plot canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Add everything to main_layout
        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.solve_button)
        main_layout.addWidget(self.canvas)

        # Connect signals
        self.solve_button.clicked.connect(self.on_solve_clicked)

    def on_solve_clicked(self):
        """
        Solve f1(x)=f2(x) for x (all real solutions), then plot the functions and mark solutions.
        """
        f1_str = self.edit_f1.text().strip()
        f2_str = self.edit_f2.text().strip()

        # Validate input
        if not f1_str or not f2_str:
            self.show_error_message("Both function fields must be filled.")
            self.clear_plot()
            return

        try:
            # Convert input strings to Sympy expressions
            expr_f1 = self.string_to_sympy_expr(f1_str)
            expr_f2 = self.string_to_sympy_expr(f2_str)

            # Solve
            x = sympy.Symbol('x', real=True)
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
                intersections = []
                for val in real_solutions:
                    float_x = float(val)
                    float_y = float(expr_f1.subs(x, float_x))
                    intersections.append((float_x, float_y))

                self.plot_functions(expr_f1, expr_f2, intersections)

        except Exception as e:
            err_msg = f"An error occurred:\n{traceback.format_exc()}"
            self.show_error_message(err_msg)

    def plot_functions(self, expr_f1, expr_f2, intersections):
        """Plot the two functions and mark intersection points."""
        import numpy as np
        self.canvas.axes.clear()

        x_sym = sympy.Symbol('x', real=True)

        # Decide range
        if intersections:
            xs = [pt[0] for pt in intersections]
            min_sol_x, max_sol_x = min(xs), max(xs)
            x_min = min_sol_x - 5
            x_max = max_sol_x + 5
        else:
            x_min, x_max = -10, 10

        x_vals = np.linspace(x_min, x_max, 400)

        f1_vals = []
        f2_vals = []
        for val in x_vals:
            y1 = expr_f1.subs(x_sym, val)
            y2 = expr_f2.subs(x_sym, val)
            f1_vals.append(float(y1) if y1.is_real else np.nan)
            f2_vals.append(float(y2) if y2.is_real else np.nan)

        # Plot
        self.canvas.axes.plot(x_vals, f1_vals, label="f1(x)")
        self.canvas.axes.plot(x_vals, f2_vals, label="f2(x)")

        # Draw axes
        self.canvas.axes.axhline(0, color='black', linewidth=0.8)
        self.canvas.axes.axvline(0, color='black', linewidth=0.8)

        # Mark intersections
        if intersections:
            from adjustText import adjust_text
            texts = []
            for i, (sol_x, sol_y) in enumerate(intersections, start=1):
                self.canvas.axes.plot(sol_x, sol_y, 'ro')
                annotation_text = f"Solution {i}: x={sol_x:.4f}, y={sol_y:.4f}"
                t = self.canvas.axes.text(sol_x, sol_y, annotation_text)
                texts.append(t)
            adjust_text(texts, ax=self.canvas.axes)

        self.canvas.axes.set_xlabel("x")
        self.canvas.axes.set_ylabel("y")
        self.canvas.axes.set_title("Intersection of f1(x) and f2(x)")
        self.canvas.axes.legend()
        self.canvas.draw()

    def clear_plot(self):
        self.canvas.axes.clear()
        self.canvas.draw()

    ####################################################################
    # Utility / Helper methods
    ####################################################################
    def show_error_message(self, msg):
        QMessageBox.critical(self, "Error", msg, QMessageBox.Ok)

    def show_info_message(self, msg):
        QMessageBox.information(self, "Information", msg, QMessageBox.Ok)

    def string_to_sympy_expr(self, expr_str):
        """Parse the user's function string into a Sympy expression (with implicit multiplication)."""
        expr_str = expr_str.replace('^', '**')  # Replace ^ with **
        safe_chars_regex = r"[0-9x\+\-\*/\(\)\.\s\*]"
        temp = expr_str.replace("log10", "").replace("sqrt", "")
        for char in temp:
            if not re.match(safe_chars_regex, char):
                raise ValueError(f"Illegal character detected: '{char}' in {expr_str}")

        transformations = standard_transformations + (implicit_multiplication_application,)
        x = sympy.Symbol('x', real=True)
        local_dict = {
            "x": x,
            "log10": lambda arg: sympy.log(arg, 10),
            "sqrt": sympy.sqrt
        }
        expr_sympy = parse_expr(expr_str, local_dict=local_dict, transformations=transformations)
        return expr_sympy

##############################################################################
# 2) The MainWindow that holds a QTabWidget. Each tab is a PlotWidget instance.
##############################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GeoWagdy with Tabs")
        self.setMinimumSize(1200, 800)

        # Create a QTabWidget
        self.tab_widget = QTabWidget()
        # Apply the style for QTabWidget and QTabBar (from your reference)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { /* The tab widget frame */
                border-top: 2px solid #C2C7CB;
            }
            QTabWidget::tab-bar {
                left: 5px; /* move to the right by 5px */
            }
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                            stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
                border: 2px solid #C4C4C3;
                border-bottom-color: #C2C7CB; /* same as the pane color */
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 2px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                            stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
            }
            QTabBar::tab:selected {
                border-color: #9B9B9B;
                border-bottom-color: #C2C7CB; /* same as pane color */
            }
            QTabBar::tab:!selected {
                margin-top: 2px; /* make non-selected tabs look smaller */
            }
        """)

        # Make the tab widget the central widget of the main window
        self.setCentralWidget(self.tab_widget)

        # We'll add an initial tab
        self.add_new_tab()

        # We can optionally add a menu or a button to create new tabs
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(self.add_new_tab)
        file_menu.addAction(new_tab_action)

    def add_new_tab(self):
        """Create a new PlotWidget and add it as a new tab."""
        new_plot_widget = PlotWidget()
        index = self.tab_widget.addTab(new_plot_widget, f"Plot {self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentIndex(index)

##############################################################################
# 3) The SplashScreen logic (with progress bar), then showing the MainWindow.
##############################################################################
class SplashScreen(QWidget):
    def __init__(self, width, height, main_window):
        super().__init__()

        self.main_window = main_window  # reference to the real main window

        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        self.setGeometry(x, y, width, height)
        self.setStyleSheet("background-color: black; border-radius: 10px;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Example image
        pixmap = QPixmap("1.png")
        if pixmap.isNull():
            print("Warning: splash image not found!")

        label = QLabel()
        scaled_pixmap = pixmap.scaled(width // 2, height // 2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignCenter)

        # Title
        message_label = QLabel("Geowagdy with Tabs!")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setFont(QFont("Times", 30, QFont.ExtraBold))
        message_label.setStyleSheet("color: white;")

        # Slogan
        slogan = QLabel("Solve and plot multiple function pairs in separate tabs!")
        slogan.setAlignment(Qt.AlignCenter)
        slogan.setFont(QFont("Arial", 13, QFont.ExtraBold))
        slogan.setStyleSheet("color: yellow;")

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #05B8CC;
                width: 20px;
            }
        """)

        layout.addWidget(label)
        layout.addWidget(message_label)
        layout.addWidget(slogan)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.progress_value = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)  # 30ms intervals

    def update_progress(self):
        self.progress_value += 1
        self.progress_bar.setValue(self.progress_value)
        if self.progress_value >= 100:
            self.timer.stop()
            self.close()
            self.main_window.show()

##############################################################################
# 4) main() entry point
##############################################################################
def main():
    app = QApplication(sys.argv)

    # Create the main window (with QTabWidget inside)
    window = MainWindow()

    # Create and show the splash screen
    splash = SplashScreen(1200, 800, window)
    splash.show()
    app.processEvents()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
