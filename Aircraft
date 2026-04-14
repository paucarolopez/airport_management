import matplotlib.pyplot as plt

from airport import IsSchengenAirport

# CLASE
# -------------------------
class Aircraft:
    def __init__(self, id="", airline="", origin="", arrival=""):
        self.id = id
        self.airline = airline
        self.origin = origin
        self.arrival = arrival  # format "hh:mm"


# CARGAR LLEGADAS
# -------------------------
def LoadArrivals(filename):
    aircrafts = []

    try:
        with open(filename, "r") as f:
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
    plt.show()


# GUARDAR VUELOS
# -------------------------
def SaveFlights(aircrafts, filename):
    if not aircrafts:
        print("Error: empty list")
        return -1

    with open(filename, "w") as f:
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

    filename = "flights.kml"

    with open(filename, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('<Document>\n')

        for a in aircrafts:
            color = "ff0000ff" if IsSchengenAirport(a.origin) else "ff00ff00"

            f.write(f"""
            <Placemark>
                <name>{a.id}</name>
                <Style>
                    <LineStyle>
                        <color>{color}</color>
                        <width>2</width>
                    </LineStyle>
                </Style>
                <LineString>
                    <coordinates>
                        2.0833,41.2974,0
                        0,0,0
                    </coordinates>
                </LineString>
            </Placemark>
            """)

        f.write('</Document>\n</kml>')

    print(f"KML file generated: {filename}")


# HAVERSINE DISTANCE
# -------------------------
import math

def Haversine(lat1, lon1, lat2, lon2):
    R = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = abs(lat1 - lat2)
    dlon = abs(lon1 - lon2)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# LLEGADAS DE LARGA DISTANCIA
# -------------------------
def LongDistanceArrivals(aircrafts):
    result = []

    # coordenades LEBL
    lat_bcn = 41.2974
    lon_bcn = 2.0833

    for a in aircrafts:
        # aquí necessitaries coords reals -> simplificació
        # assumeix que NO es poden calcular si no tens airport list
        # pots integrar-ho amb airport.py

        # placeholder: tots els vols es consideren llunyans
        dist = 3000

        if dist > 2000:
            result.append(a)

    return result


# COMPROVACIÓN
# -------------------------
if __name__ == "__main__":
    aircrafts = LoadArrivals("arrivals.txt")

    print("Loaded:", len(aircrafts))

    PlotArrivals(aircrafts)
    PlotAirlines(aircrafts)
    PlotFlightsType(aircrafts)

    SaveFlights(aircrafts, "output.txt")

    long_flights = LongDistanceArrivals(aircrafts)
    print("Long distance flights:", len(long_flights))

    MapFlights(aircrafts)
