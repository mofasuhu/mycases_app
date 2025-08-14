from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QLabel, QScrollArea,
    QDateEdit, QComboBox, QSpinBox, QPushButton, 
    QVBoxLayout, QHBoxLayout, QGroupBox, QMessageBox, QWidget
)
from PyQt5.QtCore import QDate, Qt, QSize
from PyQt5.QtGui import QIcon, QIntValidator

from datetime import date

from utils.file_manager import save_case_data_to_json, get_next_case_id # type: ignore
from utils.general import make_all_labels_copyable, create_dob_input # type: ignore

class CaseForm(QDialog):
    def __init__(self, parent=None, case_data_to_load=None):
        super().__init__(parent)

        # --- Window Properties ---
        self.setWindowTitle("إدخال بيانات الحالة")
        self.setGeometry(250, 50, 800, 600)
        # Add minimize and maximize buttons to the window
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        # self.setWindowState(Qt.WindowMaximized)
        # --- Main Layout ---
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)

        container_widget = QWidget()  # Changed from QDialog to QWidget
        self.main_layout = QVBoxLayout(container_widget)

        # --- Child Information Group ---
        child_group = QGroupBox("بيانات الحالة")
        child_layout = QFormLayout()
        child_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)  # Keep labels and fields on same line
        child_layout.setLabelAlignment(Qt.AlignRight)
        child_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)  # Prevent fields from expanding

        self.child_name_edit = QLineEdit()
        self.child_name_edit.setFixedWidth(325)
        self.child_name_edit.setFixedHeight(40)        
        child_layout.addRow(QLabel("اسم الحالة:"), self.child_name_edit)

        # --- For child DOB ---
        dob_widget, self.dob_edit, self.day_edit, self.month_edit, self.year_edit = create_dob_input(default_years_ago=5, on_date_changed=self.calculate_age)
        child_layout.addRow(QLabel("تاريخ الميلاد:"), dob_widget)

        self.age_label = QLabel("يتم حسابه")
        child_layout.addRow(QLabel("العمر:"), self.age_label)

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["ذكر", "أنثى"])
        self.gender_combo.setFixedWidth(325)
        self.gender_combo.setFixedHeight(40)
        self.gender_combo.wheelEvent = lambda event: event.ignore()
        child_layout.addRow(QLabel("الجنس:"), self.gender_combo)

        self.first_lang_edit = QComboBox()
        self.first_lang_edit.addItems(["اللغة العربية - مصر", "اللغة العربية - دولة أخرى", "اللغة الإنجليزية", "اللغة الفرنسية", "اللغة الألمانية", "لغة أخرى", "لا يوجد"])
        self.first_lang_edit.setFixedWidth(325)
        self.first_lang_edit.setFixedHeight(40)
        self.first_lang_edit.wheelEvent = lambda event: event.ignore()
        child_layout.addRow(QLabel("اللغة الأولى:"), self.first_lang_edit)

        self.first_lang_notes = QLineEdit()
        self.first_lang_notes.setFixedWidth(325)
        self.first_lang_notes.setFixedHeight(40)
        child_layout.addRow(QLabel("ملاحظات اللغة الأولى:"), self.first_lang_notes)

        self.second_lang_edit = QComboBox()
        self.second_lang_edit.addItems(["اللغة العربية - مصر", "اللغة العربية - دولة أخرى", "اللغة الإنجليزية", "اللغة الفرنسية", "اللغة الألمانية", "لغة أخرى", "لا يوجد"])
        self.second_lang_edit.setFixedWidth(325)
        self.second_lang_edit.setFixedHeight(40)
        self.second_lang_edit.wheelEvent = lambda event: event.ignore()
        child_layout.addRow(QLabel("اللغة الثانية:"), self.second_lang_edit)

        self.second_lang_notes = QLineEdit()
        self.second_lang_notes.setFixedWidth(325)
        self.second_lang_notes.setFixedHeight(40)
        child_layout.addRow(QLabel("ملاحظات اللغة الثانية:"), self.second_lang_notes)

        self.diagnosis_edit = QLineEdit()
        self.diagnosis_edit.setFixedWidth(325)
        self.diagnosis_edit.setFixedHeight(40)
        child_layout.addRow(QLabel("التشخيص:"), self.diagnosis_edit)

        self.diagnosed_by_edit = QLineEdit()
        self.diagnosed_by_edit.setFixedWidth(325)
        self.diagnosed_by_edit.setFixedHeight(40)
        child_layout.addRow(QLabel("بواسطة:"), self.diagnosed_by_edit)
        
        child_group.setLayout(child_layout)
        self.main_layout.addWidget(child_group)

        # --- Parents Information Group ---
        parents_group = QGroupBox("بيانات الوالدين")
        parents_layout = QFormLayout()
        parents_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)  # Keep labels and fields on same line
        parents_layout.setLabelAlignment(Qt.AlignRight)
        parents_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)  # Prevent fields from expanding

        self.father_name_edit = QLineEdit()
        self.father_name_edit.setFixedWidth(325)
        self.father_name_edit.setFixedHeight(40)
        parents_layout.addRow(QLabel("اسم الأب:"), self.father_name_edit)

        # --- For father DOB ---
        father_widget, self.father_dob_edit, self.father_day_edit, self.father_month_edit, self.father_year_edit = create_dob_input(default_years_ago=30, on_date_changed=self.calculate_father_age)
        parents_layout.addRow(QLabel("تاريخ ميلاد الأب:"), father_widget)
        
        # Replace QSpinBox with QLabel for father's age
        self.father_age_label = QLabel("يتم حسابه")
        parents_layout.addRow(QLabel("عمر الأب:"), self.father_age_label)
        
        self.father_job_edit = QLineEdit()
        self.father_job_edit.setFixedWidth(325)
        self.father_job_edit.setFixedHeight(40)
        parents_layout.addRow(QLabel("وظيفة الأب:"), self.father_job_edit)
        
        self.father_health_edit = QLineEdit()
        self.father_health_edit.setFixedWidth(325)
        self.father_health_edit.setFixedHeight(40)
        parents_layout.addRow(QLabel("الحالة الصحية للأب:"), self.father_health_edit)

        self.mother_name_edit = QLineEdit()
        self.mother_name_edit.setFixedWidth(325)
        self.mother_name_edit.setFixedHeight(40)
        parents_layout.addRow(QLabel("اسم الأم:"), self.mother_name_edit)
        
        # --- For mother DOB ---
        mother_widget, self.mother_dob_edit, self.mother_day_edit, self.mother_month_edit, self.mother_year_edit = create_dob_input(default_years_ago=25, on_date_changed=self.calculate_mother_age)
        parents_layout.addRow(QLabel("تاريخ ميلاد الأم:"), mother_widget)
        
        # Replace QSpinBox with QLabel for mother's age
        self.mother_age_label = QLabel("يتم حسابه")
        parents_layout.addRow(QLabel("عمر الأم:"), self.mother_age_label)
        
        self.mother_job_edit = QLineEdit()
        self.mother_job_edit.setFixedWidth(325)
        self.mother_job_edit.setFixedHeight(40)
        parents_layout.addRow(QLabel("وظيفة الأم:"), self.mother_job_edit)
        
        self.mother_health_edit = QLineEdit()
        self.mother_health_edit.setFixedWidth(325)
        self.mother_health_edit.setFixedHeight(40)
        parents_layout.addRow(QLabel("الحالة الصحية للأم:"), self.mother_health_edit)

        self.father_preg_age_label = QLabel("يتم حسابه")
        parents_layout.addRow(QLabel("عمر الأب عند الولادة:"), self.father_preg_age_label)
        
        self.mother_preg_age_label = QLabel("يتم حسابه")
        parents_layout.addRow(QLabel("عمر الأم عند الولادة:"), self.mother_preg_age_label)

        self.parents_relation_combo = QComboBox()
        self.parents_relation_combo.addItems(["نعم", "لا"])
        self.parents_relation_combo.currentIndexChanged.connect(self.toggle_relation_degree)
        self.parents_relation_combo.setFixedWidth(325)
        self.parents_relation_combo.setFixedHeight(40)
        self.parents_relation_combo.wheelEvent = lambda event: event.ignore()
        parents_layout.addRow(QLabel("صلة قرابة بين الوالدين؟"), self.parents_relation_combo)

        self.relation_degree_label = QLabel("درجة القرابة:")
        self.relation_degree_edit = QComboBox()
        self.relation_degree_edit.addItems([
            "أبناء عم/خال من الدرجة الأولى",
            "أبناء عم/خال من الدرجة الثانية",
            "أقارب بعيدون"
        ])
        self.relation_degree_edit.setFixedWidth(325)
        self.relation_degree_edit.setFixedHeight(40)
        self.relation_degree_edit.wheelEvent = lambda event: event.ignore()
        parents_layout.addRow(self.relation_degree_label, self.relation_degree_edit)
        self.toggle_relation_degree(self.parents_relation_combo.currentIndex()) 

        parents_group.setLayout(parents_layout)
        self.main_layout.addWidget(parents_group)

        # --- Family Information Group ---
        family_group = QGroupBox("معلومات الأسرة")
        family_layout = QFormLayout()
        family_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)  # Keep labels and fields on same line
        family_layout.setLabelAlignment(Qt.AlignRight)
        family_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)  # Prevent fields from expanding

        self.family_size_spin = QSpinBox()
        self.family_size_spin.setRange(2, 20)
        self.family_size_spin.setFixedWidth(325)
        self.family_size_spin.setFixedHeight(40)
        self.family_size_spin.setAlignment(Qt.AlignRight)
        self.family_size_spin.wheelEvent = lambda event: event.ignore()
        family_layout.addRow(QLabel("حجم الأسرة:"), self.family_size_spin)

        self.siblings_count_spin = QSpinBox()
        self.siblings_count_spin.setRange(0, 19)
        self.siblings_count_spin.setFixedWidth(325)
        self.siblings_count_spin.setFixedHeight(40)
        self.siblings_count_spin.setAlignment(Qt.AlignRight)
        self.siblings_count_spin.wheelEvent = lambda event: event.ignore()
        family_layout.addRow(QLabel("عدد الإخوة:"), self.siblings_count_spin)

        self.child_order_spin = QSpinBox()
        self.child_order_spin.setRange(1, 20)
        self.child_order_spin.setFixedWidth(325)
        self.child_order_spin.setFixedHeight(40)
        self.child_order_spin.setAlignment(Qt.AlignRight)
        self.child_order_spin.wheelEvent = lambda event: event.ignore()
        family_layout.addRow(QLabel("ترتيب الحالة بين الأخوة:"), self.child_order_spin)

        self.similar_cases_combo = QComboBox()
        self.similar_cases_combo.addItems(["نعم", "لا"])
        self.similar_cases_combo.currentIndexChanged.connect(self.toggle_similar_cases_who)
        self.similar_cases_combo.setFixedWidth(325)
        self.similar_cases_combo.setFixedHeight(40)
        self.similar_cases_combo.wheelEvent = lambda event: event.ignore()
        family_layout.addRow(QLabel("حالات مشابهة في العائلة؟"), self.similar_cases_combo)

        self.similar_cases_who_label = QLabel("من؟")
        self.similar_cases_who_edit = QLineEdit()
        self.similar_cases_who_edit.setFixedWidth(325)
        self.similar_cases_who_edit.setFixedHeight(40)
        family_layout.addRow(self.similar_cases_who_label, self.similar_cases_who_edit)
        self.toggle_similar_cases_who(self.similar_cases_combo.currentIndex())

        family_group.setLayout(family_layout)
        self.main_layout.addWidget(family_group)

        # --- Buttons (Save, Cancel) ---
        self.button_box = QHBoxLayout()

        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon("icons/save.png"))
        self.save_button.setIconSize(QSize(32, 32))
        self.save_button.setToolTip("حفظ")   
        self.save_button.clicked.connect(self.save_case_data)

        self.cancel_button = QPushButton()
        self.cancel_button.setIcon(QIcon("icons/cancel.png"))
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

        # Flag to prevent recursive updates between age and DOB fields
        self._updating_fields = False

        # --- Initial Age Calculation ---
        self.calculate_father_age()
        self.calculate_mother_age()
        self.calculate_age()

        self.case_data_to_load = case_data_to_load
        if self.case_data_to_load:
            self.load_data_into_form(self.case_data_to_load)
            
        # --- Set Tab Order ---
        # This ensures the Tab key navigates through form fields in a logical order
        self.setTabOrder(self.child_name_edit, self.dob_edit)
        self.setTabOrder(self.dob_edit, self.gender_combo)
        self.setTabOrder(self.gender_combo, self.first_lang_edit)
        self.setTabOrder(self.first_lang_edit, self.first_lang_notes)
        self.setTabOrder(self.first_lang_notes, self.second_lang_edit)
        self.setTabOrder(self.second_lang_edit, self.second_lang_notes)
        self.setTabOrder(self.second_lang_notes, self.diagnosis_edit)
        self.setTabOrder(self.diagnosis_edit, self.diagnosed_by_edit)
        
        # Parents section
        self.setTabOrder(self.diagnosed_by_edit, self.father_name_edit)
        self.setTabOrder(self.father_name_edit, self.father_dob_edit)
        self.setTabOrder(self.father_dob_edit, self.father_job_edit)
        self.setTabOrder(self.father_job_edit, self.father_health_edit)
        self.setTabOrder(self.father_health_edit, self.mother_name_edit)
        self.setTabOrder(self.mother_name_edit, self.mother_dob_edit)
        self.setTabOrder(self.mother_dob_edit, self.mother_job_edit)
        self.setTabOrder(self.mother_job_edit, self.mother_health_edit)
        self.setTabOrder(self.mother_health_edit, self.parents_relation_combo)
        self.setTabOrder(self.parents_relation_combo, self.relation_degree_edit)
        
        # Family section
        self.setTabOrder(self.relation_degree_edit, self.family_size_spin)
        self.setTabOrder(self.family_size_spin, self.siblings_count_spin)
        self.setTabOrder(self.siblings_count_spin, self.child_order_spin)
        self.setTabOrder(self.child_order_spin, self.similar_cases_combo)
        self.setTabOrder(self.similar_cases_combo, self.similar_cases_who_edit)
        
        # Buttons
        self.setTabOrder(self.similar_cases_who_edit, self.save_button)
        self.setTabOrder(self.save_button, self.cancel_button)
        
        make_all_labels_copyable(self)       

    def calculate_age(self):
        """Calculate child's age based on DOB and update related fields"""
        if self._updating_fields:
            return
            
        self._updating_fields = True
        
        dob_qdate = self.dob_edit.date()
        if not dob_qdate.isValid():
            self.age_label.setText("تاريخ ميلاد غير صالح")
            self._updating_fields = False
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
        
        # Calculate pregnancy ages
        self.calculate_pregnancy_ages()
        
        self._updating_fields = False

    def calculate_father_age(self):
        """Calculate father's age based on DOB"""
        if self._updating_fields:
            return
            
        self._updating_fields = True
        
        father_dob_qdate = self.father_dob_edit.date()
        if not father_dob_qdate.isValid():
            self._updating_fields = False
            return
            
        father_dob = date(father_dob_qdate.year(), father_dob_qdate.month(), father_dob_qdate.day())
        today = date.today()
        father_age = today.year - father_dob.year - ((today.month, today.day) < (father_dob.month, father_dob.day))
        father_age_months = (today.month - father_dob.month - (today.day < father_dob.day)) % 12        
        self.father_age_label.setText(f"{father_age} سنة، {father_age_months} شهر")
        
        # Calculate pregnancy ages
        self.calculate_pregnancy_ages()
        
        self._updating_fields = False

    def calculate_mother_age(self):
        """Calculate mother's age based on DOB"""
        if self._updating_fields:
            return
            
        self._updating_fields = True
        
        mother_dob_qdate = self.mother_dob_edit.date()
        if not mother_dob_qdate.isValid():
            self._updating_fields = False
            return
            
        mother_dob = date(mother_dob_qdate.year(), mother_dob_qdate.month(), mother_dob_qdate.day())
        today = date.today()
        mother_age = today.year - mother_dob.year - ((today.month, today.day) < (mother_dob.month, mother_dob.day))
        mother_age_months = (today.month - mother_dob.month - (today.day < mother_dob.day)) % 12        
        self.mother_age_label.setText(f"{mother_age} سنة، {mother_age_months} شهر")
        
        # Calculate pregnancy ages
        self.calculate_pregnancy_ages()
        
        self._updating_fields = False

    def calculate_pregnancy_ages(self):
        """Calculate parents' ages at pregnancy based on child's DOB and parents' ages"""
        child_dob_qdate = self.dob_edit.date()
        if not child_dob_qdate.isValid():
            return
            
        child_dob = date(child_dob_qdate.year(), child_dob_qdate.month(), child_dob_qdate.day())
        
        # Calculate father's age at pregnancy
        father_dob_qdate = self.father_dob_edit.date()
        if father_dob_qdate.isValid():
            father_dob = date(father_dob_qdate.year(), father_dob_qdate.month(), father_dob_qdate.day())
            father_preg_age = child_dob.year - father_dob.year - ((child_dob.month, child_dob.day) < (father_dob.month, father_dob.day))
            father_preg_age_months = (child_dob.month - father_dob.month - (child_dob.day < father_dob.day)) % 12        
            self.father_preg_age_label.setText(f"{father_preg_age} سنة، {father_preg_age_months} شهر")
        
        # Calculate mother's age at pregnancy
        mother_dob_qdate = self.mother_dob_edit.date()
        if mother_dob_qdate.isValid():
            mother_dob = date(mother_dob_qdate.year(), mother_dob_qdate.month(), mother_dob_qdate.day())
            mother_preg_age = child_dob.year - mother_dob.year - ((child_dob.month, child_dob.day) < (mother_dob.month, mother_dob.day))
            mother_preg_age_months = (child_dob.month - mother_dob.month - (child_dob.day < mother_dob.day)) % 12        
            self.mother_preg_age_label.setText(f"{mother_preg_age} سنة، {mother_preg_age_months} شهر")              

    def toggle_relation_degree(self, index):
        is_related = self.parents_relation_combo.itemText(index).startswith("نعم")
        self.relation_degree_label.setVisible(is_related)
        self.relation_degree_edit.setVisible(is_related)

    def toggle_similar_cases_who(self, index):
        has_similar = self.similar_cases_combo.itemText(index).startswith("نعم")
        self.similar_cases_who_label.setVisible(has_similar)
        self.similar_cases_who_edit.setVisible(has_similar)

    def collect_data_from_form(self):
        """Collects all data from the form fields into a dictionary."""
        # Extract father and mother ages from labels (removing the "سنة" suffix)
        father_age_text = self.father_age_label.text().split(" ")[0] if self.father_age_label.text() != "يتم حسابه" else "0"
        mother_age_text = self.mother_age_label.text().split(" ")[0] if self.mother_age_label.text() != "يتم حسابه" else "0"
        
        try:
            father_age = int(father_age_text)
        except ValueError:
            father_age = 0
            
        try:
            mother_age = int(mother_age_text)
        except ValueError:
            mother_age = 0
            
        return {
            "child_name": self.child_name_edit.text().strip(),
            "dob": self.dob_edit.date().toString("yyyy-MM-dd"),
            "age": self.age_label.text(),
            "gender": self.gender_combo.currentText(),
            "first_language": self.first_lang_edit.currentText(),
            "first_language_notes": self.first_lang_notes.text().strip(),
            "second_language": self.second_lang_edit.currentText(),
            "second_language_notes": self.second_lang_notes.text().strip(),
            "diagnosis": self.diagnosis_edit.text().strip(),
            "diagnosed_by": self.diagnosed_by_edit.text().strip(),
            
            "father_name": self.father_name_edit.text().strip(),
            "father_dob": self.father_dob_edit.date().toString("yyyy-MM-dd"),
            "father_age": father_age,
            "father_job": self.father_job_edit.text().strip(),
            "father_health": self.father_health_edit.text().strip(),
            
            "mother_name": self.mother_name_edit.text().strip(),
            "mother_dob": self.mother_dob_edit.date().toString("yyyy-MM-dd"),
            "mother_age": mother_age,
            "mother_job": self.mother_job_edit.text().strip(),
            "mother_health": self.mother_health_edit.text().strip(),
            
            "father_preg_age": self.father_preg_age_label.text(),
            "mother_preg_age": self.mother_preg_age_label.text(),
            
            "parents_relation": self.parents_relation_combo.currentText(),
            "relation_degree": self.relation_degree_edit.currentText() if self.relation_degree_edit.isVisible() else "",
            
            "family_size": self.family_size_spin.value(),
            "siblings_count": self.siblings_count_spin.value(),
            "child_order": self.child_order_spin.value(),
            
            "similar_cases_family": self.similar_cases_combo.currentText(),
            "similar_cases_who": self.similar_cases_who_edit.text().strip() if self.similar_cases_who_edit.isVisible() else "",
        }

    def load_data_into_form(self, data):
        """Populates the form fields with the given data dictionary."""
        self._updating_fields = True
        
        self.child_name_edit.setText(data.get("child_name", ""))
        dob_date = QDate.fromString(data.get("dob", ""), "yyyy-MM-dd")
        if dob_date.isValid():
            self.dob_edit.setDate(dob_date)
            self.day_edit.setText("{:02}".format(dob_date.day()))
            self.month_edit.setText("{:02}".format(dob_date.month()))
            self.year_edit.setText("{:02}".format(dob_date.year()))
            
        self.gender_combo.setCurrentText(data.get("gender", ""))
        self.first_lang_edit.setCurrentText(data.get("first_language", ""))
        self.first_lang_notes.setText(data.get("first_language_notes", ""))
        self.second_lang_edit.setCurrentText(data.get("second_language", ""))
        self.second_lang_notes.setText(data.get("second_language_notes", ""))
        self.diagnosis_edit.setText(data.get("diagnosis", ""))
        self.diagnosed_by_edit.setText(data.get("diagnosed_by", ""))

        self.father_name_edit.setText(data.get("father_name", ""))
        
        # Load father DOB if available
        father_dob_date = QDate.fromString(data.get("father_dob", ""), "yyyy-MM-dd")
        if father_dob_date.isValid():
            self.father_dob_edit.setDate(father_dob_date)
            self.father_day_edit.setText("{:02}".format(father_dob_date.day()))
            self.father_month_edit.setText("{:02}".format(father_dob_date.month()))
            self.father_year_edit.setText("{:02}".format(father_dob_date.year()))            
        
        self.father_job_edit.setText(data.get("father_job", ""))
        self.father_health_edit.setText(data.get("father_health", ""))

        self.mother_name_edit.setText(data.get("mother_name", ""))
        
        # Load mother DOB if available
        mother_dob_date = QDate.fromString(data.get("mother_dob", ""), "yyyy-MM-dd")
        if mother_dob_date.isValid():
            self.mother_dob_edit.setDate(mother_dob_date)
            self.mother_day_edit.setText("{:02}".format(mother_dob_date.day()))
            self.mother_month_edit.setText("{:02}".format(mother_dob_date.month()))
            self.mother_year_edit.setText("{:02}".format(mother_dob_date.year()))    

        self.mother_job_edit.setText(data.get("mother_job", ""))
        self.mother_health_edit.setText(data.get("mother_health", ""))

        self.parents_relation_combo.setCurrentText(data.get("parents_relation", ""))
        if data.get("relation_degree"):
            self.relation_degree_edit.setCurrentText(data.get("relation_degree", ""))
        self.toggle_relation_degree(self.parents_relation_combo.currentIndex()) # Ensure visibility is correct

        self.family_size_spin.setValue(data.get("family_size", 0))
        self.siblings_count_spin.setValue(data.get("siblings_count", 0))
        self.child_order_spin.setValue(data.get("child_order", 0))

        self.similar_cases_combo.setCurrentText(data.get("similar_cases_family", ""))
        self.similar_cases_who_edit.setText(data.get("similar_cases_who", ""))
        self.toggle_similar_cases_who(self.similar_cases_combo.currentIndex()) # Ensure visibility is correct
        
        self._updating_fields = False
        
        # Recalculate all ages based on loaded data
        self.calculate_father_age()
        self.calculate_mother_age()
        self.calculate_age()

    def save_case_data(self):
        case_data = self.collect_data_from_form()

        if not case_data["child_name"]:
            QMessageBox.warning(self, "بيانات ناقصة", "الرجاء إدخال اسم الحالة.")
            self.child_name_edit.setFocus()
            return

        if not self.case_data_to_load:
            case_data["case_id"] = get_next_case_id()
        else:
            case_data["case_id"] = self.case_data_to_load.get("case_id")

        success, message_or_path = save_case_data_to_json(case_data)

        if success:
            QMessageBox.information(self, "تم الحفظ", message_or_path)
            self.accept()
        else:
            QMessageBox.critical(self, "خطأ في الحفظ", message_or_path)
