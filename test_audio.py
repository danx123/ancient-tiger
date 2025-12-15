"""
Test script to verify audio system
Run this before starting the game to test audio
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from pathlib import Path

# Test if audio files exist
def check_audio_files():
    audio_path = Path("ancient_sfx")
    
    print("\n" + "="*50)
    print("AUDIO FILES CHECK")
    print("="*50)
    
    if not audio_path.exists():
        print(f"❌ ERROR: 'ancient_sfx' folder not found!")
        print(f"   Please create folder at: {audio_path.absolute()}")
        return False
    
    print(f"✓ Found audio folder: {audio_path.absolute()}\n")
    
    required_files = {
        'ancient_bgm.mp3': 'Background Music',
        'shoot.wav': 'Shoot Sound',
        'match.wav': 'Match Sound',
        'combo.wav': 'Combo Sound',
        'power.wav': 'Power Sound',
        'game_over.wav': 'Game Over Sound'
    }
    
    all_found = True
    for filename, description in required_files.items():
        filepath = audio_path / filename
        if filepath.exists():
            size = filepath.stat().st_size / 1024  # KB
            print(f"✓ {filename:20s} ({description:20s}) - {size:.1f} KB")
        else:
            print(f"❌ {filename:20s} ({description:20s}) - NOT FOUND")
            all_found = False
    
    print("="*50 + "\n")
    return all_found

class AudioTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ancient Tiger - Audio Test")
        self.setMinimumSize(400, 500)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🔊 Audio System Test")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFD700;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Info
        info = QLabel("Click buttons to test each sound")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        layout.addSpacing(20)
        
        # Initialize audio manager
        try:
            from services.settings_manager import SettingsManager
            from audio.audio_manager import AudioManager
            
            self.settings_manager = SettingsManager()
            self.audio_manager = AudioManager(self.settings_manager)
            
            status_label = QLabel("✓ Audio Manager Initialized")
            status_label.setStyleSheet("color: green; font-weight: bold;")
            status_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(status_label)
            
        except Exception as e:
            status_label = QLabel(f"❌ Error: {str(e)}")
            status_label.setStyleSheet("color: red; font-weight: bold;")
            status_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(status_label)
            self.audio_manager = None
        
        layout.addSpacing(20)
        
        # Test buttons
        button_style = """
            QPushButton {
                background: #8B4513;
                color: white;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #A0522D;
            }
        """
        
        if self.audio_manager:
            # BGM controls
            bgm_play = QPushButton("▶ Play Background Music")
            bgm_play.setStyleSheet(button_style)
            bgm_play.clicked.connect(self.test_bgm_play)
            layout.addWidget(bgm_play)
            
            bgm_pause = QPushButton("⏸ Pause Background Music")
            bgm_pause.setStyleSheet(button_style)
            bgm_pause.clicked.connect(self.test_bgm_pause)
            layout.addWidget(bgm_pause)
            
            bgm_stop = QPushButton("⏹ Stop Background Music")
            bgm_stop.setStyleSheet(button_style)
            bgm_stop.clicked.connect(self.test_bgm_stop)
            layout.addWidget(bgm_stop)
            
            layout.addSpacing(10)
            
            # SFX buttons
            sfx_buttons = [
                ("🎯 Test Shoot Sound", self.test_shoot),
                ("💥 Test Match Sound", self.test_match),
                ("🔥 Test Combo Sound", self.test_combo),
                ("⚡ Test Power Sound", self.test_power),
                ("☠️ Test Game Over Sound", self.test_gameover),
            ]
            
            for text, callback in sfx_buttons:
                btn = QPushButton(text)
                btn.setStyleSheet(button_style)
                btn.clicked.connect(callback)
                layout.addWidget(btn)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #2C1810;")
    
    def test_bgm_play(self):
        print("\n▶ Testing BGM Play...")
        self.audio_manager.play_bgm()
    
    def test_bgm_pause(self):
        print("\n⏸ Testing BGM Pause...")
        self.audio_manager.pause_bgm()
    
    def test_bgm_stop(self):
        print("\n⏹ Testing BGM Stop...")
        self.audio_manager.stop_bgm()
    
    def test_shoot(self):
        print("\n🎯 Testing Shoot Sound...")
        self.audio_manager.play_shoot()
    
    def test_match(self):
        print("\n💥 Testing Match Sound...")
        self.audio_manager.play_match()
    
    def test_combo(self):
        print("\n🔥 Testing Combo Sound...")
        self.audio_manager.play_combo()
    
    def test_power(self):
        print("\n⚡ Testing Power Sound...")
        self.audio_manager.play_power()
    
    def test_gameover(self):
        print("\n☠️ Testing Game Over Sound...")
        self.audio_manager.play_game_over()

def main():
    # First check if files exist
    files_ok = check_audio_files()
    
    if not files_ok:
        print("\n⚠️  WARNING: Some audio files are missing!")
        print("   The game will run but without sound.")
        print("\nTo fix this:")
        print("1. Create folder: ancient_sfx")
        print("2. Add these files to the folder:")
        print("   - ancient_bgm.mp3")
        print("   - shoot.wav")
        print("   - match.wav")
        print("   - combo.wav")
        print("   - power.wav")
        print("   - game_over.wav\n")
        
        response = input("Continue with test window? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Show test window
    app = QApplication(sys.argv)
    window = AudioTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()