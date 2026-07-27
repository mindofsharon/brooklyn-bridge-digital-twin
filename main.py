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
df = df[df['hour'].isin([14, 15, 16, 17])]
df_pedestrian = df_pedestrian[df_pedestrian['hour'].isin([14, 15, 16, 17])]

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

# hourly bike counts by 15 min increments and direction (averaged across all days of week)
day_of_week_avg_15_min = (
    df.groupby(['hour_minute', 'direction'], as_index=False)
      .agg(
            avg_counts=('counts', 'mean'),
            std_counts=('counts', 'std'),
            min_counts=('counts', 'min'),
            max_counts=('counts', 'max')
        )
      .rename(columns={
            'avg_counts': 'avg_counts',
            'std_counts': 'std_counts',
            'min_counts': 'min_counts',
            'max_counts': 'max_counts'
        })
      .round(2)
      .sort_values([ 'hour_minute', 'direction'])
)

day_of_week_avg_15_min['avg_counts'] = day_of_week_avg_15_min['avg_counts'] * 4

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

# expand each hourly value into 4 quarter-hour slots and divide by 4 to get 15-minute averages
pedestrian_week_avg_by_hour_15min = []
for _, row in pedestrian_week_avg_by_hour.iterrows():
    hour = int(row['hour_minute'][:2])
    for minute in [0, 15, 30, 45]:
        pedestrian_week_avg_by_hour_15min.append({
            'hour_minute': f'{hour:02d}:{minute:02d}',
            'avg_pedestrian_count_by_hour_15min': row['avg_pedestrian_count_by_hour'] / 4,
            'avg_in_by_hour_15min': row['avg_in_by_hour'] / 4,
            'avg_out_by_hour_15min': row['avg_out_by_hour'] / 4,
        })

pedestrian_week_avg_by_hour_15min = pd.DataFrame(pedestrian_week_avg_by_hour_15min).sort_values('hour_minute')

# -------------------------------
# avg of bikes/pedestrians 
# -------------------------------

df['counts'].describe()
df_pedestrian['pedestrian_count'].describe()

# -------------------------------
# Plot bikes and pedestrians in one figure with two subplots
# -------------------------------

# plot bike counts by 15-minute increments
plot_data = day_of_week_avg_15_min.pivot(index='hour_minute', columns='direction', values='avg_counts').reset_index()
plot_data.rename(columns={'in': 'manhattan bound', 'out': 'brooklyn bound'}, inplace=True)

# plot pedestrian counts by 15-minute increments
plot_data_pedestrian = pedestrian_week_avg_by_hour_15min.copy()
plot_data_pedestrian.rename(columns={'avg_in_by_hour_15min': 'manhattan bound', 'avg_out_by_hour_15min': 'brooklyn bound'}, inplace=True)
plot_data_pedestrian['manhattan bound'] = plot_data_pedestrian['manhattan bound'] * 4
plot_data_pedestrian['brooklyn bound'] = plot_data_pedestrian['brooklyn bound'] * 4

fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# bike subplot
axes[0].plot(plot_data['hour_minute'], plot_data['manhattan bound'], marker='o', linewidth=2, label='Manhattan Bound', color='tab:blue')
axes[0].plot(plot_data['hour_minute'], plot_data['brooklyn bound'], marker='s', linewidth=2, label='Brooklyn Bound', color='tab:orange')
axes[0].set_title('Hourly Bike Counts by 15-Minute Slot (2019)')
axes[0].set_ylabel('Average count')
axes[0].legend()
axes[0].grid(alpha=0.2)

# pedestrian subplot
axes[1].plot(plot_data_pedestrian['hour_minute'], plot_data_pedestrian['manhattan bound'], marker='o', linewidth=2, label='Manhattan Bound', color='tab:green')
axes[1].plot(plot_data_pedestrian['hour_minute'], plot_data_pedestrian['brooklyn bound'], marker='s', linewidth=2, label='Brooklyn Bound', color='tab:red')
axes[1].set_title('Hourly Pedestrian Counts by 15-Minute Slot (2019)')
axes[1].set_ylabel('Average count')
axes[1].set_xlabel('Time slot')
axes[1].legend()
axes[1].grid(alpha=0.2)

plt.tight_layout()
plt.show()