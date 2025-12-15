"""
Combo system for chain reactions and score multipliers
"""

class ComboSystem:
    """Manages combo chains and multipliers"""
    
    def __init__(self):
        self.current_combo = 0
        self.combo_timer = 0
        self.combo_timeout = 2.0  # Seconds
        self.max_combo = 10
        
    def add_match(self, orbs_matched):
        """Add a match to combo chain"""
        self.current_combo += 1
        self.combo_timer = self.combo_timeout
        
        # Calculate multiplier
        multiplier = min(self.current_combo, self.max_combo)
        return multiplier
        
    def update(self, dt):
        """Update combo timer"""
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                self.reset()
                
    def reset(self):
        """Reset combo"""
        self.current_combo = 0
        self.combo_timer = 0
        
    def get_multiplier(self):
        """Get current combo multiplier"""
        return min(self.current_combo, self.max_combo)