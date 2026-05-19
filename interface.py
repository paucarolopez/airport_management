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
root.title("Airport Manager")
root.geometry("750x620")

# ================== COLORS ==================
root.configure(bg="#1e1e2e")

COLORS = {
    "bg":       "#1e1e2e",
    "card":     "#2a2a3e",
    "accent":   "#7c6af7",
    "accent2":  "#2ea88a",   # verd més apagat (era #56cfb2)
    "danger":   "#e06c75",
    "text":     "#cdd6f4",
    "subtext":  "#cdd6f4",   # igual que text perquè es vegi bé
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
aircrafts = []

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


# ================== FUNCIONS V2 ==================

def load_arrivals():
    filename = filedialog.askopenfilename(
        title="Selecciona el fitxer d'arribades",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not filename:
        return
    global aircrafts
    aircrafts = LoadArrivals(filename)
    if not aircrafts:
        messagebox.showwarning("Atencio", "No s'ha carregat cap vol.")
        return
    refresh_flights_list()
    messagebox.showinfo("OK", f"{len(aircrafts)} vols carregats")


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
        flights_listbox.insert(tk.END,
            f"{ac.id}  |  {ac.origin}  |  {ac.arrival}  |  {ac.airline}")


# ================== FUNCIONS V3 ==================

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
            messagebox.showinfo("OK", f"Aeroport {bcn.code} carregat correctament")


def assign_gates():
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
    messagebox.showinfo("OK", f"Gates assignats: {assigned} de {len(aircrafts)} vols")


def show_occupancy():
    if bcn is None:
        messagebox.showerror("Error", "No hi ha cap aeroport carregat")
        return
    occ = GateOccupancy(bcn)
    win = tk.Toplevel(root)
    win.title(f"Ocupacio de portes — {bcn.code}")
    win.geometry("500x450")
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
        status = f"OK  {g['aircraft']}" if g['occupied'] else "--  lliure"
        lb.insert(tk.END, f"{g['gate']:22s}  {status}")


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

styled_button(frame_btns1, "Añadir",           add_airport,         COLORS["accent2"]).grid(row=0, column=0, padx=5, pady=4)
styled_button(frame_btns1, "Eliminar",          remove_airport,      COLORS["accent2"]).grid(row=0, column=1, padx=5, pady=4)
styled_button(frame_btns1, "Cargar",          load_airports,       COLORS["accent2"]).grid(row=0, column=2, padx=5, pady=4)
styled_button(frame_btns1, "Guardar Schengen",  save_schengen,       COLORS["accent2"]).grid(row=1, column=0, padx=5, pady=4)
styled_button(frame_btns1, "Gráfico",            plot_airports_chart, COLORS["accent2"]).grid(row=1, column=1, padx=5, pady=4)
styled_button(frame_btns1, "Google Earth",      map_airports_kml,    COLORS["accent2"]).grid(row=1, column=2, padx=5, pady=4)

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

styled_label(tab2, "  Gestión de Vuelos", size=15, bold=True).pack(pady=(18, 8))

frame_btns2 = tk.Frame(tab2, bg=COLORS["bg"])
frame_btns2.pack(pady=10)

styled_button(frame_btns2, "Cargar llegadas",  load_arrivals,          COLORS["accent2"]).grid(row=0, column=0, padx=5, pady=4)
styled_button(frame_btns2, "Guardar vuelos",         save_flights,           COLORS["accent2"]).grid(row=0, column=1, padx=5, pady=4)
styled_button(frame_btns2, "Gráfico por hora",       plot_arrivals_chart,    COLORS["accent2"]).grid(row=1, column=0, padx=5, pady=4)
styled_button(frame_btns2, "Gráfico aerolíneas",     plot_airlines_chart,    COLORS["accent2"]).grid(row=1, column=1, padx=5, pady=4)
styled_button(frame_btns2, "Gráfico Schengen",       plot_flights_type_chart,COLORS["accent2"]).grid(row=2, column=0, padx=5, pady=4)
styled_button(frame_btns2, "Google Earth",   map_flights_kml,        COLORS["accent2"]).grid(row=2, column=1, padx=5, pady=4)
styled_button(frame_btns2, "Larga distancia",      map_long_distance_kml,  COLORS["accent2"]).grid(row=3, column=0, columnspan=2, padx=5, pady=4)

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

styled_label(tab3, "  Gestión de Puertas de Embarque", size=15, bold=True).pack(pady=(18, 8))

frame_btns3 = tk.Frame(tab3, bg=COLORS["bg"])
frame_btns3.pack(pady=10)

styled_button(frame_btns3, "Cargar estructuras aeropuerto", load_structure,  COLORS["accent2"]).pack(pady=6)
styled_button(frame_btns3, "Asignar gates",               assign_gates,    COLORS["accent2"]).pack(pady=6)
styled_button(frame_btns3, "Mostrar ocupación",             show_occupancy,  COLORS["accent2"]).pack(pady=6)


# ==================
root.mainloop()
