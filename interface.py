import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from airport import *
from LEBL import *
# FIX 1: importar aircraft.py per poder carregar i usar els vuelos
from aircraft import (Aircraft, LoadArrivals, SaveFlights,
                      PlotArrivals, PlotAirlines, PlotFlightsType,
                      MapFlights, LongDistanceArrivals)

# ================== VENTANA ==================
root = tk.Tk()
root.title("Airport Manager")
root.geometry("750x600")

# Pestañas — FIX 5: afegida pestanya de Vuelos (V2)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab1 = tk.Frame(notebook)
tab2 = tk.Frame(notebook)
tab3 = tk.Frame(notebook)

notebook.add(tab1, text="Aeropuertos")
notebook.add(tab2, text="Vuelos")  # FIX 5: V2
notebook.add(tab3, text="Puertas")  # V3

# ================== DATOS ==================
airports = []
bcn = None
aircrafts = []


# ================== FUNCIONES V1 ==================

def add_airport():
    icaocode = entry_icao.get().upper().strip()
    if len(icaocode) != 4:
        messagebox.showerror("Error", "El código ICAO debe tener exactamente 4 caracteres")
        return
    try:
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())
    except ValueError:
        messagebox.showerror("Error", "Latitud/Longitud inválidas — introduce números")
        return

    new_airport = Airport(icaocode, lat, lon)
    SetSchengen(new_airport)
    AddAirport(airports, new_airport)
    refresh_airports_list()
    messagebox.showinfo("OK", f"{icaocode} añadido")


def remove_airport():
    code = entry_icao.get().upper().strip()
    if not code:
        messagebox.showerror("Error", "Introduce un código ICAO para eliminar")
        return
    result = RemoveAirport(airports, code)
    if result == -1:
        messagebox.showerror("Error", f"Aeropuerto '{code}' no encontrado")
    else:
        refresh_airports_list()
        messagebox.showinfo("OK", f"{code} eliminado")


