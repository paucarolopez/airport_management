import matplotlib.pyplot as plt
import math
from airport import LoadAirports, IsSchengenAirport, HaversineDistance

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
def LoadArrivals(Arrivals):
    aircrafts = []

    try:
        with open(Arrivals, "r") as f:
            lines = f.readlines()

        for line in lines[1:]:  # skip header
            parts = line.strip().split()

            if len(parts) != 4:
                continue

            id, origin, arrival, airline = parts

            # validar hora
            if ":" not in arrival:
                continue

            try:
                h, m = arrival.split(":")
                h = int(h)
                m = int(m)
                if h < 0 or h > 23 or m < 0 or m > 59:
                    continue
            except:
                continue

            aircrafts.append(Aircraft(id, airline, origin, arrival))

    except FileNotFoundError:
        print(f"[LoadArrivals] File not found: {Arrivals}")
        return []

    return aircrafts


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
    if not aircrafts:
        print("Error: empty list")
        return -1

    with open(filename, "w") as f:  # FIX 2: filename correcte
        f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")

        for a in aircrafts:
            id = a.id if a.id else "-"
            origin = a.origin if a.origin else "-"
            arrival = a.arrival if a.arrival else "0"
            airline = a.airline if a.airline else "-"

            f.write(f"{id} {origin} {arrival} {airline}\n")

    return 0


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
