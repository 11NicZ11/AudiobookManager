from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import json

@dataclass
class Audiobook:
    """Datenmodell für ein Hörbuch mit eindeutiger ID"""
    id: Optional[int] = None
    title: str = ""
    author: str = ""
    narrators: List[str] = field(default_factory=list)
    genre: str = ""
    subgenre: str = ""
    year: Optional[int] = None
    universe: str = ""
    connections: List[str] = field(default_factory=list)
    image_path: str = ""
    audio_path: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def display_id(self) -> str:
        """Gibt eine benutzerfreundliche ID zurück (z.B. für GUI)"""
        if self.id:
            return f"AUD{self.id:06d}"  # AUD000001, AUD000002, etc.
        return "Neu"
    
    def get_short_info(self) -> str:
        """Kurze Zusammenfassung des Hörbuchs"""
        return f"{self.title} ({self.year}) - {self.author}"
    
    def to_dict(self) -> dict:
        """Konvertiert Audiobook zu Dictionary für JSON/DB"""
        data = {
            'title': self.title,
            'author': self.author,
            'narrators': json.dumps(self.narrators, ensure_ascii=False),
            'genre': self.genre,
            'subgenre': self.subgenre,
            'year': self.year,
            'universe': self.universe,
            'connections': json.dumps(self.connections, ensure_ascii=False),
            'image_path': self.image_path,
            'audio_path': self.audio_path,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
        if self.id:
            data['id'] = self.id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Audiobook':
        """Erstellt Audiobook aus Dictionary"""
        audiobook = cls()
        
        # ID setzen (falls vorhanden)
        audiobook.id = data.get('id')
        
        # Einfache Felder
        audiobook.title = data.get('title', '')
        audiobook.author = data.get('author', '')
        audiobook.genre = data.get('genre', '')
        audiobook.subgenre = data.get('subgenre', '')
        audiobook.year = data.get('year')
        audiobook.universe = data.get('universe', '')
        audiobook.image_path = data.get('image_path', '')
        audiobook.audio_path = data.get('audio_path', '')
        audiobook.description = data.get('description', '')
        
        # JSON-Strings zurück zu Listen konvertieren
        narrators = data.get('narrators', '[]')
        connections = data.get('connections', '[]')
        
        audiobook.narrators = json.loads(narrators) if isinstance(narrators, str) else narrators
        audiobook.connections = json.loads(connections) if isinstance(connections, str) else connections
        
        # Datum parsen
        created_at = data.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                audiobook.created_at = datetime.fromisoformat(created_at)
            else:
                audiobook.created_at = created_at
        
        return audiobook
    
    def __eq__(self, other: object) -> bool:
        """Vergleich anhand der ID"""
        if not isinstance(other, Audiobook):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash basierend auf der ID"""
        return hash(self.id) if self.id else hash(id(self))
    
    def update_from(self, other: 'Audiobook') -> None:
        """Aktualisiert dieses Audiobook mit Daten eines anderen (außer ID)"""
        if self.id and other.id and self.id != other.id:
            raise ValueError("Cannot update with different ID")
        
        self.title = other.title
        self.author = other.author
        self.narrators = other.narrators.copy()
        self.genre = other.genre
        self.subgenre = other.subgenre
        self.year = other.year
        self.universe = other.universe
        self.connections = other.connections.copy()
        self.image_path = other.image_path
        self.audio_path = other.audio_path
        self.description = other.description