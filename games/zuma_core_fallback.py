"""
zuma_core_fallback.py
----------------------
Pure-Python fallback implementation with the EXACT same function/class API
as the compiled `zuma_core` Rust extension. If the .pyd/.so wheel isn't
installed, zuma_bridge.py imports this module instead so the game keeps
running (slower, but correct) with zero code changes elsewhere.

This is a straight line-for-line port of physics.py / collision.py / the
numeric parts of chain.py - kept in sync with lib.rs on purpose.
"""

import math

__rust_backend__ = False

RAINBOW_TYPE = 7  # must mirror games.orb.OrbType.RAINBOW


# ---------------------------------------------------------------------------
# physics.py :: Vector2D
# ---------------------------------------------------------------------------

def vec_magnitude(x, y):
    return math.sqrt(x * x + y * y)


def vec_normalize(x, y):
    mag = vec_magnitude(x, y)
    if mag > 0:
        return (x / mag, y / mag)
    return (0.0, 0.0)


def vec_dot(x1, y1, x2, y2):
    return x1 * x2 + y1 * y2


def vec_distance(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)


def vec_angle_between(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)


def vec_lerp(x1, y1, x2, y2, t):
    t = max(0.0, min(1.0, t))
    return (x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)


# ---------------------------------------------------------------------------
# physics.py :: Easing
# ---------------------------------------------------------------------------

def ease_in_quad(t):
    return t * t


def ease_out_quad(t):
    return t * (2 - t)


def ease_in_out_quad(t):
    return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t


def ease_in_cubic(t):
    return t * t * t


def ease_out_cubic(t):
    return 1 + (t - 1) ** 3


def elastic(t):
    if t == 0 or t == 1:
        return t
    p = 0.3
    s = p / 4
    return math.pow(2, -10 * t) * math.sin((t - s) * (2 * math.pi) / p) + 1


# ---------------------------------------------------------------------------
# physics.py :: CurveGenerator
# ---------------------------------------------------------------------------

def bezier_curve(p0, p1, p2, p3, num_points=50):
    points = []
    if num_points < 2:
        return [p0]
    for i in range(num_points):
        t = i / (num_points - 1)
        x = ((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] +
             3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0])
        y = ((1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] +
             3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1])
        points.append((x, y))
    return points


