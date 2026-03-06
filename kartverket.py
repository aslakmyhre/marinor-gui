import tkinter as tk
from tkinter import ttk
from tkintermapview import TkinterMapView
from tkinter import messagebox

class KartverketMap:
    def __init__(self, master):
        self.visited_path = []
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
    
    def update_boat_marker(self, lat: float, lon: float, heading: float | None = None, speed: float | None = None):
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
        
        self.map.set_position(lat, lon)
        self.visited_path.append(lat,lon)
        self.map.set_path(self.visited_path, color="red", width=4)

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