"""
Save and load game state management using JSON in Local AppData
"""

import json
import os
import sys
from pathlib import Path

class SaveManager:
    """Manages game save/load operations"""
    
    def __init__(self):
        self.save_dir = self._get_save_directory()
        self.save_file = self.save_dir / "save.json"
        
        # Ensure save directory exists
        try:
            self.save_dir.mkdir(parents=True, exist_ok=True)
            print(f"SaveManager: Save directory is {self.save_dir}")
        except Exception as e:
            print(f"SaveManager: Error creating directory {e}")
        
    def _get_save_directory(self):
        """Get platform-specific local save directory"""
        app_name = "MacanAncient"
        
        if os.name == 'nt':  # Windows
            # Try LOCALAPPDATA first (Modern standard)
            local_app_data = os.getenv('LOCALAPPDATA')
            if local_app_data:
                return Path(local_app_data) / app_name
            
            # Fallback to APPDATA (Roaming)
            app_data = os.getenv('APPDATA')
            if app_data:
                return Path(app_data) / app_name
        
        # Linux / Mac / Fallback
        home = Path.home()
        xdg_data = os.getenv('XDG_DATA_HOME')
        
        if xdg_data:
            return Path(xdg_data) / app_name
            
        if sys.platform == 'darwin': # MacOS
            return home / "Library" / "Application Support" / app_name
            
        return home / ".local" / "share" / app_name
        
    def save_game(self, game_data):
        """Save game data to JSON file"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(game_data, f, indent=4)
            print(f"SaveManager: Game saved to {self.save_file}")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
            
    def load_game(self):
        """Load game data from JSON file"""
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