def catmull_rom_curve(points, num_samples=20):
    if len(points) < 4:
        return list(points)

    curve_points = []
    for i in range(len(points) - 3):
        p0, p1, p2, p3 = points[i:i + 4]

        for j in range(num_samples):
            t = j / num_samples
            t2 = t * t
            t3 = t2 * t

            x = 0.5 * (
                (2 * p1[0]) +
                (-p0[0] + p2[0]) * t +
                (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            )
            y = 0.5 * (
                (2 * p1[1]) +
                (-p0[1] + p2[1]) * t +
                (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            )
            curve_points.append((x, y))

    return curve_points


# ---------------------------------------------------------------------------
# collision.py :: CollisionDetector
# ---------------------------------------------------------------------------

def distance_between(p1, p2):
    return vec_distance(p1[0], p1[1], p2[0], p2[1])


def check_collision(proj_x, proj_y, proj_radius, orbs):
    for i, (ox, oy, orad) in enumerate(orbs):
        dist = vec_distance(proj_x, proj_y, ox, oy)
        if dist < proj_radius + orad:
            return i
    return None


def find_insertion_point(proj_x, proj_y, orb_positions):
    if not orb_positions:
        return 0

    min_distance = float('inf')
    best_index = 0

    for i in range(len(orb_positions) + 1):
        if i == 0:
            compare_pos = orb_positions[0]
        elif i == len(orb_positions):
            compare_pos = orb_positions[-1]
        else:
            p1 = orb_positions[i - 1]
            p2 = orb_positions[i]
            compare_pos = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

        dist = vec_distance(proj_x, proj_y, compare_pos[0], compare_pos[1])
        if dist < min_distance:
            min_distance = dist
            best_index = i

    return best_index


# ---------------------------------------------------------------------------
# chain.py :: Path
# ---------------------------------------------------------------------------

def _calculate_y_position(start_y, progress, pattern_type, level, height):
    amplitude = height * (0.25 + level * 0.02)
    amplitude = min(amplitude, height * 0.4)

    if pattern_type == 0:
        wave = math.sin(progress * math.pi * 3) * amplitude
        return start_y + wave
    elif pattern_type == 1:
        wave = math.sin(progress * math.pi * 2) * amplitude * 0.8
        drift = (progress - 0.5) * height * 0.2
        return start_y + wave + drift
    elif pattern_type == 2:
        wave = math.sin(progress * math.pi * 4) * amplitude * (1 - progress * 0.5)
        return start_y + wave
    elif pattern_type == 3:
        base = start_y + math.sin(progress * math.pi * 6) * amplitude * 0.6
        oscillation = math.sin(progress * math.pi * 2) * 50
        return base + oscillation
    elif pattern_type == 4:
        wave1 = math.sin(progress * math.pi * 3) * amplitude * 0.7
        wave2 = math.sin(progress * math.pi * 5) * amplitude * 0.3
        return start_y + wave1 + wave2
    elif pattern_type == 5:
        s_curve = (progress - 0.5) * height * 0.3
        wave = math.sin(progress * math.pi * 4) * amplitude * 0.5
        return start_y + s_curve + wave
    elif pattern_type == 6:
        wave = math.sin(progress * math.pi * 5) * amplitude * progress
        return start_y + wave
    else:
        wave = 0
        for freq in (2, 3, 5):
            wave += math.sin(progress * math.pi * freq) * (amplitude / freq)
        return start_y + wave


class PathCore:
    """Pure-Python mirror of the Rust PathCore pyclass - same API."""

    def __init__(self, width, height, level):
        self.width = width
        self.height = height
        self.level = level
        self._points = []
        self._segment_lengths = []
        self._cumulative_lengths = []
        self._total_length = 0.0
        self._generate()

    def _generate(self):
        start_x = 50.0
        start_y = float(int(self.height) // 2)
        end_x = self.width - 100.0
        end_y = start_y

        num_segments = max(min(5 + self.level * 2, 20), 2)
        pattern_type = (self.level - 1) % 8

        self._points = [(start_x, start_y)]
        for i in range(1, num_segments):
            progress = i / num_segments
            x = start_x + (end_x - start_x) * progress
            y = _calculate_y_position(start_y, progress, pattern_type, self.level, self.height)
            self._points.append((x, y))
        self._points.append((end_x, end_y))

        self._calculate_length()

    def _calculate_length(self):
        self._total_length = 0.0
        self._segment_lengths = []
        self._cumulative_lengths = [0.0]

        for i in range(len(self._points) - 1):
            p1 = self._points[i]
            p2 = self._points[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            seg_len = math.sqrt(dx * dx + dy * dy)
            self._segment_lengths.append(seg_len)
            self._total_length += seg_len
            self._cumulative_lengths.append(self._total_length)

    @property
    def points(self):
        return list(self._points)

    @property
    def total_length(self):
        return self._total_length

    def get_position_at_distance(self, distance):
        if not self._points:
            return (0.0, 0.0)
        if distance < 0:
            return self._points[0]
        if distance > self._total_length:
            return self._points[-1]

        left, right = 0, len(self._cumulative_lengths) - 1
        while left < right - 1:
            mid = (left + right) // 2
            if self._cumulative_lengths[mid] <= distance:
                left = mid
            else:
                right = mid

        segment_idx = left
        segment_start = self._cumulative_lengths[segment_idx]
        segment_length = self._segment_lengths[segment_idx]

        if segment_length == 0:
            return self._points[segment_idx]

        t = (distance - segment_start) / segment_length
        p1 = self._points[segment_idx]
        p2 = self._points[segment_idx + 1]
        return (p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t)

    def get_end_position(self):
        return self._points[-1]

    def update_visible_segments(self, orb_distances):
        if not orb_distances:
            return []

        min_dist = min(orb_distances) - 100
        max_dist = max(orb_distances) + 100

        visible = []
        for i in range(len(self._cumulative_lengths) - 1):
            cumulative = self._cumulative_lengths[i]
            segment_end = self._cumulative_lengths[i + 1]
            if segment_end >= min_dist and cumulative <= max_dist:
                visible.append(i)
        return visible


# ---------------------------------------------------------------------------
# chain.py :: OrbChain numeric hot paths
# ---------------------------------------------------------------------------

def maintain_spacing_sorted(distances, spacing):
    adjusted = list(distances)
    if len(adjusted) <= 1:
        return adjusted

    for i in range(1, len(adjusted)):
        min_distance = adjusted[i - 1] + spacing
        if adjusted[i] < min_distance:
            adjusted[i] = min_distance

    max_distance = spacing + 5
    for i in range(len(adjusted) - 1, 0, -1):
        actual_distance = adjusted[i] - adjusted[i - 1]
        if actual_distance > max_distance:
            pull_amount = (actual_distance - spacing) * 0.5
            adjusted[i] -= pull_amount

    return adjusted


def check_matches_core(types, is_powerup, blocked):
    n = len(types)
    matches = []
    if n < 3:
        return matches

    def orb_matches(a, b):
        if is_powerup[a] or is_powerup[b]:
            return False
        if types[a] == RAINBOW_TYPE or types[b] == RAINBOW_TYPE:
            return True
        return types[a] == types[b]

    i = 0
    while i < n:
        if blocked[i] or is_powerup[i]:
            i += 1
            continue

        match_start = i
        match_type = types[i]
        match_count = 1
        j = i + 1

        while j < n:
            if blocked[j]:
                break

            if is_powerup[j]:
                if j + 1 < n:
                    after = j + 1
                    if (not is_powerup[after] and types[after] == match_type
                            and not blocked[after]):
                        match_count += 1
                        j += 1
                        continue
                break

            if orb_matches(j, match_start):
                match_count += 1
                j += 1
            else:
                break

        if match_count >= 3:
            matches.append(list(range(match_start, match_start + match_count)))
            i = j
        else:
            i += 1

    return matches
