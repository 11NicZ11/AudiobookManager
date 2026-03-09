from pathlib import Path
from typing import Tuple, Optional, Dict, List
import shutil
import tempfile

from .storage.local_storage import LocalStorage
from .validators.image_validator import ImageValidator
from .validators.audio_validator import AudioValidator

class FileManager:
    """Hauptklasse für Dateiverwaltung"""
    
    def __init__(self, storage_path: str = "data"):
        """
        Args:
            storage_path: Pfad für Dateispeicherung
        """
        self.storage = LocalStorage(storage_path)
        self.temp_dir = Path(tempfile.gettempdir()) / "audiobook_manager"
        self.temp_dir.mkdir(exist_ok=True)
    
    # --- Bild-Verwaltung ---
    
    def upload_image(self, source_path: str, audiobook_id: int) -> Tuple[bool, str, str]:
        """
        Lädt ein Bild hoch und verknüpft es mit einem Hörbuch
        
        Args:
            source_path: Pfad zur Quelldatei
            audiobook_id: ID des Hörbuchs
            
        Returns:
            (success, message, saved_path)
        """
        source = Path(source_path)
        
        # Validierung
        is_valid, error_message = ImageValidator.validate(source)
        if not is_valid:
            return False, error_message, ""
        
        # Speichern
        return self.storage.save_image(source, audiobook_id)
    
    def upload_multiple_images(self, image_paths: List[str], audiobook_id: int) -> Dict:
        """
        Lädt mehrere Bilder hoch
        
        Returns:
            {
                'success': bool,
                'uploaded': list of saved_paths,
                'errors': list of error_messages
            }
        """
        paths = [Path(p) for p in image_paths]
        valid_files, errors = ImageValidator.validate_multiple(paths)
        
        uploaded_paths = []
        
        for file_path in valid_files:
            success, message, saved_path = self.storage.save_image(file_path, audiobook_id)
            if success:
                uploaded_paths.append(saved_path)
            else:
                errors.append(f"{file_path.name}: {message}")
        
        return {
            'success': len(errors) == 0,
            'uploaded': uploaded_paths,
            'errors': errors,
            'total_files': len(image_paths),
            'successful_uploads': len(uploaded_paths)
        }
    
    # --- Audio-Verwaltung ---
    
    def upload_audio(self, source_path: str, audiobook_id: int) -> Tuple[bool, str, str]:
        """
        Lädt eine Audio-Datei hoch
        
        Returns:
            (success, message, saved_path)
        """
        source = Path(source_path)
        
        # Validierung
        is_valid, error_message = AudioValidator.validate(source)
        if not is_valid:
            return False, error_message, ""
        
        # Speichern
        return self.storage.save_audio(source, audiobook_id)
    
    def get_audio_info(self, audio_path: str) -> Optional[dict]:
        """Gibt Informationen über eine Audio-Datei zurück"""
        path = Path(audio_path)
        return AudioValidator.get_audio_info(path)
    
    # --- Allgemeine Dateioperationen ---
    
    def delete_file(self, file_path: str) -> Tuple[bool, str]:
        """Löscht eine Datei"""
        success = self.storage.delete_file(file_path)
        if success:
            return True, "Datei erfolgreich gelöscht"
        return False, "Datei konnte nicht gelöscht werden"
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """Gibt Dateiinformationen zurück"""
        return self.storage.get_file_info(file_path)
    
    def copy_to_temp(self, source_path: str) -> Tuple[bool, str, str]:
        """
        Kopiert eine Datei ins temporäre Verzeichnis
        
        Returns:
            (success, message, temp_path)
        """
        try:
            source = Path(source_path)
            if not source.exists():
                return False, "Quelldatei existiert nicht", ""
            
            # Temporären Dateinamen generieren
            temp_filename = self.storage.generate_unique_filename(source.name)
            temp_path = self.temp_dir / temp_filename
            
            # Kopieren
            shutil.copy2(source, temp_path)
            
            return True, "Datei temporär gespeichert", str(temp_path)
            
        except Exception as e:
            return False, f"Fehler: {str(e)}", ""
    
    def cleanup(self):
        """Räumt temporäre Dateien auf"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(exist_ok=True)
            
            self.storage.cleanup_temp_files()
            return True, "Aufräumen erfolgreich"
        except Exception as e:
            return False, f"Aufräumen fehlgeschlagen: {str(e)}"
    
    # --- Hilfsfunktionen ---
    
    def get_storage_stats(self) -> dict:
        """Gibt Statistiken über den Speicher zurück"""
        stats = {
            'images': 0,
            'audio': 0,
            'thumbnails': 0,
            'total_size': 0
        }
        
        # Zähle Dateien und Größe
        for folder_name in ['images', 'audio', 'thumbnails']:
            folder = self.storage.base_path / folder_name
            if folder.exists():
                for file in folder.iterdir():
                    if file.is_file():
                        stats[folder_name] += 1
                        stats['total_size'] += file.stat().st_size
        
        # In MB umrechnen
        stats['total_size_mb'] = stats['total_size'] / (1024 * 1024)
        
        return stats