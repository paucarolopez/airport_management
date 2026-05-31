import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from airport import *
from LEBL import *
from aircraft import (Aircraft, LoadArrivals, SaveFlights,
                      PlotArrivals, PlotAirlines, PlotFlightsType,
                      MapFlights, LongDistanceArrivals)

# ================== VENTANA ==================
root = tk.Tk()
root.title("Airport Manager - Version 4")
root.geometry("750x650")

# ================== COLORS ==================
root.configure(bg="#1e1e2e")

COLORS = {
    "bg": "#1e1e2e",
    "card": "#2a2a3e",
    "accent": "#7c6af7",
    "accent2": "#2ea88a",  # verd més apagat (era #56cfb2)
    "danger": "#e06c75",
    "text": "#cdd6f4",
    "subtext": "#cdd6f4",  # igual que text perquè es vegi bé
    "entry_bg": "#313244",
}

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background=COLORS["bg"], borderwidth=0)
style.configure("TNotebook.Tab",
                background=COLORS["card"], foreground=COLORS["subtext"],
                padding=[14, 6], font=("Georgia", 10))
style.map("TNotebook.Tab",
          background=[("selected", COLORS["accent"])],
          foreground=[("selected", "white")])

# Configure structure for TCombobox style compatibility
style.configure("TCombobox", fieldbackground=COLORS["entry_bg"], background=COLORS["card"], foreground=COLORS["text"])

# ================== PESTANYES ==================
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab1 = tk.Frame(notebook, bg=COLORS["bg"])
tab2 = tk.Frame(notebook, bg=COLORS["bg"])
tab3 = tk.Frame(notebook, bg=COLORS["bg"])

notebook.add(tab1, text="Aeropuertos")
notebook.add(tab2, text="Vuelos")
notebook.add(tab3, text="Puertas")

# ================== DADES GLOBALS ==================
airports = []
bcn = None
aircrafts = []  # Contiene la lista unificada tras el Merge o las llegadas iniciales
arrivals_raw = []  # Almacenamiento temporal estricto de llegadas
departures_raw = []  # Almacenamiento temporal estricto de salidas (NUEVO V4)


# ================== HELPERS D'ESTIL ==================

def styled_button(parent, text, command, color=None):
    c = color or COLORS["accent"]
    return tk.Button(parent, text=text, command=command,
                     bg=c, fg="white", font=("Georgia", 10, "bold"),
                     relief="flat", padx=12, pady=6, cursor="hand2",
                     activebackground=COLORS["accent"], activeforeground="white")


def styled_label(parent, text, size=10, bold=False, bg=None):
    weight = "bold" if bold else "normal"
    bg_color = bg or COLORS["bg"]
    return tk.Label(parent, text=text, bg=bg_color,
                    fg=COLORS["text"], font=("Georgia", size, weight))


def styled_entry(parent):
    return tk.Entry(parent, bg=COLORS["entry_bg"], fg=COLORS["text"],
                    font=("Georgia", 11), relief="flat", insertbackground="white", bd=6)


# ================== FUNCIONS V1 ==================

def add_airport():
    icaocode = entry_icao.get().upper().strip()
    if len(icaocode) != 4:
        messagebox.showerror("Error", "El codi ICAO ha de tenir exactament 4 caràcters")
        return
    try:
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())
    except ValueError:
        messagebox.showerror("Error", "Latitud/Longitud invàlides — introdueix números")
        return

    new_airport = Airport(icaocode, lat, lon)
    SetSchengen(new_airport)
    AddAirport(airports, new_airport)
    refresh_airports_list()
    messagebox.showinfo("OK", f"{icaocode} afegit")


def remove_airport():
    code = entry_icao.get().upper().strip()
    if not code:
        messagebox.showerror("Error", "Introdueix un codi ICAO per eliminar")
        return
    result = RemoveAirport(airports, code)
    if result == -1:
        messagebox.showerror("Error", f"Aeroport '{code}' no trobat")
    else:
        refresh_airports_list()
        messagebox.showinfo("OK", f"{code} eliminat")


