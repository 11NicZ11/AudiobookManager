"""Test für den Database Service"""
import sys
import os
from pathlib import Path

# Füge das Projekt-Root zum Python-Pfad hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print(f"Projekt Root: {project_root}")
print(f"Python Pfad: {sys.path[:3]}...")

try:
    from service.database.database_manager import DatabaseManager
    from service.database.models.audiobook import Audiobook
    
    print("✅ Import erfolgreich!")
    
    def run_test():
        """Einfacher Datenbank-Test"""
        print("\n=== Datenbank Test ===")
        
        # Temporäre Test-Datenbank
        test_db = "test_audiobooks.db"
        
        # Manager erstellen
        db = DatabaseManager(test_db)
        print("Datenbank initialisiert")
        
        # Test-Hörbuch
        audiobook = Audiobook(
            title="Der kleine Prinz",
            author="Antoine de Saint-Exupéry",
            narrators=["August Zirner"],
            genre="Literatur",
            subgenre="Philosophisches Märchen",
            year=1943,
            universe="Der kleine Prinz",
            description="Ein zeitloses Meisterwerk"
        )
        
        # Speichern
        audiobook_id = db.add_audiobook(audiobook)
        print(f"Hörbuch gespeichert mit ID: {audiobook_id}")
        
        # Wieder laden
        loaded = db.get_audiobook(audiobook_id)
        print(f"Wieder geladen: {loaded.title}")
        
        # Alle anzeigen
        all_books = db.get_all_audiobooks()
        print(f"\nAlle Hörbücher ({len(all_books)}):")
        for book in all_books:
            print(f"  - {book.display_id}: {book.title}")
        
        # Aufräumen
        if os.path.exists(test_db):
            os.remove(test_db)
            print(f"\nTest-DB '{test_db}' gelöscht")
        
        print("✅ Test erfolgreich abgeschlossen!")
    
    run_test()
    
except ImportError as e:
    print(f"❌ Import fehlgeschlagen: {e}")
    print("\nÜberprüfe die Ordnerstruktur:")
    
    # Aktuelle Struktur anzeigen
    current_dir = Path(__file__).parent.parent
    print(f"\nAktuelle Struktur in {current_dir}:")
    for root, dirs, files in os.walk(current_dir):
        level = root.replace(str(current_dir), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith('.py'):
                print(f"{subindent}{file}")