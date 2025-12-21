"""
First run detection manager
"""

import os
import sys
from pathlib import Path

class FirstRunManager:
    """Manages first run detection"""
    
    def __init__(self):
        self.first_run_dir = self._get_first_run_directory()
        self.first_run_file = self.first_run_dir / ".firstrun"
        
        # Ensure directory exists
        try:
            self.first_run_dir.mkdir(parents=True, exist_ok=True)
            print(f"FirstRunManager: Directory is {self.first_run_dir}")
        except Exception as e:
            print(f"FirstRunManager: Error creating directory {e}")
    
    def _get_first_run_directory(self):
        """Get platform-specific directory (same as save/settings)"""
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
    
    def is_first_run(self):
        """Check if this is the first run"""
        return not self.first_run_file.exists()
    
    def mark_not_first_run(self):
        """Mark that the game has been run"""
        try:
            with open(self.first_run_file, 'w') as f:
                f.write("run")
            print(f"FirstRunManager: Marked as not first run")
            return True
        except Exception as e:
            print(f"FirstRunManager: Error marking first run - {e}")
            return False
    
    def reset_first_run(self):
        """Reset first run flag (for testing)"""
        try:
            if self.first_run_file.exists():
                self.first_run_file.unlink()
                print("FirstRunManager: First run flag reset")
            return True
        except Exception as e:
            print(f"FirstRunManager: Error resetting first run - {e}")
            return False