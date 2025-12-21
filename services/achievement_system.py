"""
Achievement system for Ancient Tiger
Complete achievement tracking and persistence
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import QObject, Signal

class AchievementManager(QObject):
    """Manages achievement unlocks and tracking"""
    
    achievement_unlocked = Signal(str, str, str)  # id, name, description
    
    # Achievement definitions with categories
    ACHIEVEMENTS = {
        # I. PROGRESS & EXPLORATION (Beginner-Friendly)
        "first_launch": {
            "name": "First Launch",
            "description": "Memulai perjalanan pertama",
            "category": "Progress",
            "icon": "🚀",
            "hidden": False
        },
        "into_portal": {
            "name": "Into the Portal",
            "description": "Masuk portal untuk pertama kali",
            "category": "Progress",
            "icon": "🌀",
            "hidden": False
        },
        "first_escape": {
            "name": "First Escape",
            "description": "Menyelesaikan Level 1",
            "category": "Progress",
            "icon": "⭐",
            "hidden": False
        },
        "orb_breaker": {
            "name": "Orb Breaker",
            "description": "Menghancurkan 50 Orb",
            "category": "Progress",
            "icon": "💥",
            "hidden": False
        },
        "orb_hunter": {
            "name": "Orb Hunter",
            "description": "Menghancurkan 250 Orb",
            "category": "Progress",
            "icon": "🎯",
            "hidden": False
        },
        "orb_annihilator": {
            "name": "Orb Annihilator",
            "description": "Menghancurkan 1000 Orb",
            "category": "Progress",
            "icon": "⚡",
            "hidden": False
        },
        "beyond_void": {
            "name": "Beyond the Void",
            "description": "Menyelesaikan Level 10",
            "category": "Progress",
            "icon": "🌟",
            "hidden": False
        },
        "edge_cosmos": {
            "name": "Edge of the Cosmos",
            "description": "Menyelesaikan Level 25",
            "category": "Progress",
            "icon": "🌌",
            "hidden": False
        },
        "dimension_master": {
            "name": "Master of the Dimension",
            "description": "Menyelesaikan Level 50",
            "category": "Progress",
            "icon": "👑",
            "hidden": False
        },
        
        # II. SKILL & COMBAT MASTERY
        "perfect_aim": {
            "name": "Perfect Aim",
            "description": "10 tembakan berturut-turut tanpa miss",
            "category": "Skill",
            "icon": "🎯",
            "hidden": False
        },
        "combo_apprentice": {
            "name": "Combo Apprentice",
            "description": "Mendapat Combo x5",
            "category": "Skill",
            "icon": "🔥",
            "hidden": False
        },
        "combo_master": {
            "name": "Combo Master",
            "description": "Mendapat Combo x10",
            "category": "Skill",
            "icon": "💫",
            "hidden": False
        },
        "unstoppable_chain": {
            "name": "Unstoppable Chain",
            "description": "Hancurkan 15 Orb dalam satu rangkaian",
            "category": "Skill",
            "icon": "⛓️",
            "hidden": False
        },
        "no_panic": {
            "name": "No Panic",
            "description": "Bertahan di danger state selama 5 detik",
            "category": "Skill",
            "icon": "😌",
            "hidden": False
        },
        "calm_pressure": {
            "name": "Calm Under Pressure",
            "description": "Bertahan di danger state selama 10 detik",
            "category": "Skill",
            "icon": "🧘",
            "hidden": False
        },
        "one_shot": {
            "name": "One Shot Survivor",
            "description": "Menyelesaikan level dengan 1 orb tersisa",
            "category": "Skill",
            "icon": "🎲",
            "hidden": False
        },
        
        # III. BLACK HOLE & PHYSICS
        "event_horizon": {
            "name": "Event Horizon",
            "description": "Mendekati black hole untuk pertama kali",
            "category": "Black Hole",
            "icon": "⚫",
            "hidden": False
        },
        "gravity_victim": {
            "name": "Gravity Victim",
            "description": "Kehilangan orb karena black hole",
            "category": "Black Hole",
            "icon": "💀",
            "hidden": False
        },
        "gravity_dancer": {
            "name": "Gravity Dancer",
            "description": "Selamat dari black hole tanpa kehilangan orb",
            "category": "Black Hole",
            "icon": "💃",
            "hidden": False
        },
        "slow_hero": {
            "name": "Slow Motion Hero",
            "description": "Bertahan saat slow-motion aktif",
            "category": "Black Hole",
            "icon": "⏱️",
            "hidden": False
        },
        "singularity_escape": {
            "name": "Singularity Escape",
            "description": "Menyelesaikan level dengan black hole aktif",
            "category": "Black Hole",
            "icon": "🌠",
            "hidden": False
        },
        "void_stares": {
            "name": "The Void Stares Back",
            "description": "Masuk black hole 10 kali (total)",
            "category": "Black Hole",
            "icon": "👁️",
            "hidden": False
        },
        
        # IV. LORE & STORY
        "child_guardian": {
            "name": "Child of the Guardian",
            "description": "Menyelesaikan Story Mode",
            "category": "Lore",
            "icon": "📜",
            "hidden": False
        },
        "ancient_awakens": {
            "name": "The Ancient Awakens",
            "description": "Menonton Story pertama kali",
            "category": "Lore",
            "icon": "📖",
            "hidden": False
        },
        "temple_echoes": {
            "name": "Echoes of the Temple",
            "description": "Menonton seluruh Story tanpa skip",
            "category": "Lore",
            "icon": "🏛️",
            "hidden": False
        },
        "chosen_tiger": {
            "name": "Chosen by the Tiger",
            "description": "Menyelesaikan Story + Level 25",
            "category": "Lore",
            "icon": "🐯",
            "hidden": False
        },
        "balance_keeper": {
            "name": "Keeper of Balance",
            "description": "Menyelesaikan Story + Level 50",
            "category": "Lore",
            "icon": "⚖️",
            "hidden": False
        },
        
        # V. ENDURANCE & DEDICATION
        "endless_traveler": {
            "name": "Endless Traveler",
            "description": "Bermain total 30 menit",
            "category": "Endurance",
            "icon": "🚶",
            "hidden": False
        },
        "cosmic_journey": {
            "name": "Cosmic Journey",
            "description": "Bermain total 1 jam",
            "category": "Endurance",
            "icon": "🌍",
            "hidden": False
        },
        "no_escape": {
            "name": "No Escape, Only Focus",
            "description": "Bermain 15 menit tanpa pause",
            "category": "Endurance",
            "icon": "🎮",
            "hidden": False
        },
        "return_void": {
            "name": "Return to the Void",
            "description": "Memulai game kembali setelah Game Over",
            "category": "Endurance",
            "icon": "🔄",
            "hidden": False
        },
        
        # VI. SECRET / HIDDEN
        "ancient_alliance": {
            "name": "The Ancient Alliance",
            "description": "Main 30 menit nonstop tanpa mati",
            "category": "Secret",
            "icon": "🤝",
            "hidden": True
        },
        "turtle_ascends": {
            "name": "The Turtle Ascends",
            "description": "Melihat kura-kura terbang di cutscene level tertentu",
            "category": "Secret",
            "icon": "🐢",
            "hidden": True
        },
        "tiger_watches": {
            "name": "The Tiger Watches",
            "description": "Diam 10 detik di main menu",
            "category": "Secret",
            "icon": "👀",
            "hidden": True
        },
        "developer_secret": {
            "name": "???",
            "description": "Achievement tersembunyi (developer only 😏)",
            "category": "Secret",
            "icon": "❓",
            "hidden": True
        },
        "complete_all": {
            "name": "The Black Hole Escape",
            "description": "Unlock semua achievement",
            "category": "Secret",
            "icon": "🏆",
            "hidden": True
        }
    }
    
    def __init__(self):
        super().__init__()
        self.save_dir = self._get_save_directory()
        self.achievement_file = self.save_dir / "achievements.json"
        
        # Tracking data
        self.unlocked = {}
        self.stats = {
            "orbs_destroyed": 0,
            "levels_completed": 0,
            "max_level_reached": 0,
            "max_combo": 0,
            "total_playtime": 0,
            "continuous_playtime": 0,
            "shots_fired": 0,
            "shots_hit": 0,
            "consecutive_hits": 0,
            "danger_time": 0,
            "black_hole_enters": 0,
            "story_viewed": False,
            "story_completed": False,
            "game_overs": 0,
            "idle_time": 0
        }
        
        # Ensure directory exists
        try:
            self.save_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"AchievementManager: Error creating directory {e}")
        
        self.load_achievements()
    
    def _get_save_directory(self):
        """Get platform-specific save directory"""
        app_name = "MacanAncient"
        
        if os.name == 'nt':
            local_app_data = os.getenv('LOCALAPPDATA')
            if local_app_data:
                return Path(local_app_data) / app_name
            app_data = os.getenv('APPDATA')
            if app_data:
                return Path(app_data) / app_name
        
        home = Path.home()
        xdg_data = os.getenv('XDG_DATA_HOME')
        
        if xdg_data:
            return Path(xdg_data) / app_name
        
        if sys.platform == 'darwin':
            return home / "Library" / "Application Support" / app_name
        
        return home / ".local" / "share" / app_name
    
    def load_achievements(self):
        """Load achievements from JSON"""
        try:
            if self.achievement_file.exists():
                with open(self.achievement_file, 'r') as f:
                    data = json.load(f)
                    self.unlocked = data.get('unlocked', {})
                    self.stats = data.get('stats', self.stats)
                    print(f"AchievementManager: Loaded {len(self.unlocked)} achievements")
        except Exception as e:
            print(f"AchievementManager: Error loading - {e}")
    
    def save_achievements(self):
        """Save achievements to JSON"""
        try:
            data = {
                'unlocked': self.unlocked,
                'stats': self.stats
            }
            with open(self.achievement_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"AchievementManager: Error saving - {e}")
    
    def unlock(self, achievement_id):
        """Unlock an achievement"""
        if achievement_id not in self.ACHIEVEMENTS:
            return False
        
        if achievement_id in self.unlocked:
            return False  # Already unlocked
        
        # Unlock it
        self.unlocked[achievement_id] = {
            'unlocked_at': datetime.now().isoformat(),
            'timestamp': datetime.now().timestamp()
        }
        
        achievement = self.ACHIEVEMENTS[achievement_id]
        print(f"🏆 ACHIEVEMENT UNLOCKED: {achievement['name']}")
        
        # Emit signal
        self.achievement_unlocked.emit(
            achievement_id,
            achievement['name'],
            achievement['description']
        )
        
        # Check if all achievements unlocked
        self.check_complete_all()
        
        self.save_achievements()
        return True
    
    def check_complete_all(self):
        """Check if all achievements are unlocked"""
        total = len(self.ACHIEVEMENTS) - 1  # Exclude "complete_all" itself
        unlocked_count = len([a for a in self.unlocked if a != "complete_all"])
        
        if unlocked_count >= total:
            self.unlock("complete_all")
    
    def is_unlocked(self, achievement_id):
        """Check if achievement is unlocked"""
        return achievement_id in self.unlocked
    
    def get_progress(self):
        """Get overall progress"""
        total = len(self.ACHIEVEMENTS)
        unlocked = len(self.unlocked)
        return unlocked, total, (unlocked / total) * 100
    
    def get_by_category(self, category):
        """Get achievements by category"""
        return {
            aid: data for aid, data in self.ACHIEVEMENTS.items()
            if data['category'] == category
        }
    
    def get_categories(self):
        """Get all unique categories"""
        return sorted(set(a['category'] for a in self.ACHIEVEMENTS.values()))