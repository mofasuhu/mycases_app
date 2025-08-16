from PyQt5.QtWidgets import QDateEdit, QLineEdit, QLabel, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QIntValidator

import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not running as a bundled exe, the base path is the project's root
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(base_path, relative_path)


def make_all_labels_copyable(widget):
    for label in widget.findChildren(QLabel):
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)


def create_dob_input(default_years_ago=5, on_date_changed=None):
    # Create QDateEdit
    dob_edit = QDateEdit()
    dob_edit.setDate(QDate.currentDate().addYears(-default_years_ago))
    dob_edit.setCalendarPopup(True)
    dob_edit.setDisplayFormat("yyyy-MM-dd")
    dob_edit.setAlignment(Qt.AlignRight)
    dob_edit.setFixedWidth(325)
    dob_edit.setFixedHeight(40)
    dob_edit.wheelEvent = lambda event: event.ignore()

    if on_date_changed:
        dob_edit.dateChanged.connect(on_date_changed)

    # Create Day/Month/Year inputs
    day_edit = QLineEdit()
    day_edit.setPlaceholderText("00")
    day_edit.setMaxLength(2)
    day_edit.setFixedWidth(50)
    day_edit.setAlignment(Qt.AlignCenter)
    day_edit.setValidator(QIntValidator(1, 31))

    month_edit = QLineEdit()
    month_edit.setPlaceholderText("00")
    month_edit.setMaxLength(2)
    month_edit.setFixedWidth(50)
    month_edit.setAlignment(Qt.AlignCenter)
    month_edit.setValidator(QIntValidator(1, 12))

    year_edit = QLineEdit()
    year_edit.setPlaceholderText("0000")
    year_edit.setMaxLength(4)
    year_edit.setFixedWidth(80)
    year_edit.setAlignment(Qt.AlignCenter)
    max_year = int(QDate.currentDate().year())
    year_edit.setValidator(QIntValidator(1900, max_year))

    # Set default date values
    default_dob = dob_edit.date()
    day_edit.setText(f"{default_dob.day():02}")
    month_edit.setText(f"{default_dob.month():02}")
    year_edit.setText(f"{default_dob.year():04}")

    # Update function
    def update_dob_edit():
        day = day_edit.text()
        month = month_edit.text()
        year = year_edit.text()
        if day and month and year:
            try:
                day_int = int(day)
                month_int = int(month)
                year_int = int(year)
                current_year = QDate.currentDate().year()
                if 1900 <= year_int <= current_year:
                    vdate = QDate(year_int, month_int, day_int)
                    if vdate.isValid():
                        dob_edit.setDate(vdate)
                        day_edit.setStyleSheet("")
                        month_edit.setStyleSheet("")
                        year_edit.setStyleSheet("")
                        return
            except ValueError:
                pass
        # Invalid input
        day_edit.setStyleSheet("background-color: pink;")
        month_edit.setStyleSheet("background-color: pink;")
        year_edit.setStyleSheet("background-color: pink;")

    day_edit.textChanged.connect(update_dob_edit)
    month_edit.textChanged.connect(update_dob_edit)
    year_edit.textChanged.connect(update_dob_edit)

    # Assemble layout
    date_input_widget = QWidget()
    date_input_layout = QHBoxLayout(date_input_widget)
    date_input_layout.setContentsMargins(0, 0, 0, 0)
    date_input_layout.setSpacing(5)
    date_input_layout.addWidget(day_edit)
    date_input_layout.addWidget(month_edit)
    date_input_layout.addWidget(year_edit)

    hidden_dob_widget = QWidget()
    hidden_dob_layout = QVBoxLayout(hidden_dob_widget)
    hidden_dob_layout.setContentsMargins(0, 0, 0, 0)
    hidden_dob_layout.addWidget(date_input_widget)
    hidden_dob_layout.addWidget(dob_edit)
    dob_edit.hide()

    return hidden_dob_widget, dob_edit, day_edit, month_edit, year_edit

