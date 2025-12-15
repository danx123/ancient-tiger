"""
Save and load game state management
"""

import json
import os
from pathlib import Path

class SaveManager:
    """Manages game save/load operations"""
    
    def __init__(self):
        self.save_dir = self._get_save_directory()
        self.save_file = self.save_dir / "save.json"
        
        # Ensure save directory exists
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_save_directory(self):
        """Get platform-specific save directory"""
        if os.name == 'nt':  # Windows
            appdata = os.getenv('APPDATA')
            if appdata:
                return Path(appdata) / "MacanAncient"
        
        # Fallback to user home
        return Path.home() / ".macanancient"
        
    def save_game(self, game_data):
        """Save game data to file"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(game_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
            
    def load_game(self):
        """Load game data from file"""
        try:
            if self.save_file.exists():
                with open(self.save_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading game: {e}")
        return None
        
    def delete_save(self):
        """Delete save file"""
        try:
            if self.save_file.exists():
                self.save_file.unlink()
            return True
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False