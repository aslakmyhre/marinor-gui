import tkinter
import tkintermapview

root = tkinter.Tk()
root.geometry("800x600")

# Create map widget
map_widget = tkintermapview.TkinterMapView(root, width=800, height=600, corner_radius=0)
map_widget.pack(fill="both", expand=True)

# 1. Initialize coordinate list
visited_path = []

# Example: Adding points to the trail
def add_point_to_trail(lat, lon):
    visited_path.append((lat, lon))

# Example points (Rome, Florence, Venice)
map_widget.set_position(43.7696, 11.2558, zoom=6) # Set center
add_point_to_trail(41.9028, 12.4964) # Rome
add_point_to_trail(43.7696, 11.2558) # Florence
add_point_to_trail(45.4408, 12.3155) # Venice
map_widget.set_path(visited_path, color="red", width=4)

root.mainloop()
