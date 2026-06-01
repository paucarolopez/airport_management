# ✈️ Airport Gate Management Tool - Version 4 (Final)

## Project Description
The final version of the suite. This release implements **Dynamic Simulation**. The system now handles aircraft rotations (merging arrivals and departures), manages night aircraft (pernocta), and simulates 24-hour terminal occupancy with visualization of rejected flights.

---

## Version 4 Features
* Time-based Gate Assignment (franjas horarias)
* Aircraft Movement Merging (rotation logic)
* Night Aircraft management
* Dynamic simulation:
  * Automatic gate releasing after takeoff
  * 24-hour occupancy modeling
  * Visualization of rejected flights per hour
* Automated Google Earth integration for KML files

---

## How to Run
1. Make sure all simulation files are present:
   - `LEBL.txt`, `Arrivals.txt`, `Departures.txt`
   - Airline files for each terminal (`T1_Airlines.txt`, `T2_Airlines.txt`)
2. Run `Interface.py`.
3. **For full simulation:** - Load the airport structure.
   - Load arrivals and departures.
   - Use the "Dynamic Simulation" tab to run the 24-hour occupancy plot and generate the `flights.kml` file.
4. Google Earth Pro will open automatically with the generated routes if installed.

---

## Project Structure
* `LEBL.py` → Main simulation and temporal logic
* `aircraft.py` → Parsing and movement processing
* `airport.py` → Foundation and math engine
* `Interface.py` → Final integrated GUI

---

## Team Members
* Pau Caro Lopez
* Aniol Fàbregas Manera
* Jose Ezquerra Carrera
