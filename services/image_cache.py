"""
Image cache manager for QPixmap optimization
Stores scaled wallpapers in Local AppData to avoid re-rendering
"""

import json
import os
import sys
from pathlib import Path
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QSize, Qt
import hashlib

class ImageCache:
    """Manages cached QPixmap images for optimal performance"""
    
    def __init__(self):
        self.cache_dir = self._get_cache_directory()
        self.cache_index_file = self.cache_dir / "cache_index.json"
        self.memory_cache = {}  # In-memory cache for session
        
        # Ensure cache directory exists
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            print(f"ImageCache: Cache directory is {self.cache_dir}")
        except Exception as e:
            print(f"ImageCache: Error creating cache directory {e}")
        
        # Load cache index
        self.cache_index = self._load_cache_index()
        
    def _get_cache_directory(self):
        """Get platform-specific cache directory"""
        app_name = "MacanAncient"
        
        if os.name == 'nt':  # Windows
            local_app_data = os.getenv('LOCALAPPDATA')
            if local_app_data:
                return Path(local_app_data) / app_name / "cache"
            app_data = os.getenv('APPDATA')
            if app_data:
                return Path(app_data) / app_name / "cache"
        
        home = Path.home()
        xdg_cache = os.getenv('XDG_CACHE_HOME')
        
        if xdg_cache:
            return Path(xdg_cache) / app_name
            
        if sys.platform == 'darwin':  # MacOS
            return home / "Library" / "Caches" / app_name
            
        return home / ".cache" / app_name
    
    def _load_cache_index(self):
        """Load cache index from JSON"""
        try:
            if self.cache_index_file.exists():
                with open(self.cache_index_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"ImageCache: Error loading cache index: {e}")
        return {}
    
    def _save_cache_index(self):
        """Save cache index to JSON"""
        try:
            with open(self.cache_index_file, 'w') as f:
                json.dump(self.cache_index, f, indent=4)
        except Exception as e:
            print(f"ImageCache: Error saving cache index: {e}")
    
    def _get_file_hash(self, file_path):
        """Get MD5 hash of file for change detection"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            print(f"ImageCache: Error hashing file: {e}")
            return None
    
    def _generate_cache_key(self, image_path, size):
        """Generate cache key for image + size combination"""
        path_str = str(image_path)
        size_str = f"{size.width()}x{size.height()}"
        cache_key = hashlib.md5(f"{path_str}_{size_str}".encode()).hexdigest()
        return cache_key
    
    def get_scaled_pixmap(self, image_path, target_size, keep_aspect_ratio=True):
        """
        Get scaled pixmap from cache or create new one
        
        Args:
            image_path: Path to source image
            target_size: QSize target size
            keep_aspect_ratio: Whether to keep aspect ratio
            
        Returns:
            QPixmap or None
        """
        image_path = Path(image_path)
        
        # Check if source file exists
        if not image_path.exists():
            print(f"ImageCache: Source image not found: {image_path}")
            return None
        
        # Generate cache key
        cache_key = self._generate_cache_key(image_path, target_size)
        
        # Check memory cache first (fastest)
        if cache_key in self.memory_cache:
            print(f"ImageCache: Hit (memory) for {image_path.name}")
            return self.memory_cache[cache_key]
        
        # Check disk cache
        cached_file = self.cache_dir / f"{cache_key}.webp"
        file_hash = self._get_file_hash(image_path)
        
        # Validate cache entry
        if cache_key in self.cache_index:
            cache_entry = self.cache_index[cache_key]
            
            # Check if source file hasn't changed and cached file exists
            if (cache_entry.get('source_hash') == file_hash and 
                cached_file.exists()):
                
                # Load from disk cache
                pixmap = QPixmap(str(cached_file))
                if not pixmap.isNull():
                    print(f"ImageCache: Hit (disk) for {image_path.name}")
                    self.memory_cache[cache_key] = pixmap
                    return pixmap
        
        # Cache miss - create new scaled pixmap
        print(f"ImageCache: Miss for {image_path.name}, creating scaled version...")
        
        original_pixmap = QPixmap(str(image_path))
        if original_pixmap.isNull():
            print(f"ImageCache: Failed to load image: {image_path}")
            return None
        
        # Scale pixmap
        aspect_mode = Qt.KeepAspectRatioByExpanding if keep_aspect_ratio else Qt.IgnoreAspectRatio
        scaled_pixmap = original_pixmap.scaled(
            target_size,
            aspect_mode,
            Qt.SmoothTransformation
        )
        
        # Save to disk cache
        try:
            scaled_pixmap.save(str(cached_file), "webp")
            
            # Update cache index
            self.cache_index[cache_key] = {
                'source_path': str(image_path),
                'source_hash': file_hash,
                'size': f"{target_size.width()}x{target_size.height()}",
                'cached_file': str(cached_file)
            }
            self._save_cache_index()
            
            print(f"ImageCache: Cached {image_path.name} as {cache_key}.webp")
            
        except Exception as e:
            print(f"ImageCache: Error saving cache: {e}")
        
        # Store in memory cache
        self.memory_cache[cache_key] = scaled_pixmap
        
        return scaled_pixmap
    
    def clear_memory_cache(self):
        """Clear in-memory cache"""
        self.memory_cache.clear()
        print("ImageCache: Memory cache cleared")
    
    def clear_disk_cache(self):
        """Clear disk cache"""
        try:
            # Remove all cached files
            for cache_file in self.cache_dir.glob("*.webp"):
                cache_file.unlink()
            
            # Clear cache index
            self.cache_index = {}
            self._save_cache_index()
            
            print("ImageCache: Disk cache cleared")
            return True
            
        except Exception as e:
            print(f"ImageCache: Error clearing disk cache: {e}")
            return False
    
    def get_cache_size(self):
        """Get total size of disk cache in bytes"""
        total_size = 0
        try:
            for cache_file in self.cache_dir.glob("*.webp"):
                total_size += cache_file.stat().st_size
        except Exception as e:
            print(f"ImageCache: Error calculating cache size: {e}")
        return total_size
    
    def get_cache_size_mb(self):
        """Get cache size in MB"""
        return self.get_cache_size() / (1024 * 1024)


# Global cache instance
_global_cache = None

def get_image_cache():
    """Get global image cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = ImageCache()
    return _global_cache