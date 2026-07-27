# Digital Twin of Brooklyn Bridge Bike Path
> Data processing and safety simulation of the Brooklyn Bridge Bike Path using Python and Rockwell Arena software. 

## Preprocessing/Data Files

-**main.py**: main.py fetches data from the NYC Open Data API, calculates averages by day of week and 15-minute increments between 2-6PM for bike and pedestrian travel, and builds plots to visualize these calculations. It also outputs a data file that contains bike and pedestrian inflow/outflow to the Brooklyn Bridge in 15-min increments from 2-6PM. 

## Arena Files

- **ISYE6644_BrooklynBridgeDigitalTwin_ArenaFiles_Group266GuptaSchwab.doe**: Arena file



## Usage Instructions

### Step 1: Prepare Data for Simulation
Clone the repository and run the Python script to convert the raw API data to simulation ready data
'''bash
python main.py
'''
Data is also included in the zip file. 

### Step 2: Run the Arena Simulation 
1. Open 'ISYE6644_BrooklynBridgeDigitalTwin_ArenaFiles_Group266GuptaSchwab.doe' in Arena
2. Run the simulation
