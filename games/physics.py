"""
Physics utility functions and helpers
MIGRATED: Core math now runs in Rust (zuma_core) with automatic pure-Python
fallback (zuma_core_fallback) if the compiled wheel isn't installed.
Public API (Vector2D / Easing / CurveGenerator, QPointF in/out) is unchanged
so scene.py, shooter.py, chain.py, etc. need ZERO changes.
"""

from PySide6.QtCore import QPointF
from games.zuma_bridge import core


class Vector2D:
    """2D Vector utility class"""

    @staticmethod
    def magnitude(vec):
        """Calculate vector magnitude"""
        return core.vec_magnitude(vec.x(), vec.y())

    @staticmethod
    def normalize(vec):
        """Normalize vector to unit length"""
        x, y = core.vec_normalize(vec.x(), vec.y())
        return QPointF(x, y)

    @staticmethod
    def dot(vec1, vec2):
        """Dot product of two vectors"""
        return core.vec_dot(vec1.x(), vec1.y(), vec2.x(), vec2.y())

    @staticmethod
    def distance(pos1, pos2):
        """Distance between two points"""
        return core.vec_distance(pos1.x(), pos1.y(), pos2.x(), pos2.y())

    @staticmethod
    def angle_between(pos1, pos2):
        """Angle from pos1 to pos2 in radians"""
        return core.vec_angle_between(pos1.x(), pos1.y(), pos2.x(), pos2.y())

    @staticmethod
    def lerp(start, end, t):
        """Linear interpolation between two points"""
        x, y = core.vec_lerp(start.x(), start.y(), end.x(), end.y(), t)
        return QPointF(x, y)


class Easing:
    """Easing functions for smooth animations"""

    @staticmethod
    def ease_in_quad(t):
        return core.ease_in_quad(t)

    @staticmethod
    def ease_out_quad(t):
        return core.ease_out_quad(t)

    @staticmethod
    def ease_in_out_quad(t):
        return core.ease_in_out_quad(t)

    @staticmethod
    def ease_in_cubic(t):
        return core.ease_in_cubic(t)

    @staticmethod
    def ease_out_cubic(t):
        return core.ease_out_cubic(t)

    @staticmethod
    def elastic(t):
        return core.elastic(t)


class CurveGenerator:
    """Generate smooth curves for paths"""

    @staticmethod
    def bezier_curve(p0, p1, p2, p3, num_points=50):
        """Generate cubic Bezier curve points"""
        raw = core.bezier_curve(
            (p0.x(), p0.y()), (p1.x(), p1.y()),
            (p2.x(), p2.y()), (p3.x(), p3.y()),
            num_points,
        )
        return [QPointF(x, y) for x, y in raw]

    @staticmethod
    def catmull_rom_curve(points, num_samples=20):
        """Generate Catmull-Rom spline through points"""
        if len(points) < 4:
            return points
        raw_points = [(p.x(), p.y()) for p in points]
        raw = core.catmull_rom_curve(raw_points, num_samples)
        return [QPointF(x, y) for x, y in raw]
