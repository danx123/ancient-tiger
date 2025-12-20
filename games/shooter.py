"""
Player orb shooter with aiming and firing mechanics
UPDATED: Shooter cannon uses shoot.png asset image
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QPainter, QRadialGradient, QColor, QPen, QPixmap, QTransform
from games.orb import Orb
import math
import os
import sys

class Shooter:
    """Player-controlled orb shooter"""
    
    # Class-level cache for shoot.png
    _shooter_image = None
    _image_loaded = False
    
    def __init__(self, x, y):
        self.pos = QPointF(x, y)
        self.angle = 0  # Radians
        self.radius = 25
        
        # Current and next orbs
        self.current_orb = None
        self.next_orb = None
        self._generate_orbs()
        
        # Projectile
        self.projectile = None
        self.projectile_speed = 800
        
        # Animation state
        self.reload_anim_progress = 1.0
        
        # Load shooter image if not already loaded
        if not Shooter._image_loaded:
            self._load_shooter_image()
    
    @classmethod
    def _load_shooter_image(cls):
        """Load shoot.png asset for the cannon (class method, loads once)"""
        cls._image_loaded = True
        
        # Try multiple locations
        shoot_paths = [
            "./ancient_gfx/shoot.png",
            os.path.join(os.path.dirname(__file__), "..", "shoot.png"),
        ]
        
        # Add PyInstaller frozen path
        if hasattr(sys, "_MEIPASS"):
            shoot_paths.insert(0, os.path.join(sys._MEIPASS, "shoot.png"))
        
        for path in shoot_paths:
            if os.path.exists(path):
                cls._shooter_image = QPixmap(path)
                if not cls._shooter_image.isNull():
                    print(f"Shooter: shoot.png loaded from {path}")
                    print(f"Shooter: Image size: {cls._shooter_image.width()}x{cls._shooter_image.height()}")
                    return
        
        print("Shooter: WARNING - shoot.png not found, will use fallback rendering")
        cls._shooter_image = None
        
    def _generate_orbs(self):
        """Generate current and next orbs"""
        if not self.current_orb:
            self.current_orb = Orb(self.pos.x(), self.pos.y(), Orb.random_type(), 12)
            self.current_orb.visible_scale = 1.0
        if not self.next_orb:
            self.next_orb = Orb(self.pos.x() + 40, self.pos.y(), Orb.random_type(), 10)
            self.next_orb.visible_scale = 0.8
            
    def aim_at(self, target_pos):
        """Aim shooter at target position"""
        dx = target_pos.x() - self.pos.x()
        dy = target_pos.y() - self.pos.y()
        self.angle = math.atan2(dy, dx)
        
    def fire(self):
        """Fire current orb"""
        if self.current_orb and not self.projectile:
            self.projectile = Projectile(
                self.pos.x(),
                self.pos.y(),
                self.angle,
                self.current_orb.orb_type,
                self.projectile_speed
            )
            
            # Reload mechanism
            self.current_orb = self.next_orb
            self.current_orb.pos = self.pos
            self.reload_anim_progress = 0.0
            
            self.next_orb = Orb(self.pos.x() + 40, self.pos.y(), Orb.random_type(), 10)
            self.next_orb.visible_scale = 0.0
            
            return self.projectile
            
        return None
    
    def swap_orbs(self):
        """Swap current and next orb"""
        if self.current_orb and self.next_orb and not self.projectile:
            self.current_orb, self.next_orb = self.next_orb, self.current_orb
            self.current_orb.pos = self.pos
            self.next_orb.pos = QPointF(self.pos.x() + 40, self.pos.y())
            self.reload_anim_progress = 0.5
        
    def update(self, dt):
        """Update shooter state"""
        if self.reload_anim_progress < 1.0:
            self.reload_anim_progress += dt * 5
            if self.reload_anim_progress > 1.0:
                self.reload_anim_progress = 1.0
        
        if self.current_orb:
            self.current_orb.radius = 12
            self.current_orb.visible_scale = self.reload_anim_progress
            self.current_orb.update(dt)
            
        if self.next_orb:
            target_scale = 0.8
            if self.next_orb.visible_scale < target_scale:
                self.next_orb.visible_scale = min(target_scale, self.next_orb.visible_scale + dt * 3)
            self.next_orb.update(dt)
            
        if self.projectile:
            self.projectile.update(dt)
            if self.projectile.out_of_bounds:
                self.projectile = None
                
    def draw(self, painter):
        """Draw shooter cannon with shoot.png or fallback"""
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Draw using shoot.png or fallback to procedural
        if Shooter._shooter_image and not Shooter._shooter_image.isNull():
            self._draw_with_image(painter)
        else:
            self._draw_fallback(painter)
        
        # Draw aim line
        self._draw_aim_line(painter)
        
        # Draw current orb
        if self.current_orb:
            self.current_orb.draw(painter)
            
        # Draw next orb indicator
        if self.next_orb:
            painter.save()
            painter.setOpacity(0.7)
            self.next_orb.draw(painter)
            painter.restore()
            
        # Draw projectile
        if self.projectile:
            self.projectile.draw(painter)
    
    def _draw_with_image(self, painter):
        """Draw shooter using shoot.png asset"""
        painter.save()
        
        # Move to shooter position
        painter.translate(self.pos)
        
        # Rotate to aim direction
        angle_degrees = math.degrees(self.angle)
        painter.rotate(angle_degrees)
        
        # Scale image to appropriate size
        # Assuming shoot.png shows the full cannon
        target_width = 120  # Adjust based on your image
        target_height = 80  # Adjust based on your image
        
        scaled_image = Shooter._shooter_image.scaled(
            target_width, target_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Draw image - pivot point should be at the back/center of cannon
        # Adjust offset based on your image's design
        offset_x = -20  # Negative = pivot point moves left (back of cannon)
        offset_y = -scaled_image.height() / 2  # Center vertically
        
        painter.drawPixmap(
            int(offset_x),
            int(offset_y),
            scaled_image
        )
        
        painter.restore()
    
    def _draw_fallback(self, painter):
        """Fallback: Draw procedural cannon if image not available"""
        # Draw base platform
        platform_width = 60
        platform_height = 15
        
        gradient = QRadialGradient(self.pos, platform_width)
        gradient.setColorAt(0, QColor(139, 69, 19))
        gradient.setColorAt(1, QColor(101, 67, 33))
        
        painter.setBrush(gradient)
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(
            self.pos.x() - platform_width/2,
            self.pos.y() - platform_height/2,
            platform_width,
            platform_height
        )
        
        # Draw cannon barrel
        barrel_length = 40
        barrel_width = 12
        
        painter.save()
        painter.translate(self.pos)
        painter.rotate(math.degrees(self.angle))
        
        barrel_gradient = QRadialGradient(0, 0, barrel_width)
        barrel_gradient.setColorAt(0, QColor(160, 82, 45))
        barrel_gradient.setColorAt(1, QColor(101, 67, 33))
        
        painter.setBrush(barrel_gradient)
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawRect(0, -barrel_width/2, barrel_length, barrel_width)
        
        painter.restore()
            
    def _draw_aim_line(self, painter):
        """Draw aiming trajectory line"""
        line_length = 150
        end_x = self.pos.x() + math.cos(self.angle) * line_length
        end_y = self.pos.y() + math.sin(self.angle) * line_length
        
        pen = QPen(QColor(255, 255, 0, 100), 2, Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(self.pos, QPointF(end_x, end_y))


class Projectile:
    """Fired orb projectile"""
    
    def __init__(self, x, y, angle, orb_type, speed):
        self.orb = Orb(x, y, orb_type, 13)
        self.orb.visible_scale = 1.0
        
        self.velocity = QPointF(
            math.cos(angle) * speed,
            math.sin(angle) * speed
        )
        self.out_of_bounds = False
        
        # Trail effect
        self.trail = []
        self.max_trail_length = 10
        
    def update(self, dt):
        """Update projectile position"""
        self.orb.visible_scale = 1.0
        
        # Update position
        self.orb.pos += self.velocity * dt
        
        # Add to trail
        self.trail.append(QPointF(self.orb.pos))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
            
        # Check bounds
        if (self.orb.pos.x() < -100 or self.orb.pos.x() > 1500 or 
            self.orb.pos.y() < -100 or self.orb.pos.y() > 1000):
            self.out_of_bounds = True
            
        self.orb.update(dt)
        
    def draw(self, painter):
        """Draw projectile with trail"""
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            radius = self.orb.radius * (i / len(self.trail))
            
            color = QColor(*self.orb.get_color())
            color.setAlpha(alpha)
            
            gradient = QRadialGradient(pos, radius)
            gradient.setColorAt(0, color)
            color.setAlpha(0)
            gradient.setColorAt(1, color)
            
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(pos, radius, radius)
            
        # Draw main orb
        self.orb.draw(painter)
