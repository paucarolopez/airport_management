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
                parts = line.strip().split()
                if len(parts) >= 2:
                    code = parts[-1]
                    terminal.airlines.append(code)
    except FileNotFoundError:
        return -1


def LoadAirportStructure(filename):
    try:
        with open(filename, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        return -1

    # Primera línea
    first = lines[0].split()
    bcn = BarcelonaAP(first[0])

    i = 1
    while i < len(lines):
        # Terminal
        parts = lines[i].split()
        t_name = parts[1]
        num_areas = int(parts[2])

        terminal = Terminal(t_name)
        LoadAirlines(terminal, t_name)

        i += 1

        # Boarding Areas
        for _ in range(num_areas):
            parts = lines[i].split()

            area_name = parts[1]
            area_type = parts[2]
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
    if not name or len(terminal.airlines) == 0:
        return False
    return name in terminal.airlines


def SearchTerminal(bcn, name):
    for t in bcn.terminals:
        if IsAirlineInTerminal(t, name):
            return t.name
    return ""


def AssignGate(bcn, aircraft):
    terminal_name = SearchTerminal(bcn, aircraft.airline)

    if terminal_name == "":
        return -1

    for t in bcn.terminals:
        if t.name == terminal_name:
            for area in t.areas:

                # comprobar tipo Schengen
                if area.type.lower().startswith("schengen") and aircraft.schengen:
                    pass
                elif area.type.lower().startswith("non") and not aircraft.schengen:
                    pass
                else:
                    continue

                # buscar gate libre
                for gate in area.gates:
                    if not gate.occupied:
                        gate.occupied = True
                        gate.aircraft_id = aircraft.id
                        return gate.name

    return -1


# =========================
# TEST
# =========================

if __name__ == "__main__":

    class DummyAircraft:
        def __init__(self, id, airline, schengen):
            self.id = id
            self.airline = airline
            self.schengen = schengen

    bcn = LoadAirportStructure("LEBL.txt")

    if bcn == -1:
        print("Error loading airport")
    else:
        print("Airport loaded")

        a1 = DummyAircraft("TEST1", "VLG", True)
        a2 = DummyAircraft("TEST2", "UPS", False)

        print("Assign:", AssignGate(bcn, a1))
        print("Assign:", AssignGate(bcn, a2))

        occ = GateOccupancy(bcn)
        for g in occ[:10]:
            print(g)


# ==================
root.mainloop()
