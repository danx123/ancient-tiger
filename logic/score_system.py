"""
Score calculation and management system
"""

class ScoreSystem:
    """Manages score calculation and tracking"""
    
    def __init__(self):
        self.total_score = 0
        self.level_score = 0
        self.high_score = 0
        
        # Score values
        self.orb_match_base = 10
        self.combo_bonus = 5
        
    def calculate_match_score(self, orbs_matched, combo_multiplier=1):
        """Calculate score for orb matches"""
        base_score = orbs_matched * self.orb_match_base
        combo_bonus = (combo_multiplier - 1) * self.combo_bonus * orbs_matched
        return int(base_score + combo_bonus)
        
    def add_score(self, points):
        """Add points to score"""
        self.total_score += points
        self.level_score += points
        
        if self.total_score > self.high_score:
            self.high_score = self.total_score
            
    def reset_level_score(self):
        """Reset level score"""
        self.level_score = 0
        
    def reset(self):
        """Reset all scores"""
        self.total_score = 0
        self.level_score = 0