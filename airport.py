# Importo matplotlib para poder hacer gráficos
import matplotlib.pyplot as plt



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

            code = parts[0]  # guardo el código

            lat_str = parts[1]  # guardo latitud en formato texto
            lon_str = parts[2]  # guardo longitud en formato texto

            lat = convert_coord(lat_str)
            lon = convert_coord(lon_str)

            airport = Airport(code, lat, lon)  # creo aeropuerto

            airports.append(airport)  # lo añado a la lista

            i += 1  # paso a la siguiente línea

    except:
        return []  # si hay error devuelvo lista vacía

    return airports  # devuelvo la lista


def SaveSchengenAirports(airports, filename):
    if len(airports) == 0:  # si la lista está vacía
        return -1  # error

    F = open(filename, 'w')  # abro archivo en modo escritura

    F.write("CODE LAT LON\n")  # escribo cabecera

    for a in airports:  # recorro lista
        if a.schengen:  # si es Schengen
            line = a.code + " " + str(a.lat) + " " + str(a.lon) + "\n"
            F.write(line)  # escribo línea

    F.close()  # cierro archivo


def AddAirport(airports, airport):
    for a in airports:  # recorro lista
        if a.code == airport.code:  # si ya existe
            return  # no lo añado

    airports.append(airport)  # lo añado si no existe


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
    F = open("airports.kml", "w")  # creo archivo KML

    # escribo cabecera KML
    F.write("<?xml version='1.0' encoding='UTF-8'?>\n")
    F.write("<kml xmlns='http://www.opengis.net/kml/2.2'>\n")
    F.write("<Document>\n")

    for a in airports:  # recorro aeropuertos
        F.write("<Placemark>\n")  # inicio punto

        F.write("<name>" + a.code + "</name>\n")  # nombre

        F.write("<Point>\n")
        F.write("<coordinates>" + str(a.lon) + "," + str(a.lat) + ",0</coordinates>\n")  # coordenadas
        F.write("</Point>\n")

        F.write("</Placemark>\n")  # fin punto

    F.write("</Document>\n")  # fin documento
    F.write("</kml>\n")


    F.close()  # cierro archivo