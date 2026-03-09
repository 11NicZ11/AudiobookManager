"""
Seite zum Hinzufügen/Bearbeiten von Hörbüchern
"""
import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional, List
import tkinter as tk

from gui.pages.base_page import BasePage
from database.models.audiobook import Audiobook
from file_management.file_manager import FileManager


class AutocompleteCombobox(ctk.CTkComboBox):
    """
    Combobox mit Autocomplete-Funktionalität
    Schlägt existierende Einträge während der Eingabe vor
    """
    
    def __init__(self, master, get_suggestions_func, **kwargs):
        """
        Args:
            master: Parent-Widget
            get_suggestions_func: Funktion die basierend auf Eingabe Vorschläge liefert
            **kwargs: Weitere Argumente für CTkComboBox
        """
        super().__init__(master, **kwargs)
        
        self.get_suggestions_func = get_suggestions_func
        self.suggestions_listbox = None
        self.suggestions_frame = None
        self._current_suggestions = []
        self._selection_in_progress = False
        
        # Bindings
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<Down>", self._on_down_key)
        self.bind("<Escape>", self._hide_suggestions)
        
        # Variable trace für Wertänderungen
        if isinstance(self.cget("variable"), ctk.StringVar):
            self._textvariable = self.cget("variable")
        else:
            self._textvariable = tk.StringVar()
            self.configure(variable=self._textvariable)
    
    def _on_key_release(self, event):
        """Wird bei Tastendruck im Eingabefeld ausgelöst"""
        if event.keysym in ("Up", "Down", "Left", "Right", "Return", "Escape", "Tab"):
            return
        
        self.after(150, self._update_suggestions)
    
    def _update_suggestions(self):
        """Aktualisiert die Vorschlagsliste"""
        if self._selection_in_progress:
            return
        
        current_text = self.get().strip()
        
        if len(current_text) < 2:
            self._hide_suggestions()
            return
        
        suggestions = self.get_suggestions_func(current_text)
        
        if not suggestions or (len(suggestions) == 1 and suggestions[0] == current_text):
            self._hide_suggestions()
            return
        
        self._current_suggestions = suggestions
        self._show_suggestions()
    
    def _show_suggestions(self):
        """Zeigt die Vorschlagsliste unterhalb des Eingabefelds an"""
        self._hide_suggestions()
        
        self.suggestions_frame = ctk.CTkFrame(
            self.master,
            fg_color=("gray95", "gray25"),
            border_width=1,
            border_color=("gray70", "gray30"),
            corner_radius=5
        )
        
        x = self.winfo_rootx() - self.master.winfo_rootx()
        y = self.winfo_rooty() - self.master.winfo_rooty() + self.winfo_height()
        
        self.suggestions_frame.place(x=x, y=y, width=self.winfo_width())
        
        self.suggestions_listbox = tk.Listbox(
            self.suggestions_frame,
            bg=("#f0f0f0", "#2b2b2b"),
            fg=("#000000", "#ffffff"),
            selectbackground=("#3a7ebf", "#1f538d"),
            selectforeground="white",
            font=("Segoe UI", 12),
            height=min(6, len(self._current_suggestions)),
            borderwidth=0,
            highlightthickness=0,
            activestyle="none"
        )
        self.suggestions_listbox.pack(fill="both", expand=True, padx=2, pady=2)
        
        for suggestion in self._current_suggestions:
            self.suggestions_listbox.insert("end", suggestion)
        
        self.suggestions_listbox.bind("<ButtonRelease-1>", self._on_suggestion_click)
        self.suggestions_listbox.bind("<Return>", self._on_suggestion_select)
        self.suggestions_listbox.bind("<Double-Button-1>", self._on_suggestion_select)
        self.suggestions_listbox.bind("<Escape>", lambda e: self._hide_suggestions())
        
        self.suggestions_listbox.focus_set()
        self.suggestions_listbox.selection_set(0)
    
    def _hide_suggestions(self, event=None):
        """Versteckt die Vorschlagsliste"""
        if self.suggestions_frame:
            self.suggestions_frame.destroy()
            self.suggestions_frame = None
            self.suggestions_listbox = None
            self._current_suggestions = []
    
    def _on_suggestion_click(self, event):
        """Wird beim Klick auf einen Vorschlag ausgelöst"""
        if self.suggestions_listbox:
            selection = self.suggestions_listbox.curselection()
            if selection:
                self._select_suggestion(self.suggestions_listbox.get(selection[0]))
    
    def _on_suggestion_select(self, event):
        """Wird bei Auswahl eines Vorschlags ausgelöst"""
        if self.suggestions_listbox:
            selection = self.suggestions_listbox.curselection()
            if selection:
                self._select_suggestion(self.suggestions_listbox.get(selection[0]))
    
    def _on_down_key(self, event):
        """Wird bei Pfeil-nach-unten ausgelöst"""
        if not self.suggestions_frame:
            self._open_dropdown()
        return "break"
    
    def _select_suggestion(self, value):
        """Wählt einen Vorschlag aus"""
        self._selection_in_progress = True
        self._textvariable.set(value)
        self.icursor("end")
        self._hide_suggestions()
        self.event_generate("<<ComboboxSelected>>")
        self._selection_in_progress = False
        self.focus_set()
    
    def _on_focus_out(self, event):
        """Wird wenn Fokus verloren geht"""
        self.after(200, self._hide_suggestions)
    
    def set_suggestions(self, suggestions: List[str]):
        """Setzt die Vorschläge direkt"""
        self._current_suggestions = suggestions


