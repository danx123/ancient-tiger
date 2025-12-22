"""
Manages game session data and progression
"""

from services.save_manager import SaveManager
from services.settings_manager import SettingsManager
from logic.score_system import ScoreSystem
from audio.audio_manager import AudioManager
from services.achievement_system import AchievementManager
from services.achievement_tracker import AchievementTracker
from services.cheat_system import CheatSystem 

class GameManager:
    """Manages overall game state and progression"""
    
    def __init__(self, parent):
        self.parent = parent
        self.save_manager = SaveManager()
        self.settings_manager = SettingsManager()
        self.score_system = ScoreSystem()
        
       
        try:
            self.cheat_system = CheatSystem(self)
            print("GameManager: Cheat System initialized")
        except Exception as e:
            print(f"GameManager: Error initializing cheat system: {e}")
            self.cheat_system = None
        # --------------------------------------------
        
        # --- Inisialisasi Achievement System ---
        try:
            self.achievement_manager = AchievementManager()
            self.achievement_tracker = AchievementTracker(self.achievement_manager)
            print("GameManager: Achievement System initialized")
        except Exception as e:
            print(f"GameManager: Error initializing achievements: {e}")
            self.achievement_manager = None
            self.achievement_tracker = None
        
        print("GameManager: Initializing...")
        
        # Initialize audio manager
        try:
            self.audio_manager = AudioManager(self.settings_manager)
            print("GameManager: Audio Manager initialized successfully")
        except Exception as e:
            print(f"GameManager: ERROR initializing Audio Manager: {e}")
            self.audio_manager = None
        
        self.current_level = 1
        self.total_score = 0
        self.lives = 5
        
        self.high_score = self.settings_manager.get('high_score', 0)
        print(f"GameManager: High Score loaded: {self.high_score}")
        
    def new_game(self):
        """Start a new game"""
        self.current_level = 1
        self.total_score = 0
        self.lives = 5
        self.score_system.reset()
        
        # Reset tracker saat game baru
        if hasattr(self, 'achievement_tracker') and self.achievement_tracker:
            self.achievement_tracker.on_game_start()
            
    
    def check_high_score(self, current_score):
        if current_score > self.high_score:
            self.high_score = current_score
            self.settings_manager.set('high_score', self.high_score)
            return True
        return False
    
    def check_life_bonus(self, old_score, new_score):
        bonus_threshold = 5000
        old_milestone = old_score // bonus_threshold
        new_milestone = new_score // bonus_threshold
        
        if new_milestone > old_milestone:
            lives_to_add = new_milestone - old_milestone
            self.lives += lives_to_add
            print(f"GameManager: BONUS LIFE! Score passed {new_milestone * bonus_threshold}. Lives: {self.lives}")
            self.save_game() 
            return True
        return False
        
    def load_game(self):
        data = self.save_manager.load_game()
        if data:
            self.current_level = data.get('level', 1)
            self.total_score = data.get('score', 0)
            self.lives = data.get('lives', 5)
            self.check_high_score(self.total_score)
            return True
        return False
        
    def save_game(self):
        data = {
            'level': self.current_level,
            'score': self.total_score,
            'lives': self.lives
        }
        self.save_manager.save_game(data)
        
    def level_completed(self, current_total_score):
        self.total_score = current_total_score
        self.check_high_score(self.total_score)
        
        print(f"GameManager: Level {self.current_level} completed. Total Score: {self.total_score}")
        
        if hasattr(self, 'achievement_tracker') and self.achievement_tracker:
            self.achievement_tracker.on_level_complete(self.current_level)
            
        self.current_level += 1
        print(f"GameManager: Next level: {self.current_level}")
        self.save_game()
        
    def level_failed(self):
        print(f"GameManager: Level {self.current_level} failed")
        self.lives -= 1
        print(f"GameManager: Lives remaining: {self.lives}")
        
        if self.lives <= 0:
            print("GameManager: GAME OVER - No lives remaining")
            self.check_high_score(self.total_score)
            
            if hasattr(self, 'achievement_tracker') and self.achievement_tracker:
                self.achievement_tracker.on_game_over()
            
            self.save_game()
            return True 
        
        self.save_game()
        return False