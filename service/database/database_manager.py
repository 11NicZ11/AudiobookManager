import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Tuple
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
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_universes_name ON universes(name)')
        
        conn.commit()
        conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Erstellt eine Datenbankverbindung"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ================ AUDIOBOOK CRUD ================
    
    def add_audiobook(self, audiobook: Audiobook) -> int:
        """
        Fügt ein neues Hörbuch hinzu und gibt die ID zurück.
        Verwendet die nächste verfügbare ID (füllt Lücken).
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Nächste verfügbare ID ermitteln (Lücken füllen)
        next_id = self.get_next_available_id()
        print(f"📋 Füge neues Hörbuch mit ID {next_id} hinzu")
        
        data = audiobook.to_dict()
        
        # Setze die ID explizit (überschreibt vorhandene ID)
        data['id'] = next_id
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        
        try:
            cursor.execute(f'''
                INSERT INTO audiobooks ({columns})
                VALUES ({placeholders})
            ''', list(data.values()))
            
            audiobook.id = next_id
            conn.commit()
            print(f"✅ Hörbuch mit ID {next_id} erfolgreich hinzugefügt")
            
        except sqlite3.IntegrityError as e:
            # Falls es doch einen Konflikt gibt (sollte nicht passieren)
            print(f"❌ IntegrityError: {e}")
            # Versuche es mit der nächsten ID
            cursor.execute('SELECT MAX(id) FROM audiobooks')
            max_id = cursor.fetchone()[0] or 0
            next_id = max_id + 1
            data['id'] = next_id
            
            cursor.execute(f'''
                INSERT INTO audiobooks ({columns})
                VALUES ({placeholders})
            ''', list(data.values()))
            
            audiobook.id = next_id
            conn.commit()
            print(f"✅ Hörbuch mit ID {next_id} (Fallback) erfolgreich hinzugefügt")
            
        except Exception as e:
            print(f"❌ Fehler beim Hinzufügen: {e}")
            conn.rollback()
            raise
            
        finally:
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
        values.append(audiobook.id)
        
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
        # Prüfe ob dieses Hörbuch in Universums-Timelines vorkommt
        self._remove_audiobook_from_all_timelines(audiobook_id)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM audiobooks WHERE id = ?', (audiobook_id,))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def _remove_audiobook_from_all_timelines(self, audiobook_id: int):
        """Entfernt ein Hörbuch aus allen Universums-Timelines"""
        universes = self.get_all_universes()
        for universe in universes:
            if audiobook_id in universe.timeline_order:
                universe.remove_audiobook_from_timeline(audiobook_id)
                self.update_universe(universe)
    
    # ================ AUDIOBOOK SEARCH ================
    
    def search_audiobooks(self, search_term: str) -> List[Audiobook]:
        """Sucht Hörbücher nach Titel, Autor oder Genre"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        search_pattern = f'%{search_term}%'
        cursor.execute('''
            SELECT * FROM audiobooks 
            WHERE title LIKE ? OR author LIKE ? OR genre LIKE ? OR subgenre LIKE ? OR universe LIKE ?
            ORDER BY title
        ''', (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [Audiobook.from_dict(dict(row)) for row in rows]
    
    def get_audiobooks_by_universe(self, universe: str) -> List[Audiobook]:
        """Holt alle Hörbücher eines Universums (nach Name)"""
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
    
    def get_audiobooks_by_universe_id(self, universe_id: int) -> List[Audiobook]:
        """Holt alle Hörbücher eines Universums anhand der Universe-ID"""
        universe = self.get_universe(universe_id)
        if not universe:
            return []
        return self.get_audiobooks_by_universe(universe.name)
    
    def get_audiobooks_by_ids(self, audiobook_ids: List[int]) -> List[Audiobook]:
        """Holt mehrere Hörbücher anhand ihrer IDs"""
        if not audiobook_ids:
            return []
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join(['?' for _ in audiobook_ids])
        cursor.execute(f'''
            SELECT * FROM audiobooks 
            WHERE id IN ({placeholders})
            ORDER BY title
        ''', audiobook_ids)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [Audiobook.from_dict(dict(row)) for row in rows]
    
    def get_audiobook_by_display_id(self, display_id: str) -> Optional[Audiobook]:
        """Holt ein Hörbuch anhand der Display-ID (AUD000001)"""
        if not display_id.startswith('AUD'):
            return None
        
        try:
            audiobook_id = int(display_id[3:])
            return self.get_audiobook(audiobook_id)
        except ValueError:
            return None
    
    def get_next_available_id(self) -> int:
        """
        Gibt die nächste verfügbare ID zurück.
        Sucht zuerst nach Lücken in der ID-Sequenz.
        Wenn keine Lücke gefunden wird, wird die nächsthöhere ID vergeben.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Hole alle vorhandenen IDs
        cursor.execute('SELECT id FROM audiobooks ORDER BY id')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            # Keine IDs vorhanden, fange bei 1 an
            print("📋 Keine IDs vorhanden, starte mit ID 1")
            return 1
        
        # Extrahiere die IDs in eine Liste
        existing_ids = [row[0] for row in rows]
        
        # Sortiere die IDs
        existing_ids.sort()
        print(f"📋 Vorhandene IDs: {existing_ids}")
        
        # Suche nach der ersten Lücke in der Sequenz
        # Beginnend bei 1, prüfe ob jede erwartete ID existiert
        expected_id = 1
        for existing_id in existing_ids:
            if existing_id > expected_id:
                # Lücke gefunden bei expected_id
                print(f"🔍 Lücke gefunden: ID {expected_id} ist frei")
                return expected_id
            expected_id = existing_id + 1
        
        # Keine Lücke gefunden, nimm die nächste ID nach der höchsten
        next_id = max(existing_ids) + 1
        print(f"🔍 Keine Lücke gefunden, nächste ID: {next_id}")
        return next_id
    
    def audiobook_exists(self, audiobook_id: int) -> bool:
        """Prüft ob ein Hörbuch mit der ID existiert"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM audiobooks WHERE id = ?', (audiobook_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        
        return exists
    
    # ================ UNIVERSE CRUD ================
    
    def get_all_universes(self) -> List[Universe]:
        """Holt alle Universen"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM universes ORDER BY name')
        rows = cursor.fetchall()
        conn.close()
        
        universes = []
        for row in rows:
            data = dict(row)
            universe = Universe.from_dict(data)
            
            # Anzahl der Hörbücher in diesem Universum
            universe.audiobook_count = len(self.get_audiobooks_by_universe(universe.name))
            universes.append(universe)
        
        return universes
    
    def get_universe(self, universe_id: int) -> Optional[Universe]:
        """Holt ein Universum anhand der ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM universes WHERE id = ?', (universe_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = dict(row)
            universe = Universe.from_dict(data)
            
            # Anzahl der Hörbücher in diesem Universum
            universe.audiobook_count = len(self.get_audiobooks_by_universe(universe.name))
            return universe
        return None
    
    def get_universe_by_name(self, name: str) -> Optional[Universe]:
        """Holt ein Universum anhand des Namens"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM universes WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = dict(row)
            universe = Universe.from_dict(data)
            
            # Anzahl der Hörbücher in diesem Universum
            universe.audiobook_count = len(self.get_audiobooks_by_universe(universe.name))
            return universe
        return None
    
    def add_universe(self, universe: Universe) -> Tuple[bool, str, int]:
        """
        Fügt ein neues Universum hinzu
        
        Returns:
            (success, message, universe_id)
        """
        if not universe.name or not universe.name.strip():
            return False, "Universum-Name darf nicht leer sein", 0
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            data = universe.to_dict()
            if 'id' in data:
                del data['id']
            
            cursor.execute('''
                INSERT INTO universes (name, description, timeline_order)
                VALUES (?, ?, ?)
            ''', (data['name'], data['description'], data['timeline_order']))
            
            universe.id = cursor.lastrowid
            conn.commit()
            
            return True, f"Universum '{universe.name}' erfolgreich angelegt", universe.id
            
        except sqlite3.IntegrityError:
            return False, f"Universum '{universe.name}' existiert bereits", 0
        except Exception as e:
            return False, f"Fehler beim Anlegen: {str(e)}", 0
        finally:
            conn.close()
    
    def update_universe(self, universe: Universe) -> Tuple[bool, str]:
        """
        Aktualisiert ein Universum
        
        Returns:
            (success, message)
        """
        if not universe.id:
            return False, "Keine gültige Universum-ID"
        
        if not universe.name or not universe.name.strip():
            return False, "Universum-Name darf nicht leer sein"
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            data = universe.to_dict()
            
            cursor.execute('''
                UPDATE universes 
                SET name = ?, description = ?, timeline_order = ?
                WHERE id = ?
            ''', (data['name'], data['description'], data['timeline_order'], universe.id))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, f"Universum '{universe.name}' erfolgreich aktualisiert"
            else:
                return False, "Universum wurde nicht gefunden"
                
        except sqlite3.IntegrityError:
            return False, f"Universum '{universe.name}' existiert bereits"
        except Exception as e:
            return False, f"Fehler beim Aktualisieren: {str(e)}"
        finally:
            conn.close()
    
    def delete_universe(self, universe_id: int) -> Tuple[bool, str]:
        """
        Löscht ein Universum
        
        Returns:
            (success, message)
        """
        # Zuerst Universum holen um Namen zu kennen
        universe = self.get_universe(universe_id)
        if not universe:
            return False, "Universum wurde nicht gefunden"
        
        # Prüfe ob Hörbücher dieses Universum verwenden
        audiobooks = self.get_audiobooks_by_universe(universe.name)
        if audiobooks:
            book_titles = [f"'{ab.title}'" for ab in audiobooks[:3]]
            book_list = ", ".join(book_titles)
            if len(audiobooks) > 3:
                book_list += f" und {len(audiobooks) - 3} weitere"
            
            return False, f"Universum wird von {len(audiobooks)} Hörbüchern verwendet: {book_list}"
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM universes WHERE id = ?', (universe_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, f"Universum '{universe.name}' erfolgreich gelöscht"
            else:
                return False, "Universum wurde nicht gefunden"
                
        except Exception as e:
            return False, f"Fehler beim Löschen: {str(e)}"
        finally:
            conn.close()
    
    # ================ UNIVERSE TIMELINE ================
    
    def get_timeline_audiobooks(self, universe_id: int) -> List[Audiobook]:
        """
        Holt die Hörbücher eines Universums in der chronologischen Reihenfolge
        
        Args:
            universe_id: ID des Universums
        
        Returns:
            Liste der Hörbücher in Timeline-Reihenfolge
        """
        universe = self.get_universe(universe_id)
        if not universe or not universe.timeline_order:
            return []
        
        # Nur IDs die tatsächlich existieren
        valid_ids = []
        for audiobook_id in universe.timeline_order:
            if self.audiobook_exists(audiobook_id):
                valid_ids.append(audiobook_id)
        
        # Aktualisiere Timeline falls ungültige IDs entfernt wurden
        if len(valid_ids) != len(universe.timeline_order):
            universe.timeline_order = valid_ids
            self.update_universe(universe)
        
        return self.get_audiobooks_by_ids(valid_ids)
    
    def update_timeline_order(self, universe_id: int, audiobook_ids: List[int]) -> Tuple[bool, str]:
        """
        Aktualisiert die komplette Timeline-Reihenfolge
        
        Args:
            universe_id: ID des Universums
            audiobook_ids: Liste der Hörbuch-IDs in neuer Reihenfolge
        
        Returns:
            (success, message)
        """
        universe = self.get_universe(universe_id)
        if not universe:
            return False, "Universum wurde nicht gefunden"
        
        # Prüfe ob alle IDs existieren
        invalid_ids = []
        for audiobook_id in audiobook_ids:
            if not self.audiobook_exists(audiobook_id):
                invalid_ids.append(audiobook_id)
        
        if invalid_ids:
            return False, f"Folgende Hörbuch-IDs existieren nicht: {invalid_ids}"
        
        universe.timeline_order = audiobook_ids
        return self.update_universe(universe)
    
    def add_to_timeline(self, universe_id: int, audiobook_id: int, position: Optional[int] = None) -> Tuple[bool, str]:
        """
        Fügt ein Hörbuch zur Timeline hinzu
        
        Args:
            universe_id: ID des Universums
            audiobook_id: ID des Hörbuchs
            position: Optionale Position (None = ans Ende)
        
        Returns:
            (success, message)
        """
        universe = self.get_universe(universe_id)
        if not universe:
            return False, "Universum wurde nicht gefunden"
        
        if not self.audiobook_exists(audiobook_id):
            return False, f"Hörbuch mit ID {audiobook_id} existiert nicht"
        
        universe.add_audiobook_to_timeline(audiobook_id, position)
        return self.update_universe(universe)
    
    def remove_from_timeline(self, universe_id: int, audiobook_id: int) -> Tuple[bool, str]:
        """
        Entfernt ein Hörbuch aus der Timeline
        
        Args:
            universe_id: ID des Universums
            audiobook_id: ID des Hörbuchs
        
        Returns:
            (success, message)
        """
        universe = self.get_universe(universe_id)
        if not universe:
            return False, "Universum wurde nicht gefunden"
        
        universe.remove_audiobook_from_timeline(audiobook_id)
        return self.update_universe(universe)
    
    # ================ STATISTICS ================
    
    def get_statistics(self) -> dict:
        """Gibt verschiedene Statistiken zurück"""
        stats = {
            'total_audiobooks': 0,
            'total_universes': 0,
            'total_genres': 0,
            'most_common_genre': None,
            'most_prolific_author': None,
            'oldest_audiobook': None,
            'newest_audiobook': None,
            'audiobooks_per_year': {},
            'genres': {},
            'authors': {},
            'universes': {}
        }
        
        audiobooks = self.get_all_audiobooks()
        stats['total_audiobooks'] = len(audiobooks)
        stats['total_universes'] = len(self.get_all_universes())
        
        # Genres, Autoren, Jahre sammeln
        genres = {}
        authors = {}
        years = {}
        
        for book in audiobooks:
            # Genre
            if book.genre:
                genres[book.genre] = genres.get(book.genre, 0) + 1
            
            # Autor
            if book.author:
                authors[book.author] = authors.get(book.author, 0) + 1
            
            # Jahr
            if book.year:
                years[book.year] = years.get(book.year, 0) + 1
        
        stats['genres'] = genres
        stats['authors'] = authors
        stats['audiobooks_per_year'] = years
        stats['total_genres'] = len(genres)
        
        if genres:
            stats['most_common_genre'] = max(genres, key=genres.get)
        
        if authors:
            stats['most_prolific_author'] = max(authors, key=authors.get)
        
        if years:
            stats['oldest_audiobook'] = min(years.keys())
            stats['newest_audiobook'] = max(years.keys())
        
        return stats