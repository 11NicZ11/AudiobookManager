import sqlite3
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .models.audiobook import Audiobook
from .models.universe import Universe

class DatabaseManager:
    """Hauptklasse für Datenbankoperationen"""
    
    def __init__(self, db_path: str = "data/audiobooks.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialisiert die Datenbank mit Tabellen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabelle für Hörbücher
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audiobooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                narrators TEXT DEFAULT '[]',
                genre TEXT,
                subgenre TEXT,
                year INTEGER,
                universe TEXT,
                connections TEXT DEFAULT '[]',
                image_path TEXT,
                audio_path TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabelle für Universen
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS universes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                timeline_order TEXT DEFAULT '[]'
            )
        ''')
        
        # Indexe für schnelle Suche
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audiobooks_title ON audiobooks(title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audiobooks_author ON audiobooks(author)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audiobooks_genre ON audiobooks(genre)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audiobooks_universe ON audiobooks(universe)')
        
        conn.commit()
        conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Erstellt eine Datenbankverbindung"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Ermöglicht Zugriff über Spaltennamen
        return conn
    
    # --- CRUD-Operationen für Hörbücher ---
    
    def add_audiobook(self, audiobook: Audiobook) -> int:
        """Fügt ein neues Hörbuch hinzu und gibt die ID zurück"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data = audiobook.to_dict()
        # ID entfernen, da AUTOINCREMENT
        if 'id' in data:
            del data['id']
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        
        cursor.execute(f'''
            INSERT INTO audiobooks ({columns})
            VALUES ({placeholders})
        ''', list(data.values()))
        
        audiobook.id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return audiobook.id
    
    def get_audiobook(self, audiobook_id: int) -> Optional[Audiobook]:
        """Holt ein Hörbuch anhand der ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM audiobooks WHERE id = ?', (audiobook_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Audiobook.from_dict(dict(row))
        return None
    
    def get_all_audiobooks(self) -> List[Audiobook]:
        """Holt alle Hörbücher"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM audiobooks ORDER BY title')
        rows = cursor.fetchall()
        conn.close()
        
        return [Audiobook.from_dict(dict(row)) for row in rows]
    
    def update_audiobook(self, audiobook: Audiobook) -> bool:
        """Aktualisiert ein Hörbuch"""
        if not audiobook.id:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data = audiobook.to_dict()
        columns = ', '.join([f"{key} = ?" for key in data.keys() if key != 'id'])
        values = [data[key] for key in data.keys() if key != 'id']
        values.append(audiobook.id)  # WHERE id = ?
        
        cursor.execute(f'''
            UPDATE audiobooks 
            SET {columns}
            WHERE id = ?
        ''', values)
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def delete_audiobook(self, audiobook_id: int) -> bool:
        """Löscht ein Hörbuch"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM audiobooks WHERE id = ?', (audiobook_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    # --- Suchfunktionen ---
    
    def search_audiobooks(self, search_term: str) -> List[Audiobook]:
        """Such Hörbücher nach Titel, Autor oder Genre"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        search_pattern = f'%{search_term}%'
        cursor.execute('''
            SELECT * FROM audiobooks 
            WHERE title LIKE ? OR author LIKE ? OR genre LIKE ?
            ORDER BY title
        ''', (search_pattern, search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [Audiobook.from_dict(dict(row)) for row in rows]
    
    def get_audiobooks_by_universe(self, universe: str) -> List[Audiobook]:
        """Holt alle Hörbücher eines Universums"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM audiobooks 
            WHERE universe = ?
            ORDER BY year, title
        ''', (universe,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [Audiobook.from_dict(dict(row)) for row in rows]


    def get_audiobook_by_display_id(self, display_id: str) -> Optional[Audiobook]:
        """Holt ein Hörbuch anhand der Display-ID (AUD000001)"""
        if not display_id.startswith('AUD'):
            return None
        
        try:
            audiobook_id = int(display_id[3:])  # 'AUD000001' -> 1
            return self.get_audiobook(audiobook_id)
        except ValueError:
            return None
    
    def get_next_available_id(self) -> int:
        """Gibt die nächste verfügbare ID zurück"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT MAX(id) FROM audiobooks')
        result = cursor.fetchone()
        conn.close()
        
        max_id = result[0] if result[0] else 0
        return max_id + 1
    
    def audiobook_exists(self, audiobook_id: int) -> bool:
        """Prüft ob ein Hörbuch mit der ID existiert"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM audiobooks WHERE id = ?', (audiobook_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        
        return exists