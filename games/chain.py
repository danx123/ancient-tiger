"""
Orb chain management and movement along path
MIGRATED: Path generation/lookup, spacing maintenance, and match detection
now run in Rust (zuma_core) with automatic pure-Python fallback if the
compiled wheel isn't installed. Public API (OrbChain / Path, QPointF in/out)
is unchanged so scene.py needs ZERO changes.
"""

from PySide6.QtCore import QPointF
from games.orb import Orb, OrbType
from games.zuma_bridge import core
import random

class OrbChain:
    """Manages chain of orbs moving along a path"""
    
    def __init__(self, path, level=1):
        self.path = path
        self.orbs = []
        
        # Cap level at 50
        self.level = min(level, 50)
        
        # TUNED: Speed scaling with better progression
        # Level 1-10: Gradual increase (beginner friendly)
        # Level 11-25: Moderate increase (intermediate)
        # Level 26-40: Slower increase (expert)
        # Level 41-50: Minimal increase (master)
        if self.level <= 10:
            # Base speed 12, increase 1.5 per level
            # Level 1: 13.5, Level 10: 27
            self.speed = 12 + self.level * 1.5
        elif self.level <= 25:
            # Continue from level 10 (27), increase 1.2 per level
            # Level 11: 28.2, Level 25: 46.2
            base = 12 + 10 * 1.5
            self.speed = base + (self.level - 10) * 1.2
        elif self.level <= 40:
            # Continue from level 25 (46.2), increase 0.8 per level
            # Level 26: 47, Level 40: 59
            base = 12 + 10 * 1.5 + 15 * 1.2
            self.speed = base + (self.level - 25) * 0.8
        else:
            # Continue from level 40 (59), increase 0.5 per level
            # Level 41: 59.5, Level 50: 64
            base = 12 + 10 * 1.5 + 15 * 1.2 + 15 * 0.8
            self.speed = base + (self.level - 40) * 0.5
        
        # Spawn timer initialization
        self.spawn_timer = 0
        
        # TUNED: Spawn interval with smoother scaling
        if self.level <= 10:
            # Level 1: 2.5s, Level 10: 1.7s
            self.spawn_interval = 2.5 - (self.level * 0.08)
        elif self.level <= 20:
            # Level 11: 1.65s, Level 20: 1.15s
            self.spawn_interval = 1.7 - ((self.level - 10) * 0.05)
        elif self.level <= 35:
            # Level 21: 1.12s, Level 35: 0.82s
            self.spawn_interval = 1.15 - ((self.level - 20) * 0.02)
        else:
            # Level 36+: Cap at 0.7s (not too crazy)
            self.spawn_interval = 0.7
        
        self.spawn_interval = max(self.spawn_interval, 0.6)
        self.distance_between_orbs = 34
        self.frozen = False
        self.freeze_timer = 0
        
        # Powerup spawn system
        self.powerup_chance = 0.12
        self.orbs_since_last_powerup = 0
        self.guaranteed_powerup_after = 15
        
        # Total orbs limit per level - scales with difficulty
        self.max_total_orbs = self._calculate_max_orbs(self.level)
        self.orbs_spawned = 0
        
        # Spawn initial orbs
        self._spawn_initial_orbs()
        
        # Debug print untuk cek speed
        print(f"Level {self.level}: Speed={self.speed:.1f}, Spawn Interval={self.spawn_interval:.2f}s")
        
    def _calculate_max_orbs(self, level):
        if level == 1: return 15
        elif level == 2: return 20
        elif level == 3: return 25
        elif level <= 5: return 30
        elif level <= 10: return 40
        else: return 50
        
    def _spawn_initial_orbs(self):
        if self.level == 1: num_orbs = 4
        elif self.level == 2: num_orbs = 5
        elif self.level == 3: num_orbs = 6
        else: num_orbs = min(5 + self.level, 12)
            
        for i in range(num_orbs):
            distance = -i * self.distance_between_orbs - 200
            orb_type = Orb.random_type()
            self.add_orb_at_distance(orb_type, distance)
            
        self.orbs_spawned = num_orbs
        
    def _should_spawn_powerup(self):
        if self.orbs_since_last_powerup >= self.guaranteed_powerup_after:
            return True
        return random.random() < self.powerup_chance
    
    def _get_random_powerup_type(self):
        powerup_types = [OrbType.BOMB, OrbType.SLOW, OrbType.REVERSE, OrbType.ACCURACY]
        return random.choice(powerup_types)
            
    def add_orb_at_distance(self, orb_type, distance):
        pos = self.path.get_position_at_distance(distance)
        if pos:
            orb = Orb(pos.x(), pos.y(), orb_type)
            orb.path_distance = distance
            
            inserted = False
            for i, existing_orb in enumerate(self.orbs):
                if distance < existing_orb.path_distance:
                    self.orbs.insert(i, orb)
                    inserted = True
                    break
            
            if not inserted:
                self.orbs.append(orb)
            
            self._maintain_spacing()
            
    def insert_orb(self, orb, index):
        if 0 <= index <= len(self.orbs):
            if index < len(self.orbs):
                orb.path_distance = self.orbs[index].path_distance
            elif index > 0:
                orb.path_distance = self.orbs[index - 1].path_distance + self.distance_between_orbs
            else:
                orb.path_distance = 0
                
            self.orbs.insert(index, orb)
                
    def update(self, dt):
        if self.frozen:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.frozen = False
            return
            
        for orb in self.orbs:
            orb.path_distance += self.speed * dt
            pos = self.path.get_position_at_distance(orb.path_distance)
            if pos:
                orb.pos = pos
            orb.update(dt)
        
        self._maintain_spacing()
        
        self.spawn_timer += dt
        can_spawn = (
            self.spawn_timer >= self.spawn_interval and 
            self.orbs_spawned < self.max_total_orbs and
            len(self.orbs) < self.max_total_orbs
        )
        
        if can_spawn:
            self.spawn_timer = 0
            if self.orbs:
                backmost_distance = min(orb.path_distance for orb in self.orbs)
                new_distance = backmost_distance - self.distance_between_orbs
            else:
                new_distance = -self.distance_between_orbs
            
            if self._should_spawn_powerup():
                orb_type = self._get_random_powerup_type()
                self.orbs_since_last_powerup = 0
            else:
                orb_type = Orb.random_type()
                self.orbs_since_last_powerup += 1
            
            self.add_orb_at_distance(orb_type, new_distance)
            self.orbs_spawned += 1
            
        self.orbs = [orb for orb in self.orbs if not orb.marked_for_removal]
    
    def _maintain_spacing(self):
        """MIGRATED: two-pass overlap/gap adjustment now runs in Rust (or the
        pure-Python fallback) via core.maintain_spacing_sorted. The sort by
        path_distance still happens here in Python since orb objects (with
        their Qt-facing state) must stay in lockstep with the sorted order."""
        if len(self.orbs) <= 1:
            return
        
        self.orbs.sort(key=lambda o: o.path_distance)
        
        distances = [o.path_distance for o in self.orbs]
        adjusted = core.maintain_spacing_sorted(distances, self.distance_between_orbs)
        
        for orb, new_distance in zip(self.orbs, adjusted):
            if new_distance != orb.path_distance:
                orb.path_distance = new_distance
                pos = self.path.get_position_at_distance(new_distance)
                if pos:
                    orb.pos = pos
        
    def check_matches(self):
        """MIGRATED: match-run detection now runs in Rust (or the pure-Python
        fallback) via core.check_matches_core. Orb state is projected into
        flat arrays (type id / is_powerup / blocked) since Rust can't touch
        the Orb objects themselves."""
        if len(self.orbs) < 3:
            return []
        
        types = [orb.orb_type for orb in self.orbs]
        is_powerup = [orb.is_powerup() for orb in self.orbs]
        blocked = [orb.marked_for_removal or orb.exploding for orb in self.orbs]
        
        return core.check_matches_core(types, is_powerup, blocked)
        
    def remove_orbs(self, indices):
        for idx in sorted(indices, reverse=True):
            if 0 <= idx < len(self.orbs):
                self.orbs[idx].explode()
                
    def freeze(self, duration):
        self.frozen = True
        self.freeze_timer = duration
        
    def get_head_distance(self):
        if self.orbs:
            return max(orb.path_distance for orb in self.orbs)
        return 0
    
    def get_total_orbs_info(self):
        return {
            'current': len(self.orbs),
            'spawned': self.orbs_spawned,
            'max': self.max_total_orbs,
            'remaining': self.max_total_orbs - self.orbs_spawned
        }
        
    def draw(self, painter):
        for orb in self.orbs:
            orb.draw(painter)


