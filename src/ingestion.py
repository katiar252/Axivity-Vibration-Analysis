import pandas as pd
import matplotlib.pyplot as plt
import scipy.integrate as integrate 
import numpy as np
import os 
from openmovement.load import CwaData
from src.alignment import align_sensors 
from src.visualize import plot_first_hour


def load_sensor_data(filepath):
    """
    Loads Axivity .cwa binary files into a Pandas DataFrame.
    AX3 sensors have no gyroscope data.
    """

    print(f"Loading {filepath}")

    with CwaData(filepath, include_gyro = False) as cwa_data:
        df = cwa_data.get_samples()

    #rename columns for downstream use
    df = df.rename(columns={
        'accel_x': 'x',
        'accel_y': 'y',
        'accel_z': 'z'
    })

    return df


print("Starting pipeline...")

# create data folder if missing
os.makedirs("data", exist_ok = True)

# load data from three raw cwa files with first column as date yy-mm-dd- time AM/PM
# columns 2,3,4: X,Y,Z acceleration (need to orient the sensors properly during setup)
# these files should be in the /data folder

# load cwa file of floor sensor 
floor_file = "data\\19651_HaulAll_stock_June11-16_floor.cwa"

# load cwa file of above-seat sensor
above_seat_file = "data\\105958_HaulAll_stock_June11-16_seat.cwa"

# load cwa file of the below-seat sensor
below_seat_file = "data\\21199_HaulAll_stock_June11-16_belSeat.cwa"

print("\n--- Loading Dataframes ---")
df_floor = load_sensor_data(floor_file)
df_below_seat = load_sensor_data(below_seat_file)
df_above_seat = load_sensor_data(above_seat_file)

print("Files were loaded successfully.")

print("Here are previews of the three sensor datasets.")

print(df_floor.head())
print(df_above_seat.head())
print(df_below_seat.head())

#perform timestamp cropping to find overlapping window and resample to desired frequency (200 Hz)
df_floor, df_above_seat, df_below_seat = align_sensors(df_floor, df_above_seat, df_below_seat, 200)

print("Resampling complete.")

#save data as compressed Python files to /data folder
df_floor.to_pickle("data/floor.pkl")
df_above_seat.to_pickle("data/above_seat.pkl")
df_below_seat.to_pickle("data/below_seat.pkl")

print("Data saved successfully.")

#plot first hour of Z axis data for each of three sensors
plot_first_hour(df_floor, df_below_seat, df_above_seat)


    