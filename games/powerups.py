"""
Orb entity with procedural rendering and physics
"""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QRadialGradient, QColor, QPen, QFont
from games.orb import Orb, OrbType
import math
import random

"""
Powerup management system
"""
from games.orb import Orb, OrbType  # <--- IMPORT DARI SINI
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
            self.slow_active = True
            self.slow_timer = 5.0 # 5 seconds
            self.scene._play_audio('play_power')
        elif powerup_type == OrbType.REVERSE:
            self.reverse_active = True
            self.reverse_timer = 3.0 # 3 seconds
            self.scene._play_audio('play_power')
        elif powerup_type == OrbType.ACCURACY:
            self.accuracy_active = True
            self.accuracy_timer = 10.0
            self.scene._play_audio('play_power')
            
    def _trigger_bomb(self, source_orb):
        """Explode orbs in a radius"""
        if not source_orb or not self.scene.chain:
            return
            
        self.scene._play_audio('play_game_over') # Use explosion sound
        self.scene.screen_shake = 0.5
        
        center_idx = -1
        # Find index of source orb
        for i, orb in enumerate(self.scene.chain.orbs):
            if orb == source_orb:
                center_idx = i
                break
                
        if center_idx != -1:
            # Mark neighbors for removal (Radius of 2 orbs each side)
            start = max(0, center_idx - 2)
            end = min(len(self.scene.chain.orbs), center_idx + 3)
            
            indices_to_remove = list(range(start, end))
            self.scene.chain.remove_orbs(indices_to_remove)
            
            # Add bonus score
            self.scene.score += len(indices_to_remove) * 50
            self.scene.hud.update_score(self.scene.score)

    def update(self, dt):
        """Update timers for active effects"""
        if self.slow_active:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_active = False
                
        if self.reverse_active:
            self.reverse_timer -= dt
            if self.reverse_timer <= 0:
                self.reverse_active = False
                
        if self.accuracy_active:
            self.accuracy_timer -= dt
            if self.accuracy_timer <= 0:
                self.accuracy_active = False

    def get_speed_multiplier(self):
        """Get current speed modifier based on active powerups"""
        multiplier = 1.0
        if self.slow_active:
            multiplier *= 0.3 # Slow down to 30%
        if self.reverse_active:
            multiplier *= -1.5 # Reverse at 1.5x speed
        return multiplier

class OrbType:
    """Orb types definition"""
    # Normal Colors
    RED = 0
    BLUE = 1
    GREEN = 2
    YELLOW = 3
    PURPLE = 4
    
    # Power Ups
    BOMB = 10
    SLOW = 11
    REVERSE = 12
    ACCURACY = 13 # Aim guide

