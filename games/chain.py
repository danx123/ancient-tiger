"""
Orb chain management and movement along path
"""

from PySide6.QtCore import QPointF
from games.orb import Orb, OrbType
import math

class OrbChain:
    """Manages chain of orbs moving along a path"""
    
    def __init__(self, path, level=1):
        self.path = path
        self.orbs = []
        self.speed = 12 + level * 2  # Even slower: 12 at level 1
        self.spawn_timer = 0
        self.spawn_interval = 2.5 - (level * 0.08)  # Slower spawn: 2.5s at level 1
        self.spawn_interval = max(self.spawn_interval, 0.8)  # Minimum spawn interval
        self.distance_between_orbs = 34  # Slightly more spacing
        self.level = level
        self.frozen = False
        self.freeze_timer = 0
        
        # Total orbs limit per level
        self.max_total_orbs = self._calculate_max_orbs(level)
        self.orbs_spawned = 0
        
        # Spawn initial orbs
        self._spawn_initial_orbs()
        
    def _calculate_max_orbs(self, level):
        """Calculate maximum orbs allowed for this level"""
        if level == 1:
            return 15  # Very limited for level 1
        elif level == 2:
            return 20
        elif level == 3:
            return 25
        elif level <= 5:
            return 30
        elif level <= 10:
            return 40
        else:
            return 50  # Max cap
        
    def _spawn_initial_orbs(self):
        """Spawn initial chain of orbs"""
        # Even fewer orbs at start - very easy
        if self.level == 1:
            num_orbs = 4  # Very easy start - only 4 orbs!
        elif self.level == 2:
            num_orbs = 5
        elif self.level == 3:
            num_orbs = 6
        else:
            num_orbs = min(5 + self.level, 12)  # Cap initial orbs
            
        for i in range(num_orbs):
            # Spawn from the back (negative distance) - start VERY far back
            distance = -i * self.distance_between_orbs - 200  # Start even further back!
            orb_type = Orb.random_type()
            self.add_orb_at_distance(orb_type, distance)
            
        self.orbs_spawned = num_orbs
            
    def add_orb_at_distance(self, orb_type, distance):
        """Add orb at specific distance along path"""
        pos = self.path.get_position_at_distance(distance)
        if pos:
            orb = Orb(pos.x(), pos.y(), orb_type)
            orb.path_distance = distance
            
            # Insert orb in correct sorted position
            inserted = False
            for i, existing_orb in enumerate(self.orbs):
                if distance < existing_orb.path_distance:
                    self.orbs.insert(i, orb)
                    inserted = True
                    break
            
            if not inserted:
                self.orbs.append(orb)
            
            # Immediately fix any spacing issues
            self._maintain_spacing()
            
    def insert_orb(self, orb, index):
        """Insert orb into chain at specific index"""
        if 0 <= index <= len(self.orbs):
            # Calculate position based on neighbors
            if index < len(self.orbs):
                orb.path_distance = self.orbs[index].path_distance
            elif index > 0:
                orb.path_distance = self.orbs[index - 1].path_distance + self.distance_between_orbs
            else:
                orb.path_distance = 0
                
            self.orbs.insert(index, orb)
            # Don't push forward immediately, let update handle it naturally
            
    def _adjust_positions(self, start_index):
        """Adjust orb positions after insertion - REMOVED to prevent push forward"""
        # This function is now empty - positions will be adjusted naturally in update()
        pass
                
    def update(self, dt):
        """Update chain movement"""
        if self.frozen:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.frozen = False
            return
            
        # Move all orbs forward along the path
        for orb in self.orbs:
            orb.path_distance += self.speed * dt
            
            # Update visual position based on path
            pos = self.path.get_position_at_distance(orb.path_distance)
            if pos:
                orb.pos = pos
                
            orb.update(dt)
        
        # Maintain proper spacing between orbs
        self._maintain_spacing()
        
        # Spawn new orbs at the BACK of the chain only
        self.spawn_timer += dt
        
        # Check if we can spawn more orbs
        can_spawn = (
            self.spawn_timer >= self.spawn_interval and 
            self.orbs_spawned < self.max_total_orbs and
            len(self.orbs) < self.max_total_orbs
        )
        
        if can_spawn:
            self.spawn_timer = 0
            
            # Find the backmost orb
            if self.orbs:
                backmost_distance = min(orb.path_distance for orb in self.orbs)
                new_distance = backmost_distance - self.distance_between_orbs
            else:
                new_distance = -self.distance_between_orbs
            
            orb_type = Orb.random_type()
            self.add_orb_at_distance(orb_type, new_distance)
            self.orbs_spawned += 1
            
            print(f"Chain: Spawned orb {self.orbs_spawned}/{self.max_total_orbs}")
            
        # Remove marked orbs
        removed_count = len([orb for orb in self.orbs if orb.marked_for_removal])
        if removed_count > 0:
            print(f"Chain: Removing {removed_count} exploded orbs")
            
        self.orbs = [orb for orb in self.orbs if not orb.marked_for_removal]
        
        # Log status for debugging
        if len(self.orbs) <= 3:
            print(f"Chain: Only {len(self.orbs)} orbs left! Spawned: {self.orbs_spawned}/{self.max_total_orbs}")
    
    def _maintain_spacing(self):
        """Maintain proper spacing between all orbs"""
        if len(self.orbs) <= 1:
            return
        
        # Sort orbs by distance (back to front)
        self.orbs.sort(key=lambda o: o.path_distance)
        
        # Two-pass system: first ensure minimum spacing, then close gaps
        
        # Pass 1: Ensure minimum spacing (prevent overlap)
        for i in range(1, len(self.orbs)):
            prev_orb = self.orbs[i - 1]
            current_orb = self.orbs[i]
            
            # Calculate required minimum distance
            min_distance = prev_orb.path_distance + self.distance_between_orbs
            
            # If too close, push current orb forward
            if current_orb.path_distance < min_distance:
                current_orb.path_distance = min_distance
                
                # Update visual position
                pos = self.path.get_position_at_distance(current_orb.path_distance)
                if pos:
                    current_orb.pos = pos
        
        # Pass 2: Close large gaps (pull orbs together smoothly)
        for i in range(len(self.orbs) - 1, 0, -1):  # Iterate backwards
            prev_orb = self.orbs[i - 1]
            current_orb = self.orbs[i]
            
            # Calculate actual distance
            actual_distance = current_orb.path_distance - prev_orb.path_distance
            
            # If gap is too large, pull current orb backward
            max_distance = self.distance_between_orbs + 5  # Allow small gap
            if actual_distance > max_distance:
                # Pull backward gradually (not instant to avoid visual glitch)
                pull_amount = (actual_distance - self.distance_between_orbs) * 0.5
                current_orb.path_distance -= pull_amount
                
                # Update visual position
                pos = self.path.get_position_at_distance(current_orb.path_distance)
                if pos:
                    current_orb.pos = pos
    
    def _pull_together_instantly(self):
        """Pull orbs together instantly when there's a gap - REMOVED"""
        # This function caused the stacking issue, so it's now empty
        # Spacing is handled by _maintain_spacing instead
        pass
        
    def check_matches(self):
        """Check for matching orb sequences"""
        if len(self.orbs) < 3:
            return []
            
        matches = []
        i = 0
        
        while i < len(self.orbs):
            match_start = i
            match_type = self.orbs[i].orb_type
            match_count = 1
            
            # Count consecutive matching orbs
            j = i + 1
            while j < len(self.orbs) and self.orbs[j].matches(self.orbs[i]):
                match_count += 1
                j += 1
                
            # If 3 or more matches, mark for removal
            if match_count >= 3:
                match_indices = list(range(match_start, match_start + match_count))
                matches.append(match_indices)
                i = j
            else:
                i += 1
                
        return matches
        
    def remove_orbs(self, indices):
        """Remove orbs at specified indices"""
        for idx in sorted(indices, reverse=True):
            if 0 <= idx < len(self.orbs):
                self.orbs[idx].explode()
        
        # After marking for removal, the update loop will clean them up
        # and _maintain_spacing will fix any gaps
                
    def freeze(self, duration):
        """Freeze chain movement"""
        self.frozen = True
        self.freeze_timer = duration
        
    def get_head_distance(self):
        """Get distance of the furthest orb (front of chain)"""
        if self.orbs:
            return max(orb.path_distance for orb in self.orbs)
        return 0
    
    def get_total_orbs_info(self):
        """Get info about orb count"""
        return {
            'current': len(self.orbs),
            'spawned': self.orbs_spawned,
            'max': self.max_total_orbs,
            'remaining': self.max_total_orbs - self.orbs_spawned
        }
        
    def draw(self, painter):
        """Draw all orbs in chain"""
        for orb in self.orbs:
            orb.draw(painter)


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
        """Generate curved path procedurally with different patterns"""
        # Start position
        start_x = 50
        start_y = self.height // 2
        
        # End position (portal)
        end_x = self.width - 100
        end_y = self.height // 2
        
        # Generate control points for curves
        num_segments = 5 + complexity * 2
        self.points = [QPointF(start_x, start_y)]
        
        # Different path patterns based on level
        pattern_type = pattern_type % 5  # 5 different patterns
        
        for i in range(1, num_segments):
            progress = i / num_segments
            x = start_x + (end_x - start_x) * progress
            
            if pattern_type == 0:
                # Sine wave pattern
                wave = math.sin(progress * math.pi * 3) * (self.height * 0.3)
                y = start_y + wave
                
            elif pattern_type == 1:
                # S-curve pattern
                wave = math.sin(progress * math.pi * 2) * (self.height * 0.25)
                y = start_y + wave + (progress - 0.5) * self.height * 0.2
                
            elif pattern_type == 2:
                # Spiral pattern
                wave = math.sin(progress * math.pi * 4) * (self.height * 0.2 * (1 - progress))
                y = start_y + wave
                
            elif pattern_type == 3:
                # Zigzag pattern
                if i % 2 == 0:
                    y = start_y + self.height * 0.2
                else:
                    y = start_y - self.height * 0.2
                y += math.sin(progress * math.pi * 2) * 50
                
            else:  # pattern_type == 4
                # Double wave pattern
                wave1 = math.sin(progress * math.pi * 3) * (self.height * 0.2)
                wave2 = math.sin(progress * math.pi * 5) * (self.height * 0.1)
                y = start_y + wave1 + wave2
            
            self.points.append(QPointF(x, y))
            
        self.points.append(QPointF(end_x, end_y))
        
        # Calculate total path length
        self._calculate_length()
        
    def _calculate_length(self):
        """Calculate total path length"""
        self.total_length = 0
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            self.total_length += math.sqrt(dx * dx + dy * dy)
            
    def get_position_at_distance(self, distance):
        """Get position along path at given distance"""
        if distance < 0:
            return self.points[0]
        if distance > self.total_length:
            return self.points[-1]
            
        # Find segment
        current_length = 0
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            segment_length = math.sqrt(dx * dx + dy * dy)
            
            if current_length + segment_length >= distance:
                # Interpolate within segment
                t = (distance - current_length) / segment_length
                x = p1.x() + dx * t
                y = p1.y() + dy * t
                return QPointF(x, y)
                
            current_length += segment_length
            
        return self.points[-1]
        
    def get_end_position(self):
        """Get end portal position"""
        return self.points[-1]
