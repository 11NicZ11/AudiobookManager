import sys
import os
import traceback

# Zum Projektverzeichnis wechseln
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Aktuelles Verzeichnis zum Python-Pfad hinzufügen
sys.path.insert(0, script_dir)

print("=" * 50)
print("🎧 AUDIOBOOK MANAGER")
print("=" * 50)

print(f"📁 Arbeitsverzeichnis: {script_dir}")
print(f"🐍 Python: {sys.executable}")

try:
    # CustomTkinter prüfen
    import customtkinter as ctk
    print(f"✅ CustomTkinter {ctk.__version__} gefunden")
    
    # GUI importieren
    from service.gui.main_window import MainWindow
    
    print("\n🚀 Starte GUI...")
    print("ℹ️  Schließe das Fenster mit [X] oder über 'Beenden' in der Navigation")
    print("-" * 50)
    
    # GUI starten
    app = MainWindow()
    app.run()
    
    print("\n✅ GUI wurde beendet")
    
except ImportError as e:
    print(f"\n❌ Import Fehler: {e}")
    print("\n🔧 Lösung:")
    print("1. Virtual Environment aktivieren:")
    print("   venv\\Scripts\\activate")
    print("2. CustomTkinter installieren:")
    print("   pip install customtkinter")
    print("3. In VSCode: Python Interpreter auf 'venv' stellen")
    
except Exception as e:
    print(f"\n❌ Unerwarteter Fehler: {e}")
    traceback.print_exc()

print("\n👋 Programm beendet.")