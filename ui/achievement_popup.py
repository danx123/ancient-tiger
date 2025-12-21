"""
Achievement unlock notification popup
"""

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QPainter, QColor, QFont, QLinearGradient

class AchievementPopup(QWidget):
    """Achievement unlock notification that slides in from top"""
    
    def __init__(self, achievement_id, name, description, icon, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        self.achievement_id = achievement_id
        self.name = name
        self.description = description
        self.icon = icon
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup popup UI"""
        self.setFixedSize(400, 100)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont("Arial", 36))
        icon_label.setFixedSize(60, 60)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("color: #FFD700;")
        layout.addWidget(icon_label)
        
        # Text info
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        header = QLabel("🏆 ACHIEVEMENT UNLOCKED!")
        header.setFont(QFont("Arial", 10, QFont.Bold))
        header.setStyleSheet("color: #FFD700;")
        text_layout.addWidget(header)
        
        name_label = QLabel(self.name)
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        name_label.setStyleSheet("color: #FFFFFF;")
        text_layout.addWidget(name_label)
        
        desc_label = QLabel(self.description)
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setStyleSheet("color: #CCCCCC;")
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout, 1)
        
        self.setLayout(layout)
        
    def paintEvent(self, event):
        """Draw background with gradient"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(139, 69, 19, 240))
        gradient.setColorAt(1, QColor(101, 67, 33, 240))
        
        painter.setBrush(gradient)
        painter.setPen(QColor(255, 215, 0, 255))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        
    def show_notification(self, parent_widget):
        """Show notification with animation"""
        if parent_widget:
            # Position at top center of parent
            x = (parent_widget.width() - self.width()) // 2
            y = -self.height()  # Start above screen
            
            self.move(parent_widget.mapToGlobal(QPoint(x, y)))
        
        self.show()
        
        # Slide in animation
        self.slide_animation = QPropertyAnimation(self, b"pos")
        self.slide_animation.setDuration(500)
        self.slide_animation.setStartValue(self.pos())
        
        target_y = 20  # Final position from top
        if parent_widget:
            target_pos = parent_widget.mapToGlobal(QPoint(x, target_y))
        else:
            target_pos = QPoint(self.pos().x(), target_y)
        
        self.slide_animation.setEndValue(target_pos)
        self.slide_animation.setEasingCurve(QEasingCurve.OutBounce)
        self.slide_animation.start()
        
        # Auto hide after 4 seconds
        QTimer.singleShot(4000, self.hide_notification)
        
    def hide_notification(self):
        """Hide notification with animation"""
        self.slide_animation = QPropertyAnimation(self, b"pos")
        self.slide_animation.setDuration(300)
        self.slide_animation.setStartValue(self.pos())
        self.slide_animation.setEndValue(QPoint(self.pos().x(), -self.height()))
        self.slide_animation.setEasingCurve(QEasingCurve.InBack)
        self.slide_animation.finished.connect(self.close)
        self.slide_animation.start()