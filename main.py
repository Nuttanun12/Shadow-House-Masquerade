import sys
import os

# Ensure the project root is in the path when running directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow, APP_STYLESHEET
from storage.database import DatabaseManager


def main():
    """Application entry point."""
    # Change working directory to project root so resource paths resolve correctly
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    # Initialise the database (creates tables if they don't exist)
    db_manager = DatabaseManager(os.path.join(project_root, "game_records.db"))

    # Create the Qt application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLESHEET)
    app.setApplicationName("Shadow House: Masquerade")

    # Launch the main window
    window = MainWindow(db_manager)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
