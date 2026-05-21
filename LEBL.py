from airport import IsSchengenAirport  # necessari per FIX 1


class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft_id = None


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
