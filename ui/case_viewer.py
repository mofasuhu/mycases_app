import json
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLabel, QScrollArea, QPushButton, 
    QVBoxLayout, QHBoxLayout, QGroupBox, QMessageBox, QWidget,
    QListWidget, QListWidgetItem, QFileDialog
)
from PyQt5.QtCore import Qt, QDate, QSize
from datetime import date

from PyQt5.QtGui import QIcon

from .survey_form_first import SurveyFormFirst
from .case_form import CaseForm
from .pdf_exporter import export_survey_to_pdf_with_custom_path
from utils.file_manager import load_surveys_for_case, load_case_data_from_json # type: ignore
from utils.general import make_all_labels_copyable # type: ignore

class SurveyDetailViewer(QDialog):
    """A simple dialog to display the details of a single survey."""
    def __init__(self, survey_data, case_folder_name, parent=None):
        super().__init__(parent)
        self.survey_data = survey_data
        self.case_folder_name = case_folder_name
        self.setWindowTitle(f"عرض تفاصيل الاستبيان: {self.survey_data.get('survey_type')}")
        self.setMinimumWidth(450)
        self.setMinimumHeight(200)
        # Add minimize and maximize buttons to the window
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        layout = QVBoxLayout(self)
        
        # Add buttons layout
        self.buttons_layout = QHBoxLayout()
        
        # Add edit button
        self.edit_button = QPushButton("تعديل الاستبيان")
        self.edit_button.clicked.connect(self.edit_survey)
        self.buttons_layout.addWidget(self.edit_button)
        
        # Add export to PDF button
        self.export_pdf_button = QPushButton("تصدير إلى PDF")
        self.export_pdf_button.clicked.connect(self.export_to_pdf)
        self.buttons_layout.addWidget(self.export_pdf_button)
        
        layout.addLayout(self.buttons_layout)
        
        # Display survey type and date
        form_layout = QFormLayout()
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)

        form_layout.addRow(QLabel("نوع الاستبيان:"), QLabel(self.survey_data.get("survey_type", "-")))
        form_layout.addRow(QLabel("تاريخ الاستبيان:"), QLabel(self.survey_data.get("survey_date", "-")))
        
        layout.addLayout(form_layout)

        self.button_box = QHBoxLayout()
        self.close_button = QPushButton()
        self.close_button.setIcon(QIcon("icons/close.png"))
        self.close_button.setIconSize(QSize(32, 32))
        self.close_button.setToolTip("إغلاق")
        self.close_button.clicked.connect(self.reject)


        self.button_box.addStretch()
        self.button_box.addWidget(self.close_button)
        layout.addLayout(self.button_box)

        make_all_labels_copyable(self)            


    def edit_survey(self):
        """Open the appropriate survey form for editing based on survey type."""
        survey_type = self.survey_data.get("survey_type")
        
        if survey_type == "استبيان التقييم الأول":
            edit_form = SurveyFormFirst(self.case_folder_name, parent=self, survey_data_to_edit=self.survey_data)
            result = edit_form.exec_()
            
            if result == QDialog.Accepted:
                self.accept()  # Close this viewer and signal that data was updated
        else:
            QMessageBox.warning(self, "غير مدعوم", f"تعديل هذا النوع من الاستبيانات ({survey_type}) غير مدعوم حاليًا.")
    
    def export_to_pdf(self):
        """Export the survey data to a PDF file with a file dialog for selecting the save path."""
        # Get case data for context
        case_data = load_case_data_from_json(self.case_folder_name)
        
        # Create a file dialog to select the save path
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        
        # Generate a default filename
        survey_type = self.survey_data.get("survey_type", "استبيان")
        survey_date = self.survey_data.get("survey_date", "").replace("-", "")
        child_name = case_data.get("child_name", "حالة") if case_data else "حالة"
        default_filename = f"{survey_type}_{child_name}_{survey_date}.pdf"
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "حفظ ملف PDF", 
            default_filename,
            "PDF Files (*.pdf)", 
            options=options
        )
        
        if file_path:
            # Ensure the file has .pdf extension
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
                
            # Export the survey to PDF
            success, message = export_survey_to_pdf_with_custom_path(
                self.case_folder_name, 
                self.survey_data, 
                file_path, 
                case_data_for_context=case_data
            )
            
            if success:
                QMessageBox.information(self, "تم التصدير", f"تم تصدير الاستبيان بنجاح")
            else:
                QMessageBox.critical(self, "خطأ في التصدير", f"فشل تصدير الاستبيان\n{message}")

