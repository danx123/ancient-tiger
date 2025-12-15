"""
Orb chain management and movement along path
FIXED: 
1. Infinite loop fixed by ignoring exploding orbs in check_matches
2. Path class included
"""

from PySide6.QtCore import QPointF
from games.orb import Orb, OrbType
import math
import random

class OrbChain:
    """Manages chain of orbs moving along a path"""
    
    def __init__(self, path, level=1):
        self.path = path
        self.orbs = []
        self.speed = 12 + level * 2
        self.spawn_timer = 0
        self.spawn_interval = 2.5 - (level * 0.08)
        self.spawn_interval = max(self.spawn_interval, 0.8)
        self.distance_between_orbs = 34
        self.level = level
        self.frozen = False
        self.freeze_timer = 0
        
        # Powerup spawn system
        self.powerup_chance = 0.12
        self.orbs_since_last_powerup = 0
        self.guaranteed_powerup_after = 15
        
        # Total orbs limit per level
        self.max_total_orbs = self._calculate_max_orbs(level)
        self.orbs_spawned = 0
        
        # Spawn initial orbs
        self._spawn_initial_orbs()
        
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
        if len(self.orbs) <= 1:
            return
        
        self.orbs.sort(key=lambda o: o.path_distance)
        
        # Prevent overlap
        for i in range(1, len(self.orbs)):
            prev_orb = self.orbs[i - 1]
            current_orb = self.orbs[i]
            min_distance = prev_orb.path_distance + self.distance_between_orbs
            
            if current_orb.path_distance < min_distance:
                current_orb.path_distance = min_distance
                pos = self.path.get_position_at_distance(current_orb.path_distance)
                if pos:
                    current_orb.pos = pos
        
        # Pull together gaps
        for i in range(len(self.orbs) - 1, 0, -1):
            prev_orb = self.orbs[i - 1]
            current_orb = self.orbs[i]
            actual_distance = current_orb.path_distance - prev_orb.path_distance
            max_distance = self.distance_between_orbs + 5
            
            if actual_distance > max_distance:
                pull_amount = (actual_distance - self.distance_between_orbs) * 0.5
                current_orb.path_distance -= pull_amount
                pos = self.path.get_position_at_distance(current_orb.path_distance)
                if pos:
                    current_orb.pos = pos
        
    def check_matches(self):
        """Check for matching orb sequences - FIXED: Ignored exploding orbs"""
        if len(self.orbs) < 3:
            return []
            
        matches = []
        i = 0
        
        while i < len(self.orbs):
            current_orb = self.orbs[i]
            
            # CRITICAL FIX: Skip exploding orbs to prevent infinite loop
            if current_orb.marked_for_removal or current_orb.exploding:
                i += 1
                continue
            
            if current_orb.is_powerup():
                i += 1
                continue
            
            match_start = i
            match_type = current_orb.orb_type
            match_count = 1
            
            j = i + 1
            while j < len(self.orbs):
                next_orb = self.orbs[j]
                
                # Stop if next orb is exploding
                if next_orb.marked_for_removal or next_orb.exploding:
                    break
                
                if next_orb.is_powerup():
                    if j + 1 < len(self.orbs):
                        after_powerup = self.orbs[j + 1]
                        # Ensure orb after powerup is valid and matches type
                        if (not after_powerup.is_powerup() and 
                            after_powerup.orb_type == match_type and 
                            not after_powerup.marked_for_removal and 
                            not after_powerup.exploding):
                            match_count += 1
                            j += 1
                            continue
                    break
                
                if next_orb.matches(current_orb):
                    match_count += 1
                    j += 1
                else:
                    break
                
            if match_count >= 3:
                match_indices = list(range(match_start, match_start + match_count))
                matches.append(match_indices)
                i = j
            else:
                i += 1
                
        return matches
        
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

# --- INI CLASS PATH YANG SEBELUMNYA HILANG ---
class Path:
    """Curved path for orb movement"""
    
    def __init__(self, width, height, complexity=1, pattern_type=0):
        self.width = width
        self.height = height
        self.points = []
        self.total_length = 0
        self.pattern_type = pattern_type
        self._generate_path(complexity, pattern_type)
        
    def _generate_path(self, complexity, pattern_type):
        start_x = 50
        start_y = self.height // 2
        end_x = self.width - 100
        end_y = self.height // 2
        
        num_segments = 5 + complexity * 2
        self.points = [QPointF(start_x, start_y)]
        
        pattern_type = pattern_type % 5
        
        for i in range(1, num_segments):
            progress = i / num_segments
            x = start_x + (end_x - start_x) * progress
            
            if pattern_type == 0:
                wave = math.sin(progress * math.pi * 3) * (self.height * 0.3)
                y = start_y + wave
            elif pattern_type == 1:
                wave = math.sin(progress * math.pi * 2) * (self.height * 0.25)
                y = start_y + wave + (progress - 0.5) * self.height * 0.2
            elif pattern_type == 2:
                wave = math.sin(progress * math.pi * 4) * (self.height * 0.2 * (1 - progress))
                y = start_y + wave
            elif pattern_type == 3:
                y = (start_y + self.height * 0.2) if i % 2 == 0 else (start_y - self.height * 0.2)
                y += math.sin(progress * math.pi * 2) * 50
            else:
                wave1 = math.sin(progress * math.pi * 3) * (self.height * 0.2)
                wave2 = math.sin(progress * math.pi * 5) * (self.height * 0.1)
                y = start_y + wave1 + wave2
            
            self.points.append(QPointF(x, y))
            
        self.points.append(QPointF(end_x, end_y))
        self._calculate_length()
        
    def _calculate_length(self):
        self.total_length = 0
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            self.total_length += math.sqrt(dx * dx + dy * dy)
            
    def get_position_at_distance(self, distance):
        if distance < 0: return self.points[0]
        if distance > self.total_length: return self.points[-1]
            
        current_length = 0
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            segment_length = math.sqrt(dx * dx + dy * dy)
            
            if current_length + segment_length >= distance:
                t = (distance - current_length) / segment_length
                x = p1.x() + dx * t
                y = p1.y() + dy * t
                return QPointF(x, y)
            current_length += segment_length
        return self.points[-1]
        
    def get_end_position(self):
        return self.points[-1]
