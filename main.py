import requests
import pandas as pd
import matplotlib.pyplot as plt

# get data from NYC Open Data API, sensor_id = 100010022 is for brooklyn bridge
endpoint = "https://data.cityofnewyork.us/api/v3/views/ct66-47at/query.json"
query = """
SELECT sensor_id, 
       travelmode, 
       direction, 
       flowid, 
       flowname, 
       timestamp, 
       granularity, 
       counts, 
       status
WHERE sensor_id = '100010022'
ORDER BY timestamp DESC
"""

response = requests.get(endpoint, params={"query": query}, timeout=30)

# error handling for API request
if response.status_code == 200:
    data = response.json()
    #print(data)
else:
    print(f"Error: {response.status_code} - {response.text}")

# convert data to pandas DataFrame
df = pd.DataFrame(data)

# convert dtypes from object to appropriate types
print(df['timestamp'].dtype)
df['counts'] = pd.to_numeric(df['counts'], errors='coerce')
df['travelmode'] = df['travelmode'].astype(str)
df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
df['month'] = pd.to_datetime(df['timestamp']).dt.month
df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek

print(df['travelmode'].value_counts())

# filter out rows with counts <= 0
df = df[df['counts'] > 0]

# get peak traffic based on # of counts
print(df['hour'].value_counts())
df = df[df['hour'].isin([14, 15, 16, 17])]

# save the filtered data to a CSV file
df.to_csv('brooklyn_bridge_bike_data.csv', index=False)