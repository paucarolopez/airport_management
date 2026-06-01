import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from collections import Counter
from datetime import datetime
import copy

# =====================================================================
# IMPORTACIONES DE TUS MÓDULOS PROPIOS (MANTENIENDO TUS NOMBRES EXACTOS)
# =====================================================================
from airport import (Airport, AddAirport, RemoveAirport, LoadAirports,
                     SaveSchengenAirports, PlotAirports, MapAirports, IsSchengenAirport)

from aircraft import (Aircraft, LoadArrivals, SaveFlights, PlotArrivals,
                      PlotAirlines, PlotFlightsType, MapFlights, LongDistanceArrivals)

from LEBL import (LoadAirportStructure, AssignNightGates, AssignGatesAtTime,
                  PlotDayOccupancy, MergeMovements, NightAircraft, LoadDepartures)

# =====================================================================
# CONFIGURACIÓN DE LA VENTANA PRINCIPAL
# =====================================================================
root = tk.Tk()
root.title("AeroManager Flight & Gate Control Suite")
root.geometry("1180x880")
root.minsize(1050, 780)

# Paleta de colores profesional corporativa (Slate Dark)
COLORS = {
    "bg_main": "#0b1329",
    "bg_sidebar": "#1c2541",
    "bg_card": "#222e50",
    "accent": "#4f46e5",
    "accent_sub": "#3b82f6",
    "success": "#10b981",
    "danger": "#f43f5e",
    "text_main": "#f8fafc",
    "text_muted": "#94a3b8",
    "input_bg": "#1e293b"
}

root.configure(bg=COLORS["bg_main"])

# Estilos unificados para componentes de Tkinter (Notebooks y tablas Treeview)
style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background=COLORS["bg_main"], borderwidth=0, highlightthickness=0)
style.configure("TNotebook.Tab", background=COLORS["bg_sidebar"], foreground=COLORS["text_muted"], padding=[22, 10],
                font=("Segoe UI", 10, "bold"), borderwidth=0)
style.map("TNotebook.Tab", background=[("selected", COLORS["accent"])], foreground=[("selected", "#ffffff")])
style.configure("Treeview", background=COLORS["bg_card"], fieldbackground=COLORS["bg_card"],
                foreground=COLORS["text_main"], rowheight=28, font=("Segoe UI", 10), borderwidth=0,
                highlightthickness=0)
style.configure("Treeview.Heading", background=COLORS["bg_sidebar"], foreground=COLORS["text_main"],
                font=("Segoe UI", 10, "bold"), borderwidth=1, relief="flat")
style.map("Treeview", background=[("selected", COLORS["accent"])])
style.configure("TCombobox", fieldbackground=COLORS["input_bg"], background=COLORS["bg_card"],
                foreground=COLORS["text_main"])

# =====================================================================
# VARIABLES GLOBALES DE ALMACENAMIENTO DE DATOS
# =====================================================================
airports = []  # Contenedor de objetos Airport
bcn = None  # Estructura física BarcelonaAP cargada desde LEBL.txt
aircrafts = []  # Lista global unificada/operativa de objetos Aircraft
arrivals_raw = []  # Lista base de llegadas
departures_raw = []  # Lista base de salidas


# =====================================================================
# COMPONENTES AUXILIARES DE DISEÑO (ESTILO Y HOVER)
# =====================================================================
def get_hover_color(color_hex):
    hover_map = {COLORS["accent"]: "#6366f1", COLORS["success"]: "#34d399", COLORS["danger"]: "#fb7185",
                 COLORS["accent_sub"]: "#60a5fa"}
    return hover_map.get(color_hex, color_hex)


def create_button(parent, text, command, bg_color=COLORS["accent"]):
    btn = tk.Button(parent, text=text, command=command, bg=bg_color, fg="white", font=("Segoe UI", 9, "bold"),
                    relief="flat", bd=0, padx=14, pady=9, cursor="hand2", activebackground=get_hover_color(bg_color),
                    activeforeground="white")
    btn.bind("<Enter>", lambda e: btn.config(background=get_hover_color(bg_color)))
    btn.bind("<Leave>", lambda e: btn.config(background=bg_color))
    return btn


def create_header(parent, title, subtitle):
    frame = tk.Frame(parent, bg=parent.cget("bg"), pady=10)
    lbl_title = tk.Label(frame, text=title, bg=frame.cget("bg"), fg=COLORS["text_main"], font=("Segoe UI", 16, "bold"))
    lbl_title.pack(anchor="w")
    lbl_sub = tk.Label(frame, text=subtitle, bg=frame.cget("bg"), fg=COLORS["text_muted"], font=("Segoe UI", 9))
    lbl_sub.pack(anchor="w", pady=(2, 0))
    return frame


