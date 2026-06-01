from airport import IsSchengenAirport  # necessari per FIX 1


import datetime

class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft_id = None
        # Para la V4, necesitamos saber qué objeto Aircraft físico está ocupando la puerta
        self.current_aircraft = None

# Función auxiliar indispensable para la lógica de tiempos de la V4
def string_to_minutes(time_str):
    """Convierte un string 'hh:mm' o 'h:mm' a minutos totales desde el inicio del día."""
    try:
        parts = time_str.strip().split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return 0


class BoardingArea:
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type  # "Schengen" o "non-Schengen"
        self.gates = []


class Terminal:
    def __init__(self, name):
        self.name = name
        self.areas = []
        self.airlines = []


class BarcelonaAP:
    def __init__(self, code):
        self.code = code
        self.terminals = []


# FUNCIONES

def SetGates(area, init_gate, end_gate, prefix):
    if end_gate <= init_gate:
        return -1

    area.gates = []
    for i in range(init_gate, end_gate + 1):
        gate_name = f"{prefix}G{i}"
        area.gates.append(Gate(gate_name))


def LoadAirlines(terminal, t_name):
    filename = f"{t_name}_Airlines.txt"

    try:
        with open(filename, "r") as f:
            terminal.airlines = []
            for line in f:
                parts = line.strip().split("\t")  # el fitxer usa tabuladors
                if len(parts) >= 2:
                    code = parts[-1].strip()
                    terminal.airlines.append(code)
    except FileNotFoundError:
        return -1


