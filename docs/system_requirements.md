# 🎮 ANCIENT TIGER: THE BLACK HOLE ESCAPE
## System Requirements & Technical Specifications

---

## 📋 MINIMUM REQUIREMENTS

### Operating System
- **Windows:** Windows 10 (64-bit) or later
- **Linux:** Ubuntu 20.04 LTS or equivalent (64-bit)
- **macOS:** macOS 11 (Big Sur) or later

### Hardware
- **Processor:** Intel Core i3-6100 / AMD Ryzen 3 1200 or equivalent
  - Minimum: 2.0 GHz Dual-Core
- **Memory (RAM):** 4 GB RAM
- **Graphics:** Intel HD Graphics 520 or equivalent
  - Must support OpenGL 3.3 or higher
  - DirectX 11 compatible (Windows)
- **Storage:** 500 MB available space
  - Additional space needed for save files and cache
- **Display:** 1024x768 resolution minimum
  - 60 Hz refresh rate

### Software Dependencies
- **Python:** 3.8 or higher (if running from source)
- **PySide6:** Qt 6.2 or higher
- **Video Codec:** H.264 codec support for video playback
- **Audio:** DirectSound compatible (Windows) / ALSA (Linux) / CoreAudio (macOS)

---

## ⚡ RECOMMENDED REQUIREMENTS

### Operating System
- **Windows:** Windows 11 (64-bit)
- **Linux:** Ubuntu 22.04 LTS or later (64-bit)
- **macOS:** macOS 13 (Ventura) or later

### Hardware
- **Processor:** Intel Core i5-8400 / AMD Ryzen 5 2600 or better
  - Recommended: 3.0 GHz Quad-Core or higher
- **Memory (RAM):** 8 GB RAM or more
- **Graphics:** NVIDIA GeForce GTX 1050 / AMD Radeon RX 560 or better
  - Dedicated GPU with 2GB VRAM
  - Full OpenGL 4.5 support
- **Storage:** 1 GB available space (SSD recommended)
- **Display:** 1920x1080 (Full HD) or higher
  - 144 Hz refresh rate for smoother experience

### Software Dependencies
- **Python:** 3.11 or higher (if running from source)
- **PySide6:** Latest stable version
- **Graphics Drivers:** Up-to-date GPU drivers
- **Video Codec:** Hardware-accelerated H.264 decoder

---

## 🎯 OPTIMAL EXPERIENCE

### For Best Performance
- **Resolution:** 1920x1080 @ 60+ FPS
- **Graphics:** Mid-range dedicated GPU
- **CPU:** Modern quad-core processor (3.5 GHz+)
- **RAM:** 8 GB or more
- **Storage:** SSD with fast read speeds
- **Display:** IPS panel with good color accuracy

### For High-End Systems
- **Resolution:** 2560x1440 or 4K (3840x2160)
- **Graphics:** High-end GPU (RTX 3060 / RX 6600 XT or better)
- **CPU:** Modern 6-core+ processor (4.0 GHz+)
- **RAM:** 16 GB or more
- **Storage:** NVMe SSD
- **Display:** High refresh rate monitor (120Hz+)

---

## 📊 PERFORMANCE BENCHMARKS

### Low-End Systems (Minimum Specs)
- **Resolution:** 1024x768
- **FPS:** 30-40 FPS stable
- **Quality:** Low particle count, basic effects
- **Experience:** Playable, slight stuttering in intense moments

### Mid-Range Systems (Recommended Specs)
- **Resolution:** 1920x1080
- **FPS:** 60 FPS stable
- **Quality:** Full effects, smooth animations
- **Experience:** Optimal gameplay, no performance issues

### High-End Systems (Optimal Specs)
- **Resolution:** 2560x1440 or 4K
- **FPS:** 100+ FPS
- **Quality:** Maximum effects, ultra-smooth
- **Experience:** Buttery smooth, future-proof

---

## 🔧 TECHNICAL SPECIFICATIONS

### Game Engine
- **Framework:** PySide6 (Qt 6)
- **Language:** Python 3.8+
- **Graphics:** Qt Painter (2D rendering)
- **Audio:** Qt Multimedia

### Graphics Features
- **Rendering:** Hardware-accelerated 2D graphics
- **Effects:** Real-time particle systems, dynamic lighting
- **Animations:** 60 FPS smooth animations
- **Scaling:** Dynamic resolution scaling
- **Shaders:** Gradient rendering, alpha blending

### Audio Features
- **Format:** MP3, WAV support
- **Channels:** Stereo output
- **Effects:** Volume control, fade in/out
- **BGM:** Background music with looping
- **SFX:** Multiple simultaneous sound effects

### Video Features
- **Format:** MP4 (H.264)
- **Playback:** Full-screen video player
- **Controls:** Skip support (ESC key)
- **Resolution:** Up to 1080p

