# Importo matplotlib para gráficos y math para los cálculos matemáticos del Haversine
import matplotlib.pyplot as plt
import math

# Importo el módulo anterior para poder usar la lista de aeropuertos y sus coordenadas
from airport import *


# ================= CLASE =================

# Defino la clase Aircraft para guardar los datos de cada vuelo que llega a LEBL
class Aircraft:
    def __init__(self, aircraft_id, airline_company, origin_airport, time_of_landing):
        self.aircraft_id = aircraft_id  # matrícula del avión (string)
        self.airline_company = airline_company  # código ICAO de la aerolínea (3 caracteres)
        self.origin_airport = origin_airport  # código ICAO del aeropuerto de origen (4 caracteres)
        self.time_of_landing = time_of_landing  # hora esperada de llegada (hh:mm)


# ================= FUNCIONES DE ARCHIVOS =================

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


def SaveFlights(aircrafts, filename):
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


# ================= FUNCIONES MATEMÁTICAS =================

def Haversine(lat1, lon1, lat2, lon2):
    # Función auxiliar para calcular la distancia entre dos puntos geográficos
    # Convierto los grados a radianes necesarios para las funciones de math
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Aplico la fórmula del Haversine
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    r = 6371.0  # Radio de la Tierra en kilómetros
    return c * r


def LongDistanceArrivals(aircrafts, airports_list):
    # Nota: Pasamos la lista de aeropuertos cargados para poder buscar sus coordenadas
    long_distance_flights = []

    # Coordenadas fijas de Barcelona El Prat (LEBL) según el enunciado de la V1
    lebl_lat = 41.297445
    lebl_lon = 2.0832941

    for ac in aircrafts:
        # Busco el aeropuerto de origen del avión en nuestra base de datos de aeropuertos
        origin_ap = None
        for ap in airports_list:
            if ap.code == ac.origin_airport:
                origin_ap = ap
                break

        # Si encontramos el aeropuerto, calculamos la distancia hasta Barcelona
        if origin_ap is not None:
            dist = Haversine(origin_ap.lat, origin_ap.lon, lebl_lat, lebl_lon)
            if dist > 2000.0:  # si la distancia supera los 2000 Km
                long_distance_flights.append(ac)  # lo añado a los vuelos especiales

    return long_distance_flights


# ================= FUNCIONES DE GRÁFICOS =================

def PlotArrivals(aircrafts):
    if len(aircrafts) == 0:
        print("Error: Lista de vuelos vacía")
        return

    # Creo una lista con 24 posiciones (una para cada hora del día) iniciadas a 0
    hours_count = [0] * 24

    for ac in aircrafts:
        # Extraigo la hora antes de los dos puntos (ej: "14:35" -> "14")
        hour_part = int(ac.time_of_landing.split(':')[0])
        hours_count[hour_part] += 1  # incremento el contador de esa hora

    # Genero el eje X con las etiquetas "0h", "1h", ..., "23h"
    x_labels = []
    for h in range(24):
        x_labels.append(f"{h}h")

    plt.bar(x_labels, hours_count, color='lightblue')
    plt.title("Frecuencia de Aterrizajes por Hora")
    plt.xlabel("Franja Horaria")
    plt.ylabel("Número de Vuelos")
    plt.show()


def PlotAirlines(aircrafts):
    if len(aircrafts) == 0:
        print("Error: Lista de vuelos vacía")
        return

    # Contaremos cuántos vuelos tiene cada aerolínea usando listas paralelas
    airlines = []
    counts = []

    for ac in aircrafts:
        comp = ac.airline_company
        if comp in airlines:
            # Si ya la conocemos, buscamos su posición y sumamos 1
            idx = airlines.index(comp)
            counts[idx] += 1
        else:
            # Si es nueva, la añadimos con contador inicial a 1
            airlines.append(comp)
            counts.append(1)

    plt.bar(airlines, counts, color='lightgreen')
    plt.title("Número de Vuelos por Aerolínea")
    plt.xlabel("Compañía")
    plt.ylabel("Vuelos")
    plt.show()


