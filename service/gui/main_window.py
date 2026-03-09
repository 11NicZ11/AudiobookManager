import sys
import os
import customtkinter as ctk

# Füge das service Verzeichnis zum Python-Pfad hinzu
current_dir = os.path.dirname(os.path.abspath(__file__))
service_dir = os.path.join(current_dir, "..")
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

# Prüfe ob Database Service verfügbar ist
try:
    from database.database_manager import DatabaseManager
    from database.models.audiobook import Audiobook
    DATABASE_AVAILABLE = True
    print("✅ Database Service verfügbar")
except ImportError as e:
    DATABASE_AVAILABLE = False
    print(f"⚠️  Database Service nicht verfügbar: {e}")

# Prüfe ob File Management Service verfügbar ist
try:
    from file_management.file_manager import FileManager
    FILE_MANAGER_AVAILABLE = True
    print("✅ File Management Service verfügbar")
except ImportError as e:
    FILE_MANAGER_AVAILABLE = False
    print(f"⚠️  File Management Service nicht verfügbar: {e}")

# GUI Imports
try:
    from gui.navigation import NavigationFrame
    from gui.pages.home_page import HomePage
    from gui.pages.base_page import BasePage
    from gui.pages.audiobook_list import AudiobookListPage
    from gui.pages.add_audiobook import AddAudiobookPage
    from gui.pages.detail_audiobook import DetailAudiobookPage
    print("✅ Alle GUI Imports erfolgreich")
except ImportError as e:
    print(f"❌ Import Fehler: {e}")
    print(f"📁 Current dir: {current_dir}")
    print(f"📁 Service dir: {service_dir}")
    print(f"📁 Sys path: {sys.path[:3]}")
    raise


