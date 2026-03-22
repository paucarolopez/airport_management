import tkinter as tk
from airport import *


airports = []


def load():
   global airports
   airports = LoadAirports("airports.txt")
   output.insert(tk.END, "Loaded airports\n")


def add():
   code = entry_code.get()
   lat = float(entry_lat.get())
   lon = float(entry_lon.get())


   a = Airport(code, lat, lon)
   SetSchengen(a)
   AddAirport(airports, a)


   output.insert(tk.END, f"Added {code}\n")


def show():
   output.delete(1.0, tk.END)
   for a in airports:
       output.insert(tk.END, f"{a.code} - {a.schengen}\n")


def save():
   SaveSchengenAirports(airports, "schengen.txt")
   output.insert(tk.END, "Saved Schengen airports\n")


def plot():
   PlotAirports(airports)


# GUI
root = tk.Tk()
root.title("Airport Manager")


tk.Label(root, text="Code").pack()
entry_code = tk.Entry(root)
entry_code.pack()


tk.Label(root, text="Latitude").pack()
entry_lat = tk.Entry(root)
entry_lat.pack()


tk.Label(root, text="Longitude").pack()
entry_lon = tk.Entry(root)
entry_lon.pack()


tk.Button(root, text="Load", command=load).pack()
tk.Button(root, text="Add", command=add).pack()
tk.Button(root, text="Show", command=show).pack()
tk.Button(root, text="Save Schengen", command=save).pack()
tk.Button(root, text="Plot", command=plot).pack()


output = tk.Text(root, height=10)
output.pack()


root.mainloop()