# =====================================================================
# CONSTRUCCIÓN DE LA INTERFAZ (DECLARACIÓN TEMPRANA DE COMPONENTES V4)
# =====================================================================
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=20, pady=20)

tab0 = tk.Frame(notebook, bg=COLORS["bg_main"])
tab1 = tk.Frame(notebook, bg=COLORS["bg_main"])
tab2 = tk.Frame(notebook, bg=COLORS["bg_main"])
tab3 = tk.Frame(notebook, bg=COLORS["bg_main"])

notebook.add(tab0, text="  Main tab  ")
notebook.add(tab1, text="  Airport  ")
notebook.add(tab2, text="  Aircraft  ")
notebook.add(tab3, text="  LEBL  ")

# --- ELEMENTOS DE LA PESTAÑA 0: DASHBOARD ---
create_header(tab0, "Data Summary",
              "Real-time metrics").pack(anchor="w", padx=30,
                                                                                                   pady=20)
kpi_container = tk.Frame(tab0, bg=COLORS["bg_main"])
kpi_container.pack(fill="x", padx=30, pady=15)

# Registro de las etiquetas de KPI para que existan globalmente desde el inicio
card_tot = tk.Frame(kpi_container, bg=COLORS["bg_sidebar"], padx=20, pady=20, bd=1, relief="solid")
card_tot.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
tk.Label(card_tot, text="AMOUNT OF MOVEMENTS", bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"],
         font=("Segoe UI", 9, "bold")).pack(anchor="w")
lbl_kpi_total_val = tk.Label(card_tot, text="0", bg=COLORS["bg_sidebar"], fg=COLORS["accent_sub"],
                             font=("Segoe UI", 28, "bold"))
lbl_kpi_total_val.pack(anchor="w", pady=(8, 0))

card_line = tk.Frame(kpi_container, bg=COLORS["bg_sidebar"], padx=20, pady=20, bd=1, relief="solid")
card_line.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
tk.Label(card_line, text="MOST USED COMPANY", bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"],
         font=("Segoe UI", 9, "bold")).pack(anchor="w")
lbl_kpi_line_val = tk.Label(card_line, text="N/A", bg=COLORS["bg_sidebar"], fg=COLORS["success"],
                            font=("Segoe UI", 24, "bold"))
lbl_kpi_line_val.pack(anchor="w", pady=(8, 0))

card_rut = tk.Frame(kpi_container, bg=COLORS["bg_sidebar"], padx=20, pady=20, bd=1, relief="solid")
card_rut.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
tk.Label(card_rut, text="CONNECTED NODES", bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"],
         font=("Segoe UI", 9, "bold")).pack(anchor="w")
lbl_kpi_routes_val = tk.Label(card_rut, text="0", bg=COLORS["bg_sidebar"], fg=COLORS["danger"],
                              font=("Segoe UI", 28, "bold"))
lbl_kpi_routes_val.pack(anchor="w", pady=(8, 0))

kpi_container.columnconfigure((0, 1, 2), weight=1)

welcome_card = tk.Frame(tab0, bg=COLORS["bg_card"], padx=25, pady=25)
welcome_card.pack(fill="x", padx=30, pady=30)
tk.Label(welcome_card, text="Real-Time Terminal", bg=COLORS["bg_card"], fg=COLORS["text_main"],
         font=("Segoe UI", 12, "bold")).pack(anchor="w")
tk.Label(welcome_card,
         text="Use the top tabs to load the physical airport database, dock arrival/departure diagrams, or run ramp simulations.",
         bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 0))

# --- ELEMENTOS DE LA PESTAÑA 1: INFRAESTRUCTURA ---
create_header(tab1, "Airport Infrastructure Database",
              "Administration of geographical coordinates and Schengen control.").pack(anchor="w", padx=20, pady=15)
ap_workspace = tk.Frame(tab1, bg=COLORS["bg_main"])
ap_workspace.pack(fill="both", expand=True, padx=20)
form_card = tk.Frame(ap_workspace, bg=COLORS["bg_sidebar"], padx=20, pady=20, width=300)
form_card.pack(side="left", fill="y", pady=5)
form_card.pack_propagate(False)

tk.Label(form_card, text="REGISTER NEW NODE", bg=COLORS["bg_sidebar"], fg=COLORS["text_main"],
         font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 15))

# Instanciación explícita de las entradas de texto requeridas antes de llamar a funciones
tk.Label(form_card, text="ICAO code", bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"], font=("Segoe UI", 9)).pack(
    anchor="w", pady=(8, 2))
