"""
State management system for game flow
"""

from enum import Enum
from PySide6.QtCore import QObject, Signal

class GameState(Enum):
    """Game states"""
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    SETTINGS = "settings"

class StateManager(QObject):
    """Manages game state transitions"""
    
    state_changed = Signal(GameState)
    
    def __init__(self):
        super().__init__()
        self.current_state = GameState.MAIN_MENU
        self.previous_state = None
        
    def change_state(self, new_state):
        """Change to a new state"""
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_changed.emit(new_state)
            
    def return_to_previous(self):
        """Return to previous state"""
        if self.previous_state:
            self.change_state(self.previous_state)