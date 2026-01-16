import customtkinter as ctk

class ScrollableFrame(ctk.CTkFrame):
    """Ein Frame mit vertikaler und horizontaler Scrollbar"""
    
    def __init__(self, master, **kwargs):
        # Extrahiere Scrollbar-spezifische Parameter
        self.scrollbar_width = kwargs.pop('scrollbar_width', 16)
        self.scrollbar_fg_color = kwargs.pop('scrollbar_fg_color', None)
        self.scrollbar_button_color = kwargs.pop('scrollbar_button_color', None)
        self.scrollbar_button_hover_color = kwargs.pop('scrollbar_button_hover_color', None)
        
        super().__init__(master, **kwargs)
        
        # Grid-Konfiguration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Canvas für Scrollbars erstellen
        self.canvas = ctk.CTkCanvas(
            self,
            highlightthickness=0,
            bg=self._apply_appearance_mode(self.cget("fg_color"))
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Vertikale Scrollbar
        self.v_scrollbar = ctk.CTkScrollbar(
            self,
            orientation="vertical",
            command=self.canvas.yview,
            width=self.scrollbar_width,
            fg_color=self.scrollbar_fg_color,
            button_color=self.scrollbar_button_color,
            button_hover_color=self.scrollbar_button_hover_color
        )
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Horizontale Scrollbar
        self.h_scrollbar = ctk.CTkScrollbar(
            self,
            orientation="horizontal",
            command=self.canvas.xview,
            height=self.scrollbar_width,
            fg_color=self.scrollbar_fg_color,
            button_color=self.scrollbar_button_color,
            button_hover_color=self.scrollbar_button_hover_color
        )
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Innerer Frame (für eigentlichen Inhalt)
        self.inner_frame = ctk.CTkFrame(self.canvas)
        
        # Fenster im Canvas erstellen
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.inner_frame,
            anchor="nw",
            tags="inner_frame"
        )
        
        # Canvas konfigurieren
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        
        # Events binden
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shift_mousewheel)
        
        # Fenster-Update
        self.update_idletasks()
    
    def _on_frame_configure(self, event=None):
        """Wird aufgerufen wenn innerer Frame sich ändert"""
        # Canvas Scrollregion aktualisieren
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Canvas Fenster-Größe anpassen
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())
    
    def _on_canvas_configure(self, event):
        """Wird aufgerufen wenn Canvas Größe sich ändert"""
        # Canvas Fenster-Größe anpassen
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self._on_frame_configure()
    
    def _on_mousewheel(self, event):
        """Mousewheel für vertikales Scrollen"""
        if self.canvas.winfo_height() < self.inner_frame.winfo_reqheight():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_shift_mousewheel(self, event):
        """Shift+Mousewheel für horizontales Scrollen"""
        if self.canvas.winfo_width() < self.inner_frame.winfo_reqwidth():
            self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def get_inner_frame(self):
        """Gibt den inneren Frame zurück (für Widget-Platzierung)"""
        return self.inner_frame
    
    def scroll_to_top(self):
        """Scrollt zum Anfang"""
        self.canvas.yview_moveto(0)
        self.canvas.xview_moveto(0)
    
    def scroll_to_bottom(self):
        """Scrollt zum Ende"""
        self.canvas.yview_moveto(1)
    
    def update_scrollbars(self):
        """Aktualisiert die Scrollbar-Sichtbarkeit"""
        # Prüfe ob Scrollbars benötigt werden
        need_v = self.inner_frame.winfo_reqheight() > self.canvas.winfo_height()
        need_h = self.inner_frame.winfo_reqwidth() > self.canvas.winfo_width()
        
        # Grid für Scrollbars anpassen
        if need_v:
            self.v_scrollbar.grid()
        else:
            self.v_scrollbar.grid_remove()
        
        if need_h:
            self.h_scrollbar.grid()
        else:
            self.h_scrollbar.grid_remove()
        
        # Canvas Grid anpassen
        if need_h:
            self.canvas.grid(row=0, column=0, sticky="nsew")
        else:
            self.canvas.grid(row=0, column=0, sticky="nsew", columnspan=2 if not need_v else 1)
    def get_content_frame(self):
        """Gibt den inneren Frame zurück (für Widget-Platzierung)"""
        return self.inner_frame