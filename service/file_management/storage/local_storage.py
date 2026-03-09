import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

class LocalStorage:
    """Verwaltet lokale Dateispeicherung für Bilder und Audio"""
    
    def __init__(self, base_path: str = "data"):
        """
        Args:
            base_path: Basis-Pfad für alle Dateien
        """
        self.base_path = Path(base_path)
        self.ensure_directories()
    
    def ensure_directories(self):
        """Erstellt notwendige Verzeichnisse"""
        directories = [
            self.base_path / "images",
            self.base_path / "audio",
            self.base_path / "thumbnails",
            self.base_path / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generiert einen eindeutigen Dateinamen"""
        extension = Path(original_filename).suffix.lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}{extension}"
    
    def save_image(self, source_path: Path, audiobook_id: int) -> Tuple[bool, str, str]:
        """
        Speichert ein Bild für ein Hörbuch
        
        Returns:
            (success, message, saved_path)
        """
        try:
            # Eindeutigen Dateinamen generieren
            filename = self.generate_unique_filename(source_path.name)
            
            # Zielpfad: data/images/{audiobook_id}_{filename}
            target_path = self.base_path / "images" / f"{audiobook_id}_{filename}"
            
            # Datei kopieren
            shutil.copy2(source_path, target_path)
            
            # Thumbnail erstellen (optional)
            thumbnail_path = self.create_thumbnail(target_path, audiobook_id)
            
            return True, "Bild erfolgreich gespeichert", str(target_path)
            
        except Exception as e:
            return False, f"Fehler beim Speichern: {str(e)}", ""
    
    def save_audio(self, source_path: Path, audiobook_id: int) -> Tuple[bool, str, str]:
        """
        Speichert eine Audio-Datei für ein Hörbuch
        
        Returns:
            (success, message, saved_path)
        """
        try:
            # Eindeutigen Dateinamen generieren
            filename = self.generate_unique_filename(source_path.name)
            
            # Zielpfad: data/audio/{audiobook_id}_{filename}
            target_path = self.base_path / "audio" / f"{audiobook_id}_{filename}"
            
            # Datei kopieren
            shutil.copy2(source_path, target_path)
            
            return True, "Audio-Datei erfolgreich gespeichert", str(target_path)
            
        except Exception as e:
            return False, f"Fehler beim Speichern: {str(e)}", ""
    
    def create_thumbnail(self, image_path: Path, audiobook_id: int) -> Optional[str]:
        """
        Erstellt ein Thumbnail für ein Bild
        """
        try:
            from PIL import Image
            
            # Nur wenn Pillow installiert ist
            with Image.open(image_path) as img:
                # Thumbnail erstellen (max 200x200)
                img.thumbnail((200, 200))
                
                thumbnail_filename = f"thumb_{audiobook_id}_{image_path.name}"
                thumbnail_path = self.base_path / "thumbnails" / thumbnail_filename
                
                img.save(thumbnail_path, format=img.format if img.format else 'JPEG')
                return str(thumbnail_path)
                
        except ImportError:
            # Pillow nicht installiert, kein Thumbnail
            return None
        except Exception:
            # Fehler beim Thumbnail erstellen
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """Löscht eine Datei"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Gibt Informationen über eine Datei zurück"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            return {
                'path': str(path),
                'size': path.stat().st_size,
                'created': datetime.fromtimestamp(path.stat().st_ctime),
                'modified': datetime.fromtimestamp(path.stat().st_mtime),
                'extension': path.suffix.lower()
            }
        except Exception:
            return None
    
    def cleanup_temp_files(self, older_than_hours: int = 24):
        """Löscht temporäre Dateien älter als X Stunden"""
        temp_dir = self.base_path / "temp"
        
        if not temp_dir.exists():
            return
        
        current_time = datetime.now()
        
        for file in temp_dir.iterdir():
            if file.is_file():
                file_age = current_time - datetime.fromtimestamp(file.stat().st_mtime)
                if file_age.total_seconds() > older_than_hours * 3600:
                    file.unlink()