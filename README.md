# ✈️ Airport Gate Management Tool - Version 3

## Project Description
This version introduces the **Gate Assignment System**. We have modeled the airport structure (Terminals, Boarding Areas, and Gates) and implemented the logic to assign aircraft to available gates based on operational requirements (Schengen/Non-Schengen).

---

## Version 3 Features
* Full Airport Structure modeling (LEBL data)
* Gate/Terminal/Area hierarchy
* Automated Gate Assignment Algorithm:
  * Airline-to-Terminal mapping
  * Schengen/Non-Schengen compatibility check
* Gate occupancy tracking and manual release

---

## How to Run
1. Ensure the following files exist in the project directory:
   - `LEBL.txt` (Airport structure)
   - `T1_Airlines.txt` & `T2_Airlines.txt` (Airline assignments)
2. Run `Interface.py`.
3. To assign gates manually or test the hierarchy, you can run `LEBL.py` directly to see the console output and gate occupancy status.

---

## Demo Video



[https://youtu.be/IOMGNEMnM4Q](https://youtu.be/KyMU-hvc610)



---

## Project Structure
* `LEBL.py` → Airport operational logic and gate management
* `airport.py` → Infrastructure definitions
* `aircraft.py` → Flight and movement logic

---

## Team Members
* Pau Caro Lopez
* Aniol Fàbregas Manera
* Jose Ezquerra Carrera
