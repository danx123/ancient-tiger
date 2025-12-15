"""
Pause menu overlay
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from app.state_manager import GameState

class PauseMenu(QDialog):
    """Pause menu overlay dialog"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setModal(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup pause menu UI"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("PAUSED")
        title.setFont(QFont("Arial", 36, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)        
        title.setStyleSheet("color: #FFD700;")
        layout.addWidget(title)
        
        # Buttons
        button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #8B4513, stop:1 #654321);
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 10px;
                padding: 12px 30px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #A0522D, stop:1 #8B4513);
            }
        """
        
        resume_btn = QPushButton("Resume")
        resume_btn.setStyleSheet(button_style)
        resume_btn.clicked.connect(self.resume)
        layout.addWidget(resume_btn, alignment=Qt.AlignCenter)
        
        menu_btn = QPushButton("Main Menu")
        menu_btn.setStyleSheet(button_style)
        menu_btn.clicked.connect(self.return_to_menu)
        layout.addWidget(menu_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180);")
        
    def show_overlay(self):
        """Show pause overlay"""
        self.setGeometry(self.parent_window.rect())
        self.show()
        
    def hide_overlay(self):
        """Hide pause overlay"""
        self.hide()
        
    def resume(self):
        """Resume game"""
        self.hide_overlay()
        self.parent_window.state_manager.change_state(GameState.PLAYING)
        if self.parent_window.game_scene:
            self.parent_window.game_scene.resume_game()
            
    def return_to_menu(self):
        """Return to main menu"""
        self.hide_overlay()
        self.parent_window.state_manager.change_state(GameState.MAIN_MENU)