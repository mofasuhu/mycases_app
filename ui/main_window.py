from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QWidget, 
    QListWidget, QMessageBox, QHBoxLayout, QLabel, QDialog,
    QLineEdit, QInputDialog, QFrame
)

from PyQt5.QtGui import QIcon

from PyQt5.QtCore import Qt, QSize
import shutil

from .case_form import CaseForm
from .case_viewer import CaseViewer
from utils.file_manager import get_all_case_folders, load_case_data_from_json, get_data_directory
from utils.general import resource_path
import os
from datetime import datetime, date



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Window Properties ---
        self.setWindowTitle("إدارة الحالات")
        self.setGeometry(250, 50, 800, 600)
        self.showMaximized()

        # --- Central Widget and Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- Header for Buttons ---
        self.button_header_layout = QHBoxLayout()

        # --- "Create New Case" Button ---
        self.btn_create_case = QPushButton()
        self.btn_create_case.setIcon(QIcon(resource_path("icons/create.png")))
        self.btn_create_case.setIconSize(QSize(32, 32))
        self.btn_create_case.setToolTip("إنشاء حالة جديدة")


        self.btn_create_case.clicked.connect(self.open_new_case_form)
        self.button_header_layout.addWidget(self.btn_create_case)
        
        self.button_header_layout.addStretch(1)
        self.main_layout.addLayout(self.button_header_layout)

        # # --- Search/Filter Section ---
        # self.search_layout = QHBoxLayout()
        # self.search_label = QLabel("بحث باسم الحالة:")
        # self.search_layout.addWidget(self.search_label)
        
        # self.search_input = QLineEdit()
        # self.search_input.setPlaceholderText("أَدخِل اسم الحالة أو جزء منه...")
        # self.search_input.setFixedWidth(300)
        # self.search_input.textChanged.connect(self.filter_case_list)
        # self.search_input.setClearButtonEnabled(True)
        # self.search_layout.addWidget(self.search_input)
        
        # self.search_layout.addStretch(1)
        # self.main_layout.addLayout(self.search_layout)



        # self.age_search_layout = QHBoxLayout()
        # self.age_search_label = QLabel("بحث بالعمر:")
        # self.age_search_layout.addWidget(self.age_search_label)
        
        # self.age_search_input = QLineEdit()
        # self.age_search_input.setPlaceholderText("أَدخِل العمر بالسنين فقط...")
        # self.age_search_input.setFixedWidth(300)
        # self.age_search_input.textChanged.connect(self.age_filter_case_list)
        # self.age_search_input.setClearButtonEnabled(True)
        # self.age_search_layout.addWidget(self.age_search_input)
        
        # self.age_search_layout.addStretch(1)
        # self.main_layout.addLayout(self.age_search_layout)



        # self.diagnosis_search_layout = QHBoxLayout()
        # self.diagnosis_search_label = QLabel("بحث بالتشخيص:")
        # self.diagnosis_search_layout.addWidget(self.diagnosis_search_label)
        
        # self.diagnosis_search_input = QLineEdit()
        # self.diagnosis_search_input.setPlaceholderText("أَدخِل التشخيص...")
        # self.diagnosis_search_input.setFixedWidth(300)
        # self.diagnosis_search_input.textChanged.connect(self.diagnosis_filter_case_list)
        # self.diagnosis_search_input.setClearButtonEnabled(True)
        # self.diagnosis_search_layout.addWidget(self.diagnosis_search_input)
        
        # self.diagnosis_search_layout.addStretch(1)
        # self.main_layout.addLayout(self.diagnosis_search_layout)


        # In MainWindow.__init__, replace the entire search section with this block.

        # --- Search/Filter Section ---
        self.search_layout = QHBoxLayout()
        self.search_label = QLabel("بحث باسم الحالة:")
        self.search_layout.addWidget(self.search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("أَدخِل اسم الحالة أو جزء منه...")
        self.search_input.setFixedWidth(300)
        # Connect to the single, combined filter function
        self.search_input.textChanged.connect(self.apply_combined_filter)
        self.search_input.setClearButtonEnabled(True)
        self.search_layout.addWidget(self.search_input)

        self.search_layout.addStretch(1)
        self.main_layout.addLayout(self.search_layout)


        self.age_search_layout = QHBoxLayout()
        self.age_search_label = QLabel("بحث بالعمر (سنين):")
        self.age_search_layout.addWidget(self.age_search_label)

        self.age_search_input = QLineEdit()
        self.age_search_input.setPlaceholderText("أَدخِل العمر بالسنين فقط...")
        self.age_search_input.setFixedWidth(300)
        # Connect to the same combined filter function
        self.age_search_input.textChanged.connect(self.apply_combined_filter)
        self.age_search_input.setClearButtonEnabled(True)
        self.age_search_layout.addWidget(self.age_search_input)

        self.age_search_layout.addStretch(1)
        self.main_layout.addLayout(self.age_search_layout)


        self.diagnosis_search_layout = QHBoxLayout()
        self.diagnosis_search_label = QLabel("بحث بالتشخيص:")
        self.diagnosis_search_layout.addWidget(self.diagnosis_search_label)

        self.diagnosis_search_input = QLineEdit()
        self.diagnosis_search_input.setPlaceholderText("أَدخِل التشخيص أو جزء منه...")
        self.diagnosis_search_input.setFixedWidth(300)
        # Connect to the same combined filter function
        self.diagnosis_search_input.textChanged.connect(self.apply_combined_filter)
        self.diagnosis_search_input.setClearButtonEnabled(True)
        self.diagnosis_search_layout.addWidget(self.diagnosis_search_input)

        self.diagnosis_search_layout.addStretch(1)
        self.main_layout.addLayout(self.diagnosis_search_layout)


        
        
        # Add a separator line
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(self.separator)

        # --- Case List Area ---
        self.case_list_label = QLabel("الحالات المسجلة:")
        self.main_layout.addWidget(self.case_list_label)

        self.case_list_widget = QListWidget()
        self.case_list_widget.itemDoubleClicked.connect(self.open_selected_case)
        self.main_layout.addWidget(self.case_list_widget)
        
        # --- Buttons for Case List ---
        self.case_buttons_layout = QHBoxLayout()
        self.btn_open_case = QPushButton()
        self.btn_open_case.setIcon(QIcon(resource_path("icons/open.png")))
        self.btn_open_case.setIconSize(QSize(32, 32))
        self.btn_open_case.setToolTip("فتح الحالة المحددة")
        self.btn_open_case.clicked.connect(self.open_selected_case)
        self.case_buttons_layout.addWidget(self.btn_open_case)

        self.edit_button = QPushButton()
        self.edit_button.setIcon(QIcon(resource_path("icons/edit.png")))
        self.edit_button.setIconSize(QSize(32, 32))
        self.edit_button.setToolTip("تعديل بيانات الحالة")        
        self.edit_button.clicked.connect(self.edit_selected_case)
        self.case_buttons_layout.addWidget(self.edit_button)        

        self.btn_refresh_list = QPushButton()
        self.btn_refresh_list.setIcon(QIcon(resource_path("icons/refresh.png")))
        self.btn_refresh_list.setIconSize(QSize(32, 32))
        self.btn_refresh_list.setToolTip("تحديث القائمة")        
        self.btn_refresh_list.clicked.connect(self.populate_case_list)
        self.case_buttons_layout.addWidget(self.btn_refresh_list)
        
        # Add remove case button
        self.btn_remove_case = QPushButton()
        self.btn_remove_case.setIcon(QIcon(resource_path("icons/trash.png")))
        self.btn_remove_case.setIconSize(QSize(32, 32))
        self.btn_remove_case.setToolTip("حذف الحالة")   
        self.btn_remove_case.clicked.connect(self.remove_selected_case)
        self.case_buttons_layout.addWidget(self.btn_remove_case)
        

        self.case_buttons_layout.addStretch()
        self.main_layout.addLayout(self.case_buttons_layout)


        # Store all cases data for filtering
        self.all_cases_data = []

        # --- Styling if required ---
        self.setStyleSheet("""""")

        # --- Initial Population of Case List ---
        self.populate_case_list()

    def open_new_case_form(self):
        """Opens the CaseForm dialog for creating a new case."""
        # Pass self as parent, so the dialog is modal to the main window
        self.case_form_dialog = CaseForm(parent=self)
        # exec_() makes the dialog blocking
        result = self.case_form_dialog.exec_()
        if result == QDialog.Accepted:
            print("New case form accepted. Refreshing list.")
            self.populate_case_list() # Refresh the list if a new case was saved
        else:
            print("New case form cancelled or closed.")

    # def populate_case_list(self):
    #     """Clears and repopulates the list of saved cases from the data directory."""
    #     self.case_list_widget.clear()
    #     self.all_cases_data = []  # Clear the stored cases data
        
    #     case_folders = get_all_case_folders()
    #     if not case_folders:
    #         self.case_list_widget.addItem("لا توجد حالات مسجلة حاليًا.")
    #         self.case_list_widget.setEnabled(False)
    #         self.btn_open_case.setEnabled(False)
    #         self.btn_remove_case.setEnabled(False)
    #     else:
    #         self.case_list_widget.setEnabled(True)
    #         self.btn_open_case.setEnabled(True)
    #         self.btn_remove_case.setEnabled(True)
            
    #         for folder_name in case_folders:
    #             # Try to get a more user-friendly name from the case.json if possible
    #             case_data = load_case_data_from_json(folder_name)
    #             display_name = folder_name # Default to folder name
                
    #             if case_data and ("child_name" in case_data) and (case_data["child_name"]["value"]):
    #                 # Extract child name and DOB for a more descriptive list item
    #                 child_name_display = case_data["child_name"]["value"]
    #                 diagnosis_display = case_data["diagnosis"]["value"]
    #                 age_display = case_data["age"]["value"]
    #                 age_years_display = case_data["age"]["value"].split()[0]
    #                 dob_display = case_data.get("dob", {}).get("value", "")
    #                 case_id_display = case_data.get("case_id", "")
    #                 display_name = f"{child_name_display} - {diagnosis_display} - {age_display} - (id:{case_id_display})"
                    
    #                 # Store case data for filtering
    #                 self.all_cases_data.append({
    #                     'folder_name': folder_name,
    #                     'child_name': child_name_display,
    #                     'dob': dob_display,
    #                     'case_id': case_id_display,
    #                     'diagnosis_display': diagnosis_display,
    #                     'age_display': age_display,
    #                     'age_years_display': age_years_display,
    #                     'display_name': display_name
    #                 })
                
    #             self.case_list_widget.addItem(display_name)
    #             # Store the actual folder name with the item for later retrieval
    #             self.case_list_widget.item(self.case_list_widget.count() - 1).setData(Qt.UserRole, folder_name)
        
    #     # Reset the search field
    #     self.search_input.clear()



    def populate_case_list(self):
        """
        Clears and repopulates the list of saved cases from the data directory.
        It calculates the age dynamically and prepares data for filtering.
        """
        self.case_list_widget.clear()
        self.all_cases_data = []  # Clear the master list of case data

        case_folders = get_all_case_folders()
        if not case_folders:
            self.case_list_widget.addItem("لا توجد حالات مسجلة حاليًا.")
            self.case_list_widget.setEnabled(False)
            self.btn_open_case.setEnabled(False)
            self.btn_remove_case.setEnabled(False)
            return # Exit the function early
        
        # If we have cases, enable the buttons
        self.case_list_widget.setEnabled(True)
        self.btn_open_case.setEnabled(True)
        self.btn_remove_case.setEnabled(True)
        
        for folder_name in case_folders:
            case_data = load_case_data_from_json(folder_name)
            
            if not case_data:
                # If case.json is missing or corrupt, add a placeholder and skip
                self.case_list_widget.addItem(f"خطأ في تحميل بيانات المجلد: {folder_name}")
                continue

            # Safely get all data with fallbacks for missing keys
            child_name = case_data.get("child_name", {}).get("value", "اسم غير متوفر")
            diagnosis = case_data.get("diagnosis", {}).get("value", "تشخيص غير متوفر")
            dob_str = case_data.get("dob", {}).get("value", "")
            case_id = case_data.get("case_id", "N/A")

            # --- Dynamically calculate age in years ---
            age_in_years = "N/A"
            if dob_str:
                try:
                    # Convert the date string to a date object
                    dob_date = datetime.strptime(dob_str, "%Y-%m-%d").date()
                    today = date.today()
                    # Calculate age
                    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                    age_in_years = str(age)
                except (ValueError, TypeError):
                    # Handle cases where dob_str is empty or has an invalid format
                    age_in_years = "N/A"
            
            # Create the string that will be displayed in the list
            display_name = f"{child_name} - (العمر: {age_in_years}، التشخيص: {diagnosis})"

            # Store all necessary data for filtering and display in our master list
            self.all_cases_data.append({
                'folder_name': folder_name,
                'child_name': child_name,
                'diagnosis': diagnosis,
                'age_in_years': age_in_years,
                'display_name': display_name
            })

        # After processing all folders, apply the combined filter.
        # This will populate the list widget with the correct items.
        self.apply_combined_filter()



    def filter_case_list(self):
        """Filters the case list based on the search input."""
        search_text = self.search_input.text().strip()
        
        # If search is empty, show all cases
        if not search_text:
            self.populate_case_list()
            return
        
        # Clear the current list
        self.case_list_widget.clear()
        
        # Filter cases based on search text
        filtered_cases = []
        for case in self.all_cases_data:
            if search_text.lower() in case['child_name'].lower():
                filtered_cases.append(case)
        
        if not filtered_cases:
            self.case_list_widget.addItem("لا توجد نتائج مطابقة للبحث.")
            self.case_list_widget.setEnabled(False)
            self.btn_open_case.setEnabled(False)
            self.btn_remove_case.setEnabled(False)
        else:
            self.case_list_widget.setEnabled(True)
            self.btn_open_case.setEnabled(True)
            self.btn_remove_case.setEnabled(True)
            
            for case in filtered_cases:
                self.case_list_widget.addItem(case['display_name'])
                # Store the folder name with the item
                self.case_list_widget.item(self.case_list_widget.count() - 1).setData(Qt.UserRole, case['folder_name'])


    def age_filter_case_list(self):
        """Filters the case list based on the search input."""
        search_text = self.age_search_input.text().strip()
        
        # If search is empty, show all cases
        if not search_text:
            self.populate_case_list()
            return
        
        # Clear the current list
        self.case_list_widget.clear()
        
        # Filter cases based on search text
        filtered_cases = []
        for case in self.all_cases_data:
            print(case['age_years_display'])
            if search_text.lower() in case['age_years_display'].lower():
                filtered_cases.append(case)
        
        if not filtered_cases:
            self.case_list_widget.addItem("لا توجد نتائج مطابقة للبحث.")
            self.case_list_widget.setEnabled(False)
            self.btn_open_case.setEnabled(False)
            self.btn_remove_case.setEnabled(False)
        else:
            self.case_list_widget.setEnabled(True)
            self.btn_open_case.setEnabled(True)
            self.btn_remove_case.setEnabled(True)
            
            for case in filtered_cases:
                self.case_list_widget.addItem(case['display_name'])
                # Store the folder name with the item
                self.case_list_widget.item(self.case_list_widget.count() - 1).setData(Qt.UserRole, case['folder_name'])

    def diagnosis_filter_case_list(self):
        """Filters the case list based on the search input."""
        search_text = self.diagnosis_search_input.text().strip()
        
        # If search is empty, show all cases
        if not search_text:
            self.populate_case_list()
            return
        
        # Clear the current list
        self.case_list_widget.clear()
        
        # Filter cases based on search text
        filtered_cases = []
        for case in self.all_cases_data:
            if search_text.lower() in case['diagnosis_display'].lower():
                filtered_cases.append(case)
        
        if not filtered_cases:
            self.case_list_widget.addItem("لا توجد نتائج مطابقة للبحث.")
            self.case_list_widget.setEnabled(False)
            self.btn_open_case.setEnabled(False)
            self.btn_remove_case.setEnabled(False)
        else:
            self.case_list_widget.setEnabled(True)
            self.btn_open_case.setEnabled(True)
            self.btn_remove_case.setEnabled(True)
            
            for case in filtered_cases:
                self.case_list_widget.addItem(case['display_name'])
                # Store the folder name with the item
                self.case_list_widget.item(self.case_list_widget.count() - 1).setData(Qt.UserRole, case['folder_name'])



    def apply_combined_filter(self):
        """
        Filters the case list based on the current text in all search fields.
        """
        # 1. Get the search text from all three input fields
        name_search_text = self.search_input.text().strip().lower()
        age_search_text = self.age_search_input.text().strip()
        diagnosis_search_text = self.diagnosis_search_input.text().strip().lower()

        # 2. Start with the full list of cases
        # We create a copy to avoid modifying the original list
        filtered_cases = list(self.all_cases_data)

        # 3. Apply each filter sequentially if its search box is not empty
        if name_search_text:
            filtered_cases = [
                case for case in filtered_cases 
                if name_search_text in case.get('child_name', '').lower()
            ]

        if age_search_text:
            filtered_cases = [
                case for case in filtered_cases 
                if age_search_text == case.get('age_in_years', 'N/A')
            ]

        if diagnosis_search_text:
            filtered_cases = [
                case for case in filtered_cases 
                if diagnosis_search_text in case.get('diagnosis', '').lower()
            ]

        # 4. Update the QListWidget with the final filtered results
        self.case_list_widget.clear()
        
        if not filtered_cases:
            self.case_list_widget.addItem("لا توجد نتائج مطابقة للبحث.")
            self.case_list_widget.setEnabled(False)
            self.btn_open_case.setEnabled(False)
            self.btn_remove_case.setEnabled(False)
        else:
            self.case_list_widget.setEnabled(True)
            self.btn_open_case.setEnabled(True)
            self.btn_remove_case.setEnabled(True)
            
            for case in filtered_cases:
                self.case_list_widget.addItem(case['display_name'])
                self.case_list_widget.item(self.case_list_widget.count() - 1).setData(Qt.UserRole, case['folder_name'])


    def open_selected_case(self):
        """Opens the selected case from the list in the CaseViewer for viewing."""
        selected_item = self.case_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "لم يتم تحديد حالة", "الرجاء تحديد حالة من القائمة لفتحها.")
            return

        # Retrieve the folder name stored in the item's data
        case_folder_name = selected_item.data(Qt.UserRole)
        if not case_folder_name or not os.path.exists(os.path.join(get_data_directory(), case_folder_name, "case.json")):
             QMessageBox.critical(self, "خطأ", f"بيانات الحالة غير موجودة أو تالفة للمجلد: {case_folder_name}.")
             self.populate_case_list() # Refresh list if an item is problematic
             return

        case_data = load_case_data_from_json(case_folder_name)

        if case_data:
            # Open the case viewer
            self.case_viewer_dialog = CaseViewer(case_data, case_folder_name, parent=self)
            result = self.case_viewer_dialog.exec_()
            
            # If the viewer returns Accepted, it means data was updated (edit was performed)
            if result == QDialog.Accepted:
                print(f"Case viewer for '{case_folder_name}' closed with updates. Refreshing list.")
                self.populate_case_list() # Refresh the list to show any updates
            else:
                print(f"Case viewer for '{case_folder_name}' closed without updates.")
        else:
            QMessageBox.critical(self, "خطأ في التحميل", f"فشل تحميل بيانات الحالة من المجلد: {case_folder_name}.")
            self.populate_case_list() # Refresh list if loading failed


    def edit_selected_case(self):
        """Opens the selected case from the list in the CaseForm for editing."""
        selected_item = self.case_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "لم يتم تحديد حالة", "الرجاء تحديد حالة من القائمة لفتحها.")
            return

        # Retrieve the folder name stored in the item's data
        case_folder_name = selected_item.data(Qt.UserRole)
        if not case_folder_name or not os.path.exists(os.path.join(get_data_directory(), case_folder_name, "case.json")):
             QMessageBox.critical(self, "خطأ", f"بيانات الحالة غير موجودة أو تالفة للمجلد: {case_folder_name}.")
             self.populate_case_list() # Refresh list if an item is problematic
             return

        case_data = load_case_data_from_json(case_folder_name)

        if case_data:
            # Open the case form
            self.edit_case_dialog = CaseForm(parent=self, case_data_to_load=case_data)
            result = self.edit_case_dialog.exec_()
            
             # If the viewer returns Accepted, it means data was updated (edit was performed)
            if result == QDialog.Accepted:
                print(f"Case form for \'{case_folder_name}\' accepted (data potentially updated). Refreshing list.")
                self.populate_case_list() # Refresh if data was changed and re-saved
            else:
                print(f"Case form for \'{case_folder_name}\' cancelled or closed.")
        else:
            QMessageBox.critical(self, "خطأ في التحميل", f"فشل تحميل بيانات الحالة من المجلد: {case_folder_name}.")
            self.populate_case_list() # Refresh list if loading failed


    def remove_selected_case(self):
        """Removes the selected case after confirmation."""
        selected_item = self.case_list_widget.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "لم يتم تحديد حالة", "الرجاء تحديد حالة من القائمة لحذفها.")
            return

        # Retrieve the folder name stored in the item's data
        case_folder_name = selected_item.data(Qt.UserRole)
        if not case_folder_name or not os.path.exists(os.path.join(get_data_directory(), case_folder_name)):
            QMessageBox.critical(self, "خطأ", f"مجلد الحالة غير موجود: {case_folder_name}.")
            self.populate_case_list()  # Refresh list if an item is problematic
            return

        # Get case data for confirmation message
        case_data = load_case_data_from_json(case_folder_name)
        if not case_data:
            QMessageBox.critical(self, "خطأ", f"بيانات الحالة غير موجودة أو تالفة للمجلد: {case_folder_name}.")
            self.populate_case_list()
            return

        # Display confirmation dialog with case details
        child_name = case_data.get("child_name", {}).get("value", "")
        case_id = case_data.get("case_id", "")
        
        confirmation_message = f"هل أنت متأكد من حذف الحالة التالية نهائيًا؟\n\nاسم الحالة: {child_name}\nرقم الحالة: {case_id}\n\nلا يمكن التراجع عن هذا الإجراء."
        
        # Add extra confirmation by asking user to type "حذف" to confirm
        text, ok = QInputDialog.getText(
            self, 
            "تأكيد الحذف", 
            f"{confirmation_message}\n\nاكتب كلمة \"حذف\" للتأكيد:",
            QLineEdit.Normal
        )
        
        if ok and text == "حذف":
            try:
                # Delete the case folder and all its contents
                case_path = os.path.join(get_data_directory(), case_folder_name)
                shutil.rmtree(case_path)
                
                QMessageBox.information(self, "تم الحذف", f"تم حذف الحالة \"{child_name}\" بنجاح.")
                
                # Refresh the case list
                self.populate_case_list()
            except Exception as e:
                QMessageBox.critical(self, "خطأ في الحذف", f"حدث خطأ أثناء محاولة حذف الحالة:\n{str(e)}")
        else:
            QMessageBox.information(self, "تم إلغاء الحذف", "تم إلغاء عملية الحذف.")