class Orb:
    """Single orb entity"""
    
    ORB_COLORS = {
        OrbType.RED: (255, 50, 50),
        OrbType.BLUE: (50, 100, 255),
        OrbType.GREEN: (50, 255, 50),
        OrbType.YELLOW: (255, 255, 50),
        OrbType.PURPLE: (200, 50, 255),
        # Power Up Colors (Brighter/Distinct)
        OrbType.BOMB: (40, 40, 40),      # Dark Grey
        OrbType.SLOW: (100, 255, 255),   # Cyan
        OrbType.REVERSE: (255, 100, 255),# Magenta
        OrbType.ACCURACY: (255, 255, 255)# White
    }
    
    POWERUP_SYMBOLS = {
        OrbType.BOMB: "💣",
        OrbType.SLOW: "❄️",
        OrbType.REVERSE: "⏪",
        OrbType.ACCURACY: "🎯"
    }
    
    def __init__(self, x, y, orb_type, radius=15):
        self.pos = QPointF(x, y)
        self.orb_type = orb_type
        self.radius = radius
        self.velocity = QPointF(0, 0)
        
        # Animation
        self.pulse = 0
        self.marked_for_removal = False
        self.exploding = False
        self.explosion_progress = 0
        
    def is_powerup(self):
        """Check if this orb is a powerup"""
        return self.orb_type >= 10
        
    def update(self, dt):
        """Update orb state"""
        self.pulse += dt * 5  # Faster pulse for all
        
        if self.exploding:
            self.explosion_progress += dt * 5
            if self.explosion_progress >= 1.0:
                self.marked_for_removal = True
                
    def draw(self, painter):
        """Draw orb procedurally"""
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.exploding:
            self._draw_explosion(painter)
            return
            
        # Pulsing effect
        pulse_amount = 3 if self.is_powerup() else 1
        pulse_offset = math.sin(self.pulse) * pulse_amount
        current_radius = self.radius + pulse_offset
        
        # Draw Glow for Powerups
        if self.is_powerup():
            glow_gradient = QRadialGradient(self.pos, current_radius * 2.0)
            color = self.get_color()
            glow_color = QColor(*color)
            glow_color.setAlpha(150)
            glow_gradient.setColorAt(0, glow_color)
            glow_color.setAlpha(0)
            glow_gradient.setColorAt(1, glow_color)
            painter.setBrush(glow_gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self.pos, current_radius * 2.0, current_radius * 2.0)
        
        # Main orb body
        main_gradient = QRadialGradient(
            self.pos.x() - current_radius * 0.3,
            self.pos.y() - current_radius * 0.3,
            current_radius * 1.8
        )
        
        color_tuple = self.get_color()
        base_color = QColor(*color_tuple)
        light_color = base_color.lighter(150)
        dark_color = base_color.darker(150)
        
        main_gradient.setColorAt(0, light_color)
        main_gradient.setColorAt(0.5, base_color)
        main_gradient.setColorAt(1, dark_color)
        
        painter.setBrush(main_gradient)
        painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
        painter.drawEllipse(self.pos, current_radius, current_radius)
        
        # Draw Symbol for Powerups
        if self.is_powerup():
            symbol = self.POWERUP_SYMBOLS.get(self.orb_type, "?")
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Segoe UI Emoji", int(self.radius)) # Use Emoji font if available
            if not font.exactMatch():
                font = QFont("Arial", int(self.radius), QFont.Bold)
            
            painter.setFont(font)
            rect = QRectF(
                self.pos.x() - self.radius, 
                self.pos.y() - self.radius, 
                self.radius * 2, 
                self.radius * 2
            )
            painter.drawText(rect, Qt.AlignCenter, symbol)
            
    def _draw_explosion(self, painter):
        """Draw explosion effect"""
        progress = self.explosion_progress
        max_radius = self.radius * 4 if self.orb_type == OrbType.BOMB else self.radius * 2
        explosion_radius = max_radius * (0.2 + progress * 0.8)
        
        color = QColor(*self.get_color())
        color.setAlpha(int(255 * (1 - progress)))
        
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.pos, explosion_radius, explosion_radius)
            
    def get_color(self):
        """Get orb RGB color"""
        return self.ORB_COLORS.get(self.orb_type, (255, 255, 255))
        
    def matches(self, other):
        """Check if orbs match"""
        # Powerups match with NOTHING (they must be destroyed by generic explosion or simply clearing nearby)
        # OR implementation choice: Powerups take the color of the ball that hits them?
        # Let's stick to standard Zuma: You match the COLORS NEXT TO IT, and the gap close destroys it?
        # EASIER LOGIC: Powerups act as 'wildcards' or just match same type? 
        # IMPLEMENTATION: Powerups match themselves OR act as wildcard
        if self.is_powerup() or other.is_powerup():
            return False # Powerups don't form matches normally, they are triggered by radius/combo
        return self.orb_type == other.orb_type
        
    def explode(self):
        """Start explosion animation"""
        self.exploding = True
        
    @staticmethod
    def random_type():
        """Get random normal orb type"""
        return random.choice([
            OrbType.RED, OrbType.BLUE, OrbType.GREEN, 
            OrbType.YELLOW, OrbType.PURPLE
        ])
        
    @staticmethod
    def random_powerup():
        """Get random powerup type"""
        return random.choice([
            OrbType.BOMB, OrbType.SLOW, OrbType.REVERSE, OrbType.ACCURACY
        ])