class ToolTip:
    """
    Ein einfaches Tooltip-Fenster das beim Hover über ein Widget erscheint
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0
        
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)
        widget.bind("<Motion>", self.motion)
    
    def enter(self, event=None):
        self.schedule()
    
    def leave(self, event=None):
        self.unschedule()
        self.hidetip()
    
    def motion(self, event):
        self.x = event.x_root + 20
        self.y = event.y_root + 10
    
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)
    
    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)
    
    def showtip(self):
        if self.tip_window or not self.text:
            return
        
        # Tooltip-Fenster erstellen
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{self.x}+{self.y}")
        
        # Rahmen und Hintergrund
        frame = tk.Frame(
            self.tip_window,
            background="#ffffe0",
            relief="solid",
            borderwidth=1
        )
        frame.pack()
        
        # Text
        label = tk.Label(
            frame,
            text=self.text,
            justify="left",
            background="#ffffe0",
            foreground="#000000",
            font=("Segoe UI", 10),
            padx=5,
            pady=2
        )
        label.pack()
    
    def hidetip(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class MainWindow:
    """Hauptfenster der Anwendung mit BasePage-Integration"""
    
    def __init__(self):
        # Attribute initialisieren
        self.current_page = None
        self.db_manager = None
        self.file_manager = None
        
        # Database Manager erstellen wenn verfügbar
        if DATABASE_AVAILABLE:
            try:
                self.db_manager = DatabaseManager()
                print("✅ Database Manager initialisiert")
            except Exception as e:
                print(f"⚠️  Database Manager Fehler: {e}")
                self.db_manager = None
        
        # File Manager erstellen wenn verfügbar
        if FILE_MANAGER_AVAILABLE:
            try:
                self.file_manager = FileManager()
                print("✅ File Manager initialisiert")
            except Exception as e:
                print(f"⚠️  File Manager Fehler: {e}")
                self.file_manager = None
        
        self.setup_appearance()
        self.root = ctk.CTk()
        self.setup_window()
        self.setup_frames()
        
        # Events binden
        self.bind_events()
    
    def setup_appearance(self):
        """Setzt das Erscheinungsbild der App"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
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
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Fenster-schließen Event
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
    
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
    
    def bind_events(self):
        """Bindet benutzerdefinierte Events"""
        # Navigation zurück zur Hörbuch-Liste
        self.root.bind("<<NavigateToAudiobookList>>", 
                      lambda e: self.show_audiobook_list())
        
        # Navigation zur Startseite
        self.root.bind("<<NavigateToHome>>", 
                      lambda e: self.show_home_page())
        
        # Navigation zum Bearbeiten eines Hörbuchs
        self.root.bind("<<EditAudiobook>>", 
                      self.on_edit_audiobook_event)
        
        # Navigation zum Hinzufügen eines Hörbuchs
        self.root.bind("<<AddAudiobook>>", 
                      lambda e: self.show_add_audiobook_page())
        
        # Daten neu laden
        self.root.bind("<<RefreshAudiobookList>>", 
                      lambda e: self.refresh_audiobook_list())
        
        # Detail-Ansicht anzeigen
        self.root.bind("<<ShowAudiobookDetail>>", 
                      self.on_show_detail_event)
    
    # ================ PAGE NAVIGATION ================
    
    def navigate_to_page(self, page_name: str):
        """Navigiert zu einer Seite basierend auf dem Button"""
        print(f"Navigiere zu: {page_name}")
        
        if page_name == "home":
            self.show_home_page()
        elif page_name == "audiobooks":
            self.show_audiobook_list()
        elif page_name == "add":
            self.show_add_audiobook_page()
        elif page_name == "search":
            self.show_search_page()
        elif page_name == "universes":
            self.show_universes_page()
        elif page_name == "settings":
            self.show_settings_page()
        elif page_name == "help":
            self.show_help_page()
        elif page_name == "quit":
            self.quit()
    
    # ================ PAGE IMPLEMENTIERUNGEN ================
    
    def show_home_page(self):
        """Zeigt die Startseite an"""
        self.clear_main_frame()
        # db_manager an HomePage übergeben
        self.current_page = HomePage(self.main_frame, db_manager=self.db_manager)
        self.current_page.pack(fill="both", expand=True)
        self.navigation.set_active_button("home")
        self.update_window_title("Startseite")
    
    def show_audiobook_list(self):
        """Zeigt die Hörbuch-Liste an"""
        self.clear_main_frame()
        
        # Prüfe ob Database Manager verfügbar ist
        if not self.db_manager:
            print("⚠️  Kein Database Manager verfügbar - zeige Fehlermeldung")
            self.show_error_page(
                "📚 Datenbank nicht verfügbar",
                "Der Database Service konnte nicht initialisiert werden.\n\n"
                "Bitte überprüfe:\n"
                "• Ob die Datenbankdatei existiert\n"
                "• Ob der Ordner 'data' Schreibrechte hat\n"
                "• Ob SQLite3 korrekt installiert ist"
            )
            return
        
        try:
            self.current_page = AudiobookListPage(
                self.main_frame, 
                db_manager=self.db_manager
            )
            self.current_page.pack(fill="both", expand=True)
            print("✅ Hörbuch-Liste mit Database Manager geladen")
        except Exception as e:
            print(f"❌ Fehler beim Laden der Hörbuch-Liste: {e}")
            self.show_error_page(
                "📚 Fehler beim Laden",
                f"Die Hörbuch-Liste konnte nicht geladen werden:\n\n{str(e)}"
            )
        
        self.navigation.set_active_button("audiobooks")
        self.update_window_title("Hörbuch-Liste")
    
    def show_add_audiobook_page(self, audiobook=None):
        """
        Zeigt die Seite zum Hinzufügen/Bearbeiten von Hörbüchern
        
        Args:
            audiobook: Optional - Zu bearbeitendes Hörbuch (None = neues Hörbuch)
        """
        self.clear_main_frame()
        
        # Prüfe ob Database Manager verfügbar ist
        if not self.db_manager:
            self.show_error_page(
                "➕ Datenbank nicht verfügbar",
                "Der Database Service konnte nicht initialisiert werden.\n\n"
                "Ohne Datenbank können keine Hörbücher gespeichert werden."
            )
            return
        
        try:
            self.current_page = AddAudiobookPage(
                self.main_frame,
                db_manager=self.db_manager,
                file_manager=self.file_manager,
                audiobook=audiobook
            )
            self.current_page.pack(fill="both", expand=True)
            
            page_title = "Hörbuch bearbeiten" if audiobook else "Hörbuch hinzufügen"
            self.update_window_title(page_title)
            
            # Aktiven Button in Navigation setzen
            if not audiobook:  # Nur bei neuem Hörbuch den Add-Button aktivieren
                self.navigation.set_active_button("add")
            
            print(f"✅ {page_title} geladen")
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Add-Page: {e}")
            self.show_error_page(
                "➕ Fehler beim Laden",
                f"Die Seite konnte nicht geladen werden:\n\n{str(e)}"
            )
    
    def show_detail_page(self, audiobook):
        """
        Zeigt die Detail-Ansicht für ein Hörbuch
        
        Args:
            audiobook: Das anzuzeigende Hörbuch
        """
        self.clear_main_frame()
        
        try:
            self.current_page = DetailAudiobookPage(
                self.main_frame,
                db_manager=self.db_manager,
                audiobook=audiobook,
                file_manager=self.file_manager
            )
            self.current_page.pack(fill="both", expand=True)
            
            # Titel kürzen für Fenstertitel
            short_title = audiobook.title[:30] + "..." if len(audiobook.title) > 30 else audiobook.title
            self.update_window_title(f"Details: {short_title}")
            
            print(f"✅ Detail-Ansicht für '{audiobook.title}' geladen")
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Detail-Ansicht: {e}")
            self.show_error_page(
                "❌ Fehler beim Laden",
                f"Die Detail-Ansicht konnte nicht geladen werden:\n\n{str(e)}"
            )
    
    def show_search_page(self):
        """Zeigt die Such-Seite an"""
        self.clear_main_frame()
        self.show_placeholder_page(
            "🔍 Suche",
            "Erweiterte Suche nach Hörbüchern.\n\n"
            "Suche nach Titel, Autor, Genre, Universum oder kombiniere mehrere Kriterien.\n\n"
            "Diese Funktion befindet sich noch in Entwicklung."
        )
        self.navigation.set_active_button("search")
        self.update_window_title("Suche")
    
    def show_universes_page(self):
        """Zeigt die Universen-Verwaltung an"""
        self.clear_main_frame()
        self.show_placeholder_page(
            "🌌 Universen",
            "Verwaltung der Hörbuch-Universen.\n\n"
            "Erstelle neue Universen, verknüpfe Hörbücher und organisiere Zeitlinien.\n\n"
            "Diese Funktion befindet sich noch in Entwicklung."
        )
        self.navigation.set_active_button("universes")
        self.update_window_title("Universen")
    
    def show_settings_page(self):
        """Zeigt die Einstellungen an"""
        self.clear_main_frame()
        self.show_placeholder_page(
            "⚙️ Einstellungen",
            "Anwendungseinstellungen.\n\n"
            "Passe das Aussehen, Speicherorte und andere Optionen an.\n\n"
            "Diese Funktion befindet sich noch in Entwicklung."
        )
        self.navigation.set_active_button("settings")
        self.update_window_title("Einstellungen")
    
    def show_help_page(self):
        """Zeigt die Hilfe-Seite an"""
        self.clear_main_frame()
        self.show_placeholder_page(
            "❓ Hilfe",
            "Hilfe und Dokumentation.\n\n"
            "Lerne wie du den Audiobook Manager optimal nutzt.\n\n"
            "Diese Funktion befindet sich noch in Entwicklung."
        )
        self.update_window_title("Hilfe")
    
    # ================ HILFSFUNKTIONEN ================
    
    def show_placeholder_page(self, title: str, description: str):
        """
        Zeigt eine Platzhalter-Seite für noch nicht implementierte Funktionen
        
        Args:
            title: Titel der Seite
            description: Beschreibungstext
        """
        self.clear_main_frame()
        
        # Dynamische Platzhalter-Page-Klasse erstellen
        class PlaceholderPage(BasePage):
            def __init__(self, master, title, description):
                super().__init__(master)
                self.setup_widgets(title, description)
            
            def setup_widgets(self, title, description):
                content = self.get_content_area()
                
                # Icon
                icon_label = ctk.CTkLabel(
                    content,
                    text="🚧",
                    font=ctk.CTkFont(size=72)
                )
                icon_label.pack(pady=(40, 20))
                
                # Titel
                title_label = ctk.CTkLabel(
                    content,
                    text=title,
                    font=ctk.CTkFont(size=32, weight="bold")
                )
                title_label.pack(pady=(0, 20))
                
                # Beschreibung als Label statt Textbox
                desc_label = ctk.CTkLabel(
                    content,
                    text=description,
                    font=ctk.CTkFont(size=16),
                    wraplength=600,
                    justify="left"
                )
                desc_label.pack(pady=(0, 30))
                
                # Zurück-Button
                back_btn = ctk.CTkButton(
                    content,
                    text="← Zurück zur Startseite",
                    font=ctk.CTkFont(size=14),
                    width=200,
                    height=40,
                    command=self.go_home
                )
                back_btn.pack(pady=20)
            
            def go_home(self):
                self.master.event_generate("<<NavigateToHome>>")
        
        self.current_page = PlaceholderPage(self.main_frame, title, description)
        self.current_page.pack(fill="both", expand=True)
    
    def show_error_page(self, title: str, message: str):
        """
        Zeigt eine Fehlerseite an
        
        Args:
            title: Fehlertitel
            message: Fehlermeldung
        """
        self.clear_main_frame()
        
        class ErrorPage(BasePage):
            def __init__(self, master, title, message):
                super().__init__(master)
                self.setup_widgets(title, message)
            
            def setup_widgets(self, title, message):
                content = self.get_content_area()
                
                # Icon
                icon_label = ctk.CTkLabel(
                    content,
                    text="❌",
                    font=ctk.CTkFont(size=72)
                )
                icon_label.pack(pady=(40, 20))
                
                # Titel
                title_label = ctk.CTkLabel(
                    content,
                    text=title,
                    font=ctk.CTkFont(size=32, weight="bold"),
                    text_color="red"
                )
                title_label.pack(pady=(0, 20))
                
                # Fehlermeldung
                msg_label = ctk.CTkLabel(
                    content,
                    text=message,
                    font=ctk.CTkFont(size=14),
                    wraplength=600,
                    justify="left"
                )
                msg_label.pack(pady=(0, 30))
                
                # Button-Frame
                button_frame = ctk.CTkFrame(content, fg_color="transparent")
                button_frame.pack(pady=20)
                
                # Zurück-Button
                back_btn = ctk.CTkButton(
                    button_frame,
                    text="← Zurück zur Startseite",
                    font=ctk.CTkFont(size=14),
                    width=200,
                    height=40,
                    command=self.go_home
                )
                back_btn.pack(side="left", padx=10)
                
                # Neu laden Button
                retry_btn = ctk.CTkButton(
                    button_frame,
                    text="🔄 Neu laden",
                    font=ctk.CTkFont(size=14),
                    width=150,
                    height=40,
                    fg_color="transparent",
                    border_width=2,
                    command=self.retry
                )
                retry_btn.pack(side="left", padx=10)
            
            def go_home(self):
                self.master.event_generate("<<NavigateToHome>>")
            
            def retry(self):
                self.master.event_generate("<<RefreshAudiobookList>>")
        
        self.current_page = ErrorPage(self.main_frame, title, message)
        self.current_page.pack(fill="both", expand=True)
    
    def clear_main_frame(self):
        """Löscht alle Widgets aus dem Hauptframe"""
        if hasattr(self, 'current_page') and self.current_page:
            try:
                self.current_page.destroy()
            except:
                pass
            self.current_page = None
        
        for widget in self.main_frame.winfo_children():
            try:
                widget.destroy()
            except:
                pass
    
    def update_window_title(self, page_name: str = ""):
        """Aktualisiert den Fenstertitel mit aktueller Seite"""
        base_title = "Audiobook Manager"
        self.root.title(f"{base_title} - {page_name}" if page_name else base_title)
    
    def refresh_audiobook_list(self):
        """Lädt die Hörbuch-Liste neu"""
        if self.current_page and isinstance(self.current_page, AudiobookListPage):
            self.current_page.load_audiobooks()
        else:
            self.show_audiobook_list()
    
    # ================ EVENT HANDLER ================
    
    def on_edit_audiobook_event(self, event):
        """
        Event-Handler für Hörbuch-Bearbeitung
        
        Erwartet: event.data = audiobook_id (als String)
        """
        print(f"🔧 Edit Event empfangen!")
        
        # Versuche die ID aus dem Event zu extrahieren
        audiobook_id = None
        
        # Methode 1: Über event.data
        if hasattr(event, 'data') and event.data:
            try:
                audiobook_id = int(event.data)
                print(f"📋 ID aus event.data: {audiobook_id}")
            except (ValueError, TypeError):
                print(f"⚠️ event.data ist keine gültige Zahl: {event.data}")
        
        # Methode 2: Über event.widget (falls das Widget die ID gespeichert hat)
        if audiobook_id is None and hasattr(event, 'widget') and event.widget:
            if hasattr(event.widget, 'audiobook_id'):
                audiobook_id = event.widget.audiobook_id
                print(f"📋 ID aus event.widget.audiobook_id: {audiobook_id}")
        
        # Methode 3: Direkt über die aktuelle Page (falls die Page die ID kennt)
        if audiobook_id is None and self.current_page and hasattr(self.current_page, 'get_selected_audiobook_id'):
            audiobook_id = self.current_page.get_selected_audiobook_id()
            print(f"📋 ID aus current_page: {audiobook_id}")
        
        if audiobook_id is None:
            print("❌ Keine gültige Hörbuch-ID gefunden")
            self.show_error_page(
                "Fehler beim Bearbeiten",
                "Keine Hörbuch-ID übergeben."
            )
            return
        
        # Hörbuch aus der Datenbank laden
        try:
            print(f"📋 Lade Hörbuch mit ID {audiobook_id}...")
            
            if not self.db_manager:
                print("❌ Kein Database Manager verfügbar")
                self.show_error_page(
                    "Fehler beim Bearbeiten",
                    "Keine Datenbankverbindung verfügbar."
                )
                return
            
            audiobook = self.db_manager.get_audiobook(audiobook_id)
            
            if audiobook:
                print(f"✅ Hörbuch gefunden: {audiobook.title} (ID: {audiobook.id})")
                self.show_add_audiobook_page(audiobook)
            else:
                print(f"⚠️ Hörbuch mit ID {audiobook_id} nicht gefunden")
                self.show_error_page(
                    "Fehler beim Bearbeiten",
                    f"Hörbuch mit ID {audiobook_id} wurde nicht gefunden."
                )
        except Exception as e:
            print(f"❌ Fehler beim Laden des Hörbuchs: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_page(
                "Fehler beim Bearbeiten",
                f"Ein Fehler ist aufgetreten: {str(e)}"
            )
    
    def on_show_detail_event(self, event):
        """
        Event-Handler für Detail-Ansicht
        
        Erwartet: event.data = audiobook_id (als String)
        """
        print(f"🔍 Detail Event empfangen!")
        
        # Versuche die ID aus dem Event zu extrahieren
        audiobook_id = None
        
        # Methode 1: Über event.data
        if hasattr(event, 'data') and event.data:
            try:
                audiobook_id = int(event.data)
                print(f"📋 ID aus event.data: {audiobook_id}")
            except (ValueError, TypeError):
                print(f"⚠️ event.data ist keine gültige Zahl: {event.data}")
        
        # Methode 2: Über event.widget (falls das Widget die ID gespeichert hat)
        if audiobook_id is None and hasattr(event, 'widget') and event.widget:
            if hasattr(event.widget, 'audiobook_id'):
                audiobook_id = event.widget.audiobook_id
                print(f"📋 ID aus event.widget.audiobook_id: {audiobook_id}")
        
        # Methode 3: Direkt über die aktuelle Page (falls die Page die ID kennt)
        if audiobook_id is None and self.current_page and hasattr(self.current_page, 'get_selected_audiobook_id'):
            audiobook_id = self.current_page.get_selected_audiobook_id()
            print(f"📋 ID aus current_page: {audiobook_id}")
        
        if audiobook_id is None:
            print("❌ Keine gültige Hörbuch-ID gefunden")
            return
        
        try:
            print(f"📋 Lade Hörbuch mit ID {audiobook_id} für Detail-Ansicht...")
            
            if not self.db_manager:
                print("❌ Kein Database Manager verfügbar")
                self.show_error_page(
                    "Fehler beim Anzeigen",
                    "Keine Datenbankverbindung verfügbar."
                )
                return
            
            audiobook = self.db_manager.get_audiobook(audiobook_id)
            
            if audiobook:
                print(f"✅ Hörbuch gefunden: {audiobook.title} (ID: {audiobook.id})")
                self.show_detail_page(audiobook)
            else:
                print(f"⚠️ Hörbuch mit ID {audiobook_id} nicht gefunden")
                self.show_error_page(
                    "Fehler beim Anzeigen",
                    f"Hörbuch mit ID {audiobook_id} wurde nicht gefunden."
                )
        except Exception as e:
            print(f"❌ Fehler beim Laden des Hörbuchs: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_page(
                "Fehler beim Anzeigen",
                f"Ein Fehler ist aufgetreten: {str(e)}"
            )
    
    # ================ LADE-BILDSCHIRM ================
    
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
        self.root.update_idletasks()
    
    # ================ BEENDEN ================
    
    def quit(self):
        """Beendet die Anwendung korrekt"""
        print("\n👋 Beende Audiobook Manager...")
        
        try:
            for after_id in self.root.tk.eval('after info').split():
                self.root.after_cancel(after_id)
        except:
            pass
        
        try:
            self.clear_main_frame()
            self.navigation.destroy()
        except:
            pass
        
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
        
        print("✅ Audiobook Manager erfolgreich beendet")
        sys.exit(0)
    
    def run(self):
        """Startet die Hauptloop der Anwendung"""
        print("\n🚀 Starte GUI...")
        print("ℹ️  Schließe das Fenster mit [X] oder über 'Beenden' in der Navigation")
        print("-" * 50)
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n⚠️  Abbruch durch Benutzer")
            self.quit()
        except Exception as e:
            print(f"\n❌ Unerwarteter Fehler: {e}")
            self.quit()

# ================ START-CODE ================

if __name__ == "__main__":
    print("=" * 50)
    print("🎧 AUDIOBOOK MANAGER - MAIN WINDOW")
    print("=" * 50)
    print(f"📁 Arbeitsverzeichnis: {os.getcwd()}")
    print(f"🐍 Python: {sys.executable}")
    print("-" * 50)
    
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"\n❌ Kritischer Fehler beim Start: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Programm beendet.")