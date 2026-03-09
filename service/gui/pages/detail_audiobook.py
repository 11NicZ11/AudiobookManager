"""
Detail-Ansicht für ein einzelnes Hörbuch
"""
import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox
from typing import Optional, List
from PIL import Image
import os
import shutil
import subprocess
import platform
from tkinter import filedialog

from gui.pages.base_page import BasePage
from gui.widgets.hover_popup import UniverseBooksPopup
from database.models.audiobook import Audiobook
from database.models.universe import Universe


class DetailAudiobookPage(BasePage):
    """Detailansicht eines Hörbuchs mit allen Informationen"""
    
    def __init__(self, master, db_manager, audiobook: Audiobook, file_manager=None):
        """
        Args:
            master: Parent-Widget
            db_manager: DatabaseManager Instanz
            audiobook: Das anzuzeigende Hörbuch
            file_manager: FileManager Instanz (optional)
        """
        super().__init__(master)
        
        self.db_manager = db_manager
        self.audiobook = audiobook
        self.file_manager = file_manager
        
        # Cover-Bild
        self.cover_image = None
        self.cover_ctk_image = None
        
        # Verbundene Hörbücher
        self.connected_books = []
        
        # Hover-Popup für Universum
        self.universe_popup = UniverseBooksPopup(self.master, self.db_manager)
        self.popup_timer = None
        
        # UI erstellen
        self.setup_widgets()
        
        # Verbundene Hörbücher laden
        self.load_connected_books()
    
    def setup_widgets(self):
        """Erstellt alle Widgets der Detail-Ansicht"""
        content = self.get_content_area()
        
        # === Header mit Navigation ===
        self.create_header(content)
        
        # === Hauptbereich mit zwei Spalten ===
        main_frame = ctk.CTkFrame(content, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        
        # Grid-Konfiguration
        main_frame.grid_columnconfigure(0, weight=1)  # Linke Spalte (Cover)
        main_frame.grid_columnconfigure(1, weight=2)  # Rechte Spalte (Info)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # === LINKE SPALTE: Cover ===
        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=(0, 20), sticky="nsew")
        
        self.create_cover_section(left_frame)
        
        # === RECHTE SPALTE: Informationen ===
        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Scrollbarer Bereich für die rechte Spalte
        scroll_frame = ctk.CTkScrollableFrame(right_frame, height=600)
        scroll_frame.pack(fill="both", expand=True)
        
        self.create_info_sections(scroll_frame)
    
    def create_header(self, parent):
        """Erstellt den Kopfbereich mit Navigation"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Zurück-Button
        back_btn = ctk.CTkButton(
            header_frame,
            text="← Zurück zur Liste",
            font=ctk.CTkFont(size=14),
            width=150,
            height=35,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            hover_color=("gray80", "gray20"),
            command=self.navigate_back
        )
        back_btn.pack(side="left")
        
        # ID-Anzeige
        id_label = ctk.CTkLabel(
            header_frame,
            text=self.audiobook.display_id,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray"
        )
        id_label.pack(side="right", padx=10)
        
        # Bearbeiten-Button
        edit_btn = ctk.CTkButton(
            header_frame,
            text="✏️ Bearbeiten",
            font=ctk.CTkFont(size=14),
            width=120,
            height=35,
            command=self.on_edit_clicked
        )
        edit_btn.pack(side="right", padx=10)
        
        # Löschen-Button
        delete_btn = ctk.CTkButton(
            header_frame,
            text="🗑️ Löschen",
            font=ctk.CTkFont(size=14),
            width=120,
            height=35,
            fg_color="transparent",
            border_width=2,
            border_color="red",
            hover_color=("red", "darkred"),
            text_color="red",
            command=self.on_delete_clicked
        )
        delete_btn.pack(side="right", padx=10)
    
    # ================ COVER-BEREICH MIT DOWNLOAD ================
    
    def create_cover_section(self, parent):
        """Erstellt den Bereich für das Cover-Bild mit Download"""
        cover_frame = ctk.CTkFrame(parent)
        cover_frame.pack(fill="x", pady=(0, 20))
        
        # Header mit Titel und Download-Button
        header_frame = ctk.CTkFrame(cover_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="📷 Cover",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        # Download Button für Cover
        if self.audiobook.image_path and Path(self.audiobook.image_path).exists():
            download_btn = ctk.CTkButton(
                header_frame,
                text="⬇️ Herunterladen",
                font=ctk.CTkFont(size=12),
                width=120,
                height=30,
                fg_color="transparent",
                border_width=1,
                border_color=("gray70", "gray30"),
                hover_color=("gray80", "gray20"),
                command=self.download_cover
            )
            download_btn.pack(side="right")
        
        # Cover-Container
        image_container = ctk.CTkFrame(cover_frame, fg_color=("gray90", "gray25"))
        image_container.pack(padx=15, pady=(0, 15))
        
        # Cover-Bild laden und anzeigen
        self.load_cover_image(image_container)
        
        # Bild-Pfad (falls vorhanden)
        if self.audiobook.image_path:
            path_frame = ctk.CTkFrame(cover_frame, fg_color="transparent")
            path_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            path_label = ctk.CTkLabel(
                path_frame,
                text=f"📂 {Path(self.audiobook.image_path).name}",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            path_label.pack(side="left")
            
            # Pfad kopieren Button
            copy_btn = ctk.CTkButton(
                path_frame,
                text="📋 Pfad kopieren",
                font=ctk.CTkFont(size=10),
                width=100,
                height=25,
                fg_color="transparent",
                border_width=1,
                border_color=("gray70", "gray30"),
                hover_color=("gray80", "gray20"),
                command=self.copy_cover_path
            )
            copy_btn.pack(side="right")
    
    def load_cover_image(self, container):
        """Lädt und zeigt das Cover-Bild an"""
        try:
            if self.audiobook.image_path and Path(self.audiobook.image_path).exists():
                # Bild öffnen
                img_path = Path(self.audiobook.image_path)
                self.cover_image = Image.open(img_path)
                
                # Bild skalieren (max 300x300)
                self.cover_image.thumbnail((300, 300))
                
                # Zu CTkImage konvertieren
                self.cover_ctk_image = ctk.CTkImage(
                    light_image=self.cover_image,
                    dark_image=self.cover_image,
                    size=self.cover_image.size
                )
                
                # Bild anzeigen
                image_label = ctk.CTkLabel(
                    container,
                    image=self.cover_ctk_image,
                    text=""
                )
                image_label.pack(padx=20, pady=20)
                
            else:
                # Platzhalter wenn kein Bild vorhanden
                placeholder = ctk.CTkLabel(
                    container,
                    text="🖼️\nKein Cover",
                    font=ctk.CTkFont(size=24),
                    width=200,
                    height=200,
                    fg_color=("gray80", "gray30"),
                    corner_radius=10
                )
                placeholder.pack(padx=20, pady=20)
                
        except Exception as e:
            print(f"⚠️ Fehler beim Laden des Covers: {e}")
            # Fehler-Platzhalter
            error_label = ctk.CTkLabel(
                container,
                text="❌\nCover fehlerhaft",
                font=ctk.CTkFont(size=20),
                width=200,
                height=200,
                fg_color=("gray80", "gray30"),
                corner_radius=10
            )
            error_label.pack(padx=20, pady=20)
    
    def create_info_sections(self, parent):
        """Erstellt alle Informationsbereiche"""
        
        # === Basis-Informationen ===
        self.create_basic_info(parent)
        
        # === Kategorisierung ===
        self.create_category_info(parent)
        
        # === Universum & Verbindungen ===
        self.create_universe_info(parent)
        
        # === Datei-Informationen ===
        self.create_file_info(parent)  # Audio mit Download!
        
        # === Beschreibung ===
        self.create_description_info(parent)
        
        # === Verbundene Hörbücher ===
        self.create_connections_info(parent)
    
    def create_basic_info(self, parent):
        """Erstellt Bereich für Basis-Informationen"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 20))
        
        # Titel
        ctk.CTkLabel(
            section,
            text="📖 Titel",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        title_label = ctk.CTkLabel(
            section,
            text=self.audiobook.title or "-",
            font=ctk.CTkFont(size=18, weight="bold"),
            wraplength=500,
            justify="left"
        )
        title_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Autor
        ctk.CTkLabel(
            section,
            text="✍️ Autor",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(5, 5))
        
        author_label = ctk.CTkLabel(
            section,
            text=self.audiobook.author or "-",
            font=ctk.CTkFont(size=16),
            wraplength=500,
            justify="left"
        )
        author_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Sprecher
        ctk.CTkLabel(
            section,
            text="🎤 Sprecher",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(5, 5))
        
        narrators_text = ", ".join(self.audiobook.narrators) if self.audiobook.narrators else "-"
        narrators_label = ctk.CTkLabel(
            section,
            text=narrators_text,
            font=ctk.CTkFont(size=14),
            wraplength=500,
            justify="left"
        )
        narrators_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Jahr
        ctk.CTkLabel(
            section,
            text="📅 Erscheinungsjahr",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(5, 5))
        
        year_text = str(self.audiobook.year) if self.audiobook.year else "-"
        year_label = ctk.CTkLabel(
            section,
            text=year_text,
            font=ctk.CTkFont(size=14)
        )
        year_label.pack(anchor="w", padx=15, pady=(0, 15))
    
    def create_category_info(self, parent):
        """Erstellt Bereich für Genre/Subgenre"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section,
            text="🏷️ Kategorisierung",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Genre
        ctk.CTkLabel(
            section,
            text="Genre",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(0, 5))
        
        genre_text = self.audiobook.genre or "-"
        genre_label = ctk.CTkLabel(
            section,
            text=genre_text,
            font=ctk.CTkFont(size=14)
        )
        genre_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Subgenre
        ctk.CTkLabel(
            section,
            text="Subgenre",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(5, 5))
        
        subgenre_text = self.audiobook.subgenre or "-"
        subgenre_label = ctk.CTkLabel(
            section,
            text=subgenre_text,
            font=ctk.CTkFont(size=14)
        )
        subgenre_label.pack(anchor="w", padx=15, pady=(0, 15))
    
    def create_universe_info(self, parent):
        """Erstellt Bereich für Universum-Informationen mit Hover-Popup"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section,
            text="🌌 Universum",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        if self.audiobook.universe and self.audiobook.universe.strip():
            # Frame für Universum-Info mit Hover
            universe_frame = ctk.CTkFrame(section, fg_color="transparent")
            universe_frame.pack(anchor="w", padx=15, pady=(0, 15))
            
            # Universum-Name als klickbarer Button mit Hover-Effekt
            universe_btn = ctk.CTkButton(
                universe_frame,
                text=self.audiobook.universe,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="skyblue",
                fg_color="transparent",
                hover_color=("gray80", "gray30"),
                anchor="w",
                command=self.show_universe_popup
            )
            universe_btn.pack(side="left")
            
            # Hover-Event für verzögertes Popup
            universe_btn.bind("<Enter>", lambda e: self.schedule_universe_popup())
            universe_btn.bind("<Leave>", lambda e: self.cancel_universe_popup())
            
            # Kleiner Hinweis
            hint_label = ctk.CTkLabel(
                universe_frame,
                text="(hover für alle Bücher)",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            hint_label.pack(side="left", padx=(10, 0))
            
            # Anzahl der Bücher in diesem Universum
            try:
                books_in_universe = self.db_manager.get_audiobooks_by_universe(self.audiobook.universe)
                count_label = ctk.CTkLabel(
                    universe_frame,
                    text=f"({len(books_in_universe)} Bücher)",
                    font=ctk.CTkFont(size=12),
                    text_color="gray"
                )
                count_label.pack(side="left", padx=(10, 0))
            except:
                pass
            
        else:
            ctk.CTkLabel(
                section,
                text="Kein Universum",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            ).pack(anchor="w", padx=15, pady=(0, 15))
    
    def schedule_universe_popup(self):
        """Plant das Öffnen des Popups mit Verzögerung"""
        self.cancel_universe_popup()
        self.popup_timer = self.after(300, self.show_universe_popup)
    
    def cancel_universe_popup(self):
        """Bricht geplantes Popup ab"""
        if self.popup_timer:
            try:
                self.after_cancel(self.popup_timer)
            except:
                pass
            self.popup_timer = None
    
    def show_universe_popup(self):
        """Zeigt das Popup mit allen Büchern des Universums"""
        if self.audiobook.universe and self.audiobook.universe.strip():
            # Finde das Trigger-Widget (den Universum-Button)
            trigger_widget = None
            for widget in self.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkFrame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, ctk.CTkButton) and grandchild.cget("text") == self.audiobook.universe:
                                    trigger_widget = grandchild
                                    break
            
            self.universe_popup.show_for_universe(
                trigger_widget=trigger_widget or self,
                universe_name=self.audiobook.universe,
                current_audiobook=self.audiobook
            )
    
    # ================ AUDIO-BEREICH MIT DOWNLOAD ================
    
    def create_file_info(self, parent):
        """Erstellt Bereich für Datei-Informationen mit Download-Buttons"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section,
            text="💾 Dateien",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # === Audio-Datei ===
        ctk.CTkLabel(
            section,
            text="🎵 Audio",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(0, 5))
        
        if self.audiobook.audio_path and Path(self.audiobook.audio_path).exists():
            audio_file = Path(self.audiobook.audio_path)
            
            # Hauptframe für Audio
            audio_main_frame = ctk.CTkFrame(section, fg_color="transparent")
            audio_main_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            # Info-Frame (Icon + Name + Größe)
            info_frame = ctk.CTkFrame(audio_main_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)
            
            # Icon
            ctk.CTkLabel(
                info_frame,
                text="🎵",
                font=ctk.CTkFont(size=16),
                width=30
            ).pack(side="left")
            
            # Dateiname
            audio_name = audio_file.name
            name_label = ctk.CTkLabel(
                info_frame,
                text=audio_name[:40] + ("..." if len(audio_name) > 40 else ""),
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            name_label.pack(side="left", padx=(5, 10))
            
            # Dateigröße
            try:
                size = audio_file.stat().st_size
                size_mb = size / (1024 * 1024)
                size_label = ctk.CTkLabel(
                    info_frame,
                    text=f"({size_mb:.1f} MB)",
                    font=ctk.CTkFont(size=11),
                    text_color="gray"
                )
                size_label.pack(side="left")
            except:
                pass
            
            # Button-Frame für Aktionen
            action_frame = ctk.CTkFrame(audio_main_frame, fg_color="transparent")
            action_frame.pack(side="right")
            
            # === DOWNLOAD BUTTON ===
            download_btn = ctk.CTkButton(
                action_frame,
                text="⬇️ Herunterladen",
                font=ctk.CTkFont(size=12),
                width=120,
                height=32,
                fg_color="transparent",
                border_width=1,
                border_color=("gray70", "gray30"),
                hover_color=("gray80", "gray20"),
                command=self.download_audio
            )
            download_btn.pack(side="left", padx=5)
            
            # In Ordner öffnen Button
            folder_btn = ctk.CTkButton(
                action_frame,
                text="📂 Ordner",
                font=ctk.CTkFont(size=12),
                width=80,
                height=32,
                fg_color="transparent",
                border_width=1,
                border_color=("gray70", "gray30"),
                hover_color=("gray80", "gray20"),
                command=self.open_audio_folder
            )
            folder_btn.pack(side="left", padx=5)
            
            # Pfad kopieren Button
            copy_btn = ctk.CTkButton(
                action_frame,
                text="📋 Pfad",
                font=ctk.CTkFont(size=12),
                width=70,
                height=32,
                fg_color="transparent",
                border_width=1,
                border_color=("gray70", "gray30"),
                hover_color=("gray80", "gray20"),
                command=self.copy_audio_path
            )
            copy_btn.pack(side="left", padx=5)
            
        else:
            ctk.CTkLabel(
                section,
                text="Keine Audio-Datei",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            ).pack(anchor="w", padx=15, pady=(0, 15))
    
    def create_description_info(self, parent):
        """Erstellt Bereich für die Beschreibung"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section,
            text="📝 Beschreibung",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        if self.audiobook.description:
            desc_text = self.audiobook.description.strip()
            desc_label = ctk.CTkLabel(
                section,
                text=desc_text,
                font=ctk.CTkFont(size=13),
                wraplength=500,
                justify="left"
            )
            desc_label.pack(anchor="w", padx=15, pady=(0, 15))
        else:
            ctk.CTkLabel(
                section,
                text="Keine Beschreibung vorhanden",
                font=ctk.CTkFont(size=13),
                text_color="gray",
                wraplength=500,
                justify="left"
            ).pack(anchor="w", padx=15, pady=(0, 15))
    
    # ================ VERBINDUNGEN ================
    
    def create_connections_info(self, parent):
        """Erstellt Bereich für verbundene Hörbücher mit verbesserter Darstellung"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section,
            text="🔗 Verbundene Hörbücher",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        if self.connected_books:
            # Container für die Kacheln
            connections_container = ctk.CTkFrame(section, fg_color="transparent")
            connections_container.pack(fill="x", padx=15, pady=(0, 15))
            
            for book in self.connected_books[:5]:  # Max 5 anzeigen
                self.create_connection_card(connections_container, book)
            
            if len(self.connected_books) > 5:
                more_label = ctk.CTkLabel(
                    section,
                    text=f"... und {len(self.connected_books) - 5} weitere",
                    font=ctk.CTkFont(size=11),
                    text_color="gray"
                )
                more_label.pack(anchor="w", padx=15, pady=(5, 15))
        else:
            ctk.CTkLabel(
                section,
                text="Keine Verbindungen zu anderen Hörbüchern",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            ).pack(anchor="w", padx=15, pady=(0, 15))
    
    def create_connection_card(self, parent, book):
        """
        Erstellt eine Kachel für ein verbundenes Hörbuch
        
        Args:
            parent: Parent-Widget
            book: Das verbundene Hörbuch
        """
        # Hauptkachel
        card = ctk.CTkFrame(
            parent,
            fg_color=("gray95", "gray25"),
            corner_radius=10,
            height=70
        )
        card.pack(fill="x", pady=2)
        card.pack_propagate(False)
        
        # Grid-Layout
        card.grid_columnconfigure(1, weight=1)
        card.grid_columnconfigure(2, weight=0)
        
        # === Linke Spalte: Icon ===
        icon_frame = ctk.CTkFrame(card, fg_color="transparent", width=50)
        icon_frame.grid(row=0, column=0, padx=(10, 5), pady=10, rowspan=2, sticky="ns")
        icon_frame.grid_propagate(False)
        
        # Icon basierend auf Universum
        icon = "🌌" if book.universe else "📘"
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=ctk.CTkFont(size=24),
            width=40
        )
        icon_label.pack(expand=True)
        
        # === Mittlere Spalte: Informationen ===
        # Titel
        title_text = book.title[:50] + ("..." if len(book.title) > 50 else "")
        title_label = ctk.CTkLabel(
            card,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=1, padx=5, pady=(10, 0), sticky="w")
        
        # Autor + ID + Universum
        info_parts = []
        if book.author:
            info_parts.append(book.author[:30] + ("..." if len(book.author) > 30 else ""))
        else:
            info_parts.append("Unbekannter Autor")
        
        info_parts.append(book.display_id)
        
        info_text = " • ".join(info_parts)
        
        info_label = ctk.CTkLabel(
            card,
            text=info_text,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        info_label.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="w")
        
        # Universum-Anzeige (falls vorhanden)
        if book.universe:
            universe_badge = ctk.CTkFrame(
                card,
                fg_color=("skyblue", "navy"),
                corner_radius=12,
                height=24
            )
            universe_badge.grid(row=0, column=2, padx=(5, 10), pady=(10, 0), sticky="e")
            universe_badge.grid_propagate(False)
            
            universe_label = ctk.CTkLabel(
                universe_badge,
                text=f"🌌 {book.universe[:15]}" + ("..." if len(book.universe) > 15 else ""),
                font=ctk.CTkFont(size=10),
                text_color="white"
            )
            universe_label.pack(padx=8, pady=2)
        
        # === Rechte Spalte: Action-Button ===
        view_btn = ctk.CTkButton(
            card,
            text="👁️ Anzeigen",
            width=90,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            border_width=1,
            border_color=("gray70", "gray30"),
            hover_color=("gray80", "gray20"),
            command=lambda b=book: self.navigate_to_detail(b)
        )
        view_btn.grid(row=0, column=3, padx=(5, 15), pady=10, rowspan=2, sticky="e")
    
    def load_connected_books(self):
        """Lädt die verbundenen Hörbücher aus der Datenbank"""
        if not self.db_manager or not self.audiobook.connections:
            print("📭 Keine Verbindungen vorhanden")
            return
        
        self.connected_books = []
        for conn_id in self.audiobook.connections:
            try:
                # Konvertiere String zu int falls nötig
                if isinstance(conn_id, str):
                    book_id = int(conn_id)
                else:
                    book_id = conn_id
                
                book = self.db_manager.get_audiobook(book_id)
                if book and book.id != self.audiobook.id:  # Nicht sich selbst
                    self.connected_books.append(book)
                    print(f"✅ Verbindung geladen: {book.display_id} - {book.title}")
            except (ValueError, TypeError):
                print(f"⚠️ Ungültige Verbindungs-ID: {conn_id}")
        
        # Nach Titel sortieren
        self.connected_books.sort(key=lambda x: x.title.lower())
        print(f"✅ {len(self.connected_books)} verbundene Hörbücher geladen")
    
    def navigate_to_detail(self, audiobook):
        """Navigiert zu einem anderen Hörbuch"""
        print(f"📖 Navigiere zu: {audiobook.title} (ID: {audiobook.display_id})")
        
        # Event mit Hörbuch-ID erzeugen
        self.master.event_generate(
            "<<ShowAudiobookDetail>>",
            data=str(audiobook.id)
        )
    
    def on_edit_clicked(self):
        """Bearbeiten-Button Click"""
        print(f"✏️ Bearbeite Hörbuch: {self.audiobook.title}")
        self.master.event_generate(
            "<<EditAudiobook>>",
            data=str(self.audiobook.id)
        )
    
    def on_delete_clicked(self):
        """Löschen-Button Click"""
        # Prüfe ob das Hörbuch Verbindungen hat
        connection_warning = ""
        if self.connected_books:
            connection_warning = f"\n\n⚠️ Dieses Hörbuch ist mit {len(self.connected_books)} anderen Hörbüchern verbunden.\nDiese Verbindungen werden ebenfalls gelöscht!"
        
        if messagebox.askyesno(
            "Hörbuch löschen",
            f"Möchtest du das Hörbuch\n\n'{self.audiobook.title}'\n\nwirklich löschen?{connection_warning}\n\n"
            "Diese Aktion kann nicht rückgängig gemacht werden!"
        ):
            try:
                # Dateien löschen
                if self.file_manager:
                    if self.audiobook.image_path:
                        self.file_manager.delete_file(self.audiobook.image_path)
                    if self.audiobook.audio_path:
                        self.file_manager.delete_file(self.audiobook.audio_path)
                
                # Aus Datenbank löschen
                success = self.db_manager.delete_audiobook(self.audiobook.id)
                
                if success:
                    messagebox.showinfo("Erfolg", "Hörbuch wurde gelöscht!")
                    self.navigate_back()
                else:
                    messagebox.showerror("Fehler", "Hörbuch konnte nicht gelöscht werden.")
                    
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Löschen:\n{str(e)}")
                import traceback
                traceback.print_exc()
    
    def navigate_back(self):
        """Navigation zurück zur Liste"""
        self.master.event_generate("<<NavigateToAudiobookList>>")
    
    # ================ DOWNLOAD & FILE OPERATIONS ================
    
    def download_audio(self):
        """Lädt die Audio-Datei herunter (kopiert an vom Benutzer gewählten Ort)"""
        if not self.audiobook.audio_path or not Path(self.audiobook.audio_path).exists():
            messagebox.showerror(
                "Fehler", 
                "Keine Audio-Datei vorhanden oder Datei nicht gefunden."
            )
            return
        
        try:
            source_path = Path(self.audiobook.audio_path)
            
            # Standard-Dateinamen vorschlagen
            suggested_name = f"{self.audiobook.display_id} - {self.audiobook.title}"
            # Ungültige Zeichen für Dateinamen entfernen
            suggested_name = "".join(c for c in suggested_name if c.isalnum() or c in " .-_")
            suggested_name += source_path.suffix
            
            # Zielpfad vom Benutzer auswählen lassen
            target_path = filedialog.asksaveasfilename(
                title="Audio-Datei speichern unter",
                defaultextension=source_path.suffix,
                initialfile=suggested_name,
                filetypes=[
                    ("Audio-Dateien", f"*{source_path.suffix}"),
                    ("Alle Dateien", "*.*")
                ]
            )
            
            if target_path:
                # Datei kopieren
                shutil.copy2(source_path, target_path)
                
                # Erfolgsmeldung mit Option zum Öffnen des Ordners
                if messagebox.askyesno(
                    "Download erfolgreich",
                    f"Die Datei wurde gespeichert unter:\n{target_path}\n\n"
                    "Möchtest du den Ordner öffnen?"
                ):
                    self._open_file_location(target_path)
        
        except Exception as e:
            messagebox.showerror(
                "Fehler beim Download",
                f"Die Datei konnte nicht heruntergeladen werden:\n{str(e)}"
            )
    
    def download_cover(self):
        """Lädt das Cover-Bild herunter"""
        if not self.audiobook.image_path or not Path(self.audiobook.image_path).exists():
            messagebox.showerror("Fehler", "Kein Cover-Bild vorhanden.")
            return
        
        try:
            source_path = Path(self.audiobook.image_path)
            
            suggested_name = f"{self.audiobook.display_id} - {self.audiobook.title}"
            suggested_name = "".join(c for c in suggested_name if c.isalnum() or c in " .-_")
            suggested_name += source_path.suffix
            
            target_path = filedialog.asksaveasfilename(
                title="Cover-Bild speichern unter",
                defaultextension=source_path.suffix,
                initialfile=suggested_name,
                filetypes=[
                    ("Bilddateien", f"*{source_path.suffix}"),
                    ("Alle Dateien", "*.*")
                ]
            )
            
            if target_path:
                shutil.copy2(source_path, target_path)
                messagebox.showinfo("Erfolg", f"Cover wurde gespeichert:\n{target_path}")
        
        except Exception as e:
            messagebox.showerror("Fehler", f"Cover konnte nicht heruntergeladen werden:\n{str(e)}")
    
    def open_audio_folder(self):
        """Öffnet den Ordner in dem die Audio-Datei gespeichert ist"""
        if not self.audiobook.audio_path or not Path(self.audiobook.audio_path).exists():
            messagebox.showerror(
                "Fehler",
                "Audio-Datei nicht gefunden."
            )
            return
        
        self._open_file_location(self.audiobook.audio_path)
    
    def copy_audio_path(self):
        """Kopiert den Audio-Dateipfad in die Zwischenablage"""
        if self.audiobook.audio_path:
            self.clipboard_clear()
            self.clipboard_append(self.audiobook.audio_path)
            messagebox.showinfo("Pfad kopiert", "Der Dateipfad wurde in die Zwischenablage kopiert.")
    
    def copy_cover_path(self):
        """Kopiert den Cover-Dateipfad in die Zwischenablage"""
        if self.audiobook.image_path:
            self.clipboard_clear()
            self.clipboard_append(self.audiobook.image_path)
            messagebox.showinfo("Pfad kopiert", "Der Dateipfad wurde in die Zwischenablage kopiert.")
    
    def _open_file_location(self, file_path):
        """Öffnet den Ordner und markiert die Datei (plattformunabhängig)"""
        try:
            file_path = Path(file_path)
            
            if platform.system() == "Windows":
                # Windows: Explorer mit markierter Datei
                subprocess.run(['explorer', '/select,', str(file_path)])
            elif platform.system() == "Darwin":  # macOS
                # macOS: Finder mit markierter Datei
                subprocess.run(['open', '-R', str(file_path)])
            else:  # Linux
                # Linux: Ordner öffnen
                subprocess.run(['xdg-open', str(file_path.parent)])
        
        except Exception as e:
            print(f"⚠️ Konnte Ordner nicht öffnen: {e}")
            # Fallback: Einfach den Pfad anzeigen
            messagebox.showinfo(
                "Dateipfad",
                f"Die Datei befindet sich hier:\n{file_path}"
            )
    
    def destroy(self):
        """Räumt Ressourcen frei"""
        # Geplante Popups abbrechen
        self.cancel_universe_popup()
        
        try:
            # Bilder freigeben
            if self.cover_ctk_image:
                del self.cover_ctk_image
            if self.cover_image:
                self.cover_image.close()
        except:
            pass
        
        super().destroy()