entry_icao = tk.Entry(form_card, bg=COLORS["input_bg"], fg=COLORS["text_main"], font=("Segoe UI", 10), relief="flat",
                      insertbackground="white", bd=5)
entry_icao.pack(fill="x")

tk.Label(form_card, text="Latitude (Decimal)", bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"],
         font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 2))
entry_lat = tk.Entry(form_card, bg=COLORS["input_bg"], fg=COLORS["text_main"], font=("Segoe UI", 10), relief="flat",
                     insertbackground="white", bd=5)
entry_lat.pack(fill="x")

tk.Label(form_card, text="Longitude (Decimal)", bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"],
         font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 2))
entry_lon = tk.Entry(form_card, bg=COLORS["input_bg"], fg=COLORS["text_main"], font=("Segoe UI", 10), relief="flat",
                     insertbackground="white", bd=5)
entry_lon.pack(fill="x")

# --- ELEMENTOS DE LA PESTAÑA 2: REGISTRO VUELOS ---
create_header(tab2, "Technical Panel for Flight Movements and Registration",
              "Consolidation of flight operations and statistical analysis.").pack(anchor="w", padx=20, pady=15)
fl_workspace = tk.Frame(tab2, bg=COLORS["bg_main"])
fl_workspace.pack(fill="both", expand=True, padx=20)
fl_actions = tk.Frame(fl_workspace, bg=COLORS["bg_sidebar"], padx=15, pady=15)
fl_actions.pack(fill="x", pady=5)

search_bar_frame = tk.Frame(fl_workspace, bg=COLORS["bg_sidebar"], padx=15, pady=10)
search_bar_frame.pack(fill="x", pady=(15, 0))
tk.Label(search_bar_frame, text="Dynamic Search", bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"],
         font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
entry_search = tk.Entry(search_bar_frame, bg=COLORS["input_bg"], fg=COLORS["text_main"], font=("Segoe UI", 10),
                        relief="flat", insertbackground="white", width=30)
entry_search.pack(side="left", padx=5, ipady=3)

combo_filter_type = ttk.Combobox(search_bar_frame,
                                 values=["All", "ID", "Airline", "Route (Orig/Dest)"],
                                 state="readonly", width=18, font=("Segoe UI", 9, "bold"))
combo_filter_type.set("All")
combo_filter_type.pack(side="left", padx=5)

fl_table_card = tk.Frame(fl_workspace, bg=COLORS["bg_card"], padx=15, pady=15)
fl_table_card.pack(fill="both", expand=True, pady=(15, 10))
table_flights = ttk.Treeview(fl_table_card, columns=("id", "orig", "dest", "arr", "dep", "line"), show="headings")
for c, t in [("id", "INDICATIVE"), ("orig", "ORIGIN"), ("dest", "DESTINY"), ("arr", "H. ARRAIVAL"), ("dep", "H. DEPARTURE"),
             ("line", "AIRLINE")]: table_flights.heading(c, text=t)
table_flights.pack(side="left", fill="both", expand=True)
sb_fl = tk.Scrollbar(fl_table_card, orient="vertical", command=table_flights.yview)
table_flights.configure(yscrollcommand=sb_fl.set)
sb_fl.pack(side="right", fill="y")

# --- ELEMENTOS DE LA PESTAÑA 3: ASIGNACIÓN DE PUERTAS (LEBL) ---
create_header(tab3, "Gate Assignment and Tactical Ramp Simulation.",
              "Interactive allocation by time slots and saturation control.").pack(anchor="w", padx=20, pady=15)
ops_workspace = tk.Frame(tab3, bg=COLORS["bg_main"])
ops_workspace.pack(fill="both", expand=True, padx=20)

card_resources = tk.Frame(ops_workspace, bg=COLORS["bg_sidebar"], padx=20, pady=14)
card_resources.pack(fill="x", pady=4)
tk.Label(card_resources, text="1. PHYSICAL CONTROL OF DOORS AND ENVIRONMENT", bg=COLORS["bg_sidebar"], fg=COLORS["text_main"],
         font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 10))

card_simulation = tk.Frame(ops_workspace, bg=COLORS["bg_sidebar"], padx=20, pady=15)
card_simulation.pack(fill="x", pady=10)
tk.Label(card_simulation, text="2. EXECUTION OF DYNAMIC SIMULATION BY INTERVALS", bg=COLORS["bg_sidebar"],
         fg=COLORS["text_main"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 10))
