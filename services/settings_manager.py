"""
Game settings management
"""

import json
from pathlib import Path
import os

class SettingsManager:
    """Manages game settings"""
    
    def __init__(self):
        self.settings_dir = self._get_settings_directory()
        self.settings_file = self.settings_dir / "settings.json"
        
        # Default settings
        self.settings = {
            'music_enabled': True,
            'music_volume': 0.7,
            'sfx_enabled': True,
            'sfx_volume': 0.8,
            'fullscreen': False,
            'show_fps': False
        }
        
        # Ensure directory exists
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Load settings
        self.load_settings()
        
    def _get_settings_directory(self):
        """Get platform-specific settings directory"""
        if os.name == 'nt':  # Windows
            appdata = os.getenv('APPDATA')
            if appdata:
                return Path(appdata) / "MacanAncient"
        
        return Path.home() / ".macanancient"
        
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
            
    def load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
        except Exception as e:
            print(f"Error loading settings: {e}")
            
    def get(self, key, default=None):
        """Get setting value"""
        return self.settings.get(key, default)
        
    def set(self, key, value):
        """Set setting value"""
        self.settings[key] = value
        self.save_settings()