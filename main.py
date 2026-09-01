
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import scipy.signal as signal
from src.signal_processing import iso_filter, calculate_iso_metrics, extract_active, calculate_seat_value
from src.visualize import plot_weighted_psd


#main function- read from pickle files (pre-loaded into /data folder)
def main():
    #  access pickle files from the data folder
    print("Loading cached data...")
    df_floor = pd.read_pickle("data/floor.pkl")
    df_below = pd.read_pickle("data/below_seat.pkl")
    df_above = pd.read_pickle("data/above_seat.pkl")

    # convert g acceleration values into m/s^2
    df_floor[['x', 'y', 'z']] *= 9.80665
    df_below[['x', 'y', 'z']] *= 9.80665
    df_above[['x', 'y', 'z']] *= 9.80665

    # cropping synch knocks (delay 45 minutes, and cut off last 45 minutes)
    print("Cropping synchronization knocks, based on the first-hour window")
    crop_minutes = 45
    # determine number of samples based on sampling rate of 200 
    crop_samples = int(crop_minutes * 60 * 200)

    # slice off beginning and end of dataframes
    df_floor = df_floor.iloc[crop_samples:-crop_samples]
    df_below = df_below.iloc[crop_samples:-crop_samples]
    df_above = df_above.iloc[crop_samples:-crop_samples]   


    # check axis orientation to make sure z axis is actually vertical (z axis should be around 9.81) 
    # based on short window following cropped section; we assume the vehicle is parked here
    for name, df in [('floor', df_floor), ('below', df_below), ('above', df_above)]:
        parked_window = df.iloc[crop_samples:crop_samples + 12000]  # take small window where vehicle is parked 
        print(f"{name} (parked, raw): mean x={parked_window['x'].mean():.2f}, "
          f"y={parked_window['y'].mean():.2f}, z={parked_window['z'].mean():.2f}")    

    # obtain ISO filter coefficients for each axis with sampling rate 200 Hz 
    b_wk, a_wk = iso_filter(fs=200, axis='z')
    b_wd, a_wd = iso_filter(fs = 200, axis = 'x')

    # apply time-domain filter to Z axis for each sensor
    print("Filtering Z-axis data for each sensor...")
    floor_z_filtered = signal.lfilter(b_wk, a_wk, df_floor['z'])
    below_z_filtered = signal.lfilter(b_wk, a_wk, df_below['z'])
    above_z_filtered = signal.lfilter(b_wk, a_wk, df_above['z'])

    # Measure the exact z acceleration background noise of the parked vehicle
    parked_noise = np.mean(np.abs(floor_z_filtered[0:12000]))
    print(f"DIAGNOSTIC - Parked Sensor Noise Floor: {parked_noise:.4f} m/s^2")

    # extract active driving time 
    print("Trimming away inactive parked time...")

    dt = 1 / 200  # Timestep in seconds

    # obtain active driving for each sensor (z axis only)
    # set threshold at 0.075 m/s^2 [determined empirically- but can be changed]
    floor_active, above_active, below_active, true_t_exp = extract_active(
        floor_filtered=floor_z_filtered, 
        below_filtered=below_z_filtered, 
        above_filtered=above_z_filtered, 
        dt=dt, 
        threshold=0.075
    )

    print(f"Detected True Driving Time: {true_t_exp:.2f} hours")

    #  Calculate vibration metrics on active driving data according to ISO metrics 
    print("Calculating vibration metrics...")    
    # Calculate all metrics for the floor sensor (z axis only)
    rms_floor, cf_floor, vdv_floor, a8_floor = calculate_iso_metrics(
        floor_active, 
        dt=dt, 
        t_exp_hours=true_t_exp, 
        k_factor=1.0
    )

    # Calculate all metrics for Below Seat sensor (z axis only)
    rms_below, cf_below, vdv_below, a8_below = calculate_iso_metrics(
        below_active, 
        dt=dt, 
        t_exp_hours=true_t_exp, 
        k_factor=1.0
    )

    # Calculate all metrics for Above Seat sensor (z axis only)
    rms_above, cf_above, vdv_above, a8_above = calculate_iso_metrics(
        above_active, 
        dt=dt, 
        t_exp_hours=true_t_exp, 
        k_factor=1.0
    )   

    # Calculate SEAT value (cushion transmissibility)
    seat_value = calculate_seat_value(above_active, below_active)

    # Generate the PSD Graph which saves to directory
    print("Generating PSD visualization...")
    plot_weighted_psd(floor_active, below_active, above_active, fs=200)
    
    # print specific vibration metrics 
    print("\n--- Vibration Dose Values (Z axis only)---")
    print(f"Floor VDV:      {vdv_floor:.2f} m/s^1.75")
    print(f"Below Seat VDV: {vdv_below:.2f} m/s^1.75")
    print(f"Above Seat VDV: {vdv_above:.2f} m/s^1.75")
    print("-" * 30)
    
    print("\n--- Additional Health Metrics (Z axis only)---")
    print(f"Above Seat Crest Factor: {cf_above:.1f}")
    print(f"Floor Crest Factor: {cf_floor:.1f}")
    print(f"Above Seat A(8):         {a8_above:.3f} m/s^2")
    print(f"Floor A(8):              {a8_floor:.3f} m/s^2")
    print(f"Below Seat A(8):         {a8_below:.3f} m/s^2")

    print("\n--- Seat Cushion Transmissibility ---")
    print(f"SEAT value = {seat_value}%")
    # check if seat cushion is amplifying or attenuating vibration (over full frequency range)
    if seat_value > 100:
        print(f"Cushion is amplifying vibration by {seat_value - 100:1f}%")
    else: 
        print(f"The seat cushion is attenuating vibration by {100- seat_value:.1f}%")

if __name__ == "__main__":
    main()
