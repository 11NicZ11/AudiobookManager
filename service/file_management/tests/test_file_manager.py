"""Test für den File Management Service"""
import sys
import os
from pathlib import Path

# Projekt-Root zum Python-Pfad hinzufügen
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from service.file_management.file_manager import FileManager
    
    print("✅ Import erfolgreich!")
    
    def test_file_manager():
        """Einfacher Test des File Managers"""
        print("\n=== File Manager Test ===")
        
        # File Manager erstellen
        fm = FileManager("test_data")
        print("File Manager initialisiert")
        
        # Test: Speicher-Statistiken
        stats = fm.get_storage_stats()
        print(f"Speicher-Statistiken: {stats}")
        
        # Test: Temporäre Datei kopieren
        # Erstelle eine Testdatei
        test_file = Path("test_temp.txt")
        test_file.write_text("Testinhalt")
        
        success, message, temp_path = fm.copy_to_temp(str(test_file))
        print(f"Temporär kopieren: {success} - {message}")
        
        if success:
            # Datei-Info abrufen
            file_info = fm.get_file_info(temp_path)
            print(f"Datei-Info: {file_info}")
            
            # Datei löschen
            success, message = fm.delete_file(temp_path)
            print(f"Löschen: {success} - {message}")
        
        # Aufräumen
        test_file.unlink()
        
        # Temp-Verzeichnis bereinigen
        success, message = fm.cleanup()
        print(f"Aufräumen: {success} - {message}")
        
        print("✅ Test erfolgreich abgeschlossen!")
    
    test_file_manager()
    
except ImportError as e:
    print(f"❌ Import fehlgeschlagen: {e}")
    print("\nInstalliere benötigte Abhängigkeiten:")
    print("pip install Pillow mutagen")