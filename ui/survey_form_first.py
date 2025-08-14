from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QScrollArea,
    QDateEdit, QPushButton, QMessageBox, QLabel, QComboBox,
    QLineEdit, QGroupBox, QWidget
)
from PyQt5.QtCore import QDate, Qt, QSize
from PyQt5.QtGui import QIcon

from datetime import datetime

from utils.file_manager import save_survey_data_to_json, load_case_data_from_json # type: ignore
from utils.general import make_all_labels_copyable # type: ignore

class SurveyFormFirst(QDialog):
    def __init__(self, case_folder_name, parent=None, survey_data_to_edit=None):
        super().__init__(parent)
        self.case_folder_name = case_folder_name
        self.survey_data_to_edit = survey_data_to_edit
        self.case_data = load_case_data_from_json(case_folder_name)
        
        if not self.case_data:
            QMessageBox.critical(self, "خطأ", "فشل تحميل بيانات الحالة.")
            self.reject()
            return

        # --- Window Properties ---
        self.setWindowTitle("استبيان التقييم الأول")
        self.setGeometry(250, 50, 800, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setWindowState(Qt.WindowMaximized)

        # --- Main Layout ---
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)

        container_widget = QWidget()
        self.main_layout = QVBoxLayout(container_widget)

        # --- Case Information Display ---
        self.setup_case_info_section()
        
        # --- Survey Fields ---
        self.setup_survey_fields()

        # --- Buttons (Save, Cancel) ---
        self.button_box = QHBoxLayout()

        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon("icons/save.png"))
        self.save_button.setIconSize(QSize(32, 32))
        self.save_button.setToolTip("حفظ")   

        self.save_button.clicked.connect(self.save_survey_data)

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
        
        # Load survey data if editing
        if self.survey_data_to_edit:
            self.load_survey_data()
            
        # Apply styling
        self.apply_styles()

        make_all_labels_copyable(self)

    def setup_case_info_section(self):
        """Set up the section displaying basic case information"""
        case_info_group = QGroupBox("معلومات الحالة")
        case_info_layout = QFormLayout()
        case_info_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        case_info_layout.setLabelAlignment(Qt.AlignRight)
        case_info_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        
        # Display basic case information
        child_name = self.case_data.get("child_name", {}).get("value", "-")
        dob = self.case_data.get("dob", {}).get("value", "-")
        gender = self.case_data.get("gender", {}).get("value", "-")
        case_id = self.case_data.get("case_id", "-")
        
        case_info_layout.addRow(QLabel("اسم الحالة:"), QLabel(child_name))
        case_info_layout.addRow(QLabel("تاريخ الميلاد:"), QLabel(dob))
        case_info_layout.addRow(QLabel("الجنس:"), QLabel(gender))
        case_info_layout.addRow(QLabel("رقم الحالة:"), QLabel(str(case_id)))
        
        case_info_group.setLayout(case_info_layout)
        self.main_layout.addWidget(case_info_group)

    def setup_survey_fields(self):
        """Set up all survey fields from survey_form_first.txt"""
        survey_group = QGroupBox("استبيان التقييم الأول")
        survey_layout = QFormLayout()
        survey_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        survey_layout.setLabelAlignment(Qt.AlignRight)
        survey_layout.setFieldGrowthPolicy(QFormLayout.FieldsStayAtSizeHint)
        
        # Survey date field
        self.survey_date_label = QLabel("تاريخ التقيم:")
        self.survey_date_edit = QDateEdit()
        self.survey_date_edit.setDate(QDate.currentDate())
        self.survey_date_edit.setCalendarPopup(True)
        self.survey_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.survey_date_edit.setFixedWidth(325)
        self.survey_date_edit.setFixedHeight(40)
        survey_layout.addRow(self.survey_date_label, self.survey_date_edit)
        
        # School information
        self.school_attendance_label = QLabel("هل يذهب الى (المدرسة \\ الحضانة):")
        self.school_attendance_combo = QComboBox()
        self.school_attendance_combo.addItems(["نعم", "لا"])
        self.school_attendance_combo.setFixedWidth(325)
        self.school_attendance_combo.setFixedHeight(40)
        survey_layout.addRow(self.school_attendance_label, self.school_attendance_combo)
        
        self.school_year_label = QLabel("العام الدراسى:")
        self.school_year_edit = QLineEdit()
        self.school_year_edit.setFixedWidth(325)
        self.school_year_edit.setFixedHeight(40)
        survey_layout.addRow(self.school_year_label, self.school_year_edit)
        
        self.school_duration_label = QLabel("المدى التى قضاها:")
        self.school_duration_edit = QLineEdit()
        self.school_duration_edit.setFixedWidth(325)
        self.school_duration_edit.setFixedHeight(40)
        survey_layout.addRow(self.school_duration_label, self.school_duration_edit)
        
        self.school_type_label = QLabel("نوعها:")
        self.school_type_edit = QLineEdit()
        self.school_type_edit.setFixedWidth(325)
        self.school_type_edit.setFixedHeight(40)
        survey_layout.addRow(self.school_type_label, self.school_type_edit)
        
        self.school_discontinue_label = QLabel("سبب عدم الاستمرار:")
        self.school_discontinue_edit = QLineEdit()
        self.school_discontinue_edit.setFixedWidth(325)
        self.school_discontinue_edit.setFixedHeight(40)
        survey_layout.addRow(self.school_discontinue_label, self.school_discontinue_edit)
        
        # Care center information
        self.care_center_label = QLabel("هل يذهب الى (مركز \\ اكاديمية رعاية):")
        self.care_center_combo = QComboBox()
        self.care_center_combo.addItems(["نعم", "لا"])
        self.care_center_combo.setFixedWidth(325)
        self.care_center_combo.setFixedHeight(40)
        survey_layout.addRow(self.care_center_label, self.care_center_combo)
        
        self.care_duration_label = QLabel("المدى التى قضاها:")
        self.care_duration_edit = QLineEdit()
        self.care_duration_edit.setFixedWidth(325)
        self.care_duration_edit.setFixedHeight(40)
        survey_layout.addRow(self.care_duration_label, self.care_duration_edit)
        
        self.care_type_label = QLabel("نوعها:")
        self.care_type_edit = QLineEdit()
        self.care_type_edit.setFixedWidth(325)
        self.care_type_edit.setFixedHeight(40)
        survey_layout.addRow(self.care_type_label, self.care_type_edit)
        
        self.care_discontinue_label = QLabel("سبب عدم الاستمرار:")
        self.care_discontinue_edit = QLineEdit()
        self.care_discontinue_edit.setFixedWidth(325)
        self.care_discontinue_edit.setFixedHeight(40)
        survey_layout.addRow(self.care_discontinue_label, self.care_discontinue_edit)
        
        # Academic issues
        self.academic_issues_label = QLabel("هل يوجد مشاكل فى التحصيل الدراسى:")
        self.academic_issues_combo = QComboBox()
        self.academic_issues_combo.addItems(["نعم", "لا"])
        self.academic_issues_combo.setFixedWidth(325)
        self.academic_issues_combo.setFixedHeight(40)
        survey_layout.addRow(self.academic_issues_label, self.academic_issues_combo)
        
        self.academic_issues_type_label = QLabel("نوعها:")
        self.academic_issues_type_edit = QLineEdit()
        self.academic_issues_type_edit.setFixedWidth(325)
        self.academic_issues_type_edit.setFixedHeight(40)
        survey_layout.addRow(self.academic_issues_type_label, self.academic_issues_type_edit)
        
        # Development indicators
        self.abnormal_dev_label = QLabel("هل كانت هناك اشارات تدل على نمو غير طبيعى:")
        self.abnormal_dev_edit = QLineEdit()
        self.abnormal_dev_edit.setFixedWidth(325)
        self.abnormal_dev_edit.setFixedHeight(40)
        survey_layout.addRow(self.abnormal_dev_label, self.abnormal_dev_edit)
        
        self.abnormal_dev_what_label = QLabel("ما هى:")
        self.abnormal_dev_what_edit = QLineEdit()
        self.abnormal_dev_what_edit.setFixedWidth(325)
        self.abnormal_dev_what_edit.setFixedHeight(40)
        survey_layout.addRow(self.abnormal_dev_what_label, self.abnormal_dev_what_edit)
        
        self.diagnosis_what_label = QLabel("ما هو تشخيصه:")
        self.diagnosis_what_edit = QLineEdit()
        self.diagnosis_what_edit.setFixedWidth(325)
        self.diagnosis_what_edit.setFixedHeight(40)
        survey_layout.addRow(self.diagnosis_what_label, self.diagnosis_what_edit)
        
        # Breastfeeding information
        self.breastfeeding_duration_label = QLabel("مدة الرضاعة:")
        self.breastfeeding_duration_edit = QLineEdit()
        self.breastfeeding_duration_edit.setFixedWidth(325)
        self.breastfeeding_duration_edit.setFixedHeight(40)
        survey_layout.addRow(self.breastfeeding_duration_label, self.breastfeeding_duration_edit)
        
        self.breastfeeding_type_label = QLabel("نوع الرضاعة:")
        self.breastfeeding_type_combo = QComboBox()
        self.breastfeeding_type_combo.addItems(["طبيعى", "صناعى"])
        self.breastfeeding_type_combo.setFixedWidth(325)
        self.breastfeeding_type_combo.setFixedHeight(40)
        survey_layout.addRow(self.breastfeeding_type_label, self.breastfeeding_type_combo)
        
        self.weaning_label = QLabel("الفطام:")
        self.weaning_combo = QComboBox()
        self.weaning_combo.addItems(["تدريجى", "مفاجئ"])
        self.weaning_combo.setFixedWidth(325)
        self.weaning_combo.setFixedHeight(40)
        survey_layout.addRow(self.weaning_label, self.weaning_combo)
        
        self.weaning_age_label = QLabel("سن الفطام:")
        self.weaning_age_edit = QLineEdit()
        self.weaning_age_edit.setFixedWidth(325)
        self.weaning_age_edit.setFixedHeight(40)
        survey_layout.addRow(self.weaning_age_label, self.weaning_age_edit)
        
        self.breastfeeding_problems_label = QLabel("هل وجد مشاكل بالرضاعة:")
        self.breastfeeding_problems_edit = QLineEdit()
        self.breastfeeding_problems_edit.setFixedWidth(325)
        self.breastfeeding_problems_edit.setFixedHeight(40)
        survey_layout.addRow(self.breastfeeding_problems_label, self.breastfeeding_problems_edit)
        
        # Development milestones
        self.teething_label = QLabel("التسنين:")
        self.teething_edit = QLineEdit()
        self.teething_edit.setFixedWidth(325)
        self.teething_edit.setFixedHeight(40)
        survey_layout.addRow(self.teething_label, self.teething_edit)
        
        self.crawling_label = QLabel("الحبو:")
        self.crawling_edit = QLineEdit()
        self.crawling_edit.setFixedWidth(325)
        self.crawling_edit.setFixedHeight(40)
        survey_layout.addRow(self.crawling_label, self.crawling_edit)
        
        self.sitting_label = QLabel("الجلوس:")
        self.sitting_edit = QLineEdit()
        self.sitting_edit.setFixedWidth(325)
        self.sitting_edit.setFixedHeight(40)
        survey_layout.addRow(self.sitting_label, self.sitting_edit)
        
        self.standing_label = QLabel("الوقوف:")
        self.standing_edit = QLineEdit()
        self.standing_edit.setFixedWidth(325)
        self.standing_edit.setFixedHeight(40)
        survey_layout.addRow(self.standing_label, self.standing_edit)
        
        self.walking_start_label = QLabel("بدا المشى:")
        self.walking_start_edit = QLineEdit()
        self.walking_start_edit.setFixedWidth(325)
        self.walking_start_edit.setFixedHeight(40)
        survey_layout.addRow(self.walking_start_label, self.walking_start_edit)
        
        self.walking_label = QLabel("المشى:")
        self.walking_edit = QLineEdit()
        self.walking_edit.setFixedWidth(325)
        self.walking_edit.setFixedHeight(40)
        survey_layout.addRow(self.walking_label, self.walking_edit)
        
        # Toilet training
        self.diaper_free_label = QLabel("متى تخلص من الحفاظ:")
        self.diaper_free_edit = QLineEdit()
        self.diaper_free_edit.setFixedWidth(325)
        self.diaper_free_edit.setFixedHeight(40)
        survey_layout.addRow(self.diaper_free_label, self.diaper_free_edit)
        
        self.bathroom_request_label = QLabel("استخدام الحمام الان:")
        self.bathroom_request_combo = QComboBox()
        self.bathroom_request_combo.addItems(["يطلب لفظيا", "بالاشارة", "يحتاج تدريب"])
        self.bathroom_request_combo.setFixedWidth(325)
        self.bathroom_request_combo.setFixedHeight(40)
        survey_layout.addRow(self.bathroom_request_label, self.bathroom_request_combo)
        
        self.bathroom_independence_label = QLabel("يدخل الحمام:")
        self.bathroom_independence_combo = QComboBox()
        self.bathroom_independence_combo.addItems(["وحدة", "مساعدة جزئية", "مساعدة كلية"])
        self.bathroom_independence_combo.setFixedWidth(325)
        self.bathroom_independence_combo.setFixedHeight(40)
        survey_layout.addRow(self.bathroom_independence_label, self.bathroom_independence_combo)
        
        # Vision issues
        self.vision_issues_label = QLabel("هل يعانى من اي ضعف فى درجة الابصار؟")
        self.vision_issues_combo = QComboBox()
        self.vision_issues_combo.addItems(["نعم", "لا"])
        self.vision_issues_combo.setFixedWidth(325)
        self.vision_issues_combo.setFixedHeight(40)
        survey_layout.addRow(self.vision_issues_label, self.vision_issues_combo)
        
        self.vision_type_label = QLabel("نوعه:")
        self.vision_type_edit = QLineEdit()
        self.vision_type_edit.setFixedWidth(325)
        self.vision_type_edit.setFixedHeight(40)
        survey_layout.addRow(self.vision_type_label, self.vision_type_edit)
        
        self.vision_severity_label = QLabel("شدته:")
        self.vision_severity_edit = QLineEdit()
        self.vision_severity_edit.setFixedWidth(325)
        self.vision_severity_edit.setFixedHeight(40)
        survey_layout.addRow(self.vision_severity_label, self.vision_severity_edit)
        
        # Hearing issues
        self.hearing_issues_label = QLabel("هل يعانى من ضعف سمع؟")
        self.hearing_issues_combo = QComboBox()
        self.hearing_issues_combo.addItems(["نعم", "لا"])
        self.hearing_issues_combo.setFixedWidth(325)
        self.hearing_issues_combo.setFixedHeight(40)
        survey_layout.addRow(self.hearing_issues_label, self.hearing_issues_combo)
        
        self.hearing_type_label = QLabel("نوعه:")
        self.hearing_type_combo = QComboBox()
        self.hearing_type_combo.addItems(["توصيلى", "حسى عصبى", "مركزى", "مختلط"])
        self.hearing_type_combo.setFixedWidth(325)
        self.hearing_type_combo.setFixedHeight(40)
        survey_layout.addRow(self.hearing_type_label, self.hearing_type_combo)
        
        self.hearing_severity_label = QLabel("شدته:")
        self.hearing_severity_edit = QLineEdit()
        self.hearing_severity_edit.setFixedWidth(325)
        self.hearing_severity_edit.setFixedHeight(40)
        survey_layout.addRow(self.hearing_severity_label, self.hearing_severity_edit)
        
        # Hearing aids
        self.hearing_aid_label = QLabel("هل يلبس سماعات؟")
        self.hearing_aid_combo = QComboBox()
        self.hearing_aid_combo.addItems(["نعم", "لا"])
        self.hearing_aid_combo.setFixedWidth(325)
        self.hearing_aid_combo.setFixedHeight(40)
        survey_layout.addRow(self.hearing_aid_label, self.hearing_aid_combo)
        
        self.hearing_aid_type_label = QLabel("نوعها:")
        self.hearing_aid_type_edit = QLineEdit()
        self.hearing_aid_type_edit.setFixedWidth(325)
        self.hearing_aid_type_edit.setFixedHeight(40)
        survey_layout.addRow(self.hearing_aid_type_label, self.hearing_aid_type_edit)
        
        self.cochlear_implant_label = QLabel("هل يلبس قوقعة؟")
        self.cochlear_implant_combo = QComboBox()
        self.cochlear_implant_combo.addItems(["نعم", "لا"])
        self.cochlear_implant_combo.setFixedWidth(325)
        self.cochlear_implant_combo.setFixedHeight(40)
        survey_layout.addRow(self.cochlear_implant_label, self.cochlear_implant_combo)
        
        self.cochlear_since_label = QLabel("من امتى؟")
        self.cochlear_since_edit = QLineEdit()
        self.cochlear_since_edit.setFixedWidth(325)
        self.cochlear_since_edit.setFixedHeight(40)
        survey_layout.addRow(self.cochlear_since_label, self.cochlear_since_edit)
        
        # Speech characteristics
        self.speech_tone_label = QLabel("هل يتحدث الطفل بنبرة صوت ثابتة معينة:")
        self.speech_tone_combo = QComboBox()
        self.speech_tone_combo.addItems(["نعم", "لا"])
        self.speech_tone_combo.setFixedWidth(325)
        self.speech_tone_combo.setFixedHeight(40)
        survey_layout.addRow(self.speech_tone_label, self.speech_tone_combo)
        
        self.speech_volume_label = QLabel("هل يتحدث الطفل بصوت:")
        self.speech_volume_combo = QComboBox()
        self.speech_volume_combo.addItems(["مرتفع", "منخفض"])
        self.speech_volume_combo.setFixedWidth(325)
        self.speech_volume_combo.setFixedHeight(40)
        survey_layout.addRow(self.speech_volume_label, self.speech_volume_combo)
        
        # Other physical issues
        self.drooling_label = QLabel("هل يعانى الطفل من سيلان اللعاب:")
        self.drooling_combo = QComboBox()
        self.drooling_combo.addItems(["نعم", "لا"])
        self.drooling_combo.setFixedWidth(325)
        self.drooling_combo.setFixedHeight(40)
        survey_layout.addRow(self.drooling_label, self.drooling_combo)
        
        self.swallowing_label = QLabel("يعانى الطفل من صعوبة بلع:")
        self.swallowing_combo = QComboBox()
        self.swallowing_combo.addItems(["نعم", "لا"])
        self.swallowing_combo.setFixedWidth(325)
        self.swallowing_combo.setFixedHeight(40)
        survey_layout.addRow(self.swallowing_label, self.swallowing_combo)
        
        self.breathing_label = QLabel("هل يعانى الطفل من اضطرابات التنفس:")
        self.breathing_combo = QComboBox()
        self.breathing_combo.addItems(["نعم", "لا"])
        self.breathing_combo.setFixedWidth(325)
        self.breathing_combo.setFixedHeight(40)
        survey_layout.addRow(self.breathing_label, self.breathing_combo)
        
        self.breathing_type_label = QLabel("نوع اضطراب التنفس:")
        self.breathing_type_combo = QComboBox()
        self.breathing_type_combo.addItems(["شهيق", "زفير", "نفخ", "شفط"])
        self.breathing_type_combo.setFixedWidth(325)
        self.breathing_type_combo.setFixedHeight(40)
        survey_layout.addRow(self.breathing_type_label, self.breathing_type_combo)
        
        # Tests and evaluations
        self.iq_test_label = QLabel("اختبار ذكاء IQ:")
        self.iq_test_combo = QComboBox()
        self.iq_test_combo.addItems(["نعم", "لا"])
        self.iq_test_combo.setFixedWidth(325)
        self.iq_test_combo.setFixedHeight(40)
        survey_layout.addRow(self.iq_test_label, self.iq_test_combo)
        
        self.iq_score_label = QLabel("الدرجة:")
        self.iq_score_edit = QLineEdit()
        self.iq_score_edit.setFixedWidth(325)
        self.iq_score_edit.setFixedHeight(40)
        survey_layout.addRow(self.iq_score_label, self.iq_score_edit)
        
        self.hearing_test_label = QLabel("مقياس السمع:")
        self.hearing_test_combo = QComboBox()
        self.hearing_test_combo.addItems(["نعم", "لا"])
        self.hearing_test_combo.setFixedWidth(325)
        self.hearing_test_combo.setFixedHeight(40)
        survey_layout.addRow(self.hearing_test_label, self.hearing_test_combo)
        
        self.hearing_score_label = QLabel("الدرجة:")
        self.hearing_score_edit = QLineEdit()
        self.hearing_score_edit.setFixedWidth(325)
        self.hearing_score_edit.setFixedHeight(40)
        survey_layout.addRow(self.hearing_score_label, self.hearing_score_edit)
        
        self.ear_pressure_label = QLabel("ضغط الاذن:")
        self.ear_pressure_combo = QComboBox()
        self.ear_pressure_combo.addItems(["نعم", "لا"])
        self.ear_pressure_combo.setFixedWidth(325)
        self.ear_pressure_combo.setFixedHeight(40)
        survey_layout.addRow(self.ear_pressure_label, self.ear_pressure_combo)
        
        self.language_test_label = QLabel("اختبار اللغة:")
        self.language_test_combo = QComboBox()
        self.language_test_combo.addItems(["نعم", "لا"])
        self.language_test_combo.setFixedWidth(325)
        self.language_test_combo.setFixedHeight(40)
        survey_layout.addRow(self.language_test_label, self.language_test_combo)
        
        self.speech_test_label = QLabel("اختبار نطق:")
        self.speech_test_combo = QComboBox()
        self.speech_test_combo.addItems(["نعم", "لا"])
        self.speech_test_combo.setFixedWidth(325)
        self.speech_test_combo.setFixedHeight(40)
        survey_layout.addRow(self.speech_test_label, self.speech_test_combo)
        
        # Rehabilitation acceptance
        self.case_acceptance_label = QLabel("مدى تقبل الحالة للتاهيل:")
        self.case_acceptance_edit = QLineEdit()
        self.case_acceptance_edit.setFixedWidth(325)
        self.case_acceptance_edit.setFixedHeight(40)
        survey_layout.addRow(self.case_acceptance_label, self.case_acceptance_edit)
        
        self.family_acceptance_label = QLabel("مدى تقبل الاسرة للمشكلة:")
        self.family_acceptance_edit = QLineEdit()
        self.family_acceptance_edit.setFixedWidth(325)
        self.family_acceptance_edit.setFixedHeight(40)
        survey_layout.addRow(self.family_acceptance_label, self.family_acceptance_edit)
        
        # Therapy types
        self.speech_therapy_label = QLabel("تخاطب:")
        self.speech_therapy_combo = QComboBox()
        self.speech_therapy_combo.addItems(["نعم", "لا"])
        self.speech_therapy_combo.setFixedWidth(325)
        self.speech_therapy_combo.setFixedHeight(40)
        survey_layout.addRow(self.speech_therapy_label, self.speech_therapy_combo)
        
        self.speech_therapy_progress_label = QLabel("مدى التقدم:")
        self.speech_therapy_progress_edit = QLineEdit()
        self.speech_therapy_progress_edit.setFixedWidth(325)
        self.speech_therapy_progress_edit.setFixedHeight(40)
        survey_layout.addRow(self.speech_therapy_progress_label, self.speech_therapy_progress_edit)
        
        self.physical_therapy_label = QLabel("علاج طبيعى:")
        self.physical_therapy_combo = QComboBox()
        self.physical_therapy_combo.addItems(["نعم", "لا"])
        self.physical_therapy_combo.setFixedWidth(325)
        self.physical_therapy_combo.setFixedHeight(40)
        survey_layout.addRow(self.physical_therapy_label, self.physical_therapy_combo)
        
        self.physical_therapy_progress_label = QLabel("مدى التقدم:")
        self.physical_therapy_progress_edit = QLineEdit()
        self.physical_therapy_progress_edit.setFixedWidth(325)
        self.physical_therapy_progress_edit.setFixedHeight(40)
        survey_layout.addRow(self.physical_therapy_progress_label, self.physical_therapy_progress_edit)
        
        self.computer_therapy_label = QLabel("التعامل مع الكمبيوتر:")
        self.computer_therapy_combo = QComboBox()
        self.computer_therapy_combo.addItems(["نعم", "لا"])
        self.computer_therapy_combo.setFixedWidth(325)
        self.computer_therapy_combo.setFixedHeight(40)
        survey_layout.addRow(self.computer_therapy_label, self.computer_therapy_combo)
        
        self.computer_therapy_progress_label = QLabel("مدى التقدم:")
        self.computer_therapy_progress_edit = QLineEdit()
        self.computer_therapy_progress_edit.setFixedWidth(325)
        self.computer_therapy_progress_edit.setFixedHeight(40)
        survey_layout.addRow(self.computer_therapy_progress_label, self.computer_therapy_progress_edit)
        
        self.skills_therapy_label = QLabel("تنمية المهارات:")
        self.skills_therapy_combo = QComboBox()
        self.skills_therapy_combo.addItems(["نعم", "لا"])
        self.skills_therapy_combo.setFixedWidth(325)
        self.skills_therapy_combo.setFixedHeight(40)
        survey_layout.addRow(self.skills_therapy_label, self.skills_therapy_combo)
        
        self.skills_therapy_progress_label = QLabel("مدى التقدم:")
        self.skills_therapy_progress_edit = QLineEdit()
        self.skills_therapy_progress_edit.setFixedWidth(325)
        self.skills_therapy_progress_edit.setFixedHeight(40)
        survey_layout.addRow(self.skills_therapy_progress_label, self.skills_therapy_progress_edit)
        
        # Preferences
        self.favorite_food_label = QLabel("ما اكثر الماكولات او المشروبات التى يفضلها:")
        self.favorite_food_edit = QLineEdit()
        self.favorite_food_edit.setFixedWidth(325)
        self.favorite_food_edit.setFixedHeight(40)
        survey_layout.addRow(self.favorite_food_label, self.favorite_food_edit)
        
        self.favorite_games_label = QLabel("ما اكثر الالعاب التى يحبها:")
        self.favorite_games_edit = QLineEdit()
        self.favorite_games_edit.setFixedWidth(325)
        self.favorite_games_edit.setFixedHeight(40)
        survey_layout.addRow(self.favorite_games_label, self.favorite_games_edit)
        
        self.other_likes_label = QLabel("اشياء اخرى يحبها:")
        self.other_likes_edit = QLineEdit()
        self.other_likes_edit.setFixedWidth(325)
        self.other_likes_edit.setFixedHeight(40)
        survey_layout.addRow(self.other_likes_label, self.other_likes_edit)
        
        self.dislikes_label = QLabel("اشياء ينزعج منها:")
        self.dislikes_edit = QLineEdit()
        self.dislikes_edit.setFixedWidth(325)
        self.dislikes_edit.setFixedHeight(40)
        survey_layout.addRow(self.dislikes_label, self.dislikes_edit)
        
        # Family situation
        self.living_with_label = QLabel("مع من يعيش الطفل:")
        self.living_with_edit = QLineEdit()
        self.living_with_edit.setFixedWidth(325)
        self.living_with_edit.setFixedHeight(40)
        survey_layout.addRow(self.living_with_label, self.living_with_edit)
        
        self.attached_people_label = QLabel("هل يوجد اشخاص مرتبط بيهم الحالة (من الاسرة أو في المحيط) ويؤثرون فيه:")
        self.attached_people_edit = QLineEdit()
        self.attached_people_edit.setFixedWidth(325)
        self.attached_people_edit.setFixedHeight(40)
        survey_layout.addRow(self.attached_people_label, self.attached_people_edit)
        
        self.caregiver_label = QLabel("من هو القائم برعاية الطفل:")
        self.caregiver_edit = QLineEdit()
        self.caregiver_edit.setFixedWidth(325)
        self.caregiver_edit.setFixedHeight(40)
        survey_layout.addRow(self.caregiver_label, self.caregiver_edit)
        
        self.economic_status_label = QLabel("الوضع الاقتصادى:")
        self.economic_status_edit = QLineEdit()
        self.economic_status_edit.setFixedWidth(325)
        self.economic_status_edit.setFixedHeight(40)
        survey_layout.addRow(self.economic_status_label, self.economic_status_edit)
        
        self.cultural_status_label = QLabel("الوضع الثقافى:")
        self.cultural_status_edit = QLineEdit()
        self.cultural_status_edit.setFixedWidth(325)
        self.cultural_status_edit.setFixedHeight(40)
        survey_layout.addRow(self.cultural_status_label, self.cultural_status_edit)
        
        self.social_status_label = QLabel("الوضع الاجتماعى:")
        self.social_status_edit = QLineEdit()
        self.social_status_edit.setFixedWidth(325)
        self.social_status_edit.setFixedHeight(40)
        survey_layout.addRow(self.social_status_label, self.social_status_edit)
        
        self.family_relationship_label = QLabel("طبيعة العلاقة الاسرية:")
        self.family_relationship_edit = QLineEdit()
        self.family_relationship_edit.setFixedWidth(325)
        self.family_relationship_edit.setFixedHeight(40)
        survey_layout.addRow(self.family_relationship_label, self.family_relationship_edit)
        
        self.family_acceptance_rehab_label = QLabel("مدى تقبل الاسرة للاضطراب واستعدادها للمشاركة فى التأهيل:")
        self.family_acceptance_rehab_edit = QLineEdit()
        self.family_acceptance_rehab_edit.setFixedWidth(325)
        self.family_acceptance_rehab_edit.setFixedHeight(40)
        survey_layout.addRow(self.family_acceptance_rehab_label, self.family_acceptance_rehab_edit)
        
        # Pregnancy and birth
        self.mother_health_pregnancy_label = QLabel("صحة الام اثناء الحمل كانت:")
        self.mother_health_pregnancy_combo = QComboBox()
        self.mother_health_pregnancy_combo.addItems(["مستقرة", "غير مستقرة"])
        self.mother_health_pregnancy_combo.setFixedWidth(325)
        self.mother_health_pregnancy_combo.setFixedHeight(40)
        survey_layout.addRow(self.mother_health_pregnancy_label, self.mother_health_pregnancy_combo)
        
        self.birth_type_label = QLabel("نوع الولادة:")
        self.birth_type_combo = QComboBox()
        self.birth_type_combo.addItems(["طبيعى", "قيصرى"])
        self.birth_type_combo.setFixedWidth(325)
        self.birth_type_combo.setFixedHeight(40)
        survey_layout.addRow(self.birth_type_label, self.birth_type_combo)
        
        self.birth_weight_label = QLabel("وزن الطفل عند الولادة:")
        self.birth_weight_edit = QLineEdit()
        self.birth_weight_edit.setFixedWidth(325)
        self.birth_weight_edit.setFixedHeight(40)
        survey_layout.addRow(self.birth_weight_label, self.birth_weight_edit)
        
        self.birth_cry_label = QLabel("هل صرخ الطفل صرخة الميلاد:")
        self.birth_cry_combo = QComboBox()
        self.birth_cry_combo.addItems(["نعم", "لا"])
        self.birth_cry_combo.setFixedWidth(325)
        self.birth_cry_combo.setFixedHeight(40)
        survey_layout.addRow(self.birth_cry_label, self.birth_cry_combo)
        
        self.head_size_label = QLabel("حجم راس الطفل عند الولادة:")
        self.head_size_combo = QComboBox()
        self.head_size_combo.addItems(["طبيعى", "غير طبيعى"])
        self.head_size_combo.setFixedWidth(325)
        self.head_size_combo.setFixedHeight(40)
        survey_layout.addRow(self.head_size_label, self.head_size_combo)
        
        self.head_size_value_label = QLabel("كان:")
        self.head_size_value_edit = QLineEdit()
        self.head_size_value_edit.setFixedWidth(325)
        self.head_size_value_edit.setFixedHeight(40)
        survey_layout.addRow(self.head_size_value_label, self.head_size_value_edit)
        
        self.birth_defects_label = QLabel("هل كان هناك عيوب خلقية بعد الولادة:")
        self.birth_defects_combo = QComboBox()
        self.birth_defects_combo.addItems(["نعم", "لا"])
        self.birth_defects_combo.setFixedWidth(325)
        self.birth_defects_combo.setFixedHeight(40)
        survey_layout.addRow(self.birth_defects_label, self.birth_defects_combo)
        
        self.birth_defects_what_label = QLabel("ما هى:")
        self.birth_defects_what_edit = QLineEdit()
        self.birth_defects_what_edit.setFixedWidth(325)
        self.birth_defects_what_edit.setFixedHeight(40)
        survey_layout.addRow(self.birth_defects_what_label, self.birth_defects_what_edit)
        
        # Add many more fields based on survey_form_first.txt
        # This is just a sample of the implementation
        
        survey_group.setLayout(survey_layout)
        self.main_layout.addWidget(survey_group)

    def collect_survey_data(self):
        """Collects data from all survey form fields."""
        # Start with the case data
        survey_data = {
            "survey_type": "استبيان التقييم الأول",
            "survey_date": self.survey_date_edit.date().toString("yyyy-MM-dd"),
            "case_id": self.case_data.get("case_id", ""),
            "child_name": self.case_data.get("child_name", {}).get("value", ""),
            "dob": self.case_data.get("dob", {}).get("value", ""),
            "gender": self.case_data.get("gender", {}).get("value", ""),
            "submission_timestamp": datetime.now().isoformat()
        }

        def field_value(label_widget, input_widget, use_current_text=True):
            return {
                "ar_key": label_widget.text().replace(':', ''),
                "value": input_widget.currentText() if use_current_text else input_widget.text()
            }

        survey_data.update({
            "school_attendance": field_value(self.school_attendance_label, self.school_attendance_combo, True),
            "school_year": field_value(self.school_year_label, self.school_year_edit, False),
            "school_duration": field_value(self.school_duration_label, self.school_duration_edit, False),
            "school_type": field_value(self.school_type_label, self.school_type_edit, False),
            "school_discontinue": field_value(self.school_discontinue_label, self.school_discontinue_edit, False),
            "care_center": field_value(self.care_center_label, self.care_center_combo, True),
            "care_duration": field_value(self.care_duration_label, self.care_duration_edit, False),
            "care_type": field_value(self.care_type_label, self.care_type_edit, False),
            "care_discontinue": field_value(self.care_discontinue_label, self.care_discontinue_edit, False),
            "academic_issues": field_value(self.academic_issues_label, self.academic_issues_combo, True),
            "academic_issues_type": field_value(self.academic_issues_type_label, self.academic_issues_type_edit, False),
            "abnormal_dev": field_value(self.abnormal_dev_label, self.abnormal_dev_edit, False),
            "abnormal_dev_what": field_value(self.abnormal_dev_what_label, self.abnormal_dev_what_edit, False),
            "diagnosis_what": field_value(self.diagnosis_what_label, self.diagnosis_what_edit, False),
            "breastfeeding_duration": field_value(self.breastfeeding_duration_label, self.breastfeeding_duration_edit, False),
            "breastfeeding_type": field_value(self.breastfeeding_type_label, self.breastfeeding_type_combo, True),
            "weaning": field_value(self.weaning_label, self.weaning_combo, True),
            "weaning_age": field_value(self.weaning_age_label, self.weaning_age_edit, False),
            "breastfeeding_problems": field_value(self.breastfeeding_problems_label, self.breastfeeding_problems_edit, False),
            "teething": field_value(self.teething_label, self.teething_edit, False),
            "crawling": field_value(self.crawling_label, self.crawling_edit, False),
            "sitting": field_value(self.sitting_label, self.sitting_edit, False),
            "standing": field_value(self.standing_label, self.standing_edit, False),
            "walking_start": field_value(self.walking_start_label, self.walking_start_edit, False),
            "walking": field_value(self.walking_label, self.walking_edit, False),
            "diaper_free": field_value(self.diaper_free_label, self.diaper_free_edit, False),
            "bathroom_request": field_value(self.bathroom_request_label, self.bathroom_request_combo, True),
            "bathroom_independence": field_value(self.bathroom_independence_label, self.bathroom_independence_combo, True),
            "vision_issues": field_value(self.vision_issues_label, self.vision_issues_combo, True),
            "vision_type": field_value(self.vision_type_label, self.vision_type_edit, False),
            "vision_severity": field_value(self.vision_severity_label, self.vision_severity_edit, False),
            "hearing_issues": field_value(self.hearing_issues_label, self.hearing_issues_combo, True),
            "hearing_type": field_value(self.hearing_type_label, self.hearing_type_combo, True),
            "hearing_severity": field_value(self.hearing_severity_label, self.hearing_severity_edit, False),
            "hearing_aid": field_value(self.hearing_aid_label, self.hearing_aid_combo, True),
            "hearing_aid_type": field_value(self.hearing_aid_type_label, self.hearing_aid_type_edit, False),
            "cochlear_implant": field_value(self.cochlear_implant_label, self.cochlear_implant_combo, True),
            "cochlear_since": field_value(self.cochlear_since_label, self.cochlear_since_edit, False),
            "speech_tone": field_value(self.speech_tone_label, self.speech_tone_combo, True),
            "speech_volume": field_value(self.speech_volume_label, self.speech_volume_combo, True),
            "drooling": field_value(self.drooling_label, self.drooling_combo, True),
            "swallowing": field_value(self.swallowing_label, self.swallowing_combo, True),
            "breathing": field_value(self.breathing_label, self.breathing_combo, True),
            "breathing_type": field_value(self.breathing_type_label, self.breathing_type_combo, True),
            "iq_test": field_value(self.iq_test_label, self.iq_test_combo, True),
            "iq_score": field_value(self.iq_score_label, self.iq_score_edit, False),
            "hearing_test": field_value(self.hearing_test_label, self.hearing_test_combo, True),
            "hearing_score": field_value(self.hearing_score_label, self.hearing_score_edit, False),
            "ear_pressure": field_value(self.ear_pressure_label, self.ear_pressure_combo, True),
            "language_test": field_value(self.language_test_label, self.language_test_combo, True),
            "speech_test": field_value(self.speech_test_label, self.speech_test_combo, True),
            "case_acceptance": field_value(self.case_acceptance_label, self.case_acceptance_edit, False),
            "family_acceptance": field_value(self.family_acceptance_label, self.family_acceptance_edit, False),
            "speech_therapy": field_value(self.speech_therapy_label, self.speech_therapy_combo, True),
            "speech_therapy_progress": field_value(self.speech_therapy_progress_label, self.speech_therapy_progress_edit, False),
            "physical_therapy": field_value(self.physical_therapy_label, self.physical_therapy_combo, True),
            "physical_therapy_progress": field_value(self.physical_therapy_progress_label, self.physical_therapy_progress_edit, False),
            "computer_therapy": field_value(self.computer_therapy_label, self.computer_therapy_combo, True),
            "computer_therapy_progress": field_value(self.computer_therapy_progress_label, self.computer_therapy_progress_edit, False),
            "skills_therapy": field_value(self.skills_therapy_label, self.skills_therapy_combo, True),
            "skills_therapy_progress": field_value(self.skills_therapy_progress_label, self.skills_therapy_progress_edit, False),
            "favorite_food": field_value(self.favorite_food_label, self.favorite_food_edit, False),
            "favorite_games": field_value(self.favorite_games_label, self.favorite_games_edit, False),
            "other_likes": field_value(self.other_likes_label, self.other_likes_edit, False),
            "dislikes": field_value(self.dislikes_label, self.dislikes_edit, False),
            "living_with": field_value(self.living_with_label, self.living_with_edit, False),
            "attached_people": field_value(self.attached_people_label, self.attached_people_edit, False),
            "caregiver": field_value(self.caregiver_label, self.caregiver_edit, False),
            "economic_status": field_value(self.economic_status_label, self.economic_status_edit, False),
            "cultural_status": field_value(self.cultural_status_label, self.cultural_status_edit, False),
            "social_status": field_value(self.social_status_label, self.social_status_edit, False),
            "family_relationship": field_value(self.family_relationship_label, self.family_relationship_edit, False),
            "family_acceptance_rehab": field_value(self.family_acceptance_rehab_label, self.family_acceptance_rehab_edit, False),
            "mother_health_pregnancy": field_value(self.mother_health_pregnancy_label, self.mother_health_pregnancy_combo, True),
            "birth_type": field_value(self.birth_type_label, self.birth_type_combo, True),
            "birth_weight": field_value(self.birth_weight_label, self.birth_weight_edit, False),
            "birth_cry": field_value(self.birth_cry_label, self.birth_cry_combo, True),
            "head_size": field_value(self.head_size_label, self.head_size_combo, True),
            "head_size_value": field_value(self.head_size_value_label, self.head_size_value_edit, False),
            "birth_defects": field_value(self.birth_defects_label, self.birth_defects_combo, True),
            "birth_defects_what": field_value(self.birth_defects_what_label, self.birth_defects_what_edit, False),
        })

        return survey_data

    def load_survey_data(self):
        """Loads survey data into form fields when editing an existing survey."""
        if not self.survey_data_to_edit:
            return
            
        # Set the survey date
        survey_date_str = self.survey_data_to_edit.get("survey_date", "")
        if survey_date_str:
            try:
                date_parts = survey_date_str.split("-")
                if len(date_parts) == 3:
                    self.survey_date_edit.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
            except Exception as e:
                print(f"Error setting survey date: {str(e)}")
        
        # Set all other fields
        self.school_attendance_combo.setCurrentText(self.survey_data_to_edit.get("school_attendance", {}).get("value", ""))
        self.school_year_edit.setText(self.survey_data_to_edit.get("school_year", {}).get("value", ""))
        self.school_duration_edit.setText(self.survey_data_to_edit.get("school_duration", {}).get("value", ""))
        self.school_type_edit.setText(self.survey_data_to_edit.get("school_type", {}).get("value", ""))
        self.school_discontinue_edit.setText(self.survey_data_to_edit.get("school_discontinue", {}).get("value", ""))
        self.care_center_combo.setCurrentText(self.survey_data_to_edit.get("care_center", {}).get("value", ""))
        self.care_duration_edit.setText(self.survey_data_to_edit.get("care_duration", {}).get("value", ""))
        self.care_type_edit.setText(self.survey_data_to_edit.get("care_type", {}).get("value", ""))
        self.care_discontinue_edit.setText(self.survey_data_to_edit.get("care_discontinue", {}).get("value", ""))
        self.academic_issues_combo.setCurrentText(self.survey_data_to_edit.get("academic_issues", {}).get("value", ""))
        self.academic_issues_type_edit.setText(self.survey_data_to_edit.get("academic_issues_type", {}).get("value", ""))
        self.abnormal_dev_edit.setText(self.survey_data_to_edit.get("abnormal_dev", {}).get("value", ""))
        self.abnormal_dev_what_edit.setText(self.survey_data_to_edit.get("abnormal_dev_what", {}).get("value", ""))
        self.diagnosis_what_edit.setText(self.survey_data_to_edit.get("diagnosis_what", {}).get("value", ""))
        self.breastfeeding_duration_edit.setText(self.survey_data_to_edit.get("breastfeeding_duration", {}).get("value", ""))
        self.breastfeeding_type_combo.setCurrentText(self.survey_data_to_edit.get("breastfeeding_type", {}).get("value", ""))
        self.weaning_combo.setCurrentText(self.survey_data_to_edit.get("weaning", {}).get("value", ""))
        self.weaning_age_edit.setText(self.survey_data_to_edit.get("weaning_age", {}).get("value", ""))
        self.breastfeeding_problems_edit.setText(self.survey_data_to_edit.get("breastfeeding_problems", {}).get("value", ""))
        self.teething_edit.setText(self.survey_data_to_edit.get("teething", {}).get("value", ""))
        self.crawling_edit.setText(self.survey_data_to_edit.get("crawling", {}).get("value", ""))
        self.sitting_edit.setText(self.survey_data_to_edit.get("sitting", {}).get("value", ""))
        self.standing_edit.setText(self.survey_data_to_edit.get("standing", {}).get("value", ""))
        self.walking_start_edit.setText(self.survey_data_to_edit.get("walking_start", {}).get("value", ""))
        self.walking_edit.setText(self.survey_data_to_edit.get("walking", {}).get("value", ""))
        self.diaper_free_edit.setText(self.survey_data_to_edit.get("diaper_free", {}).get("value", ""))
        self.bathroom_request_combo.setCurrentText(self.survey_data_to_edit.get("bathroom_request", {}).get("value", ""))
        self.bathroom_independence_combo.setCurrentText(self.survey_data_to_edit.get("bathroom_independence", {}).get("value", ""))
        

    def save_survey_data(self):
        """Validates and saves the survey data using file_manager."""
        survey_data = self.collect_survey_data()
        
        success, message_or_path = save_survey_data_to_json(self.case_folder_name, survey_data)
        
        if success:
            QMessageBox.information(self, "تم الحفظ", f"تم حفظ بيانات الاستبيان بنجاح")
            self.accept() # Close the dialog if save is successful
        else:
            QMessageBox.critical(self, "خطأ في الحفظ", f"فشل حفظ بيانات الاستبيان\n{message_or_path}")

    def apply_styles(self):
        """stylings for the form if required"""
        self.setStyleSheet("""""")
