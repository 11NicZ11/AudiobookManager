"""
Seite zur Anzeige aller Hörbücher
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import List, Optional
from gui.pages.base_page import BasePage
from gui.widgets.hover_popup import UniverseBooksPopup


class AudiobookListPage(BasePage):
    """Zeigt eine Liste aller Hörbücher aus der Datenbank an"""
    
    def __init__(self, master, db_manager=None):
        """
        Args:
            master: Parent-Widget
            db_manager: DatabaseManager Instanz
        """
        super().__init__(master)
        self.db_manager = db_manager
        self.audiobooks = []
        self.filtered_audiobooks = []
        
        # Widgets-Container
        self.count_label = None
        self.status_label = None
        self.search_entry = None
        self.list_frame = None
        self.status_info_label = None
        self.search_frame = None
        self.list_container = None
        
        # Hover-Popup für Universum
        self.universe_popup = UniverseBooksPopup(self.master, self.db_manager)
        self.popup_timer = None
        self.current_hover_book = None
        
        # Speicher für die zuletzt angeklickte Hörbuch-ID (für Event-Fallback)
        self.last_clicked_audiobook_id = None
        
        # UI Komponenten erstellen
        self.setup_initial_ui()
        
        # Daten laden
        self.after(100, self.load_audiobooks)
    
    def setup_initial_ui(self):
        """Erstellt das Grundgerüst der UI (ohne Daten)"""
        content = self.get_content_area()
        
        # === Kopfbereich ===
        header_frame = ctk.CTkFrame(content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Titel
        title_label = ctk.CTkLabel(
            header_frame,
            text="📚 Alle Hörbücher",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(side="left")
        
        # Anzahl-Anzeige
        self.count_label = ctk.CTkLabel(
            header_frame,
            text="Lade Daten...",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.count_label.pack(side="right", padx=10)
        
        # Status-Anzeige
        self.status_label = ctk.CTkLabel(
            content,
            text="🔄 Verbinde mit Datenbank...",
            font=ctk.CTkFont(size=12),
            text_color="blue"
        )
        self.status_label.pack(pady=(0, 20))
        
        # === Suchleiste (ohne Filter-Dropdown) ===
        self.search_frame = ctk.CTkFrame(content, fg_color="transparent")
        self.search_frame.pack(fill="x", pady=(0, 20))
        
        # Suchfeld Container
        search_container = ctk.CTkFrame(self.search_frame, fg_color="transparent")
        search_container.pack(fill="x")
        
        ctk.CTkLabel(
            search_container,
            text="🔍 Suche:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_container,
            width=400,
            placeholder_text="Titel, Autor, Genre, Universum...",
            state="disabled"
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # === Container für die Hörbuch-Liste ===
        self.list_container = ctk.CTkFrame(content)
        self.list_container.pack(fill="both", expand=True, pady=(0, 20))
        
        # Scrollbare Liste
        self.list_frame = ctk.CTkScrollableFrame(
            self.list_container,
            height=400
        )
        self.list_frame.pack(fill="both", expand=True)
        
        # Lade-Animation
        self.show_loading_animation()
        
        # === Status-Bar ===
        status_frame = ctk.CTkFrame(content, fg_color="transparent")
        status_frame.pack(fill="x")
        
        self.status_info_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_info_label.pack(side="left")
        
        # Refresh-Button
        refresh_button = ctk.CTkButton(
            status_frame,
            text="🔄 Aktualisieren",
            width=120,
            command=self.refresh_data
        )
        refresh_button.pack(side="right", padx=5)
    
    def show_loading_animation(self):
        """Zeigt eine Lade-Animation in der Liste"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        loading_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        loading_frame.pack(expand=True, pady=50)
        
        ctk.CTkLabel(
            loading_frame,
            text="⏳",
            font=ctk.CTkFont(size=48)
        ).pack(pady=20)
        
        ctk.CTkLabel(
            loading_frame,
            text="Lade Hörbücher...",
            font=ctk.CTkFont(size=16)
        ).pack()
    
    def load_audiobooks(self):
        """Lädt Hörbücher aus der Datenbank"""
        print(f"🔄 Lade Hörbücher, db_manager vorhanden: {self.db_manager is not None}")
        
        if not self.db_manager:
            self.show_error_message(
                "Keine Datenbankverbindung",
                "Der Database Manager konnte nicht initialisiert werden.\n\n"
                "Bitte überprüfe:\n"
                "• Ob die Datenbankdatei existiert\n"
                "• Ob der Ordner 'data' Schreibrechte hat\n"
                "• Ob SQLite3 korrekt installiert ist"
            )
            return
        
        try:
            self.status_label.configure(text="🔄 Lade Hörbücher aus Datenbank...", text_color="blue")
            self.update_idletasks()
            
            self.audiobooks = self.db_manager.get_all_audiobooks()
            print(f"✅ {len(self.audiobooks)} Hörbücher aus Datenbank geladen")
            
            if len(self.audiobooks) == 0:
                self.show_empty_database_message()
            else:
                self.filtered_audiobooks = self.audiobooks.copy()
                self.enable_search()
                self.display_audiobooks()
                self.status_label.configure(
                    text=f"✅ {len(self.audiobooks)} Hörbücher geladen", 
                    text_color="green"
                )
                self.count_label.configure(text=f"{len(self.audiobooks)} Hörbücher")
                
        except Exception as e:
            error_msg = f"Fehler beim Laden aus der Datenbank: {str(e)}"
            print(f"❌ {error_msg}")
            self.show_error_message(
                "Datenbankfehler",
                f"Die Hörbücher konnten nicht geladen werden:\n\n{error_msg}\n\n"
                "Bitte überprüfe die Datenbankverbindung."
            )
    
    def enable_search(self):
        """Aktiviert die Suchleiste"""
        if self.search_entry:
            self.search_entry.configure(state="normal")
            self.search_entry.bind("<KeyRelease>", self.on_search_changed)
    
    def display_audiobooks(self):
        """Zeigt die Hörbücher in der Liste an"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        if not self.filtered_audiobooks:
            self.show_no_results_message()
            self.status_info_label.configure(text="Keine Hörbücher gefunden")
            return
        
        # Kopfzeile
        header_frame = ctk.CTkFrame(self.list_frame, height=40)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)
        
        header_frame.grid_columnconfigure(0, weight=3)
        header_frame.grid_columnconfigure(1, weight=2)
        header_frame.grid_columnconfigure(2, weight=1)
        header_frame.grid_columnconfigure(3, weight=1)
        header_frame.grid_columnconfigure(4, weight=1)
        
        headers = [
            ("📖 Titel", 0),
            ("✍️ Autor", 1),
            ("🏷️ Genre", 2),
            ("📅 Jahr", 3),
            ("⚡ Aktionen", 4)
        ]
        
        for text, col in headers:
            label = ctk.CTkLabel(
                header_frame,
                text=text,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            label.grid(row=0, column=col, padx=10, pady=10, sticky="w")
        
        # Hörbücher anzeigen
        for i, audiobook in enumerate(self.filtered_audiobooks):
            self.create_audiobook_row(i, audiobook)
        
        self.status_info_label.configure(
            text=f"📊 Zeige {len(self.filtered_audiobooks)} von {len(self.audiobooks)} Hörbüchern"
        )
    
    def create_tooltip(self, widget, text):
        """
        Erstellt einen einfachen Tooltip für ein Widget
        
        Args:
            widget: Das Widget für das der Tooltip erstellt werden soll
            text: Der anzuzeigende Text
        """
        def show_tooltip(event):
            # Tooltip-Fenster erstellen
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Tooltip-Fenster
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            # Rahmen mit Hintergrund
            frame = tk.Frame(
                self.tooltip,
                background="#ffffe0",
                relief="solid",
                borderwidth=1
            )
            frame.pack()
            
            # Text
            label = tk.Label(
                frame,
                text=text,
                justify="left",
                background="#ffffe0",
                foreground="#000000",
                font=("Segoe UI", 10),
                padx=5,
                pady=2
            )
            label.pack()
        
        def hide_tooltip(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                self.tooltip = None
        
        # Events binden
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def create_audiobook_row(self, index: int, audiobook):
        """Erstellt eine Zeile für ein Hörbuch mit Hover-Popup für Universum"""
        row_frame = ctk.CTkFrame(
            self.list_frame,
            height=50,
            fg_color=("gray95", "gray20") if index % 2 == 0 else ("gray90", "gray25")
        )
        row_frame.pack(fill="x", pady=1)
        row_frame.pack_propagate(False)
        
        row_frame.grid_columnconfigure(0, weight=3)
        row_frame.grid_columnconfigure(1, weight=2)
        row_frame.grid_columnconfigure(2, weight=1)
        row_frame.grid_columnconfigure(3, weight=1)
        row_frame.grid_columnconfigure(4, weight=1)
        
        # === Titel mit Universum-Indikator ===
        title_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Universum-Indikator mit Hover-Popup
        if audiobook.universe and audiobook.universe.strip():
            universe_btn = ctk.CTkButton(
                title_frame,
                text="🌌",
                font=ctk.CTkFont(size=14),
                width=25,
                height=25,
                fg_color="transparent",
                hover_color=("gray80", "gray30"),
                command=lambda ab=audiobook: self.show_universe_popup_click(ab)
            )
            universe_btn.pack(side="left")
            
            # Hover-Event für verzögertes Popup
            universe_btn.bind("<Enter>", lambda e, ab=audiobook: self.schedule_universe_popup(e, ab))
            universe_btn.bind("<Leave>", lambda e: self.cancel_universe_popup())
        
        # Titel
        title_text = audiobook.title[:60] + ("..." if len(audiobook.title) > 60 else "")
        title_label = ctk.CTkLabel(
            title_frame,
            text=title_text,
            font=ctk.CTkFont(size=13, weight="bold" if audiobook.universe else "normal"),
            anchor="w"
        )
        title_label.pack(side="left", padx=(5, 0))
        
        # === Autor ===
        author_text = audiobook.author[:30] + ("..." if len(audiobook.author) > 30 else "") if audiobook.author else "-"
        author_label = ctk.CTkLabel(
            row_frame,
            text=author_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        author_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # === Genre/Subgenre ===
        genre_text = audiobook.genre if audiobook.genre else "-"
        if audiobook.subgenre and audiobook.subgenre.strip():
            genre_text = f"{genre_text} › {audiobook.subgenre[:15]}"
        
        genre_label = ctk.CTkLabel(
            row_frame,
            text=genre_text[:20] + ("..." if len(genre_text) > 20 else ""),
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        genre_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        # === Jahr ===
        year_text = str(audiobook.year) if audiobook.year else "-"
        year_label = ctk.CTkLabel(
            row_frame,
            text=year_text,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        year_label.grid(row=0, column=3, padx=10, pady=5, sticky="w")
        
        # === Action-Buttons ===
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=4, padx=10, pady=5, sticky="e")
        
        # Detail-Button (Auge)
        detail_btn = ctk.CTkButton(
            action_frame,
            text="👁️",
            width=35,
            height=35,
            font=ctk.CTkFont(size=16),
            command=lambda ab=audiobook: self.on_view_details(ab)
        )
        detail_btn.pack(side="left", padx=2)
        
        # Tooltip für Detail-Button
        self.create_tooltip(detail_btn, "Details anzeigen")
        
        # Edit-Button (Stift)
        edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️",
            width=35,
            height=35,
            font=ctk.CTkFont(size=16),
            command=lambda ab=audiobook: self.on_edit_audiobook(ab)
        )
        edit_btn.pack(side="left", padx=2)
        
        # Tooltip für Edit-Button
        self.create_tooltip(edit_btn, "Hörbuch bearbeiten")
        
        # Lösch-Button (rotes X)
        delete_btn = ctk.CTkButton(
            action_frame,
            text="✕",
            width=35,
            height=35,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="transparent",
            text_color="red",
            hover_color=("red", "darkred"),
            border_width=1,
            border_color="red",
            command=lambda ab=audiobook: self.on_delete_audiobook(ab)
        )
        delete_btn.pack(side="left", padx=2)
        
        # Tooltip für Lösch-Button
        self.create_tooltip(delete_btn, "Hörbuch löschen")
        
        # ID-Anzeige
        if hasattr(audiobook, 'display_id'):
            id_label = ctk.CTkLabel(
                action_frame,
                text=audiobook.display_id,
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            id_label.pack(side="left", padx=(5, 0))
    
    # ================ LÖSCH-FUNKTION ================
    
    def on_delete_audiobook(self, audiobook):
        """
        Löscht ein Hörbuch nach Bestätigung
        
        Args:
            audiobook: Das zu löschende Hörbuch
        """
        print(f"🗑️ Lösche Hörbuch: {audiobook.title} (ID: {audiobook.id})")
        
        # Prüfe ob audiobook und ID existieren
        if not audiobook or not audiobook.id:
            print("❌ Ungültiges Hörbuch-Objekt oder keine ID")
            return
        
        # Bestätigungsdialog
        result = messagebox.askyesno(
            "Hörbuch löschen",
            f"Möchtest du das Hörbuch\n\n\"{audiobook.title}\"\n\nwirklich löschen?\n\nDiese Aktion kann nicht rückgängig gemacht werden!",
            icon="warning"
        )
        
        if result:
            try:
                # Hörbuch aus der Datenbank löschen
                success = self.db_manager.delete_audiobook(audiobook.id)
                
                if success:
                    print(f"✅ Hörbuch '{audiobook.title}' erfolgreich gelöscht")
                    
                    # Zeige Erfolgsmeldung
                    messagebox.showinfo(
                        "Erfolg",
                        f"Das Hörbuch \"{audiobook.title}\" wurde erfolgreich gelöscht."
                    )
                    
                    # Liste neu laden
                    self.load_audiobooks()
                else:
                    print(f"❌ Fehler beim Löschen des Hörbuchs")
                    messagebox.showerror(
                        "Fehler",
                        f"Das Hörbuch \"{audiobook.title}\" konnte nicht gelöscht werden."
                    )
            except Exception as e:
                print(f"❌ Fehler beim Löschen: {e}")
                messagebox.showerror(
                    "Fehler",
                    f"Beim Löschen ist ein Fehler aufgetreten:\n{str(e)}"
                )
    
    # ================ HOVER-POPUP METHODEN ================
    
    def schedule_universe_popup(self, event, audiobook):
        """Plant das Öffnen des Popups mit Verzögerung"""
        self.cancel_universe_popup()
        self.current_hover_book = audiobook
        self.popup_timer = self.after(300, lambda: self.show_universe_popup(audiobook))

    def cancel_universe_popup(self):
        """Bricht geplantes Popup ab"""
        if self.popup_timer:
            try:
                self.after_cancel(self.popup_timer)
            except:
                pass
            self.popup_timer = None
        self.current_hover_book = None

    def show_universe_popup(self, audiobook):
        """Zeigt Popup mit allen Büchern des Universums (Hover)"""
        if audiobook and audiobook.universe and audiobook.universe.strip():
            self.universe_popup.show_for_universe(
                trigger_widget=self,
                universe_name=audiobook.universe,
                current_audiobook=audiobook
            )

    def show_universe_popup_click(self, audiobook):
        """Zeigt Popup mit allen Büchern des Universums (Klick)"""
        if audiobook and audiobook.universe and audiobook.universe.strip():
            self.universe_popup.show_for_universe(
                trigger_widget=self,
                universe_name=audiobook.universe,
                current_audiobook=audiobook
            )
    
    # ================ MESSAGE HANDLER ================
    
    def show_empty_database_message(self):
        """Zeigt eine Nachricht wenn die Datenbank leer ist"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        if self.search_entry:
            self.search_entry.configure(state="disabled")
        
        empty_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        empty_frame.pack(expand=True, pady=50)
        
        ctk.CTkLabel(
            empty_frame,
            text="📭",
            font=ctk.CTkFont(size=72)
        ).pack(pady=20)
        
        ctk.CTkLabel(
            empty_frame,
            text="Keine Hörbücher gefunden",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            empty_frame,
            text="Die Datenbank ist noch leer.\nFüge dein erstes Hörbuch hinzu!",
            font=ctk.CTkFont(size=16),
            justify="center"
        ).pack(pady=10)
        
        add_button = ctk.CTkButton(
            empty_frame,
            text="➕ Neues Hörbuch hinzufügen",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=300,
            command=self.navigate_to_add_page
        )
        add_button.pack(pady=30)
        
        self.status_label.configure(
            text="📭 Datenbank ist leer - füge Hörbücher hinzu",
            text_color="orange"
        )
        self.count_label.configure(text="0 Hörbücher")
        self.status_info_label.configure(text="Keine Daten vorhanden")
    
    def show_no_results_message(self):
        """Zeigt eine Nachricht wenn die Suche keine Ergebnisse liefert"""
        empty_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        empty_frame.pack(expand=True, pady=50)
        
        ctk.CTkLabel(
            empty_frame,
            text="🔍",
            font=ctk.CTkFont(size=48)
        ).pack(pady=20)
        
        ctk.CTkLabel(
            empty_frame,
            text="Keine Hörbücher gefunden",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            empty_frame,
            text="Passe deine Suchkriterien an",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        ).pack()
    
    def show_error_message(self, title: str, message: str):
        """Zeigt eine Fehlermeldung an"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        if self.search_entry:
            self.search_entry.configure(state="disabled")
        
        error_frame = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        error_frame.pack(expand=True, pady=50)
        
        ctk.CTkLabel(
            error_frame,
            text="❌",
            font=ctk.CTkFont(size=72)
        ).pack(pady=20)
        
        ctk.CTkLabel(
            error_frame,
            text=title,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="red"
        ).pack(pady=10)
        
        msg_label = ctk.CTkLabel(
            error_frame,
            text=message,
            font=ctk.CTkFont(size=14),
            wraplength=600,
            justify="left"
        )
        msg_label.pack(pady=10, padx=20)
        
        button_frame = ctk.CTkFrame(error_frame, fg_color="transparent")
        button_frame.pack(pady=30)
        
        retry_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Erneut versuchen",
            font=ctk.CTkFont(size=14),
            width=200,
            height=40,
            command=self.load_audiobooks
        )
        retry_btn.pack(side="left", padx=10)
        
        home_btn = ctk.CTkButton(
            button_frame,
            text="🏠 Zur Startseite",
            font=ctk.CTkFont(size=14),
            width=150,
            height=40,
            fg_color="transparent",
            border_width=2,
            command=self.navigate_to_home
        )
        home_btn.pack(side="left", padx=10)
        
        self.status_label.configure(text=f"❌ {title}", text_color="red")
        self.count_label.configure(text="Fehler")
        self.status_info_label.configure(text="")
    
    # ================ EVENT HANDLER ================
    
    def on_search_changed(self, event=None):
        """Wird aufgerufen wenn sich der Suchtext ändert"""
        self.apply_filters()
    
    def apply_filters(self):
        """Wendet Suchkriterien an (nur noch Suche, ohne Genre-Filter)"""
        if not self.search_entry:
            return
        
        search_text = self.search_entry.get().lower().strip()
        
        self.filtered_audiobooks = []
        
        for audiobook in self.audiobooks:
            matches_search = True
            if search_text:
                matches_search = (
                    search_text in (audiobook.title or "").lower() or
                    search_text in (audiobook.author or "").lower() or
                    search_text in (audiobook.genre or "").lower() or
                    search_text in (audiobook.subgenre or "").lower() or
                    (audiobook.universe and search_text in audiobook.universe.lower())
                )
            
            if matches_search:
                self.filtered_audiobooks.append(audiobook)
        
        self.display_audiobooks()
    
    def refresh_data(self):
        """Lädt die Daten neu"""
        self.status_label.configure(text="🔄 Aktualisiere...", text_color="blue")
        self.count_label.configure(text="Aktualisiere...")
        self.show_loading_animation()
        self.after(300, self.load_audiobooks)
    
    # ================ NAVIGATION ================
    
    def on_view_details(self, audiobook):
        """
        Öffnet die Detail-Ansicht für ein Hörbuch
        
        Args:
            audiobook: Das anzuzeigende Hörbuch
        """
        print(f"📖 Details anzeigen: {audiobook.title} (ID: {audiobook.id}, Display: {audiobook.display_id})")
        
        # Prüfe ob audiobook und ID existieren
        if not audiobook or not audiobook.id:
            print("❌ Ungültiges Hörbuch-Objekt oder keine ID")
            return
        
        # Speichere die ID für Event-Fallback
        self.last_clicked_audiobook_id = audiobook.id
        
        # Event mit Hörbuch-ID an MainWindow senden
        try:
            self.master.event_generate(
                "<<ShowAudiobookDetail>>", 
                data=str(audiobook.id)
            )
            print(f"✅ Event <<ShowAudiobookDetail>> mit ID {audiobook.id} gesendet")
        except Exception as e:
            print(f"❌ Fehler beim Senden des Events: {e}")
    
    def on_edit_audiobook(self, audiobook):
        """
        Leitet zur Bearbeitungs-Seite für ein Hörbuch weiter
        
        Args:
            audiobook: Das zu bearbeitende Hörbuch
        """
        print(f"✏️ Bearbeite Hörbuch: {audiobook.title} (ID: {audiobook.id}, Display: {audiobook.display_id})")
        
        # Prüfe ob audiobook und ID existieren
        if not audiobook or not audiobook.id:
            print("❌ Ungültiges Hörbuch-Objekt oder keine ID")
            return
        
        # Speichere die ID für Event-Fallback
        self.last_clicked_audiobook_id = audiobook.id
        
        # Event mit Hörbuch-ID senden
        try:
            self.master.event_generate(
                "<<EditAudiobook>>", 
                data=str(audiobook.id)
            )
            print(f"✅ Event <<EditAudiobook>> mit ID {audiobook.id} gesendet")
        except Exception as e:
            print(f"❌ Fehler beim Senden des Events: {e}")
    
    def get_selected_audiobook_id(self):
        """
        Gibt die ID des aktuell ausgewählten Hörbuchs zurück.
        Diese Methode wird vom MainWindow aufgerufen wenn das Event nicht die ID enthält.
        """
        print(f"📋 get_selected_audiobook_id() aufgerufen, letzte ID: {self.last_clicked_audiobook_id}")
        return self.last_clicked_audiobook_id
    
    def navigate_to_add_page(self):
        """Navigiert zur Seite zum Hinzufügen neuer Hörbücher"""
        print("➕ Navigiere zu 'Hörbuch hinzufügen'")
        self.master.event_generate("<<AddAudiobook>>")
    
    def navigate_to_home(self):
        """Navigiert zurück zur Startseite"""
        print("🏠 Navigiere zur Startseite")
        self.master.event_generate("<<NavigateToHome>>")
    
    # ================ HILFSFUNKTIONEN ================
    
    def destroy(self):
        """Räumt Ressourcen frei beim Zerstören der Page"""
        # Geplante Popups abbrechen
        self.cancel_universe_popup()
        
        try:
            if self.search_entry:
                self.search_entry.unbind("<KeyRelease>")
        except:
            pass
        
        super().destroy()