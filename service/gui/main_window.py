import sys
import os
import customtkinter as ctk

# Füge das service Verzeichnis zum Python-Pfad hinzu
current_dir = os.path.dirname(os.path.abspath(__file__))
service_dir = os.path.join(current_dir, "..")
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

# Jetzt absolute Imports verwenden
try:
    from gui.navigation import NavigationFrame
    from gui.pages.home_page import HomePage
    from gui.pages.base_page import BasePage
    print("✅ Alle Imports erfolgreich")
except ImportError as e:
    print(f"❌ Import Fehler: {e}")
    print(f"📁 Current dir: {current_dir}")
    print(f"📁 Service dir: {service_dir}")
    print(f"📁 Sys path: {sys.path[:3]}")
    raise

class MainWindow:
    """Hauptfenster der Anwendung mit BasePage-Integration"""
    
    def __init__(self):
        # ZUERST current_page initialisieren!
        self.current_page = None
        
        self.setup_appearance()
        self.root = ctk.CTk()
        self.setup_window()
        self.setup_frames()
        
    def setup_appearance(self):
        """Setzt das Erscheinungsbild der App"""
        ctk.set_appearance_mode("dark")  # dark, light, system
        ctk.set_default_color_theme("blue")  # blue, green, dark-blue
    
    def setup_window(self):
        """Konfiguriert das Hauptfenster"""
        self.root.title("Audiobook Manager")
        self.root.geometry("1200x800")
        
        # Minimalgröße setzen
        self.root.minsize(800, 600)
        
        # Grid-Konfiguration
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Fenster-Icon (optional)
        try:
            self.root.iconbitmap("icon.ico")  # Falls du eins hast
        except:
            pass
    
    def setup_frames(self):
        """Erstellt alle Frames (Navigation + Hauptbereich)"""
        
        # Navigation/Sidebar links
        self.navigation = NavigationFrame(
            self.root,
            command=self.navigate_to_page
        )
        self.navigation.grid(row=0, column=0, sticky="nsew")
        
        # Hauptbereich rechts (für Pages)
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Startseite laden
        self.show_home_page()
    
    def show_home_page(self):
        """Zeigt die Startseite an"""
        self.clear_main_frame()
        self.current_page = HomePage(self.main_frame)
        self.current_page.pack(fill="both", expand=True)
        self.navigation.set_active_button("home")
        self.update_window_title("Startseite")
    
    def navigate_to_page(self, page_name: str):
        """Navigiert zu einer Seite basierend auf dem Button"""
        print(f"Navigiere zu: {page_name}")
        
        if page_name == "home":
            self.show_home_page()
        elif page_name == "audiobooks":
            self.show_placeholder_page(
                "📚 Hörbuch-Liste", 
                "Hier werden alle Hörbücher angezeigt. Du kannst sortieren, filtern und nach spezifischen Hörbüchern suchen."
            )
            self.navigation.set_active_button("audiobooks")
            self.update_window_title("Hörbuch-Liste")
        elif page_name == "add":
            self.show_placeholder_page(
                "➕ Hörbuch hinzufügen", 
                "Hier kannst du neue Hörbücher erfassen. Füge Titel, Autor, Genre, Universum und alle anderen Informationen hinzu."
            )
            self.navigation.set_active_button("add")
            self.update_window_title("Hörbuch hinzufügen")
        elif page_name == "search":
            self.show_placeholder_page(
                "🔍 Suche", 
                "Erweiterte Suche nach Hörbüchern. Suche nach Titel, Autor, Genre, Universum oder kombiniere mehrere Kriterien."
            )
            self.navigation.set_active_button("search")
            self.update_window_title("Suche")
        elif page_name == "universes":
            self.show_placeholder_page(
                "🌌 Universen", 
                "Verwaltung der Hörbuch-Universen. Erstelle neue Universen, verknüpfe Hörbücher und organisiere Zeitlinien."
            )
            self.navigation.set_active_button("universes")
            self.update_window_title("Universen")
        elif page_name == "settings":
            self.show_placeholder_page(
                "⚙️ Einstellungen", 
                "Anwendungseinstellungen. Passe das Aussehen, Speicherorte und andere Optionen an."
            )
            self.navigation.set_active_button("settings")
            self.update_window_title("Einstellungen")
        elif page_name == "help":
            self.show_placeholder_page(
                "❓ Hilfe", 
                "Hilfe und Dokumentation. Lerne wie du den Audiobook Manager optimal nutzt."
            )
            self.update_window_title("Hilfe")
        elif page_name == "quit":
            self.quit()
    
    def show_placeholder_page(self, title: str, description: str):
        """Zeigt eine Platzhalter-Seite (erbt von BasePage)"""
        self.clear_main_frame()
        
        # Dynamische Platzhalter-Page-Klasse erstellen
        class PlaceholderPage(BasePage):
            def __init__(self, master, title, description):
                super().__init__(master)
                self.setup_widgets(title, description)
            
            def setup_widgets(self, title, description):
                content = self.get_content_area()
                
                # Titel
                title_label = ctk.CTkLabel(
                    content,
                    text=title,
                    font=ctk.CTkFont(size=32, weight="bold")
                )
                title_label.pack(pady=(40, 20))
                
                # Beschreibung
                desc_label = ctk.CTkLabel(
                    content,
                    text=description,
                    font=ctk.CTkFont(size=16),
                    wraplength=600
                )
                desc_label.pack(pady=(0, 30))
                
                # Demo-Inhalt für Scrollbar
                demo_frame = ctk.CTkFrame(content)
                demo_frame.pack(fill="x", pady=(30, 0))
                
                demo_label = ctk.CTkLabel(
                    demo_frame,
                    text="📋 Demo-Inhalt für Scrollbar-Test",
                    font=ctk.CTkFont(size=18, weight="bold")
                )
                demo_label.pack(pady=(20, 10))
                
                # Viele Demo-Einträge
                for i in range(1, 16):
                    item_frame = ctk.CTkFrame(demo_frame, fg_color="transparent")
                    item_frame.pack(fill="x", pady=2)
                    
                    ctk.CTkLabel(
                        item_frame,
                        text=f"• Demo-Eintrag {i}:",
                        font=ctk.CTkFont(size=12, weight="bold")
                    ).pack(side="left", padx=(10, 5))
                    
                    ctk.CTkLabel(
                        item_frame,
                        text="Dies ist ein Platzhalter-Text um die Scrollbar zu testen.",
                        font=ctk.CTkFont(size=12),
                        text_color="gray"
                    ).pack(side="left")
                
                # Info-Box
                info_frame = ctk.CTkFrame(
                    content, 
                    fg_color=("gray85", "gray25"),
                    corner_radius=10
                )
                info_frame.pack(fill="x", pady=(30, 20))
                
                ctk.CTkLabel(
                    info_frame,
                    text="ℹ️  Information",
                    font=ctk.CTkFont(size=14, weight="bold")
                ).pack(pady=(10, 5))
                
                ctk.CTkLabel(
                    info_frame,
                    text="Diese Seite ist ein Platzhalter. Die eigentliche Funktion wird später implementiert.",
                    font=ctk.CTkFont(size=12),
                    wraplength=500
                ).pack(pady=(0, 10), padx=10)
                
                # Scroll-Hinweis
                scroll_hint = ctk.CTkLabel(
                    content,
                    text="↓ Diese Seite ist scrollbar ↓",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                )
                scroll_hint.pack(pady=(20, 10))
        
        # Platzhalter-Page erstellen und anzeigen
        self.current_page = PlaceholderPage(self.main_frame, title, description)
        self.current_page.pack(fill="both", expand=True)
    
    def clear_main_frame(self):
        """Löscht alle Widgets aus dem Hauptframe"""
        # Prüfe ob current_page existiert
        if hasattr(self, 'current_page') and self.current_page:
            # Zerstöre die aktuelle Page
            self.current_page.destroy()
            self.current_page = None
        
        # Sicherheitshalber alle Widgets löschen
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def update_window_title(self, page_name: str = ""):
        """Aktualisiert den Fenstertitel mit aktueller Seite"""
        base_title = "Audiobook Manager"
        if page_name:
            self.root.title(f"{base_title} - {page_name}")
        else:
            self.root.title(base_title)
    
    def show_loading_screen(self, message: str = "Lade..."):
        """Zeigt einen Ladebildschirm"""
        self.clear_main_frame()
        
        loading_frame = ctk.CTkFrame(self.main_frame)
        loading_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            loading_frame,
            text="⏳",
            font=ctk.CTkFont(size=72)
        ).pack(pady=(100, 30))
        
        ctk.CTkLabel(
            loading_frame,
            text=message,
            font=ctk.CTkFont(size=24)
        ).pack()
        
        self.current_page = loading_frame
    
    def run(self):
        """Startet die Hauptloop der Anwendung"""
        self.root.mainloop()
    
    def quit(self):
        """Beendet die Anwendung korrekt"""
        print("Beende Audiobook Manager...")
    
        # 1. Alle laufenden "after" Callbacks stornieren
        try:
            # Tkinter "after" Callbacks auflisten und canceln
            for after_id in self.root.tk.eval('after info').split():
                self.root.after_cancel(after_id)
        except:
            pass
    
        # 2. Alle Widgets zerstören
        try:
            for widget in self.root.winfo_children():
                widget.destroy()
        except:
            pass
    
        # 3. Tkinter mainloop stoppen
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
    
        # 4. Eventuell laufende Threads stoppen
        import threading
        for thread in threading.enumerate():
            if thread != threading.current_thread() and thread.is_alive():
                try:
                    # Nur unsere eigenen Threads stoppen
                    if hasattr(thread, '_stop'):
                        thread._stop()
                except:
                    pass

# Start-Code (nur wenn direkt ausgeführt)
if __name__ == "__main__":
    print("🚀 Starte Audiobook Manager...")
    app = MainWindow()
    app.run()