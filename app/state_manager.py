"""
Audio manager for background music and sound effects
"""

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, QVariantAnimation, QEasingCurve
from pathlib import Path
import os

class AudioManager:
    """Manages all game audio (BGM and SFX)"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        
        # Audio path - try multiple possible locations
        self.audio_path = self._find_audio_path()
        print(f"Audio Manager: Using audio path: {self.audio_path}")
        
        # Background Music Player
        self.bgm_player = QMediaPlayer()
        self.bgm_output = QAudioOutput()
        self.bgm_player.setAudioOutput(self.bgm_output)
        
        # Sound Effects Players (multiple for simultaneous sounds)
        self.sfx_players = []
        self.max_sfx_players = 10
        for _ in range(self.max_sfx_players):
            player = QMediaPlayer()
            output = QAudioOutput()
            player.setAudioOutput(output)
            self.sfx_players.append({'player': player, 'output': output, 'in_use': False})
        
        # Sound files mapping
        self.sounds = {
            'bgm': 'ancient_bgm.wav',
            'combo': 'combo.wav',
            'game_over': 'game_over.wav',
            'match': 'match.wav',
            'power': 'power.wav',
            'shoot': 'shoot.wav'
        }
        
        # Check which files exist
        self._check_audio_files()
        
        # Load settings
        self.update_volumes()
        
        # Start BGM
        self.play_bgm()
    
    def _find_audio_path(self):
        """Find audio path in multiple possible locations"""
        possible_paths = [
            Path("ancient_sfx"),
            Path(__file__).parent.parent / "ancient_sfx",
            Path.cwd() / "ancient_sfx",
        ]
        
        for path in possible_paths:
            if path.exists():
                print(f"Audio Manager: Found audio path at {path.absolute()}")
                return path
        
        # Default to first option even if doesn't exist
        print(f"Audio Manager: No audio path found, using default: {possible_paths[0].absolute()}")
        return possible_paths[0]
    
    def _check_audio_files(self):
        """Check which audio files exist"""
        print("Audio Manager: Checking audio files...")
        if not self.audio_path.exists():
            print(f"WARNING: Audio directory not found: {self.audio_path.absolute()}")
            print("Please create 'ancient_sfx' folder in the game directory")
            return
        
        for name, filename in self.sounds.items():
            filepath = self.audio_path / filename
            if filepath.exists():
                print(f"  ✓ Found: {filename}")
            else:
                print(f"  ✗ Missing: {filename}")
    
    def update_volumes(self):
        """Update volume levels from settings"""
        music_enabled = self.settings_manager.get('music_enabled', True)
        music_volume = self.settings_manager.get('music_volume', 0.7)
        sfx_enabled = self.settings_manager.get('sfx_enabled', True)
        sfx_volume = self.settings_manager.get('sfx_volume', 0.8)
        
        print(f"Audio Manager: Music enabled={music_enabled}, volume={music_volume}")
        print(f"Audio Manager: SFX enabled={sfx_enabled}, volume={sfx_volume}")
        
        # Set BGM volume
        if music_enabled:
            self.bgm_output.setVolume(music_volume)
        else:
            self.bgm_output.setVolume(0)
        
        # Set SFX volume
        self.sfx_volume = sfx_volume if sfx_enabled else 0
        for sfx in self.sfx_players:
            sfx['output'].setVolume(self.sfx_volume)
    
    def play_bgm(self):
        """Play background music"""
        bgm_file = self.audio_path / self.sounds['bgm']
        print(f"Audio Manager: Attempting to play BGM: {bgm_file.absolute()}")
        
        if bgm_file.exists():
            url = QUrl.fromLocalFile(str(bgm_file.absolute()))
            print(f"Audio Manager: BGM URL: {url.toString()}")
            
            self.bgm_player.setSource(url)
            self.bgm_player.setLoops(QMediaPlayer.Loops.Infinite)
            
            # Connect error signal
            self.bgm_player.errorOccurred.connect(self._on_bgm_error)
            self.bgm_player.mediaStatusChanged.connect(self._on_bgm_status_changed)
            
            self.bgm_player.play()
            print(f"Audio Manager: BGM play() called, state: {self.bgm_player.playbackState()}")
        else:
            print(f"Audio Manager ERROR: BGM file not found: {bgm_file.absolute()}")
    
    def _on_bgm_error(self, error, error_string):
        """Handle BGM player errors"""
        print(f"Audio Manager BGM ERROR: {error} - {error_string}")
    
    def _on_bgm_status_changed(self, status):
        """Handle BGM status changes"""
        status_names = {
            QMediaPlayer.MediaStatus.NoMedia: "NoMedia",
            QMediaPlayer.MediaStatus.LoadingMedia: "LoadingMedia",
            QMediaPlayer.MediaStatus.LoadedMedia: "LoadedMedia",
            QMediaPlayer.MediaStatus.BufferingMedia: "BufferingMedia",
            QMediaPlayer.MediaStatus.BufferedMedia: "BufferedMedia",
            QMediaPlayer.MediaStatus.EndOfMedia: "EndOfMedia",
            QMediaPlayer.MediaStatus.InvalidMedia: "InvalidMedia"
        }
        print(f"Audio Manager: BGM status changed to: {status_names.get(status, 'Unknown')}")
    
    def stop_bgm(self):
        """Stop background music"""
        self.bgm_player.stop()
        print("Audio Manager: BGM stopped")
    
    def pause_bgm(self):
        """Pause background music"""
        self.bgm_player.pause()
        print("Audio Manager: BGM paused")
    
    def resume_bgm(self):
        """Resume background music"""
        self.bgm_player.play()
        print("Audio Manager: BGM resumed")
    
    def play_sfx(self, sound_name):
        """Play sound effect"""
        if sound_name not in self.sounds:
            print(f"Audio Manager WARNING: Sound '{sound_name}' not in sound list")
            return
        
        sound_file = self.audio_path / self.sounds[sound_name]
        
        if not sound_file.exists():
            print(f"Audio Manager WARNING: SFX file not found: {sound_file.absolute()}")
            return
        
        # Find available player
        sfx_player = None
        for sfx in self.sfx_players:
            if not sfx['in_use'] or sfx['player'].playbackState() == QMediaPlayer.PlaybackState.StoppedState:
                sfx_player = sfx
                break
        
        if not sfx_player:
            # All players busy, use first one
            sfx_player = self.sfx_players[0]
        
        # Load and play sound
        url = QUrl.fromLocalFile(str(sound_file.absolute()))
        sfx_player['player'].setSource(url)
        sfx_player['output'].setVolume(self.sfx_volume)
        sfx_player['player'].play()
        sfx_player['in_use'] = True
        
        print(f"Audio Manager: Playing SFX '{sound_name}' - {sound_file.name}")
    
    def play_shoot(self):
        """Play shoot sound"""
        self.play_sfx('shoot')
    
    def play_match(self):
        """Play match sound"""
        self.play_sfx('match')
    
    def play_combo(self):
        """Play combo sound"""
        self.play_sfx('combo')
    
    def play_power(self):
        """Play power-up sound"""
        self.play_sfx('power')
    
    def play_game_over(self):
        """Play game over sound"""
        self.play_sfx('game_over')
    
    def cleanup(self):
        """Clean up audio resources"""
        self.stop_bgm()
        for sfx in self.sfx_players:
            sfx['player'].stop()
        print("Audio Manager: Cleanup complete")

    def fade_in_bgm(self, duration=2000):
        """Memutar BGM dengan efek Fade In"""
        self.play_bgm() # Mulai putar musik
    
        # Animasi volume dari 0 ke volume target (misal 0.7)
        target_volume = self.settings_manager.get('music_volume', 0.7)
    
        self.fade_anim = QVariantAnimation()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(target_volume)
        self.fade_anim.setDuration(duration)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
    
        # Update volume output setiap frame animasi
        self.fade_anim.valueChanged.connect(self.bgm_output.setVolume)
        self.fade_anim.start()

    def fade_out_bgm(self, duration=1500, stop_after=True):
        """Menurunkan volume BGM secara perlahan"""
        if self.fade_anim: self.fade_anim.stop()
        
        current_vol = self.bgm_output.volume()
        
        self.fade_anim = QVariantAnimation()
        self.fade_anim.setStartValue(current_vol)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.setDuration(duration)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_anim.valueChanged.connect(self.bgm_output.setVolume)
        
        if stop_after:
            self.fade_anim.finished.connect(self.bgm_player.stop)
            
        self.fade_anim.start()
