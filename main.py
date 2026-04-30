import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from storage.database import DatabaseManager

def main():
    # Ensure resource directories exist (should already be created)
    # Initialize Database
    db_manager = DatabaseManager()
    
    # Initialize Application
    app = QApplication(sys.argv)
    
    # Set global style
    app.setStyle("Fusion")
    
    window = MainWindow(db_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
