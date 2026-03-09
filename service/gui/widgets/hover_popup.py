"""
Hover-Popup für schnelle Anzeige von Informationen
Öffnet sich unter/über der Maus und schließt sich beim Verlassen
"""
import customtkinter as ctk
from typing import Optional, Callable, List
from tkinter import Toplevel
import time

class HoverPopup:
    """
    Ein Popup-Fenster das unter/über der Maus erscheint und sich automatisch schließt
    
    Features:
    - Öffnet unter der Maus (oder über wenn nicht genug Platz)
    - Schließt sich wenn Maus das Popup verlässt
    - Kann Text, Buttons oder benutzerdefinierte Widgets anzeigen
    - Verzögerung bevor es sich schließt (für versehentliches Verlassen)
    """
    
    def __init__(self, master):
        """
        Args:
            master: Parent-Widget (für Koordinaten-Berechnung)
        """
        self.master = master
        self.popup = None
        self.leave_timer = None
        self.leave_delay = 300  # ms bevor Popup schließt
        self.is_open = False
        self.current_widget = None
        
        # Popup-Größe (kann dynamisch angepasst werden)
        self.popup_width = 350
        self.popup_height = 400
        
        # Standard-Farben (angepasst an CustomTkinter Theme)
        self.bg_color = ("gray95", "gray20")  # Hell/Dunkel Modus
        self.hover_color = ("gray85", "gray25")
        self.border_color = ("gray70", "gray30")
    
    def show_popup(self, 
                   widget, 
                   content_func: Callable[[ctk.CTkFrame], None],
                   width: int = 350,
                   height: int = 400,
                   leave_delay: int = 300):
        """
        Zeigt ein Popup-Fenster unter/über der Maus an
        
        Args:
            widget: Das Widget das den Hover auslöst
            content_func: Funktion die den Content-Frame befüllt
            width: Breite des Popups
            height: Höhe des Popups
            leave_delay: Verzögerung in ms bevor Popup schließt
        """
        # Schließe altes Popup falls offen
        self.close_popup()
        
        self.current_widget = widget
        self.popup_width = width
        self.popup_height = height
        self.leave_delay = leave_delay
        
        # Mausposition ermitteln
        x = widget.winfo_pointerx()
        y = widget.winfo_pointery()
        
        # Bildschirmgröße ermitteln
        screen_width = widget.winfo_screenwidth()
        screen_height = widget.winfo_screenheight()
        
        # Position berechnen (bevorzugt unter Maus)
        popup_x = x
        popup_y = y + 20  # 20px unter Maus
        
        # Prüfe ob nach unten genug Platz ist
        if popup_y + self.popup_height > screen_height:
            # Nicht genug Platz unten -> über Maus anzeigen
            popup_y = y - self.popup_height - 20
        
        # Prüfe ob nach rechts genug Platz ist
        if popup_x + self.popup_width > screen_width:
            popup_x = screen_width - self.popup_width - 20
        
        # Prüfe ob nach links genug Platz ist
        if popup_x < 20:
            popup_x = 20
        
        # Popup erstellen
        self.popup = Toplevel(self.master)
        self.popup.withdraw()  # Versteckt bis vollständig konfiguriert
        self.popup.title("")
        self.popup.geometry(f"{self.popup_width}x{self.popup_height}+{popup_x}+{popup_y}")
        
        # Popup-Eigenschaften
        self.popup.overrideredirect(True)  # Keine Fensterdekoration
        self.popup.attributes('-topmost', True)  # Immer im Vordergrund
        self.popup.configure(bg='black')  # Hintergrund für Border-Effekt
        
        # Hauptframe mit Padding für Border
        main_frame = ctk.CTkFrame(
            self.popup,
            fg_color=self.bg_color,
            corner_radius=10,
            border_width=2,
            border_color=self.border_color
        )
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Header mit Schließen-Button
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent", height=30)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # Titel (kann durch content_func überschrieben werden)
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="📚 Universum-Bücher",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.title_label.pack(side="left")
        
        # Schließen-Button
        close_btn = ctk.CTkButton(
            header_frame,
            text="✕",
            width=25,
            height=25,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            hover_color=self.hover_color,
            command=self.close_popup
        )
        close_btn.pack(side="right")
        
        # Content Frame (wird von content_func befüllt)
        self.content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Benutzerdefinierten Content laden
        content_func(self.content_frame)
        
        # Events für automatisches Schließen
        self.setup_close_events(widget)
        
        # Popup anzeigen
        self.popup.deiconify()
        self.is_open = True
    
    def setup_close_events(self, trigger_widget):
        """
        Richtet Events ein damit Popup schließt wenn Maus es verlässt
        
        Args:
            trigger_widget: Das Widget das den Hover ausgelöst hat
        """
        # Wenn Maus Popup verlässt -> Timer starten
        self.popup.bind("<Leave>", self.on_leave_popup)
        self.popup.bind("<Enter>", self.on_enter_popup)
        
        # Wenn Maus Trigger-Widget verlässt -> Timer starten
        trigger_widget.bind("<Leave>", self.on_leave_trigger, add="+")
        
        # Globaler Escape-Key zum Schließen
        self.popup.bind("<Escape>", lambda e: self.close_popup())
        
        # Wenn Popup den Fokus verliert (z.B. Alt-Tab)
        self.popup.bind("<FocusOut>", lambda e: self.close_popup())
    
    def on_leave_popup(self, event):
        """Wird aufgerufen wenn Maus Popup verlässt"""
        self.start_close_timer()
    
    def on_enter_popup(self, event):
        """Wird aufgerufen wenn Maus Popup betritt"""
        self.cancel_close_timer()
    
    def on_leave_trigger(self, event):
        """Wird aufgerufen wenn Maus Trigger-Widget verlässt"""
        # Prüfe ob Maus wirklich das Trigger-Widget verlassen hat
        # und nicht nur zu einem Child-Widget gewandert ist
        x, y = event.x_root, event.y_root
        
        # Prüfe ob Maus über Popup ist
        if self.popup and self.is_open:
            popup_x = self.popup.winfo_rootx()
            popup_y = self.popup.winfo_rooty()
            popup_w = self.popup.winfo_width()
            popup_h = self.popup.winfo_height()
            
            # Wenn Maus im Popup -> nicht schließen
            if (popup_x <= x <= popup_x + popup_w and 
                popup_y <= y <= popup_y + popup_h):
                return
        
        self.start_close_timer()
    
    def start_close_timer(self):
        """Startet Timer zum Schließen des Popups"""
        self.cancel_close_timer()
        self.leave_timer = self.master.after(
            self.leave_delay, 
            self.close_popup
        )
    
    def cancel_close_timer(self):
        """Bricht den Schließen-Timer ab"""
        if self.leave_timer:
            try:
                self.master.after_cancel(self.leave_timer)
            except:
                pass
            self.leave_timer = None
    
    def close_popup(self):
        """Schließt das Popup"""
        self.cancel_close_timer()
        if self.popup:
            try:
                self.popup.destroy()
            except:
                pass
            self.popup = None
        self.is_open = False
        self.current_widget = None
    
    def is_popup_open(self) -> bool:
        """Prüft ob Popup gerade offen ist"""
        return self.is_open and self.popup is not None


