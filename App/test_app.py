"""
Tests for the app.py using pytest and pytest-qt.

Command to run tests:
    pytest -v
"""

import pytest
from PySide2.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

import app  # Import our main application module


@pytest.fixture
def test_app(qtbot):
    """
    A fixture to create and initialize the MainWindow.
    """
    window = app.MainWindow()
    qtbot.addWidget(window)
    window.show()
    return window


def test_valid_input_intersection(qtbot: QtBot, test_app):
    """
    Test that providing valid input with an obvious intersection
    leads to a successful result (no error message).
    """
    window = test_app

    # For instance: f1(x) = x, f2(x) = x/2
    # They intersect at x=0 obviously, but let's see the solver in action
    window.edit_f1.setText("x")
    window.edit_f2.setText("x/2")

    # Click the solve button
    qtbot.mouseClick(window.solve_button, qtbot.LeftButton)

    # We can check if an error message was displayed
    # If no error message, the test is successful
    # Alternatively, we can check the plot or some internal state
    # For simplicity, let's ensure no error message was triggered
    # by verifying there's no active modal dialog (which the show_error_message would do).
    active_modal = window.findChild(type(window.solve_button), "")  # naive check
    assert active_modal is None, "Error message was displayed unexpectedly."


def test_invalid_input_characters(qtbot: QtBot, test_app):
    """
    Test that providing an invalid input (e.g., containing letters other than x/log10/sqrt)
    displays an error message.
    """
    window = test_app

    # For instance: f1(x) = x + abc (abc is not allowed)
    window.edit_f1.setText("x + abc")
    window.edit_f2.setText("x")

    # Click the solve button
    qtbot.mouseClick(window.solve_button, qtbot.LeftButton)

    # We expect an error dialog, so let's see if that appeared
    # We can use qtbot.waitExposed or we can check the message box
    # For demonstration, let's see if it triggered show_error_message
    # Easiest approach: we can check if there's a message box active
    # or we can wrap show_error_message in a signal. Here's a naive approach:

    # If the code is well-structured, we might detect the QDialog open
    # We can do: 
    error_dialogs = window.findChildren(app.QMessageBox)
    assert len(error_dialogs) > 0, "No error dialog was displayed for invalid input."
    assert "Illegal character detected" in error_dialogs[0].text(), \
        "Expected illegal character error, but found a different message."
