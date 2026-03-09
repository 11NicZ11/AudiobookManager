from .base_page import BasePage
from .home_page import HomePage
from .audiobook_list import AudiobookListPage

__all__ = ['BasePage', 'HomePage', 'AudiobookListPage']

# Optional: Convenience-Funktionen
def get_all_pages():
    """Gibt eine Liste aller verfügbaren Page-Klassen zurück"""
    return {
        'HomePage': HomePage,
        'AudiobookListPage': AudiobookListPage,
        'BasePage': BasePage
    }

def create_page(page_name, master, **kwargs):
    """Erstellt eine Page-Instanz basierend auf dem Namen"""
    page_classes = get_all_pages()
    
    if page_name not in page_classes:
        raise ValueError(f"Unbekannte Page: {page_name}. Verfügbar: {list(page_classes.keys())}")
    
    return page_classes[page_name](master, **kwargs)