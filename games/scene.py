"""
Main game scene - handles gameplay loop and rendering
FIXED: 
1. Game Over message persisting after reload
2. Combo timer not updating (causing infinite combo)
3. Better combo reset logic
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QRadialGradient, QFont
from games.shooter import Shooter
from games.chain import OrbChain, Path
from games.collision import CollisionDetector
from games.orb import Orb
from ui.hud import HUD
from logic.combo_system import ComboSystem
from app.state_manager import GameState
from games.powerups import PowerUpManager
import math

class GameScene(QWidget):
    """Main gameplay scene"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent_window = parent
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        
        # Game logic resolution
        self.logical_width = 1366
        self.logical_height = 768
        
        # Game state
        self.running = False
        self.paused = False
        self.level = 1
        self.score = 0
        self.show_level_complete = False
        self.show_game_over_message = False
        self.show_retry_message = False
        self.level_transition = False
        self.level_transition_progress = 0
        
        # Game objects
        self.shooter = None
        self.chain = None
        self.path = None
        self.collision_detector = CollisionDetector()
        self.combo_system = ComboSystem()
        self.powerup_manager = PowerUpManager(self)
        
        # HUD
        self.hud = HUD(self)
        
        # Animation
        self.animation_time = 0
        self.screen_shake = 0
        
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.last_time = 0
        
        # Portal
        self.portal_pos = None
        self.portal_radius = 40
        
        # Gameplay assists
        self.slow_motion_active = False
        self.slow_motion_factor = 1.0
        
        print(f"GameScene: Initialized. Parent has audio: {self._has_audio()}")
    
    def _has_audio(self):
        """Check if audio manager is available"""
        return (hasattr(self.parent_window, 'game_manager') and 
                hasattr(self.parent_window.game_manager, 'audio_manager') and
                self.parent_window.game_manager.audio_manager is not None)
    
    def _play_audio(self, method_name):
        """Safely play audio"""
        if self._has_audio():
            try:
                method = getattr(self.parent_window.game_manager.audio_manager, method_name)
                method()
            except Exception as e:
                print(f"GameScene: Audio error - {method_name}: {e}")
        
    def start_new_game(self, level=1):
        """Start a new game - FIXED: Clear all game over flags"""
        # Clear ALL message flags first
        self.show_level_complete = False
        self.show_game_over_message = False
        self.show_retry_message = False
        
        # Start level transition effect
        if hasattr(self, 'level') and self.level != level and level > 1:
            self.level_transition = True
            self.level_transition_progress = 0
        
        self.level = level
        
        # Load total score from GameManager
        self.score = self.parent_window.game_manager.total_score
        
        self.running = True
        self.paused = False
        
        print(f"GameScene: Starting new game - Level {level} - Score: {self.score}")
        
        # Setup game objects
        self.shooter = Shooter(self.logical_width // 2, self.logical_height - 100)
        
        self.path = Path(self.logical_width, self.logical_height, min(self.level, 5), self.level - 1)
        self.chain = OrbChain(self.path, self.level)
        self.portal_pos = self.path.get_end_position()
        
        # Reset combo
        self.combo_system.reset()
        
        # Update HUD
        self.hud.update_level(self.level)
        self.hud.update_score(self.score)
        current_high = self.parent_window.game_manager.high_score
        self.hud.update_high_score(max(self.score, current_high))

        # Reset powerups
        self.powerup_manager = PowerUpManager(self)
        
        # Start/Resume BGM
        self._play_audio('play_bgm')
        
        # Start game loop
        self.timer.start(16)

    def _map_to_logical(self, physical_pos):
        """Convert screen mouse coordinates to logical game coordinates"""
        scale_x = self.width() / self.logical_width
        scale_y = self.height() / self.logical_height
        scale = min(scale_x, scale_y)
        
        offset_x = (self.width() - (self.logical_width * scale)) / 2
        offset_y = (self.height() - (self.logical_height * scale)) / 2
        
        logical_x = (physical_pos.x() - offset_x) / scale
        logical_y = (physical_pos.y() - offset_y) / scale
        return QPointF(logical_x, logical_y)

    def handle_matches(self, matches):
        """Handle matched orb sequences - FIXED: Only count legitimate matches for combo"""
        if not matches:
            return
            
        total_removed = 0
        has_powerup = False
        
        for match_indices in matches:
            # Check for PowerUps in the match
            for idx in match_indices:
                if idx < len(self.chain.orbs):
                    orb = self.chain.orbs[idx]
                    if orb.is_powerup():
                        self.powerup_manager.activate_powerup(orb.orb_type, orb)
                        has_powerup = True
            
            self.chain.remove_orbs(match_indices)
            total_removed += len(match_indices)
        
        # Only process if orbs were actually removed
        if total_removed == 0:
            return
        
        # Play match sound
        self._play_audio('play_match')
            
        # Update score with combo
        base_score = total_removed * 10
        combo_multiplier = self.combo_system.add_match(total_removed)
        self.score += int(base_score * combo_multiplier)
        
        # Update High Score Realtime
        self.parent_window.game_manager.check_high_score(self.score)
        
        # Play combo sound for high combos
        if combo_multiplier >= 3:
            self._play_audio('play_combo')
        
        # Update HUD
        self.hud.update_score(self.score)
        self.hud.update_combo(self.combo_system.current_combo)
        self.hud.update_high_score(self.parent_window.game_manager.high_score)
        
        # Screen shake
        self.screen_shake = 0.2

    def level_complete(self):
        """Handle level completion"""
        if hasattr(self, 'show_level_complete') and self.show_level_complete:
            return

        self.running = False
        
        # Save level score
        self.parent_window.game_manager.level_completed(self.score)
        
        print(f"GameScene: Level {self.level} completed! Total Score: {self.score}")
        
        self._show_level_complete_message()
        
        next_level = self.parent_window.game_manager.current_level
        QTimer.singleShot(3000, lambda: self.start_new_game(next_level))
        
    def stop_game(self):
        """Stop game"""
        self.running = False
        self.timer.stop()
        
    def pause_game(self):
        """Pause game"""
        self.paused = True
        self._play_audio('pause_bgm')
        
    def resume_game(self):
        """Resume game"""
        self.paused = False
        self._play_audio('resume_bgm')
        
    def game_loop(self):
        """Main game loop"""
        if not self.running or self.paused:
            return
            
        current_time = self.timer.interval()
        dt = current_time / 1000.0
        self.update_game(dt)
        self.update()
        
    def update_game(self, dt):
        """Update game logic - FIXED: Combo timer now updates properly"""
        self.animation_time += dt
        
        if self.level_transition:
            self.level_transition_progress += dt * 2
            if self.level_transition_progress >= 1.0:
                self.level_transition = False
                self.level_transition_progress = 0
            return
        
        self.powerup_manager.update(dt)
        speed_mult = self.powerup_manager.get_speed_multiplier()

        if self.chain:
            head_distance = self.chain.get_head_distance()
            danger_threshold = self.path.total_length * 0.85
            
            if head_distance >= danger_threshold:
                self.slow_motion_active = True
                danger_level = (head_distance - danger_threshold) / (self.path.total_length - danger_threshold)
                self.slow_motion_factor = 1.0 - (danger_level * 0.4)
            else:
                self.slow_motion_active = False
                self.slow_motion_factor = 1.0
            
            final_dt = dt * self.slow_motion_factor * speed_mult
        else:
            final_dt = dt
        
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - dt * 5)
        
        if self.shooter:
            self.shooter.update(dt)
            
        if self.chain:
            self.chain.update(final_dt)
            
            # CRITICAL FIX: Remove exploded orbs after update
            self.chain.orbs = [orb for orb in self.chain.orbs if not orb.marked_for_removal]
            
            if self.chain.get_head_distance() >= self.path.total_length:
                self.game_over()
                return
            
        if self.shooter and self.shooter.projectile and self.chain:
            collision = self.collision_detector.check_collision(
                self.shooter.projectile, self.chain
            )
            if collision:
                self.handle_collision(collision)
                
        if self.chain:
            matches = self.chain.check_matches()
            if matches:
                print(f"Scene: Matches detected! Count: {len(matches)}")
                self.handle_matches(matches)
            else:
                # Reset combo if no matches for too long
                pass
        
        # Victory Check
        if self.chain and self.running and not self.show_level_complete:
            remaining_to_spawn = self.chain.max_total_orbs - self.chain.orbs_spawned
            if len(self.chain.orbs) == 0 and remaining_to_spawn <= 0:
                print("GameScene: LEVEL COMPLETE - All orbs destroyed!")
                self.level_complete()
        
        # FIXED: Update combo system timer
        self.combo_system.update(dt)
        
    def handle_collision(self, collision):
        """Handle projectile collision with chain - FIXED: Use proper insert method"""
        projectile = collision['projectile']
        index = collision['index']
        
        new_orb = Orb(
            projectile.orb.pos.x(),
            projectile.orb.pos.y(),
            projectile.orb.orb_type
        )
        
        # Calculate proper path distance for insertion
        if index < len(self.chain.orbs):
            collision_orb = self.chain.orbs[index]
            new_orb.path_distance = collision_orb.path_distance - self.chain.distance_between_orbs / 2
        else:
            if self.chain.orbs:
                new_orb.path_distance = self.chain.orbs[-1].path_distance + self.chain.distance_between_orbs
            else:
                new_orb.path_distance = 0
        
        # FIXED: Use chain's insert_orb method which handles cooldown
        self.chain.insert_orb(new_orb, index)
        self.shooter.projectile = None
        self.screen_shake = 0.1
        self._push_back_chain(index)
    
    def _push_back_chain(self, start_index):
        """Push back chain after insertion to maintain spacing"""
        for i in range(start_index, len(self.chain.orbs)):
            if i > 0:
                prev_orb = self.chain.orbs[i - 1]
                required_distance = prev_orb.path_distance + self.chain.distance_between_orbs
                if self.chain.orbs[i].path_distance > required_distance:
                    self.chain.orbs[i].path_distance = required_distance
                pos = self.chain.path.get_position_at_distance(self.chain.orbs[i].path_distance)
                if pos:
                    self.chain.orbs[i].pos = pos

    def _show_level_complete_message(self):
        """Show level complete message"""
        self.show_level_complete = True
        QTimer.singleShot(3000, lambda: setattr(self, 'show_level_complete', False))
    
    def _restart_level(self):
        """Restart current level after losing a life"""
        self.show_retry_message = False
        self.start_new_game(self.level)
        
    def game_over(self):
        """Handle game over - FIXED: Properly clear flags on restart"""
        self.running = False
        game_over = self.parent_window.game_manager.level_failed()
        
        if game_over:
            self._play_audio('play_game_over')
            self.show_game_over_message = True
            QTimer.singleShot(3000, lambda: self.parent_window.state_manager.change_state(GameState.GAME_OVER))
        else:
            self.show_retry_message = True
            QTimer.singleShot(2000, lambda: self._restart_level())
            
    def paintEvent(self, event):
        """Render game scene with Scaling"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Scaling logic
        scale_x = self.width() / self.logical_width
        scale_y = self.height() / self.logical_height
        scale = min(scale_x, scale_y)
        
        offset_x = (self.width() - (self.logical_width * scale)) / 2
        offset_y = (self.height() - (self.logical_height * scale)) / 2
        
        painter.translate(offset_x, offset_y)
        painter.scale(scale, scale)
        
        # Screen shake
        if self.screen_shake > 0:
            shake_x = (math.sin(self.animation_time * 50) * self.screen_shake * 20)
            shake_y = (math.cos(self.animation_time * 50) * self.screen_shake * 20)
            painter.translate(shake_x, shake_y)
        
        # Draw Objects
        logical_rect = QRectF(0, 0, self.logical_width, self.logical_height)
        
        self._draw_background_scaled(painter, logical_rect)
        self._draw_path(painter)
        self._draw_portal(painter)
        
        if self.slow_motion_active:
            self._draw_danger_indicator_scaled(painter, logical_rect)
        
        if self.chain:
            self.chain.draw(painter)
            
        if self.shooter:
            self.shooter.draw(painter)
            
        self.hud.draw(painter)
        
        # Draw Overlays
        if hasattr(self, 'show_level_complete') and self.show_level_complete:
            self._draw_level_complete(painter, logical_rect)
        
        if hasattr(self, 'show_retry_message') and self.show_retry_message:
            self._draw_retry_message(painter, logical_rect)
        
        if hasattr(self, 'show_game_over_message') and self.show_game_over_message:
            self._draw_game_over_message(painter, logical_rect)
        
        if hasattr(self, 'level_transition') and self.level_transition:
            progress = self.level_transition_progress
            opacity = int(progress * 2 * 255) if progress < 0.5 else int((1 - progress) * 2 * 255)
            painter.fillRect(logical_rect, QColor(0, 0, 0, opacity))

        # Powerup Status Text
        if hasattr(self, 'powerup_manager'):
            y_pos = 180
            font = QFont("Arial", 16, QFont.Bold)
            painter.setFont(font)
            if self.powerup_manager.slow_active:
                painter.setPen(QColor(100, 255, 255))
                painter.drawText(20, y_pos, f"❄️ FROZEN: {int(self.powerup_manager.slow_timer)}s")
                y_pos += 30
            if self.powerup_manager.reverse_active:
                painter.setPen(QColor(255, 100, 255))
                painter.drawText(20, y_pos, f"⏪ REVERSE: {int(self.powerup_manager.reverse_timer)}s")

    def _draw_level_complete(self, painter, rect):
        """Draw level complete message"""
        painter.fillRect(rect, QColor(0, 0, 0, 180))
        
        level_themes = [220, 270, 350, 160, 40, 180, 310, 190]
        theme_hue = level_themes[(self.level - 1) % len(level_themes)]
        theme_color = QColor.fromHsv(theme_hue, 200, 255)
        
        painter.setPen(theme_color)
        font = QFont("Arial", 48, QFont.Bold)
        painter.setFont(font)
        
        text = f"LEVEL {self.level} COMPLETE!"
        text_rect = painter.boundingRect(rect, Qt.AlignCenter, text)
        painter.drawText(text_rect, Qt.AlignCenter, text)
        
        # Score
        painter.setPen(QColor(255, 215, 0))
        font = QFont("Arial", 24)
        painter.setFont(font)
        score_text = f"Score: {self.score}"
        score_rect = QRectF(rect)
        score_rect.setTop(text_rect.bottom() + 20)
        painter.drawText(score_rect, Qt.AlignHCenter | Qt.AlignTop, score_text)
    
    def _draw_retry_message(self, painter, rect):
        """Draw retry message"""
        painter.fillRect(rect, QColor(0, 0, 0, 150))
        
        lives = self.parent_window.game_manager.lives
        painter.setPen(QColor(255, 165, 0))
        font = QFont("Arial", 36, QFont.Bold)
        painter.setFont(font)
        
        text = f"Lives Remaining: {lives}"
        text_rect = painter.boundingRect(rect, Qt.AlignCenter, text)
        painter.drawText(text_rect, Qt.AlignCenter, text)
        
        painter.setPen(QColor(255, 215, 0))
        font = QFont("Arial", 20)
        painter.setFont(font)
        retry_text = "Retrying level..."
        retry_rect = QRectF(rect)
        retry_rect.setTop(text_rect.bottom() + 20)
        painter.drawText(retry_rect, Qt.AlignHCenter | Qt.AlignTop, retry_text)
    
    def _draw_game_over_message(self, painter, rect):
        """Draw game over message"""
        painter.fillRect(rect, QColor(0, 0, 0, 200))
        
        painter.setPen(QColor(255, 50, 50))
        font = QFont("Arial", 48, QFont.Bold)
        painter.setFont(font)
        text = "GAME OVER"
        text_rect = painter.boundingRect(rect, Qt.AlignCenter, text)
        painter.drawText(text_rect, Qt.AlignCenter, text)
        
        painter.setPen(QColor(255, 165, 0))
        font = QFont("Arial", 24)
        painter.setFont(font)
        score_text = f"Final Score: {self.parent_window.game_manager.total_score}"
        score_rect = QRectF(rect)
        score_rect.setTop(text_rect.bottom() + 20)
        painter.drawText(score_rect, Qt.AlignHCenter | Qt.AlignTop, score_text)
        
    def _draw_background_scaled(self, painter, rect):
        """Draw background on logical rect"""
        gradient = QLinearGradient(0, 0, 0, self.logical_height)
        
        level_themes = [
            {'base_hue': 220, 'accent_hue': 200, 'sat1': 60, 'sat2': 80, 'val1': 25, 'val2': 15},
            {'base_hue': 270, 'accent_hue': 290, 'sat1': 70, 'sat2': 85, 'val1': 30, 'val2': 18},
            {'base_hue': 350, 'accent_hue': 10, 'sat1': 75, 'sat2': 90, 'val1': 35, 'val2': 20},
            {'base_hue': 160, 'accent_hue': 140, 'sat1': 65, 'sat2': 80, 'val1': 28, 'val2': 16},
            {'base_hue': 40, 'accent_hue': 30, 'sat1': 70, 'sat2': 85, 'val1': 38, 'val2': 22},
            {'base_hue': 180, 'accent_hue': 200, 'sat1': 80, 'sat2': 90, 'val1': 32, 'val2': 19},
            {'base_hue': 310, 'accent_hue': 330, 'sat1': 85, 'sat2': 95, 'val1': 36, 'val2': 21},
            {'base_hue': 190, 'accent_hue': 170, 'sat1': 75, 'sat2': 88, 'val1': 30, 'val2': 17},
        ]
        
        theme_index = (self.level - 1) % len(level_themes)
        theme = level_themes[theme_index]
        anim_offset = math.sin(self.animation_time * 0.5) * 10
        
        color1 = QColor.fromHsv(int(theme['base_hue'] + anim_offset) % 360, theme['sat1'], theme['val1'])
        color2 = QColor.fromHsv(int(theme['accent_hue'] - anim_offset) % 360, theme['sat2'], theme['val2'])
        
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)
        painter.fillRect(rect, gradient)
        
        # Particles
        particle_base = QColor.fromHsv(int(theme['base_hue'] + 30) % 360, 40, 60)
        for i in range(20):
            x = (math.sin(self.animation_time * 0.5 + i) * 0.4 + 0.5) * self.logical_width
            y = (math.cos(self.animation_time * 0.3 + i * 0.7) * 0.4 + 0.5) * self.logical_height
            size = 5 + math.sin(self.animation_time + i) * 3
            
            radial = QRadialGradient(x, y, size)
            p_color = QColor(particle_base)
            p_color.setAlpha(30)
            radial.setColorAt(0, p_color)
            p_color.setAlpha(0)
            radial.setColorAt(1, p_color)
            
            painter.setBrush(radial)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QRectF(x - size, y - size, size * 2, size * 2))
            
    def _draw_path(self, painter):
        """Draw path guide"""
        if not self.path:
            return
        painter.setPen(Qt.NoPen)
        for i in range(len(self.path.points) - 1):
            p1 = self.path.points[i]
            p2 = self.path.points[i + 1]
            gradient = QLinearGradient(p1, p2)
            gradient.setColorAt(0, QColor(139, 69, 19, 100))
            gradient.setColorAt(1, QColor(160, 82, 45, 100))
            painter.setBrush(gradient)
            width = 25
            painter.drawEllipse(p1, width/2, width/2)
            
    def _draw_portal(self, painter):
        """Draw end portal"""
        if not self.portal_pos:
            return
        for i in range(3):
            radius = self.portal_radius * (1 + i * 0.3)
            pulse = math.sin(self.animation_time * 3 + i) * 5
            gradient = QRadialGradient(self.portal_pos, radius + pulse)
            gradient.setColorAt(0, QColor(100, 0, 150, 200))
            gradient.setColorAt(0.5, QColor(150, 0, 255, 150))
            gradient.setColorAt(1, QColor(255, 0, 255, 0))
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self.portal_pos, radius + pulse, radius + pulse)
    
    def _draw_danger_indicator_scaled(self, painter, rect):
        """Draw danger indicator with scaling support"""
        opacity = int((1.0 - self.slow_motion_factor) * 255)
        
        cx, cy = self.logical_width / 2, self.logical_height / 2
        gradient = QRadialGradient(cx, cy, self.logical_width / 2)
        gradient.setColorAt(0, QColor(255, 0, 0, 0))
        gradient.setColorAt(0.7, QColor(255, 0, 0, 0))
        gradient.setColorAt(1, QColor(255, 0, 0, opacity))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(rect)
        
        if opacity > 100:
            painter.setPen(QColor(255, 50, 50))
            font = QFont("Arial", 24, QFont.Bold)
            painter.setFont(font)
            warning = "⚠ DANGER! ⚠"
            text_rect = QRectF(rect)
            text_rect.setTop(self.logical_height - 100)
            painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, warning)

    def mouseMoveEvent(self, event):
        """Handle mouse movement with logical mapping"""
        if self.shooter and self.running and not self.paused:
            logical_pos = self._map_to_logical(event.position())
            self.shooter.aim_at(logical_pos)
            
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if not self.running or self.paused:
            return
            
        if event.button() == Qt.LeftButton and self.shooter:
            projectile = self.shooter.fire()
            if projectile:
                self._play_audio('play_shoot')
                    
        elif event.button() == Qt.RightButton and self.shooter:
            self.shooter.swap_orbs()
            self._play_audio('play_power')