class Path:
    """Dynamic curved path for orb movement - Optimized with level-based patterns.
    MIGRATED: generation, distance->position lookup (binary search), and
    visible-segment culling now run in Rust (zuma_core.PathCore) or the
    pure-Python fallback (zuma_core_fallback.PathCore). This class is a thin
    QPointF-facing wrapper so scene.py/chain.py need ZERO changes."""
    
    def __init__(self, width, height, level=1):
        self.width = width
        self.height = height
        self.level = level
        
        self._core = core.PathCore(width, height, level)
        
        # Cached QPointF views for drawing code (scene.py reads .points directly)
        self.points = [QPointF(x, y) for x, y in self._core.points]
        self.total_length = self._core.total_length
        
        # Visible rendering optimization
        self.visible_segments = []  # Only segments near orbs will be drawn
        
    def get_position_at_distance(self, distance):
        """Fast lookup, delegated to the Rust/fallback core"""
        x, y = self._core.get_position_at_distance(distance)
        return QPointF(x, y)
        
    def get_end_position(self):
        x, y = self._core.get_end_position()
        return QPointF(x, y)
    
    def update_visible_segments(self, orb_distances):
        """
        Update which path segments should be rendered
        Only render segments near orbs (optimization)
        """
        self.visible_segments = self._core.update_visible_segments(orb_distances)
