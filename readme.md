# 🐯 Ancient Tiger - Temple of the Orbs

<div align="center">

![Ancient Tiger Banner](https://via.placeholder.com/800x200/2C1810/FFD700?text=ANCIENT+TIGER)

**A Zuma-style arcade puzzle game with fully procedural graphics**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#-features) • [Installation](#-installation) • [How to Play](#-how-to-play) • [Architecture](#-architecture) • [Development](#-development)

</div>

---

## 📖 About

**Ancient Tiger** is a modern take on the classic Zuma-style puzzle game genre, featuring:
- 🎨 **100% Procedurally Generated Graphics** - No image assets required!
- ⚡ **Real-time Physics** - Smooth orb movement using mathematical curves
- 🌈 **Dynamic Visual Effects** - Glows, pulses, explosions, and screen shake
- 🎯 **Combo System** - Chain reactions for massive scores
- 💾 **Auto-save Progress** - Never lose your progress
- 🎮 **Increasing Difficulty** - Procedurally generated levels that scale with your skill

Journey through ancient temples, destroying chains of magical orbs before they reach the portal. Match 3 or more orbs of the same color to destroy them and build powerful combo chains!

---

## ✨ Features

### Core Gameplay
- **Classic Zuma Mechanics**: Shoot orbs at a moving chain to create matches
- **5 Orb Colors**: Red, Blue, Green, Yellow, Purple
- **Combo System**: Chain reactions multiply your score
- **Progressive Difficulty**: Each level increases speed and complexity
- **Lives System**: Three chances to master each level

### Visual Effects (All Procedural)
- **Radial Gradients**: Smooth color transitions on every orb
- **Glow Effects**: Dynamic lighting and particle systems
- **Pulse Animations**: Orbs breathe and react to gameplay
- **Screen Shake**: Impact feedback on collisions
- **Color Shifting**: Animated backgrounds that evolve with levels
- **Explosion Effects**: Satisfying destruction animations
- **Dynamic Level Themes**: 8 unique color palettes (Blue Mystery, Purple Twilight, Crimson Depths, Emerald Temple, Golden Ancient, Cyan Mystic, Magenta Void, Teal Abyss)
- **Level Transitions**: Smooth fade effects between levels
- **Danger Indicators**: Red vignette when chain approaches portal

### Technical Features
- **Modular Architecture**: Clean separation of concerns
- **Delta Time Physics**: Frame-rate independent movement
- **Path-based Movement**: Smooth curved trajectories
- **Collision Detection**: Precise orb-to-orb collision system
- **State Management**: Robust game state transitions
- **Save System**: JSON-based progress persistence
- **Audio System**: Background music and sound effects with volume control

---

## 🔊 Audio System

Ancient Tiger features a complete audio system with background music and sound effects.

### Audio Files Required

Create a folder named `ancient_sfx` in the game directory and place these files:

| File | Type | Purpose | Duration |
|------|------|---------|----------|
| `ancient_bgm.mp3` | Music | Background music (loops continuously) | 2-5 min recommended |
| `shoot.wav` | SFX | Played when firing an orb | Short (< 0.5s) |
| `match.wav` | SFX | Played when orbs match and explode | Short (< 1s) |
| `combo.wav` | SFX | Played on combo multiplier ≥3 | Short (< 1s) |
| `power.wav` | SFX | Played when swapping orbs (right click) | Short (< 0.5s) |
| `game_over.wav` | SFX | Played when losing all lives | Medium (1-2s) |

### Audio Controls

- **Settings Menu**: Toggle music/SFX on/off
- **Volume Sliders**: Separate controls for music and sound effects
- **Pause Game**: Automatically pauses background music
- **Resume Game**: Resumes background music playback

### Testing Audio

Run the audio test script to verify your audio setup:

```bash
python test_audio.py
```

This will:
1. Check if all audio files exist
2. Show file sizes
3. Open a test window with buttons to test each sound
4. Display detailed debug information in console

### Troubleshooting Audio

**No sound at all:**
1. Check if `ancient_sfx` folder exists in game directory
2. Run `python test_audio.py` to diagnose the issue
3. Check console output for error messages
4. Verify audio files are not corrupted
5. Check system volume and audio output device

**Background music not playing:**
1. Make sure `ancient_bgm.mp3` exists in `ancient_sfx/`
2. Try converting to different format (MP3, OGG, WAV)
3. Check Settings menu - Music might be disabled
4. Check console for error messages (run game from terminal)

**Sound effects not playing:**
1. Verify all `.wav` files exist in `ancient_sfx/`
2. Check Settings menu - SFX might be disabled or volume at 0
3. Try re-exporting audio files with different settings
4. Some audio codecs might not be supported - try standard WAV format

**Common Issues:**
- **Codec not supported**: Re-export as standard WAV (PCM, 44100Hz, 16-bit)
- **File path wrong**: Make sure folder is named exactly `ancient_sfx`
- **Volume at 0**: Check both in-game settings and system volume
- **Files corrupted**: Try playing files in media player first

### Audio Features

- ✅ Looping background music
- ✅ Multiple simultaneous sound effects (up to 10)
- ✅ Independent volume controls
- ✅ Persistent settings (saved to JSON)
- ✅ Auto-pause on game pause
- ✅ No audio files = graceful fallback (game still playable)

### Getting Audio Files

**Option 1: Create Your Own**
- Use tools like Audacity, FL Studio, or GarageBand
- Export as MP3 (music) or WAV (sound effects)

**Option 2: Free Resources**
- [Freesound.org](https://freesound.org) - Free sound effects
- [OpenGameArt.org](https://opengameart.org) - Free game audio
- [Incompetech](https://incompetech.com) - Royalty-free music

**Note**: Make sure you have the rights to use any audio files you add to the game.

---

## 🎮 How to Play

### Controls
- **Mouse Movement**: Aim the shooter (always follows cursor)
- **Left Click**: Fire orb
- **Right Click**: Swap current orb with next orb
- **ESC**: Pause/Resume game

### Objective
Destroy all orbs in the chain before they reach the end portal by matching 3 or more orbs of the same color.

### Gameplay Features

**Slow Motion System** ⏱️
- When the chain reaches 85% of the path, the game automatically slows down
- Gives you more time to make precise shots
- Speed gradually decreases as danger increases
- Visual indicator: Red vignette and "⚠ DANGER! ⚠" warning

**Instant Pull Together** 🔗
- When orbs are destroyed, the chain immediately snaps back together
- No waiting for gaps to close
- 3x faster pull speed = more responsive gameplay

**Beginner Friendly** 🎯
- Level 1 starts with only 4 orbs
- Very slow initial speed (12 pixels/second)
- Orbs start far back (200 units from start)
- Faster projectile speed (600 units/second)
- Longer spawn interval (2.5 seconds between new orbs)

### Scoring
- **Base Score**: 10 points per orb destroyed
- **Combo Multiplier**: Up to 10x for consecutive matches
- **Chain Reactions**: Matches that create new matches earn bonus points

### Tips
- Plan ahead - look at your next orb
- Create chain reactions for massive combos
- Target clusters to trigger multiple matches
- Don't let the chain reach the portal!

---

## 🚀 Installation

### Requirements
- Python 3.8 or higher
- PySide6 6.0 or higher

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/danx123/ancient-tiger.git
cd ancient-tiger
```

2. **Create audio folder and add sound files**
```bash
mkdir ancient_sfx
# Place your audio files in ancient_sfx/:
# - ancient_bgm.mp3 (background music)
# - combo.wav
# - game_over.wav
# - match.wav
# - power.wav
# - shoot.wav
```

3. **Install dependencies**
```bash
pip install PySide6
```

4. **Run the game**
```bash
python main.py
```

### Alternative: Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install PySide6

# Run game
python main.py
```

---

## 📁 Project Structure

```
macan_ancient/
│
├── main.py                      # Application entry point
│
├── app/                         # Application core
│   ├── app_window.py           # Main window and screen management
│   ├── game_manager.py         # Game session and progression
│   └── state_manager.py        # State machine for game flow
│
├── ui/                          # User interface
│   ├── main_menu.py            # Main menu with animated background
│   ├── hud.py                  # In-game heads-up display
│   ├── pause_menu.py           # Pause menu overlay
│   ├── settings_dialog.py      # Settings configuration dialog
│   └── overlays.py             # Additional UI overlays
│
├── games/                       # Core gameplay systems
│   ├── scene.py                # Main game scene and loop
│   ├── orb.py                  # Orb entity with rendering
│   ├── shooter.py              # Player shooter mechanics
│   ├── chain.py                # Orb chain movement system
│   ├── collision.py            # Collision detection
│   ├── powerups.py             # Power-up system (TODO)
│   └── physics.py              # Physics utilities (TODO)
│
├── logic/                       # Game logic systems
│   ├── score_system.py         # Score calculation
│   ├── combo_system.py         # Combo multiplier logic
│   ├── difficulty.py           # Difficulty scaling (TODO)
│   └── level_generator.py      # Procedural level generation (TODO)
│
├── audio/                       # Audio management
│   └── audio_manager.py        # Sound system and BGM control
│
├── services/                    # Shared services
│   ├── save_manager.py         # Save/load game state
│   └── settings_manager.py     # User settings persistence
│
├── ancient_sfx/                 # Audio files directory
│   ├── ancient_bgm.mp3         # Background music (looping)
│   ├── combo.wav               # Combo sound effect
│   ├── game_over.wav           # Game over sound
│   ├── match.wav               # Match/destroy sound
│   ├── power.wav               # Power-up/swap sound
│   └── shoot.wav               # Shoot sound effect
│
├── data/                        # Runtime data
│   └── save.json               # Save file (auto-generated)
│
└── README.md                    # This file
```

---

## 🎨 Why No Graphical Assets?

Ancient Tiger uses **100% procedural graphics** for several important reasons:

### 1. **Educational Value**
This project demonstrates advanced procedural rendering techniques:
- `QPainter` mastery for custom graphics
- `QLinearGradient` and `QRadialGradient` for smooth color transitions
- Mathematical functions (`sin`, `cos`) for organic animations
- Real-time effect generation

### 2. **Zero Dependencies**
- No need to bundle image files
- Smaller application size
- No licensing concerns for graphics
- Easier distribution and deployment

### 3. **Dynamic Visuals**
Procedural graphics enable:
- Real-time color shifting based on game state
- Infinite visual variations
- Smooth animations without sprite sheets
- Resolution-independent rendering

### 4. **Performance**
- No texture loading overhead
- GPU-accelerated vector rendering
- Efficient memory usage
- Fast startup time

### 5. **Learning Opportunity**
Perfect for understanding:
- Computer graphics fundamentals
- Color theory and gradients
- Animation mathematics
- Real-time rendering pipelines

---

## 🔧 Procedural Physics System

### Movement Algorithm

The game uses **parametric curve-based movement** for smooth, predictable orb paths:

```python
# Path generation using sinusoidal waves
for i in range(num_segments):
    progress = i / num_segments
    x = start_x + (end_x - start_x) * progress
    wave = sin(progress * π * 3) * amplitude
    y = start_y + wave
```

### Key Physics Components

1. **Delta Time Integration**
   - Frame-rate independent movement
   - `position += velocity * deltaTime`
   - Ensures consistent speed across all hardware

2. **Velocity Vectors**
   - 2D vector mathematics using `QPointF`
   - Directional movement: `(cos(angle), sin(angle)) * speed`
   - Smooth projectile trajectories

3. **Collision Detection**
   - Circle-to-circle collision using distance formula
   - `distance = sqrt((x2-x1)² + (y2-y1)²)`
   - Collision when `distance < radius1 + radius2`

4. **Path Following**
   - Orbs follow pre-calculated spline curves
   - Distance-based positioning along path
   - Maintains spacing between orbs using constraint solver

5. **Interpolation**
   - Smooth position updates between path points
   - Linear interpolation (lerp) for position
   - Easing functions for animations

---

## 🏗️ Architecture Principles

### Separation of Concerns
Each module has a single, well-defined responsibility:
- **games/**: Pure gameplay mechanics
- **ui/**: Visual presentation only
- **logic/**: Game rules and calculations
- **services/**: Shared utilities

### State Management
Centralized state machine prevents bugs:
```
MAIN_MENU → PLAYING → PAUSED → PLAYING
                    ↓
                GAME_OVER → MAIN_MENU
```

### Event-Driven Architecture
Qt signals/slots for clean communication:
- State changes emit signals
- UI components react to signals
- Decoupled components

---

## 📦 Building Executables

### Using PyInstaller

Create a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name "AncientTiger" main.py

# Find executable in dist/ folder
```

**Advanced options:**
```bash
pyinstaller --onefile \
            --windowed \
            --name "AncientTiger" \
            --icon=icon.ico \
            --add-data "README.md:." \
            main.py
```

### Using Nuitka (Better Performance)

Compile to native code for faster execution:

```bash
# Install Nuitka
pip install nuitka

# Compile (Windows)
python -m nuitka --standalone --windows-disable-console --enable-plugin=pyside6 main.py

# Compile (Linux/macOS)
python -m nuitka --standalone --enable-plugin=pyside6 main.py
```

**Benefits of Nuitka:**
- 2-3x faster startup
- Better runtime performance
- Smaller file size
- Native machine code

---

## 🎯 Roadmap

### Current Version (v1.0)
- ✅ Core Zuma gameplay
- ✅ 5 orb colors
- ✅ Combo system
- ✅ Level progression
- ✅ Save/load system
- ✅ Procedural graphics

### Future Features (v2.0)
- [ ] Power-ups (Bomb, Freeze, Fireball, Rainbow)
- [ ] Sound effects and music
- [ ] More level patterns
- [ ] Leaderboard system
- [ ] Achievement system
- [ ] Multiple game modes
- [ ] Particle effects enhancements

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to all functions
- Keep functions under 50 lines
- Write descriptive commit messages
- Test on multiple platforms

---

## 📝 License

This project is licensed under the **MIT License** - see below for details:

```
MIT License

Copyright (c) 2025 Ancient Tiger Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- Inspired by the classic **Zuma** game by PopCap Games
- Built with **PySide6** (Qt for Python)
- Uses **procedural generation** techniques from computer graphics
- Mathematical concepts from game physics simulations

---

## 📧 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/danx123/ancient-tiger/issues)
- **Discussions**: [Community discussions](https://github.com/danx123/ancient-tiger/discussions)

---

<div align="center">

**Made with ❤️ and Python**

⭐ Star this repo if you enjoy the game!

[Back to Top](#-ancient-tiger---temple-of-the-orbs)

</div>
