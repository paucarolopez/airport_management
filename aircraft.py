import matplotlib.pyplot as plt
import math
from airport import LoadAirports, IsSchengenAirport, HaversineDistance
import webbrowser
# Coordenades LEBL (Barcelona El Prat)
LEBL_LAT = 41.297445
LEBL_LON = 2.0832941


# CLASE
# -------------------------
class Aircraft:
    def __init__(self, id="", airline="", origin="", arrival=""):
        self.id = id
        self.airline = airline
        self.origin = origin
        self.arrival = arrival  # format "hh:mm"


# CACHE DE COORDENADES
# -------------------------
_airport_coords = {}


def _load_airport_coords():
    """Loads airport coordinates from Airports.txt into the cache."""
    global _airport_coords
    if not _airport_coords:
        airports = LoadAirports('Airports.txt')
        for a in airports:
            _airport_coords[a.code] = (a.lat, a.lon)
        # Sempre incloure LEBL
        _airport_coords['LEBL'] = (LEBL_LAT, LEBL_LON)


def _get_airport_coords(code):
    """Returns (lat, lon) for a given ICAO code, or None if unknown."""
    _load_airport_coords()
    return _airport_coords.get(code, None)


# CARGAR LLEGADAS
# -------------------------
def LoadArrivals(filename):
    aircrafts = []  # creo lista vacía para guardar los aviones

    try:
        F = open(filename, 'r')  # abro el archivo en modo lectura
        lines = F.readlines()  # leo todas las líneas
        F.close()  # cierro el archivo

        i = 1  # empiezo en 1 para saltar la línea de cabecera

        while i < len(lines):
            parts = lines[i].split()  # separo la línea por espacios o tabuladores

            # El enunciado dice que si la línea no tiene la estructura correcta, la salte
            if len(parts) < 4:
                i += 1
                continue

            aircraft_id = parts[0]
            origin_airport = parts[1]
            time_str = parts[2]
            airline_company = parts[3]

            # Validación del formato de hora hh:mm o h:mm
            time_parts = time_str.split(':')
            if len(time_parts) != 2:
                i += 1
                continue  # si no tiene ':' la saltamos

            try:
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                # Compruebo que la hora y minutos sean valores lógicos reales
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    i += 1
                    continue
            except ValueError:
                i += 1
                continue  # si la hora no contiene números válidos, la saltamos

            # Si todo es correcto, creamos el objeto Aircraft y lo añadimos
            flight = Aircraft(aircraft_id, airline_company, origin_airport, time_str)
            aircrafts.append(flight)

            i += 1  # pasamos a la siguiente línea del fichero

    except:
        return []  # si el archivo no existe o falla, devuelvo lista vacía

    return aircrafts  # devuelvo la lista de aviones cargados



# GRAFICAR LLEGADAS POR HORA
# -------------------------
def PlotArrivals(aircrafts):
    if not aircrafts:
        print("Error: empty aircraft list")
        return

    hours = [0] * 24

    for a in aircrafts:
        h = int(a.arrival.split(":")[0])
        hours[h] += 1

    plt.bar(range(24), hours)
    plt.xlabel("Hour")
    plt.ylabel("Arrivals")
    plt.title("Arrivals per hour")
    plt.xticks(range(24))
    plt.show()


# GUARDAR VUELOS
# -------------------------
def SaveFlights(aircrafts, filename):  # FIX 2: usar el paràmetre filename
    if len(aircrafts) == 0:  # si la lista está vacía
        return -1  # devuelvo código de error

    try:
        F = open(filename, 'w')  # abro el archivo en modo escritura
        F.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")  # escribo la cabecera

        for ac in aircrafts:
            # Control de campos vacíos: si no tienen valor, ponemos '-' o 0 según corresponda
            id_val = ac.aircraft_id if ac.aircraft_id else '-'
            origin_val = ac.origin_airport if ac.origin_airport else '-'
            time_val = ac.time_of_landing if ac.time_of_landing else '-'
            airline_val = ac.airline_company if ac.airline_company else '-'

            line = f"{id_val} {origin_val} {time_val} {airline_val}\n"
            F.write(line)  # escribo la línea en el archivo

        F.close()  # cierro el archivo
    except:
        return -1  # error de escritura