control_row = tk.Frame(card_simulation, bg=COLORS["bg_sidebar"])
control_row.pack(fill="x")
tk.Label(control_row, text="Select Time Slot:", bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"],
         font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
hours_list = [f"{str(h).zfill(2)}:00" for h in range(24)]
combo_hours = ttk.Combobox(control_row, values=hours_list, state="readonly", width=12, font=("Segoe UI", 10, "bold"))
combo_hours.set("12:00")
combo_hours.pack(side="left", padx=10)

card_analytics = tk.Frame(ops_workspace, bg=COLORS["bg_main"])
card_analytics.pack(fill="x", pady=4)

alert_frame = tk.LabelFrame(ops_workspace, text=" ⚠️ CONTINGENCY, SATURATION AND TACTICAL ALERTS MONITOR ",
                            bg=COLORS["bg_sidebar"], fg=COLORS["danger"], font=("Segoe UI", 10, "bold"), padx=15,
                            pady=15)
alert_frame.pack(fill="both", expand=True, pady=(15, 5))
table_alerts = ttk.Treeview(alert_frame, columns=("type", "msg"), show="headings", height=4)
table_alerts.heading("type", text="SEVERITY")
table_alerts.heading("msg", text="ANOMALY DETECTED ON PLATFORM")
table_alerts.column("type", width=140, minwidth=100, stretch=False)
table_alerts.column("msg", width=600, minwidth=300, stretch=True)
table_alerts.pack(side="left", fill="both", expand=True)
sb_al = tk.Scrollbar(alert_frame, orient="vertical", command=table_alerts.yview)
table_alerts.configure(yscrollcommand=sb_al.set)
sb_al.pack(side="right", fill="y")
table_alerts.insert("", "end", values=("NOMINAL", "Waiting for time simulation for security scanning."))


# =====================================================================
# BLOQUE DE LOGÍSTICA DE COMPORTAMIENTO Y LOGÍSTICA BACKEND (ABAJO)
# =====================================================================
def update_dashboard_kpis():
    """Actualiza las tarjetas analíticas de la pestaña principal."""
    if not aircrafts:
        lbl_kpi_total_val.config(text="0")
        lbl_kpi_line_val.config(text="N/A")
        lbl_kpi_routes_val.config(text="0")
        return
    lbl_kpi_total_val.config(text=str(len(aircrafts)))
    airlines_list = [ac.airline for ac in aircrafts if getattr(ac, 'airline', None)]
    if airlines_list:
        most_common_airline, count = Counter(airlines_list).most_common(1)[0]
        lbl_kpi_line_val.config(text=f"{most_common_airline} ({count} ops)")
    else:
        lbl_kpi_line_val.config(text="N/A")

    routes = set()
    for ac in aircrafts:
        orig = getattr(ac, 'origin', "")
        dest = getattr(ac, 'destination', "")
        if orig and orig.strip() != "": routes.add(orig)
        if dest and dest.strip() != "": routes.add(dest)
    lbl_kpi_routes_val.config(text=str(len(routes)))


def add_airport():
    icao = entry_icao.get().upper().strip()

    # Intento de conversión inicial de coordenadas
    try:
        lat, lon = float(entry_lat.get()), float(entry_lon.get())
    except ValueError:
        messagebox.showerror("Format Error",
                             "Coordinates must be valid numeric values (e.g., 41.30 and 2.07).")
        return

    # Crear objeto temporal para validar
    new_ap = Airport(icao, lat, lon)
    new_ap.schengen = IsSchengenAirport(icao)

    # Ejecutar alta con validación estricta de backend
    resultado = AddAirport(airports, new_ap)

    if resultado == "ERROR_ICAO":
        messagebox.showerror("Failed Validation",
                             "The ICAO code is not valid.\nIt must consist of exactly 4 letters (no numbers or symbols).")
    elif resultado == "ERROR_LAT":
        messagebox.showerror("Failed Validation",
                             "The entered latitude is out of range. \nIt must be a value between -90 and 90 degrees.")
    elif resultado == "ERROR_LON":
        messagebox.showerror("Failed Validation",
                             "The entered longitude is out of range. \nIt must be a value between -180 and 180 degrees.")
    elif resultado == "ERROR_DUPLICADO":
        messagebox.showwarning("Duplicate Registration", f"The airport with ICAO [{icao}] already exist in the database.")
    elif resultado == "OK":
        refresh_airports_table()
        update_dashboard_kpis()
        messagebox.showinfo("Success", f"Airport [{icao}] verified and registered on the global infrastructure.")

        # Limpiar los campos del formulario tras el éxito
        entry_icao.delete(0, tk.END)
        entry_lat.delete(0, tk.END)
        entry_lon.delete(0, tk.END)


def remove_airport():
    code = entry_icao.get().upper().strip()
    if not code: return
    if RemoveAirport(airports, code) == -1:
        messagebox.showerror("Error", f"Node not found [{code}].")
    else:
        refresh_airports_table()
        messagebox.showinfo("Success", f"Node [{code}] removed from the current infrastructure.")


def load_airports_file():
    path = filedialog.askopenfilename(filetypes=[("Data files", "*.txt")])
    if not path: return
    global airports
    airports = LoadAirports(path)
    refresh_airports_table()


def save_schengen_file():
    if not airports: return
    path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if path:
        SaveSchengenAirports(airports, path)
        messagebox.showinfo("Export", "Schengen file saved successfully.")


def refresh_airports_table():
    for item in table_airports.get_children(): table_airports.delete(item)
    for idx, ap in enumerate(airports):
        zone = "Schengen" if ap.schengen else "International"
        table_airports.insert("", "end", iid=idx, values=(ap.code, f"{ap.lat:.4f}", f"{ap.lon:.4f}", zone))


def call_plot_airports():
    if not airports:
        messagebox.showwarning("Warning", "No airport data loaded.")
        return
    try:
        PlotAirports(airports)
    except Exception as e:
        messagebox.showerror("Graphic Error", f"Airports could not be graphed: {str(e)}")


def call_map_airports():
    if not airports: return
    MapAirports(airports)
    messagebox.showinfo("KML", "The 'airports.kml' file was successfully generated in the root directory.")


def load_arrivals_file():
    path = filedialog.askopenfilename(filetypes=[("Data files", "*.txt")])
    if not path: return
    global arrivals_raw, aircrafts
    arrivals_raw = LoadArrivals(path)
    aircrafts = arrivals_raw
    refresh_flights_table()
    update_dashboard_kpis()


def load_departures_file():
    path = filedialog.askopenfilename(filetypes=[("Data files", "*.txt")])
    if not path: return
    global departures_raw
    deps, err = LoadDepartures(path)
    if err == -1:
        messagebox.showerror("Error", "Invalid output or file not found.")
    else:
        departures_raw = deps
        messagebox.showinfo("Success", f"Loaded {len(departures_raw)} departures.")
        update_dashboard_kpis()


def execute_merge():
    global aircrafts
    if not arrivals_raw or not departures_raw:
        messagebox.showwarning("Data is missing",
                               "Load the Arrivals and Departures first in order to merge the movements.")
        return
    res = MergeMovements(arrivals_raw, departures_raw)
    if res != -1:
        aircrafts = res
        refresh_flights_table()
        update_dashboard_kpis()
        messagebox.showinfo("Logistics", "Movements and scales successfully unified.")


def filter_pernoctas():
    global aircrafts
    if not aircrafts: return
    night_list = NightAircraft(aircrafts)
    if night_list == -1 or not night_list:
        messagebox.showinfo("Information", "No pure night aircraft were detected in the current records.")
        return
    for item in table_flights.get_children(): table_flights.delete(item)
    for idx, ac in enumerate(night_list):
        dest = getattr(ac, 'destination', '-')
        dep = getattr(ac, 'departure', '--:--')
        table_flights.insert("", "end", iid=idx, values=(ac.id, "Overnight (Base)", dest, "--:--", dep, ac.airline))


def refresh_flights_table():
    for item in table_flights.get_children(): table_flights.delete(item)
    query = entry_search.get().upper().strip()
    filter_mode = combo_filter_type.get()

    for idx, ac in enumerate(aircrafts):
        arr = getattr(ac, 'arrival', '') or '--:--'
        dep = getattr(ac, 'departure', '') or '--:--'
        orig = getattr(ac, 'origin', '') or 'Overnight'
        dest = getattr(ac, 'destination', '') or 'Stay'
        line = ac.airline.upper() if ac.airline else '-'
        plane_id = ac.id.upper() if ac.id else '-'

        if query:
            if filter_mode == "Indicative / ID" and query not in plane_id:
                continue
            elif filter_mode == "Airline" and query not in line:
                continue
            elif filter_mode == "Route (Orig/Dest)" and (query not in orig.upper() and query not in dest.upper()):
                continue
            elif filter_mode == "All" and (
                    query not in plane_id and query not in line and query not in orig.upper() and query not in dest.upper()):
                continue

        table_flights.insert("", "end", iid=idx, values=(plane_id, orig, dest, arr, dep, line))


def call_plot_arrivals():
    global aircrafts
    if not aircrafts:
        messagebox.showwarning("No data", "Import and merge the flights in the console before graphing.")
        return

    for ac in aircrafts:
        arr_time = str(getattr(ac, 'arrival', '')).strip()
        if not arr_time or ":" not in arr_time:
            ac.arrival = "00:00"
        else:
            parts = arr_time.split(":")
            if not parts[0].strip().isdigit():
                ac.arrival = "00:00"

    try:
        PlotArrivals(aircrafts)
    except Exception as e:
        messagebox.showerror("Backend error", f"Failure to process time charts: {str(e)}")


def call_plot_airlines():
    global aircrafts
    if not aircrafts: return
    try:
        PlotAirlines(aircrafts)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def call_plot_types():
    global aircrafts
    if not aircrafts: return
    try:
        PlotFlightsType(aircrafts)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def call_map_kml():
    global aircrafts
    if not aircrafts: return
    try:
        MapFlights(aircrafts)
        messagebox.showinfo("KML", "'flights.kml' file successfully generated.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def call_long_distance_kml():
    global aircrafts
    if not aircrafts: return
    try:
        res = LongDistanceArrivals(aircrafts)
        messagebox.showinfo("Distance Filter", f"There have been detected {len(res)} transcontinental arrivals (> 2000 km).")
    except Exception as e:
        messagebox.showerror("Error", f"Error in Haversine distance calculation: {str(e)}")


def load_airport_structure():
    global bcn
    path = filedialog.askopenfilename(filetypes=[("Structure files", "*.txt")])
    if path:
        bcn = LoadAirportStructure(path)
        if bcn == -1:
            messagebox.showerror("Error", "The physical structure of the airport could not be processed.")
            bcn = None
        else:
            messagebox.showinfo("Infrastructure", f"Aeronautical structure loaded for [{bcn.code}].")


def process_night_gates():
    if bcn and aircrafts:
        res = AssignNightGates(bcn, aircrafts)
        messagebox.showinfo("Night Assignment", f"{res} aircraft have positioned themselves for overnight stays.")
        scan_and_render_conflicts(None)


def process_hourly_simulation():
    if bcn and aircrafts:
        h = combo_hours.get()
        result = AssignGatesAtTime(bcn, aircrafts, h)
        messagebox.showinfo("Time Simulation", f"Time slot {h} completed.")
        scan_and_render_conflicts(result)


def scan_and_render_conflicts(raw_result):
    for item in table_alerts.get_children():
        table_alerts.delete(item)

    alerts_found = 0
    current_hour = combo_hours.get()

    if isinstance(raw_result, int) and raw_result > 0:
        alerts_found += raw_result
        for _ in range(raw_result):
            table_alerts.insert("", "end", values=("CRITICAL",
                                                   f"Aircraft DENIED in slot {current_hour} due to lack of space in terminal."))

    if bcn and aircrafts:
        selected_hour_int = int(current_hour.split(":")[0])
        for ac in aircrafts:
            arr_time = getattr(ac, 'arrival', '')
            dep_time = getattr(ac, 'departure', '')
            is_active_now = False

            if arr_time and ":" in str(arr_time) and arr_time.split(":")[0].strip().isdigit():
                if int(arr_time.split(":")[0]) == selected_hour_int: is_active_now = True
            if dep_time and ":" in str(dep_time) and dep_time.split(":")[0].strip().isdigit():
                if int(dep_time.split(":")[0]) == selected_hour_int: is_active_now = True

            if is_active_now:
                found_in_bcn = False
                for t in bcn.terminals:
                    for area in t.areas:
                        for gate in area.gates:
                            if gate.occupied and gate.aircraft_id == ac.id:
                                found_in_bcn = True
                if not found_in_bcn:
                    alerts_found += 1
                    table_alerts.insert("", "end", values=("WARNING",
                                                           f"Flight {ac.id} ({ac.airline}) operating without a secure gateway in slot {current_hour}."))

    if alerts_found == 0:
        table_alerts.insert("", "end", values=("NOMINAL",
                                               f"Smooth operation for the {current_hour} time slot. Zero platform conflicts."))


def export_operations_briefing():
    # Validación previa de seguridad para evitar archivos corruptos o vacíos
    if not bcn:
        messagebox.showerror("Export Error",
                             "You must load the airport's physical structure (LEBL.txt or equivalent) in Tab 3 before generating the report.")
        return

    path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Report", "*.txt")],
                                        initialfile=f"Briefing_Operativo_{bcn.code}.txt")
    if not path: return

    try:
        # 1. Conteo seguro de infraestructura física
        total_gates = 0
        occupied_gates = 0
        if hasattr(bcn, 'terminals') and bcn.terminals:
            for t in bcn.terminals:
                if hasattr(t, 'areas') and t.areas:
                    for area in t.areas:
                        if hasattr(area, 'gates') and area.gates:
                            for gate in area.gates:
                                total_gates += 1
                                if getattr(gate, 'occupied', False):
                                    occupied_gates += 1
        free_gates = total_gates - occupied_gates

        # 2. Análisis del operador hegemónico
        linea_lider = "No traffic data"
        if aircrafts:
            lines = [ac.airline for ac in aircrafts if getattr(ac, 'airline', None)]
            if lines:
                linea_lider = Counter(lines).most_common(1)[0][0]

        current_hour = combo_hours.get()
        # Corrección del formateo de tiempo nativo
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 3. Escritura del flujo completo en el archivo plano
        with open(path, "w", encoding="utf-8") as file:
            file.write("=====================================================================\n")
            file.write(f"           AEROMANAGER ENTERPRISE - DAILY OPERATIONAL BRIEFING\n")
            file.write("=====================================================================\n")
            file.write(f"Date/Time of Issue:   {fecha_actual}\n")
            file.write(f"Target Airport:  {getattr(bcn, 'code', 'LEBL')}\n")
            file.write("---------------------------------------------------------------------\n\n")
            file.write("1. PLATFORM AND TERMINAL INFRASTRUCTURE\n")
            file.write(f"   • Number of Terminals:      {len(bcn.terminals) if hasattr(bcn, 'terminals') else 0}\n")
            file.write(f"   • Total Gates:  {total_gates}\n")
            file.write(f"   • Usage Monitoring:          {occupied_gates} Ocupados / {free_gates} Libres\n\n")
            file.write("2. LOGISTICS TRAFFIC AND FLEET DATA\n")
            file.write(f"   • Volume of Registered Transactions: {len(aircrafts)}\n")
            file.write(f"   • Majority Operator:              {linea_lider}\n\n")
            file.write(f"3. SELECTED TACTICAL ZONE REPORT ({current_hour})\n")
            file.write(f"   • Analysis Window:       Synchronized at time {current_hour}\n")
            file.write("=====================================================================\n")

        messagebox.showinfo("Saved Report",
                            "The technical operational report has been fully exported with all its data blocks.")
    except Exception as e:
        messagebox.showerror("Write Error", f"Data dump processing failed: {str(e)}")

def display_visual_map():
    if bcn is None:
        messagebox.showwarning("WARNING", "Load the airport structure first.")
        return
    win = tk.Toplevel(root)
    win.title(f"Visual Occupancy Map - {bcn.code}")
    win.geometry("1000x680")
    win.configure(bg=COLORS["bg_main"])

    create_header(win, f"Stationary Distribution — Mapping of {bcn.code}",
                  "View of fixed walkways through corporate areas.").pack(anchor="w", padx=25, pady=15)

    canvas = tk.Canvas(win, bg=COLORS["bg_main"], highlightthickness=0)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=COLORS["bg_main"])

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True, padx=25)
    scrollbar.pack(side="right", fill="y")

    for t in bcn.terminals:
        t_card = tk.LabelFrame(scroll_frame, text=f" TERMINAL {t.name} ", bg=COLORS["bg_sidebar"],
                               fg=COLORS["accent_sub"], font=("Segoe UI", 12, "bold"), padx=15, pady=15, bd=1,
                               relief="solid")
        t_card.pack(fill="x", pady=10, expand=True)
        for area in t.areas:
            tk.Label(t_card, text=f"• Area {area.name} ({area.type.upper()})", bg=COLORS["bg_sidebar"],
                     fg=COLORS["text_main"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 4))
            grid_container = tk.Frame(t_card, bg=COLORS["bg_sidebar"])
            grid_container.pack(fill="x", pady=5)

            MAX_COLUMNS = 6
            for idx, gate in enumerate(area.gates):
                r_idx, c_idx = idx // MAX_COLUMNS, idx % MAX_COLUMNS
                gate_color = COLORS["danger"] if gate.occupied else COLORS["success"]
                status_text = f"{gate.name}\n✈ {gate.aircraft_id}" if gate.occupied else f"{gate.name}\nLibre"
                tk.Label(grid_container, text=status_text, font=("Consoles", 9, "bold"), bg=gate_color, fg="white",
                         width=14, height=3, relief="flat").grid(row=r_idx, column=c_idx, padx=5, pady=5)