class AudiobookSearchCombobox(AutocompleteCombobox):
    """
    Spezialisierte Combobox für die Hörbuchsuche
    Zeigt Titel, Autor und ID in den Vorschlägen an
    """
    
    def __init__(self, master, db_manager, on_select_callback, **kwargs):
        """
        Args:
            master: Parent-Widget
            db_manager: DatabaseManager Instanz
            on_select_callback: Callback wenn ein Hörbuch ausgewählt wird
            **kwargs: Weitere Argumente
        """
        self.db_manager = db_manager
        self.on_select_callback = on_select_callback
        self.exclude_ids = kwargs.pop('exclude_ids', [])
        
        super().__init__(master, self._search_audiobooks, **kwargs)
        
        # Eigene Darstellung für Hörbuch-Vorschläge
        self.suggestion_objects = []
    
    def _search_audiobooks(self, search_text: str) -> List[str]:
        """
        Sucht nach Hörbüchern und formatiert sie für die Anzeige
        
        Args:
            search_text: Suchtext (Titel, Autor oder ID)
        
        Returns:
            Liste von formatierten Strings "AUD000001 - Titel (Autor)"
        """
        if not search_text or len(search_text) < 2:
            return []
        
        try:
            # Suche in der Datenbank
            audiobooks = self.db_manager.search_audiobooks(search_text)
            
            # Aktuelles Hörbuch und bereits verbundene ausschließen
            filtered_books = []
            for book in audiobooks:
                if book.id not in self.exclude_ids:
                    # Formatiere für Anzeige
                    display_text = f"{book.display_id} - {book.title[:40]}"
                    if book.author:
                        display_text += f" ({book.author})"
                    filtered_books.append((display_text, book))
            
            # Nur die ersten 10 anzeigen
            self.suggestion_objects = filtered_books[:10]
            return [text for text, _ in self.suggestion_objects]
            
        except Exception as e:
            print(f"⚠️ Fehler bei Hörbuchsuche: {e}")
            return []
    
    def _select_suggestion(self, value):
        """Überschrieben: Übergibt das ausgewählte Hörbuch an den Callback"""
        self._selection_in_progress = True
        
        # Finde das passende Hörbuch-Objekt
        selected_book = None
        for display_text, book in self.suggestion_objects:
            if display_text == value:
                selected_book = book
                break
        
        if selected_book:
            self.on_select_callback(selected_book)
        
        # Feld leeren für nächste Eingabe
        self._textvariable.set("")
        self._hide_suggestions()
        
        self._selection_in_progress = False
        self.focus_set()
    
    def set_exclude_ids(self, exclude_ids: List[int]):
        """Setzt die auszuschließenden Hörbuch-IDs"""
        self.exclude_ids = exclude_ids


