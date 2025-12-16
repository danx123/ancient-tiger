"""
Player orb shooter with aiming and firing mechanics
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QPainter, QRadialGradient, QColor, QPen, QPainterPath
from games.orb import Orb
import math

class Shooter:
    """Player-controlled orb shooter"""
    
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
        self.projectile_speed = 600  # Even faster projectile for better response
        
        # Animation
        self.rotation_anim = 0
        
    def _generate_orbs(self):
        """Generate current and next orbs"""
        if not self.current_orb:
            self.current_orb = Orb(self.pos.x(), self.pos.y(), Orb.random_type(), 12)
        if not self.next_orb:
            self.next_orb = Orb(self.pos.x() + 40, self.pos.y(), Orb.random_type(), 10)
            
    def aim_at(self, target_pos):
        """Aim shooter at target position"""
        dx = target_pos.x() - self.pos.x()
        dy = target_pos.y() - self.pos.y()
        self.angle = math.atan2(dy, dx)
        
    def fire(self):
        """Fire current orb"""
        if self.current_orb and not self.projectile:
            # Create projectile
            self.projectile = Projectile(
                self.pos.x(),
                self.pos.y(),
                self.angle,
                self.current_orb.orb_type,
                self.projectile_speed
            )
            
            # Cycle orbs
            self.current_orb = self.next_orb
            self.current_orb.pos = self.pos
            self.current_orb.radius = 12
            
            self.next_orb = Orb(self.pos.x() + 40, self.pos.y(), Orb.random_type(), 10)
            
            # Return projectile and flag that sound should play
            return self.projectile
        return None
    
    def swap_orbs(self):
        """Swap current and next orb (right click function)"""
        if self.current_orb and self.next_orb and not self.projectile:
            # Swap the orbs
            self.current_orb, self.next_orb = self.next_orb, self.current_orb
            
            # Update positions and sizes
            self.current_orb.pos = self.pos
            self.current_orb.radius = 12
            
            self.next_orb.pos = QPointF(self.pos.x() + 40, self.pos.y())
            self.next_orb.radius = 10
        
    def update(self, dt):
        """Update shooter state"""
        self.rotation_anim += dt
        
        if self.current_orb:
            self.current_orb.update(dt)
        if self.next_orb:
            self.next_orb.update(dt)
            
        # Update projectile
        if self.projectile:
            self.projectile.update(dt)
            if self.projectile.out_of_bounds:
                self.projectile = None
                
    def draw(self, painter):
        """Draw shooter"""
        painter.setRenderHint(QPainter.Antialiasing)
        
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
        
        # Barrel gradient
        barrel_gradient = QRadialGradient(0, 0, barrel_width)
        barrel_gradient.setColorAt(0, QColor(160, 82, 45))
        barrel_gradient.setColorAt(1, QColor(101, 67, 33))
        
        painter.setBrush(barrel_gradient)
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawRect(0, -barrel_width/2, barrel_length, barrel_width)
        
        painter.restore()
        
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
            
    def _draw_aim_line(self, painter):
        """Draw aiming trajectory line"""
        line_length = 150
        end_x = self.pos.x() + math.cos(self.angle) * line_length
        end_y = self.pos.y() + math.sin(self.angle) * line_length
        
        # Dashed line
        pen = QPen(QColor(255, 255, 0, 100), 2, Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(self.pos, QPointF(end_x, end_y))


class Projectile:
    """Fired orb projectile"""
    
    def __init__(self, x, y, angle, orb_type, speed):
        self.orb = Orb(x, y, orb_type, 12)
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
        # Update position
        self.orb.pos += self.velocity * dt
        
        # Add to trail
        self.trail.append(QPointF(self.orb.pos))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
            
        # Check bounds
        if (self.orb.pos.x() < -50 or self.orb.pos.x() > 1100 or
            self.orb.pos.y() < -50 or self.orb.pos.y() > 850):
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
