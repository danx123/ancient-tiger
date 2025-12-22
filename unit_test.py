import unittest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from services.save_manager import SaveManager
from services.settings_manager import SettingsManager
from services.cheat_system import CheatSystem
from services.achievement_system import AchievementManager

# --- MOCK OBJECTS (Objek Palsu untuk Test) ---
class MockGameManager:
    """
    GameManager palsu. Kita butuh ini karena CheatSystem butuh 'parent'.
    Kita gak mau load GameManager asli karena dia bakal load Audio & UI berat.
    """
    def __init__(self):
        self.lives = 5
        self.total_score = 0
        self.current_level = 1
        self.high_score = 1000
        
        # Mocking achievement manager di dalam game manager
        self.achievement_system = MagicMock()
        
    def check_high_score(self, score):
        if score > self.high_score:
            self.high_score = score
            return True
        return False
        
    def level_completed(self, score):
        self.total_score = score
        self.current_level += 1

# --- TEST SUITE UTAMA ---
class TestAncientTiger(unittest.TestCase):

    def setUp(self):
        """
        Dijalankan SEBELUM setiap test.
        Kita buat folder sementara biar save file asli lo gak ketimpa/rusak.
        """
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """
        Dijalankan SETELAH setiap test.
        Hapus folder sementara biar bersih.
        """
        shutil.rmtree(self.test_dir)

    # ----------------------------------------------------------------
    # 1. TEST SAVE & LOAD SYSTEM
    # ----------------------------------------------------------------
    def test_save_manager_operations(self):
        print("\nTesting SaveManager...")
        
        # Kita 'paksa' SaveManager pake folder test kita, bukan AppData beneran
        with patch('services.save_manager.SaveManager._get_save_directory', return_value=self.test_path):
            manager = SaveManager()
            
            # Data game simulasi
            game_data = {
                'level': 5,
                'score': 12500,
                'lives': 3
            }
            
            # Act: Simpan
            save_success = manager.save_game(game_data)
            self.assertTrue(save_success, "Harusnya berhasil save game")
            
            # Assert: Pastikan file beneran ada
            self.assertTrue((self.test_path / "save.json").exists())
            
            # Act: Load kembali
            loaded_data = manager.load_game()
            
            # Assert: Cek isinya sama persis gak
            self.assertEqual(loaded_data['level'], 5)
            self.assertEqual(loaded_data['score'], 12500)
            self.assertEqual(loaded_data['lives'], 3)

    # ----------------------------------------------------------------
    # 2. TEST SETTINGS SYSTEM
    # ----------------------------------------------------------------
    def test_settings_persistence(self):
        print("Testing SettingsManager...")
        
        with patch('services.settings_manager.SettingsManager._get_settings_directory', return_value=self.test_path):
            settings = SettingsManager()
            
            # Default values check
            self.assertTrue(settings.get('music_enabled'))
            
            # Act: Ubah setting
            settings.set('music_enabled', False)
            settings.set('music_volume', 0.5)
            settings.save_settings()
            
            # Simulate restart (buat objek baru)
            new_settings_session = SettingsManager()
            
            # Assert: Setting harus tersimpan
            self.assertFalse(new_settings_session.get('music_enabled'))
            self.assertEqual(new_settings_session.get('music_volume'), 0.5)

    # ----------------------------------------------------------------
    # 3. TEST CHEAT SYSTEM (LOGIC)
    # ----------------------------------------------------------------
    def test_cheat_codes_logic(self):
        print("Testing CheatSystem...")
        
        # Setup lingkungan cheat dengan Mock GameManager
        mock_gm = MockGameManager()
        cheat_sys = CheatSystem(mock_gm)
        
        # Test 1: RICHMAN (Nambah Score)
        initial_score = mock_gm.total_score
        success, msg = cheat_sys.execute_cheat("RICHMAN")
        
        self.assertTrue(success)
        self.assertEqual(msg, "SCORE_UPDATE")
        # Ingat: CheatSystem di kodingan lo cuma return flag, 
        # dia mengubah nilai mock_gm.total_score di dalamnya
        self.assertEqual(mock_gm.total_score, initial_score + 10000)
        
        # Test 2: MORELIVES (Nambah Nyawa)
        initial_lives = mock_gm.lives
        success, msg = cheat_sys.execute_cheat("MORELIVES")
        
        self.assertTrue(success)
        self.assertEqual(mock_gm.lives, initial_lives + 5)
        
        # Test 3: GODMODE (Toggle)
        self.assertFalse(cheat_sys.god_mode)
        cheat_sys.execute_cheat("GODMODE")
        self.assertTrue(cheat_sys.god_mode)
        
        # Test 4: Cheat Ngawur (Harus gagal)
        success, msg = cheat_sys.execute_cheat("DUITBANYAK")
        self.assertFalse(success)

    # ----------------------------------------------------------------
    # 4. TEST ACHIEVEMENT SYSTEM
    # ----------------------------------------------------------------
    def test_achievement_unlocking(self):
        print("Testing AchievementManager...")
        
        with patch('services.achievement_system.AchievementManager._get_save_directory', return_value=self.test_path):
            ach_manager = AchievementManager()
            
            # Pastikan awalnya kosong
            self.assertFalse(ach_manager.is_unlocked("first_launch"))
            
            # Act: Unlock achievement
            unlocked = ach_manager.unlock("first_launch")
            
            # Assert
            self.assertTrue(unlocked, "Harusnya return True saat unlock baru")
            self.assertTrue(ach_manager.is_unlocked("first_launch"))
            
            # Cek apakah file json kebuat
            self.assertTrue((self.test_path / "achievements.json").exists())
            
            # Test unlock duplikat (harusnya return False)
            unlocked_again = ach_manager.unlock("first_launch")
            self.assertFalse(unlocked_again, "Harusnya return False kalau sudah pernah unlock")

    # ----------------------------------------------------------------
    # 5. TEST FILE UTILITIES (First Run)
    # ----------------------------------------------------------------
    def test_first_run_manager(self):
        print("Testing FirstRunManager...")
        from services.first_run_manager import FirstRunManager
        
        with patch('services.first_run_manager.FirstRunManager._get_first_run_directory', return_value=self.test_path):
            frm = FirstRunManager()
            
            # Awalnya harus True
            self.assertTrue(frm.is_first_run())
            
            # Tandai sudah run
            frm.mark_not_first_run()
            
            # Sekarang harus False
            self.assertFalse(frm.is_first_run())
            
            # File penanda harus ada
            self.assertTrue((self.test_path / ".firstrun").exists())

if __name__ == '__main__':
    unittest.main()