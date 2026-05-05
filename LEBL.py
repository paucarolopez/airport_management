import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from airport import *
from LEBL import *

# ================== VENTANA ==================
root = tk.Tk()
root.title("Airport Manager")
root.geometry("700x550")

# Pestañas
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab1 = tk.Frame(notebook)
tab2 = tk.Frame(notebook)

notebook.add(tab1, text="Aeropuertos (V1)")
notebook.add(tab2, text="Gates (V3)")

# ================== DATOS ==================
airports = []
bcn = None
aircrafts = []  # Debes cargar esto con versión 2

# ================== FUNCIONES V1 ==================

def add_airport():
    icaocode = entry_icao.get().upper()
    try:
        lat = float(entry_lat.get())
        lon = float(entry_lon.get())
    except:
        messagebox.showerror("Error", "Latitud/Longitud inválidas")
        return

    new_airport = Airport(icaocode, lat, lon)
    SetSchengen(new_airport)
    AddAirport(airports, new_airport)

    messagebox.showinfo("OK", f"{icaocode} añadido")


def remove_airport():
    code = entry_icao.get().upper()
    RemoveAirport(airports, code)


def load_airports():
    filename = filedialog.askopenfilename()
    if not filename:
        return

    global airports
    airports = LoadAirports(filename)

    for ap in airports:
        SetSchengen(ap)

    messagebox.showinfo("OK", "Aeropuertos cargados")


def show_airports():
    if not airports:
        messagebox.showerror("Error", "No hay datos")
        return

    text = ""
    for ap in airports:
        text += f"{ap.code} | Schengen: {ap.schengen}\n"

    messagebox.showinfo("Lista", text)


# ================== FUNCIONES V3 ==================

def load_structure():
    global bcn
    bcn = LoadAirportStructure("LEBL.txt")

    if bcn == -1:
        messagebox.showerror("Error", "No se pudo cargar LEBL")
    else:
        messagebox.showinfo("OK", "Estructura cargada")


def assign_gates():
    global bcn, aircrafts

    if bcn is None:
        messagebox.showerror("Error", "Carga primero el aeropuerto")
        return

    if not aircrafts:
        messagebox.showerror("Error", "No hay vuelos cargados")
        return

    for ac in aircrafts:
        AssignGate(bcn, ac)

    messagebox.showinfo("OK", "Gates asignados")


def show_occupancy():
    if bcn is None:
        messagebox.showerror("Error", "No hay aeropuerto")
        return

    occ = GateOccupancy(bcn)

    text = ""
    for g in occ[:25]:
        text += f"{g}\n"

    messagebox.showinfo("Ocupación", text)


# ================== TAB 1 (V1) ==================

tk.Label(tab1, text="Código ICAO").pack()
entry_icao = tk.Entry(tab1)
entry_icao.pack()

tk.Label(tab1, text="Latitud").pack()
entry_lat = tk.Entry(tab1)
entry_lat.pack()

tk.Label(tab1, text="Longitud").pack()
entry_lon = tk.Entry(tab1)
entry_lon.pack()

tk.Button(tab1, text="Agregar aeropuerto", command=add_airport).pack(pady=5)
tk.Button(tab1, text="Eliminar aeropuerto", command=remove_airport).pack(pady=5)
tk.Button(tab1, text="Cargar aeropuertos", command=load_airports).pack(pady=5)
tk.Button(tab1, text="Mostrar aeropuertos", command=show_airports).pack(pady=5)


# ================== TAB 2 (V3) ==================

tk.Label(tab2, text="Gestión de Gates LEBL", font=("Arial", 14)).pack(pady=10)

tk.Button(tab2, text="Cargar estructura aeropuerto", command=load_structure).pack(pady=5)
tk.Button(tab2, text="Asignar gates", command=assign_gates).pack(pady=5)
tk.Button(tab2, text="Mostrar ocupación", command=show_occupancy).pack(pady=5)


# ==================
root.mainloop()
