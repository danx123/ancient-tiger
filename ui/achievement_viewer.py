"""
Achievement viewer UI - displays all achievements with progress
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
                                QLabel, QPushButton, QFrame, QProgressBar)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QFont

class AchievementViewer(QWidget):
    """Achievement viewer with categorized display"""
    
    closed = Signal()
    
    def __init__(self, achievement_manager, parent=None):
        super().__init__(parent)
        self.achievement_manager = achievement_manager
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup achievement viewer UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🏆 ACHIEVEMENTS")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setStyleSheet("color: #FFD700;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Progress
        unlocked, total, percent = self.achievement_manager.get_progress()
        progress_label = QLabel(f"{unlocked}/{total} ({percent:.1f}%)")
        progress_label.setFont(QFont("Arial", 18, QFont.Bold))
        progress_label.setStyleSheet("color: #FFA500;")
        header_layout.addWidget(progress_label)
        
        main_layout.addLayout(header_layout)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMaximum(total)
        progress_bar.setValue(unlocked)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #8B4513;
                border-radius: 5px;
                background-color: #2C1810;
                height: 25px;
                text-align: center;
                color: #FFD700;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFD700, stop:1 #FFA500);
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(progress_bar)
        
        # Scroll area for achievements
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #8B4513;
                border-radius: 5px;
                background-color: rgba(0, 0, 0, 150);
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Display by category
        categories = self.achievement_manager.get_categories()
        
        for category in categories:
            # Category header
            cat_label = QLabel(f"📂 {category.upper()}")
            cat_label.setFont(QFont("Arial", 16, QFont.Bold))
            cat_label.setStyleSheet("color: #FFA500; padding: 10px 0;")
            scroll_layout.addWidget(cat_label)
            
            # Achievements in this category
            achievements = self.achievement_manager.get_by_category(category)
            
            for ach_id, ach_data in achievements.items():
                ach_widget = self.create_achievement_widget(ach_id, ach_data)
                scroll_layout.addWidget(ach_widget)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton("Close (ESC)")
        close_btn.setFixedSize(150, 50)
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8B4513, stop:1 #654321);
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #A0522D, stop:1 #8B4513);
            }
        """)
        close_btn.clicked.connect(self.close_viewer)
        close_btn.setCursor(Qt.PointingHandCursor)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def create_achievement_widget(self, ach_id, ach_data):
        """Create widget for single achievement"""
        is_unlocked = self.achievement_manager.is_unlocked(ach_id)
        is_hidden = ach_data.get('hidden', False) and not is_unlocked
        
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: {'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(139, 69, 19, 200), stop:1 rgba(101, 67, 33, 200))' if is_unlocked else 'rgba(50, 50, 50, 150)'};
                border: 2px solid {'#FFD700' if is_unlocked else '#555555'};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QHBoxLayout(frame)
        
        # Icon
        icon_label = QLabel(ach_data['icon'] if not is_hidden else "🔒")
        icon_label.setFont(QFont("Arial", 32))
        icon_label.setFixedSize(60, 60)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Info
        info_layout = QVBoxLayout()
        
        name = ach_data['name'] if not is_hidden else "???"
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        name_label.setStyleSheet(f"color: {'#FFD700' if is_unlocked else '#888888'};")
        info_layout.addWidget(name_label)
        
        desc = ach_data['description'] if not is_hidden else "Hidden achievement"
        desc_label = QLabel(desc)
        desc_label.setFont(QFont("Arial", 11))
        desc_label.setStyleSheet(f"color: {'#FFA500' if is_unlocked else '#666666'};")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout, 1)
        
        # Status
        if is_unlocked:
            status_label = QLabel("✓ UNLOCKED")
            status_label.setFont(QFont("Arial", 12, QFont.Bold))
            status_label.setStyleSheet("color: #00FF00;")
            layout.addWidget(status_label)
        else:
            status_label = QLabel("🔒 LOCKED")
            status_label.setFont(QFont("Arial", 12))
            status_label.setStyleSheet("color: #888888;")
            layout.addWidget(status_label)
        
        return frame
    
    def show_viewer(self):
        """Show achievement viewer fullscreen"""
        self.showFullScreen()
    
    def close_viewer(self):
        """Close achievement viewer"""
        self.closed.emit()
        self.close()
    
    def paintEvent(self, event):
        """Draw background"""
        painter = QPainter(self)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(20, 10, 25))
        gradient.setColorAt(1, QColor(10, 5, 15))
        painter.fillRect(self.rect(), gradient)
    
    def keyPressEvent(self, event):
        """Handle ESC to close"""
        if event.key() == Qt.Key_Escape:
            self.close_viewer()
        else:
            super().keyPressEvent(event)