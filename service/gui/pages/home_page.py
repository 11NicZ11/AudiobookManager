import customtkinter as ctk
from .base_page import BasePage

class HomePage(BasePage):
    """Startseite der Anwendung - erbt von BasePage"""
    
    def __init__(self, master, db_manager=None):
        """Initialisiert die HomePage
        
        Args:
            master: Parent-Widget
            db_manager: DatabaseManager Instanz (optional)
        """
        # db_manager speichern (für eventuelle zukünftige Verwendung)
        self.db_manager = db_manager
        
        # BasePage.__init__ aufrufen (erstellt Scrollbar etc.)
        super().__init__(master)
        
        # Widgets erstellen
        self.setup_widgets()
    
    def setup_widgets(self):
        """Erstellt alle Widgets der Startseite"""
        content = self.get_content_area()
        
        # Willkommen-Text
        welcome_label = ctk.CTkLabel(
            content,
            text="Willkommen beim Audiobook Manager",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        welcome_label.pack(pady=(50, 20))
        
        # Untertitel
        subtitle_label = ctk.CTkLabel(
            content,
            text="Verwalte deine Hörbücher ganz einfach",
            font=ctk.CTkFont(size=20),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 60))
        
        # Haupt-Buttons zentriert
        self.create_main_buttons(content)
        
        # Footer (optional)
        footer_label = ctk.CTkLabel(
            content,
            text="Wähle eine Aktion aus, um zu beginnen",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        footer_label.pack(pady=(40, 20))
    
    def create_main_buttons(self, parent):
        """Erstellt die beiden Haupt-Buttons zentriert auf der Seite"""
        
        # Container für die Buttons (zentriert)
        buttons_container = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_container.pack(expand=True, pady=20)
        
        # "Alle Hörbücher anzeigen" Button
        audiobooks_btn = ctk.CTkButton(
            buttons_container,
            text="📚 Alle Hörbücher anzeigen",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=80,
            width=350,
            fg_color=("#3a7ebf", "#1f538d"),
            hover_color=("#2a6faf", "#0f3f7a"),
            command=lambda: self.navigate_to("audiobooks")
        )
        audiobooks_btn.pack(pady=15)
        
        # "Neues Hörbuch" Button
        add_btn = ctk.CTkButton(
            buttons_container,
            text="➕ Neues Hörbuch",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=80,
            width=350,
            fg_color=("#3a7ebf", "#1f538d"),
            hover_color=("#2a6faf", "#0f3f7a"),
            command=lambda: self.navigate_to("add")
        )
        add_btn.pack(pady=15)
    
    def navigate_to(self, page_name: str):
        """Navigation zu einer anderen Seite"""
        print(f"HomePage navigiert zu: {page_name}")
        
        # Events an MainWindow senden
        if page_name == "audiobooks":
            self.master.event_generate("<<NavigateToAudiobookList>>")
        elif page_name == "add":
            self.master.event_generate("<<AddAudiobook>>")