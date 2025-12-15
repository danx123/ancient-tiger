"""
Main application window managing all screens and game states
"""

from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtCore import Qt, QTimer
from app.game_manager import GameManager
from app.state_manager import StateManager, GameState
from ui.main_menu import MainMenu
from games.scene import GameScene
from ui.pause_menu import PauseMenu

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ancient Tiger")
        self.setMinimumSize(1024, 768)
        
        # Initialize managers
        self.state_manager = StateManager()
        self.game_manager = GameManager(self)
        
        print("AppWindow: Game Manager initialized")
        print(f"AppWindow: Audio Manager available: {hasattr(self.game_manager, 'audio_manager')}")
        
        # Apply fullscreen setting from config
        fullscreen = self.game_manager.settings_manager.get('fullscreen', False)
        if fullscreen:
            print("AppWindow: Starting in fullscreen mode")
            self.showFullScreen()
        
        # Setup UI
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Create screens
        self.main_menu = MainMenu(self)
        self.game_scene = None
        self.pause_menu = None
        
        self.stack.addWidget(self.main_menu)
        
        # Connect state changes
        self.state_manager.state_changed.connect(self.on_state_changed)
        
        # Set initial state
        self.state_manager.change_state(GameState.MAIN_MENU)
        
    def on_state_changed(self, state):
        """Handle state transitions"""
        if state == GameState.MAIN_MENU:
            self.show_main_menu()
        elif state == GameState.PLAYING:
            self.start_game()
        elif state == GameState.PAUSED:
            self.show_pause_menu()
        elif state == GameState.GAME_OVER:
            self.show_game_over()
            
    def show_main_menu(self):
        """Show main menu"""
        self.stack.setCurrentWidget(self.main_menu)
        if self.game_scene:
            self.game_scene.stop_game()
        
        # Ensure BGM is playing
        if hasattr(self.game_manager, 'audio_manager'):
            self.game_manager.audio_manager.play_bgm()
            
    def start_game(self):
        """Start new game"""
        if not self.game_scene:
            self.game_scene = GameScene(self)
            self.stack.addWidget(self.game_scene)
        
        self.game_scene.start_new_game(self.game_manager.current_level)
        self.stack.setCurrentWidget(self.game_scene)
        self.game_scene.setFocus()
        
    def show_pause_menu(self):
        """Show pause menu overlay"""
        if not self.pause_menu:
            self.pause_menu = PauseMenu(self)
        
        if self.game_scene:
            self.game_scene.pause_game()
        self.pause_menu.show_overlay()
        
    def show_game_over(self):
        """Handle game over"""
        QTimer.singleShot(2000, lambda: self.state_manager.change_state(GameState.MAIN_MENU))
        
    def keyPressEvent(self, event):
        """Handle global key events"""
        if event.key() == Qt.Key_Escape:
            current_state = self.state_manager.current_state
            if current_state == GameState.PLAYING:
                self.state_manager.change_state(GameState.PAUSED)
            elif current_state == GameState.PAUSED:
                self.state_manager.change_state(GameState.PLAYING)
                if self.game_scene:
                    self.game_scene.resume_game()
                if self.pause_menu:
                    self.pause_menu.hide_overlay()
        elif event.key() == Qt.Key_F11:
            # Toggle fullscreen with F11
            if self.isFullScreen():
                self.showNormal()
                self.game_manager.settings_manager.set('fullscreen', False)
            else:
                self.showFullScreen()
                self.game_manager.settings_manager.set('fullscreen', True)
        
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close - save settings"""
        print("AppWindow: Closing, saving settings...")
        # Settings are already saved when changed, but just in case
        self.game_manager.settings_manager.save_settings()
        event.accept()