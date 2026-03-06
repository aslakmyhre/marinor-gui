import tkinter as tk
from tkinter import ttk
from tkintermapview import TkinterMapView
from tkinter import messagebox

##import csv
from typing import Callable, Optional
import threading

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
        self.start_udp_receiver()

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
            command=self.center_on_input()
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
    def step_latitude(step):
        return step*0.000009
    
    def step_longitude(step):
        #step*0.000009/cos(lat[rad])
        ## TODO: generaliser, bruker nå lat=63,4 grader
        return step*0.00002
    
    ## simulator COPILOT
    def start_udp_receiver(self):
        import socket, threading
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", 5005))

        def receiver():
            while True:
                data, _ = sock.recvfrom(1024)
                msg = data.decode().strip()
                parts = msg.split()
                if len(parts) >= 3 and parts[0] == "GPS":
                    try:
                        lat = float(parts[1]); lon = float(parts[2])
                    except ValueError:
                        continue
                    # Kjør GUI-oppdatering i hovedtråd:
                    self.window.after(0, self.map_controller.update_boat_marker, lat, lon, None, None)

        threading.Thread(target=receiver, daemon=True).start()

### TODO: håndter input fra båt
class HandleInput:
    def read_GPS():
        return 0
    def read_5G():
        return 0
    ##

class KartverketMap:
    def __init__(self, master):
        # opprett kartet
        self.map = TkinterMapView(master, width=800, height=600, corner_radius=0)
        self.map.grid(row=0, column=0, sticky="nsew")

        master.rowconfigure(1, weight=1)
        master.columnconfigure(0, weight=1)

        # sett Kartverket WMTS
        tile_url = (
            "https://cache.kartverket.no/v1/wmts/1.0.0/"
            "topo/default/webmercator/{z}/{y}/{x}.png"
        )
        self.map.set_tile_server(tile_url, max_zoom=18, tile_size=256)

        # lagre markørstatus
        self.boat_marker = None

        # start-posisjon
        self.map.set_position(63.43074, 10.40401)
        self.map.set_zoom(18)

    def center_on(self, lat, lon):
        self.map.set_position(lat, lon)
    
    def update_boat_marker(
        self,
        lat: float,
        lon: float,
        heading: float | None = None,
        speed: float | None = None
    ):
        label = "Båt"
        if heading is not None:
            label += f" {heading:.0f}°"
        if speed is not None:
            label += f" {speed:.1f} m/s"

        if getattr(self, "boat_marker", None) is None:
            self.boat_marker = self.map.set_marker(lat, lon, text=label)
        else:
            self.boat_marker.delete()
            self.boat_marker = self.map.set_marker(lat, lon, text=label)

    def parse_latlon(self, text: str) -> tuple[float, float]:

        # Normaliser input
        t = text.replace(";", ",").replace("  ", " ").strip()

        if "," in t:
            parts = [p.strip() for p in t.split(",")]
        else:
            parts = t.split()

        if len(parts) != 2:
            raise ValueError("Skriv på formen 'lat, lon' (XX.XXXXXX, XX.XXXXXX).")

        def read_num_with_hemisphere(s: str, is_lat: bool) -> float:
            s2 = s.replace("°", "").strip()
            hemi = None
            if s2[-1:].upper() in ("N", "S", "E", "W"):
                hemi = s2[-1:].upper()
                s2 = s2[:-1].strip()

            val = float(s2)  # kan kaste ValueError

            if hemi:
                if hemi == "S":
                    val = -abs(val)
                elif hemi == "W":
                    val = -abs(val)
                # N/E beholder positivt fortegn

            # verdi-sjekk
            if is_lat and not (-90 <= val <= 90):
                raise ValueError("Breddegrad (lat) må være i [-90, 90].")
            if not is_lat and not (-180 <= val <= 180):
                raise ValueError("Lengdegrad (lon) må være i [-180, 180].")

            return val

        lat = read_num_with_hemisphere(parts[0], is_lat=True)
        lon = read_num_with_hemisphere(parts[1], is_lat=False)
        return lat, lon

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # skjult rot
    app = marinorGUI(root)
    root.mainloop()