class CaseViewer(QDialog):
    def __init__(self, case_data, case_folder_name, parent=None):
        super().__init__(parent)
        self.case_data = case_data
        self.case_folder_name = case_folder_name
        self.parent_main_window = parent # To call refresh on main window if needed

        # --- Window Properties ---
        child_name_display = self.case_data.get("child_name", "")
        self.setWindowTitle(f"عرض بيانات: {child_name_display}")
        self.setGeometry(250, 50, 800, 600)
        # Add minimize and maximize buttons to the window
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        # self.setWindowState(Qt.WindowMaximized)

        # --- Main Layout ---
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)

        container_widget = QWidget()
        self.main_layout = QVBoxLayout(container_widget)

        # --- Child Information Group ---
        child_group = QGroupBox("بيانات الحالة")
        child_layout = QFormLayout()
        child_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)  # Keep labels and fields on same line
        child_layout.setLabelAlignment(Qt.AlignRight)
        child_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)  # Prevent fields from expanding

        self.child_name_label = QLabel(self.case_data.get("child_name", "-"))
        self.child_name_label.setFixedWidth(325)
        self.child_name_label.setFixedHeight(40)        
        child_layout.addRow(QLabel("اسم الحالة:"), self.child_name_label)

        self.dob_label = QLabel(self.case_data.get("dob", "-"))
        self.dob_label.setFixedWidth(325)
        self.dob_label.setFixedHeight(40)
        self.dob_label.setAlignment(Qt.AlignRight)
        child_layout.addRow(QLabel("تاريخ الميلاد:"), self.dob_label)

        self.age_label = QLabel("يتم حسابه")
        child_layout.addRow(QLabel("العمر:"), self.age_label)

        self.gender_label = QLabel(self.case_data.get("gender", "-"))
        self.gender_label.setFixedWidth(325)
        self.gender_label.setFixedHeight(40)
        child_layout.addRow(QLabel("الجنس:"), self.gender_label)

        self.first_lang_label = QLabel(self.case_data.get("first_language", "-"))
        self.first_lang_label.setFixedWidth(325)
        self.first_lang_label.setFixedHeight(40)
        child_layout.addRow(QLabel("اللغة الأولى:"), self.first_lang_label)

        self.first_lang_notes_label = QLabel(self.case_data.get("first_language_notes", "-"))
        self.first_lang_notes_label.setFixedWidth(325)
        self.first_lang_notes_label.setFixedHeight(40)
        child_layout.addRow(QLabel("ملاحظات اللغة الأولى:"), self.first_lang_notes_label)

        self.second_lang_label = QLabel(self.case_data.get("second_language", "-"))
        self.second_lang_label.setFixedWidth(325)
        self.second_lang_label.setFixedHeight(40)
        child_layout.addRow(QLabel("اللغة الثانية:"), self.second_lang_label)

        self.second_lang_notes_label = QLabel(self.case_data.get("second_language_notes", "-"))
        self.second_lang_notes_label.setFixedWidth(325)
        self.second_lang_notes_label.setFixedHeight(40)
        child_layout.addRow(QLabel("ملاحظات اللغة الثانية:"), self.second_lang_notes_label)

        self.diagnosis_label = QLabel(self.case_data.get("diagnosis", "-"))
        self.diagnosis_label.setFixedWidth(325)
        self.diagnosis_label.setFixedHeight(40)
        child_layout.addRow(QLabel("التشخيص:"), self.diagnosis_label)

        self.diagnosed_by_label = QLabel(self.case_data.get("diagnosed_by", "-"))
        self.diagnosed_by_label.setFixedWidth(325)
        self.diagnosed_by_label.setFixedHeight(40)
        child_layout.addRow(QLabel("بواسطة:"), self.diagnosed_by_label)
        
        child_group.setLayout(child_layout)
        self.main_layout.addWidget(child_group)

        # --- Parents Information Group ---
        parents_group = QGroupBox("بيانات الوالدين")
        parents_layout = QFormLayout()
        parents_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)  # Keep labels and fields on same line
        parents_layout.setLabelAlignment(Qt.AlignRight)
        parents_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)  # Prevent fields from expanding

        self.father_name_label = QLabel(self.case_data.get("father_name", "-"))
        self.father_name_label.setFixedWidth(325)
        self.father_name_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("اسم الأب:"), self.father_name_label)
        
        self.father_dob_label = QLabel(self.case_data.get("father_dob", "-"))
        self.father_dob_label.setFixedWidth(325)
        self.father_dob_label.setFixedHeight(40)
        self.father_dob_label.setAlignment(Qt.AlignRight)
        parents_layout.addRow(QLabel("تاريخ ميلاد الأب:"), self.father_dob_label)
        
        self.father_age_label = QLabel("يتم حسابه")
        parents_layout.addRow(QLabel("عمر الأب:"), self.father_age_label)
        
        self.father_job_label = QLabel(self.case_data.get("father_job", "-"))
        self.father_job_label.setFixedWidth(325)
        self.father_job_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("وظيفة الأب:"), self.father_job_label)
        
        self.father_health_label = QLabel(self.case_data.get("father_health", "-"))
        self.father_health_label.setFixedWidth(325)
        self.father_health_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("الحالة الصحية للأب:"), self.father_health_label)

        self.mother_name_label = QLabel(self.case_data.get("mother_name", "-"))
        self.mother_name_label.setFixedWidth(325)
        self.mother_name_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("اسم الأم:"), self.mother_name_label)
        
        self.mother_dob_label = QLabel(self.case_data.get("mother_dob", "-"))
        self.mother_dob_label.setFixedWidth(325)
        self.mother_dob_label.setFixedHeight(40)
        self.mother_dob_label.setAlignment(Qt.AlignRight)
        parents_layout.addRow(QLabel("تاريخ ميلاد الأم:"), self.mother_dob_label)
        
        self.mother_age_label = QLabel("يتم حسابه")
        parents_layout.addRow(QLabel("عمر الأم:"), self.mother_age_label)
        
        self.mother_job_label = QLabel(self.case_data.get("mother_job", "-"))
        self.mother_job_label.setFixedWidth(325)
        self.mother_job_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("وظيفة الأم:"), self.mother_job_label)
        
        self.mother_health_label = QLabel(self.case_data.get("mother_health", "-"))
        self.mother_health_label.setFixedWidth(325)
        self.mother_health_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("الحالة الصحية للأم:"), self.mother_health_label)

        self.father_preg_age_label = QLabel("يتم حسابه")
        parents_layout.addRow(QLabel("عمر الأب عند الولادة:"), self.father_preg_age_label)
        
        self.mother_preg_age_label = QLabel("يتم حسابه")
        parents_layout.addRow(QLabel("عمر الأم عند الولادة:"), self.mother_preg_age_label)

        self.parents_relation_label = QLabel(self.case_data.get("parents_relation", "-"))
        self.parents_relation_label.setFixedWidth(325)
        self.parents_relation_label.setFixedHeight(40)
        parents_layout.addRow(QLabel("صلة قرابة بين الوالدين؟"), self.parents_relation_label)

        # Only show relation degree if parents are related
        if self.case_data.get("parents_relation") == "نعم":
            self.relation_degree_label = QLabel("درجة القرابة:")
            self.relation_degree_value = QLabel(self.case_data.get("relation_degree", "-"))
            self.relation_degree_value.setFixedWidth(325)
            self.relation_degree_value.setFixedHeight(40)
            parents_layout.addRow(self.relation_degree_label, self.relation_degree_value)

        parents_group.setLayout(parents_layout)
        self.main_layout.addWidget(parents_group)

        # --- Family Information Group ---
        family_group = QGroupBox("معلومات الأسرة")
        family_layout = QFormLayout()
        family_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)  # Keep labels and fields on same line
        family_layout.setLabelAlignment(Qt.AlignRight)
        family_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)  # Prevent fields from expanding

        self.family_size_label = QLabel(str(self.case_data.get("family_size", "-")))
        self.family_size_label.setFixedWidth(325)
        self.family_size_label.setFixedHeight(40)
        self.family_size_label.setAlignment(Qt.AlignRight)
        family_layout.addRow(QLabel("حجم الأسرة:"), self.family_size_label)

        self.siblings_count_label = QLabel(str(self.case_data.get("siblings_count", "-")))
        self.siblings_count_label.setFixedWidth(325)
        self.siblings_count_label.setFixedHeight(40)
        self.siblings_count_label.setAlignment(Qt.AlignRight)
        family_layout.addRow(QLabel("عدد الإخوة:"), self.siblings_count_label)

        self.child_order_label = QLabel(str(self.case_data.get("child_order", "-")))
        self.child_order_label.setFixedWidth(325)
        self.child_order_label.setFixedHeight(40)
        self.child_order_label.setAlignment(Qt.AlignRight)
        family_layout.addRow(QLabel("ترتيب الحالة بين الأخوة:"), self.child_order_label)

        self.similar_cases_label = QLabel(self.case_data.get("similar_cases_family", "-"))
        self.similar_cases_label.setFixedWidth(325)
        self.similar_cases_label.setFixedHeight(40)
        family_layout.addRow(QLabel("حالات مشابهة في العائلة؟"), self.similar_cases_label)

        # Only show similar cases who if there are similar cases
        if self.case_data.get("similar_cases_family") == "نعم":
            self.similar_cases_who_label = QLabel("من؟")
            self.similar_cases_who_value = QLabel(self.case_data.get("similar_cases_who", "-"))
            self.similar_cases_who_value.setFixedWidth(325)
            self.similar_cases_who_value.setFixedHeight(40)
            family_layout.addRow(self.similar_cases_who_label, self.similar_cases_who_value)

        family_group.setLayout(family_layout)
        self.main_layout.addWidget(family_group)


        # --- Buttons (Edit, Close) ---
        self.button_box = QHBoxLayout()

        self.edit_button = QPushButton()
        self.edit_button.setIcon(QIcon("icons/edit.png"))
        self.edit_button.setIconSize(QSize(32, 32))
        self.edit_button.setToolTip("تعديل بيانات الحالة")        
        self.edit_button.clicked.connect(self.edit_case_data)

        self.close_button = QPushButton()
        self.close_button.setIcon(QIcon("icons/close.png"))
        self.close_button.setIconSize(QSize(32, 32))
        self.close_button.setToolTip("إغلاق")   
        self.close_button.clicked.connect(self.reject)

        self.button_box.addStretch()
        self.button_box.addWidget(self.edit_button)
        self.button_box.addWidget(self.close_button)
        self.main_layout.addLayout(self.button_box)


        # --- Surveys Section ---
        self.setup_surveys_section()

        scroll.setWidget(container_widget)
        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(scroll)

        # --- Set Tab Order ---
        # This ensures the Tab key navigates through form fields in a logical order
        self.setTabOrder(self.edit_button, self.close_button)
        
        # Calculate ages based on DOBs
        self.calculate_all_ages()
        
        # Load surveys
        self.load_and_display_surveys()
        
        # Apply styling
        self.apply_styles()

        make_all_labels_copyable(self)

    def calculate_all_ages(self):
        """Calculate all ages based on DOBs"""
        self.calculate_age()
        self.calculate_father_age()
        self.calculate_mother_age()
        self.calculate_pregnancy_ages()

    def calculate_age(self):
        """Calculate child's age based on DOB and update the age label"""
        dob_str = self.case_data.get("dob", "")
        if not dob_str:
            self.age_label.setText("تاريخ ميلاد غير متوفر")
            return
            
        try:
            dob_parts = dob_str.split("-")
            if len(dob_parts) != 3:
                self.age_label.setText("تاريخ ميلاد غير صالح")
                return
                
            dob_qdate = QDate(int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2]))
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
        """Calculate father's age based on DOB"""
        father_dob_str = self.case_data.get("father_dob", "")
        if not father_dob_str:
            self.father_age_label.setText("-")
            return
            
        try:
            dob_parts = father_dob_str.split("-")
            if len(dob_parts) != 3:
                self.father_age_label.setText("تاريخ ميلاد غير صالح")
                return
                
            father_dob_qdate = QDate(int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2]))
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
        """Calculate mother's age based on DOB"""
        mother_dob_str = self.case_data.get("mother_dob", "")
        if not mother_dob_str:
            self.mother_age_label.setText("-")
            return
            
        try:
            dob_parts = mother_dob_str.split("-")
            if len(dob_parts) != 3:
                self.mother_age_label.setText("تاريخ ميلاد غير صالح")
                return
                
            mother_dob_qdate = QDate(int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2]))
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
        """Calculate parents' ages at pregnancy based on child's DOB and parents' DOBs"""
        child_dob_str = self.case_data.get("dob", "")
        if not child_dob_str:
            self.father_preg_age_label.setText("-")
            self.mother_preg_age_label.setText("-")
            return
            
        try:
            child_dob_parts = child_dob_str.split("-")
            if len(child_dob_parts) != 3:
                return
                
            child_dob_qdate = QDate(int(child_dob_parts[0]), int(child_dob_parts[1]), int(child_dob_parts[2]))
            if not child_dob_qdate.isValid():
                return
                
            child_dob = date(child_dob_qdate.year(), child_dob_qdate.month(), child_dob_qdate.day())
            
            # Calculate father's age at pregnancy
            father_dob_str = self.case_data.get("father_dob", "")
            if father_dob_str:
                father_dob_parts = father_dob_str.split("-")
                if len(father_dob_parts) == 3:
                    father_dob_qdate = QDate(int(father_dob_parts[0]), int(father_dob_parts[1]), int(father_dob_parts[2]))
                    if father_dob_qdate.isValid():
                        father_dob = date(father_dob_qdate.year(), father_dob_qdate.month(), father_dob_qdate.day())
                        father_preg_age = child_dob.year - father_dob.year - ((child_dob.month, child_dob.day) < (father_dob.month, father_dob.day))
                        father_preg_age_months = (child_dob.month - father_dob.month - (child_dob.day < father_dob.day)) % 12        
                        self.father_preg_age_label.setText(f"{father_preg_age} سنة، {father_preg_age_months} شهر")

            # Calculate mother's age at pregnancy
            mother_dob_str = self.case_data.get("mother_dob", "")
            if mother_dob_str:
                mother_dob_parts = mother_dob_str.split("-")
                if len(mother_dob_parts) == 3:
                    mother_dob_qdate = QDate(int(mother_dob_parts[0]), int(mother_dob_parts[1]), int(mother_dob_parts[2]))
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
        """Set up the surveys section with buttons for each survey type."""
        self.surveys_group = QGroupBox("الاستبيانات والجلسات")
        self.surveys_layout = QVBoxLayout()
        
        # Survey type buttons layout
        self.survey_buttons_layout = QHBoxLayout()
        
        # Add button for first survey type
        self.btn_add_first_survey = QPushButton("استبيان التقييم الأول")
        self.btn_add_first_survey.setFixedWidth(200)
        self.btn_add_first_survey.clicked.connect(self.add_first_survey)
        self.survey_buttons_layout.addWidget(self.btn_add_first_survey)
        
        # Add more buttons for other survey types here in the future
        
        self.survey_buttons_layout.addStretch()
        self.surveys_layout.addLayout(self.survey_buttons_layout)
        
        # Survey list
        self.survey_list_widget = QListWidget()
        self.survey_list_widget.itemDoubleClicked.connect(self.view_selected_survey)
        self.survey_list_widget.setFixedHeight(200)
        self.surveys_layout.addWidget(self.survey_list_widget)
        
        self.surveys_group.setLayout(self.surveys_layout)
        self.main_layout.addWidget(self.surveys_group)

    def load_and_display_surveys(self):
        """Load and display all surveys for this case."""
        self.survey_list_widget.clear()
        surveys = load_surveys_for_case(self.case_folder_name)
        if surveys:
            for survey_data in surveys:
                # Display type and date for easy identification
                survey_type = survey_data.get("survey_type", "غير معروف")
                survey_date = survey_data.get("survey_date", "غير معروف")
                item_text = f'{survey_type} - {survey_date}'
                list_item = QListWidgetItem(item_text)
                # list_item.setData(Qt.UserRole, survey_data) # Store full survey data with the item
                list_item.setData(Qt.UserRole, json.dumps(survey_data, ensure_ascii=False))
                self.survey_list_widget.addItem(list_item)
        else:
            self.survey_list_widget.addItem("لا توجد استبيانات مسجلة لهذه الحالة.")
            self.survey_list_widget.setEnabled(False)

    def add_first_survey(self):
        """Open the first survey form for this case."""
        survey_form = SurveyFormFirst(self.case_folder_name, parent=self)
        if survey_form.exec_() == QDialog.Accepted:
            self.load_and_display_surveys() # Refresh the list after adding
            self.survey_list_widget.setEnabled(True)

    def view_selected_survey(self, item):
        """View the selected survey details."""
        # survey_data = item.data(Qt.UserRole)
        survey_data = json.loads(item.data(Qt.UserRole))
        if survey_data:
            detail_viewer = SurveyDetailViewer(survey_data, self.case_folder_name, parent=self)
            result = detail_viewer.exec_()
            
            # If the viewer returns Accepted, it means data was updated (edit was performed)
            if result == QDialog.Accepted:
                self.load_and_display_surveys() # Refresh the list to show any updates
        else:
            QMessageBox.warning(self, "خطأ", "لا يمكن عرض تفاصيل الاستبيان.")

    def edit_case_data(self):
        """Opens the CaseForm for editing the current case data."""
        edit_form = CaseForm(parent=self, case_data_to_load=self.case_data)
        result = edit_form.exec_()
        
        if result == QDialog.Accepted:
            # Reload the case data and refresh the display
            updated_case_data = load_case_data_from_json(self.case_folder_name)
            if updated_case_data:
                self.case_data = updated_case_data
                # Update all displayed fields with the new data
                self.update_display_with_new_data()
                # Signal to parent window that data has been updated
                self.accept()
            else:
                QMessageBox.warning(self, "خطأ", "فشل تحديث بيانات الحالة.")

    def update_display_with_new_data(self):
        """Update all displayed fields with the new case data"""
        # Update Child Information
        self.child_name_label.setText(self.case_data.get("child_name", "-"))
        self.dob_label.setText(self.case_data.get("dob", "-"))
        self.gender_label.setText(self.case_data.get("gender", "-"))
        self.first_lang_label.setText(self.case_data.get("first_language", "-"))
        self.first_lang_notes_label.setText(self.case_data.get("first_language_notes", "-"))
        self.second_lang_label.setText(self.case_data.get("second_language", "-"))
        self.second_lang_notes_label.setText(self.case_data.get("second_language_notes", "-"))
        self.diagnosis_label.setText(self.case_data.get("diagnosis", "-"))
        self.diagnosed_by_label.setText(self.case_data.get("diagnosed_by", "-"))
        
        # Update Parents Information
        self.father_name_label.setText(self.case_data.get("father_name", "-"))
        self.father_dob_label.setText(self.case_data.get("father_dob", "-"))
        self.father_job_label.setText(self.case_data.get("father_job", "-"))
        self.father_health_label.setText(self.case_data.get("father_health", "-"))
        self.mother_name_label.setText(self.case_data.get("mother_name", "-"))
        self.mother_dob_label.setText(self.case_data.get("mother_dob", "-"))
        self.mother_job_label.setText(self.case_data.get("mother_job", "-"))
        self.mother_health_label.setText(self.case_data.get("mother_health", "-"))
        self.parents_relation_label.setText(self.case_data.get("parents_relation", "-"))
        
        # Update Family Information
        self.family_size_label.setText(str(self.case_data.get("family_size", "-")))
        self.siblings_count_label.setText(str(self.case_data.get("siblings_count", "-")))
        self.child_order_label.setText(str(self.case_data.get("child_order", "-")))
        self.similar_cases_label.setText(self.case_data.get("similar_cases_family", "-"))
        
        # Recalculate all ages
        self.calculate_all_ages()

    def apply_styles(self):
        self.setStyleSheet("""""")
