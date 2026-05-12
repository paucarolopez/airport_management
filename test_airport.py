# test_airport.py (nivel INFO1 – versión 1)
from airport import *  # Importo todas las funciones y la clase Airport que definimos

print("=== PRUEBA COMPLETA DEL SISTEMA ===")

# === Test 1: Función básica de la clase Airport ===
print("\n1. Probando la clase Airport...")
airport = Airport("LEBL", 41.297445, 2.0832941)  # Creo un aeropuerto con código ICAO y coordenadas
SetSchengen(airport)  # Defino si el aeropuerto pertenece a Schengen
PrintAirport(airport)  # Muestro los datos del aeropuerto en consola

# === Test 2: IsSchengenAirport ===
# FIX 3: afegit — és una funció de airport.py que cal provar
print("\n2. Probando IsSchengenAirport...")
casos = [("LEBL", True), ("EDDF", True), ("BIKF", False), ("CYYZ", False), ("", False)]
for code, expected in casos:
    result = IsSchengenAirport(code)
    ok = "OK" if result == expected else "ERROR"
    print(f"  [{ok}] IsSchengenAirport('{code}') = {result}  (esperado: {expected})")

# === Test 3: HaversineDistance ===
# FIX 3: afegit — és una funció de airport.py que cal provar
print("\n3. Probando HaversineDistance...")
dist = HaversineDistance(41.297445, 2.0832941, 40.4936, -3.5668)  # LEBL → LEMD
print(f"  Distancia LEBL → LEMD: {dist:.1f} km  (esperado: ~505 km)")

# === Test 4: Operaciones con archivos ===
print("\n4. Probando carga y guardado de archivos...")

# Cargo la lista de aeropuertos desde Airports.txt (archivo que descargaste de Atenea)
airports = LoadAirports("Airports.txt")  # Devuelve una lista de objetos Airport
# FIX 1: LoadAirports ya llama a SetSchengen internamente → no hace falta repetirlo aquí

if len(airports) == 0:  # Si no se pudo cargar el archivo
    print("  Error al cargar el archivo de aeropuertos")
    airports = []  # FIX 2: asegurar que airports siempre existe aunque el archivo falle
else:
    print(f"  Se han cargado {len(airports)} aeropuertos")  # Informo cuántos se cargaron

    # Prueba de agregar un aeropuerto nuevo
    new_airport = Airport("TEST", 50.0, 10.0)  # Creo un aeropuerto de prueba
    SetSchengen(new_airport)
    AddAirport(airports, new_airport)  # Lo agrego a la lista
    print("  Aeropuerto TEST agregado")

    AddAirport(airports, new_airport)  # Intento duplicado → debe ignorarse
    print("  Intento duplicado de TEST (debe ignorarse)")

    RemoveAirport(airports, "TEST")  # Lo elimino de la lista
    print("  Aeropuerto TEST eliminado")

    result = RemoveAirport(airports, "ZZZZ")  # Codigo inexistente → debe devolver -1
    print(f"  RemoveAirport código inexistente devuelve: {result}  (esperado: -1)")

    # Guardar en un archivo solo los aeropuertos Schengen
    SaveSchengenAirports(airports, "schengen_airports.txt")
    print("  Aeropuertos Schengen guardados en schengen_airports.txt")

    # Probar guardar lista vacía → debe devolver -1
    result_empty = SaveSchengenAirports([], "vacio.txt")
    print(f"  SaveSchengenAirports lista vacía devuelve: {result_empty}  (esperado: -1)")

# === Test 5: Gráficos ===
# FIX 2: airports siempre está definida aquí gracias al fix anterior
print("\n5. Probando gráficos...")
if len(airports) > 0:
    PlotAirports(airports)  # Grafico barras apiladas de aeropuertos Schengen / No Schengen
    MapAirports(airports)  # Genero KML para Google Earth
    print("  KML generado en airports.kml")
else:
    print("  No hay aeropuertos para graficar")

print("\n¡Todas las pruebas han finalizado!")
