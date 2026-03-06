import tkinter as tk
from tkinter import ttk
from tkintermapview import TkinterMapView
from tkinter import messagebox


from typing import Callable, Optional
import queue
import threading
import time


class marinorGUI:
    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.window = tk.Toplevel(master=parent)
        self.window.title("MARINOR NTNU")
        self.window.geometry("1400x800")
        self.window.minsize(900, 600)
        self.window.protocol("WM_DELETE_WINDOW", self.window.quit)

        self.configure_layout()
        self.build_ui()

    def configure_layout(self) -> None:
        self.window.rowconfigure(0, weight=0)  # header
        self.window.rowconfigure(1, weight=1)  # main
        self.window.columnconfigure(0, weight=1)

    def build_ui(self) -> None:
        self.create_header(self.window)
        self.create_main_area(self.window)

    def create_header(self, master: tk.Misc) -> None:
        header = ttk.Frame(master, padding=(12, 8))
        header.grid(row=0, column=0, sticky="ew")

        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=0)

        title = self.create_label(
            header, text="MARINOR NTNU", style="Header.TLabel"
        )
        title.grid(row=0, column=0, sticky="w")

        self.create_style("Header.TLabel", font=("Segoe UI", 16, "bold"))


    def create_main_area(self, master: tk.Misc) -> None:
        """Main area with tabs."""
        main = ttk.Frame(master, padding=12)
        main.grid(row=1, column=0, sticky="nsew")
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)

        # lag tabs
        self.tabs = ttk.Notebook(main)
        self.tabs.grid(row=0, column=0, sticky="nsew")

        self.live_view_tab = ttk.Frame(self.tabs, padding=15)
        self.tab_2 = ttk.Frame(self.tabs, padding=15)
        self.tab_3 = ttk.Frame(self.tabs, padding=15)

        self.tabs.add(self.live_view_tab, text="Live Map View")
        self.tabs.add(self.tab_2, text="Tab 2")
        self.tabs.add(self.tab_3, text="Tab 3")

        # innhold i tab
        self.populate_tab1(self.live_view_tab)
        self.populate_tab2(self.tab_2)
        self.populate_tab3(self.tab_3)

        # Correct binding: bind to a method, not a Frame
        self.tabs.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def populate_tab1(self, master: tk.Misc) -> None:
        """Live Map View – viser et Kartverket-kart med koordinat-søk."""
        # ----- Topp-rad med inputfelt og knapp -----
        topbar = ttk.Frame(master)
        topbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        topbar.columnconfigure(1, weight=1)

        ttk.Label(topbar, text="Koordinat (lat, lon):").grid(row=0, column=0, padx=(0, 8), sticky="w")
        ttk.Label(topbar, text="© Kartverket \n kartverket.no").grid(row=0, column=3, padx=(0, 8), sticky="w")

        self.coord_entry = ttk.Entry(topbar)
        self.coord_entry.bind("<Return>", lambda e: self.center_on_input())
        self.coord_entry.grid(row=0, column=1, sticky="ew")

        ttk.Button(
            topbar,
            text="Sentrer",
            command=self.center_on_input
        ).grid(row=0, column=2, padx=(8, 0))

        # ----- Kart-widgeten under topbaren -----
        self.map_widget = TkinterMapView(master, width=800, height=600, corner_radius=0)
        self.map_widget.grid(row=1, column=0, sticky="nsew")

        # La taben strekke
        master.rowconfigure(1, weight=1)
        master.columnconfigure(0, weight=1)

        # Kartverket tile-server (WebMercator WMTS-cache)
        tile_url = (
            "https://cache.kartverket.no/v1/wmts/1.0.0/"
            "topo/default/webmercator/{z}/{y}/{x}.png"
        )
        self.map_widget.set_tile_server(tile_url, max_zoom=18, tile_size=256)

        # Startposisjon – Oslo
        self.map_widget.set_position(59.9139, 10.7522)
        self.map_widget.set_zoom(18)
            

    def populate_tab2(self, master: tk.Misc) -> None:
        """Example content for Tab 2."""
        lbl = self.create_label(master, text="This is Tab 2")
        lbl.grid(row=0, column=0, sticky="w")

        # Example: a scrolled text log
        container = ttk.Frame(master)
        container.grid(row=1, column=0, sticky="nsew")
        master.rowconfigure(1, weight=1)
        master.columnconfigure(0, weight=1)

        self.log = tk.Text(container, height=20, wrap="word")
        self.log.grid(row=0, column=0, sticky="nsew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.log.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log.configure(yscrollcommand=scrollbar.set)

    def populate_tab3(self, master: tk.Misc) -> None:
        """Example content for Tab 3."""
        lbl = self.create_label(master, text="This is Tab 3")
        lbl.grid(row=0, column=0, sticky="w")

        # Placeholder for future LiDAR canvas
        self.lidar_canvas = tk.Canvas(master, bg="#111", height=300)
        self.lidar_canvas.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        master.rowconfigure(1, weight=1)
        master.columnconfigure(0, weight=1)

## --------------------------------------------
    def create_button(
        self, master: tk.Misc, text: str, command: Optional[Callable] = None, style: Optional[str] = None
    ) -> ttk.Button:
        return ttk.Button(master, text=text, command=command, style=style or "TButton")

    def create_label(
        self, master: tk.Misc, text: str, style: Optional[str] = None
    ) -> ttk.Label:
        return ttk.Label(master, text=text, style=style or "TLabel")

    def create_style(self, name: str, **kwargs) -> None:
        """Create/modify a ttk style once and reuse it."""
        self.style.configure(name, **kwargs)






if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # keep using a hidden root; marinorGUI is a Toplevel
    app = marinorGUI(root)
    root.mainloop()