import pandas as pd
import numpy as np
import scipy.signal as signal

def iso_filter(fs, axis):
    """
    Generates the digital b and a coefficients for ISO 2631-1 weightings
    to raw accelerometry data (time domain).
    """

    pi2 = 2 * np.pi
    
    # 1. High-pass filter Hh(s)
    # needed to remove ultra-low frequencies
    f1, Q1 = 0.4, 1/np.sqrt(2)
    w1 = pi2 * f1
    num_h, den_h = [1, 0, 0], [1, w1/Q1, w1**2]     #numerator and denominator coefficients
    
    # 2. Low-pass filter Hl(s)
    # needed to remove very high-frequency noise that is not relevant to human body 
    f2, Q2 = 100.0, 1/np.sqrt(2)
    w2 = pi2 * f2
    num_l, den_l = [w2**2], [1, w2/Q2, w2**2]

    if axis in ['x', 'y']:
        # Wd Weighting (Horizontal)
        # Acceleration-velocity transition

        f3, f4, Q4 = 2.0, 2.0, 0.63
        w3, w4 = pi2 * f3, pi2 * f4
        num_t, den_t = [1, w3], [1, w4/Q4, w4**2]
        
        # Convolve polynomials
        num_total = np.convolve(np.convolve(num_h, num_l), num_t)
        den_total = np.convolve(np.convolve(den_h, den_l), den_t)
        
        # Apply scale factor to numerator
        scale = w4**2 / w3
        num_total = num_total * scale
        
    elif axis == 'z':
        # Wk Weighting (Vertical)
        # Acceleration-velocity transition
        # Coefficients same as above (horizontal axes) from transfer function
        f3, f4, Q4 = 12.5, 12.5, 0.63
        w3, w4 = pi2 * f3, pi2 * f4
        num_t, den_t = [1, w3], [1, w4/Q4, w4**2]
        
        # Upward step Hs(s)
        # Horizontal axes do not have upward step 
        f5, Q5, f6, Q6 = 2.37, 0.91, 3.35, 0.91
        w5, w6 = pi2 * f5, pi2 * f6
        num_s, den_s = [1, w5/Q5, w5**2], [1, w6/Q6, w6**2]
        
        # Convolve polynomials
        num_total = np.convolve(np.convolve(np.convolve(num_h, num_l), num_t), num_s)
        den_total = np.convolve(np.convolve(np.convolve(den_h, den_l), den_t), den_s)
        
        # Apply scale factor (from Acceleration-velocity transition) to numerator
        scale = w4**2 / w3

        num_total = num_total * scale
    else:
        raise ValueError("Axis must be 'x', 'y', or 'z'")
        
    # Convert analog transfer function H(s) to digital H(z) for a rigid time sampling frequency
    b, a = signal.bilinear(num_total, den_total, fs=fs)
    return b, a

def calculate_iso_metrics(filtered_data, dt, t_exp_hours, k_factor = 1.0):
    """"
    Calculates ISO 2631-1 metrics including A(8), Crest Factor, VDV, weighted RMS values
    Default k factor is 1.0 (Z axis)
    """

    # apply k factor weighting multiplier for health according to ISO
    aw = filtered_data * k_factor

    # weighted RMS calculations
    rms = np.sqrt(np.mean(aw**2))

    # crest factor (peak divided by RMS)
    peak = np.max(np.abs(aw))
    crest_factor = peak/ rms 

    # vibration dose value (VDV) 
    vdv = np.sum(aw**4 * dt)**0.25

    # A(8): 8-hour daily equivalent dose
    a8 = rms * np.sqrt(t_exp_hours / 8.0)

    return rms, crest_factor, vdv, a8

def calculate_seat_value(above_active, below_active):
    """
    Calculates SEAT (Seat Effective Amplitude Transmissibility) values.
    SEAT > 100: seat cushion amplifies vibration. 
    SEAT < 100: seat cushion attenuates vibration. 
    """

    rms_above = np.sqrt(np.mean(above_active**2))
    rms_below = np.sqrt(np.mean(below_active**2))

    seat_value = (rms_above / rms_below) * 100

    return seat_value

def extract_active(floor_filtered, below_filtered, above_filtered, dt, threshold=0.1):
    """
    Identifies true exposure time by filtering out parked/engine-off time. 
    Threshold is set at 0.1 m/s^2 by default but can be changed. 
    """
    # Find the minimum length among all three arrays (to account for sensor clock drift)
    min_len = min(len(floor_filtered), len(below_filtered), len(above_filtered))
    
    # Cut all arrays to minimum overlapping length (remove extra samples due to clock drift)
    floor_filtered = floor_filtered[:min_len]
    below_filtered = below_filtered[:min_len]
    above_filtered = above_filtered[:min_len]

    # define rolling window size
    window = int(1.0/ dt)

    # create rolling average of absolute amplitude 
    kernel = np.ones(window) / window
    envelope = np.convolve(np.abs(floor_filtered), kernel, mode='same')

    # Create a boolean mask: True when vibration exceeds the idle threshold
    is_active = envelope > threshold
    
    # Isolate only the data when the vehicle is actively moving
    floor_active = floor_filtered[is_active]
    above_seat_active = above_filtered[is_active]
    below_seat_active = below_filtered[is_active]

    # calculate time of exposure (driving time) in hours 
    t_exp_hours = len(floor_active) *dt /3600


    return floor_active, above_seat_active, below_seat_active, t_exp_hours


