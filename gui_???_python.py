
import tkinter as tk
from tkinter import ttk


class marinorGUI():
    def __init__(self, parent):
        # Create the window
        self.parent = parent                # Save a reference to our parent object
        self.window = tk.Toplevel()         # Create a window
        self.window.geometry("1400x800")     # Set pixel dimensions 400 wide by 200 high
        self.window.title("Test app")       # Set window title text
        self.window.protocol("WM_DELETE_WINDOW", self.window.quit) # Enable the close icon
        # Add all your widgets here...
        self.hello_label = tk.Label(self.window, text="Hello world!")
        self.hello_label.place(x=20, y=20)

        self.submit_button = tk.Button(self.window, text="Submit")
        self.submit_button.place(x=20, y=100)

        # Create tab containers & notebook
        self.tab_container = tk.Frame(self.window)
        self.tab_container.place(x=0,y=0,width=400,height=400)
        self.tabs = ttk.Notebook(self.tab_container)
        self.tabs.place(x=0,y=0,height=400,width=400)

        # Create 3 tabs and add them to the notebook
        self.tab_1 = tk.Frame(self.tabs)
        self.tab_2 = tk.Frame(self.tabs)
        self.tab_3 = tk.Frame(self.tabs)
        self.tabs.add(self.tab_1, text="Tab 1")
        self.tabs.add(self.tab_2, text="Tab 2")
        self.tabs.add(self.tab_3, text="Tab 3")

        # Define what function to run when current tab is changed
        self.tabs.bind("<<NotebookTabChanged>>", self.tab_1)


if __name__ == "__main__":
    root = tk.Tk()          # Initialise the tk system into an object called `root`
    root.withdraw()         # Hide the default window

    app = marinorGUI(root)   # Run our window, called marinorGUI
    root.mainloop()         # Start the program loop until all windows exit


###
root.mainloop()