# GRAFICAR AEROLINEAS
# -------------------------
def PlotAirlines(aircrafts):
    if not aircrafts:
        print("Error: empty aircraft list")
        return

    counts = {}

    for a in aircrafts:
        counts[a.airline] = counts.get(a.airline, 0) + 1

    airlines = list(counts.keys())
    values = list(counts.values())

    plt.bar(airlines, values)
    plt.xlabel("Airline")
    plt.ylabel("Flights")
    plt.title("Flights per airline")
    plt.xticks(rotation=45)
    plt.show()


# GRAFICAR TIPO DE VUELO (Schengen / Non)
# -------------------------
def PlotFlightsType(aircrafts):
    if not aircrafts:
        print("Error: empty aircraft list")
        return

    schengen = 0
    non_schengen = 0

    for a in aircrafts:
        if IsSchengenAirport(a.origin):
            schengen += 1
        else:
            non_schengen += 1

    plt.bar(["Flights"], [schengen], label="Schengen")
    plt.bar(["Flights"], [non_schengen], bottom=[schengen], label="Non-Schengen")

    plt.legend()
    plt.title("Flights type")
    plt.show()


# MAPEAR VUELOS (KML)
# -------------------------
def MapFlights(aircrafts):
    if not aircrafts:
        print("Error: empty aircraft list")
        return

    _load_airport_coords()  # FIX 3: carregar coordenades abans d'usar-les
    filename = "flights.kml"

    with open(filename, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('<Document>\n')

        for a in aircrafts:
            # FIX 3: obtenir coordenades reals de l'aeroport origen
            coords = _get_airport_coords(a.origin)
            if coords is None:
                continue  # saltar si no es coneixen les coordenades

            origin_lat, origin_lon = coords  # FIX 3: usar variables locals, no atributs inexistents
            color = "ff0000ff" if IsSchengenAirport(a.origin) else "ff00ff00"

            f.write(f'<Placemark>\n')
            f.write(f'  <name>{a.id}</name>\n')
            f.write(f'  <Style><LineStyle><color>{color}</color><width>2</width></LineStyle></Style>\n')
            f.write(f'  <LineString>\n')
            f.write(f'    <altitudeMode>clampToGround</altitudeMode>\n')
            f.write(f'    <tessellate>1</tessellate>\n')
            f.write(f'    <coordinates>{origin_lon},{origin_lat},0 {LEBL_LON},{LEBL_LAT},0</coordinates>\n')
            f.write(f'  </LineString>\n')
            f.write(f'</Placemark>\n')

        f.write('</Document>\n</kml>')

    print(f"KML file generated: {filename}")
    try:
        webbrowser.open("https://earth.google.com/web/")
    except Exception:
        pass


# LLEGADAS DE LARGA DISTANCIA
# -------------------------
def LongDistanceArrivals(aircrafts):
    result = []

    _load_airport_coords()  # FIX 4: carregar coordenades

    for a in aircrafts:
        coords = _get_airport_coords(a.origin)
        if coords is None:
            continue  # FIX 4: saltar si no es coneixen les coordenades (no assumir 3000 km)

        # FIX 4: calcular distància real amb Haversine
        dist = HaversineDistance(coords[0], coords[1], LEBL_LAT, LEBL_LON)

        if dist > 2000:
            result.append(a)

    return result
    try:
        webbrowser.open("https://earth.google.com/web/")
    except Exception:
            pass


# COMPROVACIÓ
# -------------------------
if __name__ == "__main__":
    aircrafts = LoadArrivals("Arrivals.txt")

    print("Loaded:", len(aircrafts))

    PlotArrivals(aircrafts)
    PlotAirlines(aircrafts)
    PlotFlightsType(aircrafts)

    SaveFlights(aircrafts, "output.txt")

    long_flights = LongDistanceArrivals(aircrafts)
    print("Long distance flights:", len(long_flights))

    MapFlights(aircrafts)