# =====================================================================
# ACOPLAMIENTO DE LLAMADAS A LOS BOTONES DE LA INTERFAZ
# =====================================================================
create_button(form_card, " Register Node", add_airport, COLORS["success"]).pack(fill="x", pady=4)
create_button(form_card, " Cancellation by ICAO", remove_airport, COLORS["danger"]).pack(fill="x", pady=4)

table_card = tk.Frame(ap_workspace, bg=COLORS["bg_card"], padx=15, pady=15)
table_card.pack(side="right", fill="both", expand=True, padx=(20, 0), pady=5)
toolbar_ap = tk.Frame(table_card, bg=COLORS["bg_card"])
toolbar_ap.pack(fill="x", pady=(0, 10))
create_button(toolbar_ap, " Upload .txt file", load_airports_file, COLORS["accent_sub"]).pack(side="left", padx=2)
create_button(toolbar_ap, " Save Schengen", save_schengen_file, COLORS["bg_sidebar"]).pack(side="left", padx=2)
create_button(toolbar_ap, " View Chart", call_plot_airports, COLORS["accent"]).pack(side="right", padx=2)
create_button(toolbar_ap, " Export Map KML", call_map_airports, COLORS["accent"]).pack(side="right", padx=2)

table_airports = ttk.Treeview(table_card, columns=("icao", "lat", "lon", "zone"), show="headings")
for c, t in [("icao", "ICAO CODE"), ("lat", "LATITUDE DECIMAL"), ("lon", "LONGITUDE DECIMAL"),
             ("zone", "GEOPOLITICAL STATE")]: table_airports.heading(c, text=t)
