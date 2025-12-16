"""
Orb rendering cache system for optimal performance
Pre-renders orbs to QPixmap and caches them
"""

from PySide6.QtGui import QPixmap, QPainter, QRadialGradient, QColor, QPen, QFont
from PySide6.QtCore import Qt, QRectF, QPointF
from games.orb import OrbType
import math

class OrbRenderCache:
    """Cache system for pre-rendered orb images"""
    
    def __init__(self):
        self.cache = {}  # Key: (orb_type, radius, pulse_frame) -> QPixmap
        self.pulse_frames = 8  # Number of pulse animation frames
        self.enable_cache = True
        
        print("OrbRenderCache: Initializing...")
        self._prerender_all_orbs()
        print(f"OrbRenderCache: Cached {len(self.cache)} orb variations")
    
    def _prerender_all_orbs(self):
        """Pre-render all orb types and variations"""
        # Normal orb types
        normal_types = [
            OrbType.RED, OrbType.BLUE, OrbType.GREEN, 
            OrbType.YELLOW, OrbType.PURPLE, OrbType.RAINBOW
        ]
        
        # Powerup types
        powerup_types = [
            OrbType.BOMB, OrbType.SLOW, 
            OrbType.REVERSE, OrbType.ACCURACY
        ]
        
        # Common sizes
        sizes = [10, 12, 15]  # next_orb, current_orb, chain_orb
        
        # Pre-render normal orbs with pulse animation
        for orb_type in normal_types:
            for radius in sizes:
                for pulse_frame in range(self.pulse_frames):
                    self._render_orb(orb_type, radius, pulse_frame)
        
        # Pre-render powerups (they have different pulse)
        for orb_type in powerup_types:
            for radius in sizes:
                for pulse_frame in range(self.pulse_frames):
                    self._render_orb(orb_type, radius, pulse_frame, is_powerup=True)
    
    def _render_orb(self, orb_type, radius, pulse_frame=0, is_powerup=False):
        """Render single orb to QPixmap and cache it"""
        cache_key = (orb_type, radius, pulse_frame)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Calculate pulse offset
        pulse_progress = pulse_frame / self.pulse_frames
        pulse_amount = 3 if is_powerup else 2
        pulse_offset = math.sin(pulse_progress * 2 * math.pi) * pulse_amount
        current_radius = radius + pulse_offset
        
        # Create pixmap with extra space for glow
        size = int(current_radius * 4)
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center position
        center = QPointF(size / 2, size / 2)
        
        # --- Draw PowerUp Glow ---
        if is_powerup:
            glow_gradient = QRadialGradient(center, current_radius * 2.0)
            color = self._get_orb_color(orb_type)
            glow_color = QColor(*color)
            glow_color.setAlpha(150)
            glow_gradient.setColorAt(0, glow_color)
            glow_color.setAlpha(0)
            glow_gradient.setColorAt(1, glow_color)
            painter.setBrush(glow_gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, current_radius * 2.0, current_radius * 2.0)
        
        # --- Normal Outer Glow ---
        else:
            glow_gradient = QRadialGradient(center, current_radius * 1.5)
            color = self._get_orb_color(orb_type)
            glow_color = QColor(*color)
            glow_color.setAlpha(80)
            glow_gradient.setColorAt(0, glow_color)
            glow_color.setAlpha(0)
            glow_gradient.setColorAt(1, glow_color)
            painter.setBrush(glow_gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, current_radius * 1.5, current_radius * 1.5)
        
        # --- Main orb body ---
        main_gradient = QRadialGradient(
            center.x() - current_radius * 0.3,
            center.y() - current_radius * 0.3,
            current_radius * 1.8
        )
        
        # Color Handling
        if orb_type == OrbType.RAINBOW:
            # For rainbow, use pulse_frame for color cycling
            hue = (pulse_frame * 45) % 360
            color = QColor.fromHsv(int(hue), 255, 255)
            light_color = QColor.fromHsv(int(hue), 180, 255)
            dark_color = QColor(color.red() // 2, color.green() // 2, color.blue() // 2)
        else:
            rgb = self._get_orb_color(orb_type)
            base_color = QColor(*rgb)
            light_color = base_color.lighter(150)
            dark_color = base_color.darker(150)
            color = base_color
        
        main_gradient.setColorAt(0, light_color)
        main_gradient.setColorAt(0.6, color)
        main_gradient.setColorAt(1, dark_color)
        
        painter.setBrush(main_gradient)
        painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
        painter.drawEllipse(center, current_radius, current_radius)
        
        # --- Draw Symbol for Powerups ---
        if is_powerup:
            symbol = self._get_powerup_symbol(orb_type)
            painter.setPen(QColor(255, 255, 255))
            
            font_size = int(radius)
            if font_size > 1:
                font = QFont("Segoe UI Emoji", font_size)
                if not font.exactMatch():
                    font = QFont("Arial", font_size, QFont.Bold)
                
                painter.setFont(font)
                rect = QRectF(
                    center.x() - current_radius,
                    center.y() - current_radius,
                    current_radius * 2,
                    current_radius * 2
                )
                painter.drawText(rect, Qt.AlignCenter, symbol)
        
        # --- Highlight (Glossy effect) ---
        if not is_powerup:
            highlight_pos = QPointF(
                center.x() - current_radius * 0.4,
                center.y() - current_radius * 0.4
            )
            highlight_gradient = QRadialGradient(highlight_pos, current_radius * 0.4)
            highlight_color = QColor(255, 255, 255, 150)
            highlight_gradient.setColorAt(0, highlight_color)
            highlight_color.setAlpha(0)
            highlight_gradient.setColorAt(1, highlight_color)
            
            painter.setBrush(highlight_gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(highlight_pos, current_radius * 0.4, current_radius * 0.4)
        
        painter.end()
        
        # Cache it
        self.cache[cache_key] = pixmap
        return pixmap
    
    def get_orb_pixmap(self, orb_type, radius, pulse_time, visible_scale=1.0):
        """
        Get cached orb pixmap
        
        Args:
            orb_type: Type of orb
            radius: Base radius
            pulse_time: Animation time for pulse
            visible_scale: Scale factor (for black hole effect)
        
        Returns:
            QPixmap or None
        """
        if not self.enable_cache:
            return None
        
        # Calculate pulse frame
        pulse_frame = int((pulse_time * 3) % self.pulse_frames)
        
        # Get cached pixmap
        cache_key = (orb_type, radius, pulse_frame)
        pixmap = self.cache.get(cache_key)
        
        if pixmap and visible_scale != 1.0:
            # Scale for black hole effect
            new_size = int(pixmap.width() * visible_scale)
            if new_size < 1:
                return None
            pixmap = pixmap.scaled(
                new_size, new_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        
        return pixmap
    
    def _get_orb_color(self, orb_type):
        """Get RGB color for orb type"""
        colors = {
            OrbType.RED: (255, 50, 50),
            OrbType.BLUE: (50, 100, 255),
            OrbType.GREEN: (50, 255, 50),
            OrbType.YELLOW: (255, 255, 50),
            OrbType.PURPLE: (200, 50, 255),
            OrbType.RAINBOW: (255, 255, 255),
            OrbType.BOMB: (40, 40, 40),
            OrbType.SLOW: (100, 255, 255),
            OrbType.REVERSE: (255, 100, 255),
            OrbType.ACCURACY: (255, 255, 255)
        }
        return colors.get(orb_type, (255, 255, 255))
    
    def _get_powerup_symbol(self, orb_type):
        """Get symbol for powerup type"""
        symbols = {
            OrbType.BOMB: "💣",
            OrbType.SLOW: "❄️",
            OrbType.REVERSE: "⏪",
            OrbType.ACCURACY: "🎯"
        }
        return symbols.get(orb_type, "?")
    
    def clear_cache(self):
        """Clear all cached pixmaps"""
        self.cache.clear()
        print("OrbRenderCache: Cache cleared")
    
    def get_cache_info(self):
        """Get cache statistics"""
        return {
            'total_cached': len(self.cache),
            'enabled': self.enable_cache,
            'pulse_frames': self.pulse_frames
        }


# Global cache instance
_orb_cache = None

def get_orb_cache():
    """Get global orb cache instance"""
    global _orb_cache
    if _orb_cache is None:
        _orb_cache = OrbRenderCache()
    return _orb_cache


class ExplosionCache:
    """Cache for explosion effects"""
    
    def __init__(self):
        self.cache = {}
        self.explosion_frames = 10
        print("ExplosionCache: Initializing...")
        self._prerender_explosions()
        print(f"ExplosionCache: Cached {len(self.cache)} explosion frames")
    
    def _prerender_explosions(self):
        """Pre-render explosion frames"""
        # Explosion types
        explosion_types = [
            OrbType.RED, OrbType.BLUE, OrbType.GREEN,
            OrbType.YELLOW, OrbType.PURPLE, OrbType.BOMB
        ]
        
        for orb_type in explosion_types:
            for frame in range(self.explosion_frames):
                self._render_explosion(orb_type, 15, frame)
    
    def _render_explosion(self, orb_type, base_radius, frame):
        """Render single explosion frame"""
        cache_key = (orb_type, frame)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        progress = frame / self.explosion_frames
        
        # Bigger explosion for Bomb
        scale_factor = 4 if orb_type == OrbType.BOMB else 3
        explosion_radius = base_radius * (1 + progress * scale_factor)
        
        size = int(explosion_radius * 3)
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = QPointF(size / 2, size / 2)
        
        # Draw explosion rings
        for i in range(3):
            radius = explosion_radius * (1 - i * 0.3)
            gradient = QRadialGradient(center, radius)
            
            color_rgb = self._get_explosion_color(orb_type)
            explosion_color = QColor(*color_rgb)
            explosion_color.setAlpha(int(200 * (1 - progress)))
            gradient.setColorAt(0, explosion_color)
            
            explosion_color.setAlpha(0)
            gradient.setColorAt(1, explosion_color)
            
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, radius, radius)
        
        painter.end()
        
        self.cache[cache_key] = pixmap
        return pixmap
    
    def get_explosion_pixmap(self, orb_type, explosion_progress):
        """Get cached explosion frame"""
        frame = int(explosion_progress * self.explosion_frames)
        frame = min(frame, self.explosion_frames - 1)
        
        cache_key = (orb_type, frame)
        return self.cache.get(cache_key)
    
    def _get_explosion_color(self, orb_type):
        """Get color for explosion"""
        colors = {
            OrbType.RED: (255, 50, 50),
            OrbType.BLUE: (50, 100, 255),
            OrbType.GREEN: (50, 255, 50),
            OrbType.YELLOW: (255, 255, 50),
            OrbType.PURPLE: (200, 50, 255),
            OrbType.BOMB: (255, 100, 0)
        }
        return colors.get(orb_type, (255, 255, 255))


# Global explosion cache
_explosion_cache = None

def get_explosion_cache():
    """Get global explosion cache instance"""
    global _explosion_cache
    if _explosion_cache is None:
        _explosion_cache = ExplosionCache()
    return _explosion_cache


class TrailCache:
    """Cache for projectile trail effects"""
    
    def __init__(self):
        self.cache = {}
        self.trail_steps = 10
        print("TrailCache: Initializing...")
        self._prerender_trails()
        print(f"TrailCache: Cached {len(self.cache)} trail segments")
    
    def _prerender_trails(self):
        """Pre-render trail segments"""
        trail_types = [
            OrbType.RED, OrbType.BLUE, OrbType.GREEN,
            OrbType.YELLOW, OrbType.PURPLE, OrbType.RAINBOW
        ]
        
        for orb_type in trail_types:
            for step in range(self.trail_steps):
                self._render_trail(orb_type, 12, step)
    
    def _render_trail(self, orb_type, base_radius, step):
        """Render single trail segment"""
        cache_key = (orb_type, step)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        alpha = int(255 * (step / self.trail_steps))
        radius = base_radius * (step / self.trail_steps)
        
        if radius < 1:
            return None
        
        size = int(radius * 4)
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = QPointF(size / 2, size / 2)
        
        color_rgb = self._get_trail_color(orb_type)
        color = QColor(*color_rgb)
        color.setAlpha(alpha)
        
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, color)
        color.setAlpha(0)
        gradient.setColorAt(1, color)
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)
        
        painter.end()
        
        self.cache[cache_key] = pixmap
        return pixmap
    
    def get_trail_pixmap(self, orb_type, progress):
        """Get cached trail segment"""
        step = int(progress * self.trail_steps)
        step = min(step, self.trail_steps - 1)
        
        cache_key = (orb_type, step)
        return self.cache.get(cache_key)
    
    def _get_trail_color(self, orb_type):
        """Get color for trail"""
        colors = {
            OrbType.RED: (255, 50, 50),
            OrbType.BLUE: (50, 100, 255),
            OrbType.GREEN: (50, 255, 50),
            OrbType.YELLOW: (255, 255, 50),
            OrbType.PURPLE: (200, 50, 255),
            OrbType.RAINBOW: (255, 255, 255)
        }
        return colors.get(orb_type, (255, 255, 255))


# Global trail cache
_trail_cache = None

def get_trail_cache():
    """Get global trail cache instance"""
    global _trail_cache
    if _trail_cache is None:
        _trail_cache = TrailCache()
    return _trail_cache