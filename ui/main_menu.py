"""
Main menu interface with wallpaper support
UPDATED: Added Achievement, Trailer, Story, and About buttons
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QFont, QRadialGradient, QPixmap
from PySide6.QtMultimedia import QMediaPlayer
from app.state_manager import GameState
from ui.video_player import VideoPlayer
from ui.story_viewer import StoryViewer
from ui.achievement_viewer import AchievementViewer
import math
import os

class MainMenu(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent_window = parent
        self.animation_offset = 0
        
        # Idle time tracker for achievement
        self.idle_time = 0
        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.track_idle_time)
        self.idle_timer.start(1000)  # Track every second
        
        # Load Wallpaper Image
        self.bg_image = None        
        image_path = "./ancient_gfx/splash.webp" 
        
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
        
        # Corner buttons (Trailer, Story, Achievement, About)
        corner_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #8B4513, stop:1 #654321);
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #A0522D, stop:1 #8B4513);
                border: 2px solid #FFA500;
            }
        """
        
        # Achievement button (left side, above Trailer)
        self.achievement_button = QPushButton("🏆 Achievement", self)
        self.achievement_button.setStyleSheet(corner_button_style)
        self.achievement_button.clicked.connect(self.show_achievements)
        self.achievement_button.setCursor(Qt.PointingHandCursor)
        self.achievement_button.setFixedSize(160, 50)
        self.achievement_button.raise_()
        
        # Trailer button (bottom-left)
        self.trailer_button = QPushButton("🎬 Trailer", self)
        self.trailer_button.setStyleSheet(corner_button_style)
        self.trailer_button.clicked.connect(self.show_trailer)
        self.trailer_button.setCursor(Qt.PointingHandCursor)
        self.trailer_button.setFixedSize(140, 50)
        self.trailer_button.raise_()
        
        # About button (right side, above Story)
        self.about_button = QPushButton("ℹ️ About", self)
        self.about_button.setStyleSheet(corner_button_style)
        self.about_button.clicked.connect(self.show_about)
        self.about_button.setCursor(Qt.PointingHandCursor)
        self.about_button.setFixedSize(140, 50)
        self.about_button.raise_()
        
        # Story button (bottom-right)
        self.story_button = QPushButton("📖 Story", self)
        self.story_button.setStyleSheet(corner_button_style)
        self.story_button.clicked.connect(self.show_story)
        self.story_button.setCursor(Qt.PointingHandCursor)
        self.story_button.setFixedSize(140, 50)
        self.story_button.raise_()
        
        self.setLayout(layout)
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS
        
        # Initial button positioning
        QTimer.singleShot(100, self.position_corner_buttons)

    def create_button(self, text, slot, layout, style):
        btn = QPushButton(text)
        btn.setStyleSheet(style)
        btn.clicked.connect(slot)
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
            scaled_pixmap = self.bg_image.scaled(
                self.size(), 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            )
            
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)
            
            painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
            
        else:
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            hue1 = (math.sin(self.animation_offset) * 0.1 + 0.05) * 360
            hue2 = (math.cos(self.animation_offset * 0.7) * 0.1 + 0.15) * 360
            color1 = QColor.fromHsv(int(hue1) % 360, 60, 40)
            color2 = QColor.fromHsv(int(hue2) % 360, 80, 20)
            gradient.setColorAt(0, color1)
            gradient.setColorAt(1, color2)
            painter.fillRect(self.rect(), gradient)
        
        # 2. Draw animated decorative orbs
        for i in range(15):
            x = (math.sin(self.animation_offset + i * 0.5) * 0.3 + 0.5) * self.width()
            y = (math.cos(self.animation_offset * 0.8 + i * 0.7) * 0.3 + 0.5) * self.height()
            size = 20 + math.sin(self.animation_offset * 2 + i) * 10
            
            radial = QRadialGradient(x, y, size)
            colors = [QColor(255, 0, 0), QColor(0, 0, 255), QColor(0, 255, 0), 
                     QColor(255, 255, 0), QColor(255, 0, 255)]
            color = colors[i % len(colors)]
            
            alpha = 40 if self.bg_image else 60
            color.setAlpha(alpha)
            
            radial.setColorAt(0, color)
            color.setAlpha(0)
            radial.setColorAt(1, color)
            
            painter.setBrush(radial)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(x - size/2, y - size/2, size, size))
        
    def new_game(self):
        """Start new game with intro videos"""
        # Play intro videos before starting game
        self.play_intro_videos()
        
    def play_intro_videos(self):
        """Play start_mode.mp4 then flying.mp4 before game starts"""
        start_mode_path = "./ancient_gfx/start_mode.mp4"
        flying_path = "./ancient_gfx/flying.mp4"
        
        # First video: start_mode.mp4
        video_player_1 = VideoPlayer(self)
        
        def on_start_mode_finished():
            print("Intro: start_mode.mp4 finished, playing flying.mp4...")
            video_player_1.deleteLater()
            
            # Second video: flying.mp4
            video_player_2 = VideoPlayer(self)
            
            def on_flying_finished():
                print("Intro: flying.mp4 finished, starting game...")
                video_player_2.deleteLater()
                self.start_game()
            
            def on_flying_skipped():
                print("Intro: flying.mp4 skipped, starting game...")
                video_player_2.deleteLater()
                self.start_game()
            
            video_player_2.video_finished.connect(on_flying_finished)
            video_player_2.video_skipped.connect(on_flying_skipped)
            video_player_2.play_video(flying_path)
        
        def on_start_mode_skipped():
            print("Intro: start_mode.mp4 skipped, playing flying.mp4...")
            video_player_1.deleteLater()
            
            # Skip to second video
            video_player_2 = VideoPlayer(self)
            
            def on_flying_finished():
                print("Intro: flying.mp4 finished, starting game...")
                video_player_2.deleteLater()
                self.start_game()
            
            def on_flying_skipped():
                print("Intro: flying.mp4 skipped, starting game...")
                video_player_2.deleteLater()
                self.start_game()
            
            video_player_2.video_finished.connect(on_flying_finished)
            video_player_2.video_skipped.connect(on_flying_skipped)
            video_player_2.play_video(flying_path)
        
        video_player_1.video_finished.connect(on_start_mode_finished)
        video_player_1.video_skipped.connect(on_start_mode_skipped)
        video_player_1.play_video(start_mode_path)
    
    def start_game(self):
        """Actually start the game after videos"""
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
            msg.setStyleSheet("QLabel{color: black;} QPushButton{color: black;}")
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
    
    def show_trailer(self):
        """Show trailer video"""
        trailer_path = "./ancient_gfx/trailer.mp4"
        
        video_player = VideoPlayer(self)
        video_player.video_finished.connect(lambda: print("Trailer finished"))
        video_player.video_skipped.connect(lambda: print("Trailer skipped"))
        video_player.play_video(trailer_path)
    
    def show_story(self):
        """Show story viewer"""
        story_path = "./story/story-en.txt"
        
        story_viewer = StoryViewer(self)
        
        def on_story_finished():
            print("Story finished - marking achievement")
            if hasattr(self.parent_window, 'game_manager'):
                if hasattr(self.parent_window.game_manager, 'achievement_tracker'):
                    self.parent_window.game_manager.achievement_tracker.on_story_viewed(completed=True)
        
        def on_story_closed():
            print("Story closed")
            if hasattr(self.parent_window, 'game_manager'):
                if hasattr(self.parent_window.game_manager, 'achievement_tracker'):
                    self.parent_window.game_manager.achievement_tracker.on_story_viewed(completed=False)
        
        story_viewer.story_finished.connect(on_story_finished)
        story_viewer.story_closed.connect(on_story_closed)
        story_viewer.show_story(story_path)
    
    def show_achievements(self):
        """Show achievement viewer"""
        if hasattr(self.parent_window, 'game_manager'):
            if hasattr(self.parent_window.game_manager, 'achievement_manager'):
                viewer = AchievementViewer(
                    self.parent_window.game_manager.achievement_manager,
                    self
                )
                viewer.closed.connect(lambda: print("Achievement viewer closed"))
                viewer.show_viewer()
            else:
                print("Achievement manager not available")
        else:
            print("Game manager not available")
    
    def show_about(self):
        """Show about viewer (same as story viewer)"""
        about_path = "./story/about.txt"
        
        story_viewer = StoryViewer(self)
        story_viewer.story_finished.connect(lambda: print("About finished"))
        story_viewer.story_closed.connect(lambda: print("About closed"))
        story_viewer.show_story(about_path)
    
    def track_idle_time(self):
        """Track idle time in menu for achievement"""
        if self.isVisible():
            self.idle_time += 1
            if hasattr(self.parent_window, 'game_manager'):
                if hasattr(self.parent_window.game_manager, 'achievement_tracker'):
                    self.parent_window.game_manager.achievement_tracker.update_idle_time(1)
    
    def resizeEvent(self, event):
        """Position corner buttons on resize"""
        super().resizeEvent(event)
        self.position_corner_buttons()
    
    def showEvent(self, event):
        """Reset idle time when menu is shown"""
        super().showEvent(event)
        self.idle_time = 0
        # Pastikan audio_manager tersedia
        if hasattr(self.parent_window, 'game_manager'):
            if hasattr(self.parent_window.game_manager, 'audio_manager'):
                audio = self.parent_window.game_manager.audio_manager
                if audio.bgm_player.playbackState() != QMediaPlayer.PlayingState:
                    audio.fade_in_bgm(3000)
    
    def position_corner_buttons(self):
        """Helper method to position corner buttons"""
        margin = 20
        vertical_spacing = 60  # Space between stacked buttons
        
        # Left side - Achievement (top) and Trailer (bottom)
        if hasattr(self, 'achievement_button') and self.achievement_button:
            self.achievement_button.move(
                margin,
                self.height() - (self.achievement_button.height() * 2) - vertical_spacing - margin
            )
            self.achievement_button.raise_()
        
        if hasattr(self, 'trailer_button') and self.trailer_button:
            self.trailer_button.move(
                margin,
                self.height() - self.trailer_button.height() - margin
            )
            self.trailer_button.raise_()
        
        # Right side - About (top) and Story (bottom)
        if hasattr(self, 'about_button') and self.about_button:
            self.about_button.move(
                self.width() - self.about_button.width() - margin,
                self.height() - (self.about_button.height() * 2) - vertical_spacing - margin
            )
            self.about_button.raise_()
        
        if hasattr(self, 'story_button') and self.story_button:
            self.story_button.move(
                self.width() - self.story_button.width() - margin,
                self.height() - self.story_button.height() - margin
            )
            self.story_button.raise_()