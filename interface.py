import tkinter as tk
from tkinter import filedialog, messagebox  # Para abrir archivos y mostrar mensajes
from airport import *
from aircraft import *

# Ventana principal
root = tk.Tk()
root.title("Gestión de Aeropuertos")
root.geometry("600x500")

# Lista de aeropuertos en memoria
airports = []
aircrafts = []

# ================== FUNCIONES ==================

def add_airport():
    icaocode = entry_icao.get().upper()
    try:
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())
    except ValueError:
        messagebox.showerror("Error", "Latitud y longitud deben ser números")
        return

    if len(icaocode) != 4 or not icaocode.isalpha():
        messagebox.showerror("Error", "El código ICAO debe tener 4 letras")
        return

    new_airport = Airport(icaocode, lat, lon)
    SetSchengen(new_airport)
    AddAirport(airports, new_airport)
    messagebox.showinfo("Éxito", f"Aeropuerto {icaocode} agregado correctamente")
    entry_icao.delete(0, tk.END)
    entry_lat.delete(0, tk.END)
    entry_lon.delete(0, tk.END)

def remove_airport():
    icaocode = entry_icao.get().upper()
    if len(icaocode) != 4:
        messagebox.showerror("Error", "Introduce un código ICAO válido")
        return

    result = RemoveAirport(airports, icaocode)
    if result is None:
        messagebox.showinfo("Éxito", f"Aeropuerto {icaocode} eliminado correctamente")
    else:
        messagebox.showerror("Error", f"No se encontró el aeropuerto {icaocode}")

def load_airports_file():
    filename = filedialog.askopenfilename(title="Selecciona archivo de aeropuertos")
    if not filename:
        return
    try:
        global airports
        airports = LoadAirports(filename)
        # Set Schengen para todos
        for ap in airports:
            SetSchengen(ap)
        messagebox.showinfo("Éxito", f"Cargados {len(airports)} aeropuertos desde el archivo")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

def save_schengen_airports():
    if not airports:
        messagebox.showerror("Error", "No hay aeropuertos cargados")
        return
    filename = filedialog.asksaveasfilename(title="Guardar aeropuertos Schengen", defaultextension=".txt")
    if not filename:
        return
    try:
        SaveSchengenAirports(airports, filename)
        messagebox.showinfo("Éxito", f"Aeropuertos Schengen guardados en {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

def show_airports():
    if not airports:
        messagebox.showerror("Error", "No hay aeropuertos cargados")
        return
    info = ""
    for ap in airports:
        info += f"{ap.code} - Lat:{ap.lat}, Lon:{ap.lon}, Schengen:{ap.schengen}\n"
    # Mostrar en ventana emergente
    messagebox.showinfo("Lista de Aeropuertos", info)

def plot_airports():
    if not airports:
        messagebox.showerror("Error", "No hay aeropuertos para graficar")
        return
    try:
        PlotAirports(airports)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo mostrar gráfico:\n{e}")

def map_airports():
    if not airports:
        messagebox.showerror("Error", "No hay aeropuertos para mostrar en Google Earth")
        return
    try:
        MapAirports(airports)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir Google Earth:\n{e}")

def load_arrivals():
    filename = filedialog.askopenfilename(title="Selecciona archivo de vuelos")
    if not filename:
        return

    global aircrafts
    aircrafts = LoadArrivals(filename)

    messagebox.showinfo("Éxito", f"{len(aircrafts)} vuelos cargados")


def save_flights():
    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos")
        return

    filename = filedialog.asksaveasfilename(defaultextension=".txt")
    if not filename:
        return

    SaveFlights(aircrafts, filename)
    messagebox.showinfo("Guardado", "Archivo guardado")


def plot_arrivals():
    PlotArrivals(aircrafts)


def plot_airlines():
    PlotAirlines(aircrafts)


def plot_flight_types():
    PlotFlightsType(aircrafts, airports)


def map_flights():
    MapFlights(aircrafts, airports)
    messagebox.showinfo("KML generado", "Abrir flights.kml en Google Earth")


def map_long_flights():
    MapFlights(aircrafts, airports, only_long=True)
    messagebox.showinfo("KML generado", "Solo vuelos largos")

# ================== INTERFAZ ==================
tk.Label(root, text="Código ICAO:").pack()
entry_icao = tk.Entry(root)
entry_icao.pack()

tk.Label(root, text="Latitud:").pack()
entry_lat = tk.Entry(root)
entry_lat.pack()

tk.Label(root, text="Longitud:").pack()
entry_lon = tk.Entry(root)
entry_lon.pack()

tk.Button(root, text="Agregar aeropuerto", command=add_airport).pack(pady=5)
tk.Button(root, text="Eliminar aeropuerto", command=remove_airport).pack(pady=5)
tk.Button(root, text="Cargar aeropuertos desde archivo", command=load_airports_file).pack(pady=5)
tk.Button(root, text="Guardar aeropuertos Schengen", command=save_schengen_airports).pack(pady=5)
tk.Button(root, text="Mostrar aeropuertos", command=show_airports).pack(pady=5)
tk.Button(root, text="Graficar aeropuertos", command=plot_airports).pack(pady=5)
tk.Button(root, text="Mostrar aeropuertos en Google Earth", command=map_airports).pack(pady=5)
tk.Button(root, text="Cargar vuelos", command=load_arrivals).pack(pady=5)
tk.Button(root, text="Guardar vuelos", command=save_flights).pack(pady=5)
tk.Button(root, text="Plot llegadas por hora", command=plot_arrivals).pack(pady=5)
tk.Button(root, text="Plot por aerolínea", command=plot_airlines).pack(pady=5)
tk.Button(root, text="Plot tipo vuelo", command=plot_flight_types).pack(pady=5)
tk.Button(root, text="Mostrar rutas", command=map_flights).pack(pady=5)
tk.Button(root, text="Mostrar rutas largas", command=map_long_flights).pack(pady=5)



# Arranco la ventana
root.mainloop()
