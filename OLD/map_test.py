from tkinter import Tk
from tkintermapview import TkinterMapView

root = Tk()
root.geometry("800x600")

m = TkinterMapView(root, width=800, height=600)
m.pack(fill="both", expand=True)

m.set_position(59.9139, 10.7522)
m.set_zoom(12)

root.mainloop()