
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')  # Force TkAgg backend
from scipy import stats
from scipy.signal import welch
import csv

csv_file = "hrv_data.csv"
def read_csv():
    #Reads stored RR intervals and heart rate data from CSV
    timestamps, heart_rates, rr_intervals = [], [], []
    try:
        with open(csv_file, "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                timestamp, hr, rr = float(row[0]), int(row[1]), float(row[2])
                if hr > 0:
                    timestamps.append(timestamp)
                    heart_rates.append(hr)
                    rr_intervals.append(rr)
    except FileNotFoundError:
        print("No data file found.")
    return timestamps, heart_rates, rr_intervals

# calculating the HRV with RMSSD and Baevsky index
#calculates RMSSD HRV
def calc_RMSSD(rr_intervals):
    if len(rr_intervals) < 2:
        return np.nan
    rr_diff = np.diff(rr_intervals)
    return np.sqrt(np.mean(rr_diff ** 2))

#calculates Baevsky index HRV
def calc_Baevsky(rr_intervals):
    if len(rr_intervals) == 0:
        return np.nan
    mode_rr = stats.mode(rr_intervals, keepdims=True).mode[0]
    median_rr = np.median(rr_intervals)
    max_rr = np.max(rr_intervals)
    min_rr = np.min(rr_intervals)
    mxdmn = max_rr - min_rr
    #to avoid dividing by 0
    if mxdmn == 0:
        return np.nan

    return (mode_rr * 100) / (2 * median_rr * mxdmn)

def process_data():

    timestamps, heart_rates, rr_intervals = read_csv()

    if len(rr_intervals) == 0:
        print("No data collected.")
        return

    rmssd_HRV = calc_RMSSD(rr_intervals) * 1000
    Baevsky_HRV = calc_Baevsky(rr_intervals)

    print(f"HRV(RMSSD): {rmssd_HRV:.2f} ms")
    print(f"Baevsky Index: {Baevsky_HRV:.2f}")

    plt.figure(figsize=(10, 5))
    plt.scatter(timestamps, rr_intervals, color='b', label="RR Intervals (s)")
    plt.xlabel("Time (s)")
    plt.ylabel("RR Interval (s)")
    plt.title("RR Intervals Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("rr_intervals_plot.png")

    plt.figure(figsize=(10, 5))
    plt.scatter(timestamps, heart_rates, color='b', label="Heart Rate (bpm)")
    plt.xlabel("Time (s)")
    plt.ylabel("Heart Rate (bpm)")
    plt.title("HR Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("hr_plot.png")

    rmssd_values = [calc_RMSSD(rr_intervals[:i]) * 1000 for i in range(2, len(rr_intervals) + 1)]
    rmssd_timestamps = timestamps[1:]

    plt.figure(figsize=(10, 5))
    plt.plot(rmssd_timestamps, rmssd_values, color='g', linestyle='-', marker='o', label="RMSSD HRV")
    plt.xlabel("Time (s)")
    plt.ylabel("RMSSD HRV (ms)")
    plt.title("RMSSD HRV Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("rmssd_hrv_plot.png")

    baevsky_values = [calc_Baevsky(rr_intervals[:i]) for i in range(1, len(rr_intervals) + 1)]
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, baevsky_values, color='r', linestyle='-', marker='o', label="Baevsky Index")
    plt.xlabel("Time (s)")
    plt.ylabel("Baevsky Index")
    plt.title("Baevsky Index Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("baevsky_index_plot.png")

    #to match the actual sampling frequency of the hr values
    num_valus = len(heart_rates)
    fs_rr = 1 / np.mean(np.diff(timestamps))

    fft_vals = np.fft.fft(heart_rates)
    fft_freqs = np.fft.fftfreq(num_valus, d=1/fs_rr)

    # Keep only positive frequencies
    positive_freqs = fft_freqs[:num_valus // 2]
    positive_fft_vals = np.abs(fft_vals[:num_valus // 2])

    # Plot Fourier Transform
    plt.figure()
    plt.plot(positive_freqs, positive_fft_vals)
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Magnitude')
    plt.title('Fourier Transform of Heart Rate')
    plt.grid()
    plt.semilogy(positive_freqs, positive_fft_vals)
    plt.savefig("Fourier_Transform.png")
    plt.show()

    f, Pxx = welch(heart_rates, fs=fs_rr, nperseg=min(256, len(heart_rates)))

    plt.figure(figsize=(10, 5))
    plt.semilogy(f, Pxx, color='b')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Power Spectral Density')
    plt.title('Power Spectral Density of Heart Rate')
    plt.grid()
    plt.savefig("PSD.png")
    plt.show()

if __name__ == "__main__":
    process_data()
