"""
Main menu interface with wallpaper support
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QFont, QRadialGradient, QPixmap
from app.state_manager import GameState
import math
import os

class MainMenu(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent_window = parent
        self.animation_offset = 0
        
        # Load Wallpaper Image
        self.bg_image = None
        # Cek lokasi file splash.webp (diasumsikan ada di root folder sejajar main.py)
        image_path = "splash.webp" 
        
        if os.path.exists(image_path):
            self.bg_image = QPixmap(image_path)
            print(f"MainMenu: Wallpaper loaded from {image_path}")
        else:
            print(f"MainMenu: Wallpaper not found at {image_path}, using gradient.")

        # Setup UI
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("")
        title_font = QFont("Arial", 48, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        # Menambahkan shadow hitam tebal agar teks terbaca di atas gambar
        title.setStyleSheet("color: #FFD700; text-shadow: 4px 4px 8px #000;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("")
        subtitle.setFont(QFont("Arial", 16, QFont.Bold))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #FFA500; text-shadow: 2px 2px 4px #000;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(50)
        
        # Buttons Style
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
        
        # Create Buttons
        self.create_button("New Game", self.new_game, layout, button_style)
        self.create_button("Load Game", self.load_game, layout, button_style)
        self.create_button("Settings", self.show_settings, layout, button_style)
        self.create_button("Quit", self.quit_game, layout, button_style)
        
        self.setLayout(layout)
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS
        
    def create_button(self, text, slot, layout, style):
        btn = QPushButton(text)
        btn.setStyleSheet(style)
        btn.clicked.connect(slot)
        # Tambahkan sedikit efek bayangan pada tombol
        btn.setGraphicsEffect(None) 
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        
    def animate(self):
        """Animate background elements"""
        self.animation_offset += 0.01
        self.update()
        
    def paintEvent(self, event):
        """Draw background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Draw Background Image or Fallback Gradient
        if self.bg_image:
            # Draw image scaled to fill the window (KeepAspectRatioByExpanding ensures no black bars)
            scaled_pixmap = self.bg_image.scaled(
                self.size(), 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            )
            
            # Center crop logic
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
            
            # Add Dark Overlay (Scrim) to make text readable
            painter.fillRect(self.rect(), QColor(0, 0, 0, 100)) # 100 is transparency (0-255)
            
        else:
            # Fallback: Animated gradient background if image missing
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            hue1 = (math.sin(self.animation_offset) * 0.1 + 0.05) * 360
            hue2 = (math.cos(self.animation_offset * 0.7) * 0.1 + 0.15) * 360
            color1 = QColor.fromHsv(int(hue1) % 360, 60, 40)
            color2 = QColor.fromHsv(int(hue2) % 360, 80, 20)
            gradient.setColorAt(0, color1)
            gradient.setColorAt(1, color2)
            painter.fillRect(self.rect(), gradient)
        
        # 2. Draw animated decorative orbs (overlay on top of wallpaper)
        for i in range(15):
            x = (math.sin(self.animation_offset + i * 0.5) * 0.3 + 0.5) * self.width()
            y = (math.cos(self.animation_offset * 0.8 + i * 0.7) * 0.3 + 0.5) * self.height()
            size = 20 + math.sin(self.animation_offset * 2 + i) * 10
            
            radial = QRadialGradient(x, y, size)
            colors = [QColor(255, 0, 0), QColor(0, 0, 255), QColor(0, 255, 0), 
                     QColor(255, 255, 0), QColor(255, 0, 255)]
            color = colors[i % len(colors)]
            
            # Make orbs slightly more transparent if using wallpaper
            alpha = 40 if self.bg_image else 60
            color.setAlpha(alpha)
            
            radial.setColorAt(0, color)
            color.setAlpha(0)
            radial.setColorAt(1, color)
            
            painter.setBrush(radial)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(x - size/2, y - size/2, size, size))
        
    def new_game(self):
        self.parent_window.game_manager.new_game()
        self.parent_window.state_manager.change_state(GameState.PLAYING)
        
    def load_game(self):
        success = self.parent_window.game_manager.load_game()
        if success:
            self.parent_window.state_manager.change_state(GameState.PLAYING)
        else:
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("Load Game")
            msg.setText("No saved game found!")
            msg.setStyleSheet("QLabel{color: black;} QPushButton{color: black;}") # Fix for dark theme
            msg.setInformativeText("Would you like to start a new game?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            
            if msg.exec() == QMessageBox.Yes:
                self.new_game()
        
    def show_settings(self):
        from ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.parent_window, self.parent_window.game_manager.settings_manager)
        dialog.exec()
        
    def quit_game(self):
        self.parent_window.close()