def LoadAirportStructure(filename):
    try:
        with open(filename, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        return -1

    # Primera línea: "LEBL 2 terminals"
    first = lines[0].split()
    bcn = BarcelonaAP(first[0])

    i = 1
    while i < len(lines):
        # Línia de terminal: "Terminal T1 5 boarding areas"
        parts = lines[i].split()

        # FIX 4: comprovar que la línia té prou parts abans d'accedir
        if len(parts) < 3:
            i += 1
            continue

        t_name = parts[1]
        num_areas = int(parts[2])

        terminal = Terminal(t_name)
        LoadAirlines(terminal, t_name)

        i += 1

        # Boarding Areas: "Area A Schengen Gates 1 - 11"
        for _ in range(num_areas):
            # FIX 4: comprovar que la línia té prou parts (mínim 7)
            if i >= len(lines):
                break
            parts = lines[i].split()
            if len(parts) < 7:
                i += 1
                continue

            area_name = parts[1]
            area_type = parts[2]  # "Schengen" o "non-Schengen"
            init_gate = int(parts[4])
            end_gate = int(parts[6])

            area = BoardingArea(area_name, area_type)

            prefix = f"{t_name}BA{area_name}"
            SetGates(area, init_gate, end_gate, prefix)

            terminal.areas.append(area)
            i += 1

        bcn.terminals.append(terminal)

    return bcn


def GateOccupancy(bcn):
    result = []

    for t in bcn.terminals:
        for area in t.areas:
            for gate in area.gates:
                result.append({
                    "gate": gate.name,
                    "occupied": gate.occupied,
                    "aircraft": gate.aircraft_id
                })

    return result


def IsAirlineInTerminal(terminal, name):
    # FIX 3: si name és cadena buida retornar False I codi d'error -1 (tal com demana l'enunciat)
    if not name:
        return False, -1

    if len(terminal.airlines) == 0:
        return False, None

    return name in terminal.airlines, None


def SearchTerminal(bcn, name):
    for t in bcn.terminals:
        # FIX 3: IsAirlineInTerminal ara retorna una tupla (found, error_code)
        found, _ = IsAirlineInTerminal(t, name)
        if found:
            return t.name
    return ""


def AssignGate(bcn, aircraft):
    terminal_name = SearchTerminal(bcn, aircraft.airline)

    if terminal_name == "":
        return -1

    # FIX 1: aircraft.py no té atribut .schengen → cal calcular-ho des de l'origen
    is_schengen = IsSchengenAirport(aircraft.origin)

    for t in bcn.terminals:
        if t.name == terminal_name:
            for area in t.areas:

                # comprobar tipo Schengen
                if area.type.lower() == "schengen" and is_schengen:
                    pass
                elif area.type.lower() == "non-schengen" and not is_schengen:
                    pass
                else:
                    continue

                # buscar gate libre
                for gate in area.gates:
                    if not gate.occupied:
                        gate.occupied = True
                        gate.aircraft_id = aircraft.id  # FIX 2: era aircraft.id
                        return gate.name

    return -1


# -----------------------------------------------------------------
# FUNCIONES REQUERIDAS - VERSIÓN 4
# -----------------------------------------------------------------

def LoadDepartures(filename):
    """
    Abre el fichero de salidas y devuelve una lista de objetos Aircraft
    inicializados solo con los datos de salida hallados.
    Si el fichero no existe, retorna una lista vacía y un código de error.
    """
    from aircraft import Aircraft  # Importación local para evitar importaciones circulares
    departures_list = []

    try:
        with open(filename, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        # Devuelve lista vacía y código de error -1 como pide el enunciado
        return [], -1

    # Procesar líneas saltándose la cabecera si existe
    for line in lines:
        line_str = line.strip()
        if not line_str or line_str.startswith("AIRCRAFT"):
            continue

        parts = line_str.split()
        if len(parts) >= 4:
            ac_id = parts[0].strip()
            dest = parts[1].strip()
            dep_time = parts[2].strip()
            airline = parts[3].strip()

            # Instanciar el Aircraft de la clase original
            ac = Aircraft(id=ac_id, airline=airline)
            # Actualizar campos específicos de salida de la V4
            ac.destination = dest
            ac.departure = dep_time
            # Dejar campos de llegada vacíos
            ac.origin = ""
            ac.arrival = ""

            departures_list.append(ac)

    return departures_list, 0


def MergeMovements(arrivals, departures):
    """
    Recibe la lista de arribadas y salidas. Devuelve una nueva lista unificada
    donde se fusionan los datos de aviones con mismo ID y tiempos compatibles
    (llegada anterior a la salida). Soporta múltiples rotaciones diarias.
    """
    if not arrivals or not departures:
        return -1  # Código de error si alguna lista de entrada está vacía

    merged_list = []

    # Copiamos las llegadas para no alterar las listas originales
    for arr in arrivals:
        import copy
        merged_list.append(copy.deepcopy(arr))

    # Buscamos correspondencias con las salidas
    for dep in departures:
        matched = False
        dep_min = string_to_minutes(dep.departure)

        for arr_m in merged_list:
            # Condición: Mismo ID y tiempos compatibles (llegada antes que salida)
            # Además comprobamos que ese espacio de salida no esté ya asignado (por si hay varias escalas)
            if arr_m.id == dep.id and not hasattr(arr_m, 'departure_assigned'):
                arr_min = string_to_minutes(arr_m.arrival)
                if arr_min < dep_min:
                    arr_m.destination = dep.destination
                    arr_m.departure = dep.departure
                    arr_m.departure_assigned = True  # Marcador de control interno
                    matched = True
                    break

        # Si no tiene arribada en todo el día, es un avión nocturno (Night Aircraft)
        if not matched:
            import copy
            night_ac = copy.deepcopy(dep)
            night_ac.origin = ""
            night_ac.arrival = ""
            merged_list.append(night_ac)

    # Limpiar el marcador de control interno antes de retornar la lista
    for ac in merged_list:
        if hasattr(ac, 'departure_assigned'):
            del ac.departure_assigned

    return merged_list


def NightAircraft(aircrafts):
    """
    Devuelve una nueva lista con los aviones que no tienen información de llegada,
    sólo de salida (aviones que han pasado la noche en el aeropuerto).
    """
    if not aircrafts:
        return -1  # Código de error si la lista está vacía

    night_list = []
    for ac in aircrafts:
        # No tiene datos de llegada (origin vacío o llegada vacía) pero sí destino/salida
        has_arrival = hasattr(ac, 'arrival') and ac.arrival != "" and ac.arrival is not None
        has_departure = hasattr(ac, 'departure') and ac.departure != "" and ac.departure is not None

        if not has_arrival and has_departure:
            night_list.append(ac)

    return night_list


def AssignNightGates(bcn, aircrafts):
    """
    Asigna una puerta inicial a los aviones nocturnos (solo datos de salida).
    Llama a AssignGate. Si un avión no cumple el requisito, se salta.
    """
    if not aircrafts:
        return -1

    assigned_count = 0
    for ac in aircrafts:
        has_arrival = hasattr(ac, 'arrival') and ac.arrival != "" and ac.arrival is not None
        has_departure = hasattr(ac, 'departure') and ac.departure != "" and ac.departure is not None

        # Saltarse si el avión no cumple la condición estricta de ser SOLO de salida
        if has_arrival or not has_departure:
            continue

        # Llamamos a AssignGate (versión V3 corregida que acepta el objeto bcn y el avión)
        # Nota: Como AssignGate internamente usa IsSchengenAirport(aircraft.origin), para los de la
        # noche que no tienen origen pasamos temporalmente su destino para evaluar el tipo de zona.
        original_origin = ac.origin
        ac.origin = ac.destination

        gate_name = AssignGate(bcn, ac)

        ac.origin = original_origin  # Restauramos su estado original

        if gate_name != -1:
            # Guardamos la referencia al objeto avión completo dentro del Gate para rastrearlo luego
            for t in bcn.terminals:
                for area in t.areas:
                    for gate in area.gates:
                        if gate.name == gate_name:
                            gate.current_aircraft = ac
                            assigned_count += 1

    return assigned_count


def FreeGate(bcn, id):
    """
    Busca un avión por su ID en todas las puertas del aeropuerto.
    Si lo encuentra, libera la puerta reseteando su estado. Si no, devuelve -1.
    """
    for t in bcn.terminals:
        for area in t.areas:
            for gate in area.gates:
                if gate.occupied and gate.aircraft_id == id:
                    gate.occupied = False
                    gate.aircraft_id = None
                    gate.current_aircraft = None
                    return 0  # Éxito
    return -1  # No encontrado


def AssignGatesAtTime(bcn, aircrafts, time):
    """
    Ejecuta el paso dinámico por franjas horarias:
    1. Libera las puertas cuyos aviones ya hayan despegado antes o durante esta hora.
    2. Asigna puerta a los aviones que aterrizan en el intervalo de 1 hora [time, time + 1h).
    Devuelve el número de aviones que no se pudieron asignar por falta de espacio.
    """
    start_minutes = string_to_minutes(time)
    end_minutes = start_minutes + 60
    unassigned_count = 0

    # FASE 1: Liberar puertas de aviones que ya han despegado
    for t in bcn.terminals:
        for area in t.areas:
            for gate in area.gates:
                if gate.occupied and gate.current_aircraft:
                    ac = gate.current_aircraft
                    if hasattr(ac, 'departure') and ac.departure:
                        dep_min = string_to_minutes(ac.departure)
                        # Si el avión ya despegó antes o justo al inicio de esta franja, se libera la puerta
                        if dep_min <= start_minutes:
                            gate.occupied = False
                            gate.aircraft_id = None
                            gate.current_aircraft = None

    # FASE 2: Asignar puertas a aviones que aterrizan en esta franja horaria
    for ac in aircrafts:
        if hasattr(ac, 'arrival') and ac.arrival:
            arr_min = string_to_minutes(ac.arrival)

            # Comprobar si el aterrizaje entra en el rango de la hora actual de simulación
            if start_minutes <= arr_min < end_minutes:
                gate_name = AssignGate(bcn, ac)
                if gate_name != -1:
                    # Enlazar el avión actual a la puerta física
                    for t in bcn.terminals:
                        for area in t.areas:
                            for gate in area.gates:
                                if gate.name == gate_name:
                                    gate.current_aircraft = ac
                else:
                    unassigned_count += 1

    return unassigned_count


def PlotDayOccupancy(bcn, aircrafts):
    """
    Genera un gráfico que muestra el número total de puertas asignadas en cada terminal
    hora a hora a lo largo del día, junto con la cantidad de vuelos rechazados.
    El estado inicial de bcn debe contener únicamente los aviones nocturnos.
    """
    import matplotlib.pyplot as plt
    import copy

    # Crear una copia profunda del aeropuerto para simular las 24 horas sin romper el bcn real
    bcn_sim = copy.deepcopy(bcn)

    hours = [f"{str(h).zfill(2)}:00" for h in range(24)]

    # Estructuras para almacenar los datos del gráfico
    t1_occupancy = []
    t2_occupancy = []
    unassigned_log = []

    # Simular hora a hora de las 00:00 a las 23:00
    for hour in hours:
        # Ejecutar la asignación dinámica de esa hora
        rejected = AssignGatesAtTime(bcn_sim, aircrafts, hour)
        unassigned_log.append(rejected)

        # Contar cuántas puertas están ocupadas en cada terminal en esta hora exacta
        t1_count = 0
        t2_count = 0
        for t in bcn_sim.terminals:
            count = sum(1 for area in t.areas for gate in area.gates if gate.occupied)
            if t.name.upper() == "T1":
                t1_count = count
            elif t.name.upper() == "T2":
                t2_count = count

        t1_occupancy.append(t1_count)
        t2_occupancy.append(t2_count)

    # Construir el gráfico con matplotlib
    plt.figure(figsize=(12, 6))

    plt.plot(hours, t1_occupancy, label="Ocupación Terminal T1", color="blue", marker="o")
    plt.plot(hours, t2_occupancy, label="Ocupación Terminal T2", color="green", marker="s")
    plt.bar(hours, unassigned_log, label="Vuelos Rechazados (Full)", color="red", alpha=0.5)

    plt.title("Simulación Dinámica de Ocupación del Aeropuerto LEBL - Versión 4")
    plt.xlabel("Franja Horaria del Día")
    plt.ylabel("Cantidad de Aviones / Puertas Ocupadas")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()

    plt.show()

# =========================
# TEST
# =========================

if __name__ == "__main__":

    # Usem la classe Aircraft real en lloc d'un dummy
    from aircraft import Aircraft

    bcn = LoadAirportStructure("LEBL.txt")

    if bcn == -1:
        print("Error loading airport structure (check LEBL.txt exists)")
    else:
        print(f"Airport {bcn.code} loaded with {len(bcn.terminals)} terminals")

        for t in bcn.terminals:
            print(f"  Terminal {t.name}: {len(t.areas)} areas, {len(t.airlines)} airlines")

        # FIX 1+2: usem Aircraft real amb els atributs correctes
        a1 = Aircraft(aircraft_id="TEST1", airline="VLG", origin="EGCC")  # Schengen (UK pre-Brexit era EG, però provem)
        a2 = Aircraft(aircraft_id="TEST2", airline="UPS", origin="KJFK")  # No Schengen

        r1 = AssignGate(bcn, a1)
        r2 = AssignGate(bcn, a2)
        print(f"\nAssignGate TEST1 (VLG, EGCC): {r1}")
        print(f"AssignGate TEST2 (UPS, KJFK): {r2}")

        # Test IsAirlineInTerminal
        found, err = IsAirlineInTerminal(bcn.terminals[0], "VLG")
        print(f"\nIsAirlineInTerminal('VLG'): found={found}, error={err}")
        found, err = IsAirlineInTerminal(bcn.terminals[0], "")
        print(f"IsAirlineInTerminal(''): found={found}, error={err}  (esperado: False, -1)")

        # Mostrar primers 10 gates
        occ = GateOccupancy(bcn)
        print(f"\nGateOccupancy (primers 10 de {len(occ)}):")
        for g in occ[:10]:
            print(f"  {g}")
