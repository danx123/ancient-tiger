"""
Ancient Tiger - Zuma-style Arcade Puzzle Game
Entry point for the application
"""

import sys
from PySide6.QtWidgets import QApplication
from app.app_window import AppWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Ancient Tiger")
    app.setOrganizationName("MacanAngkasa")
    
    window = AppWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()