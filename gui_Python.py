import tkinter as tk
from tkinter import ttk
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

        # Notebook with tabs
        self.tabs = ttk.Notebook(main)
        self.tabs.grid(row=0, column=0, sticky="nsew")

        self.live_view_tab = ttk.Frame(self.tabs, padding=15)
        self.tab_2 = ttk.Frame(self.tabs, padding=15)
        self.tab_3 = ttk.Frame(self.tabs, padding=15)

        self.tabs.add(self.live_view_tab, text="Live Map View")
        self.tabs.add(self.tab_2, text="Tab 2")
        self.tabs.add(self.tab_3, text="Tab 3")

        # Populate tabs
        self._populate_tab1(self.live_view_tab)
        self._populate_tab2(self.tab_2)
        self._populate_tab3(self.tab_3)

        # Correct binding: bind to a method, not a Frame
        self.tabs.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _populate_tab1(self, master: tk.Misc) -> None:
        """Example content for Tab 1."""
        lbl = self._create_label(master, text="This is Tab 1")
        lbl.grid(row=0, column=0, sticky="w")

        self.tab1_status = self._create_label(
            master, text="Status: idle", style="Status.TLabel"
        )
        self._create_style("Status.TLabel", foreground="#555")
        self.tab1_status.grid(row=1, column=0, sticky="w", pady=(6, 0))

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
