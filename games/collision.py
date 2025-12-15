"""
Collision detection and response system
"""

import math
from PySide6.QtCore import QPointF

class CollisionDetector:
    """Handles collision detection between projectiles and orb chain"""
    
    @staticmethod
    def check_collision(projectile, chain):
        """Check if projectile collides with any orb in chain"""
        if not projectile or not chain.orbs:
            return None
            
        proj_pos = projectile.orb.pos
        proj_radius = projectile.orb.radius
        
        # Check each orb in chain
        for i, orb in enumerate(chain.orbs):
            distance = CollisionDetector.distance_between(proj_pos, orb.pos)
            combined_radius = proj_radius + orb.radius
            
            if distance < combined_radius:
                return {
                    'index': i,
                    'orb': orb,
                    'projectile': projectile
                }
                
        return None
        
    @staticmethod
    def distance_between(pos1, pos2):
        """Calculate distance between two points"""
        dx = pos2.x() - pos1.x()
        dy = pos2.y() - pos1.y()
        return math.sqrt(dx * dx + dy * dy)
        
    @staticmethod
    def find_insertion_point(projectile, chain):
        """Find best insertion point for projectile in chain"""
        if not chain.orbs:
            return 0
            
        proj_pos = projectile.orb.pos
        
        # Find closest position in chain
        min_distance = float('inf')
        best_index = 0
        
        for i in range(len(chain.orbs) + 1):
            if i == 0:
                compare_pos = chain.orbs[0].pos if chain.orbs else proj_pos
            elif i == len(chain.orbs):
                compare_pos = chain.orbs[-1].pos
            else:
                # Check position between orbs
                pos1 = chain.orbs[i-1].pos
                pos2 = chain.orbs[i].pos
                compare_pos = QPointF(
                    (pos1.x() + pos2.x()) / 2,
                    (pos1.y() + pos2.y()) / 2
                )
                
            distance = CollisionDetector.distance_between(proj_pos, compare_pos)
            if distance < min_distance:
                min_distance = distance
                best_index = i
                
        return best_index