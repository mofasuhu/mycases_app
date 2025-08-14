from PyQt5.QtWidgets import QDateEdit, QLineEdit, QLabel, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QIntValidator


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


        # self.dob_edit = QDateEdit()
        # self.dob_edit.setDate(QDate.currentDate().addYears(-5))
        # self.dob_edit.setCalendarPopup(True)
        # self.dob_edit.setDisplayFormat("yyyy-MM-dd")
        # self.dob_edit.dateChanged.connect(self.calculate_age)
        # self.dob_edit.setAlignment(Qt.AlignRight)
        # self.dob_edit.setFixedWidth(325)
        # self.dob_edit.setFixedHeight(40)
        # self.dob_edit.wheelEvent = lambda event: event.ignore()
        # child_layout.addRow(QLabel("تاريخ الميلاد:"), self.dob_edit)


        # # --- Create QDateEdit as usual ---
        # self.dob_edit = QDateEdit()
        # self.dob_edit.setDate(QDate.currentDate().addYears(-5))
        # self.dob_edit.setCalendarPopup(True)
        # self.dob_edit.setDisplayFormat("yyyy-MM-dd")
        # self.dob_edit.dateChanged.connect(self.calculate_age)
        # self.dob_edit.setAlignment(Qt.AlignRight)
        # self.dob_edit.setFixedWidth(325)
        # self.dob_edit.setFixedHeight(40)
        # self.dob_edit.wheelEvent = lambda event: event.ignore()
        # # --- Create three line edits for day, month, year ---
        # self.day_edit = QLineEdit()
        # self.day_edit.setPlaceholderText("00")
        # self.day_edit.setMaxLength(2)
        # self.day_edit.setFixedWidth(50)
        # self.day_edit.setAlignment(Qt.AlignCenter)
        # self.day_edit.setValidator(QIntValidator(1, 31))
        # self.month_edit = QLineEdit()
        # self.month_edit.setPlaceholderText("00")
        # self.month_edit.setMaxLength(2)
        # self.month_edit.setFixedWidth(50)
        # self.month_edit.setAlignment(Qt.AlignCenter)
        # self.month_edit.setValidator(QIntValidator(1, 12))
        # self.year_edit = QLineEdit()
        # self.year_edit.setPlaceholderText("0000")
        # self.year_edit.setMaxLength(4)
        # self.year_edit.setFixedWidth(80)
        # self.year_edit.setAlignment(Qt.AlignCenter)
        # max_year = int(QDate.currentDate().year())
        # self.year_edit.setValidator(QIntValidator(1900, max_year))
        # default_dob = self.dob_edit.date()
        # self.day_edit.setText("{:02}".format(default_dob.day()))
        # self.month_edit.setText("{:02}".format(default_dob.month()))
        # self.year_edit.setText("{:02}".format(default_dob.year()))
        # # --- Function to sync inputs into dob_edit ---
        # def update_dob_edit():
        #     day = self.day_edit.text()
        #     month = self.month_edit.text()
        #     year = self.year_edit.text()
        #     if day and month and year:
        #         try:
        #             day_int = int(day)
        #             month_int = int(month)
        #             year_int = int(year)
        #             current_year = QDate.currentDate().year()

        #             # Check custom logic
        #             if 1900 <= year_int <= current_year:
        #                 vdate = QDate(year_int, month_int, day_int)
        #                 if vdate.isValid():
        #                     self.dob_edit.setDate(vdate)
        #                     self.day_edit.setStyleSheet("")
        #                     self.month_edit.setStyleSheet("")
        #                     self.year_edit.setStyleSheet("")
        #                     return
        #         except ValueError:
        #             pass
        #     # Highlight invalid input
        #     self.day_edit.setStyleSheet("background-color: pink;")
        #     self.month_edit.setStyleSheet("background-color: pink;")
        #     self.year_edit.setStyleSheet("background-color: pink;")
        # # --- Connect custom inputs to sync ---
        # self.day_edit.textChanged.connect(update_dob_edit)
        # self.month_edit.textChanged.connect(update_dob_edit)
        # self.year_edit.textChanged.connect(update_dob_edit)
        # # --- Layout the three fields ---
        # date_input_widget = QWidget()
        # date_input_layout = QHBoxLayout(date_input_widget)
        # date_input_layout.setContentsMargins(0, 0, 0, 0)
        # date_input_layout.setSpacing(5)
        # date_input_layout.addWidget(self.day_edit)
        # date_input_layout.addWidget(self.month_edit)
        # date_input_layout.addWidget(self.year_edit)
        # # --- Add to layout: show inputs, but keep QDateEdit hidden or minimized ---
        # hidden_dob_widget = QWidget()
        # hidden_dob_layout = QVBoxLayout(hidden_dob_widget)
        # hidden_dob_layout.setContentsMargins(0, 0, 0, 0)
        # hidden_dob_layout.addWidget(date_input_widget)
        # hidden_dob_layout.addWidget(self.dob_edit)
        # self.dob_edit.hide()
        # child_layout.addRow(QLabel("تاريخ الميلاد:"), hidden_dob_widget)





        # # Add father DOB field
        # self.father_dob_edit = QDateEdit()
        # self.father_dob_edit.setDate(QDate.currentDate().addYears(-30))  # Default age
        # self.father_dob_edit.setCalendarPopup(True)
        # self.father_dob_edit.setDisplayFormat("yyyy-MM-dd")
        # self.father_dob_edit.dateChanged.connect(self.calculate_father_age)
        # self.father_dob_edit.setAlignment(Qt.AlignRight)
        # self.father_dob_edit.setFixedWidth(325)
        # self.father_dob_edit.setFixedHeight(40)
        # self.father_dob_edit.wheelEvent = lambda event: event.ignore()
        # parents_layout.addRow(QLabel("تاريخ ميلاد الأب:"), self.father_dob_edit)



        # # Add mother DOB field
        # self.mother_dob_edit = QDateEdit()
        # self.mother_dob_edit.setDate(QDate.currentDate().addYears(-25))  # Default age
        # self.mother_dob_edit.setCalendarPopup(True)
        # self.mother_dob_edit.setDisplayFormat("yyyy-MM-dd")
        # self.mother_dob_edit.dateChanged.connect(self.calculate_mother_age)
        # self.mother_dob_edit.setAlignment(Qt.AlignRight)
        # self.mother_dob_edit.setFixedWidth(325)
        # self.mother_dob_edit.setFixedHeight(40)
        # self.mother_dob_edit.wheelEvent = lambda event: event.ignore()
        # parents_layout.addRow(QLabel("تاريخ ميلاد الأم:"), self.mother_dob_edit)



        # # Survey date field
        # self.survey_date_label = QLabel("تاريخ التقيم:")
        # self.survey_date_edit = QDateEdit()
        # self.survey_date_edit.setDate(QDate.currentDate())
        # self.survey_date_edit.setCalendarPopup(True)
        # self.survey_date_edit.setDisplayFormat("yyyy-MM-dd")
        # self.survey_date_edit.setFixedWidth(325)
        # self.survey_date_edit.setFixedHeight(40)
        # survey_layout.addRow(self.survey_date_label, self.survey_date_edit)
