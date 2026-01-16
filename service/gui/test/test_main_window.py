"""Test für das Hauptfenster der GUI"""
import sys
import os
from pathlib import Path
import time

# Projekt-Root zum Python-Pfad hinzufügen
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("🖥️  GUI TEST")
print("=" * 60)

def test_window_creation():
    """Testet ob das Fenster erstellt werden kann"""
    print("\n📋 Testbeschreibung:")
    print("-" * 40)
    print("1. Erstellt das Hauptfenster")
    print("2. Zeigt es kurz an (5 Sekunden)")
    print("3. Schließt automatisch")
    print("4. Test-Auswertung")
    print("-" * 40)
    
    try:
        import customtkinter as ctk
        from service.gui.main_window import MainWindow
        
        print("✅ Import erfolgreich")
        print(f"📦 CustomTkinter Version: {ctk.__version__}")
        
        # Fenster erstellen
        print("\n🔄 Erstelle MainWindow...")
        app = MainWindow()
        print("✅ MainWindow erstellt")
        
        # Fenster nach 5 Sekunden automatisch schließen
        print("\n⏳ GUI wird für 5 Sekunden angezeigt...")
        print("ℹ️  Das Fenster schließt automatisch")
        print("-" * 60)
        
        # Auto-Close nach 5 Sekunden
        app.root.after(5000, lambda: app.quit())
        
        # GUI starten
        app.run()
        
        print("\n✅ GUI wurde erfolgreich geschlossen")
        print("🎉 TEST BESTANDEN: GUI funktioniert korrekt!")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import fehlgeschlagen: {e}")
        print("\n🔧 Lösung:")
        print("1. Virtual Environment aktivieren:")
        print("   venv\\Scripts\\activate")
        print("2. CustomTkinter installieren:")
        print("   pip install customtkinter")
        print("3. Python Interpreter in VSCode:")
        print("   Ctrl+Shift+P → 'Python: Select Interpreter'")
        print("   → Wähle 'Python 3.x.x (venv)'")
        return False
        
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

def quick_import_test():
    """Schneller Import-Test ohne GUI"""
    print("\n🔧 Import-Test ohne GUI...")
    try:
        import customtkinter as ctk
        from service.gui.main_window import MainWindow
        from service.gui.pages.home_page import HomePage
        from service.gui.navigation import NavigationFrame
        
        print("✅ Alle Imports erfolgreich")
        print(f"✅ CustomTkinter {ctk.__version__}")
        print("✅ MainWindow Klasse verfügbar")
        print("✅ HomePage Klasse verfügbar")
        print("✅ NavigationFrame Klasse verfügbar")
        return True
    except ImportError as e:
        print(f"❌ Import fehlgeschlagen: {e}")
        return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    # Entscheidung: Vollständiger Test oder nur Import-Test
    print("\n🎯 Wähle Test-Modus:")
    print("1. Vollständiger GUI-Test (Fenster öffnet sich)")
    print("2. Schneller Import-Test (ohne GUI)")
    
    try:
        choice = input("\nDeine Wahl (1 oder 2): ").strip()
        
        if choice == "1":
            print("\n🧪 Starte vollständigen GUI-Test...")
            success = test_window_creation()
        elif choice == "2":
            print("\n🔍 Starte Import-Test...")
            success = quick_import_test()
        else:
            print("❌ Ungültige Auswahl, führe Import-Test aus")
            success = quick_import_test()
        
        # Zusammenfassung
        print("\n" + "=" * 60)
        if success:
            print("🎉 TEST BESTANDEN!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("❌ TEST FEHLGESCHLAGEN")
            print("=" * 60)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test durch Benutzer abgebrochen")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unerwarteter Fehler: {e}")
        sys.exit(1)