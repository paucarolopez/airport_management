import tkinter as tk
from tkinter import filedialog, messagebox  # Para abrir archivos y mostrar mensajes
from airport import *
from aircraft import *  # Importamos el nuevo módulo de la Versión 2

# Ventana principal
root = tk.Tk()
root.title("Gestión de Aeropuertos y Vuelos (Versión 2)")
root.geometry("600x700")  # Aumentamos el alto para acomodar los nuevos botones

# Variables de almacenamiento global en memoria
airports = []
flights = []  # Nueva lista global para registrar los vuelos activos


# ================== FUNCIONES DE AEROPUERTOS (V1) ==================

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
        messagebox.showinfo("Éxito", "Archivo airports.kml generado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir Google Earth:\n{e}")


# ================== NUEVAS FUNCIONES DE VUELOS (V2) ==================

def load_flights_file():
    filename = filedialog.askopenfilename(title="Selecciona archivo de llegadas (Arrivals)")
    if not filename:
        return
    try:
        global flights
        flights = LoadArrivals(filename)
        messagebox.showinfo("Éxito", f"Cargados {len(flights)} vuelos desde el archivo")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo de vuelos:\n{e}")


def save_flights_file():
    if not flights:
        messagebox.showerror("Error", "No hay vuelos en memoria para guardar")
        return
    filename = filedialog.asksaveasfilename(title="Guardar historial de vuelos", defaultextension=".txt")
    if not filename:
        return
    try:
        SaveFlights(flights, filename)
        messagebox.showinfo("Éxito", f"Vuelos registrados y salvados en {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")


def plot_arrivals_frequency():
    if not flights:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return
    PlotArrivals(flights)


def plot_airlines_distribution():
    if not flights:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return
    PlotAirlines(flights)


def plot_flights_schengen_type():
    if not flights or not airports:
        messagebox.showerror("Error", "Debes cargar tanto los aeropuertos como los vuelos para esta operación")
        return
    PlotFlightsType(flights, airports)


def map_flights_trajectories():
    if not flights or not airports:
        messagebox.showerror("Error", "Se necesitan vuelos y aeropuertos para mapear las rutas")
        return
    try:
        MapFlights(flights, airports, "flights_trajectories.kml")
        messagebox.showinfo("Éxito", "Archivo flights_trajectories.kml generado para Google Earth.")
    except Exception as e:
        messagebox.showerror("Error", f"Fallo al procesar trayectorias KML:\n{e}")


def map_long_distance_trajectories():
    if not flights or not airports:
        messagebox.showerror("Error", "Se necesitan vuelos y aeropuertos para calcular distancias")
        return
    try:
        # Filtro vuelos a más de 2000 km utilizando la función que programamos
        long_flights = LongDistanceArrivals(flights, airports)
        if not long_flights:
            messagebox.showinfo("Aviso", "No se detectó ningún vuelo que supere los 2000 km de distancia")
            return

        MapFlights(long_flights, airports, "long_distance_flights.kml")
        messagebox.showinfo("Éxito",
                            f"Se han mapeado {len(long_flights)} trayectorias de larga distancia en long_distance_flights.kml")
    except Exception as e:
        messagebox.showerror("Error", f"Fallo al procesar trayectorias de larga distancia:\n{e}")


# ================== INTERFAZ (UI GRÁFICA) ==================

# Sección de entradas de texto (Aeropuerto Manual)
tk.Label(root, text="Código ICAO:", font=("Arial", 9, "bold")).pack()
entry_icao = tk.Entry(root)
entry_icao.pack()

tk.Label(root, text="Latitud:", font=("Arial", 9, "bold")).pack()
entry_lat = tk.Entry(root)
entry_lat.pack()

tk.Label(root, text="Longitud:", font=("Arial", 9, "bold")).pack()
entry_lon = tk.Entry(root)
entry_lon.pack()

# Separador visual interactivo
tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

# BLOQUE DE BOTONES: GESTIÓN AEROPUERTOS (V1)
tk.Label(root, text="--- PANEL DE AEROPUERTOS ---", fg="navy").pack()
tk.Button(root, text="Agregar aeropuerto manual", command=add_airport, width=40).pack(pady=2)
tk.Button(root, text="Eliminar aeropuerto por ICAO", command=remove_airport, width=40).pack(pady=2)
tk.Button(root, text="Cargar base de aeropuertos (.txt)", command=load_airports_file, width=40).pack(pady=2)
tk.Button(root, text="Exportar aeropuertos Schengen", command=save_schengen_airports, width=40).pack(pady=2)
tk.Button(root, text="Mostrar lista en pantalla", command=show_airports, width=40).pack(pady=2)
tk.Button(root, text="Gráfico: Distribución Schengen", command=plot_airports, width=40).pack(pady=2)
tk.Button(root, text="Generar puntos en Google Earth", command=map_airports, width=40).pack(pady=2)

# Separador visual interactivo
tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

# BLOQUE DE BOTONES: GESTIÓN DE VUELOS / AVIONES (V2)
tk.Label(root, text="--- PANEL DE VUELOS (ARRIVALS) ---", fg="darkgreen").pack()
tk.Button(root, text="Cargar archivo de llegadas V2 (.txt)", command=load_flights_file, width=40).pack(pady=2)
tk.Button(root, text="Guardar copia de vuelos en disco", command=save_flights_file, width=40).pack(pady=2)
tk.Button(root, text="Gráfico V2: Llegadas por franja horaria", command=plot_arrivals_frequency, width=40).pack(pady=2)
tk.Button(root, text="Gráfico V2: Cuota por aerolínea", command=plot_airlines_distribution, width=40).pack(pady=2)
tk.Button(root, text="Gráfico V2: Tipo de vuelo (Schengen/No)", command=plot_flights_schengen_type, width=40).pack(
    pady=2)
tk.Button(root, text="Mapear todas las trayectorias en Google Earth", command=map_flights_trajectories, width=40).pack(
    pady=2)
tk.Button(root, text="Mapear SÓLO vuelos de larga distancia (>2000km)", command=map_long_distance_trajectories,
          width=40).pack(pady=2)

# Arranco la ventana
root.mainloop()
