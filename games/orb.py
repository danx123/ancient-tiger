"""
Orb entity with procedural rendering and physics
FIXED: Added visible_scale for black hole effect
"""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QRadialGradient, QColor, QPen, QFont
import math
import random

class OrbType:
    """Orb color types"""
    # Normal Colors
    RED = 0
    BLUE = 1
    GREEN = 2
    YELLOW = 3
    PURPLE = 4
    
    # Special Types
    RAINBOW = 7
    
    # Power Ups (IDs >= 10)
    BOMB = 10
    SLOW = 11
    REVERSE = 12
    ACCURACY = 13 

class Orb:
    """Single orb entity"""
    
    ORB_COLORS = {
        OrbType.RED: (255, 50, 50),
        OrbType.BLUE: (50, 100, 255),
        OrbType.GREEN: (50, 255, 50),
        OrbType.YELLOW: (255, 255, 50),
        OrbType.PURPLE: (200, 50, 255),
        OrbType.RAINBOW: (255, 255, 255),
        
        # Power Up Colors
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
        self.radius = radius # Hitbox radius (tetap)
        self.velocity = QPointF(0, 0)
        
        # Visual scaling (untuk efek black hole)
        self.visible_scale = 1.0 
        
        # Animation
        self.pulse = 0
        self.glow_intensity = 0
        
        # State
        self.marked_for_removal = False
        self.exploding = False
        self.explosion_progress = 0
        
    def is_powerup(self):
        """Check if this orb is a powerup"""
        return self.orb_type >= 10
        
    def update(self, dt):
        """Update orb state"""
        self.pulse += dt * 3
        
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
            
        # Pulsing effect factored by visible_scale
        pulse_amount = 3 if self.is_powerup() else 2
        pulse_offset = math.sin(self.pulse) * pulse_amount
        
        # Hitung radius visual (bisa mengecil)
        current_radius = (self.radius + pulse_offset) * self.visible_scale
        
        # Jika scale terlalu kecil, jangan gambar detail
        if self.visible_scale < 0.1:
            return

        # --- Draw PowerUp Glow ---
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
        
        # --- Normal Outer Glow ---
        else:
            glow_gradient = QRadialGradient(self.pos, current_radius * 1.5)
            color = self.get_color()
            glow_color = QColor(*color)
            glow_color.setAlpha(80)
            glow_gradient.setColorAt(0, glow_color)
            glow_color.setAlpha(0)
            glow_gradient.setColorAt(1, glow_color)
            painter.setBrush(glow_gradient)
            painter.setPen(QPen(Qt.NoPen))
            painter.drawEllipse(self.pos, current_radius * 1.5, current_radius * 1.5)
        
        # --- Main orb body ---
        main_gradient = QRadialGradient(
            self.pos.x() - current_radius * 0.3,
            self.pos.y() - current_radius * 0.3,
            current_radius * 1.8
        )
        
        # Color Handling
        if self.orb_type == OrbType.RAINBOW:
            hue = (self.pulse * 50) % 360
            color = QColor.fromHsv(int(hue), 255, 255)
            light_color = QColor.fromHsv(int(hue), 180, 255)
            dark_color = QColor(color.red() // 2, color.green() // 2, color.blue() // 2)
        else:
            rgb = self.get_color()
            base_color = QColor(*rgb)
            light_color = base_color.lighter(150)
            dark_color = base_color.darker(150)
            color = base_color
        
        main_gradient.setColorAt(0, light_color)
        main_gradient.setColorAt(0.6, color)
        main_gradient.setColorAt(1, dark_color)
        
        painter.setBrush(main_gradient)
        painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
        painter.drawEllipse(self.pos, current_radius, current_radius)
        
        # --- Draw Symbol for Powerups ---
        if self.is_powerup():
            symbol = self.POWERUP_SYMBOLS.get(self.orb_type, "?")
            painter.setPen(QColor(255, 255, 255))
            
            # Font size scaled
            font_size = int(self.radius * self.visible_scale)
            if font_size > 1:
                font = QFont("Segoe UI Emoji", font_size) 
                if not font.exactMatch():
                    font = QFont("Arial", font_size, QFont.Bold)
                
                painter.setFont(font)
                rect = QRectF(
                    self.pos.x() - current_radius, 
                    self.pos.y() - current_radius, 
                    current_radius * 2, 
                    current_radius * 2
                )
                painter.drawText(rect, Qt.AlignCenter, symbol)

        # --- Highlight (Glossy effect) ---
        if not self.is_powerup():
            highlight_pos = QPointF(
                self.pos.x() - current_radius * 0.4,
                self.pos.y() - current_radius * 0.4
            )
            highlight_gradient = QRadialGradient(highlight_pos, current_radius * 0.4)
            highlight_color = QColor(255, 255, 255, 150)
            highlight_gradient.setColorAt(0, highlight_color)
            highlight_color.setAlpha(0)
            highlight_gradient.setColorAt(1, highlight_color)
            
            painter.setBrush(highlight_gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(highlight_pos, current_radius * 0.4, current_radius * 0.4)
            
    def _draw_explosion(self, painter):
        """Draw explosion effect"""
        progress = self.explosion_progress
        
        # Bigger explosion for Bomb
        scale_factor = 4 if self.orb_type == OrbType.BOMB else 3
        explosion_radius = self.radius * (1 + progress * scale_factor)
        
        for i in range(3):
            radius = explosion_radius * (1 - i * 0.3)
            gradient = QRadialGradient(self.pos, radius)
            
            color_rgb = self.get_color()
            explosion_color = QColor(*color_rgb)
            explosion_color.setAlpha(int(200 * (1 - progress)))
            gradient.setColorAt(0, explosion_color)
            
            explosion_color.setAlpha(0)
            gradient.setColorAt(1, explosion_color)
            
            painter.setBrush(gradient)
            painter.setPen(QPen(Qt.NoPen))
            painter.drawEllipse(self.pos, radius, radius)
            
    def get_color(self):
        """Get orb RGB color"""
        return self.ORB_COLORS.get(self.orb_type, (255, 255, 255))
        
    def matches(self, other):
        """Check if orbs match"""
        if self.is_powerup() or other.is_powerup():
            return False
            
        if self.orb_type == OrbType.RAINBOW or other.orb_type == OrbType.RAINBOW:
            return True
            
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
