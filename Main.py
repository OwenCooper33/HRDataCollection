import numpy as np
import time
import serial
import matplotlib.pyplot as plt
from openant.easy.node import Node
from openant.easy.channel import Channel
from scipy import stats

USB_PORT = "" #when i get the ANT+ dongle it will go here

HRM_DEVICE_TYPE = 120  #120 is the hr sensor
HRM_CHANNEL_PERIOD = 8070  # standard ANT+ heart rate period
NETWORK_KEY = [0xB9, 0xA5, 0x21, 0xFB, 0xBD, 0x72, 0xC3, 0x45]  # public ANT+ network key

node = Node(serial_device=USB_PORT)
channel = node.new_channel(Channel.Type.BIDIRECTIONAL_RECEIVE)

channel.set_period(HRM_CHANNEL_PERIOD)
channel.set_search_timeout(255)
channel.set_rf_freq(57) #standard frequency
channel.set_network_key(0, NETWORK_KEY)
channel.set_id(0, HRM_DEVICE_TYPE, 0)

#array to store the hr data
heart_rate_data = []
time_stamps = []

#function to get the incoming data and store it
def store_data(data):
    hr_value = data[7]  # ANT+ HR data is in byte 7 of the incoming data
    heart_rate_data.append(hr_value)
    time_stamps.append(time.time())

channel.on_broadcast_data = store_data
channel.open()
node.start()
#continue the program until it is stoppped manually
while True:
    time.sleep(1)
#closes the connection
node.stop()

# calculating the HRV with RMSSD and Baevsky index

#converts bpm to RR interval
def bpm_to_RR(bpm):
    return 60.0 / bpm

#calculates RMSSD HRV
def calc_RMSSD(RR):
    rr_diff = np.diff(RR) #to calculate successive differences
    rmssd = np.sqrt(np.mean(np.sqrt(rr_diff)))
    return rmssd

#calculates Baevsky index HRV
def calc_Baevsky(rr_intervals):
    # Baevsky = (AMo x %100)/(2Mo x MxDMn)

    #calculate AMo
    mode_rr = stats.mode(rr_intervals)[0][0]
    #calculate Mo
    median_rr = np.median(rr_intervals)

    #Calculate Maximum and Minimum RR intervals for MxDMn
    max_rr = np.max(rr_intervals)
    min_rr = np.min(rr_intervals)

    # Calculate MxDMn
    mxdmn = max_rr - min_rr

    #(AMo x %100)/(2Mo x MxDMn)
    baevsky_index = (mode_rr * 100) / (2 * median_rr * mxdmn)

    return baevsky_index

rr_intervals = [bpm_to_rr_intervals(hr) for hr in heart_rate_data]

rmssd_HRV = calc_RMSSD(rr_intervals)
Baevsky_HRV = calc_Baevsky(rr_intervals)

print(f"HRV(RMSSD): {rmssd_HRV:.2f} seconds")
print(f"Baevsky Index: {Baevsky_HRV:.2f}")

# calculate and plot the PSD
f, Pxx = welch(rr_intervals, fs=1, nperseg=8)

plt.plot(time_stamps, heart_rate_data, marker='o', color='b', label="Heart Rate (BPM)")
plt.xlabel("Time (s)")
plt.ylabel("Heart Rate (BPM)")
plt.title("Heart Rate Over Time")
plt.legend()
plt.grid(True)
plt.show()

plt.semilogy(f, Pxx)
plt.xlabel('Frequency [Hz]')
plt.ylabel('Power Spectral Density')
plt.title('Power Spectral Density of HRV')
plt.grid()
plt.show()
