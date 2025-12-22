"""
Cheat system for Ancient Tiger
Developer tools and cheats
"""

class CheatSystem:
    """Manages cheat codes and their effects"""
    
    # Cheat code definitions
    CHEAT_CODES = {
        # Lives & Health
        "GODMODE": {
            "description": "Infinite lives",
            "category": "Lives"
        },
        "MORELIVES": {
            "description": "Add 5 lives",
            "category": "Lives"
        },
        "MAXLIVES": {
            "description": "Set lives to 99",
            "category": "Lives"
        },
        
        # Score
        "RICHMAN": {
            "description": "Add 10000 points",
            "category": "Score"
        },
        "MILLIONAIRE": {
            "description": "Add 100000 points",
            "category": "Score"
        },
        "HIGHSCORE": {
            "description": "Set score to 999999",
            "category": "Score"
        },
        
        # Level
        "SKIPTHIS": {
            "description": "Skip current level",
            "category": "Level"
        },
        "LEVELUP": {
            "description": "Go to next level",
            "category": "Level"
        },
        "GOTOLEVEL": {
            "description": "Go to specific level (usage: GOTOLEVEL 10)",
            "category": "Level",
            "needs_param": True
        },
        "FINALLEVEL": {
            "description": "Jump to level 50",
            "category": "Level"
        },
        
        # Game Speed
        "SLOWMO": {
            "description": "Slow motion mode",
            "category": "Speed"
        },
        "TURBO": {
            "description": "Turbo mode (2x speed)",
            "category": "Speed"
        },
        "NORMALSPEED": {
            "description": "Reset speed to normal",
            "category": "Speed"
        },
        "FREEZEORBS": {
            "description": "Freeze orb chain for 30 seconds",
            "category": "Speed"
        },
        
        # Power-ups
        "POWERUP": {
            "description": "Spawn random powerup",
            "category": "Powerup"
        },
        "ALLPOWER": {
            "description": "Activate all powerups",
            "category": "Powerup"
        },
        "BOMBRAIN": {
            "description": "Spawn 10 bombs",
            "category": "Powerup"
        },
        
        # Orbs
        "CLEARORBS": {
            "description": "Clear all orbs instantly",
            "category": "Orbs"
        },
        "RAINBOW": {
            "description": "All orbs become rainbow",
            "category": "Orbs"
        },
        "NOSPAWN": {
            "description": "Stop orb spawning",
            "category": "Orbs"
        },
        
        # Achievement
        "UNLOCKALL": {
            "description": "Unlock all achievements",
            "category": "Achievement"
        },
        "RESETACH": {
            "description": "Reset all achievements",
            "category": "Achievement"
        },
        "GIVEACH": {
            "description": "Unlock specific achievement (usage: GIVEACH first_launch)",
            "category": "Achievement",
            "needs_param": True
        },
        
        # Debug
        "SHOWFPS": {
            "description": "Toggle FPS counter",
            "category": "Debug"
        },
        "SHOWPATH": {
            "description": "Show full path visualization",
            "category": "Debug"
        },
        "NOCLIP": {
            "description": "Orbs can't reach portal",
            "category": "Debug"
        },
        
        # Fun
        "PARTY": {
            "description": "Party mode (rainbow effects)",
            "category": "Fun"
        },
        "BIGHEAD": {
            "description": "Make orbs huge",
            "category": "Fun"
        },
        "TINY": {
            "description": "Make orbs tiny",
            "category": "Fun"
        },
        
        # Secret
        "KONAMI": {
            "description": "???",
            "category": "Secret"
        },
        "DEVELOPER": {
            "description": "Unlock developer achievement",
            "category": "Secret"
        }
    }
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.active_cheats = set()
        self.cheat_history = []
        
        # Cheat states
        self.god_mode = False
        self.speed_multiplier = 1.0
        self.no_spawn = False
        self.no_clip = False
        self.show_fps = False
        self.show_full_path = False
        self.party_mode = False
        self.orb_size_multiplier = 1.0
        
    def execute_cheat(self, cheat_input):
        """Execute cheat code"""
        # Parse input
        parts = cheat_input.strip().upper().split()
        if not parts:
            return False, "No cheat code entered"
        
        cheat_code = parts[0]
        param = parts[1] if len(parts) > 1 else None
        
        # Check if cheat exists
        if cheat_code not in self.CHEAT_CODES:
            return False, f"Unknown cheat: {cheat_code}"
        
        # Check if param needed
        cheat_info = self.CHEAT_CODES[cheat_code]
        if cheat_info.get('needs_param') and not param:
            return False, f"Missing parameter for {cheat_code}"
        
        # Execute cheat
        try:
            success, message = self._apply_cheat(cheat_code, param)
            
            if success:
                self.active_cheats.add(cheat_code)
                self.cheat_history.append(cheat_code)
                print(f"CheatSystem: {cheat_code} activated - {message}")
            
            return success, message
            
        except Exception as e:
            return False, f"Error executing cheat: {e}"
    
    def _apply_cheat(self, cheat_code, param):
        """Apply specific cheat effect"""
        
        # Lives & Health
        if cheat_code == "GODMODE":
            self.god_mode = not self.god_mode
            return True, f"God mode {'ON' if self.god_mode else 'OFF'}"
        
        elif cheat_code == "MORELIVES":
            self.game_manager.lives += 5
            return True, f"Lives: {self.game_manager.lives}"
        
        elif cheat_code == "MAXLIVES":
            self.game_manager.lives = 99
            return True, "Lives set to 99"
        
        # Score
        elif cheat_code == "RICHMAN":
            self.game_manager.total_score += 10000
            self.game_manager.check_high_score(self.game_manager.total_score)
            return True, "SCORE_UPDATE"
        
        elif cheat_code == "MILLIONAIRE":
            self.game_manager.total_score += 100000
            self.game_manager.check_high_score(self.game_manager.total_score)
            return True, "SCORE_UPDATE"
        
        elif cheat_code == "HIGHSCORE":
            self.game_manager.total_score = 999999
            self.game_manager.check_high_score(self.game_manager.total_score)
            return True, "SCORE_UPDATE"
        
        # Level
        elif cheat_code == "SKIPTHIS":
            return True, "SKIP_LEVEL"  # Special flag
        
        elif cheat_code == "LEVELUP":
            return True, "LEVEL_UP" # Changed to flag to trigger transition
        
        elif cheat_code == "GOTOLEVEL":
            try:
                target_level = int(param)
                if 1 <= target_level <= 50:
                    self.game_manager.current_level = target_level
                    return True, f"GOTO_LEVEL:{target_level}"
                else:
                    return False, "Level must be between 1-50"
            except ValueError:
                return False, "Invalid level number"
        
        elif cheat_code == "FINALLEVEL":
            self.game_manager.current_level = 50
            return True, "GOTO_LEVEL:50"
        
        # Speed
        elif cheat_code == "SLOWMO":
            self.speed_multiplier = 0.5
            return True, "Slow motion activated"
        
        elif cheat_code == "TURBO":
            self.speed_multiplier = 2.0
            return True, "Turbo mode activated"
        
        elif cheat_code == "NORMALSPEED":
            self.speed_multiplier = 1.0
            return True, "Speed normalized"
        
        elif cheat_code == "FREEZEORBS":
            return True, "FREEZE_ORBS"
        
        # Powerups
        elif cheat_code == "POWERUP":
            return True, "SPAWN_POWERUP"
        
        elif cheat_code == "ALLPOWER":
            return True, "ALL_POWERUPS"
        
        elif cheat_code == "BOMBRAIN":
            return True, "BOMB_RAIN"
        
        # Orbs
        elif cheat_code == "CLEARORBS":
            return True, "CLEAR_ORBS"
        
        elif cheat_code == "RAINBOW":
            return True, "RAINBOW_MODE"
        
        elif cheat_code == "NOSPAWN":
            self.no_spawn = not self.no_spawn
            return True, f"No spawn {'ON' if self.no_spawn else 'OFF'}"
        
        # Achievement
        elif cheat_code == "UNLOCKALL":
            if hasattr(self.game_manager, 'achievement_manager'):
                for ach_id in self.game_manager.achievement_manager.ACHIEVEMENTS:
                    self.game_manager.achievement_manager.unlock(ach_id)
                return True, "All achievements unlocked"
            return False, "Achievement system not available"
        
        elif cheat_code == "RESETACH":
            if hasattr(self.game_manager, 'achievement_manager'):
                self.game_manager.achievement_manager.unlocked = {}
                self.game_manager.achievement_manager.save_achievements()
                return True, "Achievements reset"
            return False, "Achievement system not available"
        
        elif cheat_code == "GIVEACH":
            if hasattr(self.game_manager, 'achievement_manager'):
                if self.game_manager.achievement_manager.unlock(param.lower()):
                    return True, f"Achievement unlocked: {param}"
                return False, f"Failed to unlock: {param}"
            return False, "Achievement system not available"
        
        # Debug
        elif cheat_code == "SHOWFPS":
            self.show_fps = not self.show_fps
            return True, f"FPS display {'ON' if self.show_fps else 'OFF'}"
        
        elif cheat_code == "SHOWPATH":
            self.show_full_path = not self.show_full_path
            return True, f"Full path {'ON' if self.show_full_path else 'OFF'}"
        
        elif cheat_code == "NOCLIP":
            self.no_clip = not self.no_clip
            return True, f"No clip {'ON' if self.no_clip else 'OFF'}"
        
        # Fun
        elif cheat_code == "PARTY":
            self.party_mode = not self.party_mode
            return True, f"Party mode {'ON' if self.party_mode else 'OFF'}"
        
        elif cheat_code == "BIGHEAD":
            self.orb_size_multiplier = 2.0
            return True, "Big orbs activated"
        
        elif cheat_code == "TINY":
            self.orb_size_multiplier = 0.5
            return True, "Tiny orbs activated"
        
        # Secret
        elif cheat_code == "KONAMI":
            return True, "KONAMI_CODE"
        
        elif cheat_code == "DEVELOPER":
            if hasattr(self.game_manager, 'achievement_manager'):
                self.game_manager.achievement_manager.unlock('developer_secret')
                return True, "Developer achievement unlocked"
            return False, "Achievement system not available"
        
        return False, "Cheat not implemented"
    
    def get_all_cheats_by_category(self):
        """Get cheats organized by category"""
        categories = {}
        for code, info in self.CHEAT_CODES.items():
            category = info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'code': code,
                'description': info['description'],
                'needs_param': info.get('needs_param', False)
            })
        return categories
    
    def is_active(self, cheat_code):
        """Check if cheat is active"""
        return cheat_code in self.active_cheats