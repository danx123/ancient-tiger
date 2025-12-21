"""
Story viewer with scrolling credits animation
"""

from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QFont, QColor, QLinearGradient
import os
import sys

class StoryViewer(QWidget):
    """Story viewer with scrolling credits effect"""
    
    story_finished = Signal()
    story_closed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self.story_lines = []
        self.scroll_position = 0
        self.scroll_speed = 50  # pixels per second
        self.line_height = 40
        self.finished = False
        
        # Close button
        self.close_button = QPushButton("Close (ESC)", self)
        self.close_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #8B4513, stop:1 #654321);
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #A0522D, stop:1 #8B4513);
            }
        """)
        self.close_button.clicked.connect(self.close_story)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setFixedSize(140, 50)
        self.close_button.raise_()
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scroll)
        
    def load_story(self, story_path):
        """Load story from text file"""
        # Check PyInstaller path
        if hasattr(sys, "_MEIPASS"):
            frozen_path = os.path.join(sys._MEIPASS, story_path)
            if os.path.exists(frozen_path):
                story_path = frozen_path
        
        if not os.path.exists(story_path):
            print(f"StoryViewer: Story file not found at {story_path}")
            self.story_lines = ["Story file not found."]
            return False
        
        try:
            with open(story_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Split by lines and preserve empty lines
                self.story_lines = content.split('\n')
            
            print(f"StoryViewer: Loaded {len(self.story_lines)} lines from {story_path}")
            return True
            
        except Exception as e:
            print(f"StoryViewer: Error loading story - {e}")
            self.story_lines = ["Error loading story."]
            return False
    
    def show_story(self, story_path):
        """Show story with scrolling animation"""
        if self.load_story(story_path):
            self.scroll_position = self.height()  # Start from bottom
            self.finished = False
            self.showFullScreen()
            self.timer.start(16)  # ~60 FPS
            # Position button after showing fullscreen
            QTimer.singleShot(100, self.position_close_button)
            
    def update_scroll(self):
        """Update scroll position"""
        if not self.finished:
            self.scroll_position -= self.scroll_speed * 0.016  # dt = 16ms
            
            # Check if finished scrolling
            total_height = len(self.story_lines) * self.line_height
            if self.scroll_position < -total_height:
                self.finished = True
                self.story_finished.emit()
            
            self.update()
            
    def close_story(self):
        """Close story viewer"""
        self.timer.stop()
        self.story_closed.emit()
        self.close()
        
    def paintEvent(self, event):
        """Draw scrolling text"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(10, 5, 15))
        gradient.setColorAt(1, QColor(20, 10, 25))
        painter.fillRect(self.rect(), gradient)
        
        # Draw story text
        painter.setFont(QFont("Arial", 18))
        
        start_y = int(self.scroll_position)
        
        for i, line in enumerate(self.story_lines):
            y_pos = start_y + (i * self.line_height)
            
            # Only draw visible lines
            if -self.line_height < y_pos < self.height() + self.line_height:
                # Calculate fade effect at top and bottom
                alpha = 255
                fade_zone = 100
                
                if y_pos < fade_zone:
                    alpha = int(255 * (y_pos / fade_zone))
                elif y_pos > self.height() - fade_zone:
                    alpha = int(255 * ((self.height() - y_pos) / fade_zone))
                
                alpha = max(0, min(255, alpha))
                
                # Set text color with alpha
                if line.strip().startswith('#'):  # Title lines
                    painter.setPen(QColor(255, 215, 0, alpha))
                    painter.setFont(QFont("Arial", 24, QFont.Bold))
                else:
                    painter.setPen(QColor(255, 255, 255, alpha))
                    painter.setFont(QFont("Arial", 18))
                
                # Draw centered text
                text_rect = painter.fontMetrics().boundingRect(line)
                x_pos = (self.width() - text_rect.width()) // 2
                painter.drawText(x_pos, y_pos, line)
        
        # Draw fade overlay at top and bottom
        top_fade = QLinearGradient(0, 0, 0, 150)
        top_fade.setColorAt(0, QColor(10, 5, 15, 255))
        top_fade.setColorAt(1, QColor(10, 5, 15, 0))
        painter.fillRect(0, 0, self.width(), 150, top_fade)
        
        bottom_fade = QLinearGradient(0, self.height() - 150, 0, self.height())
        bottom_fade.setColorAt(0, QColor(20, 10, 25, 0))
        bottom_fade.setColorAt(1, QColor(20, 10, 25, 255))
        painter.fillRect(0, self.height() - 150, self.width(), 150, bottom_fade)
        
    def keyPressEvent(self, event):
        """Handle key press - ESC to close"""
        if event.key() == Qt.Key_Escape:
            self.close_story()
        else:
            super().keyPressEvent(event)
            
    def resizeEvent(self, event):
        """Position close button on resize"""
        super().resizeEvent(event)
        self.position_close_button()
    
    def position_close_button(self):
        """Helper method to position close button at bottom-right"""
        if hasattr(self, 'close_button') and self.close_button:
            margin = 20
            self.close_button.move(
                self.width() - self.close_button.width() - margin,
                self.height() - self.close_button.height() - margin
            )
            self.close_button.raise_()
        
    def closeEvent(self, event):
        """Cleanup on close"""
        self.timer.stop()
        event.accept()