import customtkinter as ctk
from .base_page import BasePage

class HomePage(BasePage):
    """Startseite der Anwendung - erbt von BasePage"""
    
    def __init__(self, master):
        # BasePage.__init__ aufrufen (erstellt Scrollbar etc.)
        super().__init__(master)
        
        # Widgets erstellen
        self.setup_widgets()
    
    def setup_widgets(self):
        """Erstellt alle Widgets der Startseite"""
        content = self.get_content_area()  # Holt den Content-Bereich
        
        # Willkommen-Text
        welcome_label = ctk.CTkLabel(
            content,
            text="Willkommen beim Audiobook Manager",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        welcome_label.pack(pady=(0, 20))
        
        # Untertitel
        subtitle_label = ctk.CTkLabel(
            content,
            text="Verwalte deine Hörbücher ganz einfach",
            font=ctk.CTkFont(size=20),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Feature-Übersicht
        self.create_features_section(content)
        
        # Quick Actions
        self.create_quick_actions(content)
        
        # Status-Anzeige
        self.create_status_section(content)
        
        # Test-Content für Scrollbar
        self.create_test_content(content)
    
    def create_features_section(self, parent):
        """Erstellt die Feature-Übersicht"""
        features_frame = ctk.CTkFrame(parent)
        features_frame.pack(fill="x", pady=(0, 40))
        
        # Titel
        features_title = ctk.CTkLabel(
            features_frame,
            text="Funktionen",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        features_title.pack(pady=(20, 20))
        
        # Features als Grid
        features_grid = ctk.CTkFrame(features_frame, fg_color="transparent")
        features_grid.pack(pady=(0, 20), padx=20)
        
        features = [
            ("📚", "Hörbuch-Verwaltung", "Erfasse und verwalte alle deine Hörbücher"),
            ("🔍", "Intelligente Suche", "Finde Hörbücher nach Genre, Autor oder Universum"),
            ("🌌", "Universen", "Verknüpfe Hörbücher in gemeinsamen Welten"),
            ("🖼️", "Bilder & Audio", "Lade Cover-Bilder und Hörbuch-Dateien hoch"),
            ("📊", "Statistiken", "Behalte den Überblick über deine Sammlung"),
            ("⚙️", "Anpassbar", "Passe alles an deine Bedürfnisse an")
        ]
        
        for i, (icon, title, description) in enumerate(features):
            row = i // 2
            col = i % 2
            
            feature_frame = ctk.CTkFrame(features_grid)
            feature_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Icon
            ctk.CTkLabel(
                feature_frame,
                text=icon,
                font=ctk.CTkFont(size=32)
            ).pack(pady=(15, 5))
            
            # Titel
            ctk.CTkLabel(
                feature_frame,
                text=title,
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=(0, 5))
            
            # Beschreibung
            ctk.CTkLabel(
                feature_frame,
                text=description,
                font=ctk.CTkFont(size=12),
                wraplength=200,
                text_color="gray"
            ).pack(pady=(0, 15))
        
        # Grid konfigurieren
        for i in range(2):
            features_grid.grid_columnconfigure(i, weight=1)
    
    def create_quick_actions(self, parent):
        """Erstellt Quick-Action Buttons"""
        actions_frame = ctk.CTkFrame(parent)
        actions_frame.pack(fill="x", pady=(0, 40))
        
        # Titel
        actions_title = ctk.CTkLabel(
            actions_frame,
            text="Schnellzugriff",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        actions_title.pack(pady=(20, 20))
        
        # Buttons
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(pady=(0, 20), padx=20)
        
        actions = [
            ("📚 Alle Hörbücher anzeigen", "audiobooks"),
            ("➕ Neues Hörbuch erfassen", "add"),
            ("🔍 Suche starten", "search"),
            ("🌌 Universen verwalten", "universes")
        ]
        
        for text, page in actions:
            button = ctk.CTkButton(
                buttons_frame,
                text=text,
                font=ctk.CTkFont(size=14),
                height=40,
                command=lambda p=page: self.navigate_to(p)
            )
            button.pack(side="left", padx=5, pady=5)
    
    def create_status_section(self, parent):
        """Erstellt den Status-Bereich"""
        status_frame = ctk.CTkFrame(parent)
        status_frame.pack(fill="x")
        
        # Titel
        status_title = ctk.CTkLabel(
            status_frame,
            text="Systemstatus",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        status_title.pack(pady=(15, 15))
        
        # Status-Einträge
        status_entries = [
            ("Database Service", "✅ Verfügbar", "success"),
            ("File Management Service", "✅ Verfügbar", "success"),
            ("Search Service", "🔧 In Entwicklung", "warning"),
            ("GUI Service", "🚀 Läuft", "success")
        ]
        
        for service, status, status_type in status_entries:
            entry_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
            entry_frame.pack(fill="x", padx=20, pady=5)
            
            ctk.CTkLabel(
                entry_frame,
                text=service,
                font=ctk.CTkFont(size=14)
            ).pack(side="left")
            
            ctk.CTkLabel(
                entry_frame,
                text=status,
                font=ctk.CTkFont(size=14),
                text_color="green" if status_type == "success" else "orange"
            ).pack(side="right")
    
    def create_test_content(self, parent):
        """Erstellt Test-Inhalt um Scrollbar zu testen"""
        test_frame = ctk.CTkFrame(parent)
        test_frame.pack(fill="x", pady=(30, 0))
        
        test_label = ctk.CTkLabel(
            test_frame,
            text="📜 Scrollbar Test - Diese Seite hat viel Inhalt",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        test_label.pack(pady=20)
        
        # Viele Test-Labels
        for i in range(1, 21):
            label = ctk.CTkLabel(
                test_frame,
                text=f"Test-Eintrag {i}: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                font=ctk.CTkFont(size=12),
                wraplength=600
            )
            label.pack(pady=2, anchor="w")
        
        # Footer
        footer = ctk.CTkLabel(
            test_frame,
            text="↓ Scroll weiter nach unten ↓",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        footer.pack(pady=20)
    
    def navigate_to(self, page_name: str):
        """Navigation zu einer anderen Seite (wird von MainWindow gehandled)"""
        print(f"HomePage möchte navigieren zu: {page_name}")
        # Event auslösen oder callback