def load_airports():
    filename = filedialog.askopenfilename(
        title="Selecciona el fitxer d'aeroports",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not filename:
        return
    global airports
    airports = LoadAirports(filename)
    if not airports:
        messagebox.showwarning("Atenció", "No s'ha carregat cap aeroport.")
        return
    refresh_airports_list()
    messagebox.showinfo("OK", f"{len(airports)} aeroports carregats")


def save_schengen():
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats")
        return
    filename = filedialog.asksaveasfilename(
        defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if not filename:
        return
    result = SaveSchengenAirports(airports, filename)
    if result == -1:
        messagebox.showerror("Error", "Llista buida, no s'ha guardat res")
    else:
        messagebox.showinfo("OK", "Aeroports Schengen guardats")


def plot_airports_chart():
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats")
        return
    PlotAirports(airports)


def map_airports_kml():
    if not airports:
        messagebox.showerror("Error", "No hi ha aeroports carregats")
        return
    MapAirports(airports)
    messagebox.showinfo("KML", "Fitxer airports.kml generat.")


def refresh_airports_list():
    airports_listbox.delete(0, tk.END)
    for ap in airports:
        sch = "Schengen" if ap.schengen else "No-Schengen"
        airports_listbox.insert(tk.END, f"{ap.code}  |  {ap.lat:.4f}, {ap.lon:.4f}  |  {sch}")


# ================== FUNCIONS V2 & V4 (VUELOS) ==================

def load_arrivals():
    filename = filedialog.askopenfilename(
        title="Selecciona el fitxer d'arribades",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not filename:
        return
    global arrivals_raw, aircrafts
    arrivals_raw = LoadArrivals(filename)
    if not arrivals_raw:
        messagebox.showwarning("Atencio", "No s'ha carregat cap vol d'arribada.")
        return
    aircrafts = arrivals_raw  # Comportamiento V2 por defecto inicial
    refresh_flights_list()
    messagebox.showinfo("OK", f"{len(arrivals_raw)} vols d'arribada carregats")


def load_departures_v4():
    """NUEVO V4: Carga las salidas utilizando la función requerida LoadDepartures"""
    filename = filedialog.askopenfilename(
        title="Selecciona el fitxer de sortides (Departures)",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not filename:
        return
    global departures_raw
    deps, error_code = LoadDepartures(filename)
    if error_code == -1:
        messagebox.showerror("Error", "No s'ha pogut trobar o llegir el fitxer de sortides.")
        return
    departures_raw = deps
    messagebox.showinfo("OK V4", f"{len(departures_raw)} vols de sortida carregats amb èxit.")


def merge_movements_v4():
    """NUEVO V4: Fusiona las listas de arribadas y salidas según requerimientos de rúbrica"""
    global arrivals_raw, departures_raw, aircrafts
    if not arrivals_raw or not departures_raw:
        messagebox.showerror("Error V4", "Es requereix haver carregat 'Arribades' i 'Sortides' abans de fusionar.")
        return

    result = MergeMovements(arrivals_raw, departures_raw)
    if result == -1:
        messagebox.showerror("Error V4", "Error al fusionar: Una de les llistes de moviments està buida.")
        return

    aircrafts = result
    refresh_flights_list()
    messagebox.showinfo("Merge OK V4", f"Moviments unificats: {len(aircrafts)} estructures actives de control.")


def show_night_aircraft_v4():
    """NUEVO V4: Extrae de forma aislada los aviones nocturnos (sólo salida) y los lista en pantalla"""
    global aircrafts
    if not aircrafts:
        messagebox.showerror("Error V4", "La llista de vols global està buida.")
        return
    night_list = NightAircraft(aircrafts)
    if night_list == -1:
        messagebox.showerror("Error V4", "Error al processar la llista.")
        return

    # Mostrar el resultado temporalmente limpiando la listbox principal
    flights_listbox.delete(0, tk.END)
    for ac in night_list:
        flights_listbox.insert(tk.END,
                               f"[NIGHT] {ac.id}  |  Destí: {ac.destination}  |  Sortida: {ac.departure}  |  {ac.airline}")
    messagebox.showinfo("Night Aircraft V4", f"S'han filtrat {len(night_list)} vols nocturnos (només sortida).")


def save_flights():
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats")
        return
    filename = filedialog.asksaveasfilename(
        defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if not filename:
        return
    result = SaveFlights(aircrafts, filename)
    if result == -1:
        messagebox.showerror("Error", "Llista buida, no s'ha guardat res")
    else:
        messagebox.showinfo("OK", "Vols guardats")


def plot_arrivals_chart():
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats")
        return
    PlotArrivals(aircrafts)


def plot_airlines_chart():
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats")
        return
    PlotAirlines(aircrafts)


def plot_flights_type_chart():
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats")
        return
    PlotFlightsType(aircrafts)


def map_flights_kml():
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats")
        return
    MapFlights(aircrafts)
    messagebox.showinfo("KML", "Fitxer flights.kml generat.")


def map_long_distance_kml():
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats")
        return
    ld = LongDistanceArrivals(aircrafts)
    messagebox.showinfo("Llarga distancia", f"{len(ld)} vols de mes de 2000 km")


def refresh_flights_list():
    flights_listbox.delete(0, tk.END)
    for ac in aircrafts:
        arr_time = getattr(ac, 'arrival', '') if getattr(ac, 'arrival', '') else '--:--'
        dep_time = getattr(ac, 'departure', '') if getattr(ac, 'departure', '') else '--:--'
        orig = getattr(ac, 'origin', '') if getattr(ac, 'origin', '') else 'NIGHT'
        dest = getattr(ac, 'destination', '') if getattr(ac, 'destination', '') else 'STAY'
        flights_listbox.insert(tk.END,
                               f"{ac.id}  |  Orig: {orig}->{dest}  |  Arr: {arr_time} Dep: {dep_time}  |  {ac.airline}")


# ================== FUNCIONS V3 & V4 (PUERTAS) ==================

def load_structure():
    global bcn
    filepath = filedialog.askopenfilename(
        title="Selecciona el fitxer LEBL.txt",
        filetypes=[("Text files", "*.txt")]
    )
    if filepath:
        bcn = LoadAirportStructure(filepath)
        if bcn == -1:
            bcn = None
            messagebox.showerror("Error", "No s'ha pogut carregar el fitxer")
        else:
            messagebox.showinfo("OK",
                                f"Aeroport {bcn.code} carregat correctament. Recorda assignar primer els Night Gates.")


def assign_night_gates_v4():
    """NUEVO V4: Ejecuta la función estricta para colocar los aviones estacionados que inician el día"""
    global bcn, aircrafts
    if bcn is None:
        messagebox.showerror("Error V4", "Carrega primer l'estructura de l'aeroport.")
        return
    if not aircrafts:
        messagebox.showerror("Error V4", "No hi ha llista de vols unificada per extreure els avions nocturnos.")
        return

    result = AssignNightGates(bcn, aircrafts)
    if result == -1:
        messagebox.showerror("Error V4", "Error al processar la llista de portes nocturnes.")
        return
    messagebox.showinfo("Night Gates OK", f"S'han establert {result} portes inicials per a vols nocturns de sortida.")


def assign_gates():
    """Se mantiene la compatibilidad V3 original solicitada por la rúbrica"""
    if bcn is None:
        messagebox.showerror("Error", "Carrega primer l'estructura de l'aeroport")
        return
    if not aircrafts:
        messagebox.showerror("Error", "No hi ha vols carregats — carrega'ls a la pestanya Vols")
        return
    assigned = 0
    for ac in aircrafts:
        result = AssignGate(bcn, ac)
        if result != -1:
            assigned += 1
    messagebox.showinfo("OK", f"Gates assignats (Estàtic V3): {assigned} de {len(aircrafts)} vols")


def assign_gates_at_time_v4():
    """NUEVO V4: Llama a la simulación dinámica por franja de 1 hora según la hora del Combobox"""
    global bcn, aircrafts
    if bcn is None:
        messagebox.showerror("Error V4", "Carrega l'estructura de l'aeroport primer.")
        return
    if not aircrafts:
        messagebox.showerror("Error V4", "No s'han preparat vols a la memòria.")
        return

    selected_hour = combo_hours.get()
    unassigned = AssignGatesAtTime(bcn, aircrafts, selected_hour)
    messagebox.showinfo("Simulació Horària",
                        f"Franja {selected_hour} processada amb èxit.\nVols rebutjats per falta d'espai en aquesta hora: {unassigned}")


def plot_day_occupancy_v4():
    """NUEVO V4: Llama al renderizado gráfico requerido de simulación de todo el día de matplotlib"""
    global bcn, aircrafts
    if bcn is None:
        messagebox.showerror("Error V4", "Estructura de l'aeroport necessària.")
        return
    if not aircrafts:
        messagebox.showerror("Error V4", "S'han de carregar moviments.")
        return
    PlotDayOccupancy(bcn, aircrafts)


def show_occupancy():
    if bcn is None:
        messagebox.showerror("Error", "No hi ha cap aeroport carregat")
        return
    occ = GateOccupancy(bcn)
    win = tk.Toplevel(root)
    win.title(f"Ocupacio de portes — {bcn.code}")
    win.geometry("540x450")
    win.configure(bg=COLORS["bg"])
    styled_label(win, f"Total gates: {len(occ)}", size=11, bold=True).pack(pady=8)
    frame = tk.Frame(win, bg=COLORS["bg"])
    frame.pack(fill="both", expand=True, padx=12, pady=4)
    lb = tk.Listbox(frame,
                    bg=COLORS["entry_bg"], fg=COLORS["text"],
                    font=("Courier New", 10), relief="flat",
                    selectbackground=COLORS["accent"], selectforeground="white")
    sb = tk.Scrollbar(frame, orient="vertical", command=lb.yview)
    lb.configure(yscrollcommand=sb.set)
    lb.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    for g in occ:
        # Actualización V4 estricta que visualiza la hora límite de despegue ('until') solicitada
        until_time = g.get('until', '--:--')
        status = f"OCUPAT ✈️ {g['aircraft']} fins les {until_time}" if g['occupied'] else "FREE 🟢 lliure"
        lb.insert(tk.END, f"{g['gate']:20s}  {status}")


# ================== TAB 1 — AEROPORTS ==================

styled_label(tab1, "  Gestión de Aeropuertos", size=15, bold=True).pack(pady=(18, 8))

frame_form = tk.Frame(tab1, bg=COLORS["card"], padx=20, pady=15)
frame_form.pack(padx=20, fill="x")

styled_label(frame_form, "Código ICAO", size=11, bold=True, bg=COLORS["card"]).grid(row=0, column=0, sticky="w", pady=6)
entry_icao = styled_entry(frame_form)
entry_icao.grid(row=0, column=1, sticky="ew", padx=(12, 0), pady=6)

styled_label(frame_form, "Latitud", size=11, bold=True, bg=COLORS["card"]).grid(row=1, column=0, sticky="w", pady=6)
entry_lat = styled_entry(frame_form)
entry_lat.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=6)

styled_label(frame_form, "Longitud", size=11, bold=True, bg=COLORS["card"]).grid(row=2, column=0, sticky="w", pady=6)
entry_lon = styled_entry(frame_form)
entry_lon.grid(row=2, column=1, sticky="ew", padx=(12, 0), pady=6)

frame_form.columnconfigure(1, weight=1)

frame_btns1 = tk.Frame(tab1, bg=COLORS["bg"])
frame_btns1.pack(pady=10)

styled_button(frame_btns1, "Añadir", add_airport, COLORS["accent2"]).grid(row=0, column=0, padx=5, pady=4)
styled_button(frame_btns1, "Eliminar", remove_airport, COLORS["accent2"]).grid(row=0, column=1, padx=5, pady=4)
styled_button(frame_btns1, "Cargar", load_airports, COLORS["accent2"]).grid(row=0, column=2, padx=5, pady=4)
styled_button(frame_btns1, "Guardar Schengen", save_schengen, COLORS["accent2"]).grid(row=1, column=0, padx=5, pady=4)
styled_button(frame_btns1, "Gráfico", plot_airports_chart, COLORS["accent2"]).grid(row=1, column=1, padx=5, pady=4)
styled_button(frame_btns1, "Google Earth", map_airports_kml, COLORS["accent2"]).grid(row=1, column=2, padx=5, pady=4)

frame_list1 = tk.Frame(tab1, bg=COLORS["bg"])
frame_list1.pack(fill="both", expand=True, padx=20, pady=(4, 12))

airports_listbox = tk.Listbox(frame_list1,
                              bg=COLORS["entry_bg"], fg=COLORS["text"],
                              font=("Courier New", 10), relief="flat",
                              selectbackground=COLORS["accent"], selectforeground="white")
sb_ap = tk.Scrollbar(frame_list1, orient="vertical", command=airports_listbox.yview)
airports_listbox.configure(yscrollcommand=sb_ap.set)
airports_listbox.pack(side="left", fill="both", expand=True)
sb_ap.pack(side="right", fill="y")

# ================== TAB 2 — VOLS ==================

styled_label(tab2, "  Gestión de Vuelos & Movimientos", size=15, bold=True).pack(pady=(18, 8))

frame_btns2 = tk.Frame(tab2, bg=COLORS["bg"])
frame_btns2.pack(pady=5)

# Fila 0: Cargas Obligatorias de Movimientos
styled_button(frame_btns2, "1. Cargar arribades", load_arrivals, COLORS["accent2"]).grid(row=0, column=0, padx=5,
                                                                                         pady=4)
styled_button(frame_btns2, "2. Cargar sortides", load_departures_v4, COLORS["accent"]).grid(row=0, column=1, padx=5,
                                                                                            pady=4)
styled_button(frame_btns2, "3. Fusionar (Merge)", merge_movements_v4, COLORS["accent"]).grid(row=0, column=2, padx=5,
                                                                                             pady=4)

# Fila 1: Filtros y persistencia
styled_button(frame_btns2, "Filtrar Nocturnos", show_night_aircraft_v4, COLORS["accent"]).grid(row=1, column=0, padx=5,
                                                                                               pady=4)
styled_button(frame_btns2, "Guardar vuelos", save_flights, COLORS["accent2"]).grid(row=1, column=1, padx=5, pady=4)
styled_button(frame_btns2, "Refrescar todo", refresh_flights_list, COLORS["accent2"]).grid(row=1, column=2, padx=5,
                                                                                           pady=4)

# Fila 2: Gráficos Estadísticos heredados
styled_button(frame_btns2, "Gráfico por hora", plot_arrivals_chart, COLORS["accent2"]).grid(row=2, column=0, padx=5,
                                                                                            pady=4)
styled_button(frame_btns2, "Gráfico aerolíneas", plot_airlines_chart, COLORS["accent2"]).grid(row=2, column=1, padx=5,
                                                                                              pady=4)
styled_button(frame_btns2, "Gráfico Schengen", plot_flights_type_chart, COLORS["accent2"]).grid(row=2, column=2, padx=5,
                                                                                                pady=4)

# Fila 3: Geo-posicionamiento y distancias
styled_button(frame_btns2, "Google Earth KML", map_flights_kml, COLORS["accent2"]).grid(row=3, column=0, padx=5, pady=4)
styled_button(frame_btns2, "Larga distancia", map_long_distance_kml, COLORS["accent2"]).grid(row=3, column=1,
                                                                                             columnspan=2, sticky="ew",
                                                                                             padx=5, pady=4)

frame_list2 = tk.Frame(tab2, bg=COLORS["bg"])
frame_list2.pack(fill="both", expand=True, padx=20, pady=(4, 12))

flights_listbox = tk.Listbox(frame_list2,
                             bg=COLORS["entry_bg"], fg=COLORS["text"],
                             font=("Courier New", 10), relief="flat",
                             selectbackground=COLORS["accent"], selectforeground="white")
sb_fl = tk.Scrollbar(frame_list2, orient="vertical", command=flights_listbox.yview)
flights_listbox.configure(yscrollcommand=sb_fl.set)
flights_listbox.pack(side="left", fill="both", expand=True)
sb_fl.pack(side="right", fill="y")

# ================== TAB 3 — PORTES ==================

styled_label(tab3, "  Gestión de Puertas de Embarque (V4)", size=15, bold=True).pack(pady=(18, 8))

frame_btns3 = tk.Frame(tab3, bg=COLORS["bg"])
frame_btns3.pack(pady=10)

# Controles estructurales base e inicialización de pernocta
styled_button(frame_btns3, "1. Cargar estructura aeropuerto", load_structure, COLORS["accent2"]).pack(fill="x", pady=4)
styled_button(frame_btns3, "2. Asignar Gates Nocturnos (Night)", assign_night_gates_v4, COLORS["accent"]).pack(fill="x",
                                                                                                               pady=4)

# Contenedor interactivo para simulación horaria en pasos discretos
frame_time_sim = tk.LabelFrame(tab3, text=" Simulación Dinámica por Horas ", bg=COLORS["bg"], fg=COLORS["text"],
                               font=("Georgia", 10, "italic"), padx=10, pady=10)
frame_time_sim.pack(fill="x", padx=40, pady=12)

styled_label(frame_time_sim, "Selecciona hora de simulación:", bg=COLORS["bg"]).pack(side="left", padx=5)

# Generación del string de horas formateado solicitado en la especificación
hours_values = [f"{str(h).zfill(2)}:00" for h in range(24)]
combo_hours = ttk.Combobox(frame_time_sim, values=hours_values, state="readonly", width=8, font=("Georgia", 11))
combo_hours.set("08:00")
combo_hours.pack(side="left", padx=10)

styled_button(frame_time_sim, "Procesar hora", assign_gates_at_time_v4, COLORS["accent"]).pack(side="left", padx=5)

# Controles de salida gráfica totalizadora y visualización
styled_button(tab3, "Plot Day Occupancy (Día Completo)", plot_day_occupancy_v4, COLORS["accent"]).pack(fill="x",
                                                                                                         padx=40,
                                                                                                         pady=4)
styled_button(tab3, "Asignación Estática (Modo V3)", assign_gates, COLORS["accent2"]).pack(fill="x", padx=40, pady=4)
styled_button(tab3, "Mostrar ocupación actual de puertas", show_occupancy, COLORS["accent2"]).pack(fill="x", padx=40,
                                                                                                     pady=8)

# ==================
root.mainloop()
