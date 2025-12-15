# 🛠️ Ancient Tiger - Developer Guide

Complete guide for developers working on or extending Ancient Tiger.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Code Organization](#code-organization)
3. [Procedural Graphics System](#procedural-graphics-system)
4. [Physics Engine](#physics-engine)
5. [Adding New Features](#adding-new-features)
6. [Performance Optimization](#performance-optimization)
7. [Testing](#testing)
8. [Debugging Tips](#debugging-tips)

---

## Architecture Overview

### Design Patterns Used

**1. Model-View-Controller (MVC)**
- **Model**: `games/`, `logic/` - Game state and rules
- **View**: `ui/` - Visual presentation
- **Controller**: `app/` - User input and coordination

**2. State Machine**
- Centralized state management via `StateManager`
- Clean state transitions
- Prevents invalid state combinations

**3. Component-Based Architecture**
- Each orb, chain, shooter is independent
- Loose coupling via interfaces
- Easy to extend and test

**4. Observer Pattern**
- Qt Signals/Slots for event communication
- Decoupled components
- Easy debugging of event flow

---

## Code Organization

### Module Responsibilities

#### `app/` - Application Core
```python
app_window.py      # Main window, screen management
game_manager.py    # Session state, progression
state_manager.py   # State machine implementation
```

**Key Classes:**
- `AppWindow`: Main application window
- `GameManager`: Manages game session data
- `StateManager`: Handles state transitions

#### `games/` - Gameplay Systems
```python
scene.py          # Main game loop, rendering
orb.py           # Orb entity with rendering
shooter.py       # Player shooter mechanics
chain.py         # Orb chain movement
collision.py     # Collision detection
physics.py       # Physics utilities
powerups.py      # Power-up system
```

**Key Classes:**
- `GameScene`: Main game loop
- `Orb`: Individual orb entity
- `OrbChain`: Chain management
- `Shooter`: Player shooter
- `CollisionDetector`: Collision handling

#### `ui/` - User Interface
```python
main_menu.py     # Main menu
hud.py          # In-game HUD
pause_menu.py   # Pause overlay
overlays.py     # Victory/game over screens
```

#### `logic/` - Game Logic
```python
score_system.py   # Score calculation
combo_system.py   # Combo multipliers
```

#### `services/` - Utilities
```python
save_manager.py      # Save/load game
settings_manager.py  # User settings
```

---

## Procedural Graphics System

### QPainter Rendering Pipeline

All graphics are rendered using Qt's `QPainter`:

```python
def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 1. Background
    self._draw_background(painter)
    
    # 2. Game objects
    self.chain.draw(painter)
    self.shooter.draw(painter)
    
    # 3. Effects
    self._draw_effects(painter)
```

### Gradient System

**Radial Gradients** (Orbs, glows):
```python
gradient = QRadialGradient(center, radius)
gradient.setColorAt(0, light_color)    # Center
gradient.setColorAt(0.6, base_color)   # Mid
gradient.setColorAt(1, dark_color)     # Edge
```

**Linear Gradients** (Backgrounds):
```python
gradient = QLinearGradient(start, end)
gradient.setColorAt(0, color1)
gradient.setColorAt(1, color2)
```

### Animation Techniques

**1. Pulsing Effect**
```python
pulse = math.sin(time * frequency) * amplitude
current_radius = base_radius + pulse
```

**2. Color Shifting**
```python
hue = (time * speed + offset) % 360
color = QColor.fromHsv(hue, saturation, value)
```

**3. Screen Shake**
```python
shake_x = math.sin(time * 50) * intensity
shake_y = math.cos(time * 50) * intensity
painter.translate(shake_x, shake_y)
```

**4. Trail Effects**
```python
for i, pos in enumerate(trail):
    alpha = int(255 * (i / len(trail)))
    color.setAlpha(alpha)
    # Draw fading trail
```

---

## Physics Engine

### Delta Time Integration

All movement is frame-rate independent:

```python
def update(self, dt):
    # dt = time since last frame (seconds)
    self.position += self.velocity * dt
    self.rotation += self.angular_velocity * dt
```

### Path-Based Movement

Orbs follow pre-calculated curves:

```python
class Path:
    def get_position_at_distance(self, distance):
        # Find segment containing distance
        # Interpolate within segment
        # Return smooth position
```

### Collision Detection

Circle-to-circle collision:

```python
def check_collision(orb1, orb2):
    dx = orb2.x - orb1.x
    dy = orb2.y - orb1.y
    distance = sqrt(dx*dx + dy*dy)
    return distance < (orb1.radius + orb2.radius)
```

### Velocity Vectors

Directional movement:

```python
velocity = QPointF(
    cos(angle) * speed,
    sin(angle) * speed
)
position += velocity * dt
```

---

## Adding New Features

### Adding a New Orb Color

1. **Define color in `orb.py`:**
```python
class OrbType:
    NEW_COLOR = 8

ORB_COLORS = {
    OrbType.NEW_COLOR: (R, G, B)
}
```

2. **Add to random generation:**
```python
@staticmethod
def random_type():
    return random.choice([
        OrbType.RED, OrbType.BLUE, 
        OrbType.NEW_COLOR  # Add here
    ])
```

### Adding a Power-Up

1. **Define in `powerups.py`:**
```python
class PowerUpType(Enum):
    MY_POWERUP = "my_powerup"
```

2. **Implement effect in `scene.py`:**
```python
def apply_powerup(self, powerup):
    if powerup.type == PowerUpType.MY_POWERUP:
        # Implement effect
        pass
```

3. **Add visual representation in `orb.py`:**
```python
def draw(self, painter):
    if self.orb_type == OrbType.MY_POWERUP:
        # Custom rendering
        pass
```

### Adding a New Game Mode

1. **Create mode class in `logic/`:**
```python
class TimeAttackMode:
    def __init__(self):
        self.time_limit = 60
        
    def update(self, dt):
        self.time_limit -= dt
```

2. **Integrate in `game_manager.py`:**
```python
def set_game_mode(self, mode):
    self.current_mode = mode
```

3. **Update UI in `main_menu.py`:**
```python
mode_selector = QComboBox()
mode_selector.addItems(["Classic", "Time Attack"])
```

---

## Performance Optimization

### Profiling

Use Python's profiler:

```bash
python -m cProfile -o profile.stats main.py
python -m pstats profile.stats
```

### Optimization Tips

**1. Reduce Draw Calls**
```python
# Bad: Draw each orb separately
for orb in orbs:
    painter.drawEllipse(orb.pos, orb.radius)

# Good: Batch similar operations
painter.setBrush(color)
for orb in orbs:
    painter.drawEllipse(orb.pos, orb.radius)
```

**2. Cull Off-Screen Objects**
```python
def draw(self, painter):
    if self.is_visible(painter.viewport()):
        self._draw_orb(painter)
```

**3. Pre-calculate Expensive Operations**
```python
# Bad: Calculate every frame
radius = math.sqrt(x*x + y*y)

# Good: Cache results
if not self.radius_cached:
    self.radius = math.sqrt(x*x + y*y)
    self.radius_cached = True
```

**4. Use Object Pooling**
```python
class OrbPool:
    def __init__(self, size=100):
        self.pool = [Orb() for _ in range(size)]
        
    def acquire(self):
        return self.pool.pop() if self.pool else Orb()
```

---

## Testing

### Unit Testing

Create `tests/` directory:

```python
# tests/test_orb.py
import unittest
from games.orb import Orb, OrbType

class TestOrb(unittest.TestCase):
    def test_orb_creation(self):
        orb = Orb(100, 100, OrbType.RED)
        self.assertEqual(orb.orb_type, OrbType.RED)
        
    def test_orb_matching(self):
        orb1 = Orb(0, 0, OrbType.RED)
        orb2 = Orb(0, 0, OrbType.RED)
        self.assertTrue(orb1.matches(orb2))
```

Run tests:
```bash
python -m unittest discover tests
```

### Integration Testing

Test complete game flows:

```python
def test_game_session():
    # Start game
    game = GameManager()
    game.new_game()
    
    # Simulate gameplay
    # Verify state transitions
    assert game.current_level == 1
```

---

## Debugging Tips

### Enable Debug Logging

Add to `main.py`:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Use in code:
```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Orb position: {self.pos}")
logger.info(f"Score: {self.score}")
logger.warning("Collision detected")
```

### Visual Debugging

Draw debug info:

```python
def paintEvent(self, event):
    painter = QPainter(self)
    
    # Draw collision boxes
    if DEBUG_MODE:
        painter.setPen(QPen(QColor(255, 0, 0)))
        for orb in self.orbs:
            painter.drawRect(orb.get_bounds())
```

### Performance Monitoring

Add FPS counter:

```python
class GameScene:
    def __init__(self):
        self.frame_count = 0
        self.fps = 0
        self.fps_timer = 0
        
    def update(self, dt):
        self.frame_count += 1
        self.fps_timer += dt
        
        if self.fps_timer >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_timer = 0
```

### Common Issues

**1. Orbs not matching:**
- Check color comparison logic
- Verify orb type assignment
- Debug with print statements

**2. Physics jitter:**
- Ensure delta time is properly passed
- Check for floating-point errors
- Limit maximum velocity

**3. Memory leaks:**
- Check for circular references
- Ensure objects are properly removed
- Use weak references where appropriate

---

## Build Process

### Development Build

```bash
python main.py
```

### Release Build (PyInstaller)

```bash
# Windows
pyinstaller --onefile --windowed ^
    --name "AncientTiger" ^
    --icon=icon.ico ^
    main.py

# macOS/Linux
pyinstaller --onefile --windowed \
    --name "AncientTiger" \
    main.py
```

### Release Build (Nuitka)

```bash
# Compile with optimizations
python -m nuitka --standalone \
    --enable-plugin=pyside6 \
    --windows-disable-console \
    --onefile \
    main.py
```

---

## Contributing Guidelines

### Code Style

Follow PEP 8:
- 4 spaces for indentation
- Max line length: 88 characters
- Use descriptive variable names

### Commit Messages

Format:
```
[Component] Brief description

Detailed explanation if needed

Fixes #123
```

Examples:
```
[Orb] Add rainbow orb matching logic
[Physics] Fix collision detection edge case
[UI] Improve main menu animations
```

### Pull Request Process

1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Submit PR with description
5. Address review comments
6. Merge when approved

---

## Resources

### Qt Documentation
- [QPainter Reference](https://doc.qt.io/qt-6/qpainter.html)
- [QGradient Guide](https://doc.qt.io/qt-6/qgradient.html)
- [Qt Graphics View](https://doc.qt.io/qt-6/graphicsview.html)

### Game Development
- [Game Programming Patterns](https://gameprogrammingpatterns.com/)
- [Math for Game Developers](https://www.youtube.com/playlist?list=PLW3Zl3wyJwWOpdhYedlD-yCB7WQoHf-My)

### Python Best Practices
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Patterns](https://python-patterns.guide/)

---

## Support

- **Issues**: [GitHub Issues](https://github.com/danx123/ancient-tiger/issues)
- **Discussions**: [GitHub Discussions](https://github.com/danx123/ancient-tiger/discussions)


---

**Happy Coding! 🐯**
