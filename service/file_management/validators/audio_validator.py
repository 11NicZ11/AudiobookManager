from pathlib import Path
from typing import Tuple, List
import wave
import mutagen

class AudioValidator:
    """Validiert Audio-Dateien"""
    
    # Unterstützte Audioformate
    SUPPORTED_FORMATS = {'.mp3', '.wav', '.flac', '.m4a', '.aac'}
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB (für Hörbücher)
    
    @classmethod
    def validate(cls, file_path: Path) -> Tuple[bool, str]:
        """
        Validiert eine Audio-Datei
        
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
            
            # Grundlegende Audio-Validierung basierend auf Format
            if extension == '.wav':
                try:
                    with wave.open(str(file_path), 'rb') as wav_file:
                        # Check if can be opened
                        channels = wav_file.getnchannels()
                        framerate = wav_file.getframerate()
                        if channels == 0 or framerate == 0:
                            return False, "Ungültige WAV-Datei"
                except Exception as e:
                    return False, f"Ungültige WAV-Datei: {str(e)}"
            
            elif extension in {'.mp3', '.flac', '.m4a', '.aac'}:
                try:
                    # Mutagen für MP3/FLAC/M4A/AAC Validierung
                    audio = mutagen.File(str(file_path))
                    if audio is None:
                        return False, "Ungültige Audio-Datei oder nicht unterstütztes Format"
                except ImportError:
                    # Mutagen nicht installiert, überspringen
                    pass
                except Exception as e:
                    return False, f"Audio-Datei ist beschädigt: {str(e)}"
            
            return True, "Audio-Datei ist valide"
            
        except Exception as e:
            return False, f"Validierungsfehler: {str(e)}"
    
    @classmethod
    def get_audio_info(cls, file_path: Path) -> dict:
        """Extrahiert Metadaten aus Audio-Datei"""
        try:
            info = {
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'extension': file_path.suffix.lower()
            }
            
            # Versuche, zusätzliche Metadaten zu extrahieren
            try:
                audio = mutagen.File(str(file_path))
                if audio:
                    info['duration'] = audio.info.length if hasattr(audio.info, 'length') else None
                    info['bitrate'] = audio.info.bitrate if hasattr(audio.info, 'bitrate') else None
                    
                    # Tags extrahieren
                    tags = {}
                    if hasattr(audio, 'tags'):
                        for key, value in audio.tags.items():
                            if isinstance(value, list):
                                tags[str(key)] = value[0]
                            else:
                                tags[str(key)] = str(value)
                    info['tags'] = tags
            except:
                pass  # Keine zusätzlichen Metadaten verfügbar
            
            return info
            
        except Exception:
            return {}