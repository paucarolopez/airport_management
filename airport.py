# Importo matplotlib para poder hacer gráficos
import matplotlib.pyplot as plt
import math  # necessari per a HaversineDistance
import webbrowser
import re
import os

# ================= CLASE =================

# Defino la clase Airport para guardar los datos de cada aeropuerto
class Airport:
    def __init__(self, code, lat, lon):  # constructor con código y coordenadas
        self.code = code  # guardo el código ICAO del aeropuerto
        self.lat = lat  # guardo la latitud
        self.lon = lon  # guardo la longitud
        self.schengen = False  # inicializo Schengen como False por defecto


# ================= FUNCIONES =================

def IsSchengenAirport(code):
    # lista de prefijos ICAO de países Schengen
    schengen_codes = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH',
                      'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS']

    if code == "":  # si el código está vacío
        return False  # no es Schengen

    prefix = code[:2]  # cojo los dos primeros caracteres

    if prefix in schengen_codes:  # si el prefijo está en la lista
        return True  # es Schengen
    else:
        return False  # no es Schengen


def convert_coord(coord_str):
    """
    Convierte coordenadas tipo 'N452805' o 'W0734429' a decimal con precisión completa.
    """
    direction = coord_str[0]

    if len(coord_str) == 7:  # latitud NDDMMSS o SDDMMSS
        degrees = int(coord_str[1:3])
        minutes = int(coord_str[3:5])
        seconds = int(coord_str[5:7])
    elif len(coord_str) == 8:  # longitud WDDDMMSS o EDDDMMSS
        degrees = int(coord_str[1:4])
        minutes = int(coord_str[4:6])
        seconds = int(coord_str[6:8])
    else:
        raise ValueError(f"Formato de coordenada inválido: {coord_str}")

    decimal = degrees + minutes / 60 + seconds / 3600

    if direction in ['S', 'W']:
        decimal = -decimal

    return decimal


def decimal_to_coord(value, is_lat):
    """
    Convierte un valor decimal a formato NDDMMSS (latitud) o EDDDMMSS (longitud).
    Necessari per a SaveSchengenAirports.
    """
    if is_lat:
        direction = 'N' if value >= 0 else 'S'
    else:
        direction = 'E' if value >= 0 else 'W'

    value = abs(value)
    degrees = int(value)
    minutes = int((value - degrees) * 60)
    seconds = int(round(((value - degrees) * 60 - minutes) * 60))

    if is_lat:
        return f"{direction}{degrees:02d}{minutes:02d}{seconds:02d}"  # NDDMMSS
    else:
        return f"{direction}{degrees:03d}{minutes:02d}{seconds:02d}"  # EDDDMMSS


def SetSchengen(airport):
    # asigno el valor de Schengen usando la función anterior
    airport.schengen = IsSchengenAirport(airport.code)


def PrintAirport(airport):
    # imprimo todos los datos del aeropuerto por pantalla
    print(airport.code, airport.lat, airport.lon, airport.schengen)


def LoadAirports(Airports):
    airports = []  # creo lista vacía para guardar aeropuertos

    try:
        F = open(Airports, 'r')  # abro archivo en modo lectura

        lines = F.readlines()  # leo todas las líneas del archivo

        F.close()  # cierro el archivo

        i = 1  # empiezo en 1 para saltar la cabecera

        while i < len(lines):  # recorro todas las líneas
            parts = lines[i].split()  # separo cada línea en partes

            if len(parts) < 3:  # línia incompleta, la salto
                i += 1
                continue

            code = parts[0]  # guardo el código

            lat_str = parts[1]  # guardo latitud en formato texto
            lon_str = parts[2]  # guardo longitud en formato texto

            lat = convert_coord(lat_str)
            lon = convert_coord(lon_str)

            airport = Airport(code, lat, lon)  # creo aeropuerto

            SetSchengen(airport)  # FIX 1: assigno Schengen (abans no es feia!)

            airports.append(airport)  # lo añado a la lista

            i += 1  # paso a la siguiente línea

    except:
        return []  # si hay error devuelvo lista vacía

    return airports  # devuelvo la lista


