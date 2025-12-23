# Contributing to Ancient Tiger: The Black Hole Escape

First off, thank you for considering contributing to Ancient Tiger! 🎮🐯

This document provides guidelines for contributing to the project. Following these guidelines helps maintain code quality and makes the contribution process smooth for everyone.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Bug Reports](#bug-reports)
- [Feature Requests](#feature-requests)
- [Project Structure](#project-structure)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Expected Behavior

- ✅ Be respectful and inclusive
- ✅ Provide constructive feedback
- ✅ Focus on what's best for the community
- ✅ Show empathy towards others

### Unacceptable Behavior

- ❌ Harassment or discriminatory language
- ❌ Trolling or insulting comments
- ❌ Personal or political attacks
- ❌ Publishing others' private information

---

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.8 or higher
- Git installed
- Basic knowledge of Python and PySide6
- Familiarity with game development concepts

### Quick Start

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/danx123/ancient-tiger.git
   cd ancient-tiger
   ```
3. **Set up development environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. **Make your changes**
6. **Test thoroughly**
7. **Submit a pull request**

---

## 💡 How Can I Contribute?

### 1. Reporting Bugs 🐛

Found a bug? Help us fix it!

**Before submitting:**
- Check existing issues to avoid duplicates
- Test on the latest version
- Gather system information

**What to include:**
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Screenshots/videos if applicable
- System specs (OS, Python version, etc.)

### 2. Suggesting Features ✨

Have an idea? We'd love to hear it!

**Before suggesting:**
- Check if it's already proposed
- Consider if it fits the game's vision
- Think about implementation complexity

**What to include:**
- Clear description of the feature
- Why it would be valuable
- Possible implementation approach
- Mockups or examples (if applicable)

### 3. Code Contributions 💻

Ready to code? Awesome!

**Areas we need help:**
- Bug fixes
- Performance optimizations
- New game features
- UI/UX improvements
- Documentation
- Test coverage
- Platform-specific fixes

### 4. Art & Assets 🎨

Not a coder? You can still help!

- Level backgrounds
- Orb designs
- Sound effects
- Music tracks
- Video cutscenes
- Icon designs

### 5. Documentation 📚

Help others understand the game!

- Code documentation
- User guides
- Tutorials
- Translation (future)

---

## 🛠️ Development Setup

### Install Dependencies

```bash
# Required packages
pip install PySide6
pip install PySide6-Addons

# Development packages
pip install pytest
pip install black
pip install pylint
pip install mypy
```

### Project Structure

```
ancient-tiger/
├── app/                    # Core application
│   ├── app_window.py      # Main window
│   ├── game_manager.py    # Game state management
│   └── state_manager.py   # State machine
├── games/                  # Game logic
│   ├── scene.py           # Main game scene
│   ├── chain.py           # Orb chain mechanics
│   ├── orb.py             # Orb entities
│   ├── shooter.py         # Player shooter
│   ├── collision.py       # Collision detection
│   ├── physics.py         # Physics utilities
│   └── powerups.py        # Powerup system
├── ui/                     # User interface
│   ├── main_menu.py       # Main menu
│   ├── hud.py             # Heads-up display
│   ├── pause_menu.py      # Pause overlay
│   ├── settings_dialog.py # Settings UI
│   ├── achievement_viewer.py # Achievement UI
│   ├── achievement_popup.py  # Achievement notifications
│   ├── video_player.py    # Video playback
│   ├── story_viewer.py    # Story viewer
│   └── cheat_console.py   # Cheat system UI
├── services/               # Core services
│   ├── save_manager.py    # Save/load
│   ├── settings_manager.py # Settings
│   ├── achievement_system.py # Achievements
│   ├── achievement_tracker.py # Achievement tracking
│   ├── cheat_system.py    # Cheat codes
│   ├── first_run_manager.py # First run detection
│   └── image_cache.py     # Image caching
├── audio/                  # Audio system
│   └── audio_manager.py   # Audio playback
├── logic/                  # Game logic
│   ├── score_system.py    # Scoring
│   └── combo_system.py    # Combo mechanics
├── ancient_gfx/            # Graphics assets
│   ├── splash.webp        # Menu background
│   ├── scene.webp         # Level backgrounds
│   ├── shoot.png          # Shooter sprite
│   ├── trailer.mp4        # Intro video
│   ├── flying.mp4         # Transition video
│   ├── start_mode.mp4     # New game video
│   └── ending.mp4         # Game over video
├── story/                  # Story content
│   ├── story-en.txt       # English story
│   └── about.txt          # About content
└── main.py                 # Entry point
```

---

## 📝 Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

```python
# Good ✅
class GameManager:
    """Manages game state and progression"""
    
    def __init__(self):
        self.score = 0
        self.level = 1
    
    def update_score(self, points: int) -> None:
        """Update player score"""
        self.score += points

# Bad ❌
class gamemanager:
    def __init__(self):
        self.Score=0
        self.Level=1
    def updateScore(self,points):
        self.Score+=points
```

### Naming Conventions

- **Classes:** `PascalCase` (e.g., `GameManager`, `OrbChain`)
- **Functions/Methods:** `snake_case` (e.g., `update_game`, `check_collision`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_ORBS`, `DEFAULT_SPEED`)
- **Private:** `_leading_underscore` (e.g., `_internal_method`)

### Documentation

```python
def calculate_score(orbs: int, combo: int) -> int:
    """
    Calculate score based on orbs destroyed and combo multiplier.
    
    Args:
        orbs: Number of orbs destroyed
        combo: Current combo multiplier
        
    Returns:
        Total score points earned
        
    Example:
        >>> calculate_score(5, 2)
        100
    """
    base_score = orbs * 10
    return base_score * combo
```

### Code Quality

- **Keep functions small:** < 50 lines ideally
- **Single responsibility:** One function = one job
- **No magic numbers:** Use named constants
- **Error handling:** Always handle exceptions
- **Type hints:** Use where appropriate

### PySide6 Best Practices

```python
# Good ✅
class GameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

# Bad ❌
class GameWidget(QWidget):
    def __init__(self):
        super().__init__()
        QVBoxLayout(self)  # Implicit parent
```

---

## 📤 Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

```bash
# Good ✅
feat(gameplay): add powerup system
fix(collision): resolve orb overlap issue
docs(readme): update installation instructions
perf(rendering): optimize particle system

# Bad ❌
fixed stuff
update
changes
WIP
```

### Commit Message Body

```
feat(achievements): add achievement notification system

- Created popup notification widget
- Added fade-in/fade-out animations
- Connected to achievement manager signals
- Positioned at top-center of screen

Closes #123
```

---

## 🔀 Pull Request Process

### Before Submitting

1. **Update your branch:**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Test thoroughly:**
   - Run all existing tests
   - Test on multiple resolutions
   - Check for performance regressions
   - Verify no new warnings

3. **Code quality:**
   ```bash
   black .                    # Format code
   pylint your_file.py        # Lint code
   mypy your_file.py          # Type check
   ```

4. **Update documentation:**
   - Update docstrings
   - Update README if needed
   - Add comments for complex logic

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested on Windows
- [ ] Tested on Linux
- [ ] Tested on macOS
- [ ] Added/updated tests

## Screenshots
(if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Commented complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass
```

### Review Process

1. **Automated checks** must pass
2. **At least one maintainer** review required
3. **Address feedback** promptly
4. **Squash commits** if requested
5. **Maintainer merges** when approved

---

## 🐛 Bug Reports

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Launch game
2. Click 'New Game'
3. Reach level 5
4. Observe issue

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Screenshots**
(if applicable)

**System Information**
- OS: Windows 11
- Python: 3.11.0
- PySide6: 6.6.0
- GPU: NVIDIA GTX 1060

**Additional Context**
Any other relevant information

**Possible Fix**
(optional) Your thoughts on how to fix
```

---

## ✨ Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature

**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other approaches you've thought of

**Additional Context**
Mockups, examples, references

**Implementation Notes**
Technical considerations
```

---

## 🧪 Testing Guidelines

### Manual Testing Checklist

- [ ] Game launches without errors
- [ ] Main menu displays correctly
- [ ] New game starts properly
- [ ] Gameplay is smooth (60 FPS)
- [ ] All controls work
- [ ] Sound/music plays correctly
- [ ] Videos play and can be skipped
- [ ] Achievements unlock correctly
- [ ] Save/load works
- [ ] Settings persist
- [ ] Pause/resume works
- [ ] Game over flow correct
- [ ] No memory leaks (play 30+ minutes)

### Performance Testing

- Test on minimum spec hardware
- Monitor FPS during intense gameplay
- Check memory usage over time
- Profile rendering performance
- Test different resolutions

### Platform Testing

- Windows 10/11
- Ubuntu 20.04+
- macOS 11+

---

## 📖 Documentation

### Code Documentation

```python
class OrbChain:
    """
    Manages chain of orbs moving along a path.
    
    The OrbChain handles orb spawning, movement, collision detection,
    and match detection along a predefined path.
    
    Attributes:
        path: Path object defining the orb movement trajectory
        orbs: List of Orb objects in the chain
        speed: Movement speed in pixels per second
        level: Current difficulty level
        
    Example:
        >>> path = Path(width=1366, height=768, level=1)
        >>> chain = OrbChain(path, level=1)
        >>> chain.update(0.016)  # Update with delta time
    """
```

### User Documentation

- Keep it simple and clear
- Use screenshots/GIFs
- Provide examples
- Link related topics
- Keep it updated

---

## 🎯 Development Priorities

### High Priority
- Bug fixes (crashes, game-breaking issues)
- Performance optimization
- Platform compatibility

### Medium Priority
- New features
- UI improvements
- Additional content

### Low Priority
- Nice-to-have features
- Code refactoring
- Minor improvements

---

## 🔍 Code Review Checklist

### For Reviewers

- [ ] Code follows style guidelines
- [ ] Logic is clear and correct
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Tests are adequate
- [ ] Documentation is updated
- [ ] No breaking changes (or properly noted)

### For Contributors

- [ ] Self-reviewed code
- [ ] Tested all changes
- [ ] Updated documentation
- [ ] No debug code left
- [ ] No commented-out code
- [ ] Meaningful variable names
- [ ] Proper error handling

---

## 🌍 Community

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** General discussion
- **Discord:** Real-time chat (coming soon)
- **Email:** support@macangames.com

### Getting Help

- Check documentation first
- Search existing issues
- Ask in discussions
- Be specific and provide context

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in game credits (major contributions)
- Acknowledged in release notes

---

## 📞 Contact

- **Project Lead:** Macan Angkasa
- **Email:** danxdigitalsolution@gmail.com


---

## 🎉 Thank You!

Every contribution, no matter how small, helps make Ancient Tiger better. We appreciate your time and effort!

Happy coding! 🎮🐯✨


