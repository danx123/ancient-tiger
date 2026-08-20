"""
Collision detection and response system
MIGRATED: Hot-path math now runs in Rust (zuma_core) with automatic
pure-Python fallback if the compiled wheel isn't installed. Public API
unchanged (CollisionDetector.check_collision / find_insertion_point,
QPointF in, dict out) so scene.py needs ZERO changes.
"""

from games.zuma_bridge import core


class CollisionDetector:
    """Handles collision detection between projectiles and orb chain"""

    @staticmethod
    def check_collision(projectile, chain):
        """Check if projectile collides with any orb in chain"""
        if not projectile or not chain.orbs:
            return None

        proj_pos = projectile.orb.pos
        proj_radius = projectile.orb.radius

        orb_tuples = [(orb.pos.x(), orb.pos.y(), orb.radius) for orb in chain.orbs]
        index = core.check_collision(proj_pos.x(), proj_pos.y(), proj_radius, orb_tuples)

        if index is None:
            return None

        return {
            'index': index,
            'orb': chain.orbs[index],
            'projectile': projectile,
        }

    @staticmethod
    def distance_between(pos1, pos2):
        """Calculate distance between two points"""
        return core.distance_between((pos1.x(), pos1.y()), (pos2.x(), pos2.y()))

    @staticmethod
    def find_insertion_point(projectile, chain):
        """Find best insertion point for projectile in chain"""
        if not chain.orbs:
            return 0

        proj_pos = projectile.orb.pos
        orb_positions = [(orb.pos.x(), orb.pos.y()) for orb in chain.orbs]
        return core.find_insertion_point(proj_pos.x(), proj_pos.y(), orb_positions)
