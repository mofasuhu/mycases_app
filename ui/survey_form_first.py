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
        
        self.setWindowTitle("استبيان التقييم الأول")
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
        survey_group = QGroupBox("استبيان التقييم الأول")
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

        
        self.school_attendance_label = QLabel("هل يذهب إلى المدرسة/الحضانة؟")
        self.school_attendance_combo = QComboBox()
        self.school_attendance_combo.addItems(["نعم", "لا"])
        self.school_attendance_combo.setFixedWidth(325)
        self.school_attendance_combo.setFixedHeight(40)
        self.school_attendance_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.school_attendance_label, self.school_attendance_combo)
        self.school_year_label = QLabel("العام الدراسي:")
        self.school_year_edit = QLineEdit()
        self.school_year_edit.setFixedWidth(325)
        self.school_year_edit.setFixedHeight(40)
        survey_layout.addRow(self.school_year_label, self.school_year_edit)
        self.school_duration_label = QLabel("المدة التي قضاها:")
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
        
        self.care_center_label = QLabel("هل يذهب إلى مركز/أكاديمية رعاية؟")
        self.care_center_combo = QComboBox()
        self.care_center_combo.addItems(["نعم", "لا"])
        self.care_center_combo.setFixedWidth(325)
        self.care_center_combo.setFixedHeight(40)
        self.care_center_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.care_center_label, self.care_center_combo)
        self.care_duration_label = QLabel("المدة التي قضاها:")
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
        
        self.academic_issues_label = QLabel("هل توجد مشاكل في التحصيل الدراسي؟")
        self.academic_issues_combo = QComboBox()
        self.academic_issues_combo.addItems(["نعم", "لا"])
        self.academic_issues_combo.setFixedWidth(325)
        self.academic_issues_combo.setFixedHeight(40)
        self.academic_issues_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.academic_issues_label, self.academic_issues_combo)
        self.academic_issues_type_label = QLabel("نوعها:")
        self.academic_issues_type_edit = QLineEdit()
        self.academic_issues_type_edit.setFixedWidth(325)
        self.academic_issues_type_edit.setFixedHeight(40)
        survey_layout.addRow(self.academic_issues_type_label, self.academic_issues_type_edit)
        
        self.abnormal_dev_label = QLabel("هل كانت هناك إشارات تدل على نمو غير طبيعي؟")
        self.abnormal_dev_edit = QLineEdit()
        self.abnormal_dev_edit.setFixedWidth(325)
        self.abnormal_dev_edit.setFixedHeight(40)
        survey_layout.addRow(self.abnormal_dev_label, self.abnormal_dev_edit)
        self.abnormal_dev_what_label = QLabel("ما هي؟")
        self.abnormal_dev_what_edit = QLineEdit()
        self.abnormal_dev_what_edit.setFixedWidth(325)
        self.abnormal_dev_what_edit.setFixedHeight(40)
        survey_layout.addRow(self.abnormal_dev_what_label, self.abnormal_dev_what_edit)
        self.diagnosis_what_label = QLabel("ما هو تشخيصه؟")
        self.diagnosis_what_edit = QLineEdit()
        self.diagnosis_what_edit.setFixedWidth(325)
        self.diagnosis_what_edit.setFixedHeight(40)
        survey_layout.addRow(self.diagnosis_what_label, self.diagnosis_what_edit)
        
        self.breastfeeding_duration_label = QLabel("مدة الرضاعة:")
        self.breastfeeding_duration_edit = QLineEdit()
        self.breastfeeding_duration_edit.setFixedWidth(325)
        self.breastfeeding_duration_edit.setFixedHeight(40)
        survey_layout.addRow(self.breastfeeding_duration_label, self.breastfeeding_duration_edit)
        self.breastfeeding_type_label = QLabel("نوع الرضاعة:")
        self.breastfeeding_type_combo = QComboBox()
        self.breastfeeding_type_combo.addItems(["طبيعي", "صناعي"])
        self.breastfeeding_type_combo.setFixedWidth(325)
        self.breastfeeding_type_combo.setFixedHeight(40)
        self.breastfeeding_type_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.breastfeeding_type_label, self.breastfeeding_type_combo)
        self.weaning_label = QLabel("الفطام:")
        self.weaning_combo = QComboBox()
        self.weaning_combo.addItems(["تدريجي", "مفاجئ"])
        self.weaning_combo.setFixedWidth(325)
        self.weaning_combo.setFixedHeight(40)
        self.weaning_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.weaning_label, self.weaning_combo)
        self.weaning_age_label = QLabel("سن الفطام:")
        self.weaning_age_edit = QLineEdit()
        self.weaning_age_edit.setFixedWidth(325)
        self.weaning_age_edit.setFixedHeight(40)
        survey_layout.addRow(self.weaning_age_label, self.weaning_age_edit)
        self.breastfeeding_problems_label = QLabel("هل وُجدت مشاكل بالرضاعة؟")
        self.breastfeeding_problems_edit = QLineEdit()
        self.breastfeeding_problems_edit.setFixedWidth(325)
        self.breastfeeding_problems_edit.setFixedHeight(40)
        survey_layout.addRow(self.breastfeeding_problems_label, self.breastfeeding_problems_edit)
        
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
        self.walking_start_label = QLabel("متى بدأ المشي؟")
        self.walking_start_edit = QLineEdit()
        self.walking_start_edit.setFixedWidth(325)
        self.walking_start_edit.setFixedHeight(40)
        survey_layout.addRow(self.walking_start_label, self.walking_start_edit)
        self.walking_label = QLabel("المشي:")
        self.walking_edit = QLineEdit()
        self.walking_edit.setFixedWidth(325)
        self.walking_edit.setFixedHeight(40)
        survey_layout.addRow(self.walking_label, self.walking_edit)
        
        self.diaper_free_label = QLabel("متى تخلص من الحفاض؟")
        self.diaper_free_edit = QLineEdit()
        self.diaper_free_edit.setFixedWidth(325)
        self.diaper_free_edit.setFixedHeight(40)
        survey_layout.addRow(self.diaper_free_label, self.diaper_free_edit)
        self.bathroom_request_label = QLabel("استخدام الحمام الآن:")
        self.bathroom_request_combo = QComboBox()
        self.bathroom_request_combo.addItems(["يطلب لفظيًا", "بالإشارة", "يحتاج تدريب"])
        self.bathroom_request_combo.setFixedWidth(325)
        self.bathroom_request_combo.setFixedHeight(40)
        self.bathroom_request_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.bathroom_request_label, self.bathroom_request_combo)
        self.bathroom_independence_label = QLabel("يدخل الحمام:")
        self.bathroom_independence_combo = QComboBox()
        self.bathroom_independence_combo.addItems(["بمفرده", "مساعدة جزئية", "مساعدة كلية"])
        self.bathroom_independence_combo.setFixedWidth(325)
        self.bathroom_independence_combo.setFixedHeight(40)
        self.bathroom_independence_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.bathroom_independence_label, self.bathroom_independence_combo)
        
        self.vision_issues_label = QLabel("هل يعاني من أي ضعف في درجة الإبصار؟")
        self.vision_issues_combo = QComboBox()
        self.vision_issues_combo.addItems(["نعم", "لا"])
        self.vision_issues_combo.setFixedWidth(325)
        self.vision_issues_combo.setFixedHeight(40)
        self.vision_issues_combo.wheelEvent = lambda event: event.ignore()
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
        
        self.hearing_issues_label = QLabel("هل يعاني من ضعف سمع؟")
        self.hearing_issues_combo = QComboBox()
        self.hearing_issues_combo.addItems(["نعم", "لا"])
        self.hearing_issues_combo.setFixedWidth(325)
        self.hearing_issues_combo.setFixedHeight(40)
        self.hearing_issues_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.hearing_issues_label, self.hearing_issues_combo)
        self.hearing_type_label = QLabel("نوعه:")
        self.hearing_type_combo = QComboBox()
        self.hearing_type_combo.addItems(["توصيلي", "حسي عصبي", "مركزي", "مختلط"])
        self.hearing_type_combo.setFixedWidth(325)
        self.hearing_type_combo.setFixedHeight(40)
        self.hearing_type_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.hearing_type_label, self.hearing_type_combo)
        self.hearing_severity_label = QLabel("شدته:")
        self.hearing_severity_edit = QLineEdit()
        self.hearing_severity_edit.setFixedWidth(325)
        self.hearing_severity_edit.setFixedHeight(40)
        survey_layout.addRow(self.hearing_severity_label, self.hearing_severity_edit)
        
        self.hearing_aid_label = QLabel("هل يرتدي سماعات؟")
        self.hearing_aid_combo = QComboBox()
        self.hearing_aid_combo.addItems(["نعم", "لا"])
        self.hearing_aid_combo.setFixedWidth(325)
        self.hearing_aid_combo.setFixedHeight(40)
        self.hearing_aid_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.hearing_aid_label, self.hearing_aid_combo)
        self.hearing_aid_type_label = QLabel("نوعها:")
        self.hearing_aid_type_edit = QLineEdit()
        self.hearing_aid_type_edit.setFixedWidth(325)
        self.hearing_aid_type_edit.setFixedHeight(40)
        survey_layout.addRow(self.hearing_aid_type_label, self.hearing_aid_type_edit)
        self.cochlear_implant_label = QLabel("هل لديه زرع قوقعة؟")
        self.cochlear_implant_combo = QComboBox()
        self.cochlear_implant_combo.addItems(["نعم", "لا"])
        self.cochlear_implant_combo.setFixedWidth(325)
        self.cochlear_implant_combo.setFixedHeight(40)
        self.cochlear_implant_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.cochlear_implant_label, self.cochlear_implant_combo)
        self.cochlear_since_label = QLabel("منذ متى؟")
        self.cochlear_since_edit = QLineEdit()
        self.cochlear_since_edit.setFixedWidth(325)
        self.cochlear_since_edit.setFixedHeight(40)
        survey_layout.addRow(self.cochlear_since_label, self.cochlear_since_edit)
        
        self.speech_tone_label = QLabel("هل يتحدث الطفل بنبرة صوت ثابتة؟")
        self.speech_tone_combo = QComboBox()
        self.speech_tone_combo.addItems(["نعم", "لا"])
        self.speech_tone_combo.setFixedWidth(325)
        self.speech_tone_combo.setFixedHeight(40)
        self.speech_tone_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.speech_tone_label, self.speech_tone_combo)
        self.speech_volume_label = QLabel("هل يتحدث الطفل بصوت:")
        self.speech_volume_combo = QComboBox()
        self.speech_volume_combo.addItems(["مرتفع", "منخفض"])
        self.speech_volume_combo.setFixedWidth(325)
        self.speech_volume_combo.setFixedHeight(40)
        self.speech_volume_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.speech_volume_label, self.speech_volume_combo)
        
        self.drooling_label = QLabel("هل يعاني الطفل من سيلان اللعاب؟")
        self.drooling_combo = QComboBox()
        self.drooling_combo.addItems(["نعم", "لا"])
        self.drooling_combo.setFixedWidth(325)
        self.drooling_combo.setFixedHeight(40)
        self.drooling_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.drooling_label, self.drooling_combo)
        self.swallowing_label = QLabel("هل يعاني الطفل من صعوبة بلع؟")
        self.swallowing_combo = QComboBox()
        self.swallowing_combo.addItems(["نعم", "لا"])
        self.swallowing_combo.setFixedWidth(325)
        self.swallowing_combo.setFixedHeight(40)
        self.swallowing_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.swallowing_label, self.swallowing_combo)
        self.breathing_label = QLabel("هل يعاني الطفل من اضطرابات في التنفس؟")
        self.breathing_combo = QComboBox()
        self.breathing_combo.addItems(["نعم", "لا"])
        self.breathing_combo.setFixedWidth(325)
        self.breathing_combo.setFixedHeight(40)
        self.breathing_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.breathing_label, self.breathing_combo)
        self.breathing_type_label = QLabel("نوع اضطراب التنفس:")
        self.breathing_type_combo = QComboBox()
        self.breathing_type_combo.addItems(["شهيق", "زفير", "نفخ", "شفط"])
        self.breathing_type_combo.setFixedWidth(325)
        self.breathing_type_combo.setFixedHeight(40)
        self.breathing_type_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.breathing_type_label, self.breathing_type_combo)
        
        self.iq_test_label = QLabel("هل تم إجراء اختبار ذكاء (IQ)؟")
        self.iq_test_combo = QComboBox()
        self.iq_test_combo.addItems(["نعم", "لا"])
        self.iq_test_combo.setFixedWidth(325)
        self.iq_test_combo.setFixedHeight(40)
        self.iq_test_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.iq_test_label, self.iq_test_combo)
        self.iq_score_label = QLabel("الدرجة:")
        self.iq_score_edit = QLineEdit()
        self.iq_score_edit.setFixedWidth(325)
        self.iq_score_edit.setFixedHeight(40)
        survey_layout.addRow(self.iq_score_label, self.iq_score_edit)
        self.hearing_test_label = QLabel("هل تم إجراء مقياس سمع؟")
        self.hearing_test_combo = QComboBox()
        self.hearing_test_combo.addItems(["نعم", "لا"])
        self.hearing_test_combo.setFixedWidth(325)
        self.hearing_test_combo.setFixedHeight(40)
        self.hearing_test_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.hearing_test_label, self.hearing_test_combo)
        self.hearing_score_label = QLabel("الدرجة:")
        self.hearing_score_edit = QLineEdit()
        self.hearing_score_edit.setFixedWidth(325)
        self.hearing_score_edit.setFixedHeight(40)
        survey_layout.addRow(self.hearing_score_label, self.hearing_score_edit)
        self.ear_pressure_label = QLabel("هل تم إجراء اختبار ضغط الأذن؟")
        self.ear_pressure_combo = QComboBox()
        self.ear_pressure_combo.addItems(["نعم", "لا"])
        self.ear_pressure_combo.setFixedWidth(325)
        self.ear_pressure_combo.setFixedHeight(40)
        self.ear_pressure_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.ear_pressure_label, self.ear_pressure_combo)
        self.language_test_label = QLabel("هل تم إجراء اختبار لغة؟")
        self.language_test_combo = QComboBox()
        self.language_test_combo.addItems(["نعم", "لا"])
        self.language_test_combo.setFixedWidth(325)
        self.language_test_combo.setFixedHeight(40)
        self.language_test_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.language_test_label, self.language_test_combo)
        self.speech_test_label = QLabel("هل تم إجراء اختبار نطق؟")
        self.speech_test_combo = QComboBox()
        self.speech_test_combo.addItems(["نعم", "لا"])
        self.speech_test_combo.setFixedWidth(325)
        self.speech_test_combo.setFixedHeight(40)
        self.speech_test_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.speech_test_label, self.speech_test_combo)
        
        self.case_acceptance_label = QLabel("مدى تقبل الحالة للتأهيل:")
        self.case_acceptance_edit = QLineEdit()
        self.case_acceptance_edit.setFixedWidth(325)
        self.case_acceptance_edit.setFixedHeight(40)
        survey_layout.addRow(self.case_acceptance_label, self.case_acceptance_edit)
        self.family_acceptance_label = QLabel("مدى تقبل الأسرة للمشكلة:")
        self.family_acceptance_edit = QLineEdit()
        self.family_acceptance_edit.setFixedWidth(325)
        self.family_acceptance_edit.setFixedHeight(40)
        survey_layout.addRow(self.family_acceptance_label, self.family_acceptance_edit)
        
        self.speech_therapy_label = QLabel("هل يتلقى جلسات تخاطب؟")
        self.speech_therapy_combo = QComboBox()
        self.speech_therapy_combo.addItems(["نعم", "لا"])
        self.speech_therapy_combo.setFixedWidth(325)
        self.speech_therapy_combo.setFixedHeight(40)
        self.speech_therapy_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.speech_therapy_label, self.speech_therapy_combo)
        self.speech_therapy_progress_label = QLabel("مدى التقدم:")
        self.speech_therapy_progress_edit = QLineEdit()
        self.speech_therapy_progress_edit.setFixedWidth(325)
        self.speech_therapy_progress_edit.setFixedHeight(40)
        survey_layout.addRow(self.speech_therapy_progress_label, self.speech_therapy_progress_edit)
        self.physical_therapy_label = QLabel("هل يتلقى علاج طبيعي؟")
        self.physical_therapy_combo = QComboBox()
        self.physical_therapy_combo.addItems(["نعم", "لا"])
        self.physical_therapy_combo.setFixedWidth(325)
        self.physical_therapy_combo.setFixedHeight(40)
        self.physical_therapy_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.physical_therapy_label, self.physical_therapy_combo)
        self.physical_therapy_progress_label = QLabel("مدى التقدم:")
        self.physical_therapy_progress_edit = QLineEdit()
        self.physical_therapy_progress_edit.setFixedWidth(325)
        self.physical_therapy_progress_edit.setFixedHeight(40)
        survey_layout.addRow(self.physical_therapy_progress_label, self.physical_therapy_progress_edit)
        self.computer_therapy_label = QLabel("هل يتعامل مع الكمبيوتر؟")
        self.computer_therapy_combo = QComboBox()
        self.computer_therapy_combo.addItems(["نعم", "لا"])
        self.computer_therapy_combo.setFixedWidth(325)
        self.computer_therapy_combo.setFixedHeight(40)
        self.computer_therapy_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.computer_therapy_label, self.computer_therapy_combo)
        self.computer_therapy_progress_label = QLabel("مدى التقدم:")
        self.computer_therapy_progress_edit = QLineEdit()
        self.computer_therapy_progress_edit.setFixedWidth(325)
        self.computer_therapy_progress_edit.setFixedHeight(40)
        survey_layout.addRow(self.computer_therapy_progress_label, self.computer_therapy_progress_edit)
        self.skills_therapy_label = QLabel("هل يتلقى تنمية مهارات؟")
        self.skills_therapy_combo = QComboBox()
        self.skills_therapy_combo.addItems(["نعم", "لا"])
        self.skills_therapy_combo.setFixedWidth(325)
        self.skills_therapy_combo.setFixedHeight(40)
        self.skills_therapy_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.skills_therapy_label, self.skills_therapy_combo)
        self.skills_therapy_progress_label = QLabel("مدى التقدم:")
        self.skills_therapy_progress_edit = QLineEdit()
        self.skills_therapy_progress_edit.setFixedWidth(325)
        self.skills_therapy_progress_edit.setFixedHeight(40)
        survey_layout.addRow(self.skills_therapy_progress_label, self.skills_therapy_progress_edit)
        
        self.favorite_food_label = QLabel("ما أكثر المأكولات أو المشروبات التي يفضلها؟")
        self.favorite_food_edit = QLineEdit()
        self.favorite_food_edit.setFixedWidth(325)
        self.favorite_food_edit.setFixedHeight(40)
        survey_layout.addRow(self.favorite_food_label, self.favorite_food_edit)
        self.favorite_games_label = QLabel("ما أكثر الألعاب التي يحبها؟")
        self.favorite_games_edit = QLineEdit()
        self.favorite_games_edit.setFixedWidth(325)
        self.favorite_games_edit.setFixedHeight(40)
        survey_layout.addRow(self.favorite_games_label, self.favorite_games_edit)
        self.other_likes_label = QLabel("أشياء أخرى يحبها:")
        self.other_likes_edit = QLineEdit()
        self.other_likes_edit.setFixedWidth(325)
        self.other_likes_edit.setFixedHeight(40)
        survey_layout.addRow(self.other_likes_label, self.other_likes_edit)
        self.dislikes_label = QLabel("أشياء ينزعج منها:")
        self.dislikes_edit = QLineEdit()
        self.dislikes_edit.setFixedWidth(325)
        self.dislikes_edit.setFixedHeight(40)
        survey_layout.addRow(self.dislikes_label, self.dislikes_edit)
        
        self.living_with_label = QLabel("مع من يعيش الطفل؟")
        self.living_with_edit = QLineEdit()
        self.living_with_edit.setFixedWidth(325)
        self.living_with_edit.setFixedHeight(40)
        survey_layout.addRow(self.living_with_label, self.living_with_edit)
        self.attached_people_label = QLabel("هل يوجد أشخاص مرتبط بهم (من الأسرة أو المحيط) ويؤثرون فيه؟")
        self.attached_people_edit = QLineEdit()
        self.attached_people_edit.setFixedWidth(325)
        self.attached_people_edit.setFixedHeight(40)
        survey_layout.addRow(self.attached_people_label, self.attached_people_edit)
        self.caregiver_label = QLabel("من هو القائم برعاية الطفل؟")
        self.caregiver_edit = QLineEdit()
        self.caregiver_edit.setFixedWidth(325)
        self.caregiver_edit.setFixedHeight(40)
        survey_layout.addRow(self.caregiver_label, self.caregiver_edit)
        self.economic_status_label = QLabel("الوضع الاقتصادي:")
        self.economic_status_edit = QLineEdit()
        self.economic_status_edit.setFixedWidth(325)
        self.economic_status_edit.setFixedHeight(40)
        survey_layout.addRow(self.economic_status_label, self.economic_status_edit)
        self.cultural_status_label = QLabel("الوضع الثقافي:")
        self.cultural_status_edit = QLineEdit()
        self.cultural_status_edit.setFixedWidth(325)
        self.cultural_status_edit.setFixedHeight(40)
        survey_layout.addRow(self.cultural_status_label, self.cultural_status_edit)
        self.social_status_label = QLabel("الوضع الاجتماعي:")
        self.social_status_edit = QLineEdit()
        self.social_status_edit.setFixedWidth(325)
        self.social_status_edit.setFixedHeight(40)
        survey_layout.addRow(self.social_status_label, self.social_status_edit)
        self.family_relationship_label = QLabel("طبيعة العلاقة الأسرية:")
        self.family_relationship_edit = QLineEdit()
        self.family_relationship_edit.setFixedWidth(325)
        self.family_relationship_edit.setFixedHeight(40)
        survey_layout.addRow(self.family_relationship_label, self.family_relationship_edit)
        self.family_acceptance_rehab_label = QLabel("مدى تقبل الأسرة للاضطراب واستعدادها للمشاركة في التأهيل:")
        self.family_acceptance_rehab_edit = QLineEdit()
        self.family_acceptance_rehab_edit.setFixedWidth(325)
        self.family_acceptance_rehab_edit.setFixedHeight(40)
        survey_layout.addRow(self.family_acceptance_rehab_label, self.family_acceptance_rehab_edit)
        
        self.mother_health_pregnancy_label = QLabel("صحة الأم أثناء الحمل كانت:")
        self.mother_health_pregnancy_combo = QComboBox()
        self.mother_health_pregnancy_combo.addItems(["مستقرة", "غير مستقرة"])
        self.mother_health_pregnancy_combo.setFixedWidth(325)
        self.mother_health_pregnancy_combo.setFixedHeight(40)
        self.mother_health_pregnancy_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.mother_health_pregnancy_label, self.mother_health_pregnancy_combo)
        self.birth_type_label = QLabel("نوع الولادة:")
        self.birth_type_combo = QComboBox()
        self.birth_type_combo.addItems(["طبيعية", "قيصرية"])
        self.birth_type_combo.setFixedWidth(325)
        self.birth_type_combo.setFixedHeight(40)
        self.birth_type_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.birth_type_label, self.birth_type_combo)
        self.birth_weight_label = QLabel("وزن الطفل عند الولادة:")
        self.birth_weight_edit = QLineEdit()
        self.birth_weight_edit.setFixedWidth(325)
        self.birth_weight_edit.setFixedHeight(40)
        survey_layout.addRow(self.birth_weight_label, self.birth_weight_edit)
        self.birth_cry_label = QLabel("هل صرخ الطفل صرخة الميلاد؟")
        self.birth_cry_combo = QComboBox()
        self.birth_cry_combo.addItems(["نعم", "لا"])
        self.birth_cry_combo.setFixedWidth(325)
        self.birth_cry_combo.setFixedHeight(40)
        self.birth_cry_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.birth_cry_label, self.birth_cry_combo)
        self.head_size_label = QLabel("حجم رأس الطفل عند الولادة:")
        self.head_size_combo = QComboBox()
        self.head_size_combo.addItems(["طبيعي", "غير طبيعي"])
        self.head_size_combo.setFixedWidth(325)
        self.head_size_combo.setFixedHeight(40)
        self.head_size_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.head_size_label, self.head_size_combo)
        self.head_size_value_label = QLabel("كان:")
        self.head_size_value_edit = QLineEdit()
        self.head_size_value_edit.setFixedWidth(325)
        self.head_size_value_edit.setFixedHeight(40)
        survey_layout.addRow(self.head_size_value_label, self.head_size_value_edit)
        self.birth_defects_label = QLabel("هل كانت هناك عيوب خلقية بعد الولادة؟")
        self.birth_defects_combo = QComboBox()
        self.birth_defects_combo.addItems(["نعم", "لا"])
        self.birth_defects_combo.setFixedWidth(325)
        self.birth_defects_combo.setFixedHeight(40)
        self.birth_defects_combo.wheelEvent = lambda event: event.ignore()
        survey_layout.addRow(self.birth_defects_label, self.birth_defects_combo)
        self.birth_defects_what_label = QLabel("ما هي؟")
        self.birth_defects_what_edit = QLineEdit()
        self.birth_defects_what_edit.setFixedWidth(325)
        self.birth_defects_what_edit.setFixedHeight(40)
        survey_layout.addRow(self.birth_defects_what_label, self.birth_defects_what_edit)
        survey_group.setLayout(survey_layout)
        self.main_layout.addWidget(survey_group)

    def collect_survey_data(self):
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
            key = label_widget.text().replace(':', '').replace('؟', '').strip()
            value = input_widget.currentText() if use_current_text else input_widget.text().strip()
            return { "ar_key": key, "value": value }

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
        if not self.survey_data_to_edit:
            return
        
        survey_date_str = self.survey_data_to_edit.get("survey_date", "")
        survey_date = QDate.fromString(survey_date_str, "yyyy-MM-dd")
        if survey_date_str:
            self.survey_date_edit.setDate(survey_date)
            self.day_edit.setText("{:02}".format(survey_date.day()))
            self.month_edit.setText("{:02}".format(survey_date.month()))
            self.year_edit.setText("{:02}".format(survey_date.year()))
        
        # Helper function to set widget values from loaded data
        def set_widget_value(widget, key):
            value = self.survey_data_to_edit.get(key, {}).get("value", "")
            if isinstance(widget, QComboBox):
                widget.setCurrentText(value)
            elif isinstance(widget, QLineEdit):
                widget.setText(value)

        # Set all fields
        set_widget_value(self.school_attendance_combo, "school_attendance")
        set_widget_value(self.school_year_edit, "school_year")
        set_widget_value(self.school_duration_edit, "school_duration")
        set_widget_value(self.school_type_edit, "school_type")
        set_widget_value(self.school_discontinue_edit, "school_discontinue")
        set_widget_value(self.care_center_combo, "care_center")
        set_widget_value(self.care_duration_edit, "care_duration")
        set_widget_value(self.care_type_edit, "care_type")
        set_widget_value(self.care_discontinue_edit, "care_discontinue")
        set_widget_value(self.academic_issues_combo, "academic_issues")
        set_widget_value(self.academic_issues_type_edit, "academic_issues_type")
        set_widget_value(self.abnormal_dev_edit, "abnormal_dev")
        set_widget_value(self.abnormal_dev_what_edit, "abnormal_dev_what")
        set_widget_value(self.diagnosis_what_edit, "diagnosis_what")
        set_widget_value(self.breastfeeding_duration_edit, "breastfeeding_duration")
        set_widget_value(self.breastfeeding_type_combo, "breastfeeding_type")
        set_widget_value(self.weaning_combo, "weaning")
        set_widget_value(self.weaning_age_edit, "weaning_age")
        set_widget_value(self.breastfeeding_problems_edit, "breastfeeding_problems")
        set_widget_value(self.teething_edit, "teething")
        set_widget_value(self.crawling_edit, "crawling")
        set_widget_value(self.sitting_edit, "sitting")
        set_widget_value(self.standing_edit, "standing")
        set_widget_value(self.walking_start_edit, "walking_start")
        set_widget_value(self.walking_edit, "walking")
        set_widget_value(self.diaper_free_edit, "diaper_free")
        set_widget_value(self.bathroom_request_combo, "bathroom_request")
        set_widget_value(self.bathroom_independence_combo, "bathroom_independence")
        set_widget_value(self.vision_issues_combo, "vision_issues")
        set_widget_value(self.vision_type_edit, "vision_type")
        set_widget_value(self.vision_severity_edit, "vision_severity")
        set_widget_value(self.hearing_issues_combo, "hearing_issues")
        set_widget_value(self.hearing_type_combo, "hearing_type")
        set_widget_value(self.hearing_severity_edit, "hearing_severity")
        set_widget_value(self.hearing_aid_combo, "hearing_aid")
        set_widget_value(self.hearing_aid_type_edit, "hearing_aid_type")
        set_widget_value(self.cochlear_implant_combo, "cochlear_implant")
        set_widget_value(self.cochlear_since_edit, "cochlear_since")
        set_widget_value(self.speech_tone_combo, "speech_tone")
        set_widget_value(self.speech_volume_combo, "speech_volume")
        set_widget_value(self.drooling_combo, "drooling")
        set_widget_value(self.swallowing_combo, "swallowing")
        set_widget_value(self.breathing_combo, "breathing")
        set_widget_value(self.breathing_type_combo, "breathing_type")
        set_widget_value(self.iq_test_combo, "iq_test")
        set_widget_value(self.iq_score_edit, "iq_score")
        set_widget_value(self.hearing_test_combo, "hearing_test")
        set_widget_value(self.hearing_score_edit, "hearing_score")
        set_widget_value(self.ear_pressure_combo, "ear_pressure")
        set_widget_value(self.language_test_combo, "language_test")
        set_widget_value(self.speech_test_combo, "speech_test")
        set_widget_value(self.case_acceptance_edit, "case_acceptance")
        set_widget_value(self.family_acceptance_edit, "family_acceptance")
        set_widget_value(self.speech_therapy_combo, "speech_therapy")
        set_widget_value(self.speech_therapy_progress_edit, "speech_therapy_progress")
        set_widget_value(self.physical_therapy_combo, "physical_therapy")
        set_widget_value(self.physical_therapy_progress_edit, "physical_therapy_progress")
        set_widget_value(self.computer_therapy_combo, "computer_therapy")
        set_widget_value(self.computer_therapy_progress_edit, "computer_therapy_progress")
        set_widget_value(self.skills_therapy_combo, "skills_therapy")
        set_widget_value(self.skills_therapy_progress_edit, "skills_therapy_progress")
        set_widget_value(self.favorite_food_edit, "favorite_food")
        set_widget_value(self.favorite_games_edit, "favorite_games")
        set_widget_value(self.other_likes_edit, "other_likes")
        set_widget_value(self.dislikes_edit, "dislikes")
        set_widget_value(self.living_with_edit, "living_with")
        set_widget_value(self.attached_people_edit, "attached_people")
        set_widget_value(self.caregiver_edit, "caregiver")
        set_widget_value(self.economic_status_edit, "economic_status")
        set_widget_value(self.cultural_status_edit, "cultural_status")
        set_widget_value(self.social_status_edit, "social_status")
        set_widget_value(self.family_relationship_edit, "family_relationship")
        set_widget_value(self.family_acceptance_rehab_edit, "family_acceptance_rehab")
        set_widget_value(self.mother_health_pregnancy_combo, "mother_health_pregnancy")
        set_widget_value(self.birth_type_combo, "birth_type")
        set_widget_value(self.birth_weight_edit, "birth_weight")
        set_widget_value(self.birth_cry_combo, "birth_cry")
        set_widget_value(self.head_size_combo, "head_size")
        set_widget_value(self.head_size_value_edit, "head_size_value")
        set_widget_value(self.birth_defects_combo, "birth_defects")
        set_widget_value(self.birth_defects_what_edit, "birth_defects_what")

    def save_survey_data(self):
        survey_data = self.collect_survey_data()
        success, message_or_path = save_survey_data_to_json(self.case_folder_name, survey_data)
        if success:
            QMessageBox.information(self, "تم الحفظ", "تم حفظ بيانات الاستبيان بنجاح.")
            self.accept() 
        else:
            QMessageBox.critical(self, "خطأ في الحفظ", f"فشل حفظ بيانات الاستبيان:\n{message_or_path}")

    def apply_styles(self):
        self.setStyleSheet("""""")

