import asyncio
import time
import numpy as np
import matplotlib.pyplot as plt
from bleak import BleakClient
from scipy import stats
from scipy.signal import welch

# Wahoo TICKR btle and  UUID
HRM_SERVICE_UUID = '0000180d-0000-1000-8000-00805f9b34fb'
HRM_CHAR_UUID = '00002a37-0000-1000-8000-00805f9b34fb'

time_stamps = []
rr_intervals = []
async def hr_data_handler(sender, data):
# gets the hr from the hr sensro incoming data
# checks the "flag" byte to see if the hr is stored in one or two
# bytes and reads in the appropriate byte
    flag = data[0]
    hr_value = data[1]  # Heart rate value is usually the second byte

    print(f"Heart Rate: {hr_value} bpm")  # Print the HR value each time it's read

    if flag & 0x10:
        rr_bytes = data[2:]
        for i in range(0, len(rr_bytes), 2):
            rr_interval = int.from_bytes(rr_bytes[i:i+2], byteorder='little') / 1000.0
            rr_intervals.append(rr_interval)
            time_stamps.append(time.time())

# calculating the HRV with RMSSD and Baevsky index
#calculates RMSSD HRV
def calc_RMSSD(RR):
    if len(RR) < 2:
        return np.nan
    rr_diff = np.diff(RR)
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
    return (mode_rr * 100) / (2 * median_rr * mxdmn)

async def main():
    #get teh adress from Scanner.py
    device_address = input("Enter Wahoo TICKR address: ")
#connects the hr sensor
    async with BleakClient(device_address) as client:
        if not client.is_connected:
            print("Failed to connect")
            return
#starts the connection
        await client.start_notify(HRM_CHAR_UUID, hr_data_handler)

        print("Collecting data, press Ctrl+C to stop...")

        try:
            while True:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            await client.stop_notify(HRM_CHAR_UUID)

        if len(rr_intervals) == 0:
            print("No data collected.")
            return


        rmssd_HRV = calc_RMSSD(rr_intervals)
        Baevsky_HRV = calc_Baevsky(rr_intervals)

        print(f"HRV(RMSSD): {rmssd_HRV:.2f} seconds")
        print(f"Baevsky Index: {Baevsky_HRV:.2f}")

        f, Pxx = welch(rr_intervals, fs=4, nperseg=min(256, len(rr_intervals)))

        plt.figure()
        plt.plot(time_stamps, rr_intervals, marker='o', color='b', label="RR Intervals (s)")
        plt.xlabel("Time (s)")
        plt.ylabel("RR Interval (s)")
        plt.title("RR Intervals Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()

        plt.figure()
        plt.semilogy(f, Pxx)
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Power Spectral Density')
        plt.title('Power Spectral Density of HRV')
        plt.grid()
        plt.show()


if __name__ == "__main__":
    asyncio.run(main())

    #40ED4EEF-107E-2438-6DC1-8C57CCE2563A
