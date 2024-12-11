# data_processing.py

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime

def process_data(parquet_folder, output_csv, minutes_per_bin=60):
    print("Loading taxi data from Parquet files...")
    all_files = glob.glob(os.path.join(parquet_folder, 'yellow_tripdata_2016-*.parquet'))
    df_list = [pd.read_parquet(file) for file in all_files]
    df = pd.concat(df_list, ignore_index=True)

    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])

    print("Filtering invalid PULocationID...")
    df = df[df['PULocationID'].notnull()]
    df = df[df['tpep_pickup_datetime'].notnull()]

    print("Creating time bins...")
    df['time_bin'] = df['tpep_pickup_datetime'].dt.floor(f'{minutes_per_bin}T')

    print("Aggregating pickups per zone per time bin...")
    pickups_aggregated = df.groupby(['PULocationID', 'time_bin']).size().reset_index(name='pickups')

    print("Preparing features...")
    pickups_aggregated['day_of_week'] = pickups_aggregated['time_bin'].dt.dayofweek
    pickups_aggregated['hour'] = pickups_aggregated['time_bin'].dt.hour
    pickups_aggregated['month'] = pickups_aggregated['time_bin'].dt.month
    pickups_aggregated['day'] = pickups_aggregated['time_bin'].dt.day
    pickups_aggregated['year'] = pickups_aggregated['time_bin'].dt.year
    pickups_aggregated['weekend'] = pickups_aggregated['day_of_week'] >= 5

    pickups_aggregated.rename(columns={'PULocationID': 'LocationID'}, inplace=True)

    print(f"Saving processed data to {output_csv}...")
    pickups_aggregated.to_csv(output_csv, index=False)
    print("Data processing completed.")

if __name__ == "__main__":
    parquet_folder = 'data/parquets/'  
    output_csv = 'data/pickups_aggregated.csv'

    os.makedirs('data', exist_ok=True)

    process_data(parquet_folder, output_csv)
