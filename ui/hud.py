"""
Heads-up display for game information
"""

from PySide6.QtGui import QPainter, QFont, QColor, QPen
from PySide6.QtCore import Qt, QRectF

class HUD:
    """Heads-up display overlay"""
    
    def __init__(self, scene):
        self.scene = scene
        self.score = 0
        self.high_score = 0  # Variabel baru
        self.combo = 0
        self.level = 1
        # --- TAMBAHKAN INI ---
        self.bonus_msg_timer = 0
        self.bonus_msg = ""

    def show_bonus_message(self, message):
        """Memicu pesan bonus untuk muncul di layar"""
        self.bonus_msg = message
        self.bonus_msg_timer = 3.0  # Tampilkan selama 3 detik
        
    def update_score(self, score):
        """Update score display"""
        self.score = score
        
    def update_high_score(self, high_score):
        """Update high score display"""
        self.high_score = high_score
        
    def update_combo(self, combo):
        """Update combo display"""
        self.combo = combo
        
    def update_level(self, level):
        """Update level display"""
        self.level = level
        
    def draw(self, painter):
        """Draw HUD elements"""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Level indicator
        level_themes = [220, 270, 350, 160, 40, 180, 310, 190]
        theme_hue = level_themes[(self.scene.level - 1) % len(level_themes)]
        level_color = QColor.fromHsv(theme_hue, 180, 255)
        
        self._draw_text(
            painter,
            f"LEVEL {self.scene.level}",
            20, 30,
            QFont("Arial", 24, QFont.Bold),
            level_color
        )
        
        # --- PERBAIKAN: Score & Best Score Display ---
        
        # Current Score
        self._draw_text(
            painter,
            f"SCORE: {self.score}",
            20, 65,
            QFont("Arial", 18, QFont.Bold),
            QColor(255, 215, 0) # Gold
        )
        
        # Best Score (Ditampilkan di tengah atas atau di bawah score)
        # Kita taruh di bawah score dengan warna ungu/spesial
        self._draw_text(
            painter,
            f"BEST: {self.high_score}",
            20, 90, 
            QFont("Arial", 14, QFont.Bold),
            QColor(200, 100, 255) # Light Purple
        )
        
        # Lives (Koordinat Y disesuaikan karena ada Best Score)
        lives = self.scene.parent_window.game_manager.lives
        life_color = QColor(255, 100, 100) if lives <= 2 else QColor(100, 255, 100)
        self._draw_text(
            painter,
            f"LIVES: {lives}",
            20, 120, # Turun sedikit
            QFont("Arial", 16, QFont.Bold),
            life_color
        )
        
        # Orbs remaining counter
        if self.scene.chain:
            try:
                orb_info = self.scene.chain.get_total_orbs_info()
                remaining = orb_info['remaining']
                current = orb_info['current']
                spawned = orb_info['spawned']
                max_orbs = orb_info['max']
                
                # Show progress
                progress_text = f"Progress: {spawned}/{max_orbs}"
                if remaining > 0:
                    progress_text += f" ({remaining} left)" # Shortened text
                else:
                    progress_text += f" (Clear all!)"
                
                progress_color = QColor(100, 200, 255) if remaining > 0 else QColor(255, 200, 100)
                
                self._draw_text(
                    painter,
                    progress_text,
                    20, 150, # Turun sedikit
                    QFont("Arial", 13, QFont.Bold),
                    progress_color
                )
            except AttributeError:
                pass
        
        # Slow motion indicator
        if hasattr(self.scene, 'slow_motion_active') and self.scene.slow_motion_active:
            slow_mo_percent = int(self.scene.slow_motion_factor * 100)
            self._draw_text(
                painter,
                f"⏱ SLOW-MO: {slow_mo_percent}%",
                self.scene.width() - 220, 30,
                QFont("Arial", 16, QFont.Bold),
                QColor(255, 255, 100)
            )
        
        # Combo (Sama seperti sebelumnya)
        if self.combo > 1:
            combo_text = f"COMBO x{self.combo}!"
            font = QFont("Arial", 24, QFont.Bold)
            
            import math
            pulse = math.sin(self.scene.animation_time * 5) * 0.1 + 1
            painter.save()
            
            text_width = painter.fontMetrics().horizontalAdvance(combo_text)
            x = self.scene.width() // 2 - text_width // 2
            y = 50
            
            painter.translate(x + text_width // 2, y)
            painter.scale(pulse, pulse)
            painter.translate(-(x + text_width // 2), -y)
            
            self._draw_text(
                painter,
                combo_text,
                x, y,
                font,
                QColor(255, 100, 100)
            )
            
            painter.restore()

        # Bonus
        if self.bonus_msg_timer > 0:
            # Hitung opacity berdasarkan sisa waktu (fade out)
            opacity = min(255, int(self.bonus_msg_timer * 255))
            
            painter.save()
            font = QFont("Arial", 28, QFont.Bold)
            painter.setFont(font)
            painter.setPen(QColor(255, 215, 0, opacity)) # Warna Emas
            
            # Gambar di tengah layar agak ke atas
            text_rect = painter.fontMetrics().boundingRect(self.bonus_msg)
            x = (self.scene.width() - text_rect.width()) // 2
            y = self.scene.height() // 3
            
            painter.drawText(x, y, self.bonus_msg)
            painter.restore()
            
            # Kurangi timer (dt biasanya 1/60 atau dari update scene)
            # Karena HUD tidak punya method update mandiri yang dipanggil dt, 
            # kita kurangi sedikit setiap frame draw
            self.bonus_msg_timer -= 0.016
            
    def _draw_text(self, painter, text, x, y, font, color):
        """Draw text with shadow"""
        painter.setFont(font)
        
        # Shadow
        painter.setPen(QPen(QColor(0, 0, 0, 150), 2))
        painter.drawText(x + 2, y + 2, text)
        
        # Main text
        painter.setPen(QPen(color, 1))
        painter.drawText(x, y, text)