def PlotFlightsType(aircrafts, airports_list):
    if len(aircrafts) == 0:
        print("Error: Lista de vuelos vacía")
        return

    sch_count = 0
    non_count = 0

    for ac in aircrafts:
        # Busco el aeropuerto de origen para saber si es Schengen
        is_schengen = False
        for ap in airports_list:
            if ap.code == ac.origin_airport:
                is_schengen = ap.schengen
                break

        if is_schengen:
            sch_count += 1
        else:
            non_count += 1

    # Gráfico de barras apiladas idéntico al de la Versión 1
    plt.bar(["Flights"], [sch_count], color='blue', label='Schengen')
    plt.bar(["Flights"], [non_count], bottom=[sch_count], color='red', label='Non Schengen')
    plt.title("Origen de los Vuelos")
    plt.legend()
    plt.show()


# ================= GEOLOCALIZACIÓN KML =================

def MapFlights(aircrafts, airports_list, filename="flights.kml"):
    try:
        F = open(filename, "w")  # creo el archivo KML de rutas

        # Cabecera KML reglamentaria
        F.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        F.write("<kml xmlns='http://www.opengis.net/kml/2.2'>\n")
        F.write("<Document>\n")

        # Coordenadas de Barcelona El Prat
        lebl_lat = 41.297445
        lebl_lon = 2.0832941

        for ac in aircrafts:
            # Busco los datos geográficos de su origen
            origin_ap = None
            for ap in airports_list:
                if ap.code == ac.origin_airport:
                    origin_ap = ap
                    break

            if origin_ap is not None:
                # El enunciado pide diferenciar colores según si es Schengen o no
                # En KML los colores se definen en formato AABBGGRR (Opacidad, Azul, Verde, Rojo)
                if origin_ap.schengen:
                    color_kml = "ff0000ff"  # Rojo para Schengen
                else:
                    color_kml = "ffff0000"  # Azul para No Schengen

                F.write("<Placemark>\n")
                F.write(f"<name>{ac.aircraft_id} ({ac.origin_airport}->LEBL)</name>\n")

                # Definimos el estilo de la línea (color y grosor)
                F.write("<Style>\n<LineStyle>\n")
                F.write(f"<color>{color_kml}</color>\n")
                F.write("<width>3</width>\n")
                F.write("</LineStyle>\n</Style>\n")

                # Dibujamos la trayectoria en el mapa (Línea desde origen hasta destino)
                F.write("<LineString>\n")
                F.write("<coordinates>\n")
                F.write(f"{origin_ap.lon},{origin_ap.lat},0\n")  # Punto Inicial
                F.write(f"{lebl_lon},{lebl_lat},0\n")  # Punto Final (LEBL)
                F.write("</coordinates>\n")
                F.write("</LineString>\n")
                F.write("</Placemark>\n")

        F.write("</Document>\n</kml>\n")
        F.close()
    except:
        print("Error generando el archivo KML de trayectorias")


# ================= SECCIÓN DE PRUEBAS (__main__) =================
# Esta sección solo se ejecuta si ejecutas directamente "aircraft.py" en tu editor.
if __name__ == "__main__":
    print("=== PROBANDO MÓDULO AIRCRAFT (SÓLO TEST SECCIÓN) ===")

    # Para probar adecuadamente, primero necesitamos cargar algunos aeropuertos de muestra
    base_airports = LoadAirports("Airports.txt")
    for a in base_airports:
        SetSchengen(a)

    # Cargo los vuelos usando el archivo de datos de Atenea
    flights = LoadArrivals("Arrivals.txt")
    print(f"Vuelos cargados con éxito: {len(flights)}")

    if len(flights) > 0:
        # Probamos los gráficos solicitados
        PlotArrivals(flights)
        PlotAirlines(flights)
        PlotFlightsType(flights, base_airports)

        # Probamos el filtro de larga distancia (2000 km)
        long_vuelos = LongDistanceArrivals(flights, base_airports)
        print(f"Vuelos de larga distancia encontrados (>2000km): {len(long_vuelos)}")

        # Probamos la generación del mapa de rutas completo
        MapFlights(flights, base_airports, "test_vuelos_completo.kml")
    long_flights = LongDistanceArrivals(aircrafts)
    print("Long distance flights:", len(long_flights))

    MapFlights(aircrafts)
