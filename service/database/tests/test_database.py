"""Test für den Database Service"""
import sys
import os
from pathlib import Path

# Gehe 3 Ebenen hoch zum Projekt-Root
project_root = Path(__file__).parent.parent.parent.parent  # Von tests/ hoch zum AudiobookManager/
sys.path.insert(0, str(project_root))

print(f"Projekt Root: {project_root}")
print(f"Python Pfad erstes Element: {sys.path[0]}")
print(f"Aktuelles Verzeichnis: {os.getcwd()}")

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
    
    # Debug: Zeige verfügbare Module
    print("\nVerfügbare Module in service/:")
    service_path = project_root / "service"
    if service_path.exists():
        for item in service_path.iterdir():
            if item.is_dir():
                print(f"  📁 {item.name}/")
            elif item.name.endswith('.py'):
                print(f"  📄 {item.name}")