table_airports.pack(side="left", fill="both", expand=True)
sb_ap = tk.Scrollbar(table_card, orient="vertical", command=table_airports.yview)
table_airports.configure(yscrollcommand=sb_ap.set)
sb_ap.pack(side="right", fill="y")

create_button(fl_actions, " Import Arrivals", load_arrivals_file, COLORS["accent_sub"]).grid(row=0, column=0, padx=5,
                                                                                                pady=5, sticky="ew")
create_button(fl_actions, " Import Departures", load_departures_file, COLORS["accent_sub"]).grid(row=0, column=1,
                                                                                                 padx=5, pady=5,
                                                                                                 sticky="ew")
create_button(fl_actions, " Merge", execute_merge, COLORS["accent"]).grid(row=0, column=2, padx=5, pady=5,
                                                                                      sticky="ew")
create_button(fl_actions, " Isolate overnight stays", filter_pernoctas, COLORS["bg_card"]).grid(row=0, column=3, padx=5,
                                                                                          pady=5, sticky="ew")
create_button(fl_actions, " Schedule Flow", call_plot_arrivals).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
create_button(fl_actions, " Distribution Airlines", call_plot_airlines).grid(row=1, column=1, padx=5, pady=5,
                                                                            sticky="ew")
create_button(fl_actions, " Flight Type", call_plot_types).grid(row=1, column=2, padx=5, pady=5, sticky="ew")
create_button(fl_actions, " KML Trace Flights", call_map_kml, COLORS["accent"]).grid(row=1, column=3, padx=5, pady=5,
                                                                                     sticky="ew")
