from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QScrollArea,
    QDateEdit, QPushButton, QMessageBox, QLabel, QComboBox,
    QLineEdit, QGroupBox, QWidget
)
from PyQt5.QtCore import QDate, Qt, QSize
from PyQt5.QtGui import QIcon
from datetime import datetime
from utils.file_manager import save_survey_data_to_json, load_case_data_from_json
from utils.general import make_all_labels_copyable, create_dob_input, resource_path

class SurveyFormDailyRoutine(QDialog):
    def __init__(self, case_folder_name, parent=None, survey_data_to_edit=None):
        super().__init__(parent)
        self.case_folder_name = case_folder_name
        self.survey_data_to_edit = survey_data_to_edit
        self.case_data = load_case_data_from_json(case_folder_name)
        if not self.case_data:
            QMessageBox.critical(self, "خطأ", "فشل تحميل بيانات الحالة.")
            self.reject()
            return

        self.setWindowTitle("استبيان الروتين اليومي")
        self.setGeometry(250, 50, 800, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setWindowState(Qt.WindowMaximized)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        container_widget = QWidget()
        self.main_layout = QVBoxLayout(container_widget)
        
        self.setup_case_info_section()
        self.setup_survey_fields()
        
        self.button_box = QHBoxLayout()
        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon(resource_path("icons/save.png")))
        self.save_button.setIconSize(QSize(32, 32))
        self.save_button.setToolTip("حفظ")
        self.save_button.clicked.connect(self.save_survey_data)
        self.cancel_button = QPushButton()
        self.cancel_button.setIcon(QIcon(resource_path("icons/cancel.png")))
        self.cancel_button.setIconSize(QSize(32, 32))
        self.cancel_button.setToolTip("إلغاء")
        self.cancel_button.clicked.connect(self.reject)
        self.button_box.addStretch()
        self.button_box.addWidget(self.save_button)
        self.button_box.addWidget(self.cancel_button)
        self.main_layout.addLayout(self.button_box)
        
        scroll.setWidget(container_widget)
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll)
        
        if self.survey_data_to_edit:
            self.load_survey_data()
        
        self.apply_styles()
        make_all_labels_copyable(self)

    def setup_case_info_section(self):
        case_info_group = QGroupBox("معلومات الحالة")
        case_info_layout = QFormLayout()
        case_info_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        case_info_layout.setLabelAlignment(Qt.AlignRight)
        case_info_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        
        case_id = self.case_data.get("case_id", "-")
        child_name = self.case_data.get("child_name", {}).get("value", "-")
        dob = self.case_data.get("dob", {}).get("value", "-")
        age = self.case_data.get("age", {}).get("value", "-")
        gender = self.case_data.get("gender", {}).get("value", "-")
        diagnosis = self.case_data.get("diagnosis", {}).get("value", "-")
        
        case_info_layout.addRow(QLabel("رقم الحالة:"), QLabel(str(case_id)))
        case_info_layout.addRow(QLabel("اسم الحالة:"), QLabel(child_name))
        case_info_layout.addRow(QLabel("تاريخ الميلاد:"), QLabel(dob))
        case_info_layout.addRow(QLabel("العمر:"), QLabel(age))
        case_info_layout.addRow(QLabel("الجنس:"), QLabel(gender))
        case_info_layout.addRow(QLabel("التشخيص:"), QLabel(diagnosis))
        
        case_info_group.setLayout(case_info_layout)
        self.main_layout.addWidget(case_info_group)

    def setup_survey_fields(self):
        survey_group = QGroupBox("أسئلة الروتين اليومي")
        survey_layout = QFormLayout()
        survey_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        survey_layout.setLabelAlignment(Qt.AlignRight)
        survey_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)

        self.survey_date_label = QLabel("تاريخ التقييم:")
        # self.survey_date_edit = QDateEdit()
        # self.survey_date_edit.setDate(QDate.currentDate())
        # self.survey_date_edit.setCalendarPopup(True)
        # self.survey_date_edit.setDisplayFormat("yyyy-MM-dd")
        # self.survey_date_edit.setFixedWidth(325)
        # self.survey_date_edit.setFixedHeight(40)
        # self.survey_date_edit.wheelEvent = lambda event: event.ignore()
        # survey_layout.addRow(self.survey_date_label, self.survey_date_edit)

        survey_date_widget, self.survey_date_edit, self.day_edit, self.month_edit, self.year_edit = create_dob_input(default_years_ago=0)
        survey_layout.addRow(self.survey_date_label, survey_date_widget)

        self.sleep_pattern_label = QLabel("نمط النوم:")
        self.sleep_pattern_combo = QComboBox()
        self.sleep_pattern_combo.addItems(["منتظم ومستقر", "متقطع", "صعوبة في النوم"])
        self.sleep_pattern_combo.setFixedWidth(325)
        self.sleep_pattern_combo.setFixedHeight(40)
        self.sleep_pattern_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.sleep_pattern_label, self.sleep_pattern_combo)

        self.eating_habits_label = QLabel("عادات الأكل:")
        self.eating_habits_combo = QComboBox()
        self.eating_habits_combo.addItems(["يأكل بشكل مستقل", "يحتاج مساعدة بسيطة", "يحتاج مساعدة كاملة"])
        self.eating_habits_combo.setFixedWidth(325)
        self.eating_habits_combo.setFixedHeight(40)
        self.eating_habits_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.eating_habits_label, self.eating_habits_combo)

        self.toilet_training_label = QLabel("التدريب على الحمام:")
        self.toilet_training_combo = QComboBox()
        self.toilet_training_combo.addItems(["مدرب بالكامل", "في مرحلة التدريب", "لم يبدأ التدريب"])
        self.toilet_training_combo.setFixedWidth(325)
        self.toilet_training_combo.setFixedHeight(40)
        self.toilet_training_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.toilet_training_label, self.toilet_training_combo)

        self.daily_routine_notes_label = QLabel("ملاحظات إضافية:")
        self.daily_routine_notes_edit = QLineEdit()
        self.daily_routine_notes_edit.setFixedWidth(325)
        self.daily_routine_notes_edit.setFixedHeight(40)
        survey_layout.addRow(self.daily_routine_notes_label, self.daily_routine_notes_edit)

        survey_group.setLayout(survey_layout)
        self.main_layout.addWidget(survey_group)

    def collect_survey_data(self):
        survey_data = {
            "survey_type": "استبيان الروتين اليومي",
            "survey_date": self.survey_date_edit.date().toString("yyyy-MM-dd"),
            "submission_timestamp": datetime.now().isoformat()
        }
        def field_value(label_widget, input_widget, use_current_text=True):
            key = label_widget.text().replace(':', '').replace('؟', '').strip()
            value = input_widget.currentText() if use_current_text else input_widget.text().strip()
            return { "ar_key": key, "value": value }

        survey_data.update({
            "sleep_pattern": field_value(self.sleep_pattern_label, self.sleep_pattern_combo, True),
            "eating_habits": field_value(self.eating_habits_label, self.eating_habits_combo, True),
            "toilet_training": field_value(self.toilet_training_label, self.toilet_training_combo, True),
            "daily_routine_notes": field_value(self.daily_routine_notes_label, self.daily_routine_notes_edit, False),
        })
        return survey_data

    def load_survey_data(self):
        if not self.survey_data_to_edit:
            return
        
        survey_date_str = self.survey_data_to_edit.get("survey_date", "")
        survey_date = QDate.fromString(survey_date_str, "yyyy-MM-dd")
        if survey_date_str:
            self.survey_date_edit.setDate(survey_date)
            self.day_edit.setText("{:02}".format(survey_date.day()))
            self.month_edit.setText("{:02}".format(survey_date.month()))
            self.year_edit.setText("{:02}".format(survey_date.year()))

        def set_widget_value(widget, key):
            value = self.survey_data_to_edit.get(key, {}).get("value", "")
            if isinstance(widget, QComboBox):
                widget.setCurrentText(value)
            elif isinstance(widget, QLineEdit):
                widget.setText(value)

        set_widget_value(self.sleep_pattern_combo, "sleep_pattern")
        set_widget_value(self.eating_habits_combo, "eating_habits")
        set_widget_value(self.toilet_training_combo, "toilet_training")
        set_widget_value(self.daily_routine_notes_edit, "daily_routine_notes")

    def save_survey_data(self):
        survey_data = self.collect_survey_data()
        success, message = save_survey_data_to_json(self.case_folder_name, survey_data)
        if success:
            QMessageBox.information(self, "تم الحفظ", "تم حفظ بيانات الاستبيان بنجاح.")
            self.accept()
        else:
            QMessageBox.critical(self, "خطأ في الحفظ", f"فشل حفظ بيانات الاستبيان:\n{message}")

    def apply_styles(self):
        self.setStyleSheet("""""")
