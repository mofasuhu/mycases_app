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

class SurveyFormSocialInteraction(QDialog):
    def __init__(self, case_folder_name, parent=None, survey_data_to_edit=None):
        super().__init__(parent)
        self.case_folder_name = case_folder_name
        self.survey_data_to_edit = survey_data_to_edit
        self.case_data = load_case_data_from_json(case_folder_name)
        if not self.case_data:
            QMessageBox.critical(self, "خطأ", "فشل تحميل بيانات الحالة.")
            self.reject()
            return

        self.setWindowTitle("استبيان التفاعل الاجتماعي")
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
        survey_group = QGroupBox("أسئلة التفاعل الاجتماعي")
        survey_layout = QFormLayout()
        survey_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        survey_layout.setLabelAlignment(Qt.AlignRight)
        survey_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)

        self.survey_date_label = QLabel("تاريخ التقييم:")
        # self.survey_date_edit = QDateEdit(QDate.currentDate())
        # self.survey_date_edit.setCalendarPopup(True)
        # self.survey_date_edit.setDisplayFormat("yyyy-MM-dd")
        # self.survey_date_edit.setFixedWidth(325)
        # self.survey_date_edit.setFixedHeight(40)
        # self.survey_date_edit.wheelEvent = lambda event: event.ignore()
        # survey_layout.addRow(self.survey_date_label, self.survey_date_edit)

        survey_date_widget, self.survey_date_edit, self.day_edit, self.month_edit, self.year_edit = create_dob_input(default_years_ago=0)
        survey_layout.addRow(self.survey_date_label, survey_date_widget)


        self.interaction_peers_label = QLabel("التفاعل مع الأقران:")
        self.interaction_peers_combo = QComboBox()
        self.interaction_peers_combo.addItems(["يبادر باللعب", "يشارك إذا طُلب منه", "يفضل اللعب منفرداً"])
        self.interaction_peers_combo.setFixedWidth(325)
        self.interaction_peers_combo.setFixedHeight(40)
        self.interaction_peers_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.interaction_peers_label, self.interaction_peers_combo)

        self.interaction_adults_label = QLabel("التفاعل مع البالغين:")
        self.interaction_adults_combo = QComboBox()
        self.interaction_adults_combo.addItems(["يتفاعل بسهولة", "خجول أو متردد", "يتجنب التفاعل"])
        self.interaction_adults_combo.setFixedWidth(325)
        self.interaction_adults_combo.setFixedHeight(40)
        self.interaction_adults_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.interaction_adults_label, self.interaction_adults_combo)

        self.eye_contact_label = QLabel("التواصل البصري:")
        self.eye_contact_combo = QComboBox()
        self.eye_contact_combo.addItems(["جيد ومستمر", "متقطع", "ضعيف أو نادر"])
        self.eye_contact_combo.setFixedWidth(325)
        self.eye_contact_combo.setFixedHeight(40)
        self.eye_contact_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.eye_contact_label, self.eye_contact_combo)

        self.social_notes_label = QLabel("ملاحظات إضافية:")
        self.social_notes_edit = QLineEdit()
        self.social_notes_edit.setFixedWidth(325)
        self.social_notes_edit.setFixedHeight(40)
        survey_layout.addRow(self.social_notes_label, self.social_notes_edit)

        survey_group.setLayout(survey_layout)
        self.main_layout.addWidget(survey_group)

    def collect_survey_data(self):
        survey_data = {
            "survey_type": "استبيان التفاعل الاجتماعي",
            "survey_date": self.survey_date_edit.date().toString("yyyy-MM-dd"),
            "submission_timestamp": datetime.now().isoformat()
        }
        def field_value(label_widget, input_widget, use_current_text=True):
            key = label_widget.text().replace(':', '').replace('؟', '').strip()
            value = input_widget.currentText() if use_current_text else input_widget.text().strip()
            return { "ar_key": key, "value": value }

        survey_data.update({
            "interaction_with_peers": field_value(self.interaction_peers_label, self.interaction_peers_combo, True),
            "interaction_with_adults": field_value(self.interaction_adults_label, self.interaction_adults_combo, True),
            "eye_contact": field_value(self.eye_contact_label, self.eye_contact_combo, True),
            "social_interaction_notes": field_value(self.social_notes_label, self.social_notes_edit, False),
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

        set_widget_value(self.interaction_peers_combo, "interaction_with_peers")
        set_widget_value(self.interaction_adults_combo, "interaction_with_adults")
        set_widget_value(self.eye_contact_combo, "eye_contact")
        set_widget_value(self.social_notes_edit, "social_interaction_notes")

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
