import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QLocale, QFile, QTextStream
from PyQt5.QtGui import QIcon

from ui.main_window import MainWindow # type: ignore
from utils.general import make_all_labels_copyable # type: ignore

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

    app.setWindowIcon(QIcon("icons/app_icon.png"))

    apply_stylesheet(app, "styles/main_style.qss")

    
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

