class Airport:
   def __init__(self, code, lat, lon):
       self.code = code
       self.lat = lat
       self.lon = lon
       self.schengen = False
       self.coordinates = (lat, lon)


def IsSchengenAirport(code):
   if not code:
       return False


   schengen_codes = ("LO", 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG',
       'EH', 'LH', 'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP',
       'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS')


   return code[:2] in schengen_codes


def SetSchengen(airport):
   airport.schengen = IsSchengenAirport(airport.code)


def PrintAirport(airport):
   print("Code: ", airport.code)
   print("Coordinates: ", airport.coordinates)
   print("Schengen: ", airport.schengen)




def convert_coord(coord):
   direction = coord[0]
   deg = int(coord[1:3])
   minutes = int(coord[3:5])
   seconds = int(coord[5:7])


   decimal = deg + minutes/60 + seconds/3600


   if direction in ['S', 'W']:
       decimal = -decimal


   return decimal




def LoadAirports(Airports):
   airports = []
   try:
       with open(Airports, 'r') as f:
           next(f)  # skip header
           for line in f:
               parts = line.split()
               code = parts[0]
               lat = convert_coord(parts[1])
               lon = convert_coord(parts[2])


               airport = Airport(code, lat, lon)
               airports.append(airport)
   except:
       return []
   return airports


def SaveSchengenAirports(airports, filename):
   if not airports:
       return -1


   with open(filename, 'w') as f:
       f.write("CODE LAT LON\n")
       for a in airports:
           if a.schengen:
               f.write(f"{a.code} {a.lat} {a.lon}\n")




def AddAirport(airports, airport):
   for a in airports:
       if a.code == airport.code:
           return
   airports.append(airport)




def RemoveAirport(airports, code):
   for a in airports:
       if a.code == code:
           airports.remove(a)
           return
   return -1






import matplotlib.pyplot as plt




def PlotAirports(airports):
   schengen = sum(1 for a in airports if a.schengen)
   non_schengen = len(airports) - schengen


   plt.bar(["Airports"], [schengen], label="Schengen")
   plt.bar(["Airports"], [non_schengen], bottom=[schengen], label="Non-Schengen")


   plt.legend()
   plt.title("Airports Distribution")
   plt.show()




def MapAirports(airports):
   with open("airports.kml", "w") as f:
       f.write("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
""")


       for a in airports:
           color = "red" if a.schengen else "blue"


           f.write(f"""
<Placemark>
   <name>{a.code}</name>
   <Style>
       <IconStyle>
           <color>{color}</color>
       </IconStyle>
   </Style>
   <Point>
       <coordinates>{a.lon},{a.lat},0</coordinates>
   </Point>
</Placemark>
""")
