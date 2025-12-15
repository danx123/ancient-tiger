# 🔊 Audio Setup Guide - Ancient Tiger

## Quick Setup

### Step 1: Create Audio Folder

In your game directory (where `main.py` is located), create a folder named:

```
ancient_sfx
```

**Full path should look like:**
```
your_game_folder/
├── ancient_sfx/        ← Create this folder
├── main.py
├── app/
├── games/
└── ...
```

### Step 2: Add Audio Files

Place these 6 files inside the `ancient_sfx/` folder:

| Filename | Type | Description |
|----------|------|-------------|
| `ancient_bgm.mp3` | Music | Background music (will loop) |
| `shoot.wav` | SFX | Sound when shooting orb |
| `match.wav` | SFX | Sound when orbs match |
| `combo.wav` | SFX | Sound on combo multiplier |
| `power.wav` | SFX | Sound when swapping orbs |
| `game_over.wav` | SFX | Sound on game over |

### Step 3: Verify Setup

Run the test script:

```bash
python test_audio.py
```

You should see:
```
==================================================
AUDIO FILES CHECK
==================================================
✓ Found audio folder: C:\your\path\ancient_sfx

✓ ancient_bgm.mp3      (Background Music     ) - 2345.6 KB
✓ shoot.wav            (Shoot Sound          ) - 12.3 KB
✓ match.wav            (Match Sound          ) - 45.6 KB
✓ combo.wav            (Combo Sound          ) - 23.4 KB
✓ power.wav            (Power Sound          ) - 18.9 KB
✓ game_over.wav        (Game Over Sound      ) - 56.7 KB
==================================================
```

### Step 4: Test Sounds

The test window will open. Click each button to test sounds:
- ▶ Play Background Music
- 🎯 Test Shoot Sound
- 💥 Test Match Sound
- 🔥 Test Combo Sound
- ⚡ Test Power Sound
- ☠️ Test Game Over Sound

---

## Audio File Specifications

### Background Music (ancient_bgm.mp3)
- **Format**: MP3, OGG, or WAV
- **Duration**: 2-5 minutes recommended (will loop)
- **Quality**: 128-320 kbps
- **Style**: Mysterious, ancient temple theme

### Sound Effects (.wav files)
- **Format**: WAV (PCM, 16-bit, 44100Hz recommended)
- **Duration**: 
  - shoot.wav: 0.1-0.5 seconds
  - match.wav: 0.5-1.0 seconds
  - combo.wav: 0.5-1.0 seconds
  - power.wav: 0.2-0.5 seconds
  - game_over.wav: 1.0-2.0 seconds
- **Quality**: Standard WAV quality

---

## Where to Get Audio Files

### Free Resources

**Music:**
- [Incompetech](https://incompetech.com/music/) - Royalty-free music
- [FreePD](https://freepd.com/) - Public domain music
- [OpenGameArt](https://opengameart.org/art-search-advanced?keys=&field_art_type_tid%5B%5D=12) - Game music

**Sound Effects:**
- [Freesound](https://freesound.org/) - Large library of free sounds
- [OpenGameArt](https://opengameart.org/art-search-advanced?keys=&field_art_type_tid%5B%5D=13) - Game SFX
- [Zapsplat](https://www.zapsplat.com/) - Free sound effects

### Search Keywords

For Background Music:
- "ancient temple music"
- "mysterious ambience"
- "ethnic instrumental"
- "adventure game music"

For Sound Effects:
- "shoot pop" or "bubble pop"
- "explosion" or "burst"
- "power up"
- "game over"

### Creating Your Own

Use these free tools:
- [Audacity](https://www.audacityteam.org/) - Audio editing
- [LMMS](https://lmms.io/) - Music creation
- [Bfxr](https://www.bfxr.net/) - 8-bit sound effects generator

---

## Troubleshooting

### "Audio folder not found"

**Solution:**
```bash
# Windows
mkdir ancient_sfx

# Linux/Mac
mkdir ancient_sfx
```

Make sure you're in the game directory (same folder as `main.py`)!

### "File not playing"

**Possible causes:**
1. **Wrong filename** - Must be exact: `ancient_bgm.mp3`, not `ancient_bgm (1).mp3`
2. **Wrong location** - Files must be in `ancient_sfx/`, not in subfolders
3. **Corrupted file** - Try opening in media player first
4. **Unsupported codec** - Re-export as standard WAV

**Quick fix:**
```bash
# Navigate to game folder
cd path/to/ancient_tiger

# List files (should show ancient_sfx folder)
dir          # Windows
ls           # Linux/Mac

# List audio files
dir ancient_sfx       # Windows
ls ancient_sfx        # Linux/Mac
```

### "Audio plays but very quiet"

1. Open Settings in game
2. Check Music Volume slider (should be 70-100%)
3. Check SFX Volume slider (should be 70-100%)
4. Verify "Enable Music" is checked
5. Verify "Enable Sound Effects" is checked

### "Background music stutters or loops wrong"

- Re-export music file with better quality
- Try converting MP3 → WAV or vice versa
- Ensure file isn't corrupted
- Check CPU usage (close other programs)

---

## Example: Converting Audio Files

### Using Audacity

1. Open audio file in Audacity
2. For SFX: `File > Export > Export as WAV`
   - Format: WAV (Microsoft)
   - Encoding: Signed 16-bit PCM
3. For Music: `File > Export > Export as MP3`
   - Quality: 192-320 kbps

### Using FFmpeg (Command Line)

```bash
# Convert to WAV
ffmpeg -i input.mp3 -acodec pcm_s16le -ar 44100 output.wav

# Convert to MP3
ffmpeg -i input.wav -codec:a libmp3lame -qscale:a 2 output.mp3
```

---

## Summary Checklist

- [ ] Created `ancient_sfx/` folder in game directory
- [ ] Added `ancient_bgm.mp3` (background music)
- [ ] Added `shoot.wav` (shoot sound)
- [ ] Added `match.wav` (match sound)
- [ ] Added `combo.wav` (combo sound)
- [ ] Added `power.wav` (power sound)
- [ ] Added `game_over.wav` (game over sound)
- [ ] Ran `python test_audio.py` successfully
- [ ] Tested all sounds in test window
- [ ] Launched game and verified audio works
- [ ] Adjusted volume in Settings menu

**When all checkboxes are complete, your audio system is ready!** ✅

---

## Need Help?

If audio still doesn't work after following this guide:

1. Run `python test_audio.py` and copy the console output
2. Check if files play in Windows Media Player / VLC
3. Verify file sizes (should not be 0 KB)
4. Make sure files aren't read-only
5. Try moving files to a different location and back

**Still having issues?** The game will still work without audio - it just won't have sound! 🎮
