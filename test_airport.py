# test_airport.py (nivel INFO1 – versión 1)
from airport import *   # Importo todas las funciones y la clase Airport que definimos

print("=== PRUEBA COMPLETA DEL SISTEMA ===")

# === Test 1: Función básica de la clase Airport ===
print("\n1. Probando la clase Airport...")
airport = Airport("LEBL", 41.297445, 2.0832941)  # Creo un aeropuerto con código ICAO y coordenadas
SetSchengen(airport)  # Defino si el aeropuerto pertenece a Schengen
PrintAirport(airport)  # Muestro los datos del aeropuerto en consola

# === Test 2: Operaciones con archivos ===
print("\n2. Probando carga y guardado de archivos...")

# Cargo la lista de aeropuertos desde Airports.txt (archivo que descargaste de Atenea)
airports = LoadAirports("Airports.txt")  # Devuelve una lista de objetos Airport

if len(airports) == 0:  # Si no se pudo cargar el archivo
    print("Error al cargar el archivo de aeropuertos")
else:
    print("Se han cargado", len(airports), "aeropuertos")  # Informo cuántos aeropuertos se cargaron

    # Defino Schengen para todos los aeropuertos cargados
    for ap in airports:
        SetSchengen(ap)  # Esto marca si cada aeropuerto está en Schengen

    # Prueba de agregar y eliminar un aeropuerto
    new_airport = Airport("TEST", 50.0, 10.0)  # Creo un aeropuerto de prueba
    AddAirport(airports, new_airport)  # Lo agrego a la lista
    print("Aeropuerto TEST agregado")

    RemoveAirport(airports, "TEST")  # Lo elimino de la lista
    print("Aeropuerto TEST eliminado")

    # Guardar en un archivo solo los aeropuertos Schengen
    SaveSchengenAirports(airports, "schengen_airports.txt")
    print("Aeropuertos Schengen guardados en schengen_airports.txt")

# === Test 3: Gráficos ===
print("\n3. Probando gráficos...")
if len(airports) > 0:
    PlotAirports(airports)  # Grafico barras apiladas de aeropuertos Schengen / No Schengen
    MapAirports(airports)   # Muestro aeropuertos en Google Earth (KML)

print("\n¡Todas las pruebas han finalizado!")