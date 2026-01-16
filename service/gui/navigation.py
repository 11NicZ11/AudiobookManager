import customtkinter as ctk
from typing import Callable

class NavigationFrame(ctk.CTkFrame):
    # Navigation/Sidebar mit allen Navigations-Buttons"""
    
    def __init__(self, master, command: Callable = None):
        super().__init__(master, corner_radius=0)
        
        self.command = command
        self.active_button = None
        self.buttons = {}
        
        self.setup_grid()
        self.create_widgets()
    
    def setup_grid(self):
        # Konfiguriert das Grid-Layout
        self.grid_rowconfigure(0, weight=0)  # Logo
        self.grid_rowconfigure(1, weight=0)  # Buttons oben
        self.grid_rowconfigure(2, weight=1)  # Flexibler Raum
        self.grid_rowconfigure(3, weight=0)  # Buttons unten
        self.grid_rowconfigure(4, weight=0)  # Info
    
    def create_widgets(self):
        # Erstellt alle Widgets der Navigation
        
        # Logo/Branding
        self.logo_label = ctk.CTkLabel(
            self,
            text="📚 Audiobook\nManager",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 40))
        
        # Navigations-Buttons (oben)
        self.create_navigation_buttons()
        
        # Einstellungs-Buttons (unten)
        self.create_bottom_buttons()
        
        # Status/Info
        self.create_info_section()
    
    def create_navigation_buttons(self):
        # Erstellt die Haupt-Navigationsbuttons
        nav_buttons = [
            ("🏠", "home", "Startseite"),
            ("📚", "audiobooks", "Alle Hörbücher"),
            ("➕", "add", "Hörbuch hinzufügen"),
            ("🔍", "search", "Suche"),
            ("🌌", "universes", "Universen")
        ]
        
        for i, (icon, name, tooltip) in enumerate(nav_buttons):
            button = ctk.CTkButton(
                self,
                text=f"  {icon}  {tooltip}",
                font=ctk.CTkFont(size=14),
                height=50,
                anchor="w",
                command=lambda n=name: self.button_clicked(n)
            )
            button.grid(row=i+1, column=0, padx=10, pady=(0, 10), sticky="ew")
            self.buttons[name] = button
    
    def create_bottom_buttons(self):
        # Erstellt Buttons unten in der Navigation
        bottom_buttons = [
            ("⚙️", "settings", "Einstellungen"),
            ("❓", "help", "Hilfe"),
            ("🚪", "quit", "Beenden")
        ]
        
        for i, (icon, name, tooltip) in enumerate(bottom_buttons):
            button = ctk.CTkButton(
                self,
                text=f"  {icon}  {tooltip}",
                font=ctk.CTkFont(size=14),
                height=50,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda n=name: self.button_clicked(n)
            )
            button.grid(row=3+i, column=0, padx=10, pady=(0, 10), sticky="ew")
            self.buttons[name] = button
    
    def create_info_section(self):
        # Erstellt den Info-Bereich ganz unten
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=6, column=0, padx=10, pady=(0, 20), sticky="ew")
        
        # Status-Anzeige
        self.status_label = ctk.CTkLabel(
            info_frame,
            text="✅ Alle Services bereit",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack()
        
        # Version
        version_label = ctk.CTkLabel(
            info_frame,
            text="v0.1.0",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        version_label.pack(pady=(5, 0))
    
    def button_clicked(self, button_name: str):
        """Wird aufgerufen wenn ein Button geklickt wird"""
        if button_name == "quit":
            self.master.quit()
            return
    
        # Aktiven Button visualisieren
        self.set_active_button(button_name)
    
        # Command ausführen (Navigation)
        if self.command:
            self.command(button_name)
    
    def set_active_button(self, button_name: str):
        # Markiert einen Button als aktiv
        # Vorherigen aktiven Button zurücksetzen
        if self.active_button and self.active_button in self.buttons:
            self.buttons[self.active_button].configure(
                fg_color=("gray75", "gray25")  # Standard
            )
        
        # Neuen Button als aktiv markieren
        if button_name in self.buttons:
            self.buttons[button_name].configure(
                fg_color=("gray65", "gray35")  # Aktiv-Farbe
            )
            self.active_button = button_name
    
    def update_status(self, status_text: str, is_ok: bool = True):
        # Aktualisiert den Status-Text
        emoji = "✅" if is_ok else "⚠️"
        self.status_label.configure(text=f"{emoji} {status_text}")