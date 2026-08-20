//! zuma_core
//! ---------
//! Single-file Rust/PyO3 extension that replaces the pure-math hot paths of the
//! Macan orb-chain game (physics.py, collision.py, and the numeric parts of
//! chain.py's Path/OrbChain). All QPainter/Qt drawing stays in Python - Rust
//! never touches rendering, only numbers.
//!
//! Build:  maturin build --release
//! Import: `import zuma_core` (falls back to zuma_core_fallback.py if missing,
//!          see zuma_bridge.py)

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

const RAINBOW_TYPE: i64 = 7; // must mirror games.orb.OrbType.RAINBOW

// ---------------------------------------------------------------------------
// physics.py :: Vector2D
// ---------------------------------------------------------------------------

#[pyfunction]
fn vec_magnitude(x: f64, y: f64) -> f64 {
    (x * x + y * y).sqrt()
}

#[pyfunction]
fn vec_normalize(x: f64, y: f64) -> (f64, f64) {
    let mag = vec_magnitude(x, y);
    if mag > 0.0 {
        (x / mag, y / mag)
    } else {
        (0.0, 0.0)
    }
}

#[pyfunction]
fn vec_dot(x1: f64, y1: f64, x2: f64, y2: f64) -> f64 {
    x1 * x2 + y1 * y2
}

#[pyfunction]
fn vec_distance(x1: f64, y1: f64, x2: f64, y2: f64) -> f64 {
    let dx = x2 - x1;
    let dy = y2 - y1;
    (dx * dx + dy * dy).sqrt()
}

#[pyfunction]
fn vec_angle_between(x1: f64, y1: f64, x2: f64, y2: f64) -> f64 {
    (y2 - y1).atan2(x2 - x1)
}

