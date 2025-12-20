"""
Manages game session data and progression
"""

from services.save_manager import SaveManager
from services.settings_manager import SettingsManager
from logic.score_system import ScoreSystem
from audio.audio_manager import AudioManager

class GameManager:
    """Manages overall game state and progression"""
    
    def __init__(self, parent):
        self.parent = parent
        self.save_manager = SaveManager()
        self.settings_manager = SettingsManager()
        self.score_system = ScoreSystem()
        
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
        
        # --- PERBAIKAN: Load High Score dari Settings ---
        self.high_score = self.settings_manager.get('high_score', 0)
        print(f"GameManager: High Score loaded: {self.high_score}")
        
    def new_game(self):
        """Start a new game"""
        self.current_level = 1
        self.total_score = 0
        self.lives = 5
        self.score_system.reset()
        
    def check_high_score(self, current_score):
        """Check and update high score immediately"""
        if current_score > self.high_score:
            self.high_score = current_score
            # Simpan otomatis ke settings agar tidak hilang
            self.settings_manager.set('high_score', self.high_score)
            return True
        return False
    
    # Reward 1 live
    def check_life_bonus(self, old_score, new_score):
        """Check if score crossed a 5000 point threshold"""
        bonus_threshold = 5000
        
        # Hitung kelipatan lama dan baru
        old_milestone = old_score // bonus_threshold
        new_milestone = new_score // bonus_threshold
        
        # Jika kelipatan baru lebih besar, berarti baru saja lewat 5000/10000/dst
        if new_milestone > old_milestone:
            lives_to_add = new_milestone - old_milestone
            self.lives += lives_to_add
            print(f"GameManager: BONUS LIFE! Score passed {new_milestone * bonus_threshold}. Lives: {self.lives}")
            # Simpan state agar jumlah nyawa aman jika crash/keluar
            self.save_game() 
            return True
            
        return False
        
    def load_game(self):
        """Load saved game"""
        data = self.save_manager.load_game()
        if data:
            self.current_level = data.get('level', 1)
            self.total_score = data.get('score', 0)
            self.lives = data.get('lives', 5)
            # Pastikan high score tetap sinkron jika save file lama
            self.check_high_score(self.total_score)
            return True
        return False
        
    def save_game(self):
        """Save current game state"""
        data = {
            'level': self.current_level,
            'score': self.total_score,
            'lives': self.lives
        }
        self.save_manager.save_game(data)
        
    def level_completed(self, current_total_score):
        """Handle level completion"""
        # --- PERBAIKAN: Update total score langsung dari scene ---
        self.total_score = current_total_score
        
        # Cek high score lagi saat level selesai
        self.check_high_score(self.total_score)
        
        print(f"GameManager: Level {self.current_level} completed. Total Score: {self.total_score}")
        
        self.current_level += 1
        print(f"GameManager: Next level: {self.current_level}")
        
        # Auto-save progress
        self.save_game()
        
    def level_failed(self):
        """Handle level failure"""
        print(f"GameManager: Level {self.current_level} failed")
        
        self.lives -= 1
        print(f"GameManager: Lives remaining: {self.lives}")
        
        if self.lives <= 0:
            print("GameManager: GAME OVER - No lives remaining")
            # Cek high score terakhir kali sebelum game over
            self.check_high_score(self.total_score)
            self.save_game()
            return True  # Game over
        
        self.save_game()
        return False  # Continue (retry level)
