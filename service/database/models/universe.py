from dataclasses import dataclass, field
from typing import List, Optional
import json

@dataclass
class Universe:
    """Modell für ein Hörbuch-Universum"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    timeline_order: List[int] = field(default_factory=list)  # IDs der Hörbücher in chronologischer Reihenfolge
    
    @property
    def display_id(self) -> str:
        """Gibt eine benutzerfreundliche ID zurück (z.B. für GUI)"""
        if self.id:
            return f"UNI{self.id:06d}"  # UNI000001, UNI000002, etc.
        return "Neu"
    
    @property
    def audiobook_count(self) -> int:
        """Gibt die Anzahl der Hörbücher in diesem Universum zurück"""
        # Wird später über den DatabaseManager befüllt
        return 0
    
    def to_dict(self) -> dict:
        """Konvertiert Universe zu Dictionary für JSON/DB"""
        data = {
            'name': self.name,
            'description': self.description,
            'timeline_order': json.dumps(self.timeline_order, ensure_ascii=False)
        }
        if self.id:
            data['id'] = self.id
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Universe':
        """Erstellt Universe aus Dictionary"""
        universe = cls()
        
        # ID setzen (falls vorhanden)
        universe.id = data.get('id')
        
        # Einfache Felder
        universe.name = data.get('name', '')
        universe.description = data.get('description', '')
        
        # JSON-String zurück zu Liste konvertieren
        timeline_order = data.get('timeline_order', '[]')
        if isinstance(timeline_order, str):
            universe.timeline_order = json.loads(timeline_order)
        else:
            universe.timeline_order = timeline_order or []
        
        return universe
    
    def __eq__(self, other: object) -> bool:
        """Vergleich anhand der ID"""
        if not isinstance(other, Universe):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash basierend auf der ID"""
        return hash(self.id) if self.id else hash(id(self))
    
    def add_audiobook_to_timeline(self, audiobook_id: int, position: Optional[int] = None):
        """Fügt ein Hörbuch an bestimmter Position zur Timeline hinzu"""
        if audiobook_id in self.timeline_order:
            self.timeline_order.remove(audiobook_id)
        
        if position is not None and 0 <= position <= len(self.timeline_order):
            self.timeline_order.insert(position, audiobook_id)
        else:
            self.timeline_order.append(audiobook_id)
    
    def remove_audiobook_from_timeline(self, audiobook_id: int):
        """Entfernt ein Hörbuch aus der Timeline"""
        if audiobook_id in self.timeline_order:
            self.timeline_order.remove(audiobook_id)
    
    def get_timeline_position(self, audiobook_id: int) -> Optional[int]:
        """Gibt die Position eines Hörbuchs in der Timeline zurück"""
        try:
            return self.timeline_order.index(audiobook_id)
        except ValueError:
            return None