"""
Main game scene - handles gameplay loop and rendering
UPDATED: Added Cheat Support for Visuals and Logic
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt, QRectF, QPointF, QSize
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QRadialGradient, QFont, QPen, QPixmap
from games.shooter import Shooter
from games.chain import OrbChain, Path
from games.collision import CollisionDetector
from games.orb import Orb
from ui.hud import HUD
from logic.combo_system import ComboSystem
from app.state_manager import GameState
from games.powerups import PowerUpManager
from services.image_cache import get_image_cache
import math
import random
import os
import sys

class GameScene(QWidget):
    """Main gameplay scene"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent_window = parent
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        
        self.logical_width = 1366
        self.logical_height = 768
        
        self.running = False
        self.paused = False
        self.level = 1
        self.score = 0
        self.show_level_complete = False
        self.show_game_over_message = False
        self.show_retry_message = False
        self.level_transition = False
        self.level_transition_progress = 0
        
        self.shooter = None
        self.chain = None
        self.path = None
        self.collision_detector = CollisionDetector()
        self.combo_system = ComboSystem()
        self.powerup_manager = PowerUpManager(self)
        self.hud = HUD(self)
        
        self.animation_time = 0
        self.screen_shake = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        
        self.portal_pos = None
        self.portal_radius = 50
        
        self.slow_motion_active = False
        self.slow_motion_factor = 1.0

        # Background Particles
        self.bg_particles = []
        self._init_background_particles()
        
        # Suction Particles for Black Hole Effect
        self.suction_particles = []
        
        # --- DYNAMIC WALLPAPER WITH CACHING (Level-based) ---
        self.image_cache = get_image_cache()
        self.current_wallpaper = None
        self.cached_wallpaper = None
        self.last_wallpaper_size = None
        self.current_wallpaper_path = None
        
        # Preload all available wallpapers
        self.available_wallpapers = self._detect_available_wallpapers()
        print(f"GameScene: Found {len(self.available_wallpapers)} wallpaper(s)")
        
    def _detect_available_wallpapers(self):
        """Detect which level wallpapers are available"""
        available = {}
        if os.path.exists("./ancient_gfx/scene.webp"):
            available['default'] = "./ancient_gfx/scene.webp"
        
        for level_num in range(1, 11):
            wallpaper_path = f"./ancient_gfx/scene{level_num}.webp"
            if hasattr(sys, "_MEIPASS"):
                frozen_path = os.path.join(sys._MEIPASS, wallpaper_path)
                if os.path.exists(frozen_path):
                    available[level_num] = frozen_path
                    continue
            
            if os.path.exists(wallpaper_path):
                available[level_num] = wallpaper_path
        return available
    
    def _get_wallpaper_for_level(self, level):
        if level in self.available_wallpapers:
            return self.available_wallpapers[level]
        if len(self.available_wallpapers) > 1:
            level_keys = [k for k in self.available_wallpapers.keys() if k != 'default']
            if level_keys:
                level_keys.sort()
                cycled_level = level_keys[(level - 1) % len(level_keys)]
                return self.available_wallpapers[cycled_level]
        return self.available_wallpapers.get('default')
    
    def _load_wallpaper_for_level(self, level):
        wallpaper_path = self._get_wallpaper_for_level(level)
        if wallpaper_path == self.current_wallpaper_path and self.current_wallpaper:
            return
        
        if wallpaper_path and os.path.exists(wallpaper_path):
            self.current_wallpaper = QPixmap(wallpaper_path)
            self.current_wallpaper_path = wallpaper_path
            self.cached_wallpaper = None
            self.last_wallpaper_size = None
        else:
            self.current_wallpaper = None
            self.current_wallpaper_path = None
            self.cached_wallpaper = None
        
    def _init_background_particles(self):
        self.bg_particles = []
        for _ in range(30):
            self.bg_particles.append({
                'x': random.uniform(0, self.logical_width),
                'y': random.uniform(0, self.logical_height),
                'speed_x': random.uniform(-20, 20),
                'speed_y': random.uniform(-20, 20),
                'size': random.uniform(5, 15)
            })
        
    def _has_audio(self):
        return (hasattr(self.parent_window, 'game_manager') and 
                hasattr(self.parent_window.game_manager, 'audio_manager') and
                self.parent_window.game_manager.audio_manager is not None)
    
    def _play_audio(self, method_name):
        if self._has_audio():
            try:
                method = getattr(self.parent_window.game_manager.audio_manager, method_name)
                method()
            except Exception:
                pass
        
    def start_new_game(self, level=1):
        self.show_level_complete = False
        self.show_game_over_message = False
        self.show_retry_message = False
        
        if hasattr(self, 'level') and self.level != level and level > 1:
            self.level_transition = True
            self.level_transition_progress = 0
        
        self.level = level
        self.score = self.parent_window.game_manager.total_score
        
        self.running = True
        self.paused = False
        
        self.shooter = Shooter(self.logical_width // 2, self.logical_height - 100)
        self.path = Path(self.logical_width, self.logical_height, self.level)
        self.chain = OrbChain(self.path, self.level)
        self.portal_pos = self.path.get_end_position()
        
        self.combo_system.reset()
        self.hud.update_level(self.level)
        self.hud.update_score(self.score)
        
        current_high = self.parent_window.game_manager.high_score
        self.hud.update_high_score(max(self.score, current_high))

        self.powerup_manager = PowerUpManager(self)
        self._init_background_particles()
        self.suction_particles = []
        
        self._load_wallpaper_for_level(self.level)
        
        self._play_audio('play_bgm')
        self.timer.start(16)

    def _map_to_logical(self, physical_pos):
        scale_x = self.width() / self.logical_width
        scale_y = self.height() / self.logical_height
        scale = min(scale_x, scale_y)
        offset_x = (self.width() - (self.logical_width * scale)) / 2
        offset_y = (self.height() - (self.logical_height * scale)) / 2
        logical_x = (physical_pos.x() - offset_x) / scale
        logical_y = (physical_pos.y() - offset_y) / scale
        return QPointF(logical_x, logical_y)

    def handle_matches(self, matches):
        if not matches: return
        powerup_orbs_to_trigger = []
        all_indices_to_remove = set()
        
        for match_indices in matches:
            all_indices_to_remove.update(match_indices)
        
        for idx in list(all_indices_to_remove):
            if idx < len(self.chain.orbs):
                orb = self.chain.orbs[idx]
                if orb.is_powerup() and not orb.exploding and not orb.marked_for_removal:
                    powerup_orbs_to_trigger.append({'orb': orb, 'type': orb.orb_type})
        
        checked_indices = set(all_indices_to_remove)
        neighbors_to_check = []
        for idx in all_indices_to_remove:
            neighbors_to_check.append(idx - 1)
            neighbors_to_check.append(idx + 1)
            
        for idx in neighbors_to_check:
            if 0 <= idx < len(self.chain.orbs) and idx not in checked_indices:
                orb = self.chain.orbs[idx]
                if orb.is_powerup() and not orb.exploding and not orb.marked_for_removal:
                    all_indices_to_remove.add(idx)
                    checked_indices.add(idx)
                    powerup_orbs_to_trigger.append({'orb': orb, 'type': orb.orb_type})
        
        self.chain.remove_orbs(list(all_indices_to_remove))
        total_removed = len(all_indices_to_remove)
        
        if total_removed == 0: return
        
        unique_powerups = []
        seen_orbs = set()
        for p in powerup_orbs_to_trigger:
            if p['orb'] not in seen_orbs:
                unique_powerups.append(p)
                seen_orbs.add(p['orb'])
                
        for powerup_data in unique_powerups:
            self.powerup_manager.activate_powerup(powerup_data['type'], powerup_data['orb'])
        
        self._play_audio('play_match')
        
        base_score = total_removed * 10
        combo_multiplier = self.combo_system.add_match(total_removed)

        old_score = self.score
        points_added = int(base_score * combo_multiplier)
        self.score += points_added        
        self.parent_window.game_manager.total_score = self.score
        self.parent_window.game_manager.check_high_score(self.score)

        if self.parent_window.game_manager.check_life_bonus(old_score, self.score):
            self._play_audio('play_power') 
            current_lives = self.parent_window.game_manager.lives
            self.hud.show_bonus_message(f"EXTRA LIFE! ❤️ {current_lives}")
       
        if combo_multiplier >= 3:
            self._play_audio('play_combo')
        
        self.hud.update_score(self.score)
        self.hud.update_combo(self.combo_system.current_combo)
        self.hud.update_high_score(self.parent_window.game_manager.high_score)
        self.screen_shake = 0.2

    def level_complete(self):
        if hasattr(self, 'show_level_complete') and self.show_level_complete: return

        self.running = False
        if self.chain and hasattr(self.parent_window.game_manager, 'achievement_tracker'):
            orbs_remaining = len(self.chain.orbs)
            self.parent_window.game_manager.achievement_tracker.on_level_complete_close_call(orbs_remaining)

        self.parent_window.game_manager.level_completed(self.score)
        self._show_level_complete_message()
        # --- LOGIKA BARU UNTUK LEVEL 50 ---
        if self.level == 50:
            print("GameScene: Level 50 Complete! Triggering Victory Sequence.")
            
            def show_victory_sequence():
                def return_to_menu():
                    # Kembali ke Main Menu setelah video selesai
                    self.parent_window.state_manager.change_state(GameState.MAIN_MENU)
                
                # Panggil fungsi video di AppWindow
                self.parent_window.show_victory_video(return_to_menu)
            
            # Beri jeda 2 detik agar tulisan "LEVEL COMPLETE" terbaca dulu
            QTimer.singleShot(2000, show_victory_sequence)
            return
        # ----------------------------------

        # Logika standar (Level < 50)
        next_level = self.parent_window.game_manager.current_level
        
        def show_transition_video():
            def start_next_level():
                self.start_new_game(next_level)
            self.parent_window.show_level_transition_video(start_next_level)
        
        QTimer.singleShot(2000, show_transition_video)
        
    def stop_game(self):
        self.running = False
        self.timer.stop()
        
    def pause_game(self):
        if not self.running: return
        self.paused = True
        self._play_audio('pause_bgm')
        
    def resume_game(self):
        if not self.running: return
        self.paused = False
        self._play_audio('resume_bgm')
        
    def game_loop(self):
        if not self.running or self.paused: return
        current_time = self.timer.interval()
        dt = current_time / 1000.0
        self.update_game(dt)
        self.update()
        
    def update_game(self, dt):
        self.animation_time += dt
        
        # --- CHEAT SYSTEM INTEGRATION ---
        cheat_sys = None
        if hasattr(self.parent_window, 'game_manager') and hasattr(self.parent_window.game_manager, 'cheat_system'):
            cheat_sys = self.parent_window.game_manager.cheat_system

        # CHEAT: Speed Multiplier
        speed_factor = 1.0
        if cheat_sys:
            speed_factor = cheat_sys.speed_multiplier
            
        final_dt_base = dt * speed_factor

        if self.level_transition:
            self.level_transition_progress += final_dt_base * 2
            if self.level_transition_progress >= 1.0:
                self.level_transition = False
                self.level_transition_progress = 0
            return

        # Update Particles
        for p in self.bg_particles:
            p['x'] += p['speed_x'] * final_dt_base
            p['y'] += p['speed_y'] * final_dt_base
            if p['x'] < -50: p['x'] = self.logical_width + 50
            if p['x'] > self.logical_width + 50: p['x'] = -50
            if p['y'] < -50: p['y'] = self.logical_height + 50
            if p['y'] > self.logical_height + 50: p['y'] = -50
            
        # CHEAT: Party Mode Logic
        if cheat_sys and cheat_sys.party_mode:
            if random.random() < 0.2:
                self.bg_particles.append({
                    'x': random.uniform(0, self.logical_width),
                    'y': random.uniform(0, self.logical_height),
                    'speed_x': random.uniform(-100, 100),
                    'speed_y': random.uniform(-100, 100),
                    'size': random.uniform(5, 25)
                })
                if len(self.bg_particles) > 200:
                    self.bg_particles.pop(0)

        # Update Suction Particles
        if self.portal_pos:
            if len(self.suction_particles) < 80:
                for _ in range(4):
                    angle = random.uniform(0, 6.28)
                    dist = random.uniform(80, 200)
                    self.suction_particles.append({
                        'x': self.portal_pos.x() + math.cos(angle) * dist,
                        'y': self.portal_pos.y() + math.sin(angle) * dist,
                        'speed': random.uniform(150, 300),
                        'size': random.uniform(2, 4),
                        'angle_offset': angle,
                        'color': random.choice([QColor(200, 100, 255), QColor(100, 200, 255), QColor(255, 255, 255)])
                    })
            
            active_suction = []
            for p in self.suction_particles:
                dx = self.portal_pos.x() - p['x']
                dy = self.portal_pos.y() - p['y']
                dist_sq = dx*dx + dy*dy
                dist = math.sqrt(dist_sq)
                
                if dist > 5:
                    nx, ny = dx/dist, dy/dist
                    tx, ty = -ny, nx
                    accel = 1.0 + (200.0 / (dist + 1.0))
                    speed = p['speed'] * accel * final_dt_base
                    p['x'] += nx * speed * 0.8 + tx * speed * 0.4
                    p['y'] += ny * speed * 0.8 + ty * speed * 0.4
                    p['size'] = max(0.5, p['size'] * 0.98)
                    active_suction.append(p)
            self.suction_particles = active_suction
        
        self.powerup_manager.update(final_dt_base)
        powerup_speed_mult = self.powerup_manager.get_speed_multiplier()

        if self.chain:
            head_distance = self.chain.get_head_distance()
            total_len = self.path.total_length
            
            # CHEAT: No Clip
            no_clip = False
            if cheat_sys and cheat_sys.no_clip:
                no_clip = True
                
            danger_threshold = total_len * 0.85
            if head_distance >= danger_threshold and not no_clip:
                self.slow_motion_active = True
                danger_level = (head_distance - danger_threshold) / (total_len - danger_threshold)
                self.slow_motion_factor = 1.0 - (danger_level * 0.4)
            else:
                self.slow_motion_active = False
                self.slow_motion_factor = 1.0
            
            chain_dt = final_dt_base * self.slow_motion_factor * powerup_speed_mult
            
            if cheat_sys and cheat_sys.no_spawn:
                 self.chain.spawn_timer = 0
            
            self.chain.update(chain_dt)
            self.chain.orbs = [orb for orb in self.chain.orbs if not orb.marked_for_removal]
            
            # CHEAT: Size Multiplier
            if cheat_sys:
                size_mult = cheat_sys.orb_size_multiplier
                if size_mult != 1.0:
                    for orb in self.chain.orbs:
                        orb.visible_scale *= size_mult

            # Logic: Update visible segments
            if self.chain.orbs and self.path:
                orb_distances = [orb.path_distance for orb in self.chain.orbs]
                self.path.update_visible_segments(orb_distances)
            
            suck_zone_start = self.path.total_length - 40 
            for orb in self.chain.orbs:
                if orb.path_distance > suck_zone_start:
                    depth = (orb.path_distance - suck_zone_start) / 60.0
                    orb.visible_scale = max(0.0, 1.0 - depth)
                else:
                    orb.visible_scale = 1.0

            game_over_threshold = self.path.total_length + 20
            if self.chain.get_head_distance() >= game_over_threshold:
                if not no_clip:
                    self.game_over()
                    return
                else:
                     for orb in self.chain.orbs:
                         orb.path_distance -= 500
            
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - final_dt_base * 5)
        
        if self.shooter:
            self.shooter.update(final_dt_base)
            
        if self.shooter and self.shooter.projectile and self.chain:
            collision = self.collision_detector.check_collision(
                self.shooter.projectile, self.chain
            )
            if collision:
                self.handle_collision(collision)
                
        if self.chain:
            matches = self.chain.check_matches()
            if matches:
                self.handle_matches(matches)
        
        if self.chain and self.running and not self.show_level_complete:
            remaining_to_spawn = self.chain.max_total_orbs - self.chain.orbs_spawned
            if len(self.chain.orbs) == 0 and remaining_to_spawn <= 0:
                self.level_complete()
        
        self.combo_system.update(final_dt_base)
        
    def handle_collision(self, collision):
        projectile = collision['projectile']
        index = collision['index']
        new_orb = Orb(projectile.orb.pos.x(), projectile.orb.pos.y(), projectile.orb.orb_type)
        
        if index < len(self.chain.orbs):
            collision_orb = self.chain.orbs[index]
            new_orb.path_distance = collision_orb.path_distance - self.chain.distance_between_orbs / 2
        else:
            if self.chain.orbs:
                new_orb.path_distance = self.chain.orbs[-1].path_distance + self.chain.distance_between_orbs
            else:
                new_orb.path_distance = 0
        
        self.chain.insert_orb(new_orb, index)
        self.shooter.projectile = None
        self.screen_shake = 0.1
        self._push_back_chain(index)
    
    def _push_back_chain(self, start_index):
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
        self.show_level_complete = True
        QTimer.singleShot(3000, lambda: setattr(self, 'show_level_complete', False))
    
    def _restart_level(self):
        self.show_retry_message = False
        self.start_new_game(self.level)
        
    def game_over(self):
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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        scale_x = self.width() / self.logical_width
        scale_y = self.height() / self.logical_height
        scale = min(scale_x, scale_y)
        offset_x = (self.width() - (self.logical_width * scale)) / 2
        offset_y = (self.height() - (self.logical_height * scale)) / 2
        
        painter.translate(offset_x, offset_y)
        painter.scale(scale, scale)
        
        if self.screen_shake > 0:
            shake_x = (math.sin(self.animation_time * 50) * self.screen_shake * 20)
            shake_y = (math.cos(self.animation_time * 50) * self.screen_shake * 20)
            painter.translate(shake_x, shake_y)
        
        logical_rect = QRectF(0, 0, self.logical_width, self.logical_height)
        
        # CHEAT: Party Mode Background
        cheat_sys = None
        if hasattr(self.parent_window, 'game_manager'):
             cheat_sys = self.parent_window.game_manager.cheat_system

        if cheat_sys and cheat_sys.party_mode:
             hue = (self.animation_time * 100) % 360
             painter.fillRect(logical_rect, QColor.fromHsv(int(hue), 150, 50))
        else:
            self._draw_background_scaled(painter, logical_rect)
        
        self._draw_path_optimized(painter)
        
        # CHEAT: Show Full Path
        if cheat_sys and cheat_sys.show_full_path and self.path:
            painter.save()
            pen = QPen(QColor(0, 255, 0, 100), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            points = self.path.points
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i+1])
            painter.restore()

        self._draw_portal(painter)
        
        if self.slow_motion_active:
            self._draw_danger_indicator_scaled(painter, logical_rect)
        
        if self.chain:
            self.chain.draw(painter)
        if self.shooter:
            self.shooter.draw(painter)
        self.hud.draw(painter)
        
        # CHEAT: Show FPS
        if cheat_sys and cheat_sys.show_fps:
             painter.save()
             painter.setPen(QColor(0, 255, 0))
             painter.setFont(QFont("Consolas", 16, QFont.Bold))
             fps = 60 
             if self.timer.interval() > 0:
                 fps = int(1000 / self.timer.interval())
             painter.drawText(self.logical_width - 120, 40, f"FPS: {fps}")
             painter.restore()
        
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

    def _draw_level_complete(self, painter, rect):
        painter.fillRect(rect, QColor(0, 0, 0, 180))
        painter.setPen(QColor(255, 215, 0))
        painter.setFont(QFont("Arial", 48, QFont.Bold))
        text = f"LEVEL {self.level} COMPLETE!"
        text_rect = painter.boundingRect(rect, Qt.AlignCenter, text)
        painter.drawText(text_rect, Qt.AlignCenter, text)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 24))
        painter.drawText(QRectF(rect).translated(0, 50), Qt.AlignCenter, f"Score: {self.score}")
    
    def _draw_retry_message(self, painter, rect):
        painter.fillRect(rect, QColor(0, 0, 0, 150))
        painter.setPen(QColor(255, 165, 0))
        painter.setFont(QFont("Arial", 36, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, f"Lives Remaining: {self.parent_window.game_manager.lives}")
    
    def _draw_game_over_message(self, painter, rect):
        painter.fillRect(rect, QColor(0, 0, 0, 200))
        painter.setPen(QColor(255, 50, 50))
        painter.setFont(QFont("Arial", 48, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, "GAME OVER")
        
    def _draw_background_scaled(self, painter, rect):
        if self.current_wallpaper and not self.current_wallpaper.isNull():
            current_size = QSize(int(rect.width()), int(rect.height()))
            if self.last_wallpaper_size != current_size or not self.cached_wallpaper:
                self.cached_wallpaper = self.image_cache.get_scaled_pixmap(
                    self.current_wallpaper_path, current_size, keep_aspect_ratio=True
                )
                self.last_wallpaper_size = current_size
            
            if self.cached_wallpaper and not self.cached_wallpaper.isNull():
                x = (rect.width() - self.cached_wallpaper.width()) / 2
                y = (rect.height() - self.cached_wallpaper.height()) / 2
                painter.drawPixmap(int(x), int(y), self.cached_wallpaper)
                painter.fillRect(rect, QColor(0, 0, 0, 60))
                painter.setBrush(QColor(255, 255, 255, 35))
                painter.setPen(Qt.NoPen)
                for p in self.bg_particles:
                    painter.drawEllipse(QPointF(p['x'], p['y']), p['size'], p['size'])
                return
        
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
        theme = level_themes[(self.level - 1) % len(level_themes)]
        anim_offset = math.sin(self.animation_time * 0.5) * 10
        color1 = QColor.fromHsv(int(theme['base_hue'] + anim_offset) % 360, theme['sat1'], theme['val1'])
        color2 = QColor.fromHsv(int(theme['accent_hue'] - anim_offset) % 360, theme['sat2'], theme['val2'])
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)
        painter.fillRect(rect, gradient)
        
        painter.setBrush(QColor(255, 255, 255, 35))
        painter.setPen(Qt.NoPen)
        for p in self.bg_particles:
            painter.drawEllipse(QPointF(p['x'], p['y']), p['size'], p['size'])
            
    def _draw_path_optimized(self, painter):
        if not self.path: return
        painter.setPen(Qt.NoPen)
        if not self.path.visible_segments:
            if len(self.path.points) >= 2:
                p1 = self.path.points[0]
                p2 = self.path.points[-1]
                gradient = QLinearGradient(p1, p2)
                gradient.setColorAt(0, QColor(139, 69, 19, 80))
                gradient.setColorAt(1, QColor(160, 82, 45, 80))
                painter.setBrush(gradient)
                painter.drawEllipse(p1, 10, 10)
                painter.drawEllipse(p2, 10, 10)
            return
        
        for i in self.path.visible_segments:
            if i < len(self.path.points) - 1:
                p1 = self.path.points[i]
                p2 = self.path.points[i + 1]
                gradient = QLinearGradient(p1, p2)
                gradient.setColorAt(0, QColor(139, 69, 19, 100))
                gradient.setColorAt(1, QColor(160, 82, 45, 100))
                painter.setBrush(gradient)
                painter.drawEllipse(p1, 12.5, 12.5)
            
    def _draw_portal(self, painter):
        if not self.portal_pos: return
        painter.save()
        painter.setPen(Qt.NoPen)
        for p in self.suction_particles:
            color = QColor(p['color'])
            alpha = int(150 * (p['size'] / 4.0)) 
            color.setAlpha(min(255, max(0, alpha)))
            painter.setBrush(color)
            painter.drawEllipse(QPointF(p['x'], p['y']), p['size'], p['size'])
        painter.translate(self.portal_pos)
        for i in range(3):
            angle = (self.animation_time * (50 + i * 20)) % 360
            painter.rotate(angle)
            radius = self.portal_radius * (1.2 + math.sin(self.animation_time * 2 + i) * 0.1)
            gradient = QRadialGradient(0, 0, radius)
            gradient.setColorAt(0, QColor(0, 0, 0, 255))
            gradient.setColorAt(0.4, QColor(50, 0, 100, 200)) 
            gradient.setColorAt(0.8, QColor(150, 0, 255, 100))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(0, 0), radius, radius)
            painter.rotate(-angle)
        core_radius = self.portal_radius * 0.6
        core_gradient = QRadialGradient(0, 0, core_radius)
        core_gradient.setColorAt(0, QColor(0, 0, 0)) 
        core_gradient.setColorAt(0.8, QColor(20, 0, 40)) 
        core_gradient.setColorAt(1, QColor(100, 0, 200))
        painter.setBrush(core_gradient)
        painter.setPen(QPen(QColor(200, 100, 255), 2)) 
        painter.drawEllipse(QPointF(0, 0), core_radius, core_radius)
        painter.restore()
    
    def _draw_danger_indicator_scaled(self, painter, rect):
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
            painter.setFont(QFont("Arial", 24, QFont.Bold))
            painter.drawText(QRectF(rect).translated(0, self.logical_height - 100), Qt.AlignHCenter | Qt.AlignTop, "⚠ DANGER! ⚠")

    def mouseMoveEvent(self, event):
        if self.shooter and self.running and not self.paused:
            logical_pos = self._map_to_logical(event.position())
            self.shooter.aim_at(logical_pos)
            
    def mousePressEvent(self, event):
        if not self.running or self.paused:
            return
        if event.button() == Qt.LeftButton and self.shooter:
            projectile = self.shooter.fire()
            if projectile:
                self._play_audio('play_shoot')
        elif event.button() == Qt.RightButton and self.shooter:
            self.shooter.swap_orbs()
            self._play_audio('play_power')