def SaveSchengenAirports(airports, SchengenAirports):
    if len(airports) == 0:  # si la lista está vacía
        return -1  # error

    F = open(SchengenAirports, 'w')  # abro archivo en modo escritura

    F.write("CODE LAT LON\n")  # escribo cabecera

    for a in airports:  # recorro lista
        if a.schengen:  # si es Schengen
            # FIX 2: guardar en format original NDDMMSS/EDDDMMSS, no decimal
            lat_str = decimal_to_coord(a.lat, is_lat=True)
            lon_str = decimal_to_coord(a.lon, is_lat=False)
            line = a.code + " " + lat_str + " " + lon_str + "\n"
            F.write(line)  # escribo línea

    F.close()  # cierro archivo


def AddAirport(airports, airport):
    # Validar que el código ICAO contenga exactamente 4 letras de la A a la Z
    if not re.match(r"^[A-Z]{4}$", airport.code):
        return "ERROR_ICAO"

    # Validar rangos físicos reales de las coordenadas geográficas
    if not (-90 <= airport.lat <= 90):
        return "ERROR_LAT"
    if not (-180 <= airport.lon <= 180):
        return "ERROR_LON"

    # Verificar si ya existe duplicado
    for a in airports:
        if a.code == airport.code:
            return "ERROR_DUPLICADO"

    airports.append(airport)
    return "OK"

def RemoveAirport(airports, code):
    i = 0  # índice

    while i < len(airports):  # recorro lista
        if airports[i].code == code:  # si coincide
            airports.pop(i)  # elimino
            return

        i += 1  # siguiente

    return -1  # error si no encontrado


def PlotAirports(airports):
    sch = 0  # contador Schengen
    non = 0  # contador no Schengen

    for a in airports:  # recorro lista
        if a.schengen:
            sch += 1  # sumo
        else:
            non += 1  # sumo

    plt.bar(["Airports"], [sch], color='blue', label='Schengen')  # barra Schengen
    plt.bar(["Airports"], [non], bottom=[sch], color='red', label='Non Schengen')  # barra encima

    plt.legend()  # muestro leyenda
    plt.show()  # muestro gráfico


def MapAirports(airports):
    filename = "airports.kml"
    F = open(filename, "w")

    F.write("<?xml version='1.0' encoding='UTF-8'?>\n")
    F.write("<kml xmlns='http://www.opengis.net/kml/2.2'>\n")
    F.write("<Document>\n")

    F.write("<Style id='schengen'><IconStyle><color>ffff0000</color></IconStyle></Style>\n")
    F.write("<Style id='non_schengen'><IconStyle><color>ff0000ff</color></IconStyle></Style>\n")

    for a in airports:
        F.write("<Placemark>\n")
        F.write("<name>" + a.code + "</name>\n")

        if a.schengen:
            F.write("<styleUrl>#schengen</styleUrl>\n")
        else:
            F.write("<styleUrl>#non_schengen</styleUrl>\n")

        F.write("<Point>\n")
        F.write("<coordinates>" + str(a.lon) + "," + str(a.lat) + ",0</coordinates>\n")
        F.write("</Point>\n")
        F.write("</Placemark>\n")

    F.write("</Document>\n")
    F.write("</kml>\n")
    F.close()

    # EJECUCIÓN DIRECTA DEL ARCHIVO KML EN EL SISTEMA OPERATIVO
    try:
        # os.startfile es exclusivo de Windows y abre el archivo con su programa asignado (Google Earth Pro)
        if hasattr(os, 'startfile'):
            os.startfile(filename)
        else:
            # Comando alternativo para sistemas basados en Unix/Mac (por si acaso)
            import subprocess
            subprocess.call(('open', filename))
    except Exception:
        # Si el sistema no tiene un programa asignado para .kml, abrimos la versión web como plan de contingencia
        webbrowser.open("https://earth.google.com/web/")


# ================= HAVERSINE =================

def HaversineDistance(lat1, lon1, lat2, lon2):
    """
    Calcula la distància en km entre dos punts (lat/lon en graus decimals).
    Necessari per a aircraft.py → LongDistanceArrivals.
    """
    R = 6371  # radi de la Terra en km

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
