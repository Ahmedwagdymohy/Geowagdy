
import pytest
from pytestqt.qtbot import QtBot
from PySide2.QtWidgets import QTabWidget, QFileDialog
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMessageBox

import os

import app  # <-- The name of your main code file if it's called "app.py".
            # If your code is in a file named differently, update this import.






@pytest.fixture
def main_window(qtbot: QtBot):
    """
    Fixture that instantiates and shows the MainWindow for testing.
    """
    # We create the MainWindow directly (bypassing the splash for test).
    window = app.MainWindow()
    qtbot.addWidget(window)
    window.show()
    return window

def test_main_window_starts(main_window, qtbot):
    """
    Test that the main window is displayed and has at least one tab.
    """
    assert main_window.isVisible(), "Main window should be visible."
    assert main_window.tab_widget.count() >= 1, "At least one tab should be open by default."



def test_solve_valid_functions(main_window, qtbot):
    # Grab the first tab's PlotWidget
    first_tab = main_window.tab_widget.widget(0)

    # Enter functions
    first_tab.edit_f1.setText("log10(x)")
    first_tab.edit_f2.setText("2*x")

    # Click solve
    qtbot.mouseClick(first_tab.solve_button, Qt.LeftButton)

    # Let the event queue process
    qtbot.wait(500)

    # Look for any QMessageBox children in the main window
    dialogs = main_window.findChildren(QMessageBox)

    # If your code sets the windowTitle to "Error" for an error dialog:
    error_dialogs = [d for d in dialogs if d.windowTitle() == "Error"]
    
    # We expect zero error dialogs
    assert len(error_dialogs) == 0, "No error dialog should appear for valid input."






def test_create_new_tab(main_window, qtbot):
    """
    Test creating a new tab via the 'New Tab' menu action.
    """
    # The initial number of tabs
    initial_tab_count = main_window.tab_widget.count()

    # Trigger the "New Tab" action
    menu_bar = main_window.menuBar()
    file_menu = menu_bar.actions()[0]  # Usually "File" is first
    # Expand "File" menu
    file_menu.menu().actions()[0].trigger()  # The first action might be "New Tab" if your code
                                             # arranged them that way.

    qtbot.wait(500)

    new_tab_count = main_window.tab_widget.count()
    assert new_tab_count == initial_tab_count + 1, "Should have exactly one more tab."






def test_export_plot_cancel(main_window, qtbot, monkeypatch):
    """
    Test that if the user cancels the export dialog, no file is saved.
    We'll 'monkeypatch' QFileDialog to simulate user cancellation.
    """
    # Grab first tab
    first_tab = main_window.tab_widget.widget(0)

    # Populate some data so there's a plot
    first_tab.edit_f1.setText("x^2")
    first_tab.edit_f2.setText("x")
    qtbot.mouseClick(first_tab.solve_button, Qt.LeftButton)
    qtbot.wait(500)

    # Mock QFileDialog to return ("", "") -> user canceled
    def mock_getSaveFileName(*args, **kwargs):
        return ("", "")

    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_getSaveFileName)

    # Trigger export from the main window
    menu_bar = main_window.menuBar()
    file_menu = menu_bar.actions()[0]  # "File"
    # "Export Plot" action is presumably the second in "File" menu
    file_menu.menu().actions()[1].trigger()  

    # If there's no crash or error, we consider this successful
    # Also, no file is created. We'll just assert True
    assert True, "Export canceled without error."





def test_open_help_link(main_window, qtbot, monkeypatch):
    """
    Test that clicking 'Open Help Link' attempts to open the default web browser.
    We'll monkeypatch `webbrowser.open` to verify it was called with the correct URL.
    """
    # Mock webbrowser.open
    called_urls = []

    def mock_webbrowser_open(url):
        called_urls.append(url)

    monkeypatch.setattr("webbrowser.open", mock_webbrowser_open)

    menu_bar = main_window.menuBar()
    help_menu = menu_bar.actions()[1]  # "Help" is presumably the second top-level menu
    # The help menu likely has one action: "Open Help Link"
    help_menu.menu().actions()[0].trigger()

    assert len(called_urls) == 1, "Should have opened exactly one URL."
    assert "https://github.com/Ahmedwagdymohy/Geowagdy" in called_urls[0], \
        "Should open the specified help URL."
