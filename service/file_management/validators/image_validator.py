from pathlib import Path
from typing import Tuple, List

class ImageValidator:
    """Validiert Bild-Dateien"""
    
    # Unterstützte Bildformate
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    @classmethod
    def validate(cls, file_path: Path) -> Tuple[bool, str]:
        """
        Validiert eine Bild-Datei
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # Existiert die Datei?
            if not file_path.exists():
                return False, "Datei existiert nicht"
            
            # Dateiendung prüfen
            extension = file_path.suffix.lower()
            if extension not in cls.SUPPORTED_FORMATS:
                return False, f"Nicht unterstütztes Format. Erlaubt: {', '.join(cls.SUPPORTED_FORMATS)}"
            
            # Dateigröße prüfen
            file_size = file_path.stat().st_size
            if file_size > cls.MAX_FILE_SIZE:
                return False, f"Datei zu groß (max {cls.MAX_FILE_SIZE // (1024*1024)} MB)"
            
            # Einfache Integritätsprüfung (versuchen zu öffnen)
            if extension in {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}:
                # Pillow für detaillierte Validierung
                try:
                    from PIL import Image
                    with Image.open(file_path) as img:
                        img.verify()  # Überprüft Integrität
                except ImportError:
                    # Pillow nicht installiert, überspringen
                    pass
                except Exception as e:
                    return False, f"Bilddatei ist beschädigt: {str(e)}"
            
            return True, "Bild ist valide"
            
        except Exception as e:
            return False, f"Validierungsfehler: {str(e)}"
    
    @classmethod
    def validate_multiple(cls, file_paths: List[Path]) -> Tuple[List[Path], List[str]]:
        """
        Validiert mehrere Bild-Dateien
        
        Returns:
            (valid_files, error_messages)
        """
        valid_files = []
        errors = []
        
        for file_path in file_paths:
            is_valid, message = cls.validate(file_path)
            if is_valid:
                valid_files.append(file_path)
            else:
                errors.append(f"{file_path.name}: {message}")
        
        return valid_files, errors