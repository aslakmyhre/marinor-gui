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

        # Theme
        self.style = ttk.Style()
        try:
            self.style.theme_use("vista")
        except Exception:
            pass

        # root container
        self._configure_layout()

        # data
        self.incoming_msgs: "queue.Queue[str]" = queue.Queue()

        # UI
        self._build_ui()
        self._schedule_ui_tick()

        # Example: start a demo background thread simulating data arrival
        self._start_demo_background_producer() # (Copilot)

    # ---------- Layout & UI ----------

    def _configure_layout(self) -> None:
        self.window.rowconfigure(0, weight=0)  # header
        self.window.rowconfigure(1, weight=1)  # main
        self.window.columnconfigure(0, weight=1)

    def _build_ui(self) -> None:
        self._create_header(self.window)
        self._create_main_area(self.window)

    def _create_header(self, master: tk.Misc) -> None:
        header = ttk.Frame(master, padding=(12, 8))
        header.grid(row=0, column=0, sticky="ew")

        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=0)

        title = self._create_label(
            header, text="MARINOR NTNU", style="Header.TLabel"
        )
        title.grid(row=0, column=0, sticky="w")

        self._create_style("Header.TLabel", font=("Segoe UI", 16, "bold"))


    def _create_main_area(self, master: tk.Misc) -> None:
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
        self._populate_tab1(self.live_view_tab)
        self._populate_tab2(self.tab_2)
        self._populate_tab3(self.tab_3)

        # Correct binding: bind to a method, not a Frame
        self.tabs.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _populate_tab1(self, master: tk.Misc) -> None:
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
            

    def _populate_tab2(self, master: tk.Misc) -> None:
        """Example content for Tab 2."""
        lbl = self._create_label(master, text="This is Tab 2")
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

    def _populate_tab3(self, master: tk.Misc) -> None:
        """Example content for Tab 3."""
        lbl = self._create_label(master, text="This is Tab 3")
        lbl.grid(row=0, column=0, sticky="w")

        # Placeholder for future LiDAR canvas
        self.lidar_canvas = tk.Canvas(master, bg="#111", height=300)
        self.lidar_canvas.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        master.rowconfigure(1, weight=1)
        master.columnconfigure(0, weight=1)

    # ---------- Helper factories (you asked about these!) ----------

    def _create_button(
        self, master: tk.Misc, text: str, command: Optional[Callable] = None, style: Optional[str] = None
    ) -> ttk.Button:
        return ttk.Button(master, text=text, command=command, style=style or "TButton")

    def _create_label(
        self, master: tk.Misc, text: str, style: Optional[str] = None
    ) -> ttk.Label:
        return ttk.Label(master, text=text, style=style or "TLabel")

    def _create_style(self, name: str, **kwargs) -> None:
        """Create/modify a ttk style once and reuse it."""
        self.style.configure(name, **kwargs)

    # ---------- Event handlers ----------

    def on_submit(self) -> None:
        self._append_log("[UI] Submit clicked\n")
        self.tab1_status.configure(text="Status: submitted")

    def _on_tab_changed(self, event: tk.Event) -> None:
        tab_idx = event.widget.index("current")
        tab_text = event.widget.tab(tab_idx, "text")
        self._append_log(f"[UI] Switched to: {tab_text}\n")

    def on_close(self) -> None:
        """Close this window and stop the app if it's the last one."""
        self.window.destroy()

    def center_on_input(self):
        """Leser koordinat fra self.coord_entry, validerer og sentrerer kartet."""
        text = (self.coord_entry.get() or "").strip()
        try:
            lat, lon = self._parse_latlon(text)
        except ValueError as e:
            messagebox.showerror("Ugyldig koordinat", str(e))
            return

        # Valider rekkevidde
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            messagebox.showerror("Ugyldig koordinat", "Lat må være i [-90,90] og Lon i [-180,180].")
            return

        # Sentrer kartet
        self.map_widget.set_position(lat, lon)
        # (valgfritt) juster zoom hvis du vil sikre et minimumsnivå:
        # if self.map_widget.get_zoom() < 10:
        #     self.map_widget.set_zoom(12)

    def _parse_latlon(self, text: str) -> tuple[float, float]:
        """
        Parse en enkel lat/lon i desimalgrader.
        Godtar separatorer: komma, semikolon, mellomrom.
        Godtar (valgfritt) N/S/E/W etter tallene.
        Eksempler:
        '59.9139,10.7522'
        '59.9139 10.7522'
        '59.9139; 10.7522'
        '59.9139 N, 10.7522 E'
        """
        # Normaliser: bytt semikolon til komma, komprimér whitespace
        t = text.replace(";", ",").replace("  ", " ").strip()

        # Del på komma hvis mulig, ellers på whitespace
        if "," in t:
            parts = [p.strip() for p in t.split(",")]
        else:
            parts = t.split()

        if len(parts) != 2:
            raise ValueError("Skriv på formen 'lat, lon' (f.eks. 59.9139, 10.7522).")

        def read_num_with_hemisphere(s: str, is_lat: bool) -> float:
            # Fjern grads‑symboler og normaliser
            s2 = s.replace("°", "").strip()
            # Sjekk for N/S/E/W
            hemi = None
            if s2[-1:].upper() in ("N", "S", "E", "W"):
                hemi = s2[-1:].upper()
                s2 = s2[:-1].strip()

            val = float(s2)  # kan kaste ValueError (fanges av kallende funksjon)

            if hemi:
                if hemi == "S":
                    val = -abs(val)
                elif hemi == "W":
                    val = -abs(val)
                # N/E beholder positivt fortegn

            # Grov rekkevidde-sjekk isolert
            if is_lat and not (-90 <= val <= 90):
                raise ValueError("Breddegrad (lat) må være i [-90, 90].")
            if not is_lat and not (-180 <= val <= 180):
                raise ValueError("Lengdegrad (lon) må være i [-180, 180].")

            return val

        lat = read_num_with_hemisphere(parts[0], is_lat=True)
        lon = read_num_with_hemisphere(parts[1], is_lat=False)
        return lat, lon

    # ---------- Background data model (prep for 5G/LiDAR) ----------

    def _schedule_ui_tick(self) -> None:
        """Periodic UI update; safe to call from main thread only."""
        self._drain_incoming_messages()
        # Redraw LiDAR canvas here if you have new data
        # self._draw_lidar_frame(latest_points)

        # Schedule next tick (e.g., 30 FPS ~ 33 ms; logs/telemetry can be 50–200 ms)
        self.window.after(100, self._schedule_ui_tick)

    def _drain_incoming_messages(self) -> None:
        """Pull messages from the background queue and update the UI."""
        try:
            while True:
                msg = self.incoming_msgs.get_nowait()
                self._append_log(msg)
        except queue.Empty:
            pass

    def _append_log(self, text: str) -> None:
        if hasattr(self, "log"):
            self.log.insert("end", text)
            self.log.see("end")

    # ---------- Demo background producer (simulate 5G data) ----------

    def _start_demo_background_producer(self) -> None:
        def worker(q: "queue.Queue[str]"):
            i = 0
            while True:
                time.sleep(1.0)
                q.put(f"[5G] Telemetry packet {i}\n")
                i += 1

        t = threading.Thread(target=worker, args=(self.incoming_msgs,), daemon=True)
        t.start()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # keep using a hidden root; marinorGUI is a Toplevel
    app = marinorGUI(root)
    root.mainloop()