#[pyfunction]
fn vec_lerp(x1: f64, y1: f64, x2: f64, y2: f64, t: f64) -> (f64, f64) {
    let t = t.clamp(0.0, 1.0);
    (x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
}

// ---------------------------------------------------------------------------
// physics.py :: Easing
// ---------------------------------------------------------------------------

#[pyfunction]
fn ease_in_quad(t: f64) -> f64 {
    t * t
}

#[pyfunction]
fn ease_out_quad(t: f64) -> f64 {
    t * (2.0 - t)
}

#[pyfunction]
fn ease_in_out_quad(t: f64) -> f64 {
    if t < 0.5 {
        2.0 * t * t
    } else {
        -1.0 + (4.0 - 2.0 * t) * t
    }
}

#[pyfunction]
fn ease_in_cubic(t: f64) -> f64 {
    t * t * t
}

#[pyfunction]
fn ease_out_cubic(t: f64) -> f64 {
    1.0 + (t - 1.0).powi(3)
}

#[pyfunction]
fn elastic(t: f64) -> f64 {
    if t == 0.0 || t == 1.0 {
        return t;
    }
    let p = 0.3;
    let s = p / 4.0;
    2f64.powf(-10.0 * t) * ((t - s) * (2.0 * std::f64::consts::PI) / p).sin() + 1.0
}

// ---------------------------------------------------------------------------
// physics.py :: CurveGenerator
// ---------------------------------------------------------------------------

#[pyfunction]
#[pyo3(signature = (p0, p1, p2, p3, num_points=50))]
fn bezier_curve(
    p0: (f64, f64),
    p1: (f64, f64),
    p2: (f64, f64),
    p3: (f64, f64),
    num_points: usize,
) -> Vec<(f64, f64)> {
    let mut points = Vec::with_capacity(num_points);
    if num_points < 2 {
        points.push(p0);
        return points;
    }
    for i in 0..num_points {
        let t = i as f64 / (num_points - 1) as f64;
        let mt = 1.0 - t;
        let x = mt.powi(3) * p0.0
            + 3.0 * mt.powi(2) * t * p1.0
            + 3.0 * mt * t.powi(2) * p2.0
            + t.powi(3) * p3.0;
        let y = mt.powi(3) * p0.1
            + 3.0 * mt.powi(2) * t * p1.1
            + 3.0 * mt * t.powi(2) * p2.1
            + t.powi(3) * p3.1;
        points.push((x, y));
    }
    points
}

#[pyfunction]
#[pyo3(signature = (points, num_samples=20))]
fn catmull_rom_curve(points: Vec<(f64, f64)>, num_samples: usize) -> Vec<(f64, f64)> {
    if points.len() < 4 {
        return points;
    }
    let mut curve_points = Vec::new();
    for i in 0..points.len() - 3 {
        let p0 = points[i];
        let p1 = points[i + 1];
        let p2 = points[i + 2];
        let p3 = points[i + 3];

        for j in 0..num_samples {
            let t = j as f64 / num_samples as f64;
            let t2 = t * t;
            let t3 = t2 * t;

            let x = 0.5
                * ((2.0 * p1.0)
                    + (-p0.0 + p2.0) * t
                    + (2.0 * p0.0 - 5.0 * p1.0 + 4.0 * p2.0 - p3.0) * t2
                    + (-p0.0 + 3.0 * p1.0 - 3.0 * p2.0 + p3.0) * t3);

            let y = 0.5
                * ((2.0 * p1.1)
                    + (-p0.1 + p2.1) * t
                    + (2.0 * p0.1 - 5.0 * p1.1 + 4.0 * p2.1 - p3.1) * t2
                    + (-p0.1 + 3.0 * p1.1 - 3.0 * p2.1 + p3.1) * t3);

            curve_points.push((x, y));
        }
    }
    curve_points
}

// ---------------------------------------------------------------------------
// collision.py :: CollisionDetector
// ---------------------------------------------------------------------------

#[pyfunction]
fn distance_between(p1: (f64, f64), p2: (f64, f64)) -> f64 {
    vec_distance(p1.0, p1.1, p2.0, p2.1)
}

/// orbs: list of (x, y, radius). Returns the index of the first orb the
/// projectile overlaps, or None.
#[pyfunction]
fn check_collision(
    proj_x: f64,
    proj_y: f64,
    proj_radius: f64,
    orbs: Vec<(f64, f64, f64)>,
) -> Option<usize> {
    for (i, (ox, oy, orad)) in orbs.iter().enumerate() {
        let dist = vec_distance(proj_x, proj_y, *ox, *oy);
        if dist < proj_radius + orad {
            return Some(i);
        }
    }
    None
}

/// orb_positions: list of (x, y) for chain.orbs, in order. Mirrors
/// CollisionDetector.find_insertion_point exactly (including its original
/// behaviour of comparing against orbs[0]/orbs[-1] rather than proj_pos
/// itself at the boundaries).
#[pyfunction]
fn find_insertion_point(proj_x: f64, proj_y: f64, orb_positions: Vec<(f64, f64)>) -> usize {
    if orb_positions.is_empty() {
        return 0;
    }

    let mut min_distance = f64::INFINITY;
    let mut best_index = 0usize;

    for i in 0..=orb_positions.len() {
        let compare_pos = if i == 0 {
            orb_positions[0]
        } else if i == orb_positions.len() {
            orb_positions[orb_positions.len() - 1]
        } else {
            let p1 = orb_positions[i - 1];
            let p2 = orb_positions[i];
            ((p1.0 + p2.0) / 2.0, (p1.1 + p2.1) / 2.0)
        };

        let dist = vec_distance(proj_x, proj_y, compare_pos.0, compare_pos.1);
        if dist < min_distance {
            min_distance = dist;
            best_index = i;
        }
    }

    best_index
}

// ---------------------------------------------------------------------------
// chain.py :: Path  (dynamic path generation + distance lookups)
// ---------------------------------------------------------------------------

#[pyclass]
struct PathCore {
    width: f64,
    height: f64,
    level: i64,
    points: Vec<(f64, f64)>,
    segment_lengths: Vec<f64>,
    cumulative_lengths: Vec<f64>,
    total_length: f64,
}

fn calculate_y_position(start_y: f64, progress: f64, pattern_type: i64, level: i64, height: f64) -> f64 {
    let mut amplitude = height * (0.25 + level as f64 * 0.02);
    amplitude = amplitude.min(height * 0.4);

    match pattern_type {
        0 => {
            let wave = (progress * std::f64::consts::PI * 3.0).sin() * amplitude;
            start_y + wave
        }
        1 => {
            let wave = (progress * std::f64::consts::PI * 2.0).sin() * amplitude * 0.8;
            let drift = (progress - 0.5) * height * 0.2;
            start_y + wave + drift
        }
        2 => {
            let wave = (progress * std::f64::consts::PI * 4.0).sin() * amplitude * (1.0 - progress * 0.5);
            start_y + wave
        }
        3 => {
            let base = start_y + (progress * std::f64::consts::PI * 6.0).sin() * amplitude * 0.6;
            let oscillation = (progress * std::f64::consts::PI * 2.0).sin() * 50.0;
            base + oscillation
        }
        4 => {
            let wave1 = (progress * std::f64::consts::PI * 3.0).sin() * amplitude * 0.7;
            let wave2 = (progress * std::f64::consts::PI * 5.0).sin() * amplitude * 0.3;
            start_y + wave1 + wave2
        }
        5 => {
            let s_curve = (progress - 0.5) * height * 0.3;
            let wave = (progress * std::f64::consts::PI * 4.0).sin() * amplitude * 0.5;
            start_y + s_curve + wave
        }
        6 => {
            let wave = (progress * std::f64::consts::PI * 5.0).sin() * amplitude * progress;
            start_y + wave
        }
        _ => {
            let mut wave = 0.0;
            for freq in [2.0, 3.0, 5.0] {
                wave += (progress * std::f64::consts::PI * freq).sin() * (amplitude / freq);
            }
            start_y + wave
        }
    }
}

impl PathCore {
    fn generate(&mut self) {
        let start_x = 50.0_f64;
        let start_y = (self.height as i64 / 2) as f64;
        let end_x = self.width - 100.0;
        let end_y = start_y;

        let num_segments = (5 + self.level * 2).min(20).max(2);
        let pattern_type = (self.level - 1).rem_euclid(8);

        self.points.clear();
        self.points.push((start_x, start_y));

        for i in 1..num_segments {
            let progress = i as f64 / num_segments as f64;
            let x = start_x + (end_x - start_x) * progress;
            let y = calculate_y_position(start_y, progress, pattern_type, self.level, self.height);
            self.points.push((x, y));
        }

        self.points.push((end_x, end_y));
        self.calculate_length();
    }

    fn calculate_length(&mut self) {
        self.total_length = 0.0;
        self.segment_lengths.clear();
        self.cumulative_lengths.clear();
        self.cumulative_lengths.push(0.0);

        for i in 0..self.points.len().saturating_sub(1) {
            let p1 = self.points[i];
            let p2 = self.points[i + 1];
            let dx = p2.0 - p1.0;
            let dy = p2.1 - p1.1;
            let seg_len = (dx * dx + dy * dy).sqrt();
            self.segment_lengths.push(seg_len);
            self.total_length += seg_len;
            self.cumulative_lengths.push(self.total_length);
        }
    }
}

#[pymethods]
impl PathCore {
    #[new]
    fn new(width: f64, height: f64, level: i64) -> Self {
        let mut p = PathCore {
            width,
            height,
            level,
            points: Vec::new(),
            segment_lengths: Vec::new(),
            cumulative_lengths: Vec::new(),
            total_length: 0.0,
        };
        p.generate();
        p
    }

    #[getter]
    fn points(&self) -> Vec<(f64, f64)> {
        self.points.clone()
    }

    #[getter]
    fn total_length(&self) -> f64 {
        self.total_length
    }

    fn get_position_at_distance(&self, distance: f64) -> (f64, f64) {
        if self.points.is_empty() {
            return (0.0, 0.0);
        }
        if distance < 0.0 {
            return self.points[0];
        }
        if distance > self.total_length {
            return self.points[self.points.len() - 1];
        }

        // Binary search for segment, mirrors the Python implementation.
        let mut left = 0usize;
        let mut right = self.cumulative_lengths.len() - 1;

        while left < right.saturating_sub(1) {
            let mid = (left + right) / 2;
            if self.cumulative_lengths[mid] <= distance {
                left = mid;
            } else {
                right = mid;
            }
        }

        let segment_idx = left;
        let segment_start = self.cumulative_lengths[segment_idx];
        let segment_length = self.segment_lengths[segment_idx];

        if segment_length == 0.0 {
            return self.points[segment_idx];
        }

        let t = (distance - segment_start) / segment_length;
        let p1 = self.points[segment_idx];
        let p2 = self.points[segment_idx + 1];

        (p1.0 + (p2.0 - p1.0) * t, p1.1 + (p2.1 - p1.1) * t)
    }

    fn get_end_position(&self) -> (f64, f64) {
        self.points[self.points.len() - 1]
    }

    /// Returns indices of segments whose span overlaps [min(dist)-100, max(dist)+100].
    fn update_visible_segments(&self, orb_distances: Vec<f64>) -> Vec<usize> {
        if orb_distances.is_empty() {
            return Vec::new();
        }
        let min_dist = orb_distances.iter().cloned().fold(f64::INFINITY, f64::min) - 100.0;
        let max_dist = orb_distances.iter().cloned().fold(f64::NEG_INFINITY, f64::max) + 100.0;

        let mut visible: Vec<usize> = Vec::new();
        for i in 0..self.cumulative_lengths.len().saturating_sub(1) {
            let cumulative = self.cumulative_lengths[i];
            let segment_end = self.cumulative_lengths[i + 1];
            if segment_end >= min_dist && cumulative <= max_dist {
                visible.push(i);
            }
        }
        visible
    }
}

// ---------------------------------------------------------------------------
// chain.py :: OrbChain (numeric hot paths only - orb objects stay in Python)
// ---------------------------------------------------------------------------

/// distances MUST already be sorted ascending (Python sorts self.orbs by
/// path_distance first, same as the original _maintain_spacing). Returns the
/// adjusted distances, same length/order.
#[pyfunction]
fn maintain_spacing_sorted(distances: Vec<f64>, spacing: f64) -> Vec<f64> {
    let mut adjusted = distances;
    if adjusted.len() <= 1 {
        return adjusted;
    }

    // Pass 1: prevent overlap (front to back).
    for i in 1..adjusted.len() {
        let min_distance = adjusted[i - 1] + spacing;
        if adjusted[i] < min_distance {
            adjusted[i] = min_distance;
        }
    }

    // Pass 2: pull together gaps (back to front).
    let max_distance = spacing + 5.0;
    for i in (1..adjusted.len()).rev() {
        let actual_distance = adjusted[i] - adjusted[i - 1];
        if actual_distance > max_distance {
            let pull_amount = (actual_distance - spacing) * 0.5;
            adjusted[i] -= pull_amount;
        }
    }

    adjusted
}

/// Mirrors OrbChain.check_matches(). `types` uses OrbType ids (RAINBOW=7);
/// `is_powerup`/`blocked` (marked_for_removal OR exploding) are precomputed
/// per-orb flags from Python. Returns list of index-runs (each len >= 3).
#[pyfunction]
fn check_matches_core(types: Vec<i64>, is_powerup: Vec<bool>, blocked: Vec<bool>) -> Vec<Vec<usize>> {
    let n = types.len();
    let mut matches: Vec<Vec<usize>> = Vec::new();
    if n < 3 {
        return matches;
    }

    let orb_matches = |a: usize, b: usize| -> bool {
        if is_powerup[a] || is_powerup[b] {
            return false;
        }
        if types[a] == RAINBOW_TYPE || types[b] == RAINBOW_TYPE {
            return true;
        }
        types[a] == types[b]
    };

    let mut i = 0usize;
    while i < n {
        if blocked[i] || is_powerup[i] {
            i += 1;
            continue;
        }

        let match_start = i;
        let match_type = types[i];
        let mut match_count = 1usize;
        let mut j = i + 1;

        while j < n {
            if blocked[j] {
                break;
            }

            if is_powerup[j] {
                if j + 1 < n {
                    let after = j + 1;
                    if !is_powerup[after]
                        && types[after] == match_type
                        && !blocked[after]
                    {
                        match_count += 1;
                        j += 1;
                        continue;
                    }
                }
                break;
            }

            if orb_matches(j, match_start) {
                match_count += 1;
                j += 1;
            } else {
                break;
            }
        }

        if match_count >= 3 {
            matches.push((match_start..match_start + match_count).collect());
            i = j;
        } else {
            i += 1;
        }
    }

    matches
}

// ---------------------------------------------------------------------------
// Module registration
// ---------------------------------------------------------------------------

#[pymodule]
fn zuma_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__rust_backend__", true)?;

    // physics.py :: Vector2D
    m.add_function(wrap_pyfunction!(vec_magnitude, m)?)?;
    m.add_function(wrap_pyfunction!(vec_normalize, m)?)?;
    m.add_function(wrap_pyfunction!(vec_dot, m)?)?;
    m.add_function(wrap_pyfunction!(vec_distance, m)?)?;
    m.add_function(wrap_pyfunction!(vec_angle_between, m)?)?;
    m.add_function(wrap_pyfunction!(vec_lerp, m)?)?;

    // physics.py :: Easing
    m.add_function(wrap_pyfunction!(ease_in_quad, m)?)?;
    m.add_function(wrap_pyfunction!(ease_out_quad, m)?)?;
    m.add_function(wrap_pyfunction!(ease_in_out_quad, m)?)?;
    m.add_function(wrap_pyfunction!(ease_in_cubic, m)?)?;
    m.add_function(wrap_pyfunction!(ease_out_cubic, m)?)?;
    m.add_function(wrap_pyfunction!(elastic, m)?)?;

    // physics.py :: CurveGenerator
    m.add_function(wrap_pyfunction!(bezier_curve, m)?)?;
    m.add_function(wrap_pyfunction!(catmull_rom_curve, m)?)?;

    // collision.py :: CollisionDetector
    m.add_function(wrap_pyfunction!(distance_between, m)?)?;
    m.add_function(wrap_pyfunction!(check_collision, m)?)?;
    m.add_function(wrap_pyfunction!(find_insertion_point, m)?)?;

    // chain.py :: Path
    m.add_class::<PathCore>()?;

    // chain.py :: OrbChain numeric hot paths
    m.add_function(wrap_pyfunction!(maintain_spacing_sorted, m)?)?;
    m.add_function(wrap_pyfunction!(check_matches_core, m)?)?;

    Ok(())
}