def load_airports():
    filename = filedialog.askopenfilename(
        title="Selecciona fichero de aeropuertos",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not filename:
        return

    global airports
    airports = LoadAirports(filename)
    # FIX 2: LoadAirports ja crida SetSchengen → eliminat el bucle redundant

    if not airports:
        messagebox.showwarning("Atención", "No se cargó ningún aeropuerto. Revisa el fichero.")
        return

    refresh_airports_list()
    messagebox.showinfo("OK", f"{len(airports)} aeropuertos cargados")


def save_schengen():
    if not airports:
        messagebox.showerror("Error", "No hay aeropuertos cargados")
        return
    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")])
    if not filename:
        return
    result = SaveSchengenAirports(airports, filename)
    if result == -1:
        messagebox.showerror("Error", "Lista vacía, no se guardó nada")
    else:
        messagebox.showinfo("OK", f"Aeropuertos Schengen guardados")


def plot_airports_chart():
    if not airports:
        messagebox.showerror("Error", "No hay aeropuertos cargados")
        return
    PlotAirports(airports)


def map_airports_kml():
    if not airports:
        messagebox.showerror("Error", "No hay aeropuertos cargados")
        return
    MapAirports(airports)
    messagebox.showinfo("KML", "Archivo airports.kml generado. Ábrelo con Google Earth.")


# FIX 3: Listbox en lloc de messagebox per suportar milers d'aeroports
def refresh_airports_list():
    airports_listbox.delete(0, tk.END)
    for ap in airports:
        sch = "Schengen" if ap.schengen else "No-Schengen"
        airports_listbox.insert(tk.END, f"{ap.code}  |  {ap.lat:.4f}, {ap.lon:.4f}  |  {sch}")


# ================== FUNCIONES V2 ==================

# FIX 5: totes les funcions de V2 que faltaven

def load_arrivals():
    filename = filedialog.askopenfilename(
        title="Selecciona fichero de llegadas",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not filename:
        return

    global aircrafts
    aircrafts = LoadArrivals(filename)

    if not aircrafts:
        messagebox.showwarning("Atención", "No se cargó ningún vuelo. Revisa el fichero.")
        return

    refresh_flights_list()
    messagebox.showinfo("OK", f"{len(aircrafts)} vuelos cargados")


def save_flights():
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return
    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")])
    if not filename:
        return
    result = SaveFlights(aircrafts, filename)
    if result == -1:
        messagebox.showerror("Error", "Lista vacía, no se guardó nada")
    else:
        messagebox.showinfo("OK", "Vuelos guardados")


def plot_arrivals_chart():
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return
    PlotArrivals(aircrafts)


def plot_airlines_chart():
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return
    PlotAirlines(aircrafts)


def plot_flights_type_chart():
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return
    PlotFlightsType(aircrafts)


def map_flights_kml():
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return
    MapFlights(aircrafts)
    messagebox.showinfo("KML", "Archivo flights.kml generado. Ábrelo con Google Earth.")


def map_long_distance_kml():
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return
    ld = LongDistanceArrivals(aircrafts)
    messagebox.showinfo("Larga distancia", f"{len(ld)} vuelos de más de 2000 km")


def refresh_flights_list():
    flights_listbox.delete(0, tk.END)
    for ac in aircrafts:
        flights_listbox.insert(tk.END,
                               f"{ac.aircraft_id}  |  {ac.origin}  |  {ac.arrival}  |  {ac.airline}")



# ================== TAB 1 — AEROPUERTOS ==================

tk.Label(tab1, text="Código ICAO").pack()
entry_icao = tk.Entry(tab1)
entry_icao.pack()

tk.Label(tab1, text="Latitud").pack()
entry_lat = tk.Entry(tab1)
entry_lat.pack()

tk.Label(tab1, text="Longitud").pack()
entry_lon = tk.Entry(tab1)
entry_lon.pack()

frame_btns1 = tk.Frame(tab1)
frame_btns1.pack(pady=5)

tk.Button(frame_btns1, text="Agregar", command=add_airport).grid(row=0, column=0, padx=4, pady=3)
tk.Button(frame_btns1, text="Eliminar", command=remove_airport).grid(row=0, column=1, padx=4, pady=3)
tk.Button(frame_btns1, text="Cargar", command=load_airports).grid(row=0, column=2, padx=4, pady=3)
tk.Button(frame_btns1, text="Guardar Schengen", command=save_schengen).grid(row=1, column=0, padx=4, pady=3)
tk.Button(frame_btns1, text="Gráfico", command=plot_airports_chart).grid(row=1, column=1, padx=4, pady=3)
tk.Button(frame_btns1, text="Google Earth", command=map_airports_kml).grid(row=1, column=2, padx=4, pady=3)

# FIX 3: Listbox amb scrollbar per mostrar aeroports
airports_listbox = tk.Listbox(tab1, height=12, font=("Courier New", 9))
airports_listbox.pack(fill="both", expand=True, padx=10, pady=5)
sb_ap = tk.Scrollbar(tab1, orient="vertical", command=airports_listbox.yview)
airports_listbox.configure(yscrollcommand=sb_ap.set)
sb_ap.pack(side="right", fill="y")

# ================== TAB 2 — VUELOS ==================

frame_btns2 = tk.Frame(tab2)
frame_btns2.pack(pady=8)

tk.Button(frame_btns2, text="Cargar llegadas", command=load_arrivals).grid(row=0, column=0, padx=4, pady=3)
tk.Button(frame_btns2, text="Guardar vuelos", command=save_flights).grid(row=0, column=1, padx=4, pady=3)
tk.Button(frame_btns2, text="Gráfico por hora", command=plot_arrivals_chart).grid(row=1, column=0, padx=4, pady=3)
tk.Button(frame_btns2, text="Gráfico aerolíneas", command=plot_airlines_chart).grid(row=1, column=1, padx=4, pady=3)
tk.Button(frame_btns2, text="Gráfico Schengen", command=plot_flights_type_chart).grid(row=2, column=0, padx=4, pady=3)
tk.Button(frame_btns2, text="Google Earth (todos)", command=map_flights_kml).grid(row=2, column=1, padx=4, pady=3)
tk.Button(frame_btns2, text="Larga distancia", command=map_long_distance_kml).grid(row=3, column=0, columnspan=2,
                                                                                   padx=4, pady=3)

flights_listbox = tk.Listbox(tab2, height=12, font=("Courier New", 9))
flights_listbox.pack(fill="both", expand=True, padx=10, pady=5)
sb_fl = tk.Scrollbar(tab2, orient="vertical", command=flights_listbox.yview)
flights_listbox.configure(yscrollcommand=sb_fl.set)
sb_fl.pack(side="right", fill="y")


# ==================
root.mainloop()
