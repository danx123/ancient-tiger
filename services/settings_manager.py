"""
Game settings management using JSON in Local AppData
UPDATED: Added factory_reset feature
"""

import json
import os
import sys
import shutil  
from pathlib import Path

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
            'fullscreen': True,
            'show_fps': False,
            'high_score': 0
        }
        
        # Ensure directory exists
        try:
            self.settings_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"SettingsManager: Error creating directory {e}")
        
        # Load settings
        self.load_settings()
        
    def _get_settings_directory(self):
        """Get platform-specific local settings directory"""
        app_name = "MacanAncient"
        
        if os.name == 'nt':  # Windows
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
        
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            # Pastikan folder ada sebelum menyimpan
            if not self.settings_dir.exists():
                self.settings_dir.mkdir(parents=True, exist_ok=True)
                
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
            
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
        except Exception as e:
            print(f"Error loading settings: {e}")
            
    def get(self, key, default=None):
        return self.settings.get(key, default)
        
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def factory_reset(self):
        """
        DANGER: Deletes ALL data in the app directory (Saves, Settings, Cache).
        Returns True if successful.
        """
        try:
            print(f"Factory Reset: Deleting {self.settings_dir}...")
            if self.settings_dir.exists():
                # Hapus seluruh folder dan isinya
                shutil.rmtree(self.settings_dir)
                
            # Buat ulang folder kosong agar tidak error saat close app
            self.settings_dir.mkdir(parents=True, exist_ok=True)
            
            # Reset variable settings ke default di memori
            self.__init__() 
            
            print("Factory Reset: Success.")
            return True
        except Exception as e:
            print(f"Factory Reset: Failed - {e}")
            return False