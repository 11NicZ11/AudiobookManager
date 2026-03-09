"""Debug-Script für die Hörbuch-Liste"""
import sys
import os

# Projekt-Pfad setzen
sys.path.insert(0, os.getcwd())

print("=" * 60)
print("🔧 DEBUG: Hörbuch-Liste")
print("=" * 60)

# 1. Prüfe Database Service
print("\n1. 📊 Database Service Check:")
try:
    from service.database.database_manager import DatabaseManager
    print("✅ DatabaseManager importiert")
    
    try:
        db = DatabaseManager()
        print("✅ DatabaseManager instanziiert")
        
        # Teste ob Datenbank existiert
        if os.path.exists("data/audiobooks.db"):
            print("✅ Datenbank-Datei existiert: data/audiobooks.db")
        else:
            print("⚠️  Datenbank-Datei existiert NICHT: data/audiobooks.db")
            print("   Erstelle Test-Daten...")
            
            # Erstelle Test-Daten
            from service.database.models.audiobook import Audiobook
            test_books = [
                Audiobook(title="Harry Potter 1", author="J.K. Rowling", genre="Fantasy", year=1998),
                Audiobook(title="Der Herr der Ringe", author="J.R.R. Tolkien", genre="Fantasy", year=1954),
                Audiobook(title="Der alte Mann und das Meer", author="Ernest Hemingway", genre="Literatur", year=1952),
            ]
            
            for book in test_books:
                db.add_audiobook(book)
            
            print("✅ Test-Daten erstellt")
            
    except Exception as e:
        print(f"❌ DatabaseManager Fehler: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"❌ DatabaseManager Import Fehler: {e}")

# 2. Prüfe GUI Imports
print("\n2. 🖥️  GUI Imports Check:")
try:
    from service.gui.pages.audiobook_list import AudiobookListPage
    print("✅ AudiobookListPage importiert")
except ImportError as e:
    print(f"❌ AudiobookListPage Import Fehler: {e}")
    import traceback
    traceback.print_exc()

# 3. Direkter Test ohne GUI
print("\n3. 🧪 Direkter Test (ohne GUI):")
try:
    from service.database.database_manager import DatabaseManager
    from service.database.models.audiobook import Audiobook
    
    db = DatabaseManager()
    
    # Teste get_all_audiobooks()
    print("Teste get_all_audiobooks()...")
    audiobooks = db.get_all_audiobooks()
    print(f"✅ {len(audiobooks)} Hörbücher gefunden")
    
    for i, book in enumerate(audiobooks[:3]):  # Zeige erste 3
        print(f"  {i+1}. {book.title} - {book.author}")
    
    if len(audiobooks) == 0:
        print("⚠️  Keine Hörbücher in Datenbank, füge Test-Daten hinzu...")
        
        test_data = [
            ("Harry Potter und der Stein der Weisen", "J.K. Rowling", "Fantasy", 1998),
            ("Die Stadt der träumenden Bücher", "Walter Moers", "Fantasy", 2004),
            ("Der Schwarm", "Frank Schätzing", "Science-Fiction", 2004),
        ]
        
        for title, author, genre, year in test_data:
            audiobook = Audiobook(title=title, author=author, genre=genre, year=year)
            db.add_audiobook(audiobook)
        
        print("✅ Test-Daten hinzugefügt")
        
except Exception as e:
    print(f"❌ Direkter Test Fehler: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🔧 Lösungsvorschläge:")
print("1. Prüfe ob Database Service korrekt importiert wird")
print("2. Prüfe ob Datenbank-Datei existiert (data/audiobooks.db)")
print("3. Prüfe ob AudiobookListPage korrekt importiert wird")
print("4. Starte GUI mit debug info: python start_app.py")
print("=" * 60)

input("\nDrücke Enter zum Beenden...")