class ConnectionChip(ctk.CTkFrame):
    """
    Visueller Chip für ein verbundenes Hörbuch
    Zeigt ID, Titel und Autor an
    """
    
    def __init__(self, master, audiobook: Audiobook, on_remove_callback, **kwargs):
        """
        Args:
            master: Parent-Widget
            audiobook: Das verbundene Hörbuch
            on_remove_callback: Callback zum Entfernen
            **kwargs: Weitere Argumente für CTkFrame
        """
        super().__init__(
            master,
            fg_color=("gray80", "gray30"),
            corner_radius=15,
            **kwargs
        )
        
        self.audiobook = audiobook
        self.on_remove_callback = on_remove_callback
        
        # Grid-Layout für bessere Kontrolle
        self.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(
            self,
            text="🔗",
            font=ctk.CTkFont(size=12),
            width=20
        )
        icon_label.grid(row=0, column=0, padx=(10, 5), pady=8)
        
        # Informationstext
        info_text = f"{audiobook.display_id} - {audiobook.title[:30]}"
        if len(audiobook.title) > 30:
            info_text += "..."
        if audiobook.author:
            info_text += f" ({audiobook.author[:20]})"
            if len(audiobook.author) > 20:
                info_text += "..."
        
        info_label = ctk.CTkLabel(
            self,
            text=info_text,
            font=ctk.CTkFont(size=12, weight="bold" if audiobook.universe else "normal"),
            anchor="w"
        )
        info_label.grid(row=0, column=1, padx=5, pady=8, sticky="w")
        
        # Universum-Indikator (falls vorhanden)
        if audiobook.universe:
            universe_label = ctk.CTkLabel(
                self,
                text="🌌",
                font=ctk.CTkFont(size=12),
                width=20
            )
            universe_label.grid(row=0, column=2, padx=5, pady=8)
        
        # Entfernen-Button
        remove_btn = ctk.CTkButton(
            self,
            text="✕",
            width=25,
            height=25,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            hover_color=("gray70", "gray20"),
            command=self.on_remove
        )
        remove_btn.grid(row=0, column=3, padx=(5, 10), pady=5)
    
    def on_remove(self):
        """Wird beim Klick auf Entfernen-Button aufgerufen"""
        if self.on_remove_callback:
            self.on_remove_callback(self.audiobook)


