import matplotlib.pyplot as plt
import math
from airport import *

# ================= CLASE =================

class Aircraft:
    def __init__(self, id, airline, origin, time):
        self.id = id
        self.airline = airline
        self.origin = origin
        self.time = time


# ================= FUNCIONES =================

def LoadArrivals(filename):
    aircrafts = []

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines[1:]:
            parts = line.split()

            if len(parts) != 4:
                continue

            try:
                h, m = parts[2].split(":")
                int(h); int(m)
            except:
                continue

            aircraft = Aircraft(parts[0], parts[3], parts[1], parts[2])
            aircrafts.append(aircraft)

    except Exception:
        return []

    return aircrafts


def SaveFlights(aircrafts, filename):
    if not aircrafts:
        return -1

    with open(filename, 'w') as f:
        f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")

        for a in aircrafts:
            id = a.id if a.id else "-"
            origin = a.origin if a.origin else "-"
            time = a.time if a.time else "0:00"
            airline = a.airline if a.airline else "-"

            f.write(f"{id} {origin} {time} {airline}\n")


def PlotArrivals(aircrafts):
    if not aircrafts:
        print("Lista vacía")
        return

    hours = [0]*24

    for a in aircrafts:
        h = int(a.time.split(":")[0])
        hours[h] += 1

    plt.bar(range(24), hours)
    plt.xlabel("Hora")
    plt.ylabel("Número de vuelos")
    plt.title("Llegadas por hora")
    plt.show()


def PlotAirlines(aircrafts):
    if not aircrafts:
        print("Lista vacía")
        return

    count = {}

    for a in aircrafts:
        count[a.airline] = count.get(a.airline, 0) + 1

    plt.bar(count.keys(), count.values())
    plt.xticks(rotation=45)
    plt.title("Vuelos por aerolínea")
    plt.show()


def PlotFlightsType(aircrafts, airports):
    if not aircrafts:
        print("Lista vacía")
        return

    sch = 0
    non = 0

    for a in aircrafts:
        for ap in airports:
            if ap.code == a.origin:
                if ap.schengen:
                    sch += 1
                else:
                    non += 1

    plt.bar(["Flights"], [sch], label="Schengen")
    plt.bar(["Flights"], [non], bottom=[sch], label="Non Schengen")
    plt.legend()
    plt.title("Tipo de vuelos")
    plt.show()


# ================= DISTANCIA =================

def Haversine(lat1, lon1, lat2, lon2):
    r = 6371

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return r * c


def LongDistanceArrivals(aircrafts, airports):
    result = []

    for a in aircrafts:
        for ap in airports:
            if ap.code.strip().upper() == a.origin.strip().upper():
                dist = Haversine(ap.lat, ap.lon, 41.297, 2.083)  # LEBL

                if dist > 2000:
                    result.append(a)

    return result


# ================= MAPA =================

def MapFlights(aircrafts, airports, only_long=False):
    F = open("flights.kml", "w")

    F.write("<?xml version='1.0' encoding='UTF-8'?>\n")
    F.write("<kml xmlns='http://www.opengis.net/kml/2.2'>\n")
    F.write("<Document>\n")

    for a in aircrafts:
        for ap in airports:
            if ap.code == a.origin:

                dist = Haversine(ap.lat, ap.lon, 41.297, 2.083)

                if only_long and dist <= 2000:
                    continue

                color = "ff0000ff" if ap.schengen else "ff00ffff"

                F.write("<Placemark>\n")
                F.write("<Style><LineStyle><color>" + color + "</color></LineStyle></Style>\n")
                F.write("<LineString>\n")
                F.write("<coordinates>")
                F.write(f"{ap.lon},{ap.lat},0 2.083,41.297,0")
                F.write("</coordinates>\n")
                F.write("</LineString>\n")
                F.write("</Placemark>\n")

    F.write("</Document>\n")
    F.write("</kml>\n")

    F.close()


# ================= TEST =================

if __name__ == "__main__":
    aircrafts = LoadArrivals("arrivals.txt")
    airports = LoadAirports("Airports.txt")

    for ap in airports:
        SetSchengen(ap)

    PlotArrivals(aircrafts)
    PlotAirlines(aircrafts)
    PlotFlightsType(aircrafts, airports)

    long_flights = LongDistanceArrivals(aircrafts, airports)
    print("Vuelos largos:", len(long_flights))

    MapFlights(aircrafts, airports)
