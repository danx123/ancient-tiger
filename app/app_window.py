"""
Main application window managing all screens and game states
FIXED: Proper pause/resume handling
UPDATED: First run trailer and level transition videos
"""
import os
import sys
from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from app.game_manager import GameManager
from app.state_manager import StateManager, GameState
from ui.main_menu import MainMenu
from games.scene import GameScene
from ui.pause_menu import PauseMenu
from ui.video_player import VideoPlayer
from services.first_run_manager import FirstRunManager
from ui.achievement_popup import AchievementPopup
from ui.cheat_console import CheatConsole

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ancient Tiger")
        self.setMinimumSize(1024, 768)
        icon_path = "orb.ico"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Initialize managers
        self.state_manager = StateManager()
        self.game_manager = GameManager(self)
        self.first_run_manager = FirstRunManager()
        
        print("AppWindow: Game Manager initialized")
        print(f"AppWindow: Audio Manager available: {hasattr(self.game_manager, 'audio_manager')}")
        
        # Apply fullscreen setting from config
        fullscreen = self.game_manager.settings_manager.get('fullscreen', True)
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
        self.cheat_console = None
        
        self.stack.addWidget(self.main_menu)
        
        # Connect state changes
        self.state_manager.state_changed.connect(self.on_state_changed)
        
        # Connect achievement notifications
        if hasattr(self.game_manager, 'achievement_manager'):
            self.game_manager.achievement_manager.achievement_unlocked.connect(
                self.show_achievement_notification
            )
        
        # Set initial state
        self.state_manager.change_state(GameState.MAIN_MENU)
        
        # Check first run and show trailer
        if self.first_run_manager.is_first_run():
            print("AppWindow: First run detected, showing trailer")
            QTimer.singleShot(500, self.show_first_run_trailer)
        
    def on_state_changed(self, state):
        """Handle state transitions"""
        print(f"AppWindow: State changed to {state}")
        
        if state == GameState.MAIN_MENU:
            self.show_main_menu()
        elif state == GameState.PLAYING:
            # Check if resuming from pause
            if self.state_manager.previous_state == GameState.PAUSED:
                # Just resume, don't restart
                if self.game_scene:
                    self.game_scene.resume_game()
                    if self.pause_menu:
                        self.pause_menu.hide_overlay()
            else:
                # Starting new game
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
        # Cheat console toggle - Multiple key options
        # Tilde (~), Backquote (`), atau F12 untuk cheat console
        key = event.key()
        text = event.text()
        
        # Debug print
        print(f"AppWindow: Key pressed - Code: {key}, Text: '{text}', Native: {event.nativeScanCode()}")
        
        # Try multiple ways to detect tilde/backquote
        if (key == Qt.Key_QuoteLeft or  # Backquote/Tilde
            key == Qt.Key_AsciiTilde or  # Tilde character
            text == '`' or text == '~' or  # Text comparison
            key == Qt.Key_F12):  # Alternative: F12
            
            print("AppWindow: Cheat console toggle detected")
            self.toggle_cheat_console()
            event.accept()
            return
        
        if key == Qt.Key_Escape:
            current_state = self.state_manager.current_state
            
            # Close cheat console if open
            if self.cheat_console and self.cheat_console.isVisible():
                self.cheat_console.close_console()
                event.accept()
                return
            
            if current_state == GameState.PLAYING:
                # Pause the game
                print("AppWindow: ESC pressed - Pausing game")
                self.state_manager.change_state(GameState.PAUSED)
                
            elif current_state == GameState.PAUSED:
                # Resume the game
                print("AppWindow: ESC pressed - Resuming game")
                self.state_manager.change_state(GameState.PLAYING)
                
        elif key == Qt.Key_F11:
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
        self.game_manager.settings_manager.save_settings()
        event.accept()
    
    def show_first_run_trailer(self):
        """Show trailer on first run"""
        trailer_path = "./ancient_gfx/trailer.mp4"
        
        video_player = VideoPlayer(self)
        
        def on_trailer_finish():
            print("AppWindow: First run trailer finished")
            self.first_run_manager.mark_not_first_run()
            video_player.deleteLater()
        
        def on_trailer_skip():
            print("AppWindow: First run trailer skipped")
            self.first_run_manager.mark_not_first_run()
            video_player.deleteLater()
        
        video_player.video_finished.connect(on_trailer_finish)
        video_player.video_skipped.connect(on_trailer_skip)
        video_player.play_video(trailer_path)
    
    def show_level_transition_video(self, callback=None):
        """Show flying video on level transition"""
        flying_path = "./ancient_gfx/flying.mp4"
        
        print(f"AppWindow: Attempting to play flying video from {flying_path}")
        
        video_player = VideoPlayer(self)
        
        def on_video_finish():
            print("AppWindow: Level transition video finished")
            video_player.close()
            video_player.deleteLater()
            if callback:
                QTimer.singleShot(100, callback)
        
        def on_video_skip():
            print("AppWindow: Level transition video skipped")
            video_player.close()
            video_player.deleteLater()
            if callback:
                QTimer.singleShot(100, callback)
        
        video_player.video_finished.connect(on_video_finish)
        video_player.video_skipped.connect(on_video_skip)
        video_player.play_video(flying_path)
    
    def show_achievement_notification(self, achievement_id, name, description):
        """Show achievement unlock notification"""
        if hasattr(self.game_manager, 'achievement_manager'):
            ach_data = self.game_manager.achievement_manager.ACHIEVEMENTS.get(achievement_id)
            if ach_data:
                icon = ach_data.get('icon', '🏆')
                popup = AchievementPopup(achievement_id, name, description, icon, self)
                popup.show_notification(self)
    
    def toggle_cheat_console(self):
        """Toggle cheat console"""
        print("AppWindow: toggle_cheat_console called")
        
        if not hasattr(self.game_manager, 'cheat_system') or not self.game_manager.cheat_system:
            print("AppWindow: Cheat system not available")
            return
        
        print("AppWindow: Cheat system available, creating console...")
        
        if not self.cheat_console:
            print("AppWindow: Creating new cheat console")
            self.cheat_console = CheatConsole(self.game_manager.cheat_system, self)
            self.cheat_console.console_closed.connect(self.on_cheat_console_closed)
            self.cheat_console.cheat_executed.connect(self.on_cheat_executed)
            print("AppWindow: Cheat console created")
        
        if self.cheat_console.isVisible():
            print("AppWindow: Closing cheat console")
            self.cheat_console.close_console()
        else:
            print("AppWindow: Showing cheat console")
            self.cheat_console.show_console()
    
    def on_cheat_console_closed(self):
        """Handle cheat console closed"""
        print("Cheat console closed")
    
    def on_cheat_executed(self, message, action_flag):
        """Handle cheat execution"""
        print(f"Cheat executed: {message}")
        
        # Handle special actions that need scene interaction
        if self.game_scene and self.game_scene.running:
            # Sync Score Display
            if action_flag == "SCORE_UPDATE":
                self.game_scene.score = self.game_manager.total_score
                self.game_scene.hud.update_score(self.game_scene.score)
                self.game_scene.hud.update_high_score(self.game_manager.high_score)
                self.game_scene.hud.show_bonus_message("CHEAT ACTIVATED!")
            
            # Level Cheats
            elif action_flag == "LEVEL_UP":
                self.game_scene.level_complete()
                
            elif action_flag == "SKIP_LEVEL":
                self.game_scene.level_complete()
            
            elif action_flag.startswith("GOTO_LEVEL"):
                level = int(action_flag.split(':')[1])
                self.game_scene.start_new_game(level)
            
            elif action_flag == "FREEZE_ORBS":
                if self.game_scene.chain:
                    self.game_scene.chain.freeze(30)
            elif action_flag == "SPAWN_POWERUP":
                if self.game_scene.chain:
                    from games.orb import OrbType
                    import random
                    powerup_type = random.choice([OrbType.BOMB, OrbType.SLOW, OrbType.REVERSE, OrbType.ACCURACY])
                    self.game_scene.chain.add_orb_at_distance(powerup_type, -100)
            elif action_flag == "ALL_POWERUPS":
                if self.game_scene.powerup_manager:
                    from games.orb import OrbType
                    for ptype in [OrbType.BOMB, OrbType.SLOW, OrbType.REVERSE, OrbType.ACCURACY]:
                        self.game_scene.powerup_manager.activate_powerup(ptype)
            elif action_flag == "BOMB_RAIN":
                if self.game_scene.chain:
                    from games.orb import OrbType
                    for i in range(10):
                        self.game_scene.chain.add_orb_at_distance(OrbType.BOMB, -100 - i * 50)
            elif action_flag == "CLEAR_ORBS":
                if self.game_scene.chain:
                    self.game_scene.chain.orbs.clear()
            
            elif action_flag == "RAINBOW_MODE":
                 if self.game_scene.chain:
                    from games.orb import OrbType
                    for orb in self.game_scene.chain.orbs:
                        orb.orb_type = OrbType.RAINBOW

            elif action_flag == "KONAMI_CODE":
                print("🎮 KONAMI CODE ACTIVATED! 🎮")
                if hasattr(self.game_manager, 'achievement_manager'):
                    self.game_manager.achievement_manager.unlock('developer_secret')