class AddAudiobookPage(BasePage):
    """Formular zum Hinzufügen und Bearbeiten von Hörbüchern"""
    
    def __init__(self, master, db_manager, file_manager=None, audiobook: Optional[Audiobook] = None):
        """
        Args:
            master: Parent-Widget
            db_manager: DatabaseManager Instanz
            file_manager: FileManager Instanz (optional)
            audiobook: Zu bearbeitendes Hörbuch (None = neues Hörbuch)
        """
        super().__init__(master)
        
        self.db_manager = db_manager
        self.file_manager = file_manager if file_manager is not None else FileManager()
        self.audiobook = audiobook
        self.is_edit_mode = audiobook is not None
        
        # Pfade für hochgeladene Dateien
        self.selected_image_path = None
        self.selected_audio_path = None
        self.narrator_entries = []
        
        # Verbundene Hörbücher (als Objekte, nicht nur IDs)
        self.connected_audiobooks = []
        
        # Cache für existierende Universen
        self.existing_universes = []
        self.load_existing_universes()
        
        # UI erstellen
        self.setup_widgets()
        
        # Wenn im Bearbeitungsmodus, Formular befüllen
        if self.is_edit_mode:
            self.load_audiobook_data()
    
    def load_existing_universes(self):
        """Lädt alle existierenden Universen aus der Datenbank"""
        try:
            if self.db_manager:
                all_books = self.db_manager.get_all_audiobooks()
                universes = set()
                for book in all_books:
                    if book.universe and book.universe.strip():
                        universes.add(book.universe.strip())
                self.existing_universes = sorted(list(universes))
                print(f"✅ {len(self.existing_universes)} existierende Universen geladen")
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Universen: {e}")
            self.existing_universes = []
    
    def get_universe_suggestions(self, current_input: str) -> List[str]:
        """
        Gibt Universum-Vorschläge basierend auf Benutzereingabe zurück
        
        Args:
            current_input: Aktuelle Eingabe im Universum-Feld
        
        Returns:
            Liste der passenden Universums-Namen
        """
        if not current_input or len(current_input) < 2:
            return []
        
        current_input = current_input.lower()
        suggestions = []
        
        for universe in self.existing_universes:
            if current_input in universe.lower():
                suggestions.append(universe)
        
        return suggestions[:10]
    
    def setup_widgets(self):
        """Erstellt alle Widgets des Formulars"""
        content = self.get_content_area()
        
        # === Header ===
        header_frame = ctk.CTkFrame(content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_text = "✏️ Hörbuch bearbeiten" if self.is_edit_mode else "➕ Neues Hörbuch"
        title_label = ctk.CTkLabel(
            header_frame,
            text=title_text,
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(side="left")
        
        # ID-Anzeige (nur im Bearbeitungsmodus)
        if self.is_edit_mode and self.audiobook:
            id_label = ctk.CTkLabel(
                header_frame,
                text=self.audiobook.display_id,
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            id_label.pack(side="right", padx=10)
        
        # === Hauptformular in zwei Spalten ===
        form_frame = ctk.CTkFrame(content)
        form_frame.pack(fill="both", expand=True)
        
        # Grid-Konfiguration
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_rowconfigure(0, weight=1)
        
        # === LINKE SPALTE: Stammdaten ===
        left_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        self.create_basic_info_section(left_frame)
        self.create_genre_section(left_frame)
        
        # === RECHTE SPALTE: Medien & Zusatzinfos ===
        right_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        self.create_media_section(right_frame)
        self.create_universe_section(right_frame)
        self.create_connections_section(right_frame)
        self.create_description_section(right_frame)
        
        # === BUTTONS (unten) ===
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Abbrechen-Button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            hover_color=("gray80", "gray20"),
            command=self.cancel
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        # Speichern-Button
        save_text = "Aktualisieren" if self.is_edit_mode else "Speichern"
        save_btn = ctk.CTkButton(
            button_frame,
            text=save_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=150,
            command=self.save_audiobook
        )
        save_btn.pack(side="right")
    
    def create_basic_info_section(self, parent):
        """Erstellt Bereich für Basis-Informationen"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 20))
        
        # Titel
        ctk.CTkLabel(
            section,
            text="📖 Titel *",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(15, 5))
        
        self.title_entry = ctk.CTkEntry(
            section,
            height=40
        )
        self.title_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Autor
        ctk.CTkLabel(
            section,
            text="✍️ Autor",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(0, 5))
        
        self.author_entry = ctk.CTkEntry(
            section,
            height=40
        )
        self.author_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Sprecher
        narrator_header = ctk.CTkFrame(section, fg_color="transparent")
        narrator_header.pack(fill="x", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(
            narrator_header,
            text="🎤 Sprecher",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            narrator_header,
            text="+ Hinzufügen",
            width=100,
            height=25,
            font=ctk.CTkFont(size=11),
            command=self.add_narrator_field
        ).pack(side="right")
        
        # Container für Sprecher-Felder
        self.narrators_container = ctk.CTkFrame(section, fg_color="transparent")
        self.narrators_container.pack(fill="x", padx=10, pady=(0, 10))
        
        # Erstes Sprecher-Feld
        self.add_narrator_field()
        
        # Jahr
        ctk.CTkLabel(
            section,
            text="📅 Erscheinungsjahr",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.year_entry = ctk.CTkEntry(
            section,
            width=100,
            height=40
        )
        self.year_entry.pack(anchor="w", padx=10, pady=(0, 15))
    
    def add_narrator_field(self, initial_value: str = ""):
        """Fügt ein neues Eingabefeld für einen Sprecher hinzu"""
        entry_frame = ctk.CTkFrame(self.narrators_container, fg_color="transparent")
        entry_frame.pack(fill="x", pady=(0, 5))
        
        entry = ctk.CTkEntry(
            entry_frame,
            height=35
        )
        entry.pack(side="left", fill="x", expand=True)
        
        if initial_value:
            entry.insert(0, initial_value)
        
        # Löschen-Button (außer beim ersten Feld)
        if len(self.narrator_entries) > 0:
            delete_btn = ctk.CTkButton(
                entry_frame,
                text="✕",
                width=30,
                height=35,
                fg_color="transparent",
                hover_color=("gray80", "gray20"),
                command=lambda: self.remove_narrator_field(entry_frame, entry)
            )
            delete_btn.pack(side="right", padx=(5, 0))
        
        self.narrator_entries.append((entry_frame, entry))
    
    def remove_narrator_field(self, frame, entry):
        """Entfernt ein Sprecher-Feld"""
        for i, (f, e) in enumerate(self.narrator_entries):
            if e == entry:
                self.narrator_entries.pop(i)
                frame.destroy()
                break
    
    def create_genre_section(self, parent):
        """Erstellt Bereich für Genre/Subgenre"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section,
            text="🏷️ Kategorisierung",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(15, 10))
        
        # Genre
        ctk.CTkLabel(
            section,
            text="Genre",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(0, 5))
        
        genre_suggestions = ["Fantasy", "Science-Fiction", "Krimi", "Roman", "Sachbuch", 
                           "Biografie", "Historisch", "Thriller", "Horror", "Philosophie"]
        
        self.genre_var = ctk.StringVar()
        genre_combo = ctk.CTkComboBox(
            section,
            values=genre_suggestions,
            variable=self.genre_var,
            height=40
        )
        genre_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        # Subgenre
        ctk.CTkLabel(
            section,
            text="Subgenre",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(0, 5))
        
        self.subgenre_entry = ctk.CTkEntry(
            section,
            height=40
        )
        self.subgenre_entry.pack(fill="x", padx=10, pady=(0, 15))
    
    def create_media_section(self, parent):
        """Erstellt Bereich für Datei-Uploads"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section,
            text="🖼️ Cover-Bild",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(15, 5))
        
        image_frame = ctk.CTkFrame(section, fg_color="transparent")
        image_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.image_path_label = ctk.CTkLabel(
            image_frame,
            text="Keine Datei ausgewählt",
            text_color="gray",
            anchor="w"
        )
        self.image_path_label.pack(side="left", fill="x", expand=True)
        
        ctk.CTkButton(
            image_frame,
            text="📂 Durchsuchen",
            width=100,
            height=35,
            command=self.browse_image
        ).pack(side="right", padx=(10, 0))
        
        # Audio-Datei
        ctk.CTkLabel(
            section,
            text="🎵 Audio-Datei",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(15, 5))
        
        audio_frame = ctk.CTkFrame(section, fg_color="transparent")
        audio_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        self.audio_path_label = ctk.CTkLabel(
            audio_frame,
            text="Keine Datei ausgewählt",
            text_color="gray",
            anchor="w"
        )
        self.audio_path_label.pack(side="left", fill="x", expand=True)
        
        ctk.CTkButton(
            audio_frame,
            text="📂 Durchsuchen",
            width=100,
            height=35,
            command=self.browse_audio
        ).pack(side="right", padx=(10, 0))
    
    def create_universe_section(self, parent):
        """Erstellt Bereich für Universum-Zuordnung mit Autocomplete"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section,
            text="🌌 Universum",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(15, 10))
        
        # Universum-Name mit Autocomplete
        ctk.CTkLabel(
            section,
            text="Name des Universums",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(0, 5))
        
        self.universe_entry = AutocompleteCombobox(
            section,
            get_suggestions_func=self.get_universe_suggestions,
            height=40
        )
        self.universe_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Button zum Aktualisieren der Universums-Liste
        refresh_frame = ctk.CTkFrame(section, fg_color="transparent")
        refresh_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        refresh_btn = ctk.CTkButton(
            refresh_frame,
            text="🔄 Universums-Liste aktualisieren",
            font=ctk.CTkFont(size=11),
            width=180,
            height=25,
            fg_color="transparent",
            border_width=1,
            border_color=("gray70", "gray30"),
            command=self.refresh_universes
        )
        refresh_btn.pack(side="left")
        
        if self.existing_universes:
            count_label = ctk.CTkLabel(
                refresh_frame,
                text=f"{len(self.existing_universes)} Universen vorhanden",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            count_label.pack(side="left", padx=(10, 0))
    
    def refresh_universes(self):
        """Aktualisiert die Liste der existierenden Universen"""
        self.load_existing_universes()
        
        if hasattr(self, 'universe_entry'):
            current_text = self.universe_entry.get()
            self.universe_entry.set_suggestions(self.get_universe_suggestions(current_text))
        
        messagebox.showinfo(
            "Universen aktualisiert",
            f"{len(self.existing_universes)} Universen wurden geladen."
        )
    
    def create_connections_section(self, parent):
        """Erstellt Bereich für Hörbuch-Verbindungen mit Autocomplete und Chips"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section,
            text="🔗 Verbindungen",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=(15, 10))
        
        # Beschreibung
        ctk.CTkLabel(
            section,
            text="Verbindungen werden automatisch in beide Richtungen gespeichert.",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(anchor="w", padx=10, pady=(0, 10))
        
        # Container für ausgewählte Verbindungen (Chips)
        self.connections_container = ctk.CTkFrame(section, fg_color="transparent")
        self.connections_container.pack(fill="x", padx=10, pady=(0, 10))
        
        # Suchfeld für neue Verbindungen
        search_frame = ctk.CTkFrame(section, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(
            search_frame,
            text="➕ Hörbuch hinzufügen:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        # Autocomplete für Hörbuchsuche
        self.connection_search = AudiobookSearchCombobox(
            section,
            db_manager=self.db_manager,
            on_select_callback=self.add_connection,
            height=40,
            exclude_ids=self._get_excluded_connection_ids()
        )
        self.connection_search.pack(fill="x", padx=10, pady=(5, 0))
        
        # Hinweis
        ctk.CTkLabel(
            section,
            text="💡 Tipp: Du kannst nach Titel, Autor oder ID suchen",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(anchor="w", padx=10, pady=(5, 10))
    
    def _get_excluded_connection_ids(self) -> List[int]:
        """
        Gibt Liste der IDs zurück, die von der Suche ausgeschlossen werden sollen:
        - Das aktuell bearbeitete Hörbuch
        - Bereits verbundene Hörbücher
        """
        exclude_ids = []
        
        # Aktuelles Hörbuch ausschließen
        if self.audiobook and self.audiobook.id:
            exclude_ids.append(self.audiobook.id)
        
        # Bereits verbundene Hörbücher ausschließen
        for book in self.connected_audiobooks:
            if book.id not in exclude_ids:
                exclude_ids.append(book.id)
        
        return exclude_ids
    
    def add_connection(self, audiobook: Audiobook):
        """
        Fügt ein Hörbuch zu den Verbindungen hinzu
        
        Args:
            audiobook: Das zu verbindende Hörbuch
        """
        # Prüfe ob bereits verbunden
        for book in self.connected_audiobooks:
            if book.id == audiobook.id:
                messagebox.showinfo(
                    "Bereits verbunden",
                    f"'{audiobook.title}' ist bereits mit diesem Hörbuch verbunden."
                )
                return
        
        # Hörbuch zu Verbindungen hinzufügen
        self.connected_audiobooks.append(audiobook)
        
        # Chip anzeigen
        chip = ConnectionChip(
            self.connections_container,
            audiobook=audiobook,
            on_remove_callback=self.remove_connection
        )
        chip.pack(pady=2, fill="x")
        
        # Suche zurücksetzen und Ausschlussliste aktualisieren
        self.connection_search.set_exclude_ids(self._get_excluded_connection_ids())
        
        print(f"✅ Verbindung hinzugefügt: {audiobook.display_id} - {audiobook.title}")
    
    def remove_connection(self, audiobook: Audiobook):
        """
        Entfernt ein Hörbuch aus den Verbindungen
        
        Args:
            audiobook: Das zu entfernende Hörbuch
        """
        # Aus Liste entfernen
        self.connected_audiobooks = [
            book for book in self.connected_audiobooks 
            if book.id != audiobook.id
        ]
        
        # Alle Chips neu erstellen
        self.refresh_connection_chips()
        
        # Ausschlussliste aktualisieren
        self.connection_search.set_exclude_ids(self._get_excluded_connection_ids())
        
        print(f"✅ Verbindung entfernt: {audiobook.display_id} - {audiobook.title}")
    
    def refresh_connection_chips(self):
        """Erstellt alle Verbindungs-Chips neu"""
        # Container leeren
        for widget in self.connections_container.winfo_children():
            widget.destroy()
        
        # Chips neu erstellen
        for book in self.connected_audiobooks:
            chip = ConnectionChip(
                self.connections_container,
                audiobook=book,
                on_remove_callback=self.remove_connection
            )
            chip.pack(pady=2, fill="x")
    
    def create_description_section(self, parent):
        """Erstellt Bereich für Beschreibung"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            section,
            text="📝 Beschreibung",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(15, 5))
        
        self.description_text = ctk.CTkTextbox(
            section,
            height=150,
            font=ctk.CTkFont(size=12)
        )
        self.description_text.pack(fill="both", expand=True, padx=10, pady=(0, 15))
    
    def browse_image(self):
        """Öffnet Dateiauswahl für Bild-Datei"""
        filename = filedialog.askopenfilename(
            title="Cover-Bild auswählen",
            filetypes=[
                ("Bilddateien", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("Alle Dateien", "*.*")
            ]
        )
        
        if filename:
            self.selected_image_path = Path(filename)
            self.image_path_label.configure(text=filename, text_color=("black", "white"))
    
    def browse_audio(self):
        """Öffnet Dateiauswahl für Audio-Datei"""
        filename = filedialog.askopenfilename(
            title="Audio-Datei auswählen",
            filetypes=[
                ("Audio-Dateien", "*.mp3 *.wav *.flac *.m4a *.aac"),
                ("Alle Dateien", "*.*")
            ]
        )
        
        if filename:
            self.selected_audio_path = Path(filename)
            self.audio_path_label.configure(text=filename, text_color=("black", "white"))
    
    def load_audiobook_data(self):
        """Lädt Daten eines existierenden Hörbuchs ins Formular"""
        if not self.audiobook:
            return
        
        book = self.audiobook
        
        # Stammdaten
        self.title_entry.insert(0, book.title)
        self.author_entry.insert(0, book.author)
        
        # Sprecher
        for frame, entry in self.narrator_entries:
            frame.destroy()
        self.narrator_entries.clear()
        
        for narrator in book.narrators:
            self.add_narrator_field(narrator)
        
        if not book.narrators:
            self.add_narrator_field()
        
        # Jahr
        if book.year:
            self.year_entry.insert(0, str(book.year))
        
        # Genre
        self.genre_var.set(book.genre if book.genre else "")
        self.subgenre_entry.insert(0, book.subgenre if book.subgenre else "")
        
        # Universum
        self.universe_entry._textvariable.set(book.universe if book.universe else "")
        
        # Verbindungen als Objekte laden
        self.connected_audiobooks = []
        for conn_id in book.connections:
            try:
                if isinstance(conn_id, str):
                    book_id = int(conn_id)
                else:
                    book_id = conn_id
                
                connected_book = self.db_manager.get_audiobook(book_id)
                if connected_book and connected_book.id != book.id:
                    self.connected_audiobooks.append(connected_book)
            except (ValueError, TypeError):
                print(f"⚠️ Ungültige Verbindungs-ID: {conn_id}")
        
        # Chips für Verbindungen anzeigen
        self.refresh_connection_chips()
        
        # Beschreibung
        if book.description:
            self.description_text.insert("1.0", book.description)
        
        # Dateipfade
        if book.image_path:
            self.selected_image_path = Path(book.image_path)
            self.image_path_label.configure(text=book.image_path, text_color=("black", "white"))
        
        if book.audio_path:
            self.selected_audio_path = Path(book.audio_path)
            self.audio_path_label.configure(text=book.audio_path, text_color=("black", "white"))
        
        # Ausschlussliste für Suche aktualisieren
        if hasattr(self, 'connection_search'):
            self.connection_search.set_exclude_ids(self._get_excluded_connection_ids())
    
    def save_audiobook(self):
        """Speichert das Hörbuch in der Datenbank mit beidseitigen Verbindungen"""
        try:
            # === Validierung ===
            title = self.title_entry.get().strip()
            if not title:
                messagebox.showerror("Fehler", "Bitte gib einen Titel ein.")
                return
            
            # === Daten sammeln ===
            narrators = []
            for _, entry in self.narrator_entries:
                narrator = entry.get().strip()
                if narrator:
                    narrators.append(narrator)
            
            year = None
            year_text = self.year_entry.get().strip()
            if year_text:
                try:
                    year = int(year_text)
                    if year < 1800 or year > 2100:
                        messagebox.showerror("Fehler", "Bitte gib ein gültiges Jahr ein (1800-2100).")
                        return
                except ValueError:
                    messagebox.showerror("Fehler", "Bitte gib eine gültige Jahreszahl ein.")
                    return
            
            # === Hörbuch-Objekt erstellen/aktualisieren ===
            if self.is_edit_mode:
                audiobook = self.audiobook
            else:
                audiobook = Audiobook()
            
            audiobook.title = title
            audiobook.author = self.author_entry.get().strip()
            audiobook.narrators = narrators
            audiobook.genre = self.genre_var.get().strip()
            audiobook.subgenre = self.subgenre_entry.get().strip()
            audiobook.year = year
            audiobook.universe = self.universe_entry.get().strip()
            audiobook.description = self.description_text.get("1.0", "end-1c").strip()
            
            # === Temporäre ID für Datei-Upload ===
            temp_id = audiobook.id if audiobook.id else 0
            
            # === Dateien speichern ===
            if self.selected_image_path and self.selected_image_path.exists():
                success, message, saved_path = self.file_manager.upload_image(
                    str(self.selected_image_path), 
                    temp_id
                )
                if success:
                    audiobook.image_path = saved_path
                else:
                    print(f"⚠️ Bild-Upload fehlgeschlagen: {message}")
            
            if self.selected_audio_path and self.selected_audio_path.exists():
                success, message, saved_path = self.file_manager.upload_audio(
                    str(self.selected_audio_path),
                    temp_id
                )
                if success:
                    audiobook.audio_path = saved_path
                else:
                    print(f"⚠️ Audio-Upload fehlgeschlagen: {message}")
            
            # === Hörbuch speichern (um eine ID zu bekommen) ===
            if self.is_edit_mode:
                success = self.db_manager.update_audiobook(audiobook)
                if not success:
                    messagebox.showerror("Fehler", "Hörbuch konnte nicht aktualisiert werden.")
                    return
            else:
                audiobook_id = self.db_manager.add_audiobook(audiobook)
                audiobook.id = audiobook_id
                
                # Dateien mit korrekter ID erneut speichern
                if audiobook.image_path and self.selected_image_path:
                    old_path = Path(audiobook.image_path)
                    if old_path.exists():
                        success, message, new_path = self.file_manager.upload_image(
                            str(old_path), audiobook_id
                        )
                        if success:
                            audiobook.image_path = new_path
                            old_path.unlink()
                
                if audiobook.audio_path and self.selected_audio_path:
                    old_path = Path(audiobook.audio_path)
                    if old_path.exists():
                        success, message, new_path = self.file_manager.upload_audio(
                            str(old_path), audiobook_id
                        )
                        if success:
                            audiobook.audio_path = new_path
                            old_path.unlink()
            
            # === Beidseitige Verbindungen speichern ===
            # 1. Alte Verbindungen des aktuellen Hörbuchs entfernen
            old_connections = audiobook.connections.copy() if audiobook.connections else []
            
            # 2. Neue Verbindungen setzen (IDs der verbundenen Hörbücher)
            new_connection_ids = [book.id for book in self.connected_audiobooks]
            audiobook.connections = new_connection_ids
            
            # 3. Aktuelles Hörbuch aktualisieren
            self.db_manager.update_audiobook(audiobook)
            
            # 4. Für jedes verbundene Hörbuch die Gegenrichtung setzen/entfernen
            for connected_book_id in old_connections:
                if connected_book_id not in new_connection_ids:
                    # Verbindung wurde entfernt - auch beim verbundenen Hörbuch entfernen
                    connected_book = self.db_manager.get_audiobook(connected_book_id)
                    if connected_book and audiobook.id in connected_book.connections:
                        connected_book.connections.remove(audiobook.id)
                        self.db_manager.update_audiobook(connected_book)
            
            for connected_book in self.connected_audiobooks:
                # Aktuelles Hörbuch zum verbundenen Hörbuch hinzufügen (falls nicht vorhanden)
                connected_book = self.db_manager.get_audiobook(connected_book.id)
                if connected_book:
                    if audiobook.id not in connected_book.connections:
                        connected_book.connections.append(audiobook.id)
                        self.db_manager.update_audiobook(connected_book)
            
            # === Erfolgsmeldung ===
            if self.is_edit_mode:
                messagebox.showinfo("Erfolg", "Hörbuch wurde aktualisiert!")
            else:
                messagebox.showinfo("Erfolg", f"Hörbuch wurde mit ID {audiobook.display_id} gespeichert!")
            
            self.navigate_back()
        
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def navigate_back(self):
        """Navigation zurück zur Liste"""
        self.master.event_generate("<<NavigateToAudiobookList>>")
    
    def cancel(self):
        """Bricht die Bearbeitung ab"""
        if messagebox.askyesno("Abbrechen", "Möchtest du wirklich abbrechen? Nicht gespeicherte Änderungen gehen verloren."):
            self.navigate_back()