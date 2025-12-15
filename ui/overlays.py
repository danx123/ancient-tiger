"""
Additional UI overlays for game events
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPainter, QColor

class VictoryOverlay(QWidget):
    """Victory screen overlay"""
    
    def __init__(self, parent, score):
        super().__init__(parent)
        self.score = score
        self.setup_ui()
        
    def setup_ui(self):
        """Setup victory UI"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("LEVEL COMPLETE!")
        title.setFont(QFont("Arial", 48, QFont.Bold))
        title.setStyleSheet("color: #FFD700;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        score_label = QLabel(f"Score: {self.score}")
        score_label.setFont(QFont("Arial", 24))
        score_label.setStyleSheet("color: #FFA500;")
        score_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(score_label)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 200);")
        

class GameOverOverlay(QWidget):
    """Game over screen overlay"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup game over UI"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("GAME OVER")
        title.setFont(QFont("Arial", 48, QFont.Bold))
        title.setStyleSheet("color: #FF4444;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("The orbs have reached the portal...")
        subtitle.setFont(QFont("Arial", 18))
        subtitle.setStyleSheet("color: #FFFFFF;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 200);")