class UniverseBooksPopup:
    """
    Spezialisiertes Popup für die Anzeige von Hörbüchern eines Universums
    """
    
    def __init__(self, master, db_manager):
        """
        Args:
            master: Parent-Widget
            db_manager: DatabaseManager Instanz
        """
        self.master = master
        self.db_manager = db_manager
        self.hover_popup = HoverPopup(master)
        self.current_universe = None
        self.current_audiobook = None
    
    def show_for_universe(self, 
                         trigger_widget, 
                         universe_name: str, 
                         current_audiobook=None):
        """
        Zeigt alle Hörbücher eines Universums im Popup an
        
        Args:
            trigger_widget: Widget das den Hover auslöst
            universe_name: Name des Universums
            current_audiobook: Das aktuell angezeigte Hörbuch (zum Hervorheben)
        """
        if not universe_name:
            return
        
        self.current_universe = universe_name
        self.current_audiobook = current_audiobook
        
        # Hörbücher aus Datenbank laden
        audiobooks = self.db_manager.get_audiobooks_by_universe(universe_name)
        
        if not audiobooks:
            return
        
        # Anzahl der Bücher bestimmt Popup-Größe
        book_count = len(audiobooks)
        popup_height = min(400, 50 + book_count * 45)  # Max 400px, pro Buch ~45px
        
        self.hover_popup.show_popup(
            widget=trigger_widget,
            content_func=lambda frame: self.create_content(frame, audiobooks),
            width=450,
            height=popup_height,
            leave_delay=400  # 400ms Verzögerung vor Schließen
        )
    
    def create_content(self, parent, audiobooks):
        """
        Erstellt den Inhalt des Popups
        
        Args:
            parent: Parent-Frame
            audiobooks: Liste der Hörbücher
        """
        # Header mit Universum-Name
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        universe_label = ctk.CTkLabel(
            header_frame,
            text=f"🌌 {self.current_universe}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="skyblue"
        )
        universe_label.pack(side="left")
        
        count_label = ctk.CTkLabel(
            header_frame,
            text=f"{len(audiobooks)} Bücher",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        count_label.pack(side="right")
        
        # Scrollbare Liste für Hörbücher
        scroll_frame = ctk.CTkScrollableFrame(
            parent,
            height=min(300, len(audiobooks) * 45)
        )
        scroll_frame.pack(fill="both", expand=True)
        
        # Hörbücher anzeigen
        for i, book in enumerate(audiobooks):
            self.create_book_row(scroll_frame, i, book)
    
    def create_book_row(self, parent, index, audiobook):
        """
        Erstellt eine Zeile für ein Hörbuch
        
        Args:
            parent: Parent-Frame
            index: Zeilenindex
            audiobook: Audiobook-Objekt
        """
        # Ist das das aktuell angezeigte Buch?
        is_current = (self.current_audiobook and 
                     self.current_audiobook.id == audiobook.id)
        
        row_frame = ctk.CTkFrame(
            parent,
            height=40,
            fg_color=("gray90", "gray25") if is_current else "transparent",
            border_width=1 if is_current else 0,
            border_color="skyblue" if is_current else None,
            corner_radius=5
        )
        row_frame.pack(fill="x", pady=1)
        row_frame.pack_propagate(False)
        
        # Hover-Effekt
        def on_enter(e):
            if not is_current:
                row_frame.configure(fg_color=("gray85", "gray30"))
        
        def on_leave(e):
            if not is_current:
                row_frame.configure(fg_color="transparent")
        
        row_frame.bind("<Enter>", on_enter)
        row_frame.bind("<Leave>", on_leave)
        
        # Grid-Layout
        row_frame.grid_columnconfigure(0, weight=0)  # Icon
        row_frame.grid_columnconfigure(1, weight=1)  # Titel
        row_frame.grid_columnconfigure(2, weight=0)  # Jahr
        row_frame.grid_columnconfigure(3, weight=0)  # Button
        
        # Icon (aktuelle Position oder Standard)
        icon = "▶️ " if is_current else "📖 "
        icon_label = ctk.CTkLabel(
            row_frame,
            text=icon,
            font=ctk.CTkFont(size=14),
            width=30
        )
        icon_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
        
        # Titel
        title_text = audiobook.title[:40] + ("..." if len(audiobook.title) > 40 else "")
        title_label = ctk.CTkLabel(
            row_frame,
            text=title_text,
            font=ctk.CTkFont(size=13, weight="bold" if is_current else "normal"),
            anchor="w"
        )
        title_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Jahr
        year_text = str(audiobook.year) if audiobook.year else "-"
        year_label = ctk.CTkLabel(
            row_frame,
            text=year_text,
            font=ctk.CTkFont(size=12),
            width=50,
            text_color="gray"
        )
        year_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
        # "Gehe zu" Button
        if not is_current:
            goto_btn = ctk.CTkButton(
                row_frame,
                text="→",
                width=30,
                height=30,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                hover_color=("gray80", "gray35"),
                command=lambda: self.navigate_to_book(audiobook)
            )
            goto_btn.grid(row=0, column=3, padx=(5, 10), pady=5, sticky="e")
    
    def navigate_to_book(self, audiobook):
        """
        Navigiert zu einem Hörbuch
        
        Args:
            audiobook: Das anzuzeigende Hörbuch
        """
        # Popup schließen
        self.hover_popup.close_popup()
        
        # Event an MainWindow senden
        self.master.event_generate(
            "<<ShowAudiobookDetail>>",
            data=str(audiobook.id)
        )


class SimpleHoverInfo:
    """
    Einfaches Hover-Popup für kurze Infotexte
    """
    
    def __init__(self, master):
        self.master = master
        self.hover_popup = HoverPopup(master)
    
    def show_info(self, trigger_widget, title: str, text: str):
        """
        Zeigt einen einfachen Infotext im Popup
        
        Args:
            trigger_widget: Widget das den Hover auslöst
            title: Titel des Popups
            text: Anzuzeigender Text
        """
        self.hover_popup.show_popup(
            widget=trigger_widget,
            content_func=lambda frame: self.create_info_content(frame, title, text),
            width=300,
            height=150,
            leave_delay=300
        )
    
    def create_info_content(self, parent, title, text):
        """Erstellt einfachen Info-Content"""
        # Titel
        title_label = ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Text mit Wrap
        text_label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=12),
            wraplength=250,
            justify="left"
        )
        text_label.pack(fill="both", expand=True)