"""
Database Service für den Audiobook Manager
"""
from .database_manager import DatabaseManager
from .models.audiobook import Audiobook
from .models.universe import Universe

__version__ = "0.1.0"
__all__ = ['DatabaseManager', 'Audiobook', 'Universe']