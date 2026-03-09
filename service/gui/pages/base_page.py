import sys
import os
import customtkinter as ctk

# Dynamischer Import für ScrollableFrame
def get_scrollable_frame():
    """Lädt die ScrollableFrame Klasse dynamisch"""
    try:
        # Von widgets Modul importieren
        from ..widgets.scrollable_frame import ScrollableFrame
        return ScrollableFrame
    except ImportError as e:
        print(f"⚠️  Import fehlgeschlagen: {e}")
        
        #Absoluten Import versuchen
        try:
            # Füge den widgets Pfad manuell hinzu
            current_dir = os.path.dirname(os.path.abspath(__file__))
            widgets_dir = os.path.join(current_dir, "..", "widgets")
            
            if widgets_dir not in sys.path:
                sys.path.insert(0, widgets_dir)
            
            from scrollable_frame import ScrollableFrame
            return ScrollableFrame
        except ImportError:
            # Fallback: Erstelle einfache Version
            print("⚠️  Erstelle Fallback-ScrollableFrame")
            
            class FallbackScrollableFrame(ctk.CTkFrame):
                """Einfacher Fallback wenn ScrollableFrame nicht importiert werden kann"""
                def __init__(self, master, **kwargs):
                    super().__init__(master, **kwargs)
                    self.canvas = ctk.CTkCanvas(self, highlightthickness=0)
                    self.canvas.pack(side="left", fill="both", expand=True)
                    
                    self.scrollbar = ctk.CTkScrollbar(
                        self, 
                        orientation="vertical", 
                        command=self.canvas.yview
                    )
                    self.scrollbar.pack(side="right", fill="y")
                    
                    self.canvas.configure(yscrollcommand=self.scrollbar.set)
                    
                    self.inner_frame = ctk.CTkFrame(self.canvas)
                    self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
                    
                    self.inner_frame.bind("<Configure>", self._on_frame_configure)
                
                def _on_frame_configure(self, event):
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                
                def get_content_frame(self):
                    return self.inner_frame
            
            return FallbackScrollableFrame

# ScrollableFrame Klasse laden
ScrollableFrame = get_scrollable_frame()

class BasePage(ctk.CTkFrame):
    
    def __init__(self, master, **kwargs):
        # Transparenter Hintergrund für alle Pages
        kwargs.setdefault('fg_color', 'transparent')
        kwargs.setdefault('corner_radius', 0)
        
        super().__init__(master, **kwargs)
        
        # Scrollable Frame erstellen
        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True)
        
        # Content Frame (für eigentlichen Inhalt)
        self.content = self.scrollable_frame.get_inner_frame()  # ACHTUNG: get_inner_frame() nicht get_content_frame()
        
        # Standard-Padding Container
        self.padded_container = ctk.CTkFrame(
            self.content, 
            fg_color="transparent"
        )
        self.padded_container.pack(
            fill="both", 
            expand=True, 
            padx=30,
            pady=20
        )
        
        # Für Widgets: self.padded_container verwenden!
    
    def get_content_area(self):
        """Gibt den Bereich zurück wo Widgets platziert werden sollen"""
        return self.padded_container
    
    def clear_content(self):
        """Löscht alle Widgets von der Page"""
        for widget in self.padded_container.winfo_children():
            widget.destroy()
    
    def show_loading(self, message="Lade..."):
        """Zeigt einen Lade-Animation (optional)"""
        self.clear_content()
        
        loading_frame = ctk.CTkFrame(
            self.padded_container,
            fg_color="transparent"
        )
        loading_frame.pack(expand=True)
        
        ctk.CTkLabel(
            loading_frame,
            text="⏳",
            font=ctk.CTkFont(size=48)
        ).pack(pady=20)
        
        ctk.CTkLabel(
            loading_frame,
            text=message,
            font=ctk.CTkFont(size=16)
        ).pack()
        
        return loading_frame
    
    def scroll_to_top(self):
        """Scrollt zum Seitenanfang"""
        if hasattr(self.scrollable_frame, 'scroll_to_top'):
            self.scrollable_frame.scroll_to_top()

# Test-Code (nur wenn direkt ausgeführt)
if __name__ == "__main__":
    print("⚠️  Diese Datei sollte nicht direkt ausgeführt werden!")
    print("ℹ️  Importiere sie stattdessen von main_window.py aus")
    
    # Nur für Debugging: Test-Fenster
    root = ctk.CTk()
    root.geometry("600x400")
    
    page = BasePage(root)
    page.pack(fill="both", expand=True)
    
    # Test-Label
    content = page.get_content_area()
    label = ctk.CTkLabel(content, text="BasePage Test - Läuft!")
    label.pack(pady=50)
    
    root.mainloop()