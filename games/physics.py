"""
Physics utility functions and helpers
"""

import math
from PySide6.QtCore import QPointF

class Vector2D:
    """2D Vector utility class"""
    
    @staticmethod
    def magnitude(vec):
        """Calculate vector magnitude"""
        return math.sqrt(vec.x() ** 2 + vec.y() ** 2)
    
    @staticmethod
    def normalize(vec):
        """Normalize vector to unit length"""
        mag = Vector2D.magnitude(vec)
        if mag > 0:
            return QPointF(vec.x() / mag, vec.y() / mag)
        return QPointF(0, 0)
    
    @staticmethod
    def dot(vec1, vec2):
        """Dot product of two vectors"""
        return vec1.x() * vec2.x() + vec1.y() * vec2.y()
    
    @staticmethod
    def distance(pos1, pos2):
        """Distance between two points"""
        dx = pos2.x() - pos1.x()
        dy = pos2.y() - pos1.y()
        return math.sqrt(dx * dx + dy * dy)
    
    @staticmethod
    def angle_between(pos1, pos2):
        """Angle from pos1 to pos2 in radians"""
        dx = pos2.x() - pos1.x()
        dy = pos2.y() - pos1.y()
        return math.atan2(dy, dx)
    
    @staticmethod
    def lerp(start, end, t):
        """Linear interpolation between two points"""
        t = max(0, min(1, t))  # Clamp t to [0, 1]
        x = start.x() + (end.x() - start.x()) * t
        y = start.y() + (end.y() - start.y()) * t
        return QPointF(x, y)


class Easing:
    """Easing functions for smooth animations"""
    
    @staticmethod
    def ease_in_quad(t):
        """Quadratic ease in"""
        return t * t
    
    @staticmethod
    def ease_out_quad(t):
        """Quadratic ease out"""
        return t * (2 - t)
    
    @staticmethod
    def ease_in_out_quad(t):
        """Quadratic ease in-out"""
        return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t
    
    @staticmethod
    def ease_in_cubic(t):
        """Cubic ease in"""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t):
        """Cubic ease out"""
        return 1 + (t - 1) ** 3
    
    @staticmethod
    def elastic(t):
        """Elastic easing"""
        if t == 0 or t == 1:
            return t
        p = 0.3
        s = p / 4
        return math.pow(2, -10 * t) * math.sin((t - s) * (2 * math.pi) / p) + 1


class CurveGenerator:
    """Generate smooth curves for paths"""
    
    @staticmethod
    def bezier_curve(p0, p1, p2, p3, num_points=50):
        """Generate cubic Bezier curve points"""
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            
            # Cubic Bezier formula
            x = (1-t)**3 * p0.x() + \
                3 * (1-t)**2 * t * p1.x() + \
                3 * (1-t) * t**2 * p2.x() + \
                t**3 * p3.x()
                
            y = (1-t)**3 * p0.y() + \
                3 * (1-t)**2 * t * p1.y() + \
                3 * (1-t) * t**2 * p2.y() + \
                t**3 * p3.y()
                
            points.append(QPointF(x, y))
        return points
    
    @staticmethod
    def catmull_rom_curve(points, num_samples=20):
        """Generate Catmull-Rom spline through points"""
        if len(points) < 4:
            return points
            
        curve_points = []
        for i in range(len(points) - 3):
            p0, p1, p2, p3 = points[i:i+4]
            
            for j in range(num_samples):
                t = j / num_samples
                t2 = t * t
                t3 = t2 * t
                
                x = 0.5 * (
                    (2 * p1.x()) +
                    (-p0.x() + p2.x()) * t +
                    (2*p0.x() - 5*p1.x() + 4*p2.x() - p3.x()) * t2 +
                    (-p0.x() + 3*p1.x() - 3*p2.x() + p3.x()) * t3
                )
                
                y = 0.5 * (
                    (2 * p1.y()) +
                    (-p0.y() + p2.y()) * t +
                    (2*p0.y() - 5*p1.y() + 4*p2.y() - p3.y()) * t2 +
                    (-p0.y() + 3*p1.y() - 3*p2.y() + p3.y()) * t3
                )
                
                curve_points.append(QPointF(x, y))
                
        return curve_points