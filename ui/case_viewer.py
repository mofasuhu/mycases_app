import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLabel, QScrollArea, QPushButton,
    QVBoxLayout, QHBoxLayout, QGroupBox, QMessageBox, QWidget,
    QListWidget, QListWidgetItem, QFileDialog, QGridLayout,
    QCheckBox, QFrame
)
from PyQt5.QtCore import Qt, QDate, QSize
from datetime import date
from PyQt5.QtGui import QIcon

from .survey_form_first import SurveyFormFirst
from .survey_form_motor_skills import SurveyFormMotorSkills
from .survey_form_social_interaction import SurveyFormSocialInteraction
from .survey_form_daily_routine import SurveyFormDailyRoutine
from .survey_form_communication import SurveyFormCommunication



from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.units import cm

try:
    from bidi.algorithm import get_display
    import arabic_reshaper
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False


from .case_form import CaseForm
from .pdf_exporter import export_survey_to_pdf_with_custom_path
from utils.file_manager import load_surveys_for_case, load_case_data_from_json, delete_survey_file, register_fonts
from utils.general import make_all_labels_copyable, resource_path

class SurveyDetailViewer(QDialog):
    def __init__(self, survey_data, case_folder_name, parent=None):
        super().__init__(parent)
        self.survey_data = survey_data
        self.case_folder_name = case_folder_name
        self.setWindowTitle(f"عرض تفاصيل الاستبيان: {self.survey_data.get('survey_type')} - {self.survey_data.get('survey_date')}")
        self.setGeometry(250, 50, 800, 600)        
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setWindowState(Qt.WindowMaximized)

        layout = QVBoxLayout(self)
        
        self.buttons_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("تعديل الاستبيان")
        self.edit_button.clicked.connect(self.edit_survey)
        self.buttons_layout.addWidget(self.edit_button)
        
        self.export_pdf_button = QPushButton("تصدير إلى PDF")
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        self.buttons_layout.addWidget(self.export_pdf_button)

        self.delete_button = QPushButton("حذف الاستبيان")
        self.delete_button.setStyleSheet("background-color: #ff4d4d; color: white;") # Make it stand out
        self.delete_button.clicked.connect(self.delete_survey)
        self.buttons_layout.addWidget(self.delete_button)

        layout.addLayout(self.buttons_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QFormLayout(scroll_content)
        scroll_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        scroll_layout.setLabelAlignment(Qt.AlignRight)
        scroll_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        
        scroll_layout.addRow(QLabel("نوع الاستبيان:"), QLabel(self.survey_data.get("survey_type", "-")))
        scroll_layout.addRow(QLabel("تاريخ الاستبيان:"), QLabel(self.survey_data.get("survey_date", "-")))


        skip_keys = ['survey_type', 'survey_date', 'submission_timestamp', 'case_id', 'child_name', 'dob', 'gender', '_filename']
        for key, value_dict in self.survey_data.items():
            if key not in skip_keys and isinstance(value_dict, dict):
                label = value_dict.get('ar_key', key)
                value = value_dict.get('value', '-')
                scroll_layout.addRow(QLabel(f"{label}:"), QLabel(str(value)))
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.button_box = QHBoxLayout()
        self.close_button = QPushButton()
        self.close_button.setIcon(QIcon(resource_path("icons/close.png")))
        self.close_button.setIconSize(QSize(32, 32))
        self.close_button.setToolTip("إغلاق")
        self.close_button.clicked.connect(self.reject)
        self.button_box.addStretch()
        self.button_box.addWidget(self.close_button)
        layout.addLayout(self.button_box)
        make_all_labels_copyable(self)

    def edit_survey(self):
        survey_type = self.survey_data.get("survey_type")
        edit_form = None

        if survey_type == "استبيان التقييم الأول":
            edit_form = SurveyFormFirst(self.case_folder_name, parent=self, survey_data_to_edit=self.survey_data)
        elif survey_type == "استبيان المهارات الحركية":
            edit_form = SurveyFormMotorSkills(self.case_folder_name, parent=self, survey_data_to_edit=self.survey_data)
        elif survey_type == "استبيان التفاعل الاجتماعي":
            edit_form = SurveyFormSocialInteraction(self.case_folder_name, parent=self, survey_data_to_edit=self.survey_data)
        elif survey_type == "استبيان الروتين اليومي":
            edit_form = SurveyFormDailyRoutine(self.case_folder_name, parent=self, survey_data_to_edit=self.survey_data)
        elif survey_type == "استبيان التواصل واللغة":
            edit_form = SurveyFormCommunication(self.case_folder_name, parent=self, survey_data_to_edit=self.survey_data)
        else:
            QMessageBox.warning(self, "غير مدعوم", f"تعديل هذا النوع من الاستبيانات ({survey_type}) غير مدعوم حاليًا.")
            return

        if edit_form:
            result = edit_form.exec_()
            if result == QDialog.Accepted:
                self.accept()  

    def export_to_pdf(self):
        case_data = load_case_data_from_json(self.case_folder_name)
        survey_type = self.survey_data.get("survey_type", "استبيان")
        survey_date = self.survey_data.get("survey_date", "").replace("-", "")
        child_name = case_data.get("child_name", {}).get("value", "حالة") if case_data else "حالة"
        default_filename = f"{survey_type}_{child_name}_{survey_date}.pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(self, "حفظ الملف", default_filename, "PDF Files (*.pdf)")
        if file_path:
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            
            success, message = export_survey_to_pdf_with_custom_path(
                self.survey_data,
                file_path,
                case_data_for_context=case_data
            )
            if success:
                QMessageBox.information(self, "تم التصدير", f"تم تصدير الاستبيان بنجاح")
            else:
                QMessageBox.critical(self, "خطأ في التصدير", f"فشل تصدير الاستبيان\n{message}")

    def delete_survey(self):        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("تأكيد الحذف")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText(f"هل أنت متأكد من حذف هذا الاستبيان نهائيًا؟")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
               
        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            # The filename was stored in the survey data when loaded
            filename = self.survey_data.get("_filename")
            if not filename:
                QMessageBox.critical(self, "خطأ", "لم يتم العثور على اسم ملف الاستبيان. لا يمكن الحذف.")
                return

            success, message = delete_survey_file(self.case_folder_name, filename + ".json")
            
            if success:
                QMessageBox.information(self, "تم الحذف", message)
                self.accept()  # Close the detail view and signal a refresh
            else:
                QMessageBox.critical(self, "خطأ في الحذف", message)


class SurveySelectionDialog(QDialog):
    """A dialog to allow users to select which surveys to export."""
    def __init__(self, surveys, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تحديد الاستبيانات للتصدير")
        self.setMinimumWidth(400)
        
        self.layout = QVBoxLayout(self)
        
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        
        self.scroll_content = QWidget()
        self.checkbox_layout = QVBoxLayout(self.scroll_content)
        
        self.checkboxes = []
        self.surveys = surveys

        # "Select All" checkbox
        self.select_all_checkbox = QCheckBox("تحديد الكل")
        self.select_all_checkbox.stateChanged.connect(self.toggle_all_checkboxes)
        self.checkbox_layout.addWidget(self.select_all_checkbox)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.checkbox_layout.addWidget(separator)

        # Individual survey checkboxes
        for survey in self.surveys:
            survey_type = survey.get("survey_type", "غير معروف")
            survey_date = survey.get("survey_date", "غير معروف")
            display_text = f"{survey_type} - {survey_date}"
            
            checkbox = QCheckBox(display_text)
            checkbox.setChecked(False) # Default not to selected
            self.checkboxes.append(checkbox)
            self.checkbox_layout.addWidget(checkbox)
            
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)
        
        # Buttons
        self.button_box = QHBoxLayout()
        self.ok_button = QPushButton("تصدير")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.clicked.connect(self.reject)
        
        self.button_box.addStretch()
        self.button_box.addWidget(self.ok_button)
        self.button_box.addWidget(self.cancel_button)
        
        self.layout.addLayout(self.button_box)

    def toggle_all_checkboxes(self, state):
        """Set all checkboxes to the state of the 'Select All' checkbox."""
        is_checked = (state == Qt.Checked)
        for checkbox in self.checkboxes:
            checkbox.setChecked(is_checked)

    def get_selected_surveys(self):
        """Return a list of survey data for the checked items."""
        selected = []
        for i, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked():
                selected.append(self.surveys[i])
        return selected
    

class CaseViewer(QDialog):
    def __init__(self, case_data, case_folder_name, parent=None):
        super().__init__(parent)
        self.case_data = case_data
        self.case_folder_name = case_folder_name
        self.parent_main_window = parent
        
        child_name_display = self.case_data.get("child_name", {}).get("value", "")
        self.setWindowTitle(f"عرض بيانات: {child_name_display}")
        self.setGeometry(250, 50, 800, 600)
        
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setWindowState(Qt.WindowMaximized)
        
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        container_widget = QWidget()
        self.main_layout = QVBoxLayout(container_widget)





        self.button_box = QHBoxLayout()

        self.edit_button = QPushButton()
        self.edit_button.setIcon(QIcon(resource_path("icons/edit.png")))
        self.edit_button.setIconSize(QSize(32, 32))
        self.edit_button.setToolTip("تعديل بيانات الحالة")
        self.edit_button.clicked.connect(self.edit_case_data)

        self.export_full_case_button = QPushButton()
        self.export_full_case_button.setIcon(QIcon(resource_path("icons/export.png")))
        self.export_full_case_button.setIconSize(QSize(32, 32))
        self.export_full_case_button.setToolTip("تصدير بيانات الحالة وكافة الاستبيانات إلى PDF")
        self.export_full_case_button.clicked.connect(self.export_full_case_to_pdf)

        self.button_box.addStretch()
        self.button_box.addWidget(self.edit_button)
        self.button_box.addWidget(self.export_full_case_button)
        self.main_layout.addLayout(self.button_box)



        child_group = QGroupBox("بيانات الحالة")
        child_layout = QFormLayout()
        child_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)  
        child_layout.setLabelAlignment(Qt.AlignRight)
        child_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.child_name_label = QLabel(self.case_data.get("child_name", {}).get("value", "-"))
        self.child_name_label.setFixedWidth(325)
        self.child_name_label.setFixedHeight(40)
        child_layout.addRow(QLabel("اسم الحالة:"), self.child_name_label)
        self.dob_label = QLabel(self.case_data.get("dob", {}).get("value", "-"))
        self.dob_label.setFixedWidth(325)
        self.dob_label.setFixedHeight(40)
        self.dob_label.setAlignment(Qt.AlignRight)
        child_layout.addRow(QLabel("تاريخ الميلاد:"), self.dob_label)
        self.age_label = QLabel("يتم حسابه")
        child_layout.addRow(QLabel("العمر:"), self.age_label)
        self.gender_label = QLabel(self.case_data.get("gender", {}).get("value", "-"))
        self.gender_label.setFixedWidth(325)
        self.gender_label.setFixedHeight(40)
        child_layout.addRow(QLabel("الجنس:"), self.gender_label)
        self.first_lang_label = QLabel(self.case_data.get("first_language", {}).get("value", "-"))
        self.first_lang_label.setFixedWidth(325)
        self.first_lang_label.setFixedHeight(40)
        child_layout.addRow(QLabel("اللغة الأولى:"), self.first_lang_label)
        self.first_lang_notes_label = QLabel(self.case_data.get("first_language_notes", {}).get("value", "-"))
        self.first_lang_notes_label.setFixedWidth(325)
        self.first_lang_notes_label.setFixedHeight(40)
        child_layout.addRow(QLabel("ملاحظات اللغة الأولى:"), self.first_lang_notes_label)
        self.second_lang_label = QLabel(self.case_data.get("second_language", {}).get("value", "-"))
        self.second_lang_label.setFixedWidth(325)
        self.second_lang_label.setFixedHeight(40)
        child_layout.addRow(QLabel("اللغة الثانية:"), self.second_lang_label)
        self.second_lang_notes_label = QLabel(self.case_data.get("second_language_notes", {}).get("value", "-"))
        self.second_lang_notes_label.setFixedWidth(325)
        self.second_lang_notes_label.setFixedHeight(40)
        child_layout.addRow(QLabel("ملاحظات اللغة الثانية:"), self.second_lang_notes_label)
        self.diagnosis_label = QLabel(self.case_data.get("diagnosis", {}).get("value", "-"))
        self.diagnosis_label.setFixedWidth(325)
        self.diagnosis_label.setFixedHeight(40)
        child_layout.addRow(QLabel("التشخيص:"), self.diagnosis_label)
        self.diagnosed_by_label = QLabel(self.case_data.get("diagnosed_by", {}).get("value", "-"))
        self.diagnosed_by_label.setFixedWidth(325)
        self.diagnosed_by_label.setFixedHeight(40)
        child_layout.addRow(QLabel("بواسطة:"), self.diagnosed_by_label)
        child_group.setLayout(child_layout)
        self.main_layout.addWidget(child_group)
        
        parents_group = QGroupBox("بيانات الوالدين")
        parents_layout = QFormLayout()
        parents_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)  
        parents_layout.setLabelAlignment(Qt.AlignRight)
        parents_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.father_name_label = QLabel(self.case_data.get("father_name", {}).get("value", "-"))
        self.father_name_label.setFixedWidth(325)
        self.father_name_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("اسم الأب:"), self.father_name_label)
        self.father_dob_label = QLabel(self.case_data.get("father_dob", {}).get("value", "-"))
        self.father_dob_label.setFixedWidth(325)
        self.father_dob_label.setFixedHeight(40)
        self.father_dob_label.setAlignment(Qt.AlignRight)
        parents_layout.addRow(QLabel("تاريخ ميلاد الأب:"), self.father_dob_label)
        self.father_age_label = QLabel("يتم حسابه")
        parents_layout.addRow(QLabel("عمر الأب:"), self.father_age_label)
        self.father_job_label = QLabel(self.case_data.get("father_job", {}).get("value", "-"))
        self.father_job_label.setFixedWidth(325)
        self.father_job_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("وظيفة الأب:"), self.father_job_label)
        self.father_health_label = QLabel(self.case_data.get("father_health", {}).get("value", "-"))
        self.father_health_label.setFixedWidth(325)
        self.father_health_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("الحالة الصحية للأب:"), self.father_health_label)
        self.mother_name_label = QLabel(self.case_data.get("mother_name", {}).get("value", "-"))
        self.mother_name_label.setFixedWidth(325)
        self.mother_name_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("اسم الأم:"), self.mother_name_label)
        self.mother_dob_label = QLabel(self.case_data.get("mother_dob", {}).get("value", "-"))
        self.mother_dob_label.setFixedWidth(325)
        self.mother_dob_label.setFixedHeight(40)
        self.mother_dob_label.setAlignment(Qt.AlignRight)
        parents_layout.addRow(QLabel("تاريخ ميلاد الأم:"), self.mother_dob_label)
        self.mother_age_label = QLabel("يتم حسابه")
        parents_layout.addRow(QLabel("عمر الأم:"), self.mother_age_label)
        self.mother_job_label = QLabel(self.case_data.get("mother_job", {}).get("value", "-"))
        self.mother_job_label.setFixedWidth(325)
        self.mother_job_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("وظيفة الأم:"), self.mother_job_label)
        self.mother_health_label = QLabel(self.case_data.get("mother_health", {}).get("value", "-"))
        self.mother_health_label.setFixedWidth(325)
        self.mother_health_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("الحالة الصحية للأم:"), self.mother_health_label)
        self.father_preg_age_label = QLabel("يتم حسابه")
        parents_layout.addRow(QLabel("عمر الأب عند الولادة:"), self.father_preg_age_label)
        self.mother_preg_age_label = QLabel("يتم حسابه")
        parents_layout.addRow(QLabel("عمر الأم عند الولادة:"), self.mother_preg_age_label)
        self.parents_relation_label = QLabel(self.case_data.get("parents_relation", {}).get("value", "-"))
        self.parents_relation_label.setFixedWidth(325)
        self.parents_relation_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("صلة قرابة بين الوالدين؟"), self.parents_relation_label)
        
        if self.case_data.get("parents_relation", {}).get("value", "") =="نعم":
            self.relation_degree_label = QLabel("درجة القرابة:")
            self.relation_degree_value = QLabel(self.case_data.get("relation_degree", {}).get("value", "-"))
            self.relation_degree_value.setFixedWidth(325)
            self.relation_degree_value.setFixedHeight(40)
            parents_layout.addRow(self.relation_degree_label, self.relation_degree_value)
        parents_group.setLayout(parents_layout)
        self.main_layout.addWidget(parents_group)
        
        family_group = QGroupBox("معلومات الأسرة")
        family_layout = QFormLayout()
        family_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)  
        family_layout.setLabelAlignment(Qt.AlignRight)
        family_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        self.family_size_label = QLabel(str(self.case_data.get("family_size", {}).get("value", "-")))
        self.family_size_label.setFixedWidth(325)
        self.family_size_label.setFixedHeight(40)
        self.family_size_label.setAlignment(Qt.AlignRight)
        family_layout.addRow(QLabel("حجم الأسرة:"), self.family_size_label)
        self.siblings_count_label = QLabel(str(self.case_data.get("siblings_count", {}).get("value", "-")))
        self.siblings_count_label.setFixedWidth(325)
        self.siblings_count_label.setFixedHeight(40)
        self.siblings_count_label.setAlignment(Qt.AlignRight)
        family_layout.addRow(QLabel("عدد الإخوة:"), self.siblings_count_label)
        self.child_order_label = QLabel(str(self.case_data.get("child_order", {}).get("value", "-")))
        self.child_order_label.setFixedWidth(325)
        self.child_order_label.setFixedHeight(40)
        self.child_order_label.setAlignment(Qt.AlignRight)
        family_layout.addRow(QLabel("ترتيب الحالة بين الأخوة:"), self.child_order_label)
        self.similar_cases_label = QLabel(self.case_data.get("similar_cases_family", {}).get("value", "-"))
        self.similar_cases_label.setFixedWidth(325)
        self.similar_cases_label.setFixedHeight(40)
        family_layout.addRow(QLabel("حالات مشابهة في العائلة؟"), self.similar_cases_label)
        
        if self.case_data.get("similar_cases_family", {}).get("value", "") == "نعم":
            self.similar_cases_who_label = QLabel("من؟")
            self.similar_cases_who_value = QLabel(self.case_data.get("similar_cases_who", {}).get("value", "-"))
            self.similar_cases_who_value.setFixedWidth(325)
            self.similar_cases_who_value.setFixedHeight(40)
            family_layout.addRow(self.similar_cases_who_label, self.similar_cases_who_value)
        family_group.setLayout(family_layout)
        self.main_layout.addWidget(family_group)
        
        
        self.setup_surveys_section()
        scroll.setWidget(container_widget)
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll)
                
        self.calculate_all_ages()
        self.load_and_display_surveys()
        
        self.apply_styles()
        make_all_labels_copyable(self)

    def calculate_all_ages(self):
        self.calculate_age()
        self.calculate_father_age()
        self.calculate_mother_age()
        self.calculate_pregnancy_ages()

    def calculate_age(self):
        dob_str = self.case_data.get("dob", {}).get("value", "")
        if not dob_str:
            self.age_label.setText("تاريخ ميلاد غير متوفر")
            return
        try:
            dob_qdate = QDate.fromString(dob_str, "yyyy-MM-dd")
            if not dob_qdate.isValid():
                self.age_label.setText("تاريخ ميلاد غير صالح")
                return
            dob = date(dob_qdate.year(), dob_qdate.month(), dob_qdate.day())
            today = date.today()
            age_years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            age_months = (today.month - dob.month - (today.day < dob.day)) % 12
            if today.day < dob.day:
                prev_month_days = (QDate(today.year, today.month, 1).addMonths(-1)).daysInMonth()
                age_days = prev_month_days - dob.day + today.day
            else:
                age_days = today.day - dob.day
            self.age_label.setText(f"{age_years} سنة، {age_months} شهر، {age_days} يوم")
        except Exception as e:
            print(f"Error calculating age: {str(e)}")
            self.age_label.setText("خطأ في حساب العمر")

    def calculate_father_age(self):
        father_dob_str = self.case_data.get("father_dob", {}).get("value", "")
        if not father_dob_str:
            self.father_age_label.setText("-")
            return
        try:
            father_dob_qdate = QDate.fromString(father_dob_str, "yyyy-MM-dd")
            if not father_dob_qdate.isValid():
                self.father_age_label.setText("تاريخ ميلاد غير صالح")
                return
            father_dob = date(father_dob_qdate.year(), father_dob_qdate.month(), father_dob_qdate.day())
            today = date.today()
            father_age = today.year - father_dob.year - ((today.month, today.day) < (father_dob.month, father_dob.day))
            father_age_months = (today.month - father_dob.month - (today.day < father_dob.day)) % 12
            self.father_age_label.setText(f"{father_age} سنة، {father_age_months} شهر")
        except Exception as e:
            print(f"Error calculating father age: {str(e)}")
            self.father_age_label.setText("خطأ في حساب العمر")

    def calculate_mother_age(self):
        mother_dob_str = self.case_data.get("mother_dob", {}).get("value", "")
        if not mother_dob_str:
            self.mother_age_label.setText("-")
            return
        try:
            mother_dob_qdate = QDate.fromString(mother_dob_str, "yyyy-MM-dd")
            if not mother_dob_qdate.isValid():
                self.mother_age_label.setText("تاريخ ميلاد غير صالح")
                return
            mother_dob = date(mother_dob_qdate.year(), mother_dob_qdate.month(), mother_dob_qdate.day())
            today = date.today()
            mother_age = today.year - mother_dob.year - ((today.month, today.day) < (mother_dob.month, mother_dob.day))
            mother_age_months = (today.month - mother_dob.month - (today.day < mother_dob.day)) % 12
            self.mother_age_label.setText(f"{mother_age} سنة، {mother_age_months} شهر")
        except Exception as e:
            print(f"Error calculating mother age: {str(e)}")
            self.mother_age_label.setText("خطأ في حساب العمر")

    def calculate_pregnancy_ages(self):
        child_dob_str = self.case_data.get("dob", {}).get("value", "")
        if not child_dob_str:
            self.father_preg_age_label.setText("-")
            self.mother_preg_age_label.setText("-")
            return
        try:
            child_dob_qdate = QDate.fromString(child_dob_str, "yyyy-MM-dd")
            if not child_dob_qdate.isValid(): return
            child_dob = date(child_dob_qdate.year(), child_dob_qdate.month(), child_dob_qdate.day())
            
            father_dob_str = self.case_data.get("father_dob", {}).get("value", "")
            if father_dob_str:
                father_dob_qdate = QDate.fromString(father_dob_str, "yyyy-MM-dd")
                if father_dob_qdate.isValid():
                    father_dob = date(father_dob_qdate.year(), father_dob_qdate.month(), father_dob_qdate.day())
                    father_preg_age = child_dob.year - father_dob.year - ((child_dob.month, child_dob.day) < (father_dob.month, father_dob.day))
                    father_preg_age_months = (child_dob.month - father_dob.month - (child_dob.day < father_dob.day)) % 12
                    self.father_preg_age_label.setText(f"{father_preg_age} سنة، {father_preg_age_months} شهر")
            
            mother_dob_str = self.case_data.get("mother_dob", {}).get("value", "")
            if mother_dob_str:
                mother_dob_qdate = QDate.fromString(mother_dob_str, "yyyy-MM-dd")
                if mother_dob_qdate.isValid():
                    mother_dob = date(mother_dob_qdate.year(), mother_dob_qdate.month(), mother_dob_qdate.day())
                    mother_preg_age = child_dob.year - mother_dob.year - ((child_dob.month, child_dob.day) < (mother_dob.month, mother_dob.day))
                    mother_preg_age_months = (child_dob.month - mother_dob.month - (child_dob.day < mother_dob.day)) % 12
                    self.mother_preg_age_label.setText(f"{mother_preg_age} سنة، {mother_preg_age_months} شهر")
        except Exception as e:
            print(f"Error calculating pregnancy ages: {str(e)}")
            self.father_preg_age_label.setText("خطأ في حساب العمر")
            self.mother_preg_age_label.setText("خطأ في حساب العمر")

    def setup_surveys_section(self):
        self.surveys_group = QGroupBox("الاستبيانات والجلسات")
        self.surveys_layout = QVBoxLayout()
        
        self.survey_buttons_layout = QGridLayout()
        
        self.btn_add_first_survey = QPushButton("استبيان التقييم الأول")
        self.btn_add_first_survey.clicked.connect(self.add_first_survey)
        self.survey_buttons_layout.addWidget(self.btn_add_first_survey, 0, 0)

        self.btn_add_motor_skills = QPushButton("استبيان المهارات الحركية")
        self.btn_add_motor_skills.clicked.connect(self.add_motor_skills_survey)
        self.survey_buttons_layout.addWidget(self.btn_add_motor_skills, 0, 1)

        self.btn_add_social = QPushButton("استبيان التفاعل الاجتماعي")
        self.btn_add_social.clicked.connect(self.add_social_interaction_survey)
        self.survey_buttons_layout.addWidget(self.btn_add_social, 0, 2)

        self.btn_add_daily_routine = QPushButton("استبيان الروتين اليومي")
        self.btn_add_daily_routine.clicked.connect(self.add_daily_routine_survey)
        self.survey_buttons_layout.addWidget(self.btn_add_daily_routine, 1, 0)

        self.btn_add_communication = QPushButton("استبيان التواصل واللغة")
        self.btn_add_communication.clicked.connect(self.add_communication_survey)
        self.survey_buttons_layout.addWidget(self.btn_add_communication, 1, 1)

        self.surveys_layout.addLayout(self.survey_buttons_layout)
        
        self.survey_list_widget = QListWidget()
        self.survey_list_widget.itemDoubleClicked.connect(self.view_selected_survey)
        self.survey_list_widget.setFixedHeight(200)
        self.surveys_layout.addWidget(self.survey_list_widget)
        self.surveys_group.setLayout(self.surveys_layout)
        self.main_layout.addWidget(self.surveys_group)

    def _open_survey_form(self, FormClass):
        """Helper function to open a survey form and refresh the list on success."""
        survey_form = FormClass(self.case_folder_name, parent=self)
        if survey_form.exec_() == QDialog.Accepted:
            self.load_and_display_surveys()
            self.survey_list_widget.setEnabled(True)

    def add_first_survey(self):
        self._open_survey_form(SurveyFormFirst)

    def add_motor_skills_survey(self):
        self._open_survey_form(SurveyFormMotorSkills)

    def add_social_interaction_survey(self):
        self._open_survey_form(SurveyFormSocialInteraction)

    def add_daily_routine_survey(self):
        self._open_survey_form(SurveyFormDailyRoutine)

    def add_communication_survey(self):
        self._open_survey_form(SurveyFormCommunication)

    def load_and_display_surveys(self):
        self.survey_list_widget.clear()
        surveys = load_surveys_for_case(self.case_folder_name)
        if surveys:
            for survey_data in surveys:
                survey_type = survey_data.get("survey_type", "غير معروف")
                survey_date = survey_data.get("survey_date", "غير معروف")
                item_text = f'{survey_type} - {survey_date}'
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.UserRole, json.dumps(survey_data, ensure_ascii=False))
                self.survey_list_widget.addItem(list_item)
        else:
            self.survey_list_widget.addItem("لا توجد استبيانات مسجلة لهذه الحالة.")
            self.survey_list_widget.setEnabled(False)

    def view_selected_survey(self, item):
        try:
            survey_data_str = item.data(Qt.UserRole)
            if not survey_data_str: return
            survey_data = json.loads(survey_data_str)
            detail_viewer = SurveyDetailViewer(survey_data, self.case_folder_name, parent=self)
            if detail_viewer.exec_() == QDialog.Accepted:
                self.load_and_display_surveys()
        except (json.JSONDecodeError, TypeError) as e:
            QMessageBox.warning(self, "خطأ", f"لا يمكن عرض تفاصيل الاستبيان. البيانات غير صالحة: {e}")

    def edit_case_data(self):
        edit_form = CaseForm(parent=self, case_data_to_load=self.case_data)
        if edit_form.exec_() == QDialog.Accepted:
            updated_case_data = load_case_data_from_json(self.case_folder_name)
            if updated_case_data:
                self.case_data = updated_case_data
                self.update_display_with_new_data()
                self.accept()
            else:
                QMessageBox.warning(self, "خطأ", "فشل تحديث بيانات الحالة.")

    def update_display_with_new_data(self):
        self.child_name_label.setText(self.case_data.get("child_name", {}).get("value", "-"))
        self.dob_label.setText(self.case_data.get("dob", {}).get("value", "-"))
        self.gender_label.setText(self.case_data.get("gender", {}).get("value", "-"))
        self.first_lang_label.setText(self.case_data.get("first_language", {}).get("value", "-"))
        self.first_lang_notes_label.setText(self.case_data.get("first_language_notes", {}).get("value", "-"))
        self.second_lang_label.setText(self.case_data.get("second_language", {}).get("value", "-"))
        self.second_lang_notes_label.setText(self.case_data.get("second_language_notes", {}).get("value", "-"))
        self.diagnosis_label.setText(self.case_data.get("diagnosis", {}).get("value", "-"))
        self.diagnosed_by_label.setText(self.case_data.get("diagnosed_by", {}).get("value", "-"))
        
        self.father_name_label.setText(self.case_data.get("father_name", {}).get("value", "-"))
        self.father_dob_label.setText(self.case_data.get("father_dob", {}).get("value", "-"))
        self.father_job_label.setText(self.case_data.get("father_job", {}).get("value", "-"))
        self.father_health_label.setText(self.case_data.get("father_health", {}).get("value", "-"))
        self.mother_name_label.setText(self.case_data.get("mother_name", {}).get("value", "-"))
        self.mother_dob_label.setText(self.case_data.get("mother_dob", {}).get("value", "-"))
        self.mother_job_label.setText(self.case_data.get("mother_job", {}).get("value", "-"))
        self.mother_health_label.setText(self.case_data.get("mother_health", {}).get("value", "-"))
        self.parents_relation_label.setText(self.case_data.get("parents_relation", {}).get("value", "-"))
        
        self.family_size_label.setText(str(self.case_data.get("family_size", {}).get("value", "-")))
        self.siblings_count_label.setText(str(self.case_data.get("siblings_count", {}).get("value", "-")))
        self.child_order_label.setText(str(self.case_data.get("child_order", {}).get("value", "-")))
        self.similar_cases_label.setText(self.case_data.get("similar_cases_family", {}).get("value", "-"))
        
        self.calculate_all_ages()

    def apply_styles(self):
        self.setStyleSheet("""""")

    def export_full_case_to_pdf(self):
        def pdf_ar_fix(text):
            if not ARABIC_SUPPORT:
                return text
            try:
                return get_display(arabic_reshaper.reshape(str(text)))
            except:
                return text
        try:
            all_surveys = load_surveys_for_case(self.case_folder_name)

            # Show the selection dialog
            selection_dialog = SurveySelectionDialog(all_surveys, self)
            surveys_to_export = []
            if selection_dialog.exec_() == QDialog.Accepted:
                surveys_to_export = selection_dialog.get_selected_surveys()
            else:
                return # User cancelled

            register_fonts()

            ar_font = 'MyNoto'
            ar_font_bold = 'MyNotoBold'
            cell_style = ParagraphStyle(name='Cell', fontName=ar_font, fontSize=10, alignment=TA_RIGHT, leading=14, wordWrap='RTL')
            cell_style_bold = ParagraphStyle(name='CellBold', fontName=ar_font_bold, fontSize=10, alignment=TA_RIGHT, leading=14, wordWrap='RTL')
            header_name_style = ParagraphStyle(name='HeaderName', fontName=ar_font_bold, fontSize=18, alignment=TA_CENTER, textColor=colors.white, wordWrap='RTL')
            header_style = ParagraphStyle(name='Header', fontName=ar_font_bold, fontSize=18, alignment=TA_CENTER, spaceAfter=5, wordWrap='RTL')
            subheader_style = ParagraphStyle(name='SubHeader',fontName=ar_font,fontSize=10,alignment=TA_RIGHT,spaceAfter=5,wordWrap='RTL')
            section_style = ParagraphStyle(name='Section', fontName=ar_font_bold, fontSize=14, alignment=TA_RIGHT, spaceAfter=10, wordWrap='RTL')
            
            file_path, _ = QFileDialog.getSaveFileName(self, "حفظ تقرير الحالة", f"{self.case_data.get('child_name', {}).get('value', 'حالة')}.pdf", "PDF Files (*.pdf)")
            if not file_path:
                return
            if not file_path.lower().endswith(".pdf"):
                file_path += ".pdf"
            
            doc = SimpleDocTemplate(file_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
            story = []
            
            # Header with Logo and Centered White Text ---
            # logo_path = os.path.join(os.path.dirname(__file__), "..", "icons", "app_icon.png")
            logo_path = resource_path("icons/app_icon.png")
            if os.path.exists(logo_path):
                im = Image(logo_path, width=1.5*cm, height=1.5*cm)
                
                # Create the Paragraph for the child's name using the new white style
                child_name_paragraph = Paragraph(
                    pdf_ar_fix(self.case_data.get("child_name", {}).get("value", "-")),
                    header_name_style
                )

                # Create a table with two cells: one for the logo, one for the name
                header_table_data = [[im, child_name_paragraph]]
                header_table = Table(header_table_data, colWidths=[2*cm, doc.width - 2*cm])
                
                header_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#175606")),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # Vertically align content
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),   # Center the logo cell
                    ('SPAN', (1, 0), (1, 0)),              # The name cell spans as before
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                story.append(header_table)
            
            story.append(Spacer(1, 5)) # Add space after the logo header

            # story.append(Paragraph(pdf_ar_fix(self.case_data.get("child_name", {}).get("value", "-")), header_style))
            story.append(Paragraph(pdf_ar_fix(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"), subheader_style))
            story.append(Paragraph(pdf_ar_fix("بيانات الحالة"), section_style))
            case_table_data = [
                [Paragraph(pdf_ar_fix(self.case_data.get("case_id", "-")), cell_style), Paragraph(pdf_ar_fix("رقم الحالة"), cell_style_bold)]
            ]
            skip_fields = ['case_id', 'child_name']
            for key, value in self.case_data.items():
                if key not in skip_fields and value:
                    if isinstance(value, dict):
                        val = value.get("value", "-")
                        label = value.get("ar_key", key)
                    else:
                        val = value
                        label = key
                    case_table_data.append([Paragraph(pdf_ar_fix(str(val)), cell_style), Paragraph(pdf_ar_fix(str(label)), cell_style_bold)])
            table = Table(case_table_data, colWidths=[doc.width*0.35, doc.width*0.65])
            table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.white),
                ('BACKGROUND', (1, 0), (1, -1), colors.whitesmoke),
            ]))
            story.append(table)
            
                        
            skip_fields = ['survey_type', 'survey_date', 'submission_timestamp', 'case_id', 'child_name', 'dob', 'gender', '_filename']
            if surveys_to_export:
                for i, survey in enumerate(surveys_to_export, 1):
                    story.append(PageBreak())
                    story.append(Paragraph(pdf_ar_fix(f"الاستبيان رقم {i} - {survey.get('survey_type', '-') }"), section_style))
                    survey_table_data = [
                        [Paragraph(pdf_ar_fix(survey.get("survey_type", "-")), cell_style), Paragraph(pdf_ar_fix("نوع الاستبيان"), cell_style_bold)],
                        [Paragraph(pdf_ar_fix(survey.get("survey_date", "-")), cell_style), Paragraph(pdf_ar_fix("تاريخ الاستبيان"), cell_style_bold)]
                    ]
                    for key, value in survey.items():
                        if key not in skip_fields and value:
                            if isinstance(value, dict):
                                val = value.get("value", "-")
                                label = value.get("ar_key", key)
                            else:
                                val = value
                                label = key
                            survey_table_data.append([Paragraph(pdf_ar_fix(str(val)), cell_style), Paragraph(pdf_ar_fix(str(label)), cell_style_bold)])
                    s_table = Table(survey_table_data, colWidths=[doc.width*0.35, doc.width*0.65])
                    s_table.setStyle(TableStyle([
                        ('GRID', (0,0), (-1,-1), 1, colors.white),
                        ('BACKGROUND', (1, 0), (1, -1), colors.whitesmoke),
                    ]))
                    story.append(s_table)
            
            story.append(Spacer(1, 20))
            story.append(Paragraph(pdf_ar_fix("تم إنشاؤه بواسطة تطبيق MyCases"), ParagraphStyle(name='Footer', fontName=ar_font, fontSize=8, alignment=1)))
            
            doc.build(story)
            QMessageBox.information(self, "تم التصدير", "تم تصدير تقرير الحالة بنجاح.")
        except Exception as e:
            QMessageBox.critical(self, "خطأ في التصدير", f"فشل تصدير تقرير الحالة\n{e}")

