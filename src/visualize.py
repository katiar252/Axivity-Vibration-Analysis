import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from src.signal_processing import iso_filter

def plot_first_hour(df_floor, df_below_seat, df_above_seat):
    """
    Plots first hour of z axis data across 3 sensors to visually locate synchronization knocks.
    """

    print("Plotting first hour of Z axis data.")

    #only first hour for plotting 
    start_time = df_floor.index[0]
    end_time = start_time + pd.Timedelta(minutes=60)

    #take first hour
    plot_floor = df_floor.loc[start_time:end_time]
    plot_below = df_below_seat.loc[start_time:end_time]
    plot_above = df_above_seat.loc[start_time:end_time]

    #create figure with 3 subplots (one for each sensor)
    print("Drawing graphs")
    fig, axes = plt.subplots(3,1, figsize=(15,8), sharex=True)

    #plot z axis for each sensor
    axes[0].plot(plot_floor.index, plot_floor['z'], color='blue', label='Floor (Z)')
    axes[0].legend(loc='upper right')
    axes[0].set_ylabel('Acceleration (g)')

    axes[1].plot(plot_below.index, plot_below['z'], color='orange', label='Below Seat (Z)')
    axes[1].legend(loc='upper right')
    axes[1].set_ylabel('Acceleration (g)')

    axes[2].plot(plot_above.index, plot_above['z'], color='green', label='Above Seat (Z)')
    axes[2].legend(loc='upper right')
    axes[2].set_ylabel('Acceleration (g)')

    # Formatting
    plt.xlabel('Time')
    plt.suptitle('Z Axis Acceleration- First 60 minutes')
    plt.tight_layout()
    
    # Open the interactive window
    print("Saving Z axis accelerometry plot to file")
    plt.savefig("Z axis 1 hour.png", dpi=300) 
    print("check file")

    plt.close()



import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

def plot_weighted_psd(floor_data, below_data, above_data, fs=200):
    """
    Calculates and plots the Power Spectral Density (PSD) of the three sensors.
    Shades the area where the seat amplifies (red) and attenuates (green) the floor vibration.
    """
    # calculate PSD using Welch's method
    # nperseg=2048 gives us a smooth frequency resolution of about 0.1 Hz
    freqs, psd_floor = signal.welch(floor_data, fs=fs, nperseg=2048)
    _, psd_below = signal.welch(below_data, fs=fs, nperseg=2048)
    _, psd_above = signal.welch(above_data, fs=fs, nperseg=2048)

    # setup plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # plot floor sensor and above seat PSDs 
    ax.plot(freqs, psd_floor, label='z-floor', color='royalblue', linewidth=1.5)
    ax.plot(freqs, psd_below, label='z-below', color='purple', linewidth=1.5)
    ax.plot(freqs, psd_above, label='z-seat', color='forestgreen', linewidth=1.5)

    # add shading between the floor and the seat
    # Red where seat > floor (Amplification/Hazard)
    ax.fill_between(freqs, psd_floor, psd_above, 
                    where=(psd_above > psd_floor), 
                    interpolate=True, color='lightcoral', alpha=0.5, label='Amplification')
    
    # Green where seat <= floor (Attenuation/Protection)
    ax.fill_between(freqs, psd_floor, psd_above, 
                    where=(psd_above <= psd_floor), 
                    interpolate=True, color='lightgreen', alpha=0.5, label='Attenuation')


    # 6. Formatting to match the reference style
    ax.set_title('Average Weighted PSD', fontweight='bold', fontsize=12)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Weighted PSD')
    
    # Restrict X-axis to 0-30 Hz since WBV energy is predominantly low-frequency
    ax.set_xlim(0, 30)
    
    # Add light grid and legend
    ax.grid(axis='y', linestyle='-', alpha=0.7)
    ax.legend(loc='upper right')
    
    # Light gray background for the plot area
    ax.set_facecolor("#bdc2c7")
    fig.patch.set_facecolor('white')

    plt.tight_layout()

    print("Saving weighted PSD plot to file")
    plt.savefig("Weighted PSD.png", dpi=300) 

    plt.close()


# Calculate and plot ISO filter 
b_wk, a_wk = iso_filter(fs=200, axis='z')
b_wd, a_wd = iso_filter(fs=200, axis='x')   #both x and y axes have the same filter

# Calculate frequency responses using freqz
# worN=8000 calculataes at 8000 frequencies
w_wk, h_wk = signal.freqz(b_wk, a_wk, worN=8000, fs=200)
w_wd, h_wd = signal.freqz(b_wd, a_wd, worN=8000, fs=200)


# Convert complex response 'h' to magnitude in decibels (dB)
# We add a tiny offset to avoid taking log of zero
mag_wk = 20 * np.log10(np.abs(h_wk) + 1e-10)
mag_wd = 20 * np.log10(np.abs(h_wd) + 1e-10)

# Plotting the Bode plot
plt.figure(figsize=(10, 6))

# semilogx- axis is logarithmic for Bode plot
plt.semilogx(w_wk, mag_wk, color='#7fb3d5', linewidth=2, label= r'Vertical $W_k$ (Z axis)')
plt.semilogx(w_wd, mag_wd, color="#ce9d54", linewidth=2, label=r'Horizontal $W_d$ (X,Y axes)')

plt.title('Frequency Response of ISO 2631-1 $W_k$ (Z-Axis) and $W_d$ (X & Y Axes) Filter ', fontsize=14)
plt.xlabel('Frequency $f$ in Hertz', fontsize=12)
plt.ylabel('Magnitude in dB', fontsize=12)

# Set grid
plt.grid(True, which="both", ls="-", color='0.7')

# Set the axis limits
# Nyquist frequency is exactly half your sampling rate (100 Hz)
plt.xlim([0.1, 100]) 
plt.ylim([-60, 10])  

plt.legend(loc='upper left', fontsize=12)
plt.tight_layout()

print("Displaying filter response plot...")
print("Saving ISO filter plot to file")
plt.savefig("ISO filter response.png", dpi=300) 

plt.close()
