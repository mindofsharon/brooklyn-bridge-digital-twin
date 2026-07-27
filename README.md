# Digital Twin of Brooklyn Bridge Bike Path
> Data processing and safety simulation of the Brooklyn Bridge Bike Path using Python and Rockwell Arena software. 

## Preprocessing/Data Files

- **main.py**: main.py fetches data from the NYC Open Data API, calculates averages by day of week and 15-minute increments between 2-6PM for bike and pedestrian travel, and builds plots to visualize these calculations. It also outputs a data file that contains bike and pedestrian inflow/outflow to the Brooklyn Bridge in 15-min increments from 2-6PM.
- **Output**: bike_pedestrian_counts_combined.csv

## Arena Files

- **ISYE6644_BrooklynBridgeDigitalTwin_ArenaFiles_Group266GuptaSchwab.doe**: Arena file
- **ISYE6644_BrooklynBridgeDigitalTwin_ProcessAnalyzer_Group266GuptaSchwab.pan**: Process Analyzer (runs both scenarios)
- **redesign.p**: output results of simulation
- **baseline.p**: output results of simulation
- **redesign.out.txt**: SIMAN report output
- **baseline.out.txt**: SIMAN report output

## Final Report

- **ISYE6644_Group266Topic1_FinalReport.pdf**: Final Report


## Usage Instructions

### Step 1: Prepare Data for Simulation
Clone the repository and run the Python script to convert the raw API data to simulation ready data
  ```bash
   python main.py
   ```
Data is also included in the zip file as bike_pedestrian_counts_combined.csv. 

### Step 2: Run the Arena Simulation 
1. Open 'ISYE6644_BrooklynBridgeDigitalTwin_ArenaFiles_Group266GuptaSchwab.doe' in Arena
2. under Data Definition -> Variable -> PedsInBikeZone - value should be 1 for baseline and 0 for redesign
3. Run the simulation
Note: the current arena files are all set to redesign 