### Storage & Saves
- **Save Format:** JSON
- **Location:** Local AppData / User directory
- **Size:** < 1 MB per save
- **Features:** Auto-save, manual save/load
- **Cache:** Scaled image cache for performance

---

## 🌐 PLATFORM-SPECIFIC NOTES

### Windows
- DirectX 11 or higher required
- Windows Defender may flag on first run (false positive)
- Run as administrator if permission issues occur
- Supports fullscreen and windowed modes

### Linux
- X11 or Wayland display server required
- May need to install: `libgl1-mesa-glx`, `libegl1-mesa`
- Audio: ALSA or PulseAudio
- For Wayland: Set `QT_QPA_PLATFORM=wayland`

### macOS
- Requires Apple Silicon (M1/M2) or Intel processor
- May need to allow in Security & Privacy settings
- Retina display fully supported
- Native fullscreen on macOS

---

## 📱 INPUT DEVICES

### Supported
- ✅ Mouse (Required)
- ✅ Keyboard (Required)
- ✅ Trackpad (Supported but not recommended)

### Controls
- **Mouse:** Aim and shoot
- **Keyboard:** 
  - ESC - Pause/Menu
  - F11 - Fullscreen toggle
  - F12 - Cheat console
  - ~ - Cheat console (alternative)

---

## 🔊 AUDIO REQUIREMENTS

### Minimum
- Any audio output device
- Stereo speakers or headphones
- 16-bit audio support

### Recommended
- Dedicated sound card
- Quality headphones or speakers
- Surround sound capable (optional)

---

## 🌍 INTERNET CONNECTION

- **Not Required** - Fully offline game
- **Optional:** For checking updates (future feature)

---

## 💾 DISK SPACE BREAKDOWN

```
Total: ~500 MB

Game Files:           ~300 MB
├── Executable        ~100 MB
├── Graphics Assets   ~150 MB
├── Audio Files       ~30 MB
└── Videos            ~20 MB

User Data:            ~10 MB
├── Save Files        ~1 MB
├── Settings          ~1 KB
├── Achievements      ~1 KB
└── Cache             ~5 MB

Temporary Files:      ~50 MB
└── Video cache       Variable
```

---

## ⚠️ KNOWN COMPATIBILITY ISSUES

### Windows
- Windows 7 is NOT supported (EOL)
- Some antivirus may flag executable (whitelist if needed)

### Linux
- Older Mesa drivers may have rendering issues
- Update GPU drivers to latest version

### macOS
- macOS 10.x (Catalina and older) not supported
- Rosetta 2 required for Intel Macs on Apple Silicon

---

## 🔍 TROUBLESHOOTING

### Low FPS
1. Lower resolution in settings
2. Close background applications
3. Update graphics drivers
4. Enable hardware acceleration

### Video Playback Issues
1. Install K-Lite Codec Pack (Windows)
2. Update video drivers
3. Check if H.264 codec is installed

### Audio Not Working
1. Check volume in settings
2. Update audio drivers
3. Try different audio device
4. Restart the game

### Game Won't Start
1. Run as administrator (Windows)
2. Install Visual C++ Redistributable
3. Check antivirus/firewall settings
4. Verify all files are present

---

## 📞 SUPPORT & CONTACT

- **Developer:** Macan Angkasa
- **Email:** danxdigitalsolution.com

---

## 🏆 ACHIEVEMENTS SYSTEM

- **Storage:** Local JSON file
- **Total Achievements:** 36
- **Categories:** 6
- **Sync:** Local only (no cloud)

---

## 🎨 GRAPHICS SETTINGS

### Available Options
- Fullscreen toggle
- Resolution selection (automatic)
- VSync support (automatic)

### Effects
- Particle systems
- Glow effects
- Screen shake
- Smooth animations

---

## 📊 PERFORMANCE METRICS

### Target FPS
- **Minimum:** 30 FPS
- **Recommended:** 60 FPS
- **Maximum:** Uncapped (hardware limited)

### Memory Usage
- **Idle:** ~200 MB
- **Gameplay:** ~300-400 MB
- **Peak:** ~500 MB (with cache)

### CPU Usage
- **Idle:** 2-5%
- **Gameplay:** 10-20%
- **Peak:** 30-40% (intense scenes)

---

## ✅ COMPATIBILITY TESTED ON

### Windows
- ✅ Windows 10 (21H2, 22H2)
- ✅ Windows 11 (22H2, 25H2)

### Linux
- ✅ Ubuntu 20.04, 22.04
- ✅ Fedora 36, 37
- ✅ Arch Linux (latest)

### macOS
- ✅ macOS 11 (Big Sur)
- ✅ macOS 12 (Monterey)
- ✅ macOS 13 (Ventura)


---

*For the best experience, we recommend playing on a system that meets or exceeds the recommended requirements. The game is optimized for 1080p @ 60 FPS gameplay.*
