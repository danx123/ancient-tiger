"""
Main menu interface with procedurally drawn elements
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QFont, QRadialGradient
from app.state_manager import GameState
import math

class MainMenu(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent_window = parent
        self.animation_offset = 0
        
        # Setup UI
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("ANCIENT TIGER")
        title_font = QFont("Arial", 48, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #FFD700; text-shadow: 2px 2px 4px #000;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Temple of the Orbs")
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #FFA500;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(50)
        
        # Buttons
        button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #8B4513, stop:1 #654321);
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 10px;
                padding: 15px 40px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #A0522D, stop:1 #8B4513);
                border: 2px solid #FFA500;
            }
            QPushButton:pressed {
                background: #654321;
            }
        """
        
        new_game_btn = QPushButton("New Game")
        new_game_btn.setStyleSheet(button_style)
        new_game_btn.clicked.connect(self.new_game)
        layout.addWidget(new_game_btn, alignment=Qt.AlignCenter)
        
        load_game_btn = QPushButton("Load Game")
        load_game_btn.setStyleSheet(button_style)
        load_game_btn.clicked.connect(self.load_game)
        layout.addWidget(load_game_btn, alignment=Qt.AlignCenter)
        
        settings_btn = QPushButton("Settings")
        settings_btn.setStyleSheet(button_style)
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn, alignment=Qt.AlignCenter)
        
        quit_btn = QPushButton("Quit")
        quit_btn.setStyleSheet(button_style)
        quit_btn.clicked.connect(self.quit_game)
        layout.addWidget(quit_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS
        
    def animate(self):
        """Animate background"""
        self.animation_offset += 0.01
        self.update()
        
    def paintEvent(self, event):
        """Draw animated background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Animated gradient background
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        
        hue1 = (math.sin(self.animation_offset) * 0.1 + 0.05) * 360
        hue2 = (math.cos(self.animation_offset * 0.7) * 0.1 + 0.15) * 360
        
        color1 = QColor.fromHsv(int(hue1) % 360, 60, 40)
        color2 = QColor.fromHsv(int(hue2) % 360, 80, 20)
        
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)
        painter.fillRect(self.rect(), gradient)
        
        # Draw decorative orbs
        for i in range(15):
            x = (math.sin(self.animation_offset + i * 0.5) * 0.3 + 0.5) * self.width()
            y = (math.cos(self.animation_offset * 0.8 + i * 0.7) * 0.3 + 0.5) * self.height()
            size = 20 + math.sin(self.animation_offset * 2 + i) * 10
            
            radial = QRadialGradient(x, y, size)
            colors = [QColor(255, 0, 0), QColor(0, 0, 255), QColor(0, 255, 0), 
                     QColor(255, 255, 0), QColor(255, 0, 255)]
            color = colors[i % len(colors)]
            color.setAlpha(60)
            
            radial.setColorAt(0, color)
            color.setAlpha(0)
            radial.setColorAt(1, color)
            
            painter.setBrush(radial)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(x - size/2, y - size/2, size, size))
        
    def new_game(self):
        """Start new game"""
        self.parent_window.game_manager.new_game()
        self.parent_window.state_manager.change_state(GameState.PLAYING)
        
    def load_game(self):
        """Load saved game"""
        success = self.parent_window.game_manager.load_game()
        if success:
            print(f"MainMenu: Game loaded - Level {self.parent_window.game_manager.current_level}")
            self.parent_window.state_manager.change_state(GameState.PLAYING)
        else:
            # Show error message if no save exists
            print("MainMenu: No save game found")
            # Could show a dialog here, but for now just start new game
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Load Game")
            msg.setText("No saved game found!")
            msg.setInformativeText("Would you like to start a new game?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            
            result = msg.exec()
            if result == QMessageBox.Yes:
                self.new_game()
        
    def show_settings(self):
        """Show settings"""
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.parent_window, self.parent_window.game_manager.settings_manager)
        dialog.exec()
        
    def quit_game(self):
        """Quit application"""
        self.parent_window.close()