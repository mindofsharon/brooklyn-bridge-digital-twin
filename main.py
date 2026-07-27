import requests
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------
# get data from NYC Open Data API
# -------------------------------

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

endpoint2 = "https://data.cityofnewyork.us/api/v3/views/6fi9-q3ta/query.json"
query2 = '''
SELECT hour_beginning,
       location,
       Pedestrians,
       towards_manhattan,
       towards_brooklyn
WHERE location = 'Brooklyn Bridge'
ORDER BY hour_beginning 
'''

response = requests.get(endpoint, params={"query": query}, timeout=30)
response2 = requests.get(endpoint2, params={"query": query2}, timeout=30)

# error handling for API request
if response.status_code == 200:
    data = response.json()
    #print(data)
else:
    print(f"Error: {response.status_code} - {response.text}")

if response2.status_code == 200:
    data2 = response2.json()
    #print(data2)
else:
    print(f"Error: {response2.status_code} - {response2.text}") 

# convert data to pandas DataFrame
df = pd.DataFrame(data)
df_pedestrian = pd.DataFrame(data2)

# -------------------------------
# data cleaning and preprocessing
# -------------------------------

# convert dtypes from object to appropriate types
print(df['timestamp'].dtype)
df['counts'] = pd.to_numeric(df['counts'], errors='coerce')
df['travelmode'] = df['travelmode'].astype(str)
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
df['day'] = pd.to_datetime(df['timestamp']).dt.day
df['month'] = pd.to_datetime(df['timestamp']).dt.month
df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
df['year'] = pd.to_datetime(df['timestamp']).dt.year
df['hour_minute'] = pd.to_datetime(df['timestamp']).dt.strftime('%H:%M')

df_pedestrian['Pedestrians'] = pd.to_numeric(df_pedestrian['Pedestrians'], errors='coerce')
df_pedestrian['towards_manhattan'] = pd.to_numeric(df_pedestrian['towards_manhattan'], errors='coerce')
df_pedestrian['towards_brooklyn'] = pd.to_numeric(df_pedestrian['towards_brooklyn'], errors='coerce')
df_pedestrian['hour_beginning'] = pd.to_datetime(df_pedestrian['hour_beginning'])
df_pedestrian['hour_minute'] = df_pedestrian['hour_beginning'].dt.strftime('%H:%M')
df_pedestrian['year'] = df_pedestrian['hour_beginning'].dt.year
df_pedestrian['day_of_week'] = df_pedestrian['hour_beginning'].dt.dayofweek
df_pedestrian['hour'] = df_pedestrian['hour_beginning'].dt.hour

df = df.sort_values(by='timestamp')

print(df['travelmode'].value_counts())

# filter out rows with counts <= 0
df = df[df['counts'] > 0]
df_pedestrian = df_pedestrian[df_pedestrian['Pedestrians'] > 0]

# filter for year 2019
df = df[df['year'] == 2019]
df_pedestrian = df_pedestrian[df_pedestrian['year'] == 2019]

# get peak traffic based on # of counts
print(df['hour'].value_counts())
df = df[df['hour'].isin([14, 15, 16, 17, 18])]
df_pedestrian = df_pedestrian[df_pedestrian['hour'].isin([14, 15, 16, 17, 18])]

# bike counts by day of week, 15 min increments, and direction
day_of_week_avg = (
    df.groupby(['day_of_week', 'hour_minute', 'direction'], as_index=False)
      .agg(
            avg_counts=('counts', 'mean'),
            std_counts=('counts', 'std'),
            min_counts=('counts', 'min'),
            max_counts=('counts', 'max')
        )
      .rename(columns={
            'avg_counts': 'avg_counts_by_day_of_week',
            'std_counts': 'std_counts_by_day_of_week',
            'min_counts': 'min_counts_by_day_of_week',
            'max_counts': 'max_counts_by_day_of_week'
        })
      .round(2)
      .sort_values(['day_of_week', 'hour_minute', 'direction'])
)

# bike counts by day of week, hourly increments, and direction
day_of_week_avg_by_hour = (
    df.groupby(['day_of_week', 'hour', 'direction'], as_index=False)
      .agg(
            avg_counts=('counts', 'mean'),
            std_counts=('counts', 'std'),
            min_counts=('counts', 'min'),
            max_counts=('counts', 'max')
        )
      .rename(columns={
            'avg_counts': 'avg_counts_by_day_of_week_hourly',
            'std_counts': 'std_counts_by_day_of_week_hourly',
            'min_counts': 'min_counts_by_day_of_week_hourly',
            'max_counts': 'max_counts_by_day_of_week_hourly'
        })
      .round(2)
      .sort_values(['day_of_week', 'hour', 'direction'])
)

# rename columns for pedestrian data and select relevant columns
df_pedestrian.rename(columns={'Pedestrians': 'pedestrian_count', 'towards_manhattan': 'in', 'towards_brooklyn': 'out', 'hour_beginning': 'timestamp'}, inplace=True)
df_pedestrian = df_pedestrian[['timestamp', 'hour_minute', 'day_of_week', 'pedestrian_count', 'in', 'out']]

# pedestrian counts by day of week, hourly increments, and direction
pedestrian_day_of_week_avg = (
    df_pedestrian.groupby(['day_of_week', 'hour_minute'], as_index=False)[['pedestrian_count', 'in', 'out']]
      .agg(
          avg_pedestrian_count=('pedestrian_count', 'mean'),
          std_pedestrian_count=('pedestrian_count', 'std'),
          min_pedestrian_count=('pedestrian_count', 'min'),
          max_pedestrian_count=('pedestrian_count', 'max'),
          avg_in=('in', 'mean'),
          std_in=('in', 'std'),
          min_in=('in', 'min'),
          max_in=('in', 'max'),
          avg_out=('out', 'mean'),
          std_out=('out', 'std'),
          min_out=('out', 'min'),
          max_out=('out', 'max')
      )
      .rename(columns={
          'avg_pedestrian_count': 'avg_pedestrian_count_by_day_of_week',
          'std_pedestrian_count': 'std_pedestrian_count_by_day_of_week',
          'min_pedestrian_count': 'min_pedestrian_count_by_day_of_week',
          'max_pedestrian_count': 'max_pedestrian_count_by_day_of_week',
          'avg_in': 'avg_in_by_day_of_week',
          'std_in': 'std_in_by_day_of_week',
          'min_in': 'min_in_by_day_of_week',
          'max_in': 'max_in_by_day_of_week',
          'avg_out': 'avg_out_by_day_of_week',
          'std_out': 'std_out_by_day_of_week',
          'min_out': 'min_out_by_day_of_week',
          'max_out': 'max_out_by_day_of_week'
      })
      .sort_values(['day_of_week', 'hour_minute'])
      .round(2)
)

# pedestrian counts by hourly increments, and direction
pedestrian_week_avg_by_hour = (
    df_pedestrian.groupby(['hour_minute'], as_index=False)[['pedestrian_count', 'in', 'out']]
      .mean()
      .rename(columns={
          'pedestrian_count': 'avg_pedestrian_count_by_hour',
          'in': 'avg_in_by_hour',
          'out': 'avg_out_by_hour'
      })
      .sort_values(['hour_minute'])
)

# -------------------------------
# sum of bikes/pedestrians by day
# -------------------------------
bike_daily_totals = (
    df.assign(date=df['timestamp'].dt.date)
      .groupby(['date', 'direction'], as_index=False)['counts']
      .sum()
      .rename(columns={'counts': 'bike_total'})
      .sort_values(['date', 'direction'])
)

bike_daily_totals = bike_daily_totals.pivot_table(
    index='date',
    columns='direction',
    values='bike_total',
    aggfunc='sum'
).reset_index().rename(columns={'in': 'bike_in_total', 'out': 'bike_out_total'})

pedestrian_daily_totals = (
    df_pedestrian.assign(date=df_pedestrian['timestamp'].dt.date)
      .groupby('date', as_index=False)[['pedestrian_count', 'in', 'out']]
      .sum()
      .rename(columns={
          'pedestrian_count': 'pedestrian_total',
          'in': 'pedestrian_in_total',
          'out': 'pedestrian_out_total'
      })
      .sort_values('date')
)

daily_totals = (
    bike_daily_totals.merge(pedestrian_daily_totals, on='date', how='outer')
      .sort_values('date')
)

print(daily_totals)


# -------------------------------
# Plot bikes and pedestrians on separate figures, with in/out on the same plot
# -------------------------------
# Bike figure (15-minute slots)
bike_slot_frame = pd.DataFrame({'slot': [f"{hour:02d}:{minute:02d}" for hour in range(14, 18) for minute in [0, 15, 30, 45]]})

bike_in_plot = (
    df[df['direction'] == 'in']
    .assign(slot=df.loc[df['direction'] == 'in', 'timestamp'].dt.floor('15min').dt.strftime('%H:%M'))
    .groupby('slot', as_index=False)['counts']
    .mean()
    .rename(columns={'counts': 'avg_bike_in'})
)

bike_out_plot = (
    df[df['direction'] == 'out']
    .assign(slot=df.loc[df['direction'] == 'out', 'timestamp'].dt.floor('15min').dt.strftime('%H:%M'))
    .groupby('slot', as_index=False)['counts']
    .mean()
    .rename(columns={'counts': 'avg_bike_out'})
)

bike_plot_data = bike_slot_frame.merge(bike_in_plot, on='slot', how='left').merge(bike_out_plot, on='slot', how='left').fillna(0)

fig_bike, ax_bike = plt.subplots(figsize=(12, 6))
ax_bike.plot(range(len(bike_plot_data)), bike_plot_data['avg_bike_in'], marker='o', linewidth=2, label='Bike In', color='tab:blue')
ax_bike.plot(range(len(bike_plot_data)), bike_plot_data['avg_bike_out'], marker='s', linewidth=2, label='Bike Out', color='tab:orange')
ax_bike.set_title('Bike Counts by 15-Minute Slot')
ax_bike.set_ylabel('Average count')
ax_bike.set_xlabel('Time slot')
ax_bike.set_xticks(range(len(bike_plot_data)))
ax_bike.set_xticklabels(bike_plot_data['slot'], rotation=45)
ax_bike.legend()
ax_bike.grid(alpha=0.2)
plt.tight_layout()
plt.show()

# Pedestrian figure (hourly slots)
pedestrian_slot_frame = pd.DataFrame({'slot': [f"{hour:02d}:00" for hour in range(14, 18)]})

pedestrian_in_plot = (
    df_pedestrian.assign(slot=df_pedestrian['timestamp'].dt.floor('h').dt.strftime('%H:00'))
    .groupby('slot', as_index=False)['in']
    .mean()
    .rename(columns={'in': 'avg_pedestrian_in'})
)

pedestrian_out_plot = (
    df_pedestrian.assign(slot=df_pedestrian['timestamp'].dt.floor('h').dt.strftime('%H:00'))
    .groupby('slot', as_index=False)['out']
    .mean()
    .rename(columns={'out': 'avg_pedestrian_out'})
)

pedestrian_plot_data = pedestrian_slot_frame.merge(pedestrian_in_plot, on='slot', how='left').merge(pedestrian_out_plot, on='slot', how='left').fillna(0)

fig_ped, ax_ped = plt.subplots(figsize=(12, 6))
ax_ped.plot(range(len(pedestrian_plot_data)), pedestrian_plot_data['avg_pedestrian_in'], marker='o', linewidth=2, label='Pedestrian In', color='tab:green')
ax_ped.plot(range(len(pedestrian_plot_data)), pedestrian_plot_data['avg_pedestrian_out'], marker='s', linewidth=2, label='Pedestrian Out', color='tab:red')
ax_ped.set_title('Pedestrian Counts by Hour')
ax_ped.set_ylabel('Average count')
ax_ped.set_xlabel('Time slot')
ax_ped.set_xticks(range(len(pedestrian_plot_data)))
ax_ped.set_xticklabels(pedestrian_plot_data['slot'], rotation=45)
ax_ped.legend()
ax_ped.grid(alpha=0.2)
plt.tight_layout()
plt.show()
