from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Universe:
    """Modell für ein Hörbuch-Universum"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    timeline_order: List[int] = None  # IDs der Hörbücher in chronologischer Reihenfolge
    
    def __post_init__(self):
        if self.timeline_order is None:
            self.timeline_order = []