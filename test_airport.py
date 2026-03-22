# test_airport.py (complete version)
from airport import *

print("=== FULL SYSTEM TEST ===")

# Test 1: Basic functionality
print("\n1. Testing Airport class...")
airport = Airport("LEBL", 41.297445, 2.0832941)
SetSchengen(airport)
PrintAirport(airport)

# Test 2: File operations
print("\n2. Testing file load/save...")
airports = LoadAirports("airports.txt")
print(f"Loaded {len(airports)} airports")

if airports:
    # Set Schengen for all
    for ap in airports:
        SetSchengen(ap)

    # Test add/remove
    new_airport = Airport("TEST", 50.0, 10.0)
    AddAirport(airports, new_airport)
    RemoveAirport(airports, "TEST")

    # Save Schengen airports
    SaveSchengenAirports(airports, "schengen_airports.txt")

# Test 3: Graphics
print("\n3. Testing graphics...")
if airports:
    PlotAirports(airports)
    MapAirports(airports)

print("\nAll tests completed!")