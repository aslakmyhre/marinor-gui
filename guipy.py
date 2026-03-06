import tkinter as tk
from tkinter import ttk
from tkintermapview import TkinterMapView
from tkinter import messagebox

##import csv
from typing import Callable, Optional
import threading

from kartverket import KartverketMap
from inputhandler import HandleInput

class marinorGUI:
    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.window = tk.Toplevel(master=parent)
        self.window.title("MARINOR NTNU")
        self.window.geometry("1400x800")
        self.window.minsize(900, 600)
        self.window.protocol("WM_DELETE_WINDOW", self.window.quit)
        self.style = ttk.Style()

        #simulator:
        self.handle_input = HandleInput(self)
        self.handle_input.start_udp_receiver()

        self.configure_layout()
        self.build_ui()

    def configure_layout(self) -> None:
        self.window.rowconfigure(0, weight=0) # header
        self.window.rowconfigure(1, weight=1) # main
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

        header.battery_bar = ttk.Progressbar(
            header,
            orient="vertical",
            length=50,
            mode="determinate"
        )

        header.battery_bar.grid(
            row=0,
            column=1,
            sticky="e",
            padx=20
        )

        header.battery_bar["maximum"] = 100
        #header.battery_bar["value"] = 100


    def create_main_area(self, master: tk.Misc) -> None:
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

    def populate_tab1(self, master: tk.Misc) -> None:
        topbar = ttk.Frame(master)
        topbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        topbar.columnconfigure(1, weight=1)

        ttk.Label(topbar, text="Koordinat (lat, lon):").grid(row=0, column=0, padx=(0, 8), sticky="w")
        ttk.Label(topbar, text="© Kartverket \nkartverket.no").grid(row=0, column=3, padx=(12, 0), sticky="w")

        map_frame = ttk.Frame(master)
        map_frame.grid(row=1, column=0, sticky="nsew")
        master.rowconfigure(0, weight=0) # topbar
        master.rowconfigure(1, weight=1) # kart
        master.columnconfigure(0, weight=1)

        self.map_controller = KartverketMap(map_frame)
        self.coord_entry = ttk.Entry(topbar)
        self.coord_entry.bind("<Return>", lambda e: self.center_on_input())
        self.coord_entry.grid(row=0, column=1, sticky="ew")

        ttk.Button(
            topbar,
            text="Sentrer",
            command=self.center_on_input
        ).grid(row=0, column=2, padx=(8, 0))
            
    def populate_tab2(self, master: tk.Misc) -> None:
        #foreløpig tom
        lbl = self.create_label(master, text="This is Tab 2")
        lbl.grid(row=0, column=0, sticky="w")

    def populate_tab3(self, master: tk.Misc) -> None:
        #foreløpig tom
        lbl = self.create_label(master, text="This is Tab 3")
        lbl.grid(row=0, column=0, sticky="w")

    ## GUI-funksjoner
    def create_button(
        self, master: tk.Misc, text: str, command: Optional[Callable] = None, style: Optional[str] = None
    ) -> ttk.Button:
        return ttk.Button(master, text=text, command=command, style=style or "TButton")

    def create_label(
        self, master: tk.Misc, text: str, style: Optional[str] = None
    ) -> ttk.Label:
        return ttk.Label(master, text=text, style=style or "TLabel")

    def create_style(self, name: str, **kwargs) -> None:
        self.style.configure(name, **kwargs)

    ## sentrer
    def center_on_input(self):
        text = (self.coord_entry.get() or "").strip()
        try:
            lat, lon = self.map_controller.parse_latlon(text)
        except ValueError as e:
            messagebox.showerror("Ugyldig koordinat", str(e))
            return

        # Valider
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            messagebox.showerror("Ugyldig koordinat", "Lat må være i [-90,90] og Lon i [-180,180].")
            return

        # Sentrer kartet
        self.map_controller.center_on(lat, lon)
    
    ## andre funksjoner
    """def battery_level(self, batteryPercent):
        self.battery_bar['value'] = batteryPercent
        print(batteryPercent)
        return 0"""

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # skjult rot
    app = marinorGUI(root)
    root.mainloop()