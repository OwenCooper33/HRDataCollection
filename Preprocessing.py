import numpy as np
import pandas as pd

def preprocess_hr_data(data):
    """
    Preprocess heart rate data for RMSSD calculation.

    Parameters:
        data (pd.DataFrame): DataFrame containing 'time', 'bpm', and 'rr_interval' (in ms).

    Returns:
        np.ndarray: Cleaned RR intervals ready for RMSSD calculation.
    """
    # 1. Drop rows with missing RR intervals
    data = data.dropna(subset=['rr_interval'])

    # 2. Filter out unrealistic RR intervals (below 300ms or above 2000ms)
    data = data[(data['rr_interval'] >= 300) & (data['rr_interval'] <= 2000)]

    # 3. Apply simple smoothing if data is noisy (optional)
    data['rr_interval_smooth'] = data['rr_interval'].rolling(window=3, center=True, min_periods=1).mean()

    return data['rr_interval_smooth'].to_numpy()

def compute_rmssd(rr_intervals):
    """
    Compute RMSSD (Root Mean Square of Successive Differences) for HRV.

    Parameters:
        rr_intervals (np.ndarray): Array of cleaned RR intervals in ms.

    Returns:
        float: RMSSD value.
    """
    # Calculate successive differences
    diff_rr = np.diff(rr_intervals)

    squared_diff = diff_rr ** 2

    mean_squared_diff = np.mean(squared_diff)

    rmssd = np.sqrt(mean_squared_diff)

    return rmssd

# Example Usage:
if __name__ == "__main__":

    data = "hr_data3.csv"

    cleaned_rr = preprocess_hr_data(data)

    rmssd = compute_rmssd(cleaned_rr)
    print(f"RMSSD: {rmssd:.2f} ms")
