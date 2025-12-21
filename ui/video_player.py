"""
Video player widget for trailers and cutscenes
"""

from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt, QUrl, Signal, QTimer
from PySide6.QtGui import QPainter, QFont, QColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
import os
import sys

class VideoPlayer(QWidget):
    """Video player with skip button"""
    
    video_finished = Signal()
    video_skipped = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")
        
        # Setup media player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Video widget
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        
        # Skip button
        self.skip_button = QPushButton("Skip (ESC)")
        self.skip_button.setStyleSheet("""
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
        self.skip_button.clicked.connect(self.skip_video)
        self.skip_button.setCursor(Qt.PointingHandCursor)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video_widget)
        
        # Position skip button
        self.skip_button.setParent(self)
        self.skip_button.raise_()
        
        self.setLayout(layout)
        
        # Connect signals
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.media_player.errorOccurred.connect(self.on_error)
        
    def play_video(self, video_path):
        """Play video from path"""
        print(f"VideoPlayer: Attempting to load video from: {video_path}")
        
        # Check if path exists
        if hasattr(sys, "_MEIPASS"):
            frozen_path = os.path.join(sys._MEIPASS, video_path)
            if os.path.exists(frozen_path):
                video_path = frozen_path
                print(f"VideoPlayer: Using frozen path: {frozen_path}")
        
        if not os.path.exists(video_path):
            print(f"VideoPlayer: ERROR - Video not found at {video_path}")
            self.video_finished.emit()
            return
        
        print(f"VideoPlayer: Video file found, loading...")
        print(f"VideoPlayer: File size: {os.path.getsize(video_path)} bytes")
        
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        
        print(f"VideoPlayer: Media source set, starting playback...")
        self.media_player.play()
        
        print(f"VideoPlayer: Showing fullscreen...")
        self.showFullScreen()
        
        print(f"VideoPlayer: Video playback started")
        
    def skip_video(self):
        """Skip video playback"""
        print("VideoPlayer: Video skipped")
        self.media_player.stop()
        self.video_skipped.emit()
        self.close()
        
    def on_media_status_changed(self, status):
        """Handle media status changes"""
        if status == QMediaPlayer.EndOfMedia:
            print("VideoPlayer: Video finished")
            self.video_finished.emit()
            QTimer.singleShot(100, self.close)
        elif status == QMediaPlayer.LoadedMedia:
            print("VideoPlayer: Video loaded successfully")
            
    def on_error(self, error):
        """Handle playback errors"""
        print(f"VideoPlayer: Error - {self.media_player.errorString()}")
        self.video_finished.emit()
        self.close()
        
    def keyPressEvent(self, event):
        """Handle key press - ESC to skip"""
        if event.key() == Qt.Key_Escape:
            self.skip_video()
        else:
            super().keyPressEvent(event)
            
    def resizeEvent(self, event):
        """Position skip button on resize"""
        super().resizeEvent(event)
        button_margin = 20
        self.skip_button.move(
            self.width() - self.skip_button.width() - button_margin,
            self.height() - self.skip_button.height() - button_margin
        )
        
    def closeEvent(self, event):
        """Cleanup on close"""
        self.media_player.stop()
        event.accept()