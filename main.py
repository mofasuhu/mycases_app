import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QLocale, QFile, QTextStream
from PyQt5.QtGui import QIcon

from ui.main_window import MainWindow
from utils.file_manager import set_data_directory
from utils.general import make_all_labels_copyable, resource_path

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def get_data_path_from_user(parent=None):
    QMessageBox.information(
        parent,
        "تحديد مجلد الحالات",
        "الرجاء تحديد المجلد الذي سيتم حفظ بيانات الحالات فيه."
    )
    path = QFileDialog.getExistingDirectory(
        parent,
        "اختر مجلد الحالات",
        os.path.expanduser("~")
    )
    return path

def apply_stylesheet(app, path):
    file = QFile(path)
    if file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())
        file.close()

def main():
    """Main function to initialize and run the PyQt5 application."""
    # Create a QApplication instance
    # sys.argv allows passing command-line arguments to the application
    app = QApplication(sys.argv)
    
    QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

    app.setLayoutDirection(Qt.RightToLeft) # Set layout to RTL for Arabic

    # app.setWindowIcon(QIcon("icons/app_icon.png"))
    app.setWindowIcon(QIcon(resource_path("icons/app_icon.png")))




    config = load_config()
    data_path = config.get("data_path")

    # Loop until we get a valid path
    while not data_path or not os.path.isdir(data_path):
        path_from_dialog = get_data_path_from_user()
        if path_from_dialog: # If user selected a path
            data_path = path_from_dialog
            config["data_path"] = data_path
            save_config(config)
        else: # If user cancelled the dialog
            QMessageBox.critical(None, "خطأ", "يجب تحديد مجلد بيانات صالح لتشغيل التطبيق.")
            sys.exit(1) # Exit the application

    # Set the data directory for the rest of the application to use
    if not set_data_directory(data_path):
        QMessageBox.critical(None, "خطأ", f"لا يمكن الوصول إلى أو إنشاء مجلد البيانات:\n{data_path}")
        sys.exit(1)






    # apply_stylesheet(app, "styles/main_style.qss")
    apply_stylesheet(app, resource_path("styles/main_style.qss"))

    
    # Create an instance of the MainWindow
    main_window = MainWindow()

    make_all_labels_copyable(main_window)

    # Show the main window
    main_window.show()

    # Start the Qt event loop
    # sys.exit() ensures a clean exit, passing the application's exit status
    sys.exit(app.exec_())

# --- Entry Point Check ---
# This ensures that main() is called only when the script is executed directly (not when it's imported as a module into another script).
if __name__ == '__main__':
    main()

