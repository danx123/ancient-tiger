"""
Powerup management system
COMPLETE: All powerups fully implemented
"""
from games.orb import OrbType
import random

class PowerUpManager:
    """Manages active power-ups and their effects"""
    
    def __init__(self, scene):
        self.scene = scene
        
        # Status Effects
        self.slow_active = False
        self.slow_timer = 0
        self.reverse_active = False
        self.reverse_timer = 0
        self.accuracy_active = False
        self.accuracy_timer = 0
        
    def activate_powerup(self, powerup_type, source_orb=None):
        """Trigger a specific powerup effect"""
        print(f"PowerUp Activated: {powerup_type}")
        
        if powerup_type == OrbType.BOMB:
            self._trigger_bomb(source_orb)
        elif powerup_type == OrbType.SLOW:
            self._trigger_slow()
        elif powerup_type == OrbType.REVERSE:
            self._trigger_reverse()
        elif powerup_type == OrbType.ACCURACY:
            self._trigger_accuracy()
            
    def _trigger_bomb(self, source_orb):
        """Explode orbs in a radius around the bomb"""
        if not source_orb or not self.scene.chain:
            return
            
        print("PowerUp: BOMB activated!")
        self.scene._play_audio('play_game_over')  # Use explosion sound
        self.scene.screen_shake = 0.8
        
        center_idx = -1
        # Find index of source orb
        for i, orb in enumerate(self.scene.chain.orbs):
            if orb == source_orb:
                center_idx = i
                break
                
        if center_idx != -1:
            # Mark neighbors for removal (Radius of 3 orbs each side)
            start = max(0, center_idx - 3)
            end = min(len(self.scene.chain.orbs), center_idx + 4)
            
            indices_to_remove = list(range(start, end))
            print(f"PowerUp: BOMB removing {len(indices_to_remove)} orbs")
            
            self.scene.chain.remove_orbs(indices_to_remove)
            
            # Add bonus score
            bonus = len(indices_to_remove) * 50
            self.scene.score += bonus
            self.scene.hud.update_score(self.scene.score)
            
            # Check high score
            self.scene.parent_window.game_manager.check_high_score(self.scene.score)
    
    def _trigger_slow(self):
        """Freeze/slow down the chain"""
        print("PowerUp: SLOW/FREEZE activated!")
        self.slow_active = True
        self.slow_timer = 5.0  # 5 seconds
        self.scene._play_audio('play_power')
        
        # Optional: Actually freeze the chain
        if self.scene.chain:
            self.scene.chain.freeze(5.0)
    
    def _trigger_reverse(self):
        """Reverse chain direction temporarily"""
        print("PowerUp: REVERSE activated!")
        self.reverse_active = True
        self.reverse_timer = 3.0  # 3 seconds
        self.scene._play_audio('play_power')
    
    def _trigger_accuracy(self):
        """Show aim guide for better shooting"""
        print("PowerUp: ACCURACY activated!")
        self.accuracy_active = True
        self.accuracy_timer = 10.0  # 10 seconds
        self.scene._play_audio('play_power')

    def update(self, dt):
        """Update timers for active effects"""
        if self.slow_active:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_active = False
                print("PowerUp: SLOW expired")
                
        if self.reverse_active:
            self.reverse_timer -= dt
            if self.reverse_timer <= 0:
                self.reverse_active = False
                print("PowerUp: REVERSE expired")
                
        if self.accuracy_active:
            self.accuracy_timer -= dt
            if self.accuracy_timer <= 0:
                self.accuracy_active = False
                print("PowerUp: ACCURACY expired")

    def get_speed_multiplier(self):
        """Get current speed modifier based on active powerups"""
        multiplier = 1.0
        
        if self.slow_active:
            multiplier *= 0.3  # Slow down to 30% speed
            
        if self.reverse_active:
            multiplier *= -0.8  # Reverse at 80% speed (negative = backward)
            
        return multiplier
    
    def is_any_active(self):
        """Check if any powerup is currently active"""
        return self.slow_active or self.reverse_active or self.accuracy_active
