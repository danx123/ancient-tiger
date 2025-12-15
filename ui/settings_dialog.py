"""
Settings dialog interface
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                                QLabel, QSlider, QCheckBox, QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class SettingsDialog(QDialog):
    """Settings configuration dialog"""
    
    def __init__(self, parent, settings_manager):
        super().__init__(parent)
        self.parent_window = parent
        self.settings_manager = settings_manager
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Setup settings UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        
        # Title
        title = QLabel("SETTINGS")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #FFD700; padding: 10px;")
        main_layout.addWidget(title)
        
        # Audio Settings Group
        audio_group = QGroupBox("Audio")
        audio_group.setStyleSheet("""
            QGroupBox {
                color: #FFD700;
                border: 2px solid #8B4513;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        audio_layout = QVBoxLayout()
        
        # Music Enable/Disable
        self.music_checkbox = QCheckBox("Enable Music")
        self.music_checkbox.setStyleSheet("color: #FFA500; font-size: 14px;")
        audio_layout.addWidget(self.music_checkbox)
        
        # Music Volume
        music_vol_layout = QHBoxLayout()
        music_vol_label = QLabel("Music Volume:")
        music_vol_label.setStyleSheet("color: #FFA500;")
        music_vol_layout.addWidget(music_vol_label)
        
        self.music_slider = QSlider(Qt.Horizontal)
        self.music_slider.setMinimum(0)
        self.music_slider.setMaximum(100)
        self.music_slider.setTickPosition(QSlider.TicksBelow)
        self.music_slider.setTickInterval(10)
        self.music_slider.valueChanged.connect(self.update_music_volume_label)
        music_vol_layout.addWidget(self.music_slider)
        
        self.music_vol_value = QLabel("70%")
        self.music_vol_value.setStyleSheet("color: #FFA500; min-width: 40px;")
        music_vol_layout.addWidget(self.music_vol_value)
        
        audio_layout.addLayout(music_vol_layout)
        
        # SFX Enable/Disable
        self.sfx_checkbox = QCheckBox("Enable Sound Effects")
        self.sfx_checkbox.setStyleSheet("color: #FFA500; font-size: 14px;")
        audio_layout.addWidget(self.sfx_checkbox)
        
        # SFX Volume
        sfx_vol_layout = QHBoxLayout()
        sfx_vol_label = QLabel("SFX Volume:")
        sfx_vol_label.setStyleSheet("color: #FFA500;")
        sfx_vol_layout.addWidget(sfx_vol_label)
        
        self.sfx_slider = QSlider(Qt.Horizontal)
        self.sfx_slider.setMinimum(0)
        self.sfx_slider.setMaximum(100)
        self.sfx_slider.setTickPosition(QSlider.TicksBelow)
        self.sfx_slider.setTickInterval(10)
        self.sfx_slider.valueChanged.connect(self.update_sfx_volume_label)
        sfx_vol_layout.addWidget(self.sfx_slider)
        
        self.sfx_vol_value = QLabel("80%")
        self.sfx_vol_value.setStyleSheet("color: #FFA500; min-width: 40px;")
        sfx_vol_layout.addWidget(self.sfx_vol_value)
        
        audio_layout.addLayout(sfx_vol_layout)
        
        audio_group.setLayout(audio_layout)
        main_layout.addWidget(audio_group)
        
        # Display Settings Group
        display_group = QGroupBox("Display")
        display_group.setStyleSheet("""
            QGroupBox {
                color: #FFD700;
                border: 2px solid #8B4513;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        display_layout = QVBoxLayout()
        
        # Fullscreen
        self.fullscreen_checkbox = QCheckBox("Fullscreen Mode")
        self.fullscreen_checkbox.setStyleSheet("color: #FFA500; font-size: 14px;")
        display_layout.addWidget(self.fullscreen_checkbox)
        
        # Show FPS
        #self.fps_checkbox = QCheckBox("Show FPS Counter")
        #self.fps_checkbox.setStyleSheet("color: #FFA500; font-size: 14px;")
        #display_layout.addWidget(self.fps_checkbox)
        
        display_group.setLayout(display_layout)
        main_layout.addWidget(display_group)
        
        # Spacer
        main_layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
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
            QPushButton:pressed {
                background: #654321;
            }
        """
        
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(button_style)
        save_btn.clicked.connect(self.save_and_close)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(button_style)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Style dialog background
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #2C1810, stop:1 #1A0F0A);
            }
        """)
        
    def load_settings(self):
        """Load current settings"""
        self.music_checkbox.setChecked(
            self.settings_manager.get('music_enabled', True)
        )
        self.music_slider.setValue(
            int(self.settings_manager.get('music_volume', 0.7) * 100)
        )
        
        self.sfx_checkbox.setChecked(
            self.settings_manager.get('sfx_enabled', True)
        )
        self.sfx_slider.setValue(
            int(self.settings_manager.get('sfx_volume', 0.8) * 100)
        )
        
        self.fullscreen_checkbox.setChecked(
            self.settings_manager.get('fullscreen', False)
        )
        #self.fps_checkbox.setChecked(
            #self.settings_manager.get('show_fps', False)
        #)
        
    def update_music_volume_label(self, value):
        """Update music volume label"""
        self.music_vol_value.setText(f"{value}%")
        
    def update_sfx_volume_label(self, value):
        """Update SFX volume label"""
        self.sfx_vol_value.setText(f"{value}%")
        
    def save_and_close(self):
        """Save settings and close dialog"""
        # Save audio settings
        self.settings_manager.set('music_enabled', self.music_checkbox.isChecked())
        self.settings_manager.set('music_volume', self.music_slider.value() / 100.0)
        self.settings_manager.set('sfx_enabled', self.sfx_checkbox.isChecked())
        self.settings_manager.set('sfx_volume', self.sfx_slider.value() / 100.0)
        
        # Save display settings
        fullscreen_enabled = self.fullscreen_checkbox.isChecked()
        self.settings_manager.set('fullscreen', fullscreen_enabled)
        #self.settings_manager.set('show_fps', self.fps_checkbox.isChecked())
        
        print(f"SettingsDialog: Saving fullscreen={fullscreen_enabled}")
        
        # Apply audio settings immediately
        if hasattr(self.parent_window, 'game_manager') and hasattr(self.parent_window.game_manager, 'audio_manager'):
            self.parent_window.game_manager.audio_manager.update_volumes()
        
        # Apply fullscreen setting
        if fullscreen_enabled:
            print("SettingsDialog: Switching to fullscreen")
            self.parent_window.showFullScreen()
        else:
            print("SettingsDialog: Switching to windowed")
            self.parent_window.showNormal()
        
        # Force settings save to disk
        self.settings_manager.save_settings()
        print("SettingsDialog: Settings saved to disk")
        
        self.accept()