create_button(fl_actions, " Filter Long Distance (>2k km)", call_long_distance_kml, COLORS["bg_card"]).grid(row=1,
                                                                                                                column=4,
                                                                                                                padx=5,
                                                                                                                pady=5,
                                                                                                                sticky="ew")
fl_actions.columnconfigure((0, 1, 2, 3, 4), weight=1)

entry_search.bind("<KeyRelease>", lambda e: refresh_flights_table())
combo_filter_type.bind("<<ComboboxSelected>>", lambda e: refresh_flights_table())

create_button(card_resources, " Link Airport Structure (LEBL.txt)", load_airport_structure).pack(side="left",
                                                                                                          fill="x",
                                                                                                          expand=True,
                                                                                                          padx=4)
create_button(card_resources, " Assign Initial Doors (Overnight Stays)", process_night_gates, COLORS["success"]).pack(
    side="left", fill="x", expand=True, padx=4)
create_button(control_row, " Simulate Selected Tactical Zone", process_hourly_simulation, COLORS["accent"]).pack(
    side="left", fill="x", expand=True, padx=(10, 0))

create_button(card_analytics, " Plot Day Occupancy (24h History)",
              lambda: PlotDayOccupancy(bcn, aircrafts) if bcn and aircrafts else messagebox.showerror("Error",
                                                                                                      "Faltan datos operacionales."),
              COLORS["accent"]).pack(side="left", fill="x", expand=True, padx=(0, 4))
create_button(card_analytics, " Save Operational Briefing (.txt)", export_operations_briefing,
              COLORS["accent_sub"]).pack(side="left", fill="x", expand=True, padx=4)
create_button(card_analytics, " Open Platform Visual Plan", display_visual_map, COLORS["success"]).pack(
    side="right", fill="x", expand=True, padx=(4, 0))

# =====================================================================
# INICIALIZACIÓN COMPLETA DEL SISTEMA
# =====================================================================
root.mainloop()
