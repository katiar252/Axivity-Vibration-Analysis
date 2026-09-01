import numpy as np
from scipy import signal

def align_sensors(df_floor, df_above_seat, df_below_seat, fs):
    """
    Input three Axivity dataframes and cut data so that the timeframe overlaps for all sensors. 
    Resample to the given sampling rate desired (set to rate tested at).
    """

    # set index to time column 
    df_floor = df_floor.set_index('time')
    df_above_seat = df_above_seat.set_index('time')
    df_below_seat = df_below_seat.set_index('time')


    # find the latest start time and earliest end time from the three sensors
    start_time = max(df_floor.index.min(),
                     df_below_seat.index.min(),
                     df_above_seat.index.min())

    end_time = min(df_floor.index.max(),
                   df_below_seat.index.max(),
                   df_above_seat.index.max())

    print(f"Overlapping time window found for the three sensors: {start_time} to {end_time}")

    # crop all three sensors to this window
    df_floor_crop = df_floor.loc[start_time:end_time]
    df_above_crop = df_above_seat.loc[start_time:end_time]
    df_below_crop = df_below_seat.loc[start_time:end_time]
   

    print("The datasets have been cropped to the overlapped window.")

    #resample to desired frequency
    ms_interval = int(1000/fs)
    freq = f"{ms_interval}ms"
    print(f"Resampling to {fs} Hz")
    
    df_floor_resamp = df_floor_crop.resample(freq).mean().interpolate(method = "linear")
    df_above_resamp = df_above_crop.resample(freq).mean().interpolate(method = "linear")
    df_below_resamp = df_below_crop.resample(freq).mean().interpolate(method = "linear")

    print(f"The resampling to {fs} Hz was successful.")

    return df_floor_resamp, df_above_resamp